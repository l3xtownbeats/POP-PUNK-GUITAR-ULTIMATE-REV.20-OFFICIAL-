import unittest

from rhythm_analysis import analyze_rhythm


class RhythmAnalysisTests(unittest.TestCase):
    def test_regular_pulse_produces_tempo_and_repeat_candidate(self):
        report = {"duration_seconds": 8.0,
                  "onset_evidence_seconds": [i * 0.5 for i in range(12)]}
        result = analyze_rhythm(report)
        self.assertTrue(result["repeating_pulse_candidate"])
        self.assertTrue(result["tempo_candidates"])
        self.assertIn(120, [item["bpm"] for item in result["tempo_candidates"]])
        self.assertEqual(result["review_status"], "NEEDS_MUSICAL_REVIEW")

    def test_irregular_events_do_not_claim_stable_pulse(self):
        report = {"duration_seconds": 8.0,
                  "onset_evidence_seconds": [0.1, 0.4, 1.3, 1.55, 3.2, 3.9]}
        result = analyze_rhythm(report)
        self.assertFalse(result["repeating_pulse_candidate"])

    def test_descriptor_is_search_only_and_never_duplicate_authority(self):
        report = {"duration_seconds": 4.0,
                  "onset_evidence_seconds": [0.0, 0.5, 1.0, 1.5, 2.0]}
        result = analyze_rhythm(report)
        self.assertEqual(result["rhythm_descriptor"]["purpose"],
                         "SEARCH_AND_GROUPING_ONLY_NOT_DUPLICATE_ID")
        self.assertEqual(result["automatic_destructive_action"], "NONE")

    def test_filters_out_of_range_and_duplicate_timestamps(self):
        report = {"duration_seconds": 2.0,
                  "onset_evidence_seconds": [-1, 0, 0, 0.5, 3]}
        result = analyze_rhythm(report)
        self.assertEqual(result["onset_evidence_seconds"], [0.0, 0.5])

    def test_rejects_invalid_duration_and_tolerance(self):
        with self.assertRaises(ValueError):
            analyze_rhythm({"duration_seconds": 0, "onset_evidence_seconds": []})
        with self.assertRaises(ValueError):
            analyze_rhythm({"duration_seconds": 1, "onset_evidence_seconds": []},
                           tolerance=0.9)


if __name__ == "__main__":
    unittest.main()
