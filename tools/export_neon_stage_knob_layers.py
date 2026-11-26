#!/usr/bin/env python3
"""Export independent six-layer rotary artwork for the nine REV.20 main controls."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw

from rotary_master_layers import load_rotary_master_layers

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


MASTER_LAYER_SVGS = load_rotary_master_layers(ROOT)


def layer_svg(layer: str) -> str:
    try:
        return MASTER_LAYER_SVGS[layer]
    except KeyError as exc:
        raise ValueError(f"Unknown canonical rotary layer: {layer}") from exc


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
        "source_reference": "SKIN/Skin_053/assets/vector/rotary_knob_master.svg",
        "source_layers": "Extracted from the canonical 512x512 master SVG without drawing substitute geometry.",
        "palette_reference": "SKIN/Skin_053/theme.json",
        "visual_acceptance": "SOURCE_MASTER_LAYER_EXPORT_VERIFIED; RENDERED_REFERENCE_PARITY_AND_JUCE_USE_REMAIN_SEPARATE_GATES",
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
