import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from chord_analysis import analyze_chords


def write_chord(path: Path, frequencies, seconds=0.9, rate=11025):
    samples = []
    for index in range(int(rate * seconds)):
        value = sum(math.sin(2 * math.pi * frequency * index / rate)
                    for frequency in frequencies)
        sample = max(-32767, min(32767, int(value * 7000 / max(1, len(frequencies)))))
        samples.append(struct.pack("<h", sample))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(b"".join(samples))


class ChordAnalysisTests(unittest.TestCase):
    def test_detects_stable_major_chord_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "c_major.wav"
            write_chord(path, [261.63, 329.63, 392.00])
            result = analyze_chords(path)
            self.assertGreaterEqual(result["chord_candidate_count"], 1)
            self.assertIn("C", [item["root_pitch_class"]
                                for item in result["chord_candidates"]])
            self.assertTrue(all(item["review_status"] == "NEEDS_MUSICAL_REVIEW"
                                for item in result["chord_candidates"]))
            self.assertEqual(result["license_status"], "UNREVIEWED")

    def test_single_note_does_not_become_a_chord(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "single_note.wav"
            write_chord(path, [440.0])
            result = analyze_chords(path)
            self.assertEqual(result["chord_candidates"], [])

    def test_source_hash_is_preserved_and_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chord.wav"
            write_chord(path, [261.63, 329.63, 392.00])
            before = path.read_bytes()
            result = analyze_chords(path)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(len(result["source_sha256"]), 64)
            self.assertEqual(result["automatic_destructive_action"], "NONE")

    def test_rejects_invalid_analysis_parameters(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chord.wav"
            write_chord(path, [261.63, 329.63, 392.00])
            with self.assertRaises(ValueError):
                analyze_chords(path, frame_ms=20)


if __name__ == "__main__":
    unittest.main()
