#!/usr/bin/env python3
"""Build side-by-side master/runtime contact sheets for Skin_053 artwork review."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TILE_W, TILE_H = 470, 205
COLS, ROWS = 3, 4
THUMB_W, THUMB_H = 184, 142
BG = (12, 14, 19)
PANEL = (28, 31, 39)
TEXT = (238, 235, 242)
MUTED = (174, 170, 182)
ACCENT = (230, 0, 126)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def fit_rgba(path: Path) -> Image.Image:
    with Image.open(path) as source:
        image = source.convert("RGBA")
    image.thumbnail((THUMB_W, THUMB_H), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (THUMB_W, THUMB_H), (8, 9, 13, 255))
    canvas.alpha_composite(image, ((THUMB_W-image.width)//2, (THUMB_H-image.height)//2))
    return canvas.convert("RGB")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("SKIN/Skin_053"))
    parser.add_argument("--output", type=Path, default=Path("build/neon_stage_visual_audit"))
    args = parser.parse_args()
    root, output = args.root, args.output
    manifest_path = root / "assets/controls/control_states_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = manifest.get("records", [])
    if len(records) != 135:
        raise SystemExit(f"Expected 135 control-state records, found {len(records)}")
    output.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    audit = []
    for record in records:
        master = root / record["master"]
        runtime = root / record["runtime"]
        if not master.is_file() or not runtime.is_file():
            raise SystemExit(f"Missing artwork pair: {master} / {runtime}")
        audit.append({
            "controlId": record["controlId"], "state": record["state"],
            "master": str(master), "runtime": str(runtime),
            "masterSize": list(Image.open(master).size),
            "runtimeSize": list(Image.open(runtime).size),
            "masterSha256": sha256(master), "runtimeSha256": sha256(runtime),
        })
    per_page = COLS * ROWS
    for page_index in range((len(audit) + per_page - 1) // per_page):
        page_records = audit[page_index*per_page:(page_index+1)*per_page]
        sheet = Image.new("RGB", (COLS*TILE_W, ROWS*TILE_H), BG)
        draw = ImageDraw.Draw(sheet)
        for local_index, item in enumerate(page_records):
            x = (local_index % COLS) * TILE_W
            y = (local_index // COLS) * TILE_H
            draw.rounded_rectangle((x+5, y+5, x+TILE_W-5, y+TILE_H-5), radius=8, fill=PANEL)
            title = f'{item["controlId"]} / {item["state"]}'
            draw.text((x+14, y+12), title, fill=TEXT, font=font)
            for offset, label, key in [(14, "MASTER", "master"), (244, "RUNTIME", "runtime")]:
                draw.text((x+offset, y+31), label, fill=ACCENT if label=="RUNTIME" else MUTED, font=font)
                image = fit_rgba(Path(item[key]))
                sheet.paste(image, (x+offset, y+48))
                size = item["masterSize"] if key=="master" else item["runtimeSize"]
                draw.text((x+offset, y+192), f'{size[0]} x {size[1]}', fill=MUTED, font=font)
        sheet.save(output / f"skin053-master-runtime-{page_index+1:02d}.jpg", quality=92, optimize=True)
    (output / "audit.json").write_text(json.dumps({
        "skinId": "skin-053", "recordCount": len(audit),
        "pages": (len(audit)+per_page-1)//per_page, "records": audit,
        "note": "Side-by-side visual review aid only; image presence and checksums are not a visual approval."
    }, indent=2), encoding="utf-8")
    print(f"Created {(len(audit)+per_page-1)//per_page} contact sheets for {len(audit)} master/runtime pairs.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
