#!/usr/bin/env python3
"""Source-level guardrails for the NEON STAGE 30 Hz animation loop."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EDITOR = (ROOT / "Source/PluginEditor.cpp").read_text(encoding="utf-8")
WORKSPACE = (ROOT / "Source/UI/PPGUMultiWindowWorkspace.cpp").read_text(encoding="utf-8")
HEADER = (ROOT / "Source/UI/PPGUMultiWindowWorkspace.h").read_text(encoding="utf-8")


class NeonStageAnimationContract(unittest.TestCase):
    def test_editor_animation_timer_is_30_hz(self):
        self.assertIn("startTimerHz(30);", EDITOR)

    def test_rotary_controls_receive_phase_repaints(self):
        callback = EDITOR.split("void PopPunkGuitarUltimateAudioProcessorEditor::timerCallback()", 1)[1]
        callback = callback.split("void PopPunkGuitarUltimateAudioProcessorEditor::configureKnob", 1)[0]
        self.assertIn("premiumLookAndFeel.setAnimationPhase(animationPhase)", callback)
        self.assertIn("for (auto& knob : knobs)", callback)
        self.assertIn("knob.repaint()", callback)

    def test_fx_and_mode_buttons_only_repaint_when_animated(self):
        callback = EDITOR.split("void PopPunkGuitarUltimateAudioProcessorEditor::timerCallback()", 1)[1]
        self.assertIn("button.getToggleState() || button.isMouseOverOrDragging()", callback)
        self.assertIn("for (auto& button : fxButtons)", callback)
        self.assertIn("repaintIfAnimated(melodyTab)", callback)
        self.assertIn("repaintIfAnimated(patternTab)", callback)

    def test_auxiliary_windows_receive_phase_without_full_editor_repaint(self):
        callback = EDITOR.split("void PopPunkGuitarUltimateAudioProcessorEditor::timerCallback()", 1)[1]
        callback = callback.split("void PopPunkGuitarUltimateAudioProcessorEditor::configureKnob", 1)[0]
        self.assertIn("auxiliaryWorkspace->setAnimationPhase(animationPhase)", callback)
        self.assertNotIn("\n    repaint();", callback)

    def test_workspace_pulses_chrome_and_repaints_active_child_controls(self):
        self.assertIn("void setAnimationPhase(float phase);", HEADER)
        self.assertIn("borderColour.withAlpha(0.055f + 0.105f * breathe)", WORKSPACE)
        self.assertIn("repaintAnimatedDescendants(*content)", WORKSPACE)
        self.assertIn("slider->repaint()", WORKSPACE)


if __name__ == "__main__":
    unittest.main()
