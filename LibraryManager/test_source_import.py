from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from source_import import register_sources, import_sources_to_library


class SourceImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.library = self.root / "Guitar Library"
        (self.library / "Nested").mkdir(parents=True)
        self.wav = self.library / "Nested" / "clean.wav"
        self.wav.write_bytes(b"original-wav-bytes")
        self.sfz = self.library / "instrument.sfz"
        self.sfz.write_text('<region> sample="Nested/clean.wav"\n', encoding="utf-8")
        self.registry = self.root / "manager" / "reports" / "import_registry.json"
        self.before = {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (self.wav, self.sfz)
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_registers_nested_audio_and_sfz_without_touching_sources(self):
        result = register_sources([self.library], self.registry)
        data = json.loads(self.registry.read_text(encoding="utf-8"))
        self.assertEqual(result["registered_files"], 2)
        self.assertEqual(data["source_count"], 2)
        by_name = {item["filename"]: item for item in data["sources"]}
        self.assertEqual(by_name["clean.wav"]["relative_path"], str(Path("Nested") / "clean.wav"))
        self.assertEqual(by_name["instrument.sfz"]["format_group"], "SFZ")
        self.assertEqual(by_name["clean.wav"]["format_group"], "AUDIO")
        self.assertFalse(result["source_files_modified"])
        self.assertFalse(result["source_files_moved"])
        self.assertFalse(result["source_files_deleted"])
        for path in (self.wav, self.sfz):
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), self.before[str(path)])

    def test_multiple_selections_and_repeat_import_are_idempotent(self):
        first = register_sources([self.wav, self.library], self.registry)
        second = register_sources([self.library], self.registry)
        self.assertEqual(first["registered_files"], 2)
        self.assertEqual(second["registered_files"], 0)
        self.assertEqual(second["already_registered"], 2)
        data = json.loads(self.registry.read_text(encoding="utf-8"))
        self.assertEqual(data["source_count"], 2)

    def test_inaccessible_nested_folder_is_reported_not_silently_skipped(self):
        from unittest.mock import patch
        import os
        real_scandir = os.scandir

        def guarded_scandir(path):
            if Path(path).name == "Nested":
                raise PermissionError("simulated access denied")
            return real_scandir(path)

        with patch("source_import.os.scandir", side_effect=guarded_scandir):
            result = register_sources([self.library], self.registry)

        self.assertTrue(any(
            item.get("stage") == "IMPORT_DIRECTORY_SCAN"
            and Path(item["path"]).name == "Nested"
            for item in result["errors"]
        ))
        data = json.loads(self.registry.read_text(encoding="utf-8"))
        self.assertEqual(data["source_count"], 1)
        self.assertTrue(self.sfz.exists())
        self.assertTrue(self.wav.exists())

    def test_sfz_dependencies_are_audited_and_saved_to_registry(self):
        result = register_sources([self.library], self.registry)
        data = json.loads(self.registry.read_text(encoding="utf-8"))
        rows = data["sfz_dependency_audit"]
        self.assertEqual(data["registry_version"], 2)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "FOUND")
        self.assertEqual(rows[0]["resolved_sample"], str(self.wav.resolve()))
        self.assertEqual(result["sfz_dependencies_found"], 1)
        self.assertEqual(result["sfz_dependencies_blocked"], 0)

    def test_multiple_sfz_files_are_audited_without_registry_lookup_loss(self):
        extra = self.library / "second.sfz"
        extra.write_text('<region> sample="Nested/clean.wav"\n', encoding="utf-8")
        result = register_sources([self.library], self.registry)
        data = json.loads(self.registry.read_text(encoding="utf-8"))
        sfz_rows = data["sfz_dependency_audit"]
        self.assertEqual(result["sfz_dependency_rows"], 2)
        self.assertEqual(result["sfz_dependencies_found"], 2)
        self.assertEqual({Path(row["sfz_path"]).name for row in sfz_rows},
                         {"instrument.sfz", "second.sfz"})

    def test_sfz_missing_and_outside_dependencies_are_blocked(self):
        outside = self.root / "outside.wav"
        outside.write_bytes(b"not part of library")
        self.sfz.write_text(
            '<region> sample="missing.wav"\n'
            '<region> sample="../outside.wav"\n',
            encoding="utf-8",
        )
        result = register_sources([self.library], self.registry)
        data = json.loads(self.registry.read_text(encoding="utf-8"))
        statuses = [row["status"] for row in data["sfz_dependency_audit"]]
        self.assertEqual(statuses, ["MISSING", "OUTSIDE_LIBRARY"])
        self.assertEqual(result["sfz_dependencies_found"], 0)
        self.assertEqual(result["sfz_dependencies_blocked"], 2)
        self.assertTrue(outside.exists())

    def test_existing_v1_registry_is_migrated_without_losing_records(self):
        import os

        self.registry.parent.mkdir(parents=True)
        legacy = {
            "registry_version": 1,
            "source_count": 1,
            "sources": [{
                "identity": os.path.normcase(str(self.wav.resolve())),
                "source_path": str(self.wav.resolve()),
                "filename": self.wav.name,
            }],
        }
        self.registry.write_text(json.dumps(legacy), encoding="utf-8")
        result = register_sources([self.library], self.registry)
        data = json.loads(self.registry.read_text(encoding="utf-8"))
        self.assertEqual(data["registry_version"], 2)
        self.assertEqual(data["source_count"], 2)
        self.assertEqual(result["registered_files"], 1)


    def test_import_copies_to_scannable_incoming_and_preserves_originals(self):
        incoming = self.root / "Samples" / "Import Sample Guitar"
        incoming.mkdir(parents=True)
        result = import_sources_to_library([self.library], incoming, self.registry)
        self.assertEqual(result["copied_files"], 2)
        self.assertEqual(result["copy_integrity"], "SHA256_VERIFIED")
        self.assertEqual(result["next_stage"], "SCAN_LIBRARY")
        self.assertFalse(result["source_files_modified"])
        self.assertFalse(result["source_files_moved"])
        self.assertFalse(result["source_files_deleted"])
        batch = Path(result["import_batch"])
        copied_wav = batch / "Sources" / "001_Guitar Library" / "Nested" / "clean.wav"
        copied_sfz = batch / "Sources" / "001_Guitar Library" / "instrument.sfz"
        self.assertEqual(copied_wav.read_bytes(), self.wav.read_bytes())
        self.assertEqual(copied_sfz.read_bytes(), self.sfz.read_bytes())
        data = json.loads(self.registry.read_text(encoding="utf-8"))
        by_name = {item["filename"]: item for item in data["sources"]}
        self.assertEqual(Path(by_name["clean.wav"]["imported_path"]), copied_wav)
        self.assertEqual(Path(by_name["instrument.sfz"]["imported_path"]), copied_sfz)
        self.assertEqual(
            by_name["clean.wav"]["imported_sha256"],
            hashlib.sha256(self.wav.read_bytes()).hexdigest().upper(),
        )
        self.assertEqual(
            hashlib.sha256(self.wav.read_bytes()).hexdigest(),
            self.before[str(self.wav)],
        )
        self.assertEqual(
            hashlib.sha256(self.sfz.read_bytes()).hexdigest(),
            self.before[str(self.sfz)],
        )

    def test_individual_sfz_and_sample_selections_keep_relative_dependency_paths(self):
        incoming = self.root / "Samples" / "Import Sample Guitar"
        incoming.mkdir(parents=True)
        result = import_sources_to_library([self.sfz, self.wav], incoming, self.registry)
        batch = Path(result["import_batch"])
        copied_sfz = batch / "Selected_Files"
        sfz_files = list(copied_sfz.rglob("instrument.sfz"))
        self.assertEqual(len(sfz_files), 1)
        copied_root = sfz_files[0].parent
        copied_sample = copied_root / "Nested" / "clean.wav"
        self.assertTrue(copied_sample.is_file())
        self.assertEqual(
            copied_sample.read_bytes(),
            self.wav.read_bytes(),
        )
        self.assertEqual(
            sfz_files[0].read_text(encoding="utf-8"),
            self.sfz.read_text(encoding="utf-8"),
        )
        self.assertEqual(result["copied_files"], 2)

    def test_reimport_reuses_verified_imported_copies(self):
        incoming = self.root / "Samples" / "Import Sample Guitar"
        incoming.mkdir(parents=True)
        first = import_sources_to_library([self.library], incoming, self.registry)
        second = import_sources_to_library([self.library], incoming, self.registry)
        self.assertEqual(first["copied_files"], 2)
        self.assertEqual(second["copied_files"], 0)
        self.assertIsNone(second["import_batch"])
        self.assertEqual(second["registry"]["already_registered"], 2)
        self.assertEqual(len(list(incoming.glob("IMPORT_BATCH_*"))), 1)

    def test_changed_source_updates_registry_and_next_import_reuses_new_copy(self):
        incoming = self.root / "Samples" / "Import Sample Guitar"
        incoming.mkdir(parents=True)
        first = import_sources_to_library([self.library], incoming, self.registry)

        changed_bytes = b"updated-original-wav-with-a-new-size"
        self.wav.write_bytes(changed_bytes)
        second = import_sources_to_library([self.library], incoming, self.registry)
        # One changed file refreshes the complete folder so SFZ and its sample
        # remain together with matching relative paths in the new batch.
        self.assertEqual(second["copied_files"], 2)

        data = json.loads(self.registry.read_text(encoding="utf-8"))
        wave_record = next(item for item in data["sources"] if item["filename"] == "clean.wav")
        sfz_record = next(item for item in data["sources"] if item["filename"] == "instrument.sfz")
        updated_copy = Path(wave_record["imported_path"])
        updated_sfz = Path(sfz_record["imported_path"])
        expected_new_batch = Path(second["import_batch"])
        self.assertEqual(
            updated_copy,
            expected_new_batch / "Sources" / "001_Guitar Library" / "Nested" / "clean.wav",
        )
        self.assertEqual(
            updated_sfz,
            expected_new_batch / "Sources" / "001_Guitar Library" / "instrument.sfz",
        )
        self.assertEqual(updated_copy.read_bytes(), changed_bytes)
        self.assertTrue(updated_sfz.is_file())
        self.assertEqual(wave_record["size_bytes"], self.wav.stat().st_size)
        self.assertEqual(wave_record["modified_ns"], self.wav.stat().st_mtime_ns)
        self.assertEqual(
            wave_record["imported_sha256"],
            hashlib.sha256(changed_bytes).hexdigest().upper(),
        )
        self.assertEqual(len(list(expected_new_batch.rglob("clean.wav"))), 1)
        self.assertEqual(len(list(expected_new_batch.rglob("instrument.sfz"))), 1)

        third = import_sources_to_library([self.library], incoming, self.registry)
        self.assertEqual(third["copied_files"], 0)
        self.assertIsNone(third["import_batch"])
        self.assertEqual(len(list(incoming.glob("IMPORT_BATCH_*"))), 2)

    def test_tampered_existing_import_copy_blocks_reimport(self):
        incoming = self.root / "Samples" / "Import Sample Guitar"
        incoming.mkdir(parents=True)
        first = import_sources_to_library([self.library], incoming, self.registry)
        batch = Path(first["import_batch"])
        copied_wav = batch / "Sources" / "001_Guitar Library" / "Nested" / "clean.wav"
        copied_wav.write_bytes(b"tampered copy")

        with self.assertRaisesRegex(IOError, "копия была изменена или повреждена"):
            import_sources_to_library([self.library], incoming, self.registry)

        self.assertEqual(len(list(incoming.glob("IMPORT_BATCH_*"))), 1)
        self.assertEqual(copied_wav.read_bytes(), b"tampered copy")
        self.assertEqual(self.wav.read_bytes(), b"original-wav-bytes")
        registry_data = json.loads(self.registry.read_text(encoding="utf-8"))
        record = next(item for item in registry_data["sources"] if item["filename"] == "clean.wav")
        self.assertEqual(Path(record["imported_path"]), copied_wav)

    def test_failed_import_rolls_back_partial_batch_and_keeps_sources(self):
        from unittest.mock import patch
        import source_import

        incoming = self.root / "Samples" / "Import Sample Guitar"
        incoming.mkdir(parents=True)
        real_copy = source_import._copy_verified
        calls = {"count": 0}

        def fail_after_first(source, destination, **kwargs):
            calls["count"] += 1
            if calls["count"] == 2:
                raise OSError("simulated destination disk failure")
            return real_copy(source, destination, **kwargs)

        with patch("source_import._copy_verified", side_effect=fail_after_first):
            with self.assertRaisesRegex(OSError, "simulated destination disk failure"):
                import_sources_to_library([self.library], incoming, self.registry)

        self.assertEqual(list(incoming.iterdir()), [])
        self.assertFalse(self.registry.exists())
        self.assertEqual(self.wav.read_bytes(), b"original-wav-bytes")
        self.assertTrue(self.sfz.exists())

    def test_symlink_inside_source_folder_aborts_batch_without_copying(self):
        incoming = self.root / "Samples" / "Import Sample Guitar"
        incoming.mkdir(parents=True)
        link = self.library / "linked.wav"
        try:
            link.symlink_to(self.wav)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlinks are unavailable in this environment: {exc}")

        with self.assertRaisesRegex(OSError, "Символические ссылки"):
            import_sources_to_library([self.library], incoming, self.registry)

        self.assertEqual(list(incoming.iterdir()), [])
        self.assertFalse(self.registry.exists())
        self.assertEqual(self.wav.read_bytes(), b"original-wav-bytes")

    def test_direct_symlink_source_is_rejected_before_resolving_target(self):
        linked = self.root / "linked.wav"
        try:
            linked.symlink_to(self.wav)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlinks are unavailable in this environment: {exc}")
        incoming = self.root / "Samples" / "Import Sample Guitar"
        incoming.mkdir(parents=True)

        with self.assertRaisesRegex(ValueError, "Символические ссылки"):
            import_sources_to_library([linked], incoming, self.registry)

        self.assertEqual(list(incoming.iterdir()), [])
        self.assertFalse(self.registry.exists())
        self.assertEqual(self.wav.read_bytes(), b"original-wav-bytes")

    def test_import_rejects_target_folder_as_its_own_source(self):
        incoming = self.root / "Samples" / "Import Sample Guitar"
        incoming.mkdir(parents=True)
        existing = incoming / "already-there.wav"
        existing.write_bytes(b"already in active library")

        with self.assertRaisesRegex(ValueError, "сама целевая папка"):
            import_sources_to_library([incoming], incoming, self.registry)

        self.assertEqual(list(incoming.iterdir()), [existing])
        self.assertFalse(self.registry.exists())
        self.assertEqual(existing.read_bytes(), b"already in active library")

    def test_import_rejects_samples_parent_to_prevent_recursive_self_copy(self):
        incoming = self.root / "Samples" / "Import Sample Guitar"
        incoming.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "папку-родитель"):
            import_sources_to_library([incoming.parent], incoming, self.registry)
        self.assertEqual(list(incoming.iterdir()), [])
        self.assertFalse(self.registry.exists())

    def test_missing_source_does_not_create_registry(self):
        with self.assertRaises(FileNotFoundError):
            register_sources([self.root / "missing"], self.registry)
        self.assertFalse(self.registry.exists())

    def test_corrupt_registry_is_not_overwritten(self):
        self.registry.parent.mkdir(parents=True)
        self.registry.write_text("{broken", encoding="utf-8")
        before = self.registry.read_bytes()
        with self.assertRaises(json.JSONDecodeError):
            register_sources([self.library], self.registry)
        self.assertEqual(self.registry.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
