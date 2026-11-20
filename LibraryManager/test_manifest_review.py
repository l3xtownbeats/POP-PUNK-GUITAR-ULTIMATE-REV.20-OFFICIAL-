from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import wave
from pathlib import Path

from manifest_review import review_manifest


def write_wav(path: Path, frames: int = 1000) -> None:
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(8000)
        out.writeframes(b"\x01\x00" * frames)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class ManifestReviewTests(unittest.TestCase):
    def test_explicit_review_validates_source_clip_and_records_approvals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staging = root / "staging"
            clips = staging / "clips"
            manifests = staging / "manifests"
            clips.mkdir(parents=True)
            manifests.mkdir()
            source = root / "original.wav"
            clip = clips / "clip.wav"
            write_wav(source, 1000)
            write_wav(clip, 400)
            manifest = manifests / "clip.json"
            manifest.write_text(json.dumps({
                "asset_id": "TEST-001",
                "source_path": str(source),
                "source_sha256": sha(source),
                "source_start_sample": 100,
                "source_end_sample": 500,
                "derived_path": str(clip),
                "derived_sha256": sha(clip),
                "musical_metadata": {},
                "review_status": "NEEDS_MUSICAL_REVIEW",
                "license_status": "UNREVIEWED",
            }), encoding="utf-8")
            result = review_manifest(
                manifest, staging,
                style_family="POP_PUNK",
                instrument_family="ELECTRIC_GUITAR",
                asset_role="RHYTHM_PATTERN",
                tone_family="CRUNCH",
                musical_review_notes="Listened to the whole clip and confirmed boundaries.",
                license_evidence="Original source license permits redistribution of derived WAV.",
                approve_musical_review=True,
                approve_license=True,
            )
            record = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(result["review_status"], "REVIEWED")
            self.assertEqual(record["license_status"], "LICENSE_APPROVED")
            self.assertEqual(record["musical_metadata"]["style_family"], "POP_PUNK")
            self.assertEqual(record["musical_metadata"]["format_family"], "WAV")
            self.assertTrue(record["review_validation"]["source_sha256_verified"])

    def test_review_records_only_explicit_valid_mode_assignments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staging = root / "staging"
            (staging / "clips").mkdir(parents=True)
            (staging / "manifests").mkdir()
            source = root / "original.wav"
            clip = staging / "clips" / "clip.wav"
            write_wav(source, 1000)
            write_wav(clip, 400)
            manifest = staging / "manifests" / "clip.json"
            manifest.write_text(json.dumps({
                "asset_id": "MODE-TEST",
                "source_path": str(source),
                "source_sha256": sha(source),
                "source_start_sample": 100,
                "source_end_sample": 500,
                "derived_path": str(clip),
                "derived_sha256": sha(clip),
                "musical_metadata": {},
                "review_status": "NEEDS_MUSICAL_REVIEW",
                "license_status": "UNREVIEWED",
            }), encoding="utf-8")
            result = review_manifest(
                manifest, staging,
                style_family="POP_PUNK",
                instrument_family="ELECTRIC_GUITAR",
                asset_role="RHYTHM_PATTERN",
                tone_family="CRUNCH",
                musical_review_notes="Confirmed musical content and boundaries.",
                license_evidence="Source license explicitly permits derived WAV distribution.",
                approve_musical_review=True,
                approve_license=True,
                mode_assignments=["SAMPLE MODE", "MELODY MODE"],
                confirmed_midi_note=60,
            )
            record = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(record["mode_assignments"], ["SAMPLE MODE", "MELODY MODE"])
            self.assertEqual(result["mode_assignments"], ["SAMPLE MODE", "MELODY MODE"])
            self.assertEqual(record["musical_metadata"]["confirmed_midi_note"], 60)
            self.assertTrue(result["musical_mapping_verified"])

    def test_review_records_confirmed_techniques_velocity_and_mode_event_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staging = root / "staging"
            (staging / "clips").mkdir(parents=True)
            (staging / "manifests").mkdir()
            source = root / "original.wav"
            clip = staging / "clips" / "clip.wav"
            write_wav(source, 1000)
            write_wav(clip, 400)
            manifest = staging / "manifests" / "clip.json"
            manifest.write_text(json.dumps({
                "asset_id": "STRUCTURE-TEST", "source_path": str(source),
                "source_sha256": sha(source), "source_start_sample": 100,
                "source_end_sample": 500, "derived_path": str(clip),
                "derived_sha256": sha(clip), "musical_metadata": {},
            }), encoding="utf-8")
            pattern = {
                "loop_start_sample": 0, "loop_end_sample": 400, "tempo_bpm": 170,
                "time_signature": "4/4", "attack_events": [{"sample": 0}],
                "beat_grid": [0, 100, 200, 300],
                "technique_events": [{"sample": 0, "technique": "DOWNSTROKE"}],
                "harmonic_events": [{"sample": 0, "chord": "C5"}],
                "cycle_integrity_verified": True, "musical_review_verified": True,
            }
            melody_events = [
                {"midi_note": 60, "start_beats": 0, "duration_beats": 1, "velocity": 90},
                {"midi_note": 62, "start_beats": 1, "duration_beats": 1, "velocity": 100},
            ]
            review_manifest(
                manifest, staging, style_family="POP_PUNK",
                instrument_family="ELECTRIC_GUITAR", asset_role="RHYTHM_PATTERN",
                tone_family="CRUNCH", musical_review_notes="Pattern and melody events checked.",
                license_evidence="Distribution license verified.", approve_musical_review=True,
                approve_license=True, mode_assignments=["PATTERN MODE", "MELODY MODE"],
                confirmed_note_sequence=[60, 62],
                confirmed_techniques=["DOWNSTROKE", "PALM_MUTE"],
                confirmed_velocity_layer="HIGH",
                advanced_metadata={
                    "pattern_performance_review": pattern,
                    "confirmed_melody_events": melody_events,
                    "melody_phrase_boundaries": [0, 2],
                    "melody_mapping_verified": True,
                    "velocity_min": 90, "velocity_max": 110,
                },
            )
            metadata = json.loads(manifest.read_text(encoding="utf-8"))["musical_metadata"]
            self.assertEqual(metadata["confirmed_techniques"], ["DOWNSTROKE", "PALM_MUTE"])
            self.assertEqual(metadata["confirmed_velocity_layer"], "HIGH")
            self.assertEqual(metadata["pattern_performance_review"]["loop_end_sample"], 400)
            self.assertEqual(len(metadata["confirmed_melody_events"]), 2)
            self.assertTrue(metadata["melody_mapping_verified"])

    def test_license_unknown_cannot_be_approved_without_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staging = root / "staging"
            (staging / "clips").mkdir(parents=True)
            (staging / "manifests").mkdir()
            source = root / "original.wav"
            clip = staging / "clips" / "clip.wav"
            write_wav(source, 1000)
            write_wav(clip, 400)
            manifest = staging / "manifests" / "clip.json"
            manifest.write_text(json.dumps({
                "source_path": str(source), "source_sha256": sha(source),
                "source_start_sample": 0, "source_end_sample": 400,
                "derived_path": str(clip), "derived_sha256": sha(clip),
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                review_manifest(
                    manifest, staging,
                    style_family="POP_PUNK",
                    instrument_family="ELECTRIC_GUITAR",
                    asset_role="INDIVIDUAL_NOTE",
                    tone_family="CLEAN",
                    musical_review_notes="Reviewed.",
                    license_evidence="",
                    approve_musical_review=True,
                    approve_license=True,
                )


if __name__ == "__main__":
    unittest.main()
