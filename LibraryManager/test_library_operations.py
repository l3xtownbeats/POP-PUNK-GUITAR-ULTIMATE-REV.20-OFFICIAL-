from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
import wave
from pathlib import Path

from library_operations import (
    cleanup_original_sources,
    distribute_assets,
    distribution_plan,
)


def write_wav(path: Path, frames: int = 800) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(8000)
        output.writeframes(b"\x01\x00" * frames)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class LibraryOperationsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.samples = self.root / "Samples"
        self.incoming = self.samples / "Import Sample Guitar"
        self.incoming.mkdir(parents=True)
        self.staging = self.root / "staging"
        (self.staging / "clips").mkdir(parents=True)
        self.original = self.incoming / "long_take.wav"
        self.staged = self.staging / "clips" / "riff_001.wav"
        write_wav(self.original)
        write_wav(self.staged, 400)
        self.manifest = self.staging / "clips" / "riff_001.wav.json"
        record = {
            "schema_version": 1,
            "asset_id": "riff-001",
            "source_path": str(self.original.resolve()),
            "source_sha256": sha(self.original),
            "source_start_sample": 100,
            "source_end_sample": 500,
            "derived_path": str(self.staged.resolve()),
            "derived_sha256": sha(self.staged),
            "kind": "rhythm_pattern",
            "engine_targets": ["PATTERN_MODE", "PATTERN_INSTRUMENT"],
            "review_status": "REVIEWED",
            "license_status": "LICENSE_APPROVED",
            "review_validation": {
                "source_sha256_verified": True,
                "derived_sha256_verified": True,
                "sample_boundaries_verified": True,
                "explicit_musical_approval": True,
                "explicit_license_approval": True,
            },
            "musical_metadata": {
                "style_family": "POP_PUNK",
                "instrument_family": "ELECTRIC_GUITAR",
                "asset_role": "RHYTHM_PATTERN",
                "tone_family": "CRUNCH",
                "musical_review_notes": "Reviewed boundaries and guitar content.",
                "license_evidence": "License explicitly permits redistribution.",
            },
        }
        self.manifest.write_text(json.dumps(record), encoding="utf-8")
        self.journal = self.root / "operations.jsonl"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_plan_is_dry_run_and_routes_by_reviewed_tags(self) -> None:
        plan = distribution_plan([self.manifest], self.samples, self.staging)
        self.assertEqual(plan["entries"][0]["category_path"],
                         "POP_PUNK/WAV/ELECTRIC_GUITAR/RHYTHM_PATTERN/CRUNCH")
        self.assertEqual(plan["entries"][0]["status"], "READY_FOR_EXPLICIT_APPROVAL")
        self.assertTrue(self.original.exists())
        self.assertTrue(self.staged.exists())

    def test_distribution_requires_approval_and_verifies_copy(self) -> None:
        plan = distribution_plan([self.manifest], self.samples, self.staging)
        dry = distribute_assets(plan, approve=False, journal_path=self.journal)
        self.assertFalse(dry["executed"])
        self.assertFalse(Path(plan["entries"][0]["destination_path"]).exists())
        result = distribute_assets(plan, approve=True, journal_path=self.journal)
        destination = Path(result["results"][0]["destination"])
        self.assertEqual(sha(destination), sha(self.staged))
        self.assertTrue(self.original.exists())
        self.assertTrue(self.staged.exists())
        sidecar = destination.with_suffix(destination.suffix + ".json")
        self.assertEqual(json.loads(sidecar.read_text())["distribution_status"],
                         "VERIFIED_COPIED")

    def test_original_cleanup_requires_two_confirmations_and_verified_children(self) -> None:
        plan = distribution_plan([self.manifest], self.samples, self.staging)
        result = distribute_assets(plan, approve=True, journal_path=self.journal)
        destination = Path(result["results"][0]["destination"])
        sidecar = destination.with_suffix(destination.suffix + ".json")
        with self.assertRaises(ValueError):
            cleanup_original_sources([sidecar], samples_root=self.samples,
                                     confirm_delete=True,
                                     confirm_all_dependents_accounted_for=False,
                                     journal_path=self.journal)
        self.assertTrue(self.original.exists())
        deleted = cleanup_original_sources(
            [sidecar], samples_root=self.samples,
            confirm_delete=True,
            confirm_all_dependents_accounted_for=True,
            journal_path=self.journal,
        )
        self.assertEqual(deleted["status"], "ORIGINAL_CLEANUP_COMPLETE")
        self.assertFalse(self.original.exists())
        self.assertTrue(destination.exists())
        self.assertTrue(self.staged.exists())

    def test_unreviewed_or_unlicensed_assets_cannot_be_distributed(self) -> None:
        record = json.loads(self.manifest.read_text())
        record["license_status"] = "UNREVIEWED"
        self.manifest.write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaises(ValueError):
            distribution_plan([self.manifest], self.samples, self.staging)

    def test_original_source_change_after_plan_blocks_factory_copy(self) -> None:
        plan = distribution_plan([self.manifest], self.samples, self.staging)
        self.original.write_bytes(self.original.read_bytes() + b"changed")
        with self.assertRaises(RuntimeError):
            distribute_assets(plan, approve=True, journal_path=self.journal)
        self.assertFalse(Path(plan["entries"][0]["destination_path"]).exists())

    def test_changed_staged_asset_is_rejected(self) -> None:
        self.staged.write_bytes(self.staged.read_bytes() + b"tampered")
        with self.assertRaises(ValueError):
            distribution_plan([self.manifest], self.samples, self.staging)


if __name__ == "__main__":
    unittest.main()
