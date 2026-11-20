import unittest

from pattern_candidate_analyzer import find_repeating_patterns


class RepeatingPatternCandidateTests(unittest.TestCase):
    def test_finds_repeated_timing_motif_and_preserves_source_offsets(self):
        # The same 3-interval contour occurs twice, separated by a longer gap.
        onsets = [0.0,  0.25, 0.50, 0.75,  1.75,
                  2.00, 2.25, 2.50,  3.50]
        report = {
            "source": "long_guitar_take.wav",
            "source_sha256": "A" * 64,
            "duration_seconds": 4.0,
            "onset_evidence_seconds": onsets,
        }
        result = find_repeating_patterns(report, min_intervals=3, max_intervals=3)
        self.assertGreaterEqual(result["candidate_count"], 1)
        matching = [
            item for item in result["patterns"]
            if [occurrence["start_seconds"] for occurrence in item["occurrences"]]
            == [0.0, 1.75]
        ]
        self.assertTrue(matching)
        candidate = matching[0]
        self.assertEqual(candidate["candidate_type"], "REPEATED_RHYTHM_MOTIF")
        self.assertEqual(candidate["occurrence_count"], 2)
        self.assertEqual([o["end_seconds"] for o in candidate["occurrences"]], [0.75, 2.5])
        self.assertEqual(candidate["pattern_role_candidate"], "RHYTHM_PATTERN")
        self.assertEqual(candidate["musical_section_candidate"], "UNKNOWN")
        self.assertEqual(candidate["review_status"], "NEEDS_MUSICAL_REVIEW")

    def test_does_not_invent_pattern_when_timing_is_not_repeated(self):
        report = {
            "duration_seconds": 10.0,
            "onset_evidence_seconds": [0.0, 0.2, 0.7, 1.1, 2.0, 3.4, 5.1],
        }
        result = find_repeating_patterns(report, min_intervals=3, max_intervals=3)
        self.assertEqual(result["candidate_count"], 0)

 
    def test_overlapping_windows_are_not_counted_as_repetitions(self):
        report = {
            "duration_seconds": 2.0,
            "onset_evidence_seconds": [0.0, 0.25, 0.50, 0.75, 1.0, 1.25],
        }
        result = find_repeating_patterns(report, min_intervals=3, max_intervals=3)
        self.assertEqual(result["candidate_count"], 0)

    def test_preserves_source_hash_from_rhythm_report(self):
        report = {
            "source": "take.wav",
            "source_sha256": "B" * 64,
            "duration_seconds": 4.0,
            "onset_evidence_seconds": [0.0, 0.25, 0.50, 0.75, 1.75,
                                       2.00, 2.25, 2.50, 3.50],
        }
        result = find_repeating_patterns(report, min_intervals=3, max_intervals=3)
        self.assertEqual(result["source_sha256"], "B" * 64)

    def test_rejects_invalid_report_and_parameters(self):
        with self.assertRaises(ValueError):
            find_repeating_patterns({"duration_seconds": 0, "onset_evidence_seconds": []})
        with self.assertRaises(ValueError):
            find_repeating_patterns({
                "duration_seconds": 2.0,
                "onset_evidence_seconds": [0.0, 0.2, 0.4, 0.6],
            }, min_intervals=1)


if __name__ == "__main__":
    unittest.main()
