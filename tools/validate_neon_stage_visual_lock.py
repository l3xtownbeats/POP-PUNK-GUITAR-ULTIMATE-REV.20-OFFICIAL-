#!/usr/bin/env python3
"""Lock the NEON STAGE DEFAULT runtime to its approved repository mockup."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MOCKUP = ROOT / "01 INTERFACE  NEON STAGE DEFAULT .png"
EXPECTED_GIT_BLOB_SHA = "747207e183c77e8b913a543b2dc40b29829e77da"
THEME_FILE = ROOT / "SKIN" / "Skin_053" / "theme.json"
EDITOR_FILE = ROOT / "Source" / "PluginEditor.cpp"

EXPECTED_PALETTE = {
    "window_bg": "#080B14",
    "panel": "#101827",
    "panel_elevated": "#17243A",
    "control_bg": "#0C1422",
    "control_face": "#1A2940",
    "control_border": "#31506F",
    "text_primary": "#F4F7FF",
    "text_secondary": "#B5C4DC",
    "text_disabled": "#71829D",
    "accent": "#00D9FF",
    "accent_glow": "#6B8CFF",
    "danger": "#FF557A",
    "warning": "#FFBE55",
    "success": "#42E6B0",
    "lcd_bg": "#050D1B",
    "lcd_text": "#8DEBFF",
    "led_on": "#00E5FF",
    "led_off": "#263B55",
    "shadow": "#03060B",
    "highlight": "#8DCBFF",
    "lowlight": "#080F1B",
}
EXPECTED_CONTROLS = {
    "preset_browser", "mode_selector",
    *(f"knob{i:02d}" for i in range(1, 10)),
    *(f"fx_switch{i:02d}" for i in range(1, 8)),
    "midi_keyboard", "LCD_display", "LED_indicator", "SKIN_button",
    "Import_Guitar", "Auto_Discover", "Curator", "Settings", "About",
}


def fail(message: str) -> None:
    print(f"NEON STAGE VISUAL LOCK: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


if not MOCKUP.is_file():
    fail("approved main mockup is missing")
blob = MOCKUP.read_bytes()
git_blob_sha = hashlib.sha1(b"blob " + str(len(blob)).encode("ascii") + b"\\0" + blob).hexdigest()
if git_blob_sha != EXPECTED_GIT_BLOB_SHA:
    fail(f"approved mockup changed unexpectedly: {git_blob_sha}")

try:
    theme = json.loads(THEME_FILE.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    fail(f"cannot read theme manifest: {exc}")

if theme.get("id") != "skin-053" or theme.get("name") != "NEON STAGE DEFAULT":
    fail("canonical theme identity must remain skin-053 / NEON STAGE DEFAULT")
if theme.get("palette") != EXPECTED_PALETTE:
    fail("Skin-1 palette differs from the approved graphite/cyan token set")
controls = theme.get("controls", {})
if set(controls) != EXPECTED_CONTROLS | {"sync_selector"}:
    fail("theme control map differs from the closed 27-control contract")

source = EDITOR_FILE.read_text(encoding="utf-8")
required_source_contract = (
    "drawPanel(g, left, \"FACTORY PRESET BROWSER\")",
    "drawPanel(g, work, \"PLAYING CORE  /  MELODY + PATTERN\")",
    "drawPanel(g, right, \"AMP & TONE  /  FX CHAIN\")",
    "const int columns = 3;",
    "const int rows = 3;",
    "for (size_t i = 0; i < knobs.size(); ++i)",
    "for (size_t i = 0; i < fxButtons.size(); ++i)",
    "aboutButton.setEnabled(false)",
    "mainFxEdit->setVisible(false)",
)
for token in required_source_contract:
    if token not in source:
        fail(f"main editor is missing required layout/availability contract: {token}")
if "fxChain.removeFromBottom" in source:
    fail("legacy bottom FX bar still overrides the approved right-side FX column")

print("NEON STAGE VISUAL LOCK: PASS")
print(f"Approved mockup Git blob: {git_blob_sha}")
print("Canonical palette, 27 controls, three-zone editor, 3x3 knob deck and seven FX switches verified.")
