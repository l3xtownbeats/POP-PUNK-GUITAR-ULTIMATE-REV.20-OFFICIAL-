from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from source_import import register_sources


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
        self.registry.parent.mkdir(parents=True)
        legacy = {
            "registry_version": 1,
            "source_count": 1,
            "sources": [{
                "identity": str(self.wav.resolve()).casefold(),
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
