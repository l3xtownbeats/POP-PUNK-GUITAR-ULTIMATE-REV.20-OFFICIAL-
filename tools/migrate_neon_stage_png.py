#!/usr/bin/env python3
"""Create audited 1x/2x/3x RGBA PNG derivatives for NEON STAGE SVG batches."""
from __future__ import annotations
import hashlib, json, re, sys, colorsys, subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
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
        match = re.match(r"^\s*(\d+(?:\.\d+)?)", value)
        return round(float(match.group(1))) if match else None
    width, height = number(root.get("width")), number(root.get("height"))
    if not width or not height:
        view = (root.get("viewBox") or "").replace(",", " ").split()
        if len(view) == 4:
            width = width or round(float(view[2])); height = height or round(float(view[3]))
    if not width or not height: raise ValueError("SVG has no usable width/height or viewBox")
    return width, height

def purple_pixel_diagnostics(image: Image.Image, limit: int = 12) -> tuple[int, list[str]]:
    """Return a count plus reproducible pixel coordinates for palette-audit failures."""
    rgba = image.convert("RGBA")
    width, height = rgba.size
    count = 0
    samples: list[str] = []
    for index, (r, g, b, a) in enumerate(rgba.getdata()):
        if a < 16:
            continue
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        # Reject saturated violet/purple/magenta accents, not neutral metal or blue/cyan.
        if s >= 0.38 and v >= 0.18 and 0.76 <= h <= 0.94:
            count += 1
            if len(samples) < limit:
                x, y = index % width, index // width
                samples.append(
                    f"(x={x},y={y},rgba={r},{g},{b},{a},hsv={h:.3f},{s:.3f},{v:.3f})"
                )
    return count, samples


def purple_pixels(image: Image.Image) -> int:
    return purple_pixel_diagnostics(image)[0]


def render_png(source: Path, output: Path, width: int, height: int) -> None:
    """Render with resvg so SVG text/gradients are rasterized consistently."""
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["node", str(ROOT / "tools" / "render_neon_stage_svg.cjs"),
         str(source), str(output), str(width), str(height)],
        check=True,
    )

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
                    render_png(source, out, width*scale, height*scale)
                    with Image.open(out) as im:
                        im.load()
                        rgba = im.convert("RGBA")
                        if rgba.size != (width*scale, height*scale):
                            raise ValueError(f"{scale}x dimensions mismatch: {rgba.size}")
                        alpha_min, alpha_max = rgba.getchannel("A").getextrema()
                        bad, samples = purple_pixel_diagnostics(rgba)
                        if bad:
                            raise ValueError(
                                f"{bad} visible purple/violet/magenta pixels detected at {scale}x; "
                                f"first pixel samples: {'; '.join(samples)}"
                            )
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
    # Convert canonical Skin-1 runtime layers to the exact dimensions consumed by ThemeManager.
    core_artwork = [
        ("texture", ROOT / "SKIN" / "Skin_053" / "svg" / "texture.svg", 512, 512),
        ("bezel", ROOT / "SKIN" / "Skin_053" / "svg" / "bezel.svg", 800, 450),
        ("crest", ROOT / "SKIN" / "Skin_053" / "svg" / "crest.svg", 480, 168),
    ]
    core_records = []
    for name, source, width, height in core_artwork:
        try:
            svg = source.read_bytes()
            root = ET.fromstring(svg)
            if not root.tag.endswith("svg"):
                raise ValueError("Root XML element is not <svg>")
            out = OUTPUT / "runtime_artwork" / f"{name}.png"
            out.parent.mkdir(parents=True, exist_ok=True)
            render_png(source, out, width, height)
            with Image.open(out) as im:
                im.load()
                rgba = im.convert("RGBA")
                if rgba.size != (width, height):
                    raise ValueError(f"runtime dimensions mismatch: {rgba.size}")
                alpha_min, alpha_max = rgba.getchannel("A").getextrema()
                bad, samples = purple_pixel_diagnostics(rgba)
                if bad:
                    raise ValueError(
                        f"{bad} visible purple/violet/magenta pixels detected; "
                        f"first pixel samples: {'; '.join(samples)}"
                    )
                rgba.save(out, format="PNG", optimize=True)
            payload = out.read_bytes()
            core_records.append({
                "name": name, "source": source.relative_to(ROOT).as_posix(),
                "sourceSha256": sha256(svg), "png": out.relative_to(ROOT).as_posix(),
                "width": width, "height": height, "format": "PNG", "mode": "RGBA",
                "alphaExtrema": [alpha_min, alpha_max], "pngSha256": sha256(payload)
            })
        except Exception as exc:
            errors.append(f"{source.relative_to(ROOT)}: {exc}")
    manifest = {"schemaVersion":"1.1.0","skinId":"skin-053","theme":"NEON STAGE DEFAULT",
                "conversion":"SVG -> PNG RGBA; 1x/2x/3x","sourceCount":source_count,
                "convertedSourceCount":len(records),"variantCount":sum(len(x["variants"]) for x in records),
                "records":records,"runtimeArtwork":core_records}
    path = OUTPUT / "png_manifest.json"
    path.write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(f"SVG sources: {source_count}; converted sources: {len(records)}; PNG variants: {manifest['variantCount']}")
    print(f"Manifest: {path.relative_to(ROOT)}")
    print(f"Runtime artwork layers: {len(core_records)}/3")
    if errors:
        print("PNG MIGRATION AUDIT: FAIL")
        for error in errors: print("ERROR:", error)
        return 1
    if source_count == 0: print("PNG MIGRATION AUDIT: FAIL (no SVG sources)"); return 1
    if len(core_records) != 3: print("PNG MIGRATION AUDIT: FAIL (runtime artwork incomplete)"); return 1
    print("PNG MIGRATION AUDIT: PASS (batch HiDPI + 3 runtime layers; RGBA, dimensions, alpha, palette scan, SHA-256)")
    print("Runtime texture/bezel/crest paths are PNG-backed; batch control artwork still requires individual JUCE component bindings.")
    return 0

if __name__ == "__main__": sys.exit(main())
