#!/usr/bin/env python3
"""Create audited 1x/2x/3x RGBA PNG derivatives for NEON STAGE SVG batches."""
from __future__ import annotations
import hashlib, json, re, sys, colorsys
import xml.etree.ElementTree as ET
from pathlib import Path
import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "SKIN" / "Skin_053" / "assets"
BATCHES = [ASSETS / f"artwork_batch_{i:02d}" for i in range(1, 9)]
OUTPUT = ASSETS / "png_migration"
SCALES = (1, 2, 3)

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def dimensions(root: ET.Element) -> tuple[int, int]:
    def number(value):
        if not value: return None
        match = re.match(r"^\\s*(\\d+(?:\\.\\d+)?)", value)
        return round(float(match.group(1))) if match else None
    width, height = number(root.get("width")), number(root.get("height"))
    if not width or not height:
        view = (root.get("viewBox") or "").replace(",", " ").split()
        if len(view) == 4:
            width = width or round(float(view[2])); height = height or round(float(view[3]))
    if not width or not height: raise ValueError("SVG has no usable width/height or viewBox")
    return width, height

def purple_pixels(image: Image.Image) -> int:
    count = 0
    rgba = image.convert("RGBA")
    for r, g, b, a in rgba.getdata():
        if a < 16: continue
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        # Reject saturated violet/purple/magenta accents, not neutral metal or blue/cyan.
        if s >= 0.38 and v >= 0.18 and 0.76 <= h <= 0.94:
            count += 1
    return count

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
                if not root.tag.endswith("svg"): raise ValueError("Root XML element is not <svg>")
                width, height = dimensions(root)
                source_record = {"source": source.relative_to(ROOT).as_posix(),
                                 "sourceSha256": sha256(svg), "variants": []}
                for scale in SCALES:
                    out = OUTPUT / batch.name / f"{source.stem}{'@'+str(scale)+'x' if scale > 1 else ''}.png"
                    out.parent.mkdir(parents=True, exist_ok=True)
                    png = cairosvg.svg2png(bytestring=svg, output_width=width*scale, output_height=height*scale)
                    out.write_bytes(png)
                    with Image.open(out) as im:
                        im.load()
                        rgba = im.convert("RGBA")
                        if rgba.size != (width*scale, height*scale):
                            raise ValueError(f"{scale}x dimensions mismatch: {rgba.size}")
                        alpha_min, alpha_max = rgba.getchannel("A").getextrema()
                        bad = purple_pixels(rgba)
                        if bad:
                            raise ValueError(f"{bad} visible purple/violet/magenta pixels detected at {scale}x")
                        if rgba.mode != "RGBA": raise ValueError("RGBA conversion failed")
                        rgba.save(out, format="PNG", optimize=True)
                    payload = out.read_bytes()
                    source_record["variants"].append({
                        "scale": f"{scale}x", "png": out.relative_to(ROOT).as_posix(),
                        "width": width*scale, "height": height*scale, "format": "PNG",
                        "mode": "RGBA", "alphaExtrema": [alpha_min, alpha_max],
                        "purplePixelCount": 0, "pngSha256": sha256(payload)
                    })
                records.append(source_record)
            except Exception as exc:
                errors.append(f"{source.relative_to(ROOT)}: {exc}")
    manifest = {"schemaVersion":"1.1.0","skinId":"skin-053","theme":"NEON STAGE DEFAULT",
                "conversion":"SVG -> PNG RGBA; 1x/2x/3x","sourceCount":source_count,
                "convertedSourceCount":len(records),"variantCount":sum(len(x["variants"]) for x in records),
                "records":records}
    path = OUTPUT / "png_manifest.json"
    path.write_text(json.dumps(manifest, indent=2)+"\\n", encoding="utf-8")
    print(f"SVG sources: {source_count}; converted sources: {len(records)}; PNG variants: {manifest['variantCount']}")
    print(f"Manifest: {path.relative_to(ROOT)}")
    if errors:
        print("PNG MIGRATION AUDIT: FAIL")
        for error in errors: print("ERROR:", error)
        return 1
    if source_count == 0: print("PNG MIGRATION AUDIT: FAIL (no SVG sources)"); return 1
    print("PNG MIGRATION AUDIT: PASS (RGBA, 1x/2x/3x, dimensions, alpha, purple-pixel scan, SHA-256)")
    print("NOTE: PNGs are not yet wired into JUCE runtime controls.")
    return 0

if __name__ == "__main__": sys.exit(main())
