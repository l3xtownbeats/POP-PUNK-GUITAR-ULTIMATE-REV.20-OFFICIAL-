import unittest
from candidate_builder import build_candidates


class CandidateBuilderTests(unittest.TestCase):
    def test_groups_nearby_onsets_and_keeps_review_flags(self):
        report = {"duration_seconds": 8.0, "source": "guitar.wav",
                  "onset_evidence_seconds": [0.5, 0.8, 1.2, 4.0, 4.4]}
        result = build_candidates(report)
        self.assertEqual(result["candidate_count"], 2)
        first, second = result["candidates"]
        self.assertEqual(first["review_status"], "NEEDS_MUSICAL_REVIEW")
        self.assertEqual(first["license_status"], "UNREVIEWED")
        self.assertLess(first["end_seconds"], second["start_seconds"])
        self.assertEqual(first["kind"], "audio_region_candidate")

    def test_empty_onset_report_does_not_invent_segments(self):
        result = build_candidates({"duration_seconds": 3.0, "onset_evidence_seconds": []})
        self.assertEqual(result["candidates"], [])

    def test_invalid_duration_and_limits_rejected(self):
        with self.assertRaises(ValueError):
            build_candidates({"duration_seconds": 0})
        with self.assertRaises(ValueError):
            build_candidates({"duration_seconds": 3}, min_duration_seconds=2,
                             max_duration_seconds=1)

    def test_long_group_is_bounded_without_musical_claim(self):
        result = build_candidates({"duration_seconds": 30.0,
                                   "onset_evidence_seconds": [1, 5, 10, 15, 20, 25]},
                                  max_gap_seconds=30, max_duration_seconds=8)
        self.assertGreaterEqual(result["candidate_count"], 3)
        self.assertTrue(all(c["boundary_basis"].startswith("grouped_onset")
                            for c in result["candidates"]))


if __name__ == "__main__":
    unittest.main()
