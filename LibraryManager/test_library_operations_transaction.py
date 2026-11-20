from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from library_operations import cleanup_original_sources, distribute_assets_transactional


class TransactionalDistributionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.samples = self.root / "Samples"
        self.samples.mkdir()
        self.staging = self.root / "LibraryManager" / "staging"
        self.clips = self.staging / "clips"
        self.clips.mkdir(parents=True)
        self.journal = self.root / "operations.jsonl"
        self.entries = []
        self.sources = []
        for index in range(2):
            source = self.clips / f"asset_{index}.wav"
            payload = (f"fake-pcm-wave-{index}").encode("ascii")
            source.write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest().upper()
            manifest = self.clips / f"asset_{index}.json"
            manifest.write_text(json.dumps({
                "asset_id": f"A{index}",
                "review_status": "REVIEWED",
                "license_status": "LICENSE_APPROVED",
            }), encoding="utf-8")
            destination = (
                self.samples / "FACTORY" / "POP_PUNK" / "WAV"
                / "ELECTRIC_GUITAR" / "RIFF" / "DISTORTION" / source.name
            )
            self.entries.append({
                "manifest_path": str(manifest.resolve()),
                "source_path": str(source.resolve()),
                "source_sha256": digest,
                "destination_path": str(destination.resolve()),
                "category_path": "POP_PUNK/WAV/ELECTRIC_GUITAR/RIFF/DISTORTION",
            })
            self.sources.append((source, payload))
        self.plan = {
            "samples_root": str(self.samples.resolve()),
            "staging_root": str(self.staging.resolve()),
            "entries": self.entries,
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _run_with_plan(self, *, approve: bool):
        with patch("library_operations.distribution_plan", return_value=self.plan):
            return distribute_assets_transactional(
                self.plan, staging_root=self.staging, approve=approve,
                journal_path=self.journal,
            )

    def test_dry_run_does_not_create_factory_files(self) -> None:
        result = self._run_with_plan(approve=False)
        self.assertEqual(result["status"], "DRY_RUN")
        self.assertFalse((self.samples / "FACTORY").exists())
        self.assertTrue(all(source.is_file() for source, _ in self.sources))

    def test_batch_failure_rolls_back_every_file_created_by_this_batch(self) -> None:
        import shutil

        real_copy = shutil.copyfileobj
        calls = 0

        def fail_on_second_copy(source, destination, length=0):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated disk write failure")
            return real_copy(source, destination, length)

        with patch("shutil.copyfileobj", side_effect=fail_on_second_copy):
            with self.assertRaisesRegex(RuntimeError, "all files created by this batch were rolled back"):
                self._run_with_plan(approve=True)

        for entry in self.entries:
            destination = Path(entry["destination_path"])
            sidecar = destination.with_suffix(destination.suffix + ".json")
            self.assertFalse(destination.exists())
            self.assertFalse(sidecar.exists())
        for source, payload in self.sources:
            self.assertTrue(source.is_file())
            self.assertEqual(source.read_bytes(), payload)
        journal_events = [
            json.loads(line) for line in self.journal.read_text(encoding="utf-8").splitlines()
        ]
        self.assertTrue(any(item["event"] == "ASSET_DISTRIBUTED" for item in journal_events))
        self.assertEqual(
            sum(item["event"] == "BATCH_ROLLBACK" for item in journal_events), 2
        )

    def test_auto_distribution_skips_bad_manifest_and_continues(self) -> None:
        from library_operations import auto_distribute_approved

        manifests_dir = self.staging / "manifests"
        manifests_dir.mkdir(parents=True)
        bad = manifests_dir / "00_bad.json"
        good = manifests_dir / "01_good.json"
        bad.write_text("not-json", encoding="utf-8")
        good.write_text("{}", encoding="utf-8")
        single_plan = {
            **self.plan,
            "entries": [self.entries[0]],
        }
        with patch("library_operations.distribution_plan",
                   side_effect=[ValueError("broken manifest"), single_plan]), \
             patch("library_operations.distribute_assets_transactional",
                   return_value={"results": [{"status": "VERIFIED_COPIED"}]}) as distribute, \
             patch("finalization.finalize_library",
                   return_value={"factory_finalized": True}) as finalize:
            result = auto_distribute_approved(
                self.samples, self.staging, approve=True, journal_path=self.journal,
            )

        self.assertEqual(result["status"], "DISTRIBUTION_COMPLETE_WITH_ERRORS")
        self.assertEqual(result["manifests_seen"], 2)
        self.assertEqual(result["ready_count"], 1)
        self.assertEqual(result["copied_count"], 1)
        self.assertEqual(len(result["rejected"]), 1)
        self.assertEqual(Path(result["rejected"][0]["manifest_path"]), bad)
        distribute.assert_called_once()
        finalize.assert_called_once()
        self.assertTrue(result["finalization"]["factory_finalized"])
        self.assertTrue(result["source_originals_deleted"] is False)

    def test_existing_destination_blocks_the_entire_batch_before_copy(self) -> None:
        first_destination = Path(self.entries[0]["destination_path"])
        first_destination.parent.mkdir(parents=True)
        first_destination.write_bytes(b"existing-user-file")
        with self.assertRaises(FileExistsError):
            self._run_with_plan(approve=True)
        self.assertEqual(first_destination.read_bytes(), b"existing-user-file")
        second_destination = Path(self.entries[1]["destination_path"])
        self.assertFalse(second_destination.exists())

    def _make_cleanup_fixture(self):
        incoming = self.samples / "Import Sample Guitar" / "IMPORT_BATCH_TEST"
        incoming.mkdir(parents=True)
        source = incoming / "original.wav"
        source_payload = b"original-source-audio"
        source.write_bytes(source_payload)
        source_hash = hashlib.sha256(source_payload).hexdigest().upper()

        destination = (
            self.samples / "FACTORY" / "POP_PUNK" / "WAV"
            / "ELECTRIC_GUITAR" / "RIFF" / "DISTORTION" / "original.wav"
        )
        destination.parent.mkdir(parents=True)
        destination_payload = b"verified-derived-audio"
        destination.write_bytes(destination_payload)
        destination_hash = hashlib.sha256(destination_payload).hexdigest().upper()

        distributed = {
            "source_path": str(source.resolve()),
            "source_sha256": source_hash,
            "distributed_path": str(destination.resolve()),
            "distributed_sha256": destination_hash,
            "distribution_status": "VERIFIED_COPIED",
        }
        sidecar = destination.with_suffix(destination.suffix + ".json")
        sidecar.write_text(json.dumps(distributed), encoding="utf-8")
        staging_manifest = self.clips / "original.json"
        staging_manifest.write_text(json.dumps({
            **distributed,
            "asset_id": "CLEANUP-TEST",
        }), encoding="utf-8")
        return source, destination, sidecar, staging_manifest, distributed

    def test_cleanup_requires_verified_factory_sidecar_and_deletes_only_original(self):
        source, destination, sidecar, manifest, _ = self._make_cleanup_fixture()
        result = cleanup_original_sources(
            [manifest],
            samples_root=self.samples,
            confirm_delete=True,
            confirm_all_dependents_accounted_for=True,
            journal_path=self.journal,
        )
        self.assertEqual(result["status"], "ORIGINAL_CLEANUP_COMPLETE")
        self.assertFalse(source.exists())
        self.assertTrue(destination.is_file())
        self.assertTrue(sidecar.is_file())
        self.assertEqual(result["deleted"][0]["source"], str(source.resolve()))

    def test_cleanup_refuses_unverified_or_tampered_factory_sidecar(self):
        source, destination, sidecar, manifest, distributed = self._make_cleanup_fixture()
        distributed["distributed_sha256"] = "0" * 64
        sidecar.write_text(json.dumps(distributed), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "sidecar does not verify"):
            cleanup_original_sources(
                [manifest],
                samples_root=self.samples,
                confirm_delete=True,
                confirm_all_dependents_accounted_for=True,
                journal_path=self.journal,
            )
        self.assertTrue(source.is_file())
        self.assertTrue(destination.is_file())

    def test_cleanup_rejects_factory_path_outside_factory_root(self):
        source, destination, sidecar, manifest, distributed = self._make_cleanup_fixture()
        outside = self.root / "outside.wav"
        outside.write_bytes(destination.read_bytes())
        distributed["distributed_path"] = str(outside.resolve())
        sidecar.write_text(json.dumps(distributed), encoding="utf-8")
        manifest.write_text(json.dumps(distributed), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "inside FACTORY"):
            cleanup_original_sources(
                [manifest],
                samples_root=self.samples,
                confirm_delete=True,
                confirm_all_dependents_accounted_for=True,
                journal_path=self.journal,
            )
        self.assertTrue(source.is_file())


if __name__ == "__main__":
    unittest.main()
