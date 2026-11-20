import unittest

from pattern_engine_schema import (
    DEFAULT_PATTERN_SLOTS, build_pattern_engine_manifest, validate_pattern_engine_manifest,
)


class PatternEngineSchemaTests(unittest.TestCase):
    def test_approved_selector_mapping_is_locked(self):
        self.assertEqual(
            [(slot["key_label"], slot["display_name"]) for slot in DEFAULT_PATTERN_SLOTS],
            [
                ("C1", "Pop Punk Downstroke"),
                ("C#1", "Palm Mute 8th Notes"),
                ("D1", "Power Chord Rhythm"),
                ("D#1", "Punk Rock Rhythm"),
                ("E1", "Fast Downstroke"),
                ("F1", "Alternative Punk Rhythm"),
            ],
        )

    def test_manifest_keeps_host_octave_calibration_open(self):
        manifest = build_pattern_engine_manifest()
        self.assertIsNone(manifest["midi_mapping"]["selector_note_numbers"])
        self.assertEqual(manifest["midi_mapping"]["host_calibration_target"], "FL_STUDIO_20")
        self.assertTrue(manifest["midi_mapping"]["selector_keys_are_control_only"])
        self.assertEqual(validate_pattern_engine_manifest(manifest), [])

    def test_selector_and_playable_ranges_must_not_overlap(self):
        manifest = build_pattern_engine_manifest()
        manifest["midi_mapping"]["range_overlap_allowed"] = True
        self.assertIn("Selector and playable ranges must never overlap",
                      validate_pattern_engine_manifest(manifest))

    def test_duplicate_selector_labels_are_rejected(self):
        manifest = build_pattern_engine_manifest()
        manifest["pattern_slots"][1]["key_label"] = "C1"
        self.assertIn("Duplicate selector key labels", validate_pattern_engine_manifest(manifest))

    def test_template_is_not_factory_ready(self):
        manifest = build_pattern_engine_manifest()
        self.assertEqual(manifest["status"], "TEMPLATE_ONLY_NOT_FACTORY_READY")
        self.assertFalse(manifest["review_policy"]["automatic_factory_promotion"])
        self.assertEqual(manifest["review_policy"]["required_license_status"], "LICENSE_APPROVED")


if __name__ == "__main__":
    unittest.main()
