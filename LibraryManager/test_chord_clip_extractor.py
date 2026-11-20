import hashlib
import json
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

import chord_clip_extractor as extractor
import audio_segmenter


def write_wav(path: Path, frames: int = 16000) -> None:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(8000)
        output.writeframes(b"\x00\x00" * frames)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            value.update(block)
    return value.hexdigest().upper()


class ChordClipExtractorTests(unittest.TestCase):
    def test_extracts_chord_and_power_chord_with_exact_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            staging = base / "staging"
            source = base / "guitar.wav"
            write_wav(source)
            report = {
                "source_path": str(source),
                "source_sha256": digest(source),
                "chord_candidates": [
                    {"start_seconds": 0.2, "end_seconds": 0.5,
                     "chord_name_candidate": "C", "quality": "MAJOR",
                     "root_pitch_class": "C", "pitch_classes_candidate": ["C", "E", "G"],
                     "confidence": 0.91},
                    {"start_seconds": 0.8, "end_seconds": 1.1,
                     "chord_name_candidate": "G5", "quality": "POWER5",
                     "root_pitch_class": "G", "pitch_classes_candidate": ["G", "D"],
                     "confidence": 0.88},
                ],
            }
            with patch.object(extractor, "STAGING_BASE", staging.resolve()), \
                 patch.object(audio_segmenter, "STAGING_BASE", staging.resolve()):
                results = extractor.extract_chord_samples(report, staging)
            self.assertEqual(len(results), 2)
            self.assertEqual({item["kind"] for item in results},
                             {"chord_sample_candidate", "power_chord_sample_candidate"})
            for item in results:
                self.assertEqual(item["source_sha256"], digest(source))
                self.assertEqual(item["frame_count"],
                                 item["source_end_sample"] - item["source_start_sample"])
                self.assertEqual(item["review_status"], "NEEDS_MUSICAL_REVIEW")
                self.assertEqual(item["license_status"], "UNREVIEWED")
                self.assertEqual(item["musical_metadata"]["voicing_candidate"], "UNKNOWN")
                self.assertTrue(Path(item["derived_path"]).is_file())
                manifest = Path(staging / "manifests" / (Path(item["derived_path"]).stem + ".json"))
                self.assertTrue(manifest.is_file())

    def test_refuses_changed_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            staging = base / "staging"
            source = base / "guitar.wav"
            write_wav(source)
            report = {"source_path": str(source), "source_sha256": "0" * 64,
                      "chord_candidates": []}
            with patch.object(extractor, "STAGING_BASE", staging.resolve()), \
                 patch.object(audio_segmenter, "STAGING_BASE", staging.resolve()):
                with self.assertRaisesRegex(RuntimeError, "SHA-256 changed"):
                    extractor.extract_chord_samples(report, staging)


    def test_pre_cancelled_batch_writes_no_assets(self):
        import threading
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            staging = base / "staging"
            source = base / "guitar.wav"
            write_wav(source)
            report = {
                "source_path": str(source),
                "source_sha256": digest(source),
                "chord_candidates": [{"start_seconds": 0.2, "end_seconds": 0.5}],
            }
            event = threading.Event()
            event.set()
            with patch.object(extractor, "STAGING_BASE", staging.resolve()), \
                 patch.object(audio_segmenter, "STAGING_BASE", staging.resolve()):
                with self.assertRaisesRegex(RuntimeError, "cancelled"):
                    extractor.extract_chord_samples(report, staging, cancel_event=event)
            self.assertFalse(list((staging / "clips").glob("*.wav")) if (staging / "clips").exists() else [])
            self.assertFalse(list((staging / "manifests").glob("*.json")) if (staging / "manifests").exists() else [])



if __name__ == "__main__":
    unittest.main()
