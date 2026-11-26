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
    button_states = button_group[0]["states"]
    button_grid = button_group[0]["grid"]
    switch_names = button_group[1]["switches"]
    switch_layout = button_group[1]["card_layout"]
    switch_states = button_group[1]["states"]
    led_colours = button_group[2]["colors"]
    led_states = button_group[2]["states"]
    led_layout = button_group[2]["layout"]
    rotary_group = atlas_manifest["sheets"][2]["groups"][0]
    icon_group = atlas_manifest["sheets"][4]["groups"][0]
    icon_names = icon_group["names"]
    icon_grid = icon_group["grid"]
    if (len(family_ids) != 27 or len(button_states) != 5 or len(switch_names) != 7
            or len(switch_states) != 2 or len(led_colours) != 5 or len(led_states) != 2
            or len(icon_names) != 35):
        raise SystemExit("Canonical atlas manifest counts do not match 27/7/5/35 contract")

    records: list[dict] = []
    counts = {"buttons": 0, "fx_switches": 0, "leds": 0, "knob_frames": 0, "icons": 0}

    # The source sheet uses a four-column family matrix, 5 states per family.
    button_path = src / "02_ppgu_atlas_buttons_switches.png"
    with Image.open(button_path) as sheet:
        sheet.load()
        sheet = sheet.convert("RGBA")
        for index, family in enumerate(family_ids):
            row, col = divmod(index, int(button_grid["family_columns"]))
            family_x = int(button_grid["origin_x"]) + col * int(button_grid["family_step_x"])
            family_y = int(button_grid["origin_y"]) + row * int(button_grid["family_step_y"])
            for state_index, state in enumerate(button_states):
                x = family_x + state_index * int(button_grid["state_step_x"]) + int(button_grid["state_offset_x"])
                y = family_y + int(button_grid["state_offset_y"])
                padding = int(button_grid["crop_padding"])
                width = int(button_grid["control_width"])
                height = int(button_grid["control_height"])
                box = ((x - padding) * scale, (y - padding) * scale,
                       (x + width + padding) * scale, (y + height + padding) * scale)
                target = out / "buttons" / family / f"{state}.png"
                save_crop(sheet, box, target, f"button:{family}:{state}", records)
                counts["buttons"] += 1

        # Seven dedicated FX card switch pairs in the lower atlas band.
        for index, name in enumerate(switch_names):
            group_x = int(switch_layout["origin_x"]) + index * int(switch_layout["card_step_x"])
            for state in switch_states:
                state_layout = switch_layout["states"][state]
                switch_x = group_x + int(state_layout["offset"][0])
                switch_y = int(switch_layout["origin_y"]) + int(state_layout["offset"][1])
                width, height = map(int, state_layout["size"])
                pad_x, pad_y = map(int, state_layout["crop_padding"])
                # Preserve bezel and state text, plus the authored halo allowance.
                box = ((switch_x - pad_x) * scale, (switch_y - pad_y) * scale,
                       (switch_x + width + pad_x) * scale,
                       (switch_y + height + pad_y) * scale)
                target = out / "fx_switches" / name / f"{state}.png"
                save_crop(sheet, box, target, f"fx_switch:{name}:{state}", records)
                counts["fx_switches"] += 1

        # Five LED colours, each with a dim and lit visual.
        for index, colour in enumerate(led_colours):
            group_x = int(led_layout["origin_x"]) + index * int(led_layout["group_step_x"])
            for state_index, state in enumerate(led_states):
                centre_x = group_x + int(led_layout["state_center_offsets"][state_index][0])
                centre_y = int(led_layout["origin_y"]) + int(led_layout["state_center_offsets"][state_index][1])
                radius = int(led_layout["crop_radius"])
                box = ((centre_x - radius) * scale, (centre_y - radius) * scale,
                       (centre_x + radius) * scale, (centre_y + radius) * scale)
                target = out / "leds" / colour / f"{state}.png"
                save_crop(sheet, box, target, f"led:{colour}:{state}", records)
                counts["leds"] += 1

    # Three 61-frame vertical filmstrips are already exported as exact cell crops.
    rotary_styles = rotary_group["styles"]
    frame_count = int(rotary_group["frames_per_style"])
    frame_width, frame_height = map(int, rotary_group["frame_size"])
    for style_index, style_name in enumerate(rotary_styles, start=1):
        strip_path = src / f"rotary_strip_{style_index}_{frame_count}_frames.png"
        with Image.open(strip_path) as strip:
            strip.load()
            strip = strip.convert("RGBA")
            expected = (frame_width * scale, frame_count * frame_height * scale)
            if strip.size != expected:
                raise SystemExit(f"{strip_path.name}: expected {expected}, got {strip.size}")
            for frame in range(frame_count):
                y = frame * frame_height * scale
                box = (0, y, frame_width * scale, y + frame_height * scale)
                target = out / "knobs" / style_name / f"frame_{frame:03d}.png"
                save_crop(strip, box, target,
                          f"knob:{style_name}:frame_{frame:03d}", records)
                counts["knob_frames"] += 1

    # Icon tiles are laid out according to their canonical atlas manifest grid.
    icons_path = src / "05_ppgu_atlas_icons_hardware.png"
    with Image.open(icons_path) as sheet:
        sheet.load()
        sheet = sheet.convert("RGBA")
        for index, name in enumerate(icon_names):
            row, col = divmod(index, int(icon_grid["columns"]))
            x = int(icon_grid["origin_x"]) + col * int(icon_grid["step_x"])
            y = int(icon_grid["origin_y"]) + row * int(icon_grid["step_y"])
            icon_width, icon_height = map(int, icon_group["cell_size"])
            box = (x * scale, y * scale,
                   (x + icon_width) * scale, (y + icon_height) * scale)
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
