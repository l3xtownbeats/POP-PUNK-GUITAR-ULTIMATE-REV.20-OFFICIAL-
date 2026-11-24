#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "LibraryManager"))
from pattern_clip_registry import load_pattern_clip_registry


class PatternClipRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "clips").mkdir()
        (self.root / "licenses").mkdir()
        (self.root / "licenses" / "CC0.txt").write_text("CC0 license evidence fixture", encoding="utf-8")
        self.clip = self.root / "clips" / "fixture.wav"
        with wave.open(str(self.clip), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(48000)
            wav.writeframes(b"\x00\x00" * 4800)
        digest = hashlib.sha256(self.clip.read_bytes()).hexdigest().upper()
        self.record = {
            "asset_id": "TEST-CLIP-001",
            "kind": "note_event",
            "engine_targets": ["PATTERN_MODE"],
            "source_path": "external-source-library/guitar-source.wav",
            "source_sha256": "A" * 64,
            "source_start_sample": 1200,
            "source_end_sample": 6000,
            "sample_rate": 48000,
            "frame_count": 4800,
            "clip_path": "clips/fixture.wav",
            "derived_sha256": digest,
            "license_status": "LICENSE_APPROVED",
            "license": {
                "spdx_id": "CC0-1.0",
                "source_url": "https://example.org/source",
                "evidence_path": "licenses/CC0.txt",
                "reviewed_by": "test reviewer",
                "reviewed_at_utc": "2026-11-24T00:00:00Z"
            },
            "musical_review": {
                "status": "APPROVED",
                "reviewed_by": "test reviewer",
                "reviewed_at_utc": "2026-11-24T00:00:00Z",
                "boundary_basis": "human-auditioned-sample-boundaries"
            },
            "mapping": {
                "trigger_midi_note": 60,
                "source_midi_note": 60,
                "articulation_id": "open",
                "velocity_min": 1,
                "velocity_max": 127,
                "round_robin_group": "RR-1"
            }
        }
        self.manifest = self.root / "pattern_clips.json"

    def tearDown(self):
        self.tmp.cleanup()

    def write_manifest(self, clips=None):
        self.manifest.write_text(json.dumps({
            "schema_version": 1,
            "clips": [self.record] if clips is None else clips
        }), encoding="utf-8")

    def test_valid_manifest_publishes_immutable_ready_mapping(self):
        self.write_manifest()
        result = load_pattern_clip_registry(self.manifest)
        self.assertTrue(result.ready)
        self.assertEqual(result.status, "READY_VALIDATED")
        self.assertEqual(result.mappings[0].trigger_midi_note, 60)
        with self.assertRaises(Exception):
            result.mappings[0].trigger_midi_note = 61

    def test_empty_registry_is_valid_but_never_ready(self):
        self.write_manifest([])
        result = load_pattern_clip_registry(self.manifest)
        self.assertFalse(result.ready)
        self.assertEqual(result.status, "EMPTY_NO_APPROVED_CLIPS")
        self.assertEqual(result.mappings, ())

    def test_unapproved_license_is_rejected(self):
        self.record["license_status"] = "UNREVIEWED"
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "LICENSE_APPROVED"):
            load_pattern_clip_registry(self.manifest)

    def test_unreviewed_musical_boundaries_are_rejected(self):
        self.record["musical_review"]["status"] = "NEEDS_MUSICAL_REVIEW"
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "musical_review APPROVED"):
            load_pattern_clip_registry(self.manifest)

    def test_clip_hash_mismatch_is_rejected(self):
        self.record["derived_sha256"] = "B" * 64
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            load_pattern_clip_registry(self.manifest)

    def test_path_traversal_is_rejected(self):
        self.record["clip_path"] = "../outside.wav"
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "safe relative path"):
            load_pattern_clip_registry(self.manifest)

    def test_license_evidence_must_be_packaged(self):
        self.record["license"]["evidence_path"] = "licenses/missing.txt"
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "does not exist"):
            load_pattern_clip_registry(self.manifest)

    def test_sample_range_must_match_frame_count(self):
        self.record["source_end_sample"] = 6001
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "frame_count"):
            load_pattern_clip_registry(self.manifest)

    def test_midi_key_range_is_bounded(self):
        self.record["mapping"]["trigger_midi_note"] = 128
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, "MIDI notes"):
            load_pattern_clip_registry(self.manifest)

    def test_velocity_layers_must_not_overlap(self):
        second = json.loads(json.dumps(self.record))
        second["asset_id"] = "TEST-CLIP-002"
        second["mapping"]["velocity_min"] = 100
        self.record["mapping"]["velocity_max"] = 110
        self.write_manifest([self.record, second])
        with self.assertRaisesRegex(ValueError, "Overlapping velocity zones"):
            load_pattern_clip_registry(self.manifest)

    def test_round_robin_lanes_can_share_velocity_zone(self):
        second = json.loads(json.dumps(self.record))
        second["asset_id"] = "TEST-CLIP-002"
        second["mapping"]["round_robin_group"] = "RR-2"
        self.write_manifest([self.record, second])
        result = load_pattern_clip_registry(self.manifest)
        self.assertEqual(len(result.mappings), 2)

    def test_registry_rejects_duplicate_asset_ids(self):
        self.write_manifest([self.record, self.record])
        with self.assertRaisesRegex(ValueError, "Duplicate asset_id"):
            load_pattern_clip_registry(self.manifest)


if __name__ == "__main__":
    unittest.main()
