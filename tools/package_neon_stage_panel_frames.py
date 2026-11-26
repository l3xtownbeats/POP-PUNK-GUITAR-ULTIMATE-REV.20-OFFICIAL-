#!/usr/bin/env python3
"""Package verified 1x/2x NEON STAGE standalone panel-frame exports."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
SCALES = {
    "1x": BUILD / "neon_stage_panel_frames_1x",
    "2x": BUILD / "neon_stage_panel_frames_2x",
}
EXPECTED = 16


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    package_root = BUILD / "PPGU-NEON-STAGE-PANEL-FRAMES-1X-2X"
    package_root.mkdir(parents=True, exist_ok=True)
    records = []
    for scale, source_dir in SCALES.items():
        report_path = source_dir / "NEON_STAGE_PANEL_FRAME_EXPORT_REPORT.json"
        if not report_path.is_file():
            raise SystemExit(f"Missing export report: {report_path}")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("count") != EXPECTED or len(report.get("records", [])) != EXPECTED:
            raise SystemExit(f"{scale}: expected {EXPECTED} panel frames")
        for item in report["records"]:
            png = source_dir / item["png"]
            if not png.is_file() or digest(png) != item["sha256"]:
                raise SystemExit(f"{scale}: missing or changed PNG: {item['png']}")
            if png.stat().st_size != item["bytes"]:
                raise SystemExit(f"{scale}: byte-count mismatch: {item['png']}")
            records.append({
                "scale": scale,
                "source_svg": item["source"],
                "file": f"{scale}/{item['png']}",
                "width": item["width"],
                "height": item["height"],
                "format": "PNG",
                "mode": item["mode"],
                "alpha_min": item["alpha_min"],
                "alpha_max": item["alpha_max"],
                "bytes": item["bytes"],
                "sha256": item["sha256"],
            })

    manifest = {
        "schema": "ppgu.neon-stage.panel-frame-package/1",
        "product": "POP PUNK GUITAR ULTIMATE REV.20",
        "theme": "SKIN-1 / NEON STAGE DEFAULT / skin-053",
        "status": "PANEL_FRAME_EXPORT_VERIFIED; FULL_ASSET_PACK_NOT_COMPLETE",
        "panel_count_per_scale": EXPECTED,
        "scales": ["1x", "2x"],
        "records": records,
        "visual_acceptance": "NOT_PERFORMED",
        "main_window_composition": "NOT_GENERATED_OR_ASSERTED",
    }
    manifest_path = package_root / "PANEL_FRAME_PACKAGE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    archive = BUILD / "PPGU-NEON-STAGE-PANEL-FRAMES-1X-2X.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(manifest_path, "PANEL_FRAME_PACKAGE_MANIFEST.json")
        for scale, source_dir in SCALES.items():
            for path in sorted(source_dir.rglob("*")):
                if path.is_file():
                    zf.write(path, f"{scale}/{path.relative_to(source_dir).as_posix()}")
    print(f"PASS: packaged {len(records)} verified PNG panel frames (16 at 1x + 16 at 2x)")
    print(f"Archive: {archive}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
