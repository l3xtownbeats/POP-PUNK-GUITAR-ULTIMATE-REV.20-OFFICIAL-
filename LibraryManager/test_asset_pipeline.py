import tempfile
import unittest
import wave
from pathlib import Path
from asset_pipeline import extract_reviewed_wav

class AssetPipelineTests(unittest.TestCase):
    def make_wav(self, path):
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
            w.writeframes(b"".join((i % 100).to_bytes(2, "little", signed=False) for i in range(100)))

    def test_extracts_exact_range_and_keeps_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = root / "source.wav"; self.make_wav(source)
            before = source.read_bytes()
            result = extract_reviewed_wav(source, root / "staging", 10, 30,
                kind="note_event", engines=["MELODY_INSTRUMENT", "PATTERN_MODE"])
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(result["frame_count"], 20)
            self.assertEqual(result["engine_targets"], ["MELODY_INSTRUMENT", "PATTERN_MODE"])
            with wave.open(result["derived_path"], "rb") as w:
                self.assertEqual(w.getnframes(), 20)
            self.assertTrue(Path(result["derived_path"]).with_suffix(".json").is_file())

    def test_rejects_bad_range(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = root / "source.wav"; self.make_wav(source)
            with self.assertRaises(ValueError):
                extract_reviewed_wav(source, root / "staging", 90, 120,
                    kind="note_event", engines=["MELODY_INSTRUMENT"])

    def test_rejects_unknown_engine(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = root / "source.wav"; self.make_wav(source)
            with self.assertRaises(ValueError):
                extract_reviewed_wav(source, root / "staging", 1, 5,
                    kind="note_event", engines=["MADE_UP"])

if __name__ == "__main__":
    unittest.main()
