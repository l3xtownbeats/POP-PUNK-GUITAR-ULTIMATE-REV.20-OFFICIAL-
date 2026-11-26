#!/usr/bin/env python3
"""Export 41 standalone PPGU neon icons as SVG and 16/24/32/48 RGBA PNGs."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

import cairosvg
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "ASSETS" / "PPGU_REV20_NEON_STAGE_ASSETS"
SOURCE = ASSETS / "05_ppgu_atlas_icons_hardware.svg"
SIZES = (16, 24, 32, 48)
EXPECTED = (
    "IMPORT", "GUITAR", "SFZ", "WAV", "PRESET", "SEARCH", "MELODY",
    "PATTERN", "AUTOCHORDS", "SETTINGS", "SKIN", "FAVORITE", "PREVIEW",
    "APPLY", "CANCEL", "POWER", "COMPRESSOR", "EQ", "DISTORTION",
    "CHORUS", "FLANGER", "DELAY", "REVERB", "CABINET", "KEYBOARD",
    "MIDI", "HARMONY", "NOTES", "LIBRARY", "WARNING", "ERROR", "SUCCESS",
    "INFO", "CLOSE", "MINIMIZE", "MAXIMIZE", "ARROW_DOWN", "ARROW_LEFT",
    "ARROW_RIGHT", "CHEVRON", "STAR",
)
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "neon_stage_icons")
    args = parser.parse_args()
    output: Path = args.output
    output.mkdir(parents=True, exist_ok=True)

    source_root = ET.parse(SOURCE).getroot()
    defs = next((node for node in list(source_root) if local(node.tag) == "defs"), None)
    if defs is None:
        raise SystemExit("Icon atlas has no self-contained <defs> section.")
    glow = next(
        (node for node in defs.iter() if local(node.tag) == "filter" and node.attrib.get("id") == "glow"),
        None,
    )
    if glow is None:
        raise SystemExit("Icon atlas is missing its local glow filter.")

    icons: dict[str, ET.Element] = {}
    for group in source_root.iter():
        if local(group.tag) != "g" or not re.fullmatch(r"translate\(\d+ \d+\)", group.attrib.get("transform", "")):
            continue
        labels = [
            (child.text or "").strip()
            for child in list(group)
            if local(child.tag) == "text" and (child.text or "").strip()
        ]
        glyphs = [child for child in list(group) if local(child.tag) == "g"]
        if len(labels) != 1 or len(glyphs) != 1:
            raise SystemExit("Each icon tile must have one label and one glyph group.")
        name = labels[0]
        if name in icons:
            raise SystemExit(f"Duplicate icon name: {name}")
        icons[name] = copy.deepcopy(glyphs[0])

    if tuple(name for name in EXPECTED if name in icons) != EXPECTED:
        missing = [name for name in EXPECTED if name not in icons]
        extras = [name for name in icons if name not in EXPECTED]
        raise SystemExit(f"Icon family mismatch; missing={missing}, extras={extras}")
    if len(icons) != 41:
        raise SystemExit(f"Expected 41 individual icon masters, found {len(icons)}.")

    records: list[dict] = []
    glyph_serialized = set()
    for name in EXPECTED:
        glyph = icons[name]
        serialized = ET.tostring(glyph, encoding="unicode")
        if serialized in glyph_serialized:
            raise SystemExit(f"Duplicate glyph body: {name}")
        glyph_serialized.add(serialized)

        icon_root = ET.Element(
            f"{{{SVG_NS}}}svg",
            {"width": "68", "height": "68", "viewBox": "0 0 68 68", "version": "1.1"},
        )
        icon_defs = ET.SubElement(icon_root, f"{{{SVG_NS}}}defs")
        icon_defs.append(copy.deepcopy(glow))
        icon_root.append(glyph)
        svg_path = output / "svg" / f"{name.lower()}.svg"
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(icon_root).write(svg_path, encoding="utf-8", xml_declaration=True)
        records.append({
            "name": name,
            "format": "SVG",
            "file": svg_path.relative_to(output).as_posix(),
            "width": 68,
            "height": 68,
            "bytes": svg_path.stat().st_size,
            "sha256": sha256(svg_path),
        })

        for size in SIZES:
            png_path = output / "png" / str(size) / f"{name.lower()}.png"
            png_path.parent.mkdir(parents=True, exist_ok=True)
            cairosvg.svg2png(
                url=str(svg_path),
                write_to=str(png_path),
                output_width=size,
                output_height=size,
            )
            with Image.open(png_path) as rendered:
                rendered.load()
                if rendered.size != (size, size) or rendered.mode != "RGBA":
                    raise SystemExit(f"{name} {size}px: expected RGBA {size}x{size}, got {rendered.mode} {rendered.size}")
                if rendered.getchannel("A").getbbox() is None:
                    raise SystemExit(f"{name} {size}px: fully transparent render")
            records.append({
                "name": name,
                "format": "PNG",
                "size": size,
                "file": png_path.relative_to(output).as_posix(),
                "width": size,
                "height": size,
                "mode": "RGBA",
                "bytes": png_path.stat().st_size,
                "sha256": sha256(png_path),
            })

    # One QA sheet with all 41 icons at 48px, names are labels only in this review image.
    columns, cell_w, cell_h = 7, 88, 88
    rows = (len(EXPECTED) + columns - 1) // columns
    contact = Image.new("RGBA", (columns * cell_w, rows * cell_h), (5, 10, 18, 255))
    draw = ImageDraw.Draw(contact)
    for index, name in enumerate(EXPECTED):
        x, y = (index % columns) * cell_w, (index // columns) * cell_h
        png_path = output / "png" / "48" / f"{name.lower()}.png"
        with Image.open(png_path) as rendered:
            icon = rendered.convert("RGBA")
            contact.alpha_composite(icon, (x + 20, y + 3))
        draw.text((x + 5, y + 56), name, fill=(183, 221, 239, 255))
    contact_path = output / "previews" / "PPGU_41_ICONS_48PX_CONTACT_SHEET.png"
    contact_path.parent.mkdir(parents=True, exist_ok=True)
    contact.save(contact_path, format="PNG", optimize=True)

    manifest = {
        "schema": "ppgu.neon-stage.icons/1",
        "product": "POP PUNK GUITAR ULTIMATE REV.20",
        "skin": "skin-053",
        "theme": "NEON STAGE DEFAULT",
        "source": "ASSETS/PPGU_REV20_NEON_STAGE_ASSETS/05_ppgu_atlas_icons_hardware.svg",
        "icon_count": len(EXPECTED),
        "sizes_px": list(SIZES),
        "standalone_svg_count": len(EXPECTED),
        "standalone_png_count": len(EXPECTED) * len(SIZES),
        "contact_sheet": {
            "file": contact_path.relative_to(output).as_posix(),
            "width": contact.width,
            "height": contact.height,
            "bytes": contact_path.stat().st_size,
            "sha256": sha256(contact_path),
        },
        "records": records,
    }
    manifest_path = output / "PPGU_41_ICONS_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(EXPECTED)} standalone SVG icons and {len(EXPECTED) * len(SIZES)} RGBA PNGs exported.")
    print(f"CONTACT: {contact_path}")
    print(f"MANIFEST: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
