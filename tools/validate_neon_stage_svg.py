#!/usr/bin/env python3
"""Validate NEON STAGE vector-library structure, provenance anchors and palette contract."""
from __future__ import annotations

import colorsys
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets/NEON_STAGE"
MANIFEST_PATH = ASSET_DIR / "neon_stage_4k_asset_manifest.json"
TOKENS_PATH = ASSET_DIR / "neon_stage_default_tokens.json"
THEME_PATH = ROOT / "SKIN/Skin_053/theme.json"
MASTER_PATH = ROOT / "assets/POP_PUNK_GUITAR_ULTIMATE_BANNER.svg"
EXPECTED_MASTER_BLOB = "82854d433e3a4183c13fbd6d3c131d565a621f46"
EXPECTED_VIEWBOX = "0 0 1800 720"
EXPECTED_SIZE = ("3840", "1536")
SVG_NS = "{http://www.w3.org/2000/svg}"
HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def git_blob_sha(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path.relative_to(ROOT))],
        cwd=ROOT, text=True
    ).strip()


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return {}


def validate_svg(path: Path, expected_symbols: set[str]) -> None:
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        fail(f"{path.relative_to(ROOT)}: malformed SVG/XML: {exc}")
        return

    root = tree.getroot()
    if root.tag != SVG_NS + "svg":
        fail(f"{path.name}: root element is not SVG")
    if (root.get("width"), root.get("height")) != EXPECTED_SIZE:
        fail(f"{path.name}: expected 3840x1536 export dimensions")
    if root.get("viewBox") != EXPECTED_VIEWBOX:
        fail(f"{path.name}: expected viewBox {EXPECTED_VIEWBOX} (5:2 source geometry)")

    ids: set[str] = set()
    duplicates: set[str] = set()
    for node in root.iter():
        identifier = node.get("id")
        if identifier:
            if identifier in ids:
                duplicates.add(identifier)
            ids.add(identifier)
    if duplicates:
        fail(f"{path.name}: duplicate XML ids: {sorted(duplicates)}")

    actual_symbols = {
        node.get("id") for node in root.findall(f".//{SVG_NS}symbol")
        if node.get("id")
    }
    missing = expected_symbols - actual_symbols
    if missing:
        fail(f"{path.name}: manifest symbols missing from SVG: {sorted(missing)}")

    for node in root.iter():
        for attr in ("href", "{http://www.w3.org/1999/xlink}href"):
            ref = node.get(attr)
            if ref and ref.startswith("#") and ref[1:] not in ids:
                fail(f"{path.name}: unresolved local reference {ref}")

    # The master banner is intentionally excluded: it is immutable artwork.
    # Runtime library assets must not reintroduce the legacy blue/cyan palette.
    for node in root.iter():
        for attr in ("fill", "stroke", "stop-color", "flood-color", "color"):
            value = node.get(attr)
            if not value or not HEX_RE.match(value):
                continue
            r, g, b = (int(value[i:i+2], 16) / 255.0 for i in (1, 3, 5))
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            hue = h * 360.0
            if s > 0.45 and v > 0.2 and 175.0 <= hue <= 255.0:
                fail(f"{path.name}: forbidden blue/cyan runtime color {value}")


def main() -> int:
    manifest = load_json(MANIFEST_PATH)
    tokens = load_json(TOKENS_PATH)
    theme = load_json(THEME_PATH)
    palette = theme.get("palette", {})
    token_palette = tokens.get("palette", {})
    if palette != token_palette:
        fail("neon_stage_default_tokens.json palette differs from Skin_053/theme.json")

    try:
        master_sha = git_blob_sha(MASTER_PATH)
        if master_sha != EXPECTED_MASTER_BLOB:
            fail(f"immutable master banner blob changed: {master_sha}")
    except Exception as exc:
        fail(f"could not verify immutable master banner: {exc}")

    authority = manifest.get("visualAuthority", {})
    if authority.get("sha") != EXPECTED_MASTER_BLOB or authority.get("immutable") is not True:
        fail("manifest visualAuthority does not pin the immutable master banner")
    if manifest.get("themeAuthority", {}).get("file") != "SKIN/Skin_053/theme.json":
        fail("manifest themeAuthority does not point to canonical Skin_053 theme")

    files = manifest.get("files", [])
    catalog_entries = manifest.get("catalogs", [])
    if not files or not catalog_entries:
        fail("manifest must list SVG files and symbol catalogs")

    catalog_by_file = {
        entry.get("file"): set(entry.get("symbols", []))
        for entry in catalog_entries
    }
    for relative in files:
        path = ROOT / relative
        if path.suffix.lower() != ".svg":
            continue
        if not path.is_file():
            fail(f"manifest SVG does not exist: {relative}")
            continue
        validate_svg(path, catalog_by_file.get(path.name, set()))

    if manifest.get("sourceArtworkAuthorization", {}).get("status") != "owner_attested_2026-11-21":
        fail("Meshy owner-attestation status missing from asset manifest")

    if ERRORS:
        print("NEON STAGE SVG validation FAILED:")
        for error in ERRORS:
            print(f" - {error}")
        return 1

    symbol_count = sum(len(entry.get("symbols", [])) for entry in catalog_entries)
    print(f"NEON STAGE SVG validation passed: {len(files)} manifest files, {symbol_count} catalog symbols; 3840x1536/5:2; Skin_053 palette; immutable master SHA verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
