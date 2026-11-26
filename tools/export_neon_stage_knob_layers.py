#!/usr/bin/env python3
"""Export independent six-layer rotary artwork for the nine REV.20 main controls."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = (
    "GAIN", "TREBLE", "MID", "BASS", "VELOCITY",
    "DYNAMICS", "SWING", "HUMANIZE", "ACCENT",
)
LAYERS = ("BASE", "RIM", "FACE", "POINTER", "SCALE", "GLOW")
SIZES = (192, 384)
SVG_NS = "http://www.w3.org/2000/svg"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def pt(radius: float, angle: float, cx: float = 96, cy: float = 96) -> tuple[float, float]:
    radians = math.radians(angle)
    return cx + radius * math.cos(radians), cy + radius * math.sin(radians)


def f(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def common_defs() -> str:
    return """
<defs>
  <linearGradient id="baseBody" x1="0" y1="0" x2="0" y2="1">
    <stop stop-color="#3B5168"/><stop offset=".12" stop-color="#17283B"/>
    <stop offset=".55" stop-color="#050C16"/><stop offset=".88" stop-color="#14243A"/>
    <stop offset="1" stop-color="#526B82"/>
  </linearGradient>
  <radialGradient id="metalRim" cx="31%" cy="22%" r="82%">
    <stop stop-color="#F4F8FC"/><stop offset=".12" stop-color="#AEBFCE"/>
    <stop offset=".28" stop-color="#657A8E"/><stop offset=".47" stop-color="#D7E0E8"/>
    <stop offset=".66" stop-color="#485D72"/><stop offset=".86" stop-color="#9AACBA"/>
    <stop offset="1" stop-color="#24384C"/>
  </radialGradient>
  <radialGradient id="faceMetal" cx="32%" cy="23%" r="88%">
    <stop stop-color="#849AAF"/><stop offset=".18" stop-color="#41566C"/>
    <stop offset=".42" stop-color="#1B2C40"/><stop offset=".72" stop-color="#0A1422"/>
    <stop offset="1" stop-color="#293D53"/>
  </radialGradient>
  <linearGradient id="needleMetal" x1="0" y1="0" x2="1" y2="0">
    <stop stop-color="#526A80"/><stop offset=".38" stop-color="#F4FAFF"/>
    <stop offset=".62" stop-color="#9FB4C6"/><stop offset="1" stop-color="#344B61"/>
  </linearGradient>
  <linearGradient id="cyanScale" x1="0" y1="0" x2="1" y2="1">
    <stop stop-color="#DDFEFF"/><stop offset=".35" stop-color="#00D9FF"/>
    <stop offset="1" stop-color="#6B8CFF"/>
  </linearGradient>
  <pattern id="microKnurl" width="6" height="6" patternUnits="userSpaceOnUse">
    <path d="M0 0L6 6M6 0L0 6" stroke="#D9E8F4" stroke-opacity=".24" stroke-width=".8"/>
  </pattern>
  <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="3.2" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="wideGlow" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="6.5" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>"""


def layer_svg(layer: str) -> str:
    if layer == "BASE":
        body = """
<ellipse cx="96" cy="101" rx="88" ry="88" fill="#02060B" opacity=".78"/>
<circle cx="96" cy="96" r="84" fill="url(#baseBody)" stroke="#415A72" stroke-width="2.2"/>
<circle cx="96" cy="96" r="75" fill="#07111E" stroke="#182C41" stroke-width="2"/>
<circle cx="96" cy="96" r="69" fill="#0B1726" stroke="#30465B" stroke-width="1.4"/>"""
    elif layer == "RIM":
        marks = []
        for i in range(72):
            angle = i * 5.0
            r1 = 78
            r2 = 84 if i % 3 == 0 else 81
            x1, y1 = pt(r1, angle)
            x2, y2 = pt(r2, angle)
            marks.append(f'<path d="M{f(x1)} {f(y1)}L{f(x2)} {f(y2)}"/>')
        body = f"""
