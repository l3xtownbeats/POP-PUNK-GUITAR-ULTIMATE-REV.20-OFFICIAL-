#!/usr/bin/env python3
"""Export the 16 canonical NEON STAGE standalone SVG panel frames as RGBA PNGs.

The SVGs remain the source of truth. This exporter does not compose a guessed
main-window preview and does not bake dynamic JUCE labels or controls.
Requires CairoSVG==2.7.1 and Pillow==10.4.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PANEL_ROOT = ROOT / "ASSETS" / "PPGU_REV20_NEON_STAGE_ASSETS" / "panels"
EXPECTED_PANEL_COUNT = 16


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "build" / "neon_stage_panel_frames")
    parser.add_argument("--scale", type=float, default=1.0)
    args = parser.parse_args()
    if not 0 < args.scale <= 4:
        parser.error("--scale must be greater than 0 and no more than 4")

    sources = sorted(PANEL_ROOT.rglob("*.svg"))
    if len(sources) != EXPECTED_PANEL_COUNT:
        raise SystemExit(
            f"Expected exactly {EXPECTED_PANEL_COUNT} standalone panel SVGs, found {len(sources)}"
        )

    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    tiles = []
    for source in sources:
        relative = source.relative_to(PANEL_ROOT)
        target = args.output / relative.with_suffix(".png")
        target.parent.mkdir(parents=True, exist_ok=True)
        cairosvg.svg2png(url=str(source), write_to=str(target), scale=args.scale)

        with Image.open(target) as image:
            image.load()
            if image.mode != "RGBA":
                raise SystemExit(f"{relative}: expected RGBA, got {image.mode}")
            alpha_min, alpha_max = image.getchannel("A").getextrema()
            if alpha_min != 0:
                raise SystemExit(f"{relative}: canvas is not transparent (alpha min={alpha_min})")
            width, height = image.size
            records.append({
                "source": relative.as_posix(),
                "png": target.relative_to(args.output).as_posix(),
                "width": width,
                "height": height,
                "mode": image.mode,
                "alpha_min": alpha_min,
                "alpha_max": alpha_max,
                "bytes": target.stat().st_size,
                "sha256": sha256(target),
            })

            thumb = image.copy()
            thumb.thumbnail((420, 260), Image.Resampling.LANCZOS)
            tile = Image.new("RGBA", (440, 300), (5, 10, 18, 255))
            tile.alpha_composite(thumb, ((440 - thumb.width) // 2, 30))
            draw = ImageDraw.Draw(tile)
            draw.text((10, 8), relative.as_posix(), fill=(220, 248, 255, 255))
            tiles.append(tile.convert("RGB"))

    columns = 4
    rows = (len(tiles) + columns - 1) // columns
    contact = Image.new("RGB", (columns * 440, rows * 300), (5, 10, 18))
    for index, tile in enumerate(tiles):
        contact.paste(tile, ((index % columns) * 440, (index // columns) * 300))
    contact_path = args.output / "NEON_STAGE_PANEL_FRAMES_CONTACT_SHEET.jpg"
    contact.save(contact_path, quality=92, optimize=True)

    report = {
        "schema": "ppgu.neon-stage.panel-frame-export/1",
        "scale": args.scale,
        "source": "standalone SVG panel frames",
        "format": "PNG RGBA",
        "count": len(records),
        "records": records,
        "contact_sheet": contact_path.name,
        "visual_acceptance": "NOT_PERFORMED",
        "main_window_preview": "NOT_GENERATED_CANONICAL_REFERENCE_REQUIRED",
    }
    report_path = args.output / "NEON_STAGE_PANEL_FRAME_EXPORT_REPORT.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: exported {len(records)} standalone panel frames at {args.scale:g}x")
    print(f"Contact sheet: {contact_path}")
    print(f"Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
