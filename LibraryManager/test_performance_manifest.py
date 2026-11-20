import json
import tempfile
import unittest
from pathlib import Path

from plugin_asset_catalog import CATALOG_SCHEMA, MODE_ORDER
from performance_manifest import (
    PERFORMANCE_SCHEMA, build_performance_manifest, validate_performance_manifest,
)


class PerformanceManifestTests(unittest.TestCase):
    def test_builds_all_mode_contracts_without_inventing_event_timing(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            catalog = {
                "schema": CATALOG_SCHEMA,
                "modes": [
                    {"mode": mode, "assets": [], "candidates": []}
                    for mode in MODE_ORDER
                ],
            }
            catalog["modes"][0]["assets"] = [{
                "asset_id": "SAMPLE-1",
                "kind": "sample_note_candidate",
                "asset_file": "../staging/clips/SAMPLE-1.wav",
                "source_path": "F:/guitar.wav",
                "source_sha256": "A" * 64,
                "source_start_sample": 0,
                "source_end_sample": 1000,
                "sample_rate": 44100,
                "channels": 2,
                "frame_count": 1000,
                "derived_sha256": "B" * 64,
                "review_status": "NEEDS_MUSICAL_REVIEW",
                "license_status": "UNREVIEWED",
                "integrity_status": "VERIFIED",
                "playable": False,
                "target_modes": ["SAMPLE MODE"],
            }]
            arpeggio = next(item for item in catalog["modes"] if item["mode"] == "ARPEGGIO")
            arpeggio["candidates"] = [{
                "candidate_id": "VOICING-CANDIDATE-1",
                "candidate_type": "ARPEGGIO_VOICING_HYPOTHESIS",
                "voicing_candidates": [{"voicing_candidate_id": "VOICING-001",
                                        "review_status": "NEEDS_MUSICAL_REVIEW"}],
                "tuning_status": "NEEDS_CONFIRMATION",
            }]
            catalog_path = base / "plugin_asset_catalog.json"
            output = base / "performance_manifest.json"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            result = build_performance_manifest(catalog_path, output)
            manifest = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema"], PERFORMANCE_SCHEMA)
            self.assertEqual(result["mode_count"], 10)
            self.assertEqual(manifest["event_count"], 0)
            self.assertEqual(manifest["events"], [])
            self.assertTrue(manifest["event_contract"]["unknown_timing_must_remain_unknown"])
            self.assertEqual(manifest["asset_bindings"][0]["asset_id"], "SAMPLE-1")
            self.assertEqual([item["pitch_class"] for item in manifest["chromatic_pitch_map"]["pitch_classes"]], list(range(12)))
            self.assertTrue(manifest["chromatic_pitch_map"]["enharmonic_aliases_are_merged"])
            self.assertTrue(manifest["midi_contract"]["autochords_uses_same_canonical_pitch_classes"])
            self.assertEqual(manifest["mode_candidate_bindings"]["ARPEGGIO"][0]["candidate_type"], "ARPEGGIO_VOICING_HYPOTHESIS")
            self.assertEqual(validate_performance_manifest(manifest), [])

    def test_rejects_unreviewed_runtime_event(self):
        manifest = {
            "schema": PERFORMANCE_SCHEMA,
            "mode_execution_models": [{"mode": mode} for mode in MODE_ORDER],
            "mode_asset_bindings": {mode: [] for mode in MODE_ORDER},
            "events": [{
                "event_id": "E1", "position_ticks": 0, "duration_ticks": 100,
                "event_kind": "NOTE_ON", "review_status": "NEEDS_MUSICAL_REVIEW",
                "source_sha256": "A" * 64, "source_start_sample": 0,
                "source_end_sample": 100,
            }],
            "event_count": 1,
            "safety": {"events_invented": False},
        }
        self.assertTrue(any("Unreviewed performance events" in error
                            for error in validate_performance_manifest(manifest)))


if __name__ == "__main__":
    unittest.main()
