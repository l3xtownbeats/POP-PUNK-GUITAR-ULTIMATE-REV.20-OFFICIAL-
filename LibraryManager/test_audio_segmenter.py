import math
import shutil
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from audio_segmenter import STAGING_BASE, extract_segments, propose_segments, sha256_file


def write_notes(path: Path, rate=16000):
    samples = []
    for frequency, seconds in [(440.0, 0.45), (None, 0.12), (523.25, 0.45)]:
        for i in range(int(rate * seconds)):
            value = 0 if frequency is None else int(
                12000 * math.sin(2 * math.pi * frequency * i / rate))
            samples.append(struct.pack("<h", value))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(b"".join(samples))


class AudioSegmenterTests(unittest.TestCase):
    def test_dry_run_only_proposes_ranges_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "phrase.wav"
            write_notes(source)
            before = sha256_file(source)
            report = propose_segments(source)
            self.assertFalse(report["extraction_performed"])
            self.assertGreaterEqual(report["candidate_count"], 1)
            self.assertEqual(sha256_file(source), before)
            self.assertTrue(all(x["review_status"] == "NEEDS_MUSICAL_REVIEW"
                                for x in report["segments"]))
            self.assertTrue(all(x["pre_roll_ms"] >= 0 and x["post_roll_ms"] >= 0
                                for x in report["segments"]))

    def test_extracts_pcm_to_staging_and_keeps_source_format_and_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "phrase.wav"
            write_notes(source)
            before = sha256_file(source)
            report = propose_segments(source)
            stage = STAGING_BASE / ("test-" + next(tempfile._get_candidate_names()))
            try:
                records = extract_segments(report, stage)
                self.assertTrue(records)
                self.assertEqual(sha256_file(source), before)
                with wave.open(records[0]["derived_path"], "rb") as clip:
                    self.assertEqual(clip.getframerate(), 16000)
                    self.assertEqual(clip.getnchannels(), 1)
                    self.assertEqual(clip.getsampwidth(), 2)
                self.assertEqual(records[0]["license_status"], "UNREVIEWED")
                self.assertEqual(records[0]["review_status"], "NEEDS_MUSICAL_REVIEW")
            finally:
                shutil.rmtree(stage, ignore_errors=True)

    def test_rejects_output_outside_staging(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "phrase.wav"
            write_notes(source)
            report = propose_segments(source)
            with self.assertRaises(ValueError):
                extract_segments(report, Path(tmp) / "outside")

    def test_existing_staged_asset_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "phrase.wav"
            write_notes(source)
            report = propose_segments(source)
            stage = STAGING_BASE / ("test-" + next(tempfile._get_candidate_names()))
            try:
                extract_segments(report, stage)
                with self.assertRaises(FileExistsError):
                    extract_segments(report, stage)
            finally:
                shutil.rmtree(stage, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
