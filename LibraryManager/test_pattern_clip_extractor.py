import hashlib
import math
import shutil
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from audio_segmenter import STAGING_BASE, sha256_file
from pattern_clip_extractor import extract_pattern_occurrences


def write_wav(path: Path, rate: int = 8000) -> None:
    frames = []
    for i in range(rate * 3):
        value = int(9000 * math.sin(2 * math.pi * 220 * i / rate))
        frames.append(struct.pack("<h", value))
    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(rate)
        writer.writeframes(b"".join(frames))


class PatternClipExtractorTests(unittest.TestCase):
    def test_extracts_each_repeated_occurrence_with_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.wav"
            write_wav(source)
            digest = sha256_file(source)
            report = {
                "source": str(source),
                "source_sha256": digest,
                "pattern_analysis": {"patterns": [{
                    "pattern_candidate_id": "ABC123",
                    "pattern_signature_units": [1, 2, 1],
                    "occurrences": [
                        {"start_seconds": 0.4, "end_seconds": 0.9},
                        {"start_seconds": 1.4, "end_seconds": 1.9},
                    ],
                }]},
            }
            stage = STAGING_BASE / ("pattern-test-" + next(tempfile._get_candidate_names()))
            try:
                before = hashlib.sha256(source.read_bytes()).hexdigest().upper()
                records = extract_pattern_occurrences(report, stage, pre_roll_ms=20, post_roll_ms=30)
                reused = extract_pattern_occurrences(report, stage, pre_roll_ms=20, post_roll_ms=30)
                self.assertEqual(len(records), 2)
                self.assertTrue(all(item.get("reused_existing") is False for item in records))
                self.assertEqual(len(reused), 2)
                self.assertTrue(all(item.get("reused_existing") is True for item in reused))
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest().upper(), before)
                for record in records:
                    clip = Path(record["derived_path"])
                    self.assertTrue(clip.is_file())
                    self.assertEqual(sha256_file(clip), record["derived_sha256"])
                    self.assertEqual(record["source_sha256"], digest)
                    self.assertEqual(record["review_status"], "NEEDS_MUSICAL_REVIEW")
                    self.assertEqual(record["license_status"], "UNREVIEWED")
                    with wave.open(str(clip), "rb") as wav:
                        self.assertEqual(wav.getframerate(), 8000)
                        self.assertEqual(wav.getnchannels(), 1)
            finally:
                shutil.rmtree(stage, ignore_errors=True)

    def test_extracts_aiff_to_pcm_wav_when_decoder_supports_format(self):
        try:
            import numpy as np
            import soundfile as sf
        except ImportError:
            self.skipTest("python-soundfile is unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.aiff"
            samples = (0.2 * np.sin(2 * np.pi * 220 * np.arange(24000) / 8000)).astype("float32")
            try:
                sf.write(str(source), samples, 8000, format="AIFF", subtype="PCM_16")
            except Exception:
                self.skipTest("libsndfile AIFF decoding/encoding unavailable")
            report = {
                "source": str(source),
                "source_sha256": sha256_file(source),
                "pattern_analysis": {"patterns": [{
                    "pattern_candidate_id": "AIFF-001",
                    "occurrences": [{"start_seconds": 0.4, "end_seconds": 0.9}],
                }]},
            }
            stage = STAGING_BASE / ("pattern-aiff-" + next(tempfile._get_candidate_names()))
            try:
                records = extract_pattern_occurrences(
                    report, stage, pre_roll_ms=0, post_roll_ms=0,
                )
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0]["source_format"], "AIFF")
                self.assertEqual(records[0]["derived_subtype"], "PCM_24")
                with wave.open(records[0]["derived_path"], "rb") as clip:
                    self.assertEqual(clip.getframerate(), 8000)
                    self.assertEqual(clip.getnframes(), 4000)
            finally:
                shutil.rmtree(stage, ignore_errors=True)

    def test_rolls_back_all_created_clips_when_batch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.wav"
            write_wav(source)
            report = {
                "source": str(source), "source_sha256": sha256_file(source),
                "pattern_analysis": {"patterns": [{
                    "pattern_candidate_id": "ROLLBACK",
                    "occurrences": [
                        {"start_seconds": 0.4, "end_seconds": 0.9},
                        {"start_seconds": 0.4, "end_seconds": 0.9},
                    ],
                }]},
            }
            stage = STAGING_BASE / ("pattern-rollback-" + next(tempfile._get_candidate_names()))
            try:
                with self.assertRaises(FileExistsError):
                    extract_pattern_occurrences(report, stage, pre_roll_ms=0, post_roll_ms=0)
                self.assertFalse(list((stage / "clips").glob("*.wav")) if (stage / "clips").exists() else [])
                self.assertFalse(list((stage / "manifests").glob("*.json")) if (stage / "manifests").exists() else [])
            finally:
                shutil.rmtree(stage, ignore_errors=True)

    def test_refuses_changed_source_and_outside_staging(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.wav"
            write_wav(source)
            report = {
                "source": str(source), "source_sha256": sha256_file(source),
                "pattern_analysis": {"patterns": []},
            }
            with self.assertRaises(ValueError):
                extract_pattern_occurrences(report, Path(tmp) / "outside")
            source.write_bytes(source.read_bytes() + b"x")
            stage = STAGING_BASE / ("pattern-test-" + next(tempfile._get_candidate_names()))
            try:
                with self.assertRaises(RuntimeError):
                    extract_pattern_occurrences(report, stage)
            finally:
                shutil.rmtree(stage, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
