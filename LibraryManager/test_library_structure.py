from __future__ import annotations

import unittest

from library_structure import MODES, SCHEMA, build_library_structure, validate_library_structure


def _catalog(assets_by_mode=None):
    assets_by_mode = assets_by_mode or {}
    return {
        "schema": "ppgu.plugin_asset_catalog/1.0.0",
        "modes": [
            {"mode": mode, "assets": list(assets_by_mode.get(mode, []))}
            for mode in MODES
        ],
    }


class LibraryStructureTests(unittest.TestCase):
    def test_all_ten_modes_and_coverage_gaps_are_explicit(self):
        result = build_library_structure(_catalog())
        self.assertEqual(result["schema"], SCHEMA)
        self.assertEqual([x["mode"] for x in result["modes"]], list(MODES))
        self.assertEqual(len(result["coverage"]["pitch_classes"]), 12)
        self.assertTrue(all(x["status"] == "GAP" for x in result["coverage"]["pitch_classes"]))
        self.assertEqual(result["summary"]["unique_asset_count"], 0)
        self.assertEqual(validate_library_structure(result), [])

    def test_multi_mode_asset_is_logically_indexed_without_duplication(self):
        asset = {
            "asset_id": "A1", "asset_file": "staging/clips/a.wav", "manifest_file": "a.json",
            "kind": "note_event", "playable": True, "playable_in_mode": True,
            "review_status": "REVIEWED", "license_status": "LICENSE_APPROVED",
            "integrity_status": "VERIFIED", "playable_modes": ["SAMPLE MODE"],
            "confirmed_midi_note": 60, "confirmed_note_sequence": [60, 62, 64], "musical_metadata": {
                "confirmed_techniques": ["DOWNSTROKE", "PALM_MUTE"],
                "confirmed_velocity_layer": "HIGH",
            }, "blocking_reasons": [],
        }
        result = build_library_structure(_catalog({
            "SAMPLE MODE": [asset], "PATTERN MODE": [asset],
        }))
        self.assertEqual(result["summary"]["unique_asset_count"], 1)
        self.assertEqual(result["summary"]["mode_assignment_count"], 2)
        self.assertEqual(result["summary"]["multi_mode_asset_count"], 1)
        self.assertEqual(result["coverage"]["pitch_classes"][0]["status"], "COVERED")
        self.assertEqual(result["coverage"]["techniques"][0]["status"], "COVERED")
        self.assertEqual(validate_library_structure(result), [])

    def test_unreviewed_technique_is_not_counted_as_confirmed(self):
        asset = {
            "asset_id": "A2", "playable": False, "playable_in_mode": False,
            "review_status": "NEEDS_MUSICAL_REVIEW", "license_status": "UNREVIEWED",
            "integrity_status": "VERIFIED", "musical_metadata": {
                "confirmed_techniques": ["PALM_MUTE"],
            },
        }
        result = build_library_structure(_catalog({"ARTICULATIONS": [asset]}))
        self.assertEqual(result["coverage"]["techniques"][2]["status"], "GAP")
        self.assertEqual(result["modes"][8]["assets"][0]["status"], "REVIEW_REQUIRED")

    def test_pattern_and_melody_require_their_own_event_data(self):
        pattern = {"asset_id": "P1", "playable": False, "playable_in_mode": False,
                   "musical_metadata": {"pattern_performance_review": {"tempo_bpm": 170}}}
        melody = {"asset_id": "M1", "playable": False, "playable_in_mode": False,
                  "confirmed_note_sequence": [60, 62, 64], "musical_metadata": {}}
        result = build_library_structure(_catalog({"PATTERN MODE": [pattern], "MELODY MODE": [melody]}))
        self.assertEqual(result["pattern_mode"]["assets"][0]["pattern_structure_status"], "INCOMPLETE")
        self.assertIn("loop_start_sample", result["pattern_mode"]["assets"][0]["missing_fields"])
        self.assertEqual(result["melody_mode"]["assets"][0]["melody_structure_status"], "INCOMPLETE")
        self.assertIn("confirmed_melody_events_with_timing", result["melody_mode"]["assets"][0]["missing_fields"])

    def test_pattern_note_zone_is_not_mistaken_for_a_rhythm_loop(self):
        note_zone = {
            "asset_id": "PN1", "kind": "note_event", "asset_file": "staging/clips/note.wav",
            "review_status": "REVIEWED", "license_status": "LICENSE_APPROVED",
            "integrity_status": "VERIFIED", "confirmed_midi_note": 60,
            "playable": False, "playable_in_mode": False,
        }
        result = build_library_structure(_catalog({"PATTERN MODE": [note_zone]}))
        pattern = result["pattern_mode"]["assets"][0]
        self.assertEqual(pattern["pattern_structure_status"], "NOTE_ZONE_READY")
        self.assertEqual(pattern["missing_fields"], [])
        self.assertEqual(result["pattern_mode"]["note_zone_ready_count"], 1)
        self.assertEqual(result["pattern_mode"]["structure_verified_count"], 0)

    def test_complete_pattern_and_melody_metadata_is_recognized(self):
        pattern = {
            "asset_id": "P2", "review_status": "REVIEWED",
            "license_status": "LICENSE_APPROVED", "integrity_status": "VERIFIED",
            "musical_metadata": {"pattern_performance_review": {
                "loop_start_sample": 0, "loop_end_sample": 48000,
                "tempo_bpm": 170, "time_signature": "4/4",
                "attack_events": [{"sample": 0, "stroke": "DOWNSTROKE"}],
                "beat_grid": [0, 12000, 24000, 36000],
                "technique_events": [{"sample": 0, "technique": "DOWNSTROKE"}],
                "harmonic_events": [{"sample": 0, "chord": "C5"}],
                "cycle_integrity_verified": True, "musical_review_verified": True,
            }},
        }
        melody = {
            "asset_id": "M2", "review_status": "REVIEWED",
            "license_status": "LICENSE_APPROVED", "integrity_status": "VERIFIED",
            "confirmed_note_sequence": [60, 62],
            "musical_metadata": {
                "confirmed_note_sequence": [60, 62],
                "confirmed_melody_events": [
                    {"midi_note": 60, "start_beats": 0, "duration_beats": 1, "velocity": 92},
                    {"midi_note": 62, "start_beats": 1, "duration_beats": 1, "velocity": 100},
                ],
                "melody_phrase_boundaries": [0, 2],
                "melody_mapping_verified": True,
            },
        }
        result = build_library_structure(_catalog({
            "PATTERN MODE": [pattern], "MELODY MODE": [melody],
        }))
        self.assertEqual(result["pattern_mode"]["assets"][0]["pattern_structure_status"], "STRUCTURE_VERIFIED")
        self.assertEqual(result["melody_mode"]["assets"][0]["melody_structure_status"], "STRUCTURE_VERIFIED")

    def test_runtime_ready_requires_review_license_and_integrity(self):
        bad = {"asset_id": "X", "asset_file": "x.wav", "playable": True,
               "playable_in_mode": True, "review_status": "NEEDS_MUSICAL_REVIEW",
               "license_status": "UNREVIEWED", "integrity_status": "BLOCKED",
            "playable_modes": ["SAMPLE MODE"]}
        result = build_library_structure(_catalog({"SAMPLE MODE": [bad]}))
        self.assertEqual(result["modes"][0]["assets"][0]["runtime_ready"], False)
        self.assertEqual(validate_library_structure(result), [])


if __name__ == "__main__":
    unittest.main()
