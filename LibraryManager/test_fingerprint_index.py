import math
import tempfile
import unittest
import wave
from pathlib import Path

from fingerprint_index import build_fingerprint_index


class FingerprintIndexTests(unittest.TestCase):
    def make_tone(self, path, hz=220, seconds=1.2, rate=8000):
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            data = bytearray()
            for i in range(int(seconds * rate)):
                t = i / rate
                value = 0.55 * math.sin(2 * math.pi * hz * t)
                value += 0.22 * math.sin(2 * math.pi * (hz * 1.5) * t)
                sample = int(max(-1.0, min(1.0, value)) * 28000)
                data.extend(sample.to_bytes(2, "little", signed=True))
            w.writeframes(data)

    def test_indexes_wavs_and_reports_exact_duplicates_without_touching_sources(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a = root / "a.wav"
            b = root / "copy.wav"
            c = root / "different.wav"
            self.make_tone(a)
            b.write_bytes(a.read_bytes())
            self.make_tone(c, hz=587.33)
            before = {p.name: p.read_bytes() for p in (a, b, c)}
            report = build_fingerprint_index(root, workers=2)
            self.assertEqual(report["files_discovered"], 3)
            self.assertEqual(report["files_fingerprinted"], 3)
            self.assertEqual(len(report["exact_duplicate_groups"]), 1)
            self.assertEqual(report["exact_duplicate_groups"][0]["count"], 2)
            self.assertFalse(report["safety"]["source_files_modified"])
            self.assertEqual(before, {p.name: p.read_bytes() for p in (a, b, c)})

    def test_excludes_piano_bell_drum_labeled_paths(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            guitar = root / "Electric Guitar" / "riff.wav"
            piano = root / "Piano" / "riff.wav"
            bell = root / "Bell Samples" / "hit.wav"
            drum = root / "Drum_Loops" / "loop.wav"
            for path in (guitar, piano, bell, drum):
                path.parent.mkdir(parents=True, exist_ok=True)
                self.make_tone(path)
            report = build_fingerprint_index(root, workers=2)
            self.assertEqual(report["files_discovered"], 1)
            self.assertEqual(report["files_fingerprinted"], 1)
            self.assertEqual(report["files_excluded_by_label"], 3)

    def test_ignores_non_wav_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "notes.txt").write_text("not audio")
            report = build_fingerprint_index(root)
            self.assertEqual(report["files_discovered"], 0)
            self.assertEqual(report["files_fingerprinted"], 0)


if __name__ == "__main__":
    unittest.main()
