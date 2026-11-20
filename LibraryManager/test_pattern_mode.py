import unittest

from pattern_mode import build_pattern_asset, build_playback_plan, set_doubling


class PatternModeTests(unittest.TestCase):
    def make_pattern(self):
        return build_pattern_asset(
            asset_id="PAT-001", source_sha256="a" * 64,
            source_start_sample=100, source_end_sample=5100,
            sample_rate=48000, recorded_tempo_bpm=180,
            meter_numerator=4, meter_denominator=4,
            loop_start_sample=200, loop_end_sample=5000,
            events=[
                {"position_ticks": 0, "duration_ticks": 120, "articulation": "DOWNSTROKE"},
                {"position_ticks": 120, "duration_ticks": 120, "articulation": "PALM_MUTE"},
            ],
            articulations_reviewed=True,
        )

    def test_pattern_is_recorded_audio_and_time_stretch_is_disabled(self):
        pattern = self.make_pattern()
        plan = build_playback_plan(pattern, project_tempo_bpm=150)
        self.assertFalse(pattern["time_stretch"]["enabled"])
        self.assertFalse(plan["time_stretch_applied"])
        self.assertTrue(plan["source_audio_timing_preserved"])
        self.assertTrue(plan["tempo_mismatch_warning"])

    def test_articulations_must_be_explicitly_recorded_and_reviewed(self):
        pattern = self.make_pattern()
        self.assertEqual(pattern["articulations"]["events"][1]["articulation"], "PALM_MUTE")
        self.assertTrue(pattern["articulations"]["reviewed"])
        self.assertFalse(pattern["articulations"]["automatic_inference"])

    def test_doubling_creates_two_voice_configuration_without_claiming_render(self):
        pattern = set_doubling(self.make_pattern(), enabled=True, timing_offset_ms=9.5,
                               velocity_delta=-5, humanization_seed=42)
        self.assertEqual(pattern["doubling"]["voice_count"], 2)
        self.assertEqual(pattern["doubling"]["timing_offset_ms"], 9.5)
        self.assertEqual(pattern["doubling"]["velocity_delta"], -5)
        plan = build_playback_plan(pattern, project_tempo_bpm=180)
        self.assertEqual(plan["doubling"]["humanization_seed"], 42)
        self.assertFalse(plan["runtime_ready"])

    def test_invalid_loop_and_articulation_are_rejected(self):
        with self.assertRaises(ValueError):
            build_pattern_asset(asset_id="x", source_sha256="a"*64,
                source_start_sample=100, source_end_sample=500,
                sample_rate=48000, recorded_tempo_bpm=120,
                loop_start_sample=50, loop_end_sample=300)
        with self.assertRaises(ValueError):
            build_pattern_asset(asset_id="x", source_sha256="a"*64,
                source_start_sample=100, source_end_sample=500,
                sample_rate=48000, recorded_tempo_bpm=120,
                events=[{"position_ticks": 0, "duration_ticks": 10,
                         "articulation": "MADE_UP"}])


if __name__ == "__main__":
    unittest.main()
