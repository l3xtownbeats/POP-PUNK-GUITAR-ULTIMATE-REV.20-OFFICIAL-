import unittest

from classification_schema import empty_profile, validate_profile


class ClassificationSchemaTests(unittest.TestCase):
    def test_empty_profile_is_valid_and_unknowns_are_explicit(self):
        profile = empty_profile("asset-1", "incoming/guitar.wav", "A" * 64)
        self.assertEqual(validate_profile(profile), [])
        self.assertEqual(profile["instrument_family"]["value"], "UNKNOWN")
        self.assertEqual(profile["tonality"]["key_candidate"], None)
        self.assertEqual(profile["automatic_destructive_action"], "NONE")

    def test_rejects_unapproved_values_and_destructive_actions(self):
        profile = empty_profile("asset-1", "incoming/guitar.wav", "A" * 64)
        profile["asset_roles"] = [{"value": "DELETE_DUPLICATE", "confidence": 1.0, "evidence": []}]
        profile["automatic_destructive_action"] = "DELETE"
        errors = validate_profile(profile)
        self.assertTrue(any("asset_roles" in error for error in errors))
        self.assertTrue(any("Destructive" in error for error in errors))

    def test_rejects_invalid_structure_timing(self):
        profile = empty_profile("asset-1", "incoming/guitar.wav", "A" * 64)
        profile["structure"] = [{"section": "VERSE", "start_seconds": 4.0, "end_seconds": 2.0}]
        self.assertTrue(any("time bounds" in error for error in validate_profile(profile)))


if __name__ == "__main__":
    unittest.main()
