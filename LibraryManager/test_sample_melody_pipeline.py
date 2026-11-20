import hashlib
import math
import shutil
import struct
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

import sample_melody_pipeline as pipeline


def _hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _write_test_wav(path, rate=8000, seconds=2.0):
    frames = []
    for index in range(int(rate * seconds)):
        value = int(7000 * math.sin(2 * math.pi * 440 * index / rate))
        frames.append(struct.pack("<h", value))
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(b"".join(frames))


class SampleMelodyPipelineTests(unittest.TestCase):
    def test_creates_note_samples_and_grouped_melody_with_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.wav"
            _write_test_wav(source)
            rate = 8000
            events = []
            for index, (start, end, midi) in enumerate([
                (0.10, 0.30, 69), (0.42, 0.62, 71), (0.74, 0.94, 72)
            ], 1):
                a, b = round(start * rate), round(end * rate)
                events.append({
                    "segment_id": f"NOTE-{index:04d}",
                    "source_start_sample": a,
                    "source_end_sample": b,
                    "source_start_seconds": a / rate,
                    "source_end_seconds": b / rate,
                    "detected_note_start_seconds": start,
                    "detected_note_end_seconds": end,
                    "midi_note_candidate": midi,
                    "note_name_candidate": "CANDIDATE",
                    "confidence": 0.8,
                })
            fake_report = {
                "source_sha256": _hash(source),
                "sample_rate": rate,
                "segments": events,
            }
            stage = pipeline.STAGING_BASE / ("test-sample-melody-" + next(tempfile._get_candidate_names()))
            try:
                with patch.object(pipeline, "propose_segments", return_value=fake_report):
                    result = pipeline.prepare_sample_and_melody(source, stage)
                    repeated = pipeline.prepare_sample_and_melody(source, stage)
                self.assertEqual(result["sample_mode_count"], 3)
                self.assertEqual(result["melody_note_mode_count"], 3)
                self.assertEqual(
                    [item["asset_id"] for item in result["sample_mode"]],
                    [item["asset_id"] for item in result["melody_note_mode"]],
                )
                for asset in result["melody_note_mode"]:
                    self.assertEqual(asset["musical_metadata"]["melody_asset_role"], "SINGLE_GUITAR_NOTE")
                    self.assertTrue(asset["musical_metadata"]["one_sound_one_note"])
                    self.assertIn("MELODY_MODE", asset["engine_targets"])
                self.assertTrue(all(item.get("reused_existing") is False
                                    for item in result["sample_mode"] + result["melody_mode"]))
                self.assertEqual(repeated["sample_mode_count"], 3)
                self.assertEqual(repeated["melody_note_mode_count"], 3)
                self.assertEqual(repeated["melody_mode_count"], 1)
                self.assertTrue(all(item.get("reused_existing") is True
                                    for item in repeated["sample_mode"] + repeated["melody_mode"]))
                self.assertEqual(result["melody_mode_count"], 1)
                self.assertFalse(result["source_modified"])
                self.assertEqual(result["review_status"], "NEEDS_MUSICAL_REVIEW")
                self.assertEqual(result["license_status"], "UNREVIEWED")
                for asset in result["sample_mode"] + result["melody_note_mode"] + result["melody_mode"]:
                    self.assertEqual(asset["source_sha256"], _hash(source))
                    self.assertTrue(Path(asset["derived_path"]).is_file())
                    with wave.open(asset["derived_path"], "rb") as clip:
                        self.assertEqual(clip.getframerate(), rate)
                        self.assertEqual(clip.getnframes(), asset["frame_count"])
                    self.assertTrue(Path(stage, "manifests", Path(asset["derived_path"]).stem + ".json").exists()
                                    or list((stage / "manifests").glob("*.json")))
            finally:
                shutil.rmtree(stage, ignore_errors=True)

    def test_sample_and_melody_extraction_from_aiff_source(self):
        try:
            import numpy as np
            import soundfile as sf
        except ImportError:
            self.skipTest("python-soundfile is unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "guitar.aiff"
            samples = (0.2 * np.sin(2 * np.pi * 330 * np.arange(16000) / 8000)).astype("float32")
            try:
                sf.write(str(source), samples, 8000, format="AIFF", subtype="PCM_16")
            except Exception:
                self.skipTest("libsndfile AIFF decoding/encoding unavailable")
            events = []
            for index, start in enumerate((0.1, 0.4, 0.7), 1):
                a, b = round(start * 8000), round((start + 0.2) * 8000)
                events.append({
                    "source_start_sample": a,
                    "source_end_sample": b,
                    "source_start_seconds": a / 8000,
                    "source_end_seconds": b / 8000,
                    "detected_note_start_seconds": start,
                    "detected_note_end_seconds": start + 0.2,
                    "midi_note_candidate": 60 + index,
                    "note_name_candidate": "CANDIDATE",
                    "confidence": 0.8,
                })
            fake_report = {
                "source_sha256": _hash(source),
                "sample_rate": 8000,
                "segments": events,
            }
            stage = pipeline.STAGING_BASE / ("test-aiff-sample-" + next(tempfile._get_candidate_names()))
            candidates = [{
                "start_seconds": event["detected_note_start_seconds"],
                "end_seconds": event["detected_note_end_seconds"],
                "midi_note_candidate": event["midi_note_candidate"],
                "note_name_candidate": event["note_name_candidate"],
                "confidence": event["confidence"],
            } for event in events]
            try:
                result = pipeline.prepare_sample_and_melody(
                    source, stage,
                    pre_roll_ms=0, post_roll_ms=0,
                    pitch_candidates=candidates,
                    expected_source_sha256=_hash(source),
                    source_metadata={
                        "note_candidate": "C4",
                        "velocity_candidate": "80",
                        "string_candidate": "2",
                        "articulation_candidates": "palm;mute",
                    },
                )
                self.assertEqual(result["sample_mode_count"], 3)
                self.assertEqual(result["melody_mode_count"], 1)
                self.assertEqual(result["sample_mode"][0]["source_format"], "AIFF")
                self.assertEqual(
                    result["sample_mode"][0]["musical_metadata"]["source_filename_metadata"]["velocity_candidate"],
                    "80",
                )
                with wave.open(result["sample_mode"][0]["derived_path"], "rb") as clip:
                    self.assertEqual(clip.getframerate(), 8000)
                    self.assertEqual(clip.getnframes(), 1600)
            finally:
                shutil.rmtree(stage, ignore_errors=True)

    def test_total_sample_and_melody_outputs_respect_asset_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.wav"
            _write_test_wav(source)
            candidates = [
                {"start_seconds": start, "end_seconds": start + 0.12,
                 "midi_note_candidate": 60 + index,
                 "note_name_candidate": "CANDIDATE", "confidence": 0.8}
                for index, start in enumerate((0.10, 0.35, 0.60, 0.85, 1.10, 1.35), 1)
            ]
            stage = pipeline.STAGING_BASE / ("test-asset-cap-" + next(tempfile._get_candidate_names()))
            try:
                result = pipeline.prepare_sample_and_melody(
                    source, stage, pre_roll_ms=0, post_roll_ms=0,
                    pitch_candidates=candidates, expected_source_sha256=_hash(source),
                    max_note_events=20, max_assets=4,
                )
                total = result["sample_mode_count"] + result["melody_mode_count"]
                self.assertEqual(total, 4)
                self.assertEqual(result["sample_mode_count"], 3)
                self.assertEqual(result["melody_mode_count"], 1)
                self.assertEqual(result["max_assets"], 4)
            finally:
                shutil.rmtree(stage, ignore_errors=True)


    def test_existing_manifest_is_never_deleted_or_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.wav"
            _write_test_wav(source)
            stage = pipeline.STAGING_BASE / ("test-collision-" + next(tempfile._get_candidate_names()))
            candidates = [{
                "start_seconds": 0.2, "end_seconds": 0.4,
                "midi_note_candidate": 60, "note_name_candidate": "C4",
                "confidence": 0.9,
            }]
            # Account for the default 35 ms pre-roll and 220 ms post-roll.
            start = max(0, round(8000 * 0.2) - 280)
            end = round(8000 * 0.4) + 1760
            asset_id = pipeline._identity(_hash(source), "SAMPLE_NOTE", start, end)
            manifest = stage / "manifests" / f"SAMPLE-{asset_id}.json"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            sentinel = '{"do_not_delete": true}\\n'
            manifest.write_text(sentinel, encoding="utf-8")
            try:
                with self.assertRaises(FileExistsError):
                    pipeline.prepare_sample_and_melody(
                        source, stage, pitch_candidates=candidates,
                        expected_source_sha256=_hash(source),
                    )
                self.assertEqual(manifest.read_text(encoding="utf-8"), sentinel)
                self.assertFalse((stage / "clips" / f"SAMPLE-{asset_id}.wav").exists())
            finally:
                shutil.rmtree(stage, ignore_errors=True)

    def test_rejects_non_staging_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.wav"
            _write_test_wav(source)
            with self.assertRaises(ValueError):
                pipeline.prepare_sample_and_melody(source, Path(tmp) / "outside")


if __name__ == "__main__":
    unittest.main()
