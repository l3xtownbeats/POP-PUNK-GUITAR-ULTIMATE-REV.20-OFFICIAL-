from __future__ import annotations

import unittest

from mode_sorter import MODE_ORDER, build_mode_sorting_report


def record(**overrides):
    value = {
        "source_path": "guitar.wav",
        "source_sha256": "A" * 64,
        "acoustic_analysis": {"sample_rate": 1000, "total_frames": 5000, "duration_seconds": 5.0},
        "classification": {},
        "pitch_candidates": [],
        "virtual_extraction": {"candidates": []},
        "irregular_phrase_extraction": {"candidates": []},
    }
    value.update(overrides)
    return value


class ModeSorterTests(unittest.TestCase):
    def test_all_ten_approved_modes_are_always_present(self):
        report = build_mode_sorting_report([])
        self.assertEqual([item["mode"] for item in report["modes"]], list(MODE_ORDER))
        self.assertEqual(report["mode_count"], 10)

    def test_repeated_motif_goes_to_pattern_not_irregular_phrase(self):
        source = record(virtual_extraction={"candidates": [{
            "candidate_id": "PAT-1", "source_start_sample": 120, "source_end_sample": 980,
            "start_seconds": 0.12, "end_seconds": 0.98,
        }]})
        report = build_mode_sorting_report([source])
        modes = {item["mode"]: item for item in report["modes"]}
        self.assertEqual(modes["PATTERN MODE"]["candidate_count"], 1)
        self.assertEqual(modes["PHRASE MODE"]["candidate_count"], 0)
        candidate = modes["PATTERN MODE"]["candidates"][0]
        self.assertEqual((candidate["source_start_sample"], candidate["source_end_sample"]), (120, 980))
        self.assertFalse(candidate["automatic_factory_promotion"])

    def test_irregular_phrase_is_not_mislabeled_as_pattern(self):
        source = record(irregular_phrase_extraction={"candidates": [{
            "candidate_id": "PHR-1", "source_start_sample": 321, "source_end_sample": 4321,
            "onset_count_candidate": 4,
        }]})
        report = build_mode_sorting_report([source])
        modes = {item["mode"]: item for item in report["modes"]}
        self.assertEqual(modes["PATTERN MODE"]["candidate_count"], 0)
        self.assertEqual(modes["PHRASE MODE"]["candidate_count"], 1)
        self.assertEqual(modes["RIFF MODE"]["candidates"][0]["mode_assignment_status"],
                         "AMBIGUOUS_RIFF_OR_PHRASE")

    def test_pitch_events_produce_review_only_melody_and_note_candidates(self):
        source = record(classification={
            "asset_kind_candidate": "SAMPLE",
            "features": {"distinct_pitch_count": 3, "pitch_sequence": [60, 62, 64]},
            "fragment_candidates": [
                {"start_seconds": 0.1, "end_seconds": 0.3, "midi_note_candidate": 60},
                {"start_seconds": 0.4, "end_seconds": 0.6, "midi_note_candidate": 62},
                {"start_seconds": 0.7, "end_seconds": 0.9, "midi_note_candidate": 64},
            ],
        })
        report = build_mode_sorting_report([source])
        modes = {item["mode"]: item for item in report["modes"]}
        self.assertEqual(modes["SAMPLE MODE"]["candidate_count"], 3)
        self.assertEqual(modes["MELODY MODE"]["candidate_count"], 1)
        self.assertEqual(modes["MELODY MODE"]["candidates"][0]["source_start_sample"], 100)
        self.assertEqual(modes["MELODY MODE"]["candidates"][0]["source_end_sample"], 900)

    def test_chord_and_power_chord_hypotheses_enter_sample_mode(self):
        source = record(chord_analysis={
            "chord_candidates": [
                {"start_seconds": 0.2, "end_seconds": 0.6,
                 "chord_name_candidate": "C", "root_pitch_class": "C", "quality": "MAJOR",
                 "pitch_classes_candidate": ["C", "E", "G"], "confidence": 0.9},
                {"start_seconds": 0.8, "end_seconds": 1.2,
                 "chord_name_candidate": "G5", "root_pitch_class": "G", "quality": "POWER5",
                 "pitch_classes_candidate": ["G", "D"], "confidence": 0.88},
            ]
        })
        report = build_mode_sorting_report([source])
        sample = {item["candidate_type"] for item in
                  next(x for x in report["modes"] if x["mode"] == "SAMPLE MODE")["candidates"]}
        self.assertIn("CHORD_SAMPLE", sample)
        self.assertIn("POWER_CHORD_SAMPLE", sample)
        modes = {item["mode"]: item for item in report["modes"]}
        self.assertGreater(modes["ARPEGGIO"]["candidate_count"], 0)
        voicing = modes["ARPEGGIO"]["candidates"][0]["voicing_candidates"]
        self.assertTrue(voicing)
        self.assertTrue(all(item["review_status"] == "NEEDS_MUSICAL_REVIEW"
                            for item in voicing))

    def test_strumming_arpeggio_articulations_and_ending_are_not_guessed(self):
        report = build_mode_sorting_report([record()])
        modes = {item["mode"]: item for item in report["modes"]}
        for mode in ("STRUMMING", "ARPEGGIO", "ARTICULATIONS", "ENDING"):
            self.assertEqual(modes[mode]["candidate_count"], 0)
            self.assertEqual(modes[mode]["status"], "NO_SUPPORTED_CANDIDATES")

    def test_short_one_shot_is_candidate_only(self):
        source = record(classification={"asset_kind_candidate": "ONE_SHOT"})
        report = build_mode_sorting_report([source])
        modes = {item["mode"]: item for item in report["modes"]}
        candidate = modes["SAMPLE MODE"]["candidates"][0]
        self.assertEqual((candidate["source_start_sample"], candidate["source_end_sample"]), (0, 5000))
        self.assertEqual(candidate["license_status"], "UNREVIEWED")
        self.assertEqual(candidate["review_status"], "NEEDS_MUSICAL_REVIEW")


if __name__ == "__main__":
    unittest.main()
