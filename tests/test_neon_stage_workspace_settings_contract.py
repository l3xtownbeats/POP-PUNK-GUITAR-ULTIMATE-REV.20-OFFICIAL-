#!/usr/bin/env python3
"""Keep workspace runtime clamps identical to the NEON STAGE Settings UI."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = (ROOT / "Source/UI/PPGUMultiWindowWorkspace.cpp").read_text(encoding="utf-8")
EDITOR = (ROOT / "Source/PluginEditor.cpp").read_text(encoding="utf-8")


class NeonStageWorkspaceSettingsContract(unittest.TestCase):
    def test_panel_scale_runtime_matches_settings_range(self):
        self.assertIn("juce::jlimit(0.5f, 1.5f, scale)", WORKSPACE)
        self.assertIn("configureSlider(scaleSlider, 0.5, 1.5, 0.05", EDITOR)

    def test_panel_gap_runtime_matches_settings_range(self):
        self.assertIn("juce::jlimit(0, 32, pixels)", WORKSPACE)
        self.assertIn("configureSlider(gapSlider, 0.0, 32.0, 1.0", EDITOR)

    def test_non_finite_scale_resets_to_default(self):
        self.assertIn("std::isfinite(scale) ? juce::jlimit(0.5f, 1.5f, scale) : 1.0f", WORKSPACE)


if __name__ == "__main__":
    unittest.main()
