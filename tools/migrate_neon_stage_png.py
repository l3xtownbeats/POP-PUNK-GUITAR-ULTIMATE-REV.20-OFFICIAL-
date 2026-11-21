#!/usr/bin/env python3
"""Convert NEON STAGE artwork batches 01-08 from SVG sources to audited RGBA PNG.

SVG files remain source material during the migration. Runtime integration is a
separate step; this tool creates deterministic PNG derivatives and a SHA-256
manifest without modifying existing UI bindings.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "SKIN" / "Skin_053" / "assets"
BATCHES = [ASSETS / f"artwork_batch_{i:02d}" for i in range(1, 9)]
OUTPUT = ASSETS / "png_migration"
FORBIDDEN = re.compile(r"#(?:[89a-fA-F][0-9a-fA-F]{0,4})?(?:[89a-fA-F][0-9a-fA-F]){0,2}", re.I)
FORBIDDEN_COLORS = {"#ff00ff", "#ff00cc", "#d000ff", "#a000ff", "#8000ff", "#c000c0", "#ff00aa"}

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def dimensions(root: ET.Element) -> tuple[int, int]:
    def number(value: str | None) -> int | None:
        if not value:
            return None
        match = re.match(r"^\s*(\d+(?:\.\d+)?)", value)
        return round(float(match.group(1))) if match else None
    width, height = number(root.get("width")), number(root.get("height"))
    if not width or not height:
        view = (root.get("viewBox") or "").replace(",", " ").split()
        if len(view) == 4:
            width = width or round(float(view[2]))
            height = height or round(float(view[3]))
    if not width or not height:
        raise ValueError("SVG has no usable width/height or viewBox")
    return width, height

def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records, errors, source_count = [], [], 0
    for batch in BATCHES:
        if not batch.is_dir():
            errors.append(f"Missing batch directory: {batch.relative_to(ROOT)}")
            continue
        for source in sorted(batch.rglob("*.svg")):
            source_count += 1
            try:
                svg = source.read_bytes()
                root = ET.fromstring(svg)
                if not root.tag.endswith("svg"):
                    raise ValueError("Root XML element is not <svg>")
                width, height = dimensions(root)
                out = OUTPUT / batch.name / (source.stem + ".png")
                out.parent.mkdir(parents=True, exist_ok=True)
                png = cairosvg.svg2png(bytestring=svg, output_width=width, output_height=height)
                out.write_bytes(png)
                with Image.open(out) as image:
                    image.load()
                    if image.format != "PNG":
                        raise ValueError("Renderer did not produce PNG")
                    if image.mode not in ("RGBA", "LA"):
                        image = image.convert("RGBA")
                        image.save(out)
                    with Image.open(out) as checked:
                        checked.load()
                        if checked.size != (width, height):
                            raise ValueError(f"PNG size {checked.size} != expected {(width, height)}")
                        if checked.mode != "RGBA":
                            raise ValueError(f"PNG mode is {checked.mode}, expected RGBA")
                        alpha_min, alpha_max = checked.getchannel("A").getextrema()
                colors = sorted({c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}", svg)})
                forbidden = sorted(set(colors) & FORBIDDEN_COLORS)
                if forbidden:
                    errors.append(f"{source.relative_to(ROOT)} uses forbidden accent colors: {forbidden}")
                payload = out.read_bytes()
                records.append({
                    "source": source.relative_to(ROOT).as_posix(),
                    "png": out.relative_to(ROOT).as_posix(),
                    "width": width,
                    "height": height,
                    "format": "PNG",
                    "mode": "RGBA",
                    "alphaExtrema": [alpha_min, alpha_max],
                    "sourceSha256": sha256(svg),
                    "pngSha256": sha256(payload),
                    "paletteHex": colors,
                })
            except Exception as exc:
                errors.append(f"{source.relative_to(ROOT)}: {exc}")
    manifest = {
        "schemaVersion": "1.0.0",
        "skinId": "skin-053",
        "theme": "NEON STAGE DEFAULT",
        "conversion": "SVG source -> PNG RGBA derivative",
        "sourceCount": source_count,
        "convertedCount": len(records),
        "records": records,
    }
    manifest_path = OUTPUT / "png_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"SVG sources discovered: {source_count}")
    print(f"PNG files converted and audited: {len(records)}")
    print(f"Manifest: {manifest_path.relative_to(ROOT)}")
    if errors:
        print("PNG MIGRATION AUDIT: FAIL")
        for error in errors:
            print("ERROR:", error)
        return 1
    if source_count == 0:
        print("PNG MIGRATION AUDIT: FAIL (no SVG sources found)")
        return 1
    print("PNG MIGRATION AUDIT: PASS (RGBA, dimensions, alpha metadata, SHA-256)")
    print("NOTE: generated PNGs are not yet connected to JUCE runtime controls.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
