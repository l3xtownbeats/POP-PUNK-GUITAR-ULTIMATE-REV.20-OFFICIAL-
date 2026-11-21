#!/usr/bin/env python3
"""Audit the journal-driven NEON STAGE all-window asset and UI contract.

This validator deliberately separates verified structural coverage from visual
artwork completion. A passing contract is not a claim of pixel parity.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIN = ROOT / "SKIN" / "Skin_053"
ASSETS = SKIN / "assets"
SOURCE = ROOT / "Source"


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    pending: list[str] = []

    scope = read_json(ASSETS / "window_asset_scope.json")
    theme = read_json(SKIN / "theme.json")
    controls = read_json(ASSETS / "controls" / "control_states_manifest.json")
    editor = (SOURCE / "PluginEditor.cpp").read_text(encoding="utf-8")
    editor_h = (SOURCE / "PluginEditor.h").read_text(encoding="utf-8")
    theme_manager = (SOURCE / "UI" / "ThemeManager.cpp").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "rev20-windows-vst3-skin-validation.yml").read_text(encoding="utf-8")

    require(scope.get("skin", {}).get("id") == "skin-053", "Scope manifest is not bound to skin-053.", errors)
    require(theme.get("id") == "skin-053", "theme.json is not skin-053.", errors)
    require(theme.get("palette", {}).get("window_bg") == "#080B14", "Wrong NEON STAGE graphite background token.", errors)
    require(theme.get("palette", {}).get("accent") == "#00D9FF", "Wrong NEON STAGE cyan token.", errors)
    require(theme.get("palette", {}).get("accent_glow") == "#6B8CFF", "Wrong NEON STAGE electric-blue token.", errors)
    require("setSize(1024, 700);" in editor, "Main editor default must be 1024x700.", errors)
    require("setResizeLimits(900, 640, 1600, 1100);" in editor, "Main editor resize limits must be 900x640 through 1600x1100.", errors)

    expected_ids = [
        "preset_browser", "mode_selector",
        *(f"knob{i:02d}" for i in range(1, 10)),
        *(f"fx_switch{i:02d}" for i in range(1, 8)),
        "midi_keyboard", "LCD_display", "LED_indicator", "SKIN_button",
        "Import_Guitar", "Auto_Discover", "Curator", "Settings", "About",
    ]
    require(controls.get("controlIds") == expected_ids, "27-control ID order/set differs from the approved contract.", errors)
    required_source_states = {"default", "hover", "pressed", "disabled", "dragged"}
    require(set(controls.get("states", [])) == required_source_states,
            "Current source control-state manifest changed unexpectedly.", errors)
    records = controls.get("records", [])
    record_keys = {(r.get("controlId"), r.get("state")) for r in records}
    require(len(records) == 135 and len(record_keys) == 135,
            "Expected 27 controls × 5 unique source artwork states.", errors)
    for record in records:
        relative = record.get("runtime", "")
        path = (SKIN / relative).resolve()
        require(path.is_relative_to(SKIN.resolve()) and path.is_file(),
                f"Missing/unsafe control artwork: {relative}", errors)

    required_parameters = [
        "ampGain", "eqHigh", "eqMid", "eqLow", "velocity",
        "dynamics", "swing", "humanize", "accent",
    ]
    required_fx = [
        "compressorOn", "eqOn", "distortionOn", "chorusOn",
        "delayOn", "reverbOn", "cabinetOn",
    ]
    for item in required_parameters:
        require(f'"{item}"' in editor_h or f'"{item}"' in editor,
                f"Missing existing main rotary binding: {item}", errors)
    for item in required_fx:
        require(f'"{item}"' in editor_h or f'"{item}"' in editor,
                f"Missing existing main FX binding: {item}", errors)
    require('"MELODY"' in editor and '"PATTERN"' in editor,
            "Both approved main modes must remain present.", errors)
    require("FLANGER" in editor and "fx_switch07" in controls.get("controlIds", []),
            "FX EDIT must retain FLANGER while the control manifest retains exactly seven main switches.", errors)

    for panel_class in (
        "PPGUSkinGalleryPanel", "PPGUSettingsPanel", "PPGUImportGuitarPanel",
        "PPGUFXEditPanel", "PPGUPatternSectionPanel", "PPGUAutoChordsPanel",
    ):
        require(panel_class in editor, f"Missing real auxiliary module class: {panel_class}", errors)

    require('"SETUP ONLY — MIDI CHORD GENERATION / CUSTOM MODE / PREVIEW ENGINE NOT CONNECTED"' in editor,
            "AutoChords must communicate the documented setup-only state.", errors)
    require('offButton.setEnabled(false);' in editor,
            "AutoChords generator control must remain disabled until its backend is connected.", errors)
    require('aboutButton.setEnabled(false);' in editor,
            "About must remain visibly disabled until its approved content module exists.", errors)

    require("candidate.controlsSpriteSheet = {};" in theme_manager
            and "candidate.metersSlidersSpriteSheet = {};" in theme_manager,
            "Legacy prototype atlases must not be loaded into the production skin.", errors)
    require("generate_neon_stage_spritesheets.py" not in workflow,
            "REV.20 CI must not regenerate the legacy mismatched prototype sprite sheets.", errors)

    # The current source art exists, but the journal's full production state set
    # and individual window frame library are not yet complete.
    target_states = set(scope.get("controlContract", {}).get("statesRequired", []))
    current_states = set(controls.get("states", []))
    missing_states = sorted(target_states - current_states)
    if missing_states:
        pending.append("Dedicated control artwork states still missing: " + ", ".join(missing_states))
    required_panel_assets = [
        "PPGU_SKIN053_PANEL_HEADER.png",
        "PPGU_SKIN053_PANEL_PRESET_BROWSER.png",
        "PPGU_SKIN053_PANEL_PLAYING_CORE.png",
        "PPGU_SKIN053_PANEL_AMP_FX_RACK.png",
        "PPGU_SKIN053_PANEL_PERFORMANCE_STRIP.png",
        "PPGU_SKIN053_PANEL_MIDI_KEYBOARD_BAY.png",
        "PPGU_SKIN053_PANEL_STATUS_FOOTER.png",
        "PPGU_SKIN053_PANEL_IMPORT_GUITAR.png",
        "PPGU_SKIN053_PANEL_FX_EDIT.png",
        "PPGU_SKIN053_PANEL_PATTERN_ROUTING.png",
        "PPGU_SKIN053_PANEL_AUTOCHORDS.png",
        "PPGU_SKIN053_PANEL_WORKSPACE_SETTINGS.png",
        "PPGU_SKIN053_PANEL_SKIN_GALLERY.png",
    ]
    missing_panels = [name for name in required_panel_assets if not (ASSETS / "panels" / name).is_file()]
    if missing_panels:
        pending.append(f"Window-specific production panel artwork missing: {len(missing_panels)}/{len(required_panel_assets)} panels")
    art_manifest = read_json(ASSETS / "asset_manifest.json")
    hero = next((r for r in art_manifest.get("records", []) if r.get("path") == "assets/hero.png"), None)
    if hero and hero.get("sha256") == "dcdb2acdcdc01c76c62883ecd542356e6ba6106b0edd0544d74456bae56120f8":
        pending.append("Playing Core hero is the preserved legacy placeholder; exact approved guitar artwork still required.")

    if errors:
        print("NEON STAGE WINDOW SCOPE: FAIL")
        for error in errors:
            print("ERROR:", error)
        return 1

    print("NEON STAGE WINDOW SCOPE CONTRACT: PASS")
    print("27 control IDs and their current 135 runtime artwork files: present")
    print("Main nine rotary bindings, seven FX bindings, and auxiliary module classes: present")
    print("Legacy prototype sprite atlas loading/generation: disabled")
    if pending:
        print("PRODUCTION ARTWORK COMPLETION: NOT COMPLETE")
        for item in pending:
            print("PENDING:", item)
    else:
        print("PRODUCTION ARTWORK COMPLETION: all tracked scope items present (visual review still required)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
