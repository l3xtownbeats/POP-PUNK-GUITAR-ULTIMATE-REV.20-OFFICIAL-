import json
import math
import tempfile
import unittest
import wave
from pathlib import Path

from audio_fingerprint import compare_fingerprints, fingerprint_wav


class AudioFingerprintTests(unittest.TestCase):
    def make_signal(self, path, gain=0.7, seconds=1.2, rate=8000, offset=0.0):
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            data = bytearray()
            for i in range(int(seconds * rate)):
                t = i / rate
                value = gain * (0.55 * math.sin(2 * math.pi * 220 * t)
                                + 0.25 * math.sin(2 * math.pi * 330 * t)
                                + 0.12 * math.sin(2 * math.pi * 440 * t))
                sample = max(-32768, min(32767, int(value * 30000)))
                data.extend(sample.to_bytes(2, "little", signed=True))
            w.writeframes(data)

    def test_fingerprint_is_deterministic_and_gain_tolerant(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td)/"a.wav", Path(td)/"b.wav"
            self.make_signal(a, gain=0.7)
            self.make_signal(b, gain=0.45)
            fa, fb = fingerprint_wav(a), fingerprint_wav(b)
            self.assertGreater(fa["landmark_count"], 0)
            self.assertEqual(fa["landmarks"], fingerprint_wav(a)["landmarks"])
            comparison = compare_fingerprints(fa, fb)
            self.assertEqual(comparison["review_status"], "NEEDS_MUSICAL_REVIEW")
            self.assertEqual(comparison["action"], "REPORT_ONLY_NO_DESTRUCTIVE_ACTION")
            self.assertGreater(comparison["aligned_landmarks"], 0)

    def test_different_frequency_content_is_not_assumed_same_recording(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td)/"a.wav", Path(td)/"b.wav"
            self.make_signal(a)
            with wave.open(str(b), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
                raw = bytearray()
                for i in range(9600):
                    v = int(18000 * math.sin(2 * math.pi * 587.33 * i / 8000))
                    raw.extend(v.to_bytes(2, "little", signed=True))
                w.writeframes(raw)
            result = compare_fingerprints(fingerprint_wav(a), fingerprint_wav(b))
            self.assertNotEqual(result["relationship_candidate"], "POSSIBLE_SAME_RECORDED_PASSAGE")

    def test_version_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            compare_fingerprints({"fingerprint_version":"x","landmarks":[]},
                                 {"fingerprint_version":"y","landmarks":[]})


if __name__ == "__main__":
    unittest.main()
