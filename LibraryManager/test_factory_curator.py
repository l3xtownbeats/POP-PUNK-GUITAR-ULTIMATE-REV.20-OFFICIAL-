import json
import tempfile
import unittest
import wave
from pathlib import Path

from factory_curator import promote_asset, promotion_plan, sha256_file


class FactoryCuratorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.staging = self.root / "LibraryManager" / "staging"
        self.clips = self.staging / "clips"
        self.clips.mkdir(parents=True)
        self.factory = self.root / "SAMPLES" / "FACTORY"
        self.wav = self.clips / "approved.wav"
        with wave.open(str(self.wav), "wb") as writer:
            writer.setnchannels(1)
            writer.setsampwidth(2)
            writer.setframerate(44100)
            writer.writeframes(b"\x01\x00" * 4410)
        self.manifest = self.wav.with_suffix(".json")
        self.record = {
            "derived_path": str(self.wav),
            "derived_sha256": sha256_file(self.wav),
            "review_status": "REVIEWED",
            "license_status": "LICENSE_APPROVED",
            "review_validation": {
                "source_sha256_verified": True,
                "derived_sha256_verified": True,
                "sample_boundaries_verified": True,
                "explicit_musical_approval": True,
                "explicit_license_approval": True,
            },
            "musical_metadata": {
                "style_family": "POP_PUNK",
                "instrument_family": {"value": "ELECTRIC_GUITAR"},
                "asset_role": "RHYTHM_PATTERN",
                "tone_family": "DISTORTION",
                "musical_review_notes": "Reviewed by listening.",
                "license_evidence": "License allows redistribution."
            }
        }
        self.manifest.write_text(json.dumps(self.record), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_dry_run_proposes_canonical_group_without_copying(self):
        result = promotion_plan(self.manifest, self.factory, self.staging)
        self.assertEqual(result["group_path"], "POP_PUNK/WAV/ELECTRIC_GUITAR/RHYTHM_PATTERN/DISTORTION")
        self.assertEqual(result["operation"], "COPY_ONLY")
        self.assertFalse(self.factory.exists())

    def test_requires_explicit_approval_and_preserves_staging_source(self):
        result = promote_asset(self.manifest, self.factory, self.staging)
        self.assertEqual(result["promotion_status"], "READY_FOR_EXPLICIT_APPROVAL")
        self.assertFalse(self.factory.exists())
        source_hash = sha256_file(self.wav)
        copied = promote_asset(self.manifest, self.factory, self.staging, approve=True)
        self.assertEqual(copied["promotion_status"], "COPIED_TO_FACTORY")
        self.assertTrue(Path(copied["destination_path"]).is_file())
        self.assertEqual(sha256_file(self.wav), source_hash)
        self.assertTrue(Path(copied["sidecar_path"]).is_file())

    def test_rejects_unreviewed_or_unlicensed_assets(self):
        self.record["license_status"] = "UNREVIEWED"
        self.manifest.write_text(json.dumps(self.record), encoding="utf-8")
        with self.assertRaises(ValueError):
            promotion_plan(self.manifest, self.factory, self.staging)
        self.record["license_status"] = "LICENSE_APPROVED"
        self.record["review_status"] = "NEEDS_MUSICAL_REVIEW"
        self.manifest.write_text(json.dumps(self.record), encoding="utf-8")
        with self.assertRaises(ValueError):
            promotion_plan(self.manifest, self.factory, self.staging)

    def test_rejects_source_hash_mismatch_and_unknown_folder_tags(self):
        self.record["derived_sha256"] = "0" * 64
        self.manifest.write_text(json.dumps(self.record), encoding="utf-8")
        with self.assertRaises(ValueError):
            promotion_plan(self.manifest, self.factory, self.staging)
        self.record["derived_sha256"] = sha256_file(self.wav)
        self.record["musical_metadata"]["asset_role"] = "UNKNOWN"
        self.manifest.write_text(json.dumps(self.record), encoding="utf-8")
        with self.assertRaises(ValueError):
            promotion_plan(self.manifest, self.factory, self.staging)

    def test_refuses_overwrite(self):
        first = promote_asset(self.manifest, self.factory, self.staging, approve=True)
        with self.assertRaises(FileExistsError):
            promote_asset(self.manifest, self.factory, self.staging, approve=True)
        self.assertTrue(Path(first["destination_path"]).is_file())


if __name__ == "__main__":
    unittest.main()
