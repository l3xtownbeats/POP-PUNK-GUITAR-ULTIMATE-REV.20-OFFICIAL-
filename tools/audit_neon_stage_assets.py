#!/usr/bin/env python3
"""Read-only NEON STAGE asset audit.

Checks allowed artwork formats, PNG integrity/dimensions, decoded-memory estimates,
SHA-256 entries, sprite-sheet dimensions, and forbidden purple/magenta palette tokens.
Does not rewrite or recompress approved artwork.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:
    raise SystemExit("Pillow is required: python -m pip install Pillow") from exc

ROOT = Path(__file__).resolve().parents[1]
SKIN = ROOT / "SKIN" / "Skin_053"
ALLOWED = {".png", ".jpg", ".jpeg", ".gbl"}
FORBIDDEN_TOKENS = re.compile(r"#ff007f|magenta|purple|violet", re.IGNORECASE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit() -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    images: list[dict] = []
    total_decoded = 0
    files = sorted(p for p in SKIN.rglob("*") if p.is_file())

    for path in files:
        suffix = path.suffix.lower()
        rel = path.relative_to(ROOT).as_posix()
        if suffix == ".svg":
            errors.append(f"Disallowed SVG resource: {rel}")
            continue
        if suffix not in ALLOWED:
            continue
        if suffix == ".gbl":
            images.append({"path": rel, "format": "GBL", "bytes": path.stat().st_size,
                           "decoded_bytes": None})
            continue
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
                mode = image.mode
                decoded = width * height * (4 if "A" in mode else 3)
                total_decoded += decoded
                images.append({
                    "path": rel, "format": image.format, "dimensions": [width, height],
                    "mode": mode, "alpha": "A" in mode,
                    "bytes": path.stat().st_size, "decoded_bytes_estimate": decoded,
                    "sha256": sha256(path),
                })
        except Exception as exc:  # Pillow raises several format-specific exceptions.
            errors.append(f"Unreadable image {rel}: {exc}")

    manifest_path = SKIN / "assets" / "asset_manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            records = {r.get("path"): r for r in manifest.get("records", [])}
            for item in images:
                if item["format"] == "GBL":
                    continue
                asset_rel = item["path"].split("SKIN/Skin_053/", 1)[-1]
                record = records.get(asset_rel)
                if record is None:
                    warnings.append(f"No asset_manifest record: {asset_rel}")
                    continue
                if record.get("sha256") and record["sha256"].lower() != item["sha256"]:
                    errors.append(f"SHA-256 mismatch: {asset_rel}")
                if record.get("bytes") is not None and int(record["bytes"]) != item["bytes"]:
                    errors.append(f"Byte-size mismatch: {asset_rel}")
                expected = record.get("dimensions")
                if expected and "dimensions" in item:
                    actual = f'{item["dimensions"][0]}x{item["dimensions"][1]}'
                    if expected != actual:
                        errors.append(f"Dimension mismatch {asset_rel}: {actual} != {expected}")
        except Exception as exc:
            errors.append(f"Cannot parse asset_manifest.json: {exc}")
    else:
        warnings.append("assets/asset_manifest.json is missing")

    sprite_manifest_path = SKIN / "assets" / "spritesheets" / "neon_stage_spritesheet_manifest.json"
    if sprite_manifest_path.exists():
        try:
            sprite_manifest = json.loads(sprite_manifest_path.read_text(encoding="utf-8"))
            for name, spec in sprite_manifest.get("sheets", {}).items():
                path = SKIN / "assets" / "spritesheets" / name
                if not path.is_file():
                    errors.append(f"Missing sprite sheet: {path.relative_to(ROOT)}")
                    continue
                with Image.open(path) as image:
                    if list(image.size) != spec.get("resolution"):
                        errors.append(f"Sprite sheet dimensions mismatch: {name}")
        except Exception as exc:
            errors.append(f"Cannot validate sprite-sheet manifest: {exc}")

    text_candidates = [
        SKIN / "theme.json",
        SKIN / "assets" / "spritesheets" / "neon_stage_spritesheet_manifest.json",
        ROOT / "tools" / "generate_neon_stage_spritesheets.py",
    ]
    for path in text_candidates:
        if path.exists():
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if FORBIDDEN_TOKENS.search(line):
                    errors.append(
                        f"Forbidden palette token in {path.relative_to(ROOT)}:{line_no}: {line.strip()}"
                    )

    return {
        "skin": "skin-053",
        "name": "NEON STAGE DEFAULT",
        "files_scanned": len(files),
        "image_files": len(images),
        "estimated_decoded_image_bytes": total_decoded,
        "estimated_decoded_image_mib": round(total_decoded / (1024 * 1024), 2),
        "images": images,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, help="Write JSON report to this path")
    parser.add_argument("--report-only", action="store_true",
                        help="Return success even when the audit finds blockers")
    args = parser.parse_args()
    result = audit()
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    return 0 if args.report_only or not result["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
