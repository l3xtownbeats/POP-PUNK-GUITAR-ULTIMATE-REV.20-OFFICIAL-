#!/usr/bin/env python3
"""Validate the single canonical REV.20 factory preset database."""
import json
import math
import sys
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else "presets/factory_bank_500.json")
data = json.loads(path.read_text(encoding="utf-8"))
errors = []

if data.get("schemaVersion") != "2.0.0":
    errors.append("schemaVersion must be 2.0.0")
if data.get("catalogId") != "PPGU_FACTORY_MASTER":
    errors.append("catalogId must be PPGU_FACTORY_MASTER")
if data.get("catalogStatus") != "INTEGRATION_IN_PROGRESS":
    errors.append("catalogStatus must remain INTEGRATION_IN_PROGRESS until acceptance")
if data.get("targetPresetCount") != 500:
    errors.append("targetPresetCount must be 500")
presets = data.get("presets")
if not isinstance(presets, list):
    errors.append("presets must be the one canonical array")
    presets = []
if "melodyPresets" in data or "patternPresets" in data:
    errors.append("legacy split preset arrays must not be present")
if data.get("currentPresetCount") != len(presets):
    errors.append(f"currentPresetCount metadata ({data.get('currentPresetCount')!r}) does not match array length ({len(presets)})")
if len(presets) != 300:
    errors.append(f"current authored catalog has {len(presets)} entries; expected 300 at this integration stage (500 is the target, not filler)")

artists = {item.get("name") for item in data.get("artists", []) if isinstance(item, dict)}
seen = set()
mode_counts = {"MELODY": 0, "PATTERN": 0}
ready_count = 0

for index, preset in enumerate(presets):
    label = preset.get("id", f"index {index}") if isinstance(preset, dict) else f"index {index}"
    if not isinstance(preset, dict):
        errors.append(f"{label}: preset entry must be an object")
        continue
    preset_id = preset.get("id")
    if not isinstance(preset_id, str) or not preset_id.strip():
        errors.append(f"{label}: missing non-empty id")
    elif preset_id in seen:
        errors.append(f"{label}: duplicate preset id")
    else:
        seen.add(preset_id)
    if not isinstance(preset.get("name"), str) or not preset["name"].strip():
        errors.append(f"{label}: missing name")
    mode = preset.get("mode")
    if mode not in mode_counts:
        errors.append(f"{label}: mode must be MELODY or PATTERN")
    else:
        mode_counts[mode] += 1
    artist = preset.get("referenceArtist")
    if artist not in artists:
        errors.append(f"{label}: unknown referenceArtist {artist!r}")
    params = preset.get("parameters")
    if not isinstance(params, dict):
        errors.append(f"{label}: parameters must be an object")
        params = {}
    for key, low, high in (("drive", 0, 1), ("tone", 0, 10), ("reverb", 0, 1), ("outputDb", -24, 12)):
        value = params.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            errors.append(f"{label}: parameters.{key} must be a finite number")
        elif not low <= value <= high:
            errors.append(f"{label}: parameters.{key} outside {low}..{high}")
    if mode == "MELODY":
        if not isinstance(preset.get("sampleProfile"), str) or not preset["sampleProfile"].strip():
            errors.append(f"{label}: missing sampleProfile")
        if not preset.get("noteBehavior"):
        errors.append(f"{label}: missing noteBehavior")
    if mode == "PATTERN":
        if not preset.get("groove"):
            errors.append(f"{label}: missing groove")
        if not isinstance(preset.get("sampleRequirement"), str) or not preset["sampleRequirement"].strip():
            errors.append(f"{label}: missing sampleRequirement")
    if preset.get("status") == "READY":
        ready_count += 1

if sum(mode_counts.values()) != len(presets):
    errors.append("one or more entries have an invalid mode")
if ready_count != 0:
    errors.append("No preset may be marked READY until sample/performance mapping and playback acceptance are verified")

if errors:
    print("Unified factory database validation FAILED:")
    for error in errors:
        print(f" - {error}")
    raise SystemExit(1)

print(f"Unified factory database OK: {len(presets)} definitions ({mode_counts['MELODY']} MELODY + {mode_counts['PATTERN']} PATTERN)")
print(f"Playable acceptance: {ready_count}/500; target remains 500, no filler records accepted")
