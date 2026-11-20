import unittest

from irregular_phrase_segmenter import analyze_irregular_guitar_phrases


class IrregularPhraseSegmenterTests(unittest.TestCase):
    def test_finds_non_repeating_irregular_phrase_with_exact_source_offsets(self):
        onsets = [1.00, 1.19, 1.61, 1.84, 2.31, 2.48]
        report = analyze_irregular_guitar_phrases(
            "take.wav", {"sample_rate": 1000, "duration_seconds": 5.0,
                         "onset_evidence_seconds": onsets},
            guitar_source_confirmed=True, source_sha256="A" * 64,
        )
        self.assertEqual(report["candidate_count"], 1)
        candidate = report["candidates"][0]
        self.assertEqual(candidate["candidate_type"], "IRREGULAR_GUITAR_LOOP_PHRASE")
        self.assertEqual(candidate["source_start_sample"], 965)
        self.assertEqual(candidate["source_end_sample"], 2660)
        self.assertEqual(candidate["review_status"], "NEEDS_MUSICAL_REVIEW")
        self.assertIsNone(candidate["tempo_candidate_bpm"])
        self.assertFalse(report["audio_modified"])

    def test_splits_phrases_at_long_pauses(self):
        onsets = [0.5, 0.7, 0.9, 2.0, 2.2, 2.4]
        report = analyze_irregular_guitar_phrases(
            "take.wav", {"sample_rate": 1000, "duration_seconds": 4.0,
                         "onset_evidence_seconds": onsets},
            guitar_source_confirmed=True, source_sha256="B" * 64,
        )
        self.assertEqual(report["candidate_count"], 2)

    def test_requires_manual_guitar_confirmation(self):
        with self.assertRaises(ValueError):
            analyze_irregular_guitar_phrases(
                "take.wav", {"sample_rate": 1000, "duration_seconds": 4.0,
                             "onset_evidence_seconds": [0.1, 0.2, 0.3]},
            )

    def test_does_not_promote_noise_or_short_groups_automatically(self):
        report = analyze_irregular_guitar_phrases(
            "take.wav", {"sample_rate": 1000, "duration_seconds": 4.0,
                         "onset_evidence_seconds": [0.1, 0.2]},
            guitar_source_confirmed=True, source_sha256="C" * 64,
        )
        self.assertEqual(report["candidate_count"], 0)
        self.assertFalse(report["automatic_factory_promotion"])


if __name__ == "__main__":
    unittest.main()