<circle cx="96" cy="96" r="84" fill="url(#metalRim)" stroke="#D4E1EA" stroke-width="1.2"/>
<circle cx="96" cy="96" r="80" fill="#132238" stroke="#657F95" stroke-width="1.2"/>
<circle cx="96" cy="96" r="73" fill="none" stroke="#BFCFDC" stroke-opacity=".62" stroke-width="1.6"/>
<g fill="none" stroke="#E6F3FC" stroke-opacity=".72" stroke-width="1.25" stroke-linecap="round">{''.join(marks)}</g>
<circle cx="96" cy="96" r="69" fill="none" stroke="#314B63" stroke-width="1.6"/>"""
    elif layer == "FACE":
        brush = []
        for i in range(36):
            angle = i * 10.0
            x1, y1 = pt(18, angle)
            x2, y2 = pt(60, angle)
            brush.append(f'<path d="M{f(x1)} {f(y1)}L{f(x2)} {f(y2)}"/>')
        body = f"""
<circle cx="96" cy="96" r="63" fill="url(#faceMetal)" stroke="#91A8BB" stroke-width="1.4"/>
<circle cx="96" cy="96" r="58" fill="none" stroke="#E5F3FC" stroke-opacity=".14" stroke-width="1"/>
<g fill="none" stroke="#E7F3FB" stroke-opacity=".075" stroke-width=".7">{''.join(brush)}</g>
<ellipse cx="79" cy="68" rx="31" ry="13" transform="rotate(-30 79 68)" fill="#FFFFFF" opacity=".12"/>
<circle cx="96" cy="96" r="49" fill="none" stroke="#020812" stroke-opacity=".55" stroke-width="1.4"/>"""
    elif layer == "POINTER":
        body = """
<path d="M96 34L101 96L96 110L91 96Z" fill="url(#needleMetal)" stroke="#EDF8FF" stroke-width="1.1"/>
<path d="M96 42V31" stroke="#00D9FF" stroke-width="3.2" stroke-linecap="round" filter="url(#softGlow)"/>
<path d="M94 49L94 89" stroke="#FFFFFF" stroke-opacity=".76" stroke-width="1"/>
<circle cx="96" cy="96" r="12" fill="url(#metalRim)" stroke="#F2FAFF" stroke-width="1"/>
<circle cx="96" cy="96" r="8" fill="#253A50" stroke="#728DA3" stroke-width="1"/>
<circle cx="93" cy="93" r="2.5" fill="#FFFFFF" opacity=".65"/>"""
    elif layer == "SCALE":
        ticks = []
        for i in range(61):
            angle = 210 + i * 3
            major = (i % 5 == 0)
            inner = 65 if major else 67.5
            outer = 72
            x1, y1 = pt(inner, angle - 90)
            x2, y2 = pt(outer, angle - 90)
            color = "#B7CBD9" if major else "#7990A5"
            opacity = ".92" if major else ".64"
            width = 1.5 if major else .85
            ticks.append(
                f'<path d="M{f(x1)} {f(y1)}L{f(x2)} {f(y2)}" '
                f'stroke="{color}" stroke-opacity="{opacity}" stroke-width="{width}"/>'
            )
        body = f"""
<circle cx="96" cy="96" r="68" fill="none" stroke="#8AA1B5" stroke-opacity=".28" stroke-width="1"/>
<g fill="none" stroke-linecap="round">{''.join(ticks)}</g>
<path d="M{f(pt(72,120)[0])} {f(pt(72,120)[1])}A72 72 0 0 1 {f(pt(72,300)[0])} {f(pt(72,300)[1])}"
      fill="none" stroke="url(#cyanScale)" stroke-width="2.1" stroke-opacity=".86"/>"""
    elif layer == "GLOW":
        x1, y1 = pt(86, 120)
        x2, y2 = pt(86, 300)
        body = f"""
<circle cx="96" cy="96" r="87" fill="none" stroke="#6B8CFF" stroke-width="4.5" stroke-opacity=".26" filter="url(#wideGlow)"/>
<path d="M{f(x1)} {f(y1)}A86 86 0 0 1 {f(x2)} {f(y2)}"
      fill="none" stroke="#00D9FF" stroke-width="4.5" stroke-linecap="round" stroke-opacity=".46" filter="url(#wideGlow)"/>
