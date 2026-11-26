#!/usr/bin/env python3
"""Render supplemental NEON STAGE SVG masters to transparent PNG review assets.

Requires CairoSVG and Pillow. Exports are build artifacts; source SVGs remain canonical.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ASSETS" / "PPGU_REV20_NEON_STAGE_ASSETS"
SHEETS = [
    ("01_ppgu_atlas_backgrounds_frames.svg", (1920, 1000)),
    ("02_ppgu_atlas_buttons_switches.svg", (1920, 1020)),
    ("03_ppgu_atlas_knob_strips.svg", (1920, 8000)),
    ("04_ppgu_atlas_displays_keyboard.svg", (1920, 1040)),
    ("05_ppgu_atlas_icons_hardware.svg", (1920, 1020)),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "build" / "neon_stage_vector_atlases")
    parser.add_argument("--scale", type=float, default=1.0,
                        help="PNG render scale; 1.0 preserves SVG pixel dimensions.")
    args = parser.parse_args()
    if args.scale <= 0 or args.scale > 4:
        parser.error("--scale must be greater than 0 and no more than 4")

    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    previews = []
    for filename, expected in SHEETS:
        source = SOURCE / filename
        if not source.is_file():
            raise SystemExit(f"Missing source atlas: {source}")
        target = args.output / (source.stem + ".png")
        cairosvg.svg2png(
            url=str(source),
            write_to=str(target),
            output_width=round(expected[0] * args.scale),
            output_height=round(expected[1] * args.scale),
        )
        with Image.open(target) as image:
            image.load()
            if image.mode != "RGBA":
                raise SystemExit(f"{target.name}: expected RGBA, got {image.mode}")
            alpha_min, alpha_max = image.getchannel("A").getextrema()
            if alpha_min != 0:
                raise SystemExit(f"{target.name}: transparent atlas canvas was lost (alpha min={alpha_min})")
            width, height = image.size
            # Build a legible overview tile; never alter the full-resolution PNG.
            thumb_width = 760
            thumb_height = max(1, round(height * thumb_width / width))
            thumb = image.copy()
            thumb.thumbnail((thumb_width, 3400), Image.Resampling.LANCZOS)
            preview = Image.new("RGBA", (thumb_width, thumb.height + 48), (5, 10, 18, 255))
            preview.alpha_composite(thumb, (0, 48))
            draw = ImageDraw.Draw(preview)
            draw.text((12, 14), f"{filename}  |  {width} x {height}  |  alpha min/max {alpha_min}/{alpha_max}",
                      fill=(220, 248, 255, 255))
            previews.append(preview.convert("RGB"))
            records.append({
                "source": filename,
                "png": target.name,
                "width": width,
                "height": height,
                "mode": image.mode,
                "alpha_min": alpha_min,
                "alpha_max": alpha_max,
                "bytes": target.stat().st_size,
                "sha256": sha256(target),
            })

        if filename.startswith("03_"):
            # The 3×61 frame strips are stored at x=20/270/520, y=70, pitch=128.
            with Image.open(target) as image:
                for index, x in enumerate((20, 270, 520), start=1):
                    crop = image.crop((round(x * args.scale), round(70 * args.scale),
                                       round((x + 128) * args.scale),
                                       round((70 + 61 * 128) * args.scale)))
                    strip_path = args.output / f"rotary_strip_{index}_61_frames.png"
                    crop.save(strip_path, optimize=True)
                    records.append({
                        "source": filename,
                        "png": strip_path.name,
                        "width": crop.width,
                        "height": crop.height,
                        "mode": crop.mode,
                        "bytes": strip_path.stat().st_size,
                        "sha256": sha256(strip_path),
                        "frames": 61,
                        "frame_size": [round(128 * args.scale), round(128 * args.scale)],
                    })

    preview_height = sum(tile.height for tile in previews)
    contact = Image.new("RGB", (760, preview_height), (5, 10, 18))
    y = 0
    for tile in previews:
        contact.paste(tile, (0, y))
        y += tile.height
    contact_path = args.output / "NEON_STAGE_ATLAS_CONTACT_SHEET.jpg"
    contact.save(contact_path, quality=92, optimize=True)

    report = {
        "schema": "ppgu.neon-stage.svg-export-report/1",
        "scale": args.scale,
        "source_format": "SVG",
        "raster_format": "PNG RGBA",
        "sheets": records,
        "contact_sheet": contact_path.name,
        "visual_qa": "NOT_PERFORMED_BY_THIS_SCRIPT",
    }
    report_path = args.output / "NEON_STAGE_ATLAS_EXPORT_REPORT.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered {len(SHEETS)} atlas sheets and {len(records) - len(SHEETS)} rotary strip crops.")
    print(f"Contact sheet: {contact_path}")
    print(f"Export report: {report_path}")
    for record in records:
        print(f"{record['png']}\t{record['width']}x{record['height']}\t{record['bytes']} bytes\t{record['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
