import unittest

from chromatic_pitch_map import (
    ALIASES, build_chromatic_pitch_map, canonical_pitch_classes,
    chromatic_note_table, midi_pitch_class, normalize_note_name,
    note_name_for_pitch_class,
)


class ChromaticPitchMapTests(unittest.TestCase):
    def test_all_twelve_chromatic_classes_are_distinct_and_present(self):
        table = chromatic_note_table()
        self.assertEqual([row["pitch_class"] for row in table], list(range(12)))
        self.assertEqual(len({row["pitch_class"] for row in table}), 12)
        self.assertEqual([row["canonical_name"] for row in table],
                         ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])

    def test_enharmonic_spellings_merge_but_e_and_f_remain_distinct(self):
        self.assertEqual(normalize_note_name("C#"), normalize_note_name("Db"))
        self.assertEqual(normalize_note_name("F#"), normalize_note_name("Gb"))
        self.assertEqual(normalize_note_name("D#"), normalize_note_name("Eb"))
        self.assertNotEqual(normalize_note_name("E"), normalize_note_name("F"))
        self.assertEqual(canonical_pitch_classes(["C#", "Db", "F#", "Gb", "E", "F"]), [1, 4, 5, 6])

    def test_key_aware_flat_and_sharp_display_does_not_change_pitch(self):
        self.assertEqual(note_name_for_pitch_class(1, key_name="F", spelling="key"), "Db")
        self.assertEqual(note_name_for_pitch_class(1, key_name="G", spelling="key"), "C#")
        self.assertEqual(normalize_note_name("Db"), normalize_note_name("C#"))

    def test_all_midi_keys_have_a_row_and_missing_sources_are_explicit(self):
        manifest = build_chromatic_pitch_map(midi_min=48, midi_max=83, key_name="C")
        self.assertEqual(manifest["coverage"]["midi_key_count"], 36)
        self.assertEqual(len(manifest["midi_note_map"]), 36)
        self.assertEqual({row["pitch_class"] for row in manifest["midi_note_map"]}, set(range(12)))
        self.assertEqual(manifest["coverage"]["missing_source_count"], 36)
        self.assertFalse(any(row["runtime_ready_in_catalog"] for row in manifest["midi_note_map"]))

    def test_approved_exact_samples_are_bound_but_unreviewed_assets_are_ignored(self):
        catalog = {"modes": [
            {"mode": "SAMPLE MODE", "assets": [{
                "asset_id": "OK", "confirmed_midi_note": 60, "playable": True,
                "review_status": "REVIEWED", "license_status": "LICENSE_APPROVED",
                "integrity_status": "VERIFIED", "asset_file": "Samples/ok.wav",
            }, {
                "asset_id": "NO", "confirmed_midi_note": 61, "playable": False,
                "review_status": "NEEDS_MUSICAL_REVIEW", "license_status": "UNREVIEWED",
                "integrity_status": "VERIFIED", "asset_file": "Samples/no.wav",
            }]},
        ]}
        manifest = build_chromatic_pitch_map(catalog, midi_min=60, midi_max=61)
        self.assertEqual(manifest["midi_note_map"][0]["status"], "EXACT_APPROVED_SAMPLE")
        self.assertEqual(manifest["midi_note_map"][0]["asset_ids"], ["OK"])
        self.assertEqual(manifest["midi_note_map"][1]["status"], "SOURCE_MISSING")

    def test_autochords_deduplicates_aliases_not_distinct_notes(self):
        self.assertEqual(canonical_pitch_classes(["C#", "Db", "D#", "Eb", "E", "F"]),
                         [1, 3, 4, 5])


if __name__ == "__main__":
    unittest.main()