<circle cx="96" cy="96" r="73" fill="none" stroke="#00D9FF" stroke-width="1.6" stroke-opacity=".34" filter="url(#softGlow)"/>"""
    else:
        raise ValueError(layer)

    return (
        f'<svg xmlns="{SVG_NS}" width="192" height="192" viewBox="0 0 192 192" version="1.1">'
        f'{common_defs()}<g id="{layer.lower()}">{body}</g></svg>'
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "neon_stage_knob_layers")
    args = parser.parse_args()
    out: Path = args.output
    out.mkdir(parents=True, exist_ok=True)

    records = []
    composite_tiles = []
    for parameter in PARAMETERS:
        layer_svgs: dict[str, Path] = {}
        for layer in LAYERS:
            source = layer_svg(layer)
            svg_path = out / "svg" / parameter.lower() / f"{layer.lower()}.svg"
            svg_path.parent.mkdir(parents=True, exist_ok=True)
            svg_path.write_text(source, encoding="utf-8")
            layer_svgs[layer] = svg_path
            records.append({
                "parameter": parameter, "layer": layer, "format": "SVG",
                "file": svg_path.relative_to(out).as_posix(),
                "width": 192, "height": 192, "bytes": svg_path.stat().st_size,
                "sha256": sha256(svg_path),
            })

            for size in SIZES:
                png_path = out / "png" / str(size) / parameter.lower() / f"{layer.lower()}.png"
                png_path.parent.mkdir(parents=True, exist_ok=True)
                cairosvg.svg2png(url=str(svg_path), write_to=str(png_path),
                                 output_width=size, output_height=size)
                with Image.open(png_path) as rendered:
                    rendered.load()
                    if rendered.size != (size, size) or rendered.mode != "RGBA":
                        raise SystemExit(f"{parameter}/{layer}/{size}: expected RGBA {size}x{size}")
                    if rendered.getchannel("A").getbbox() is None:
                        raise SystemExit(f"{parameter}/{layer}/{size}: transparent output")
                records.append({
                    "parameter": parameter, "layer": layer, "format": "PNG",
                    "size": size, "file": png_path.relative_to(out).as_posix(),
                    "width": size, "height": size, "mode": "RGBA",
                    "bytes": png_path.stat().st_size, "sha256": sha256(png_path),
                })

        # Compose the six separate source layers for a visual QA tile.
        composite = Image.new("RGBA", (192, 192), (0, 0, 0, 0))
        for layer in ("BASE", "GLOW", "RIM", "FACE", "SCALE", "POINTER"):
            rendered = cairosvg.svg2png(url=str(layer_svgs[layer]))
            from io import BytesIO
            with Image.open(BytesIO(rendered)) as image:
                composite = Image.alpha_composite(composite, image.convert("RGBA"))
        composite_tiles.append((parameter, composite))

    cols, cell = 3, 224
    rows = (len(PARAMETERS) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (5, 10, 18, 255))
    draw = ImageDraw.Draw(sheet)
    for idx, (name, image) in enumerate(composite_tiles):
        x, y = (idx % cols) * cell, (idx // cols) * cell
        image.thumbnail((184, 184), Image.Resampling.LANCZOS)
        sheet.alpha_composite(image, (x + 20, y + 2))
        draw.text((x + 10, y + 190), name, fill=(190, 224, 241, 255))
    preview = out / "previews" / "PPGU_9_MAIN_KNOB_LAYERS_CONTACT_SHEET.png"
    preview.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(preview, format="PNG", optimize=True)

    expected_svg = len(PARAMETERS) * len(LAYERS)
    expected_png = expected_svg * len(SIZES)
    if sum(1 for r in records if r["format"] == "SVG") != expected_svg:
        raise SystemExit("Knob SVG count mismatch")
    if sum(1 for r in records if r["format"] == "PNG") != expected_png:
        raise SystemExit("Knob PNG count mismatch")

    manifest = {
        "schema": "ppgu.neon-stage.main-knob-layers/1",
        "product": "POP PUNK GUITAR ULTIMATE REV.20",
        "skin": "skin-053",
        "theme": "NEON STAGE DEFAULT",
        "parameters": list(PARAMETERS),
        "layers": list(LAYERS),
        "svg_count": expected_svg,
        "png_count": expected_png,
        "png_sizes_px": list(SIZES),
        "visual_acceptance": "LAYER_EXPORT_VERIFIED; RENDERED_REFERENCE_PARITY_AND_JUCE_USE_REMAIN_SEPARATE_GATES",
        "preview": {
            "file": preview.relative_to(out).as_posix(),
            "width": sheet.width, "height": sheet.height,
            "bytes": preview.stat().st_size, "sha256": sha256(preview),
        },
        "records": records,
    }
    manifest_path = out / "PPGU_9_MAIN_KNOB_LAYERS_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {expected_svg} standalone SVG layers; {expected_png} RGBA PNG layer renders.")
    print(f"PREVIEW: {preview}")
    print(f"MANIFEST: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
