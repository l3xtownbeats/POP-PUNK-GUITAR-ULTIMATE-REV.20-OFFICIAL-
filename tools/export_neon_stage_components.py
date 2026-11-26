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
from PIL import Image, ImageDraw

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
              target: Path, label: str, records: list[dict], output_root: Path) -> None:
    crop = safe_crop(image, box, label)
    target.parent.mkdir(parents=True, exist_ok=True)
    crop.save(target, format="PNG", optimize=True)
    records.append({
        "asset": label,
        "file": target.relative_to(output_root).as_posix(),
        "width": crop.width,
        "height": crop.height,
        "mode": crop.mode,
        "bytes": target.stat().st_size,
        "sha256": digest(target),
    })





def save_white_key(target: Path, width: int, height: int, scale: int,
                   records: list[dict], output_root: Path, label: str) -> None:
    pixel_width, pixel_height = width * scale, height * scale
    image = Image.new("RGBA", (pixel_width, pixel_height), (0, 0, 0, 0))
    # Slightly cool porcelain-to-anodized gradient, matching the keyboard's
    # white-key face while remaining a fully independent transparent asset.
    top = (246, 250, 254)
    bottom = (202, 216, 229)
    gradient = Image.new("RGB", (1, pixel_height))
    for y in range(pixel_height):
        t = y / max(1, pixel_height - 1)
        rgb = tuple(round(top[i] * (1.0 - t) + bottom[i] * t) for i in range(3))
        gradient.putpixel((0, y), rgb)
    face = gradient.resize((max(1, pixel_width - 2 * scale), max(1, pixel_height - 2 * scale)))
    image.paste(face, (scale, scale))
    draw = ImageDraw.Draw(image)
    outline = (108, 130, 151, 255)
    draw.rounded_rectangle(
        (0, 0, pixel_width - 1, pixel_height - 1),
        radius=2 * scale, outline=outline, width=max(1, 2 * scale)
    )
    draw.line((3 * scale, 4 * scale, 3 * scale, pixel_height - 5 * scale),
              fill=(255, 255, 255, 190), width=max(1, scale))
    draw.line((pixel_width - 4 * scale, 4 * scale,
               pixel_width - 4 * scale, pixel_height - 5 * scale),
              fill=(92, 116, 139, 150), width=max(1, scale))
    draw.line((3 * scale, pixel_height - 4 * scale,
               pixel_width - 4 * scale, pixel_height - 4 * scale),
              fill=(104, 126, 147, 175), width=max(1, scale))
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, format="PNG", optimize=True)
    records.append({
        "asset": label,
        "file": target.relative_to(output_root).as_posix(),
        "width": image.width,
        "height": image.height,
        "mode": image.mode,
        "bytes": target.stat().st_size,
        "sha256": digest(target),
    })

def save_generated_overlay(target: Path, width: int, height: int, scale: int,
                           fill: str, opacity: float, label: str,
                           records: list[dict], output_root: Path) -> None:
    rgb = tuple(int(fill[index:index + 2], 16) for index in (1, 3, 5))
    alpha = max(0, min(255, round(255 * opacity)))
    layer = Image.new("RGBA", (width * scale, height * scale), (*rgb, alpha))
    target.parent.mkdir(parents=True, exist_ok=True)
    layer.save(target, format="PNG", optimize=True)
    records.append({
        "asset": label,
        "file": target.relative_to(output_root).as_posix(),
        "width": layer.width,
        "height": layer.height,
        "mode": layer.mode,
        "bytes": target.stat().st_size,
        "sha256": digest(target),
    })

