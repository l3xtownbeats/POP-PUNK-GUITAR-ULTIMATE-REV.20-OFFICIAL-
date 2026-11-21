#!/usr/bin/env python3
"""Static contract checks for the live NEON STAGE JUCE editor wiring."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = (ROOT / "Source/PluginEditor.h").read_text(encoding="utf-8")
EDITOR = (ROOT / "Source/PluginEditor.cpp").read_text(encoding="utf-8")
LOOK_AND_FEEL = EDITOR[EDITOR.find("void PPGUPremiumLookAndFeel::drawRotarySlider"):
                       EDITOR.find("void PPGUPremiumLookAndFeel::drawComboBox")]
FAILURES: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        FAILURES.append(message)


def extract_array(source: str, declaration: str) -> list[str]:
    match = re.search(re.escape(declaration) + r"\\s*\\{([^}]*)\\}", source, re.S)
    if not match:
        return []
    return re.findall(r'"([^"]+)"', match.group(1))


expected_knobs = [
    "ampGain", "eqHigh", "eqMid", "eqLow", "velocity",
    "dynamics", "swing", "humanize", "accent",
]
expected_fx = [
    "compressorOn", "eqOn", "distortionOn", "chorusOn",
    "delayOn", "reverbOn", "cabinetOn",
]
require(extract_array(HEADER, "std::array<juce::String, 9> parameterIDs")
        == expected_knobs, "the nine rotary APVTS IDs/order must match the approved contract")
require(extract_array(HEADER, "std::array<juce::String, 7> fxParameterIDs")
        == expected_fx, "the seven FX APVTS IDs/order must match the approved contract")

require("std::array<juce::Slider, 9> knobs" in HEADER,
        "all nine rotary controls must be native JUCE sliders")
require("std::array<juce::TextButton, 7> fxButtons" in HEADER,
        "all seven FX controls must be native JUCE toggle buttons")
require("std::array<std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment>, 9> knobAttachments" in HEADER,
        "nine APVTS slider attachments must be declared")
require("std::array<std::unique_ptr<juce::AudioProcessorValueTreeState::ButtonAttachment>, 7> fxAttachments" in HEADER,
        "seven APVTS button attachments must be declared")
require('SliderAttachment>(processor.parameters, parameterIDs[i], knobs[i])' in EDITOR,
        "each rotary must bind to its matching APVTS parameter")
require('ButtonAttachment>(processor.parameters, fxParameterIDs[i], b)' in EDITOR,
        "each FX toggle must bind to its matching APVTS parameter")
require('ComboBoxAttachment>(processor.parameters, "playMode", modeBox)' in EDITOR,
        "MELODY/PATTERN must share the authoritative APVTS playMode")
require("melodyTab.setClickingTogglesState(true)" in EDITOR
        and "patternTab.setClickingTogglesState(true)" in EDITOR,
        "both mode tabs must be real toggle buttons")
require('melodyTab.setComponentID("mode_tab")' in EDITOR
        and 'patternTab.setComponentID("mode_tab")' in EDITOR,
        "both mode tabs must use the dedicated mode-tab rendering path")
require("melodyTab.setToggleState(!patternSelected" in EDITOR
        and "patternTab.setToggleState(patternSelected" in EDITOR,
        "mode tabs must be mutually exclusive and synchronized from playMode")

require("valueArc" in LOOK_AND_FEEL and "pointer.lineTo" in LOOK_AND_FEEL,
        "rotary rendering must show a live value arc and rotating pointer")
require('controlId == "mode_tab"' in LOOK_AND_FEEL
        and 'findControlArtwork("mode_selector", artworkState)' in LOOK_AND_FEEL,
        "mode tabs must use mode-selector artwork, not FX rocker artwork")
require("button.getToggleState()" in LOOK_AND_FEEL
        and 'palette.token("accent_glow")' in LOOK_AND_FEEL,
        "active buttons/modes must display a live accent glow")

required_windows = [
    "openFxEditPanel", "openPatternSectionPanel", "openAutoChordsPanel",
    "openImportGuitarPanel", "openSkinGalleryPanel", "openSettingsPanel",
]
for method in required_windows:
    require(f"void PopPunkGuitarUltimateAudioProcessorEditor::{method}" in EDITOR,
            f"missing real window implementation: {method}")
require("PPGUMultiWindowWorkspace" in HEADER and "auxiliaryWorkspace->openPanel" in EDITOR,
        "auxiliary windows must use the shared multi-window workspace")
require("void PopPunkGuitarUltimateAudioProcessorEditor::applyPalette" in EDITOR,
        "theme changes must propagate through the editor")
require("void PopPunkGuitarUltimateAudioProcessorEditor::resized" in EDITOR,
        "responsive layout implementation is required")

if FAILURES:
    for failure in FAILURES:
        print(f"FAIL: {failure}")
    raise SystemExit(1)

print("PASS: NEON STAGE UI contract — 9 rotary/APVTS, 7 FX/APVTS, mutually-exclusive mode tabs,")
print("      live rotary arc/pointer, mode-specific artwork/glow, theme propagation and all auxiliary windows.")
