import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch

import plugin_asset_catalog as catalog_module
import wave
from pathlib import Path

from plugin_asset_catalog import (
    CATALOG_SCHEMA, MODE_ORDER, build_plugin_asset_catalog,
    validate_plugin_asset_catalog,
)


def write_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(8000)
        output.writeframes(b"\x00\x00" * 800)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            value.update(block)
    return value.hexdigest().upper()


class PluginAssetCatalogTests(unittest.TestCase):
    def test_builds_all_modes_and_keeps_unreviewed_assets_non_playable(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            staging = base / "staging"
            manifests = staging / "manifests"
            clips = staging / "clips"
            manifests.mkdir(parents=True)
            clips.mkdir()
            source = base / "source.wav"
            derived = clips / "sample.wav"
            write_wav(source)
            write_wav(derived)
            manifest = {
                "asset_id": "ASSET-1",
                "kind": "sample_note_candidate",
                "source_path": str(source),
                "source_sha256": digest(source),
                "source_start_sample": 0,
                "source_end_sample": 800,
                "sample_rate": 8000,
                "channels": 1,
                "frame_count": 800,
                "duration_seconds": 0.1,
                "derived_path": str(derived),
                "derived_sha256": digest(derived),
                "engine_targets": ["SAMPLE_MODE", "KEYBOARD_PLAYBACK"],
                "musical_metadata": {"midi_note_candidate": 60},
                "review_status": "NEEDS_MUSICAL_REVIEW",
                "license_status": "UNREVIEWED",
            }
            (manifests / "asset.json").write_text(json.dumps(manifest), encoding="utf-8")
            strum_wav = clips / "strum.wav"
            write_wav(strum_wav)
            strum_manifest = dict(manifest)
            strum_manifest.update({
                "asset_id": "ASSET-STRUM",
                "kind": "audio_region_candidate",
                "derived_path": str(strum_wav),
                "derived_sha256": digest(strum_wav),
                "engine_targets": [],
                "mode_assignments": ["STRUMMING"],
            })
            (manifests / "strum.json").write_text(json.dumps(strum_manifest), encoding="utf-8")
            mode_report = base / "mode_sorting_report.json"
            mode_report.write_text(json.dumps({"modes": [
                {"mode": "RIFF MODE", "candidates": [{"candidate_type": "RIFF_OR_PHRASE_REVIEW"}]}
            ]}), encoding="utf-8")
            output = base / "plugin_asset_catalog.json"
            with patch.object(catalog_module, "STAGING_BASE", staging.resolve()):
                result = build_plugin_asset_catalog(staging, output, mode_report_path=mode_report)
            catalog = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(catalog["schema"], CATALOG_SCHEMA)
            self.assertEqual([item["mode"] for item in catalog["modes"]], list(MODE_ORDER))
            sample_mode = next(item for item in catalog["modes"] if item["mode"] == "SAMPLE MODE")
            self.assertEqual(sample_mode["asset_count"], 1)
            self.assertFalse(sample_mode["assets"][0]["playable"])
            self.assertEqual(sample_mode["assets"][0]["review_status"], "NEEDS_MUSICAL_REVIEW")
            strumming_mode = next(item for item in catalog["modes"] if item["mode"] == "STRUMMING")
            self.assertEqual(strumming_mode["asset_count"], 1)
            self.assertEqual(strumming_mode["assets"][0]["mode_assignments"], ["STRUMMING"])
            riff_mode = next(item for item in catalog["modes"] if item["mode"] == "RIFF MODE")
            self.assertEqual(riff_mode["candidate_count"], 1)
            self.assertEqual(result["playable_asset_count"], 0)
            self.assertEqual(validate_plugin_asset_catalog(catalog), [])

    def test_approved_asset_is_runtime_playable_only_after_full_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            staging = base / "staging"
            (staging / "manifests").mkdir(parents=True)
            (staging / "clips").mkdir()
            source = base / "source.wav"
            derived = staging / "clips" / "sample.wav"
            write_wav(source)
            write_wav(derived)
            record = {
                "asset_id": "ASSET-APPROVED",
                "kind": "sample_note_candidate",
                "source_path": str(source),
                "source_sha256": digest(source),
                "source_start_sample": 0,
                "source_end_sample": 800,
                "sample_rate": 8000,
                "channels": 1,
                "frame_count": 800,
                "duration_seconds": 0.1,
                "derived_path": str(derived),
                "derived_sha256": digest(derived),
                "engine_targets": ["SAMPLE_MODE", "MELODY_MODE"],
                "musical_metadata": {"melody_asset_role": "SINGLE_GUITAR_NOTE", "one_sound_one_note": True, "license_evidence": "User-owned recording; verified", "confirmed_midi_note": 60},
                "review_status": "REVIEWED",
                "license_status": "LICENSE_APPROVED",
                "review_validation": {
                    "musical_mapping_verified": True,
                    "source_sha256_verified": True,
                    "derived_sha256_verified": True,
                    "sample_boundaries_verified": True,
                    "explicit_musical_approval": True,
                    "explicit_license_approval": True,
                    "single_note_identity_verified": True,
                },
            }
            (staging / "manifests" / "approved.json").write_text(json.dumps(record), encoding="utf-8")
            pattern_derived = staging / "clips" / "pattern.wav"
            write_wav(pattern_derived)
            pattern_record = dict(record)
            pattern_record.update({
                "asset_id": "PATTERN-UNREADY",
                "kind": "audio_region_candidate",
                "derived_path": str(pattern_derived),
                "derived_sha256": digest(pattern_derived),
                "engine_targets": ["PATTERN_MODE"],
                "musical_metadata": dict(record["musical_metadata"]),
            })
            (staging / "manifests" / "pattern.json").write_text(json.dumps(pattern_record), encoding="utf-8")
            output = base / "catalog.json"
            with patch.object(catalog_module, "STAGING_BASE", staging.resolve()):
                result = build_plugin_asset_catalog(staging, output)
            catalog = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["playable_asset_count"], 1)
            self.assertEqual(catalog["status"], "READY_FOR_PLUGIN_IMPORT")
            self.assertEqual(catalog["playable_assets"][0]["asset_id"], "ASSET-APPROVED")
            self.assertTrue(catalog["playable_assets"][0]["playable"])
            sample_mode = next(item for item in catalog["modes"] if item["mode"] == "SAMPLE MODE")
            melody_mode = next(item for item in catalog["modes"] if item["mode"] == "MELODY MODE")
            self.assertEqual(sample_mode["asset_count"], 1)
            self.assertEqual(melody_mode["asset_count"], 1)
            self.assertEqual(sample_mode["assets"][0]["asset_id"], melody_mode["assets"][0]["asset_id"])
            self.assertTrue(melody_mode["assets"][0]["playable_in_mode"])
            pattern_mode = next(item for item in catalog["modes"] if item["mode"] == "PATTERN MODE")
            self.assertEqual(pattern_mode["asset_count"], 1)
            self.assertFalse(pattern_mode["assets"][0]["playable_in_mode"])

    def test_rejects_derived_asset_outside_staging_and_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            staging = base / "staging"
            (staging / "manifests").mkdir(parents=True)
            (staging / "clips").mkdir()
            source = base / "source.wav"
            outside = base / "outside.wav"
            write_wav(source)
            write_wav(outside)
            record = {
                "asset_id": "BAD",
                "kind": "sample_note_candidate",
                "source_path": str(source),
                "source_sha256": digest(source),
                "source_start_sample": 0,
                "source_end_sample": 800,
                "sample_rate": 8000,
                "channels": 1,
                "frame_count": 800,
                "derived_path": str(outside),
                "derived_sha256": "0" * 64,
                "engine_targets": ["SAMPLE_MODE"],
                "review_status": "REVIEWED",
                "license_status": "LICENSE_APPROVED",
                "musical_metadata": {"license_evidence": "evidence"},
                "review_validation": {"source_sha256_verified": True,
                    "derived_sha256_verified": True, "sample_boundaries_verified": True,
                    "explicit_musical_approval": True, "explicit_license_approval": True},
            }
            (staging / "manifests" / "bad.json").write_text(json.dumps(record), encoding="utf-8")
            output = base / "catalog.json"
            with patch.object(catalog_module, "STAGING_BASE", staging.resolve()):
                result = build_plugin_asset_catalog(staging, output)
            catalog = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(result["playable_asset_count"], 0)
            self.assertEqual(catalog["modes"][0]["assets"][0]["integrity_status"], "BLOCKED")
            self.assertGreaterEqual(result["integrity_error_count"], 2)

    def test_refuses_to_overwrite_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            staging = base / "staging"
            staging.mkdir()
            output = base / "catalog.json"
            output.write_text("sentinel", encoding="utf-8")
            with patch.object(catalog_module, "STAGING_BASE", staging.resolve()):
                with self.assertRaises(FileExistsError):
                    build_plugin_asset_catalog(staging, output)
            self.assertEqual(output.read_text(encoding="utf-8"), "sentinel")


if __name__ == "__main__":
    unittest.main()
