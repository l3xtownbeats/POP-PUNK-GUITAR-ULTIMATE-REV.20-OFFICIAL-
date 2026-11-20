import unittest

from voicing_generator import generate_voicing_candidates


class VoicingGeneratorTests(unittest.TestCase):
    def test_generates_compact_c_major_voicing_hypotheses(self):
        result = generate_voicing_candidates({
            "chord_name_candidate": "C",
            "root_pitch_class": "C",
            "quality": "MAJOR",
            "pitch_classes_candidate": ["C", "E", "G"],
        })
        self.assertGreater(result["candidate_count"], 0)
        self.assertEqual(result["tuning_status"], "NEEDS_CONFIRMATION")
        for candidate in result["voicing_candidates"]:
            self.assertLessEqual(candidate["fret_span_candidate"], 4)
            self.assertGreaterEqual(candidate["sounding_string_count"], 3)
            self.assertEqual(candidate["review_status"], "NEEDS_MUSICAL_REVIEW")
            self.assertEqual(candidate["fingering_candidate"], "UNKNOWN")
            for position in candidate["string_positions_6_to_1"]:
                fret = position["fret_number"]
                if fret is not None:
                    midi = position["midi_note_candidate"]
                    self.assertIn(midi % 12, {0, 4, 7})

    def test_generates_power_chord_candidates(self):
        result = generate_voicing_candidates({
            "chord_name_candidate": "G5",
            "root_pitch_class": "G",
            "quality": "POWER5",
            "pitch_classes_candidate": ["G", "D"],
        })
        self.assertGreater(result["candidate_count"], 0)
        for candidate in result["voicing_candidates"]:
            self.assertGreaterEqual(candidate["sounding_string_count"], 2)
            self.assertTrue(set(candidate["pitch_classes_candidate"]).issubset({"G", "D"}))

    def test_unknown_chord_does_not_invent_voicings(self):
        result = generate_voicing_candidates({
            "chord_name_candidate": None,
            "root_pitch_class": None,
            "quality": "UNKNOWN",
            "pitch_classes_candidate": [],
        })
        self.assertEqual(result["candidate_count"], 0)
        self.assertEqual(result["voicing_candidates"], [])

    def test_rejects_invalid_tuning(self):
        with self.assertRaises(ValueError):
            generate_voicing_candidates({"pitch_classes_candidate": ["C"]},
                                        tuning_open_midi=(40, 45, 50))


if __name__ == "__main__":
    unittest.main()
