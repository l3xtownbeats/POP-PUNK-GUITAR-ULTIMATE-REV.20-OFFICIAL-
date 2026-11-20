"""Regression tests for Samples path normalization."""
import tempfile
import unittest
from pathlib import Path

from unified_manager import resolve_samples_root


class SamplesPathResolutionTests(unittest.TestCase):
    def test_accepts_samples_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Samples"
            (root / "Import Sample Guitar").mkdir(parents=True)
            self.assertEqual(resolve_samples_root(root), root.resolve())

    def test_accepts_realistic_factory_and_import_layout_with_spaces(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "POP PUNK GUITAR ULTIMATE" / "Samples"
            (root / "Factory").mkdir(parents=True)
            (root / "Import Sample Guitar").mkdir()
            self.assertEqual(resolve_samples_root(root), root.resolve())

    def test_accepts_import_folder_itself(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Samples"
            incoming = root / "Import Sample Guitar"
            incoming.mkdir(parents=True)
            self.assertEqual(resolve_samples_root(incoming), root.resolve())

    def test_case_insensitive_child_name(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Samples"
            (root / "IMPORT SAMPLE GUITAR").mkdir(parents=True)
            self.assertEqual(resolve_samples_root(root), root.resolve())

    def test_trailing_whitespace_in_child_name(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Samples"
            (root / "Import Sample Guitar ").mkdir(parents=True)
            self.assertEqual(resolve_samples_root(root), root.resolve())

    def test_missing_folder_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Samples"
            root.mkdir()
            with self.assertRaisesRegex(FileNotFoundError, "Import Sample Guitar"):
                resolve_samples_root(root)

    def test_rejects_file_path(self):
        with tempfile.TemporaryDirectory() as temp:
            file_path = Path(temp) / "not_a_folder.txt"
            file_path.write_text("x", encoding="utf-8")
            with self.assertRaises(NotADirectoryError):
                resolve_samples_root(file_path)


if __name__ == "__main__":
    unittest.main()
