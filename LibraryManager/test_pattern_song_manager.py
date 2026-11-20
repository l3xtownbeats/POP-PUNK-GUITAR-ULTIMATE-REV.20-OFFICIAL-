from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pattern_song_manager import (
    SCHEMA, add_pattern, create_song, load_library, new_library,
    rhythm_distance, save_library, search_similar_patterns, tap_intervals,
    validate_library,
)


class PatternSongManagerTests(unittest.TestCase):
    def test_song_accepts_multiple_section_patterns_and_persists(self):
        library = new_library()
        song = create_song("Pop Punk Demo", style="Pop Punk")
        library["songs"].append(song)
        pattern = add_pattern(
            song, name="Chorus Accents", wav_path="staging/clips/chorus.wav",
            role="CHORUS", selector_note=36, tempo_min_bpm=120, tempo_max_bpm=170,
            numerator=4, denominator=4, shift_beats=0.5, end_beats=8,
            chord_qualities=["MAJOR", "MINOR", "DOM7"],
            articulations=["DOWNSTROKE", "PALM_MUTE", "SLIDE"],
            doubling_enabled=True,
        )
        self.assertFalse(pattern["time_stretch"])
        self.assertEqual(pattern["tempo_policy"], "NATIVE_AUDIO_RATE_NO_TIME_STRETCH")
        self.assertEqual(pattern["doubling"]["mode"], "NATURAL_SECOND_TAKE")
        self.assertFalse(pattern["chord_compatibility"]["whole_chord_wav_transposition_allowed"])
        validate_library(library)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pattern_song_library.json"
            save_library(path, library)
            restored = load_library(path)
        self.assertEqual(restored["schema"], SCHEMA)
        self.assertEqual(restored["songs"][0]["patterns"][0]["role"], "CHORUS")

    def test_selector_keys_must_be_unique(self):
        library = new_library()
        song = create_song("Song")
        library["songs"].append(song)
        add_pattern(song, name="A", wav_path="a.wav", selector_note=36)
        add_pattern(song, name="B", wav_path="b.wav", selector_note=36)
        with self.assertRaises(ValueError):
            validate_library(library)

    def test_no_time_stretch_and_no_chord_wav_transposition_are_hard_invariants(self):
        library = new_library()
        song = create_song("Song")
        library["songs"].append(song)
        pattern = add_pattern(song, name="A", wav_path="a.wav")
        pattern["time_stretch"] = True
        with self.assertRaises(ValueError):
            validate_library(library)
        pattern["time_stretch"] = False
        pattern["chord_compatibility"]["whole_chord_wav_transposition_allowed"] = True
        with self.assertRaises(ValueError):
            validate_library(library)

    def test_rhythm_search_handles_rotation_and_tempo_scale(self):
        self.assertLess(rhythm_distance([0.25, 0.25, 0.5, 0.25], [0.5, 0.25, 0.25, 0.25]), 0.01)
        library = new_library()
        song = create_song("Song")
        library["songs"].append(song)
        pattern = add_pattern(song, name="R", wav_path="r.wav")
        pattern["rhythm_search_signature"] = [0.25, 0.25, 0.5]
        self.assertEqual(search_similar_patterns(library, [0.5, 0.5, 1.0])[0]["pattern_id"], pattern["pattern_id"])

    def test_tap_requires_enough_ordered_timestamps(self):
        self.assertEqual(tap_intervals([0.0, 0.5, 1.0]), [0.5, 0.5])
        with self.assertRaises(ValueError):
            tap_intervals([0.0, 0.5])
        with self.assertRaises(ValueError):
            tap_intervals([0.0, 0.5, 0.4])


if __name__ == "__main__":
    unittest.main()
