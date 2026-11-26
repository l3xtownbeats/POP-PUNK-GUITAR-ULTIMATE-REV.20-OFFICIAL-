#!/usr/bin/env python3
"""Extract deterministic standalone NEON STAGE UI components from rendered SVG atlases.

This creates review/package assets only. It does not alter the JUCE runtime,
APVTS, DSP, sampler, MIDI routing, control geometry, or parameter semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "ASSETS" / "PPGU_REV20_NEON_STAGE_ASSETS"
DEFAULT_INPUT = ROOT / "build" / "neon_stage_vector_atlases_2x"

STATE_NAMES = ("normal", "hover", "pressed", "active", "disabled")
SWITCH_STATES = ("off", "on")
LED_STATES = ("dim", "lit")


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def safe_crop(image: Image.Image, box: tuple[int, int, int, int], label: str) -> Image.Image:
    left, top, right, bottom = box
    if left < 0 or top < 0 or right > image.width or bottom > image.height:
        raise SystemExit(f"{label}: crop {box} exceeds image bounds {image.size}")
    crop = image.crop(box).convert("RGBA")
    if crop.getchannel("A").getbbox() is None:
        raise SystemExit(f"{label}: crop is completely transparent")
    return crop


def save_crop(image: Image.Image, box: tuple[int, int, int, int],
              target: Path, label: str, records: list[dict]) -> None:
    crop = safe_crop(image, box, label)
    target.parent.mkdir(parents=True, exist_ok=True)
    crop.save(target, format="PNG", optimize=True)
    records.append({
        "asset": label,
        "file": target.as_posix(),
        "width": crop.width,
        "height": crop.height,
        "mode": crop.mode,
        "bytes": target.stat().st_size,
        "sha256": digest(target),
    })


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "build" / "neon_stage_components_2x")
    parser.add_argument("--scale", type=int, choices=(1, 2), default=2)
    args = parser.parse_args()
    scale = args.scale
    src = args.input_dir
    out = args.output
    out.mkdir(parents=True, exist_ok=True)

    atlas_manifest = json.loads(
        (ASSETS / "NEON_STAGE_ATLAS_MANIFEST.json").read_text(encoding="utf-8")
    )
    button_group = atlas_manifest["sheets"][1]["groups"]
    family_ids = button_group[0]["family_ids"]
    switch_names = button_group[1]["switches"]
    led_colours = button_group[2]["colors"]
    icon_names = atlas_manifest["sheets"][4]["groups"][0]["names"]
    if len(family_ids) != 27 or len(switch_names) != 7 or len(led_colours) != 5 or len(icon_names) != 35:
        raise SystemExit("Canonical atlas manifest counts do not match 27/7/5/35 contract")

    records: list[dict] = []
    counts = {"buttons": 0, "fx_switches": 0, "leds": 0, "knob_frames": 0, "icons": 0}

    # The source sheet uses a four-column family matrix, 5 states per family.
    button_path = src / "02_ppgu_atlas_buttons_switches.png"
    with Image.open(button_path) as sheet:
        sheet.load()
        sheet = sheet.convert("RGBA")
        for index, family in enumerate(family_ids):
            row, col = divmod(index, 4)
            family_x = 28 + col * 472
            family_y = 72 + row * 92
            for state_index, state in enumerate(STATE_NAMES):
                x = family_x + state_index * 88 + 5
                y = family_y + 15
                # Two pixels of bleed retain the hover/active glow outside the face.
                box = ((x - 2) * scale, (y - 2) * scale,
                       (x + 80) * scale, (y + 50) * scale)
                target = out / "buttons" / family / f"{state}.png"
                save_crop(sheet, box, target, f"button:{family}:{state}", records)
                counts["buttons"] += 1

        # Seven dedicated FX card switch pairs in the lower atlas band.
        for index, name in enumerate(switch_names):
            group_x = 24 + index * 268
            for state_index, state in enumerate(SWITCH_STATES):
                switch_x = group_x + (10 if state_index == 0 else 126)
                # Preserve bezel and state text, plus a 3px halo allowance.
                box = ((switch_x - 3) * scale, 781 * scale,
                       (switch_x + 111) * scale, 849 * scale)
                target = out / "fx_switches" / name / f"{state}.png"
                save_crop(sheet, box, target, f"fx_switch:{name}:{state}", records)
                counts["fx_switches"] += 1

        # Five LED colours, each with a dim and lit visual.
        for index, colour in enumerate(led_colours):
            group_x = 470 + index * 205
            for state_index, state in enumerate(LED_STATES):
                centre_x = group_x + (28 if state_index == 0 else 102)
                centre_y = 963
                radius = 24
                box = ((centre_x - radius) * scale, (centre_y - radius) * scale,
                       (centre_x + radius) * scale, (centre_y + radius) * scale)
                target = out / "leds" / colour / f"{state}.png"
                save_crop(sheet, box, target, f"led:{colour}:{state}", records)
                counts["leds"] += 1

    # Three 61-frame vertical filmstrips are already exported as exact cell crops.
    for style_index, style_name in enumerate(("conical_chrome", "black_disc", "knurled_steel"), start=1):
        strip_path = src / f"rotary_strip_{style_index}_61_frames.png"
        with Image.open(strip_path) as strip:
            strip.load()
            strip = strip.convert("RGBA")
            expected = (128 * scale, 61 * 128 * scale)
            if strip.size != expected:
                raise SystemExit(f"{strip_path.name}: expected {expected}, got {strip.size}")
            for frame in range(61):
                y = frame * 128 * scale
                box = (0, y, 128 * scale, y + 128 * scale)
                target = out / "knobs" / style_name / f"frame_{frame:03d}.png"
                save_crop(strip, box, target,
                          f"knob:{style_name}:frame_{frame:03d}", records)
                counts["knob_frames"] += 1

    # Icon tiles are laid out left-to-right, seven columns, five rows.
    icons_path = src / "05_ppgu_atlas_icons_hardware.png"
    with Image.open(icons_path) as sheet:
        sheet.load()
        sheet = sheet.convert("RGBA")
        for index, name in enumerate(icon_names):
            row, col = divmod(index, 7)
            x = 40 + col * 265
            y = 80 + row * 135
            box = (x * scale, y * scale, (x + 68) * scale, (y + 68) * scale)
            target = out / "icons" / f"{name}.png"
            save_crop(sheet, box, target, f"icon:{name}", records)
            counts["icons"] += 1

    expected = {
        "buttons": 135, "fx_switches": 14, "leds": 10,
        "knob_frames": 183, "icons": 35,
    }
    if counts != expected:
        raise SystemExit(f"Export count mismatch: expected {expected}, got {counts}")

    package_manifest = {
        "schema": "ppgu.neon-stage.standalone-components/1",
        "skin": "skin-053",
        "theme": "NEON STAGE DEFAULT",
        "scale": f"{scale}x",
        "source_format": "rendered transparent SVG atlas PNGs",
        "source_dir": src.as_posix(),
        "counts": counts,
        "total_assets": sum(counts.values()),
        "visual_acceptance": "EXPORTED_AND_HASHED; PIXEL_PARITY_AND_RUNTIME_WIRING_REMAIN_SEPARATE_GATES",
        "records": records,
    }
    manifest_path = out / "STANDALONE_COMPONENTS_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(package_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("PASS: 377 standalone component PNGs extracted with RGBA and SHA-256.")
    for name, count in counts.items():
        print(f"{name}: {count}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
