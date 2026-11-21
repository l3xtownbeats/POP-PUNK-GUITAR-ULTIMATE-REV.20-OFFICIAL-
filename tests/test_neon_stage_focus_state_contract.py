#!/usr/bin/env python3
"""Guard independent keyboard-focus feedback for PNG-backed NEON STAGE controls."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EDITOR = (ROOT / "Source/PluginEditor.cpp").read_text(encoding="utf-8")


class NeonStageFocusStateContract(unittest.TestCase):
    def test_png_backed_rotaries_keep_a_separate_focus_ring(self):
        start = EDITOR.index("void PPGUPremiumLookAndFeel::drawRotarySlider")
        end = EDITOR.index("void PPGUPremiumLookAndFeel::drawLinearSlider", start)
        rotary = EDITOR[start:end]
        self.assertIn("slider.hasKeyboardFocus(true)", rotary)
        self.assertIn('palette.token("highlight").withAlpha(0.96f)', rotary)
        self.assertIn("g.drawEllipse", rotary)

    def test_png_backed_buttons_keep_focus_visible_over_active_art(self):
        start = EDITOR.index("void PPGUPremiumLookAndFeel::drawButtonBackground")
        end = EDITOR.index("void PPGUPremiumLookAndFeel::drawComboBox", start)
        button = EDITOR[start:end]
        image_draw = button.index("g.drawImageWithin(*artwork")
        focus_check = button.index("button.hasKeyboardFocus(true)", image_draw)
        self.assertGreater(focus_check, image_draw)
        self.assertIn('palette.token("highlight").withAlpha(0.98f)', button)
        self.assertIn("g.drawRoundedRectangle", button)

    def test_focus_does_not_replace_real_apvts_toggle_state(self):
        self.assertIn("button.getToggleState()", EDITOR)
        self.assertIn("button.hasKeyboardFocus(true)", EDITOR)


if __name__ == "__main__":
    unittest.main()
