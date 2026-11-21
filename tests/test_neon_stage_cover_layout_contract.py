#!/usr/bin/env python3
"""Static guard for the approved NEON STAGE cover composition and journal-only controls."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITOR_H = (ROOT / "Source" / "PluginEditor.h").read_text(encoding="utf-8")
EDITOR_CPP = (ROOT / "Source" / "PluginEditor.cpp").read_text(encoding="utf-8")
THEME_H = (ROOT / "Source" / "UI" / "ThemeManager.h").read_text(encoding="utf-8")
THEME_CPP = (ROOT / "Source" / "UI" / "ThemeManager.cpp").read_text(encoding="utf-8")

checks = {
    "exactly nine approved rotary bindings": 'std::array<juce::Slider, 9> knobs' in EDITOR_H,
    "exactly seven approved main FX switches": 'std::array<juce::TextButton, 7> fxButtons' in EDITOR_H,
    "only MELODY and PATTERN are main mode tabs": 'juce::TextButton melodyTab { "♫  MELODY" }, patternTab { "PATTERN" }' in EDITOR_H,
    "approved guitar hero is a decoded palette asset": "juce::Image heroArtwork" in THEME_H and 'candidate.heroArtwork' in THEME_CPP,
    "main cover draws the guitar hero": "p.heroArtwork" in EDITOR_CPP,
    "no third PUNK GROUP mode": "PUNK GROUP" not in EDITOR_CPP and "PUNK GROUP" not in EDITOR_H,
    "Auto Discover is not exposed as an active feature": "autoSoundHunterButton.setVisible(false)" in EDITOR_CPP,
    "Curator is not exposed as an active feature": "curatorButton.setVisible(false)" in EDITOR_CPP,
    "CPU/RAM are not fabricated as static labels": "CPU: 4.8%" not in EDITOR_CPP and "RAM:" not in EDITOR_CPP,
    "FX EDIT remains an auxiliary action": "openFxEditPanel(detailGroups[i])" in EDITOR_CPP,
}

failed = [name for name, passed in checks.items() if not passed]
for name, passed in checks.items():
    print(("PASS" if passed else "FAIL") + " — " + name)
if failed:
    raise SystemExit(1)
print("PASS — NEON STAGE cover layout contract.")
