import json
import tempfile
import unittest
import wave
from pathlib import Path

from factory_curator import sha256_file
from manifest_reviewer import annotate_manifest


class ManifestReviewerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.staging = self.root / "LibraryManager" / "staging"
        self.clips = self.staging / "clips"
        self.clips.mkdir(parents=True)
        self.wav = self.clips / "candidate.wav"
        with wave.open(str(self.wav), "wb") as writer:
            writer.setnchannels(1)
            writer.setsampwidth(2)
            writer.setframerate(44100)
            writer.writeframes(b"\x02\x00" * 4410)
        self.manifest = self.wav.with_suffix(".json")
        self.record = {
            "derived_path": str(self.wav),
            "derived_sha256": sha256_file(self.wav),
            "review_status": "BOUNDARIES_USER_OR_REVIEWER_APPROVED",
            "license_status": "UNREVIEWED",
            "musical_metadata": {"bpm_candidate": 172, "articulations": ["PALM_MUTE"]}
        }
        self.manifest.write_text(json.dumps(self.record), encoding="utf-8")
        self.original_hash = sha256_file(self.wav)

    def tearDown(self):
        self.temp.cleanup()

    def test_explicit_tags_bridge_staging_manifest_to_curator(self):
        result = annotate_manifest(
            self.manifest, self.staging,
            instrument_family="ELECTRIC_GUITAR",
            asset_role="RHYTHM_PATTERN",
            tone_family="DISTORTION",
            reviewed_by="human reviewer",
            confirm_musical_review=True,
        )
        saved = json.loads(self.manifest.read_text(encoding="utf-8"))
        self.assertEqual(saved["review_status"], "REVIEWED")
        self.assertEqual(saved["musical_metadata"]["instrument_family"], "ELECTRIC_GUITAR")
        self.assertEqual(saved["musical_metadata"]["asset_role"], "RHYTHM_PATTERN")
        self.assertEqual(saved["musical_metadata"]["tone_family"], "DISTORTION")
        self.assertEqual(saved["musical_metadata"]["bpm_candidate"], 172)
        self.assertEqual(saved["license_status"], "UNREVIEWED")
        self.assertFalse(result["promotion_ready"])
        self.assertEqual(sha256_file(self.wav), self.original_hash)

    def test_requires_explicit_confirmation_and_valid_tags(self):
        with self.assertRaises(ValueError):
            annotate_manifest(
                self.manifest, self.staging,
                instrument_family="ELECTRIC_GUITAR", asset_role="RIFF",
                tone_family="CRUNCH", reviewed_by="reviewer",
            )
        with self.assertRaises(ValueError):
            annotate_manifest(
                self.manifest, self.staging,
                instrument_family="PIANO", asset_role="RIFF",
                tone_family="CRUNCH", reviewed_by="reviewer",
                confirm_musical_review=True,
            )

    def test_rejects_hash_mismatch_without_changing_manifest(self):
        self.record["derived_sha256"] = "0" * 64
        before = json.dumps(self.record)
        self.manifest.write_text(before, encoding="utf-8")
        with self.assertRaises(ValueError):
            annotate_manifest(
                self.manifest, self.staging,
                instrument_family="ELECTRIC_GUITAR", asset_role="RIFF",
                tone_family="CRUNCH", reviewed_by="reviewer",
                confirm_musical_review=True,
            )
        self.assertEqual(self.manifest.read_text(encoding="utf-8"), before)

    def test_manifest_outside_staging_is_rejected(self):
        outside = self.root / "outside.json"
        outside.write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError):
            annotate_manifest(
                outside, self.staging,
                instrument_family="ELECTRIC_GUITAR", asset_role="RIFF",
                tone_family="CRUNCH", reviewed_by="reviewer",
                confirm_musical_review=True,
            )


if ( __name__ == "__main__" ):
    unittest.main()
