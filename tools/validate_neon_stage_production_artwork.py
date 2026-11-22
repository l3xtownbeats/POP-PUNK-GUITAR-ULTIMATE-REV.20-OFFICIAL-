#!/usr/bin/env python3
"""Strict audit for the authored NEON STAGE production PNG library.

This intentionally rejects legacy SVG-derived PNGs and screenshot composites.
It does not generate or approve artwork; it verifies a separately authored
production_artwork_manifest.json before runtime integration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit("Pillow is required: python -m pip install Pillow") from exc

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "SKIN/Skin_053/assets/production_artwork_manifest.json"
REQUIRED_GROUPS = {
    "main.header", "main.presets", "main.playing_core", "main.amp_tone",
    "main.performance_strip", "main.fx_chain", "main.midi_keyboard",
    "main.footer", "window.fx_edit", "window.autochords",
    "window.pattern_routing", "window.melody", "window.import_guitar",
    "window.skin_gallery",
}
REQUIRED_CONTROL_STATES = {
    "normal", "hover", "pressed", "active", "disabled", "focus"
}
REQUIRED_SCALES = {"1x", "2x", "3x"}


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    errors: list[str] = []

    try:
        manifest_path.relative_to(ROOT)
    except ValueError:
        print("FAIL: manifest must be inside the repository")
        return 2
    if not manifest_path.is_file():
        print(f"FAIL: production manifest not found: {manifest_path.relative_to(ROOT)}")
        print("No production artwork is inferred from legacy migration files.")
        return 2

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot parse manifest: {exc}")
        return 2

    if manifest.get("schemaVersion") != "1.0.0":
        fail("schemaVersion must be 1.0.0", errors)
    records = manifest.get("assets")
    if not isinstance(records, list) or not records:
        fail("assets must be a non-empty array", errors)
        records = []

    seen: set[tuple[str, str, str]] = set()
    groups: set[str] = set()
    controls: dict[str, set[str]] = {}
    checked = 0

    for index, record in enumerate(records):
        label = f"assets[{index}]"
        if not isinstance(record, dict):
            fail(f"{label}: record must be an object", errors)
            continue
        semantic_id = record.get("semanticId")
        group = record.get("group")
        state = record.get("state", "static")
        scale = record.get("scale")
        relative = record.get("path")
        expected_hash = record.get("sha256")
        dimensions = record.get("dimensions")
        if not all(isinstance(value, str) and value for value in
                   (semantic_id, group, state, scale, relative, expected_hash)):
            fail(f"{label}: missing semanticId/group/state/scale/path/sha256", errors)
            continue
        key = (semantic_id, state, scale)
        if key in seen:
            fail(f"{label}: duplicate semanticId/state/scale {key}", errors)
        seen.add(key)
        groups.add(group)
        if group.startswith("control."):
            controls.setdefault(semantic_id, set()).add(state)
        if scale not in REQUIRED_SCALES and scale != "master":
            fail(f"{label}: unsupported scale {scale!r}", errors)
        if not relative.lower().endswith(".png"):
            fail(f"{label}: production artwork must be PNG: {relative}", errors)
        lowered = relative.lower().replace("\\", "/")
        if "/svg/" in lowered or "png_migration" in lowered or "artwork_batch_" in lowered:
            fail(f"{label}: legacy/intermediate asset cannot be production: {relative}", errors)
        candidate = (ROOT / relative).resolve()
        try:
            candidate.relative_to(ROOT)
        except ValueError:
            fail(f"{label}: path escapes repository: {relative}", errors)
            continue
        if not candidate.is_file():
            fail(f"{label}: missing file: {relative}", errors)
            continue
        if sha256(candidate) != expected_hash:
            fail(f"{label}: SHA-256 mismatch: {relative}", errors)
            continue
        try:
            with Image.open(candidate) as image:
                image.load()
                if image.format != "PNG":
                    fail(f"{label}: decoder did not identify PNG: {relative}", errors)
                if image.mode != "RGBA":
                    fail(f"{label}: expected RGBA, got {image.mode}: {relative}", errors)
                if not isinstance(dimensions, list) or len(dimensions) != 2:
                    fail(f"{label}: dimensions must be [width, height]", errors)
                elif list(image.size) != dimensions:
                    fail(f"{label}: dimensions mismatch; manifest={dimensions}, file={list(image.size)}", errors)
        except Exception as exc:
            fail(f"{label}: PNG decode failed: {relative}: {exc}", errors)
            continue
        checked += 1

    missing_groups = sorted(REQUIRED_GROUPS - groups)
    if missing_groups:
        fail("missing required groups: " + ", ".join(missing_groups), errors)

    if len(controls) != 27:
        fail(f"expected exactly 27 control semantic IDs, found {len(controls)}", errors)
    for semantic_id, states in sorted(controls.items()):
        missing = sorted(REQUIRED_CONTROL_STATES - states)
        if missing:
            fail(f"{semantic_id}: missing states: {', '.join(missing)}", errors)

    if errors:
        print(f"NEON STAGE PRODUCTION ARTWORK: FAIL ({len(errors)} issue(s), {checked} file(s) decoded)")
        for error in errors:
            print("ERROR:", error)
        return 1

    print(f"NEON STAGE PRODUCTION ARTWORK: PASS ({checked} RGBA PNG assets)")
    print("Required main/auxiliary groups present; 27 controls have six distinct states.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
