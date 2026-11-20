import unittest

from melody_note_mapper import map_single_note_candidate


class MelodyNoteMapperTests(unittest.TestCase):
    def test_maps_midi_to_chromatic_pitch_class_and_octave(self):
        mapped = map_single_note_candidate({
            "midi_note_candidate": 60,
            "confidence": 0.93,
            "velocity": 96,
            "articulation": "OPEN",
        })
        self.assertEqual(mapped["pitch_class_name_candidate"], "C")
        self.assertEqual(mapped["pitch_class_index_candidate"], 0)
        self.assertEqual(mapped["octave_candidate"], 4)
        self.assertEqual(mapped["velocity_layer_candidate"], "HIGH")
        self.assertEqual(mapped["pitch_mapping_status"], "HIGH_CONFIDENCE_CANDIDATE")

    def test_all_twelve_chromatic_positions_are_represented(self):
        expected = ["C", "C#", "D", "D#", "E", "F",
                    "F#", "G", "G#", "A", "A#", "B"]
        actual = [
            map_single_note_candidate({
                "midi_note_candidate": 60 + i, "confidence": 0.9
            })["pitch_class_name_candidate"]
            for i in range(12)
        ]
        self.assertEqual(actual, expected)

    def test_uncertain_pitch_is_not_confirmed(self):
        mapped = map_single_note_candidate({
            "midi_note_candidate": 61, "confidence": 0.42
        })
        self.assertEqual(mapped["pitch_mapping_status"], "REQUIRES_REVIEW")
        self.assertTrue(mapped["review_required"])
        self.assertEqual(mapped["velocity_layer_candidate"], "UNKNOWN")
        self.assertEqual(mapped["articulation_candidate"], "UNKNOWN")

    def test_invalid_midi_is_not_mapped(self):
        mapped = map_single_note_candidate({
            "midi_note_candidate": 200, "confidence": 0.99
        })
        self.assertIsNone(mapped["pitch_class_name_candidate"])
        self.assertIsNone(mapped["octave_candidate"])
        self.assertEqual(mapped["pitch_mapping_status"], "REQUIRES_REVIEW")


if __name__ == "__main__":
    unittest.main()