def save_contact_sheet(records: list[dict], prefix: str, columns: int,
                       output: Path, thumb_size: tuple[int, int]) -> dict | None:
    selected = [item for item in records if item["asset"].startswith(prefix)]
    if not selected:
        return None
    thumb_w, thumb_h = thumb_size
    cell_w, cell_h = thumb_w + 18, thumb_h + 30
    rows = (len(selected) + columns - 1) // columns
    sheet = Image.new("RGBA", (columns * cell_w, rows * cell_h), (5, 10, 18, 255))
    draw = ImageDraw.Draw(sheet)
    for index, item in enumerate(selected):
        col, row = index % columns, index // columns
        x, y = col * cell_w, row * cell_h
        with Image.open(output / item["file"]) as source:
            thumb = source.convert("RGBA")
            thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            px = x + (thumb_w - thumb.width) // 2 + 9
            py = y + 2 + (thumb_h - thumb.height) // 2
            sheet.alpha_composite(thumb, (px, py))
        label = item["asset"].replace(prefix, "").replace(":", " / ")
        if len(label) > 25:
            label = label[:22] + "..."
        draw.text((x + 6, y + thumb_h + 5), label, fill=(183, 221, 239, 255))
    target = output / "previews" / f"{prefix.rstrip(':').replace(':', '_')}_contact_sheet.jpg"
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(target, format="JPEG", quality=91, optimize=True)
    return {
        "file": target.relative_to(output).as_posix(),
        "width": sheet.width,
        "height": sheet.height,
        "bytes": target.stat().st_size,
        "sha256": digest(target),
        "items": len(selected),
    }

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
    background_group = atlas_manifest["sheets"][0]["groups"][0]
    frame_group = atlas_manifest["sheets"][0]["groups"][1]
    display_group = atlas_manifest["sheets"][3]["groups"][0]
    keyboard_group = atlas_manifest["sheets"][3]["groups"][1]
    fader_group = atlas_manifest["sheets"][3]["groups"][2]
    hardware_group = atlas_manifest["sheets"][4]["groups"][1]
    if (len(family_ids) != 27 or len(button_states) != 5 or len(switch_names) != 7
            or len(switch_states) != 2 or len(led_colours) != 5 or len(led_states) != 2
            or len(icon_names) != 35):
        raise SystemExit("Canonical atlas manifest counts do not match 27/7/5/35 contract")

    records: list[dict] = []
    counts = {
        "backgrounds": 0, "panel_frames": 0,
        "buttons": 0, "fx_switches": 0, "leds": 0,
        "knob_frames": 0, "icons": 0,
        "display_frames": 0, "meter_segments": 0,
        "white_keys": 0, "black_keys": 0, "active_key_overlays": 0,
        "fader_parts": 0, "hardware_parts": 0,
    }

    # Background material swatches and standalone bezel/frame elements.
    background_path = src / "01_ppgu_atlas_backgrounds_frames.png"
    with Image.open(background_path) as sheet:
        sheet.load()
        sheet = sheet.convert("RGBA")
        grid = background_group["grid"]
        for index, name in enumerate(background_group["items"]):
            x = int(grid["origin_x"]) + index * int(grid["step_x"])
            y = int(grid["origin_y"])
            width, height = int(grid["cell_width"]), int(grid["cell_height"])
            box = (x * scale, y * scale, (x + width) * scale, (y + height) * scale)
            target = out / "backgrounds" / f"{name}.png"
            save_crop(sheet, box, target, f"background:{name}", records, out)
            counts["backgrounds"] += 1
        padding = int(frame_group.get("crop_padding", 0))
        for item in frame_group["items"]:
            x, y, width, height = (int(item[k]) for k in ("x", "y", "w", "h"))
            box = ((x - padding) * scale, (y - padding) * scale,
                   (x + width + padding) * scale, (y + height + padding) * scale)
            target = out / "panel_frames" / f"{item['id']}.png"
            save_crop(sheet, box, target, f"panel_frame:{item['id']}", records, out)
            counts["panel_frames"] += 1

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
                save_crop(sheet, box, target, f"button:{family}:{state}", records, out)
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
                save_crop(sheet, box, target, f"fx_switch:{name}:{state}", records, out)
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
                save_crop(sheet, box, target, f"led:{colour}:{state}", records, out)
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
                          f"knob:{style_name}:frame_{frame:03d}", records, out)
                counts["knob_frames"] += 1

    # Display frames, value/status tiles and twelve individual meter segments.
    displays_path = src / "04_ppgu_atlas_displays_keyboard.png"
    with Image.open(displays_path) as sheet:
        sheet.load()
        sheet = sheet.convert("RGBA")
        for name, bounds in display_group["bounds"].items():
            x, y, width, height = map(int, bounds)
            box = (x * scale, y * scale, (x + width) * scale, (y + height) * scale)
            target = out / "displays" / f"{name}.png"
            save_crop(sheet, box, target, f"display:{name}", records, out)
            counts["display_frames"] += 1

        meter = display_group["meter_segments"]
        for index in range(int(meter["count"])):
            x = int(meter["x"])
            y = int(meter["y"]) + index * int(meter["step_y"])
            width, height = int(meter["width"]), int(meter["height"])
            box = (x * scale, y * scale, (x + width) * scale, (y + height) * scale)
            target = out / "meters" / "reference_sample" / f"segment_{index + 1:02d}.png"
            save_crop(sheet, box, target, f"meter_segment:{index + 1:02d}", records, out)
            counts["meter_segments"] += 1

        # Individual white keys are exported in their neutral state; active tints
        # are generated as transparent overlays so JUCE can composite them live.
        white = keyboard_group["white_key_layout"]
        active_overlays = keyboard_group["active_key_overlays"]
        normal_rgb = tuple(int(white["normal_fill"][i:i + 2], 16) for i in (1, 3, 5))
        for index in range(int(white["count"])):
            x = int(white["x0"]) + index * int(white["step_x"])
            y, width, height = (int(white[k]) for k in ("y", "width", "height"))
            target = out / "keyboard" / "white" / f"white_{index + 1:02d}.png"
            save_white_key(
                target, width, height, scale, records, out,
                f"key:white:{index + 1:02d}"
            )
            counts["white_keys"] += 1

        black = keyboard_group["black_key_layout"]
        y, width, height = (int(black[k]) for k in ("y", "width", "height"))
        for index, x_value in enumerate(black["x_positions"]):
            x = int(x_value)
            box = (x * scale, y * scale, (x + width) * scale, (y + height) * scale)
            target = out / "keyboard" / "black" / f"black_{index + 1:02d}.png"
            save_crop(sheet, box, target, f"key:black:{index + 1:02d}", records, out)
            counts["black_keys"] += 1

        overlay_style = keyboard_group["active_overlay_style"]
        for overlay in active_overlays:
            name = overlay["name"]
            _, _, width, height = (int(overlay[k]) for k in ("x", "y", "width", "height"))
            target = out / "keyboard" / "active_overlays" / f"{name}.png"
            save_generated_overlay(
                target, width, height, scale,
                overlay_style["fill"], float(overlay_style["opacity"]),
                f"key:active:{name}", records, out
            )
            counts["active_key_overlays"] += 1

        # Pitch and modulation rails and their three distinct positions.
        for name in ("pitch", "mod"):
            layout = fader_group["fader_layout"][name]
            x, y, width, height = map(int, layout["track"])
            box = (x * scale, y * scale, (x + width) * scale, (y + height) * scale)
            target = out / "faders" / name / "track.png"
            save_crop(sheet, box, target, f"fader:{name}:track", records, out)
            counts["fader_parts"] += 1
            thumb_x = int(layout["thumb_x"])
            thumb_w, thumb_h = map(int, fader_group["fader_layout"]["thumb_size"])
            for pose, thumb_y in zip(("min", "mid", "max"), fader_group["fader_layout"]["thumb_y_positions"]):
                thumb_y = int(thumb_y)
                box = (thumb_x * scale, thumb_y * scale,
                       (thumb_x + thumb_w) * scale, (thumb_y + thumb_h) * scale)
                target = out / "faders" / name / f"thumb_{pose}.png"
                save_crop(sheet, box, target, f"fader:{name}:thumb:{pose}", records, out)
                counts["fader_parts"] += 1

    # Standalone hardware pieces from the icon/hardware atlas.
    hardware_path = src / "05_ppgu_atlas_icons_hardware.png"
    with Image.open(hardware_path) as sheet:
        sheet.load()
        sheet = sheet.convert("RGBA")
        geometry = hardware_group["crop_geometry"]
        for name in ("side_bracket_type_1", "side_bracket_type_2",
                     "side_bracket_type_3", "vent_grille", "blue_light_bar"):
            x, y, width, height = map(int, geometry[name])
            box = (x * scale, y * scale, (x + width) * scale, (y + height) * scale)
            target = out / "hardware" / f"{name}.png"
            save_crop(sheet, box, target, f"hardware:{name}", records, out)
            counts["hardware_parts"] += 1
        screws = geometry["screw_set"]
        radius = int(screws["radius"])
        centre_y = int(screws["centre_y"])
        for index, centre_x in enumerate(screws["centres_x"]):
            centre_x = int(centre_x)
            box = ((centre_x - radius) * scale, (centre_y - radius) * scale,
                   (centre_x + radius) * scale, (centre_y + radius) * scale)
            target = out / "hardware" / "screws" / f"screw_{index + 1:02d}.png"
            save_crop(sheet, box, target, f"hardware:screw:{index + 1:02d}", records, out)
            counts["hardware_parts"] += 1

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
            save_crop(sheet, box, target, f"icon:{name}", records, out)
            counts["icons"] += 1

    expected = {
        "backgrounds": 5, "panel_frames": 7,
        "buttons": 135, "fx_switches": 14, "leds": 10,
        "knob_frames": 183, "icons": 35,
        "display_frames": 10, "meter_segments": 12,
        "white_keys": 29, "black_keys": 20, "active_key_overlays": 3,
        "fader_parts": 8, "hardware_parts": 13,
    }
    if counts != expected:
        raise SystemExit(f"Export count mismatch: expected {expected}, got {counts}")

    previews = {
        "backgrounds": save_contact_sheet(records, "background:", 5, out, (120, 80)),
        "panel_frames": save_contact_sheet(records, "panel_frame:", 4, out, (120, 70)),
        "buttons": save_contact_sheet(records, "button:", 5, out, (76, 48)),
        "fx_switches": save_contact_sheet(records, "fx_switch:", 2, out, (108, 62)),
        "leds": save_contact_sheet(records, "led:", 2, out, (52, 52)),
        "knobs": {style: save_contact_sheet(records, f"knob:{style}:", 16, out, (48, 48)) for style in rotary_styles},
        "icons": save_contact_sheet(records, "icon:", 7, out, (68, 68)),
        "displays": save_contact_sheet(records, "display:", 4, out, (120, 70)),
        "meter_segments": save_contact_sheet(records, "meter_segment:", 6, out, (46, 18)),
        "keyboard": save_contact_sheet(records, "key:", 7, out, (36, 82)),
        "faders": save_contact_sheet(records, "fader:", 4, out, (68, 62)),
        "hardware": save_contact_sheet(records, "hardware:", 5, out, (68, 58)),
    }

    package_manifest = {
        "schema": "ppgu.neon-stage.standalone-components/1",
        "skin": "skin-053",
        "theme": "NEON STAGE DEFAULT",
        "scale": f"{scale}x",
        "source_format": "rendered transparent SVG atlas PNGs",
        "source_dir": src.as_posix(),
        "counts": counts,
        "total_assets": sum(counts.values()),
        "contact_sheets": previews,
        "visual_acceptance": "EXPORTED_AND_HASHED; PIXEL_PARITY_AND_RUNTIME_WIRING_REMAIN_SEPARATE_GATES",
        "records": records,
    }
    manifest_path = out / "STANDALONE_COMPONENTS_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(package_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"PASS: {sum(counts.values())} standalone component PNGs extracted with RGBA and SHA-256.")
    for name, count in counts.items():
        print(f"{name}: {count}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
