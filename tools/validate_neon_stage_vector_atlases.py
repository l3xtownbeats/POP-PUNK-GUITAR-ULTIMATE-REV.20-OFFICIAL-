#!/usr/bin/env python3
"""Structural checks for the supplemental PPGU NEON STAGE SVG atlas masters.

Uses only the Python standard library. This is not pixel-level visual QA,
PNG export validation, or proof that an asset is wired into the JUCE runtime.
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "ASSETS" / "PPGU_REV20_NEON_STAGE_ASSETS"

SHEETS = {
    "01_ppgu_atlas_backgrounds_frames.svg": (1920, 1000),
    "02_ppgu_atlas_buttons_switches.svg": (1920, 1020),
    "03_ppgu_atlas_knob_strips.svg": (1920, 8000),
    "04_ppgu_atlas_displays_keyboard.svg": (1920, 1840),
    "05_ppgu_atlas_icons_hardware.svg": (1920, 1020),
}
ICON_NAMES = {
    "IMPORT", "GUITAR", "SFZ", "WAV", "PRESET", "SEARCH", "MELODY",
    "PATTERN", "AUTOCHORDS", "SETTINGS", "SKIN", "FAVORITE", "PREVIEW",
    "APPLY", "CANCEL", "POWER", "COMPRESSOR", "EQ", "DISTORTION",
    "CHORUS", "FLANGER", "DELAY", "REVERB", "CABINET", "KEYBOARD",
    "MIDI", "HARMONY", "NOTES", "LIBRARY", "WARNING", "ERROR", "SUCCESS",
    "INFO", "CLOSE", "MINIMIZE", "MAXIMIZE", "ARROW_DOWN", "ARROW_LEFT",
    "ARROW_RIGHT", "CHEVRON", "STAR",
}
BUTTON_FAMILIES = {
    "PILL", "SLAB", "TAB", "ICON", "TOGGLE", "LABEL", "FAVORITE",
    "POWER", "LOAD", "SAVE", "BROWSER", "PRESET", "MODE", "MIDI",
    "FX", "AMP", "TONE", "CAB", "CHORUS", "DELAY", "REVERB", "EQ",
    "COMP", "DRIVE", "HARMONY", "SCALE", "SETTINGS",
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def children_named(node: ET.Element, name: str):
    return [child for child in node.iter() if local_name(child.tag) == name]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> int:
    parsed: dict[str, ET.Element] = {}
    for filename, expected_size in SHEETS.items():
        path = ASSETS / filename
        if not path.is_file():
            fail(f"missing atlas: {path}")
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            fail(f"{filename}: invalid SVG/XML: {exc}")
        if local_name(root.tag) != "svg":
            fail(f"{filename}: root element is not <svg>")
        width = int(float(root.attrib.get("width", "0")))
        height = int(float(root.attrib.get("height", "0")))
        view_box = root.attrib.get("viewBox", "").split()
        if (width, height) != expected_size:
            fail(f"{filename}: expected {expected_size}, got {(width, height)}")
        if view_box != ["0", "0", str(width), str(height)]:
            fail(f"{filename}: viewBox does not match declared dimensions")
        for element in root.iter():
            if any(key.endswith("href") for key in element.attrib):
                fail(f"{filename}: external/embedded href found; keep masters self-contained")
            if local_name(element.tag) == "rect":
                rw = float(element.attrib.get("width", "0"))
                rh = float(element.attrib.get("height", "0"))
                if rw >= width and rh >= height:
                    fail(f"{filename}: opaque full-sheet rectangle defeats transparent atlas canvas")
        parsed[filename] = root

    backgrounds = parsed["01_ppgu_atlas_backgrounds_frames.svg"]
    if not any(node.attrib.get("id") == "weaveClip" for node in children_named(backgrounds, "clipPath")):
        fail("background atlas: carbon-weave swatch must be clipped to its own tile")

    buttons = parsed["02_ppgu_atlas_buttons_switches.svg"]
    family_labels = {
        (node.text or "").strip()
        for node in children_named(buttons, "text")
        if re.match(r"^\d{2} ", (node.text or "").strip())
    }
    if len(family_labels) != 27:
        fail(f"button atlas: expected 27 family headings, found {len(family_labels)}")
    if {label.split(" ", 1)[1] for label in family_labels} != BUTTON_FAMILIES:
        fail("button atlas: family headings do not match the canonical 27-family contract")

    rotary = parsed["03_ppgu_atlas_knob_strips.svg"]
    strip_groups: dict[int, list[tuple[int, int]]] = {84: [], 334: [], 584: []}
    for node in children_named(rotary, "g"):
        match = re.fullmatch(r"translate\((\d+) (\d+)\)", node.attrib.get("transform", ""))
        if not match:
            continue
        x, y = map(int, match.groups())
        if x in strip_groups:
            rotations = [
                child.attrib.get("transform", "")
                for child in children_named(node, "g")
                if child.attrib.get("transform", "").startswith("rotate(")
            ]
            if len(rotations) != 1:
                fail(f"rotary frame at x={x}, y={y}: expected one needle rotation")
            angle_match = re.fullmatch(r"rotate\(([-\d.]+) 0 0\)", rotations[0])
            if not angle_match:
                fail(f"rotary frame at x={x}, y={y}: malformed rotation")
            strip_groups[x].append((y, int(float(angle_match.group(1)))))
    for x, frames in strip_groups.items():
        frames.sort()
        if len(frames) != 61:
            fail(f"rotary strip x={x}: expected 61 frames, found {len(frames)}")
        for index, (y, angle) in enumerate(frames):
            if y != 134 + index * 128:
                fail(f"rotary strip x={x}: frame {index} has unexpected y={y}")
            if angle != 210 + index * 3:
                fail(f"rotary strip x={x}: frame {index} has unexpected angle={angle}")

    keyboard = parsed["04_ppgu_atlas_displays_keyboard.svg"]
    keyboard_rects = children_named(keyboard, "rect")
    white_keys = [
        node for node in keyboard_rects
        if node.attrib.get("y") == "390"
        and node.attrib.get("width") == "63"
        and node.attrib.get("height") == "230"
        and node.attrib.get("fill") == "#d8e5ef"
    ]
    black_key_groups = [
        node for node in children_named(keyboard, "g")
        if node.attrib.get("class") == "ppgu-black-key"
    ]
    black_keys = []
    for group in black_key_groups:
        bodies = [
            node for node in list(group)
            if local_name(node.tag) == "rect"
            and node.attrib.get("y") == "390"
            and node.attrib.get("width") == "38"
            and node.attrib.get("height") == "135"
            and node.attrib.get("fill") == "url(#blackKey)"
        ]
        if len(bodies) != 1:
            fail("keyboard atlas: black-key group must contain one gradient key body")
        black_keys.extend(bodies)
    if not any(node.attrib.get("id") == "blackKey" for node in children_named(keyboard, "linearGradient")):
        fail("keyboard atlas: metallic black-key gradient is missing")
    active_keys = [
        node for node in keyboard_rects
        if node.attrib.get("y") == "555"
        and node.attrib.get("fill") == "#00d9ff"
    ]
    if len(white_keys) != 29 or len(black_keys) != 20 or len(active_keys) != 3:
        fail(
            "keyboard atlas: expected 29 white keys, 20 black keys and "
            f"3 C/E/G active overlays; found {len(white_keys)}/{len(black_keys)}/{len(active_keys)}"
        )

    if len([node for node in keyboard_rects if node.attrib.get("x") == "1080" and node.attrib.get("width") == "42" and node.attrib.get("height") == "9"]) != 12:
        fail("display atlas: expected a 12-segment meter sample")

    rotary_first_frames = {}
    for x in (334, 584):
        frame = next(node for node in children_named(rotary, "g") if node.attrib.get("transform") == f"translate({x} 134)")
        rotary_first_frames[x] = ET.tostring(frame, encoding="unicode")
    if rotary_first_frames[334] == rotary_first_frames[584]:
        fail("rotary atlas: black-disc and knurled-steel materials must be distinct")

    icons = parsed["05_ppgu_atlas_icons_hardware.svg"]
    icon_groups = [
        node for node in children_named(icons, "g")
        if re.fullmatch(r"translate\(\d+ \d+\)", node.attrib.get("transform", ""))
    ]
    labels = []
    glyph_bodies = []
    for group in icon_groups:
        labels.extend(
            (node.text or "").strip()
            for node in children_named(group, "text")
            if (node.text or "").strip()
        )
        nested = [
            child for child in list(group)
            if local_name(child.tag) == "g"
        ]
        if len(nested) != 1:
            fail("icon atlas: each tile must contain exactly one glyph group")
        glyph_bodies.append(ET.tostring(nested[0], encoding="unicode"))
    if len(icon_groups) != 41 or set(labels) != ICON_NAMES or len(labels) != 41:
        fail(f"icon atlas: expected all 41 named icon tiles, found {len(icon_groups)}")
    if len(set(glyph_bodies)) != 41:
        fail("icon atlas: duplicate glyph body detected")

    print("PASS: 5 SVG masters parse; dimensions/viewBoxes and transparent canvases match.")
    print("PASS: carbon-weave material is clipped to its swatch.")
    print("PASS: 27 button-family headings match the declared contract.")
    print("PASS: 3 rotary strips × 61 frames; 128px pitch; 210°–390° in 3° steps; materials differ.")
    print("PASS: 49-key keyboard contains 29 white keys, 20 black keys and C/E/G active overlays.")
    print("PASS: display atlas includes a 12-segment meter sample.")
    print("PASS: 41 icon tiles have 41 distinct glyph bodies and all declared labels.")
    print("NOTE: This validator does not render images or replace pixel-level visual QA.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
