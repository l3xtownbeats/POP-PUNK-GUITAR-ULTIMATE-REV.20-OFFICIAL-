#!/usr/bin/env python3
"""Validate REV.20's exact 16-theme registry without accepting legacy skins."""
from __future__ import annotations
import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIN = ROOT / "SKIN"
EXPECTED = [
    ("SKIN-1", "NEON STAGE DEFAULT", "skin-053", 53, "Skin_053"),
    ("SKIN-2", "OBSIDIAN GOLD", "skin-103", 103, "Skin_103"),
    ("SKIN-3", "CARBON FORGE", "skin-104", 104, "Skin_104"),
    ("SKIN-4", "MIDNIGHT CRIMSON", "skin-105", 105, "Skin_105"),
    ("SKIN-5", "ARCTIC PLATINUM", "skin-106", 106, "Skin_106"),
    ("SKIN-6", "VIOLET NOIR", "skin-107", 107, "Skin_107"),
    ("SKIN-7", "TITANIUM STORM", "skin-108", 108, "Skin_108"),
    ("SKIN-8", "EMERALD CIRCUIT", "skin-109", 109, "Skin_109"),
    ("SKIN-9", "SOLAR FLARE", "skin-110", 110, "Skin_110"),
    ("SKIN-10", "DEEP OCEAN", "skin-111", 111, "Skin_111"),
    ("SKIN-11", "ROSE CHROME", "skin-112", 112, "Skin_112"),
    ("SKIN-12", "DESERT AMBER", "skin-113", 113, "Skin_113"),
    ("SKIN-13", "GLACIER TEAL", "skin-114", 114, "Skin_114"),
    ("SKIN-14", "PHANTOM GRAPHITE", "skin-115", 115, "Skin_115"),
    ("SKIN-15", "ULTRAVIOLET DRIVE", "skin-116", 116, "Skin_116"),
    ("SKIN-16", "VOLCANIC STEEL", "skin-117", 117, "Skin_117"),
]

def validate_png(path: Path, expected_size: tuple[int, int]) -> None:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise SystemExit(f"FAIL: invalid PNG signature: {path}")
    offset = 8
    dimensions = None
    saw_iend = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise SystemExit(f"FAIL: truncated PNG chunk: {path}")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(data):
            raise SystemExit(f"FAIL: PNG chunk exceeds file size: {path}")
        chunk_type = data[offset + 4:offset + 8]
        chunk_data = data[offset + 8:offset + 8 + length]
        stored_crc = struct.unpack(">I", data[offset + 8 + length:end])[0]
        actual_crc = zlib.crc32(data[offset + 4:offset + 8 + length]) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            raise SystemExit(f"FAIL: PNG CRC mismatch in {chunk_type!r}: {path}")
        if chunk_type == b"IHDR":
            if length != 13:
                raise SystemExit(f"FAIL: invalid PNG IHDR length: {path}")
            dimensions = struct.unpack(">II", chunk_data[:8])
        if chunk_type == b"IEND":
            if length != 0:
                raise SystemExit(f"FAIL: invalid PNG IEND: {path}")
            saw_iend = True
            offset = end
            break
        offset = end
    if not saw_iend or offset != len(data):
        raise SystemExit(f"FAIL: incomplete PNG or trailing data: {path}")
    if dimensions != expected_size:
        raise SystemExit(f"FAIL: PNG dimensions {dimensions!r}, expected {expected_size!r}: {path}")


def main() -> int:
    registry = json.loads((SKIN / "theme_manifest.json").read_text(encoding="utf-8"))
    entries = registry.get("themes", [])
    if registry.get("totalSkins") != 16 or len(entries) != 16:
        raise SystemExit("FAIL: runtime registry must contain exactly 16 themes")
    if registry.get("defaultStableId") != "skin-053":
        raise SystemExit("FAIL: NEON STAGE DEFAULT must remain skin-053")
    seen = set()
    ready = []
    for position, (entry, expected) in enumerate(zip(entries, EXPECTED, strict=True), 1):
        label, name, stable_id, index, folder = expected
        actual = (entry.get("label"), entry.get("name"), entry.get("id"),
                  entry.get("index"), Path(entry.get("path", "")).parent.name)
        if actual != expected:
            raise SystemExit(f"FAIL: theme entry mismatch: {actual!r} != {expected!r}")
        if entry.get("ordinal") != position:
            raise SystemExit("FAIL: logical theme ordinals must be 1..16 in order")
        if stable_id in seen:
            raise SystemExit("FAIL: duplicate stable theme ID")
        seen.add(stable_id)
        manifest_path = SKIN / entry["path"]
        if not manifest_path.is_file():
            raise SystemExit(f"FAIL: missing theme manifest: {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("id") != stable_id or manifest.get("index") != index:
            raise SystemExit(f"FAIL: manifest stable identity mismatch for {label}")
        if manifest.get("name") != name:
            raise SystemExit(f"FAIL: manifest name mismatch for {label}")
        if len(manifest.get("palette", {})) != 21:
            raise SystemExit(f"FAIL: {label} must define exactly 21 palette tokens")
        if len(manifest.get("controls", {})) != 28:
            raise SystemExit(f"FAIL: {label} must retain 27 controls plus sync_selector metadata")
        assets = manifest.get("assets", {})
        for key, size in (("preview", (360, 240)), ("hero", (800, 450))):
            relative = entry.get(key)
            expected_relative = f"{folder}/assets/{key}.png"
            if relative != expected_relative or assets.get(key) != f"assets/{key}.png":
                raise SystemExit(f"FAIL: invalid {key} path for {label}")
            asset_path = SKIN / relative
            if not asset_path.is_file():
                raise SystemExit(f"FAIL: {label} lacks artwork {key}: {asset_path}")
            validate_png(asset_path, size)
        for key in ("texture", "bezel", "crest"):
            relative_svg = assets.get(key)
            if not relative_svg or not (manifest_path.parent / relative_svg).is_file():
                raise SystemExit(f"FAIL: {label} lacks SVG layer {key}")
        if entry.get("runtimeReady") is True:
            ready.append(stable_id)
        elif entry.get("runtimeReady") is not False:
            raise SystemExit(f"FAIL: runtimeReady must be explicit for {label}")
    expected_dirs = {entry[4] for entry in EXPECTED}
    actual_dirs = {p.name for p in SKIN.iterdir()
                   if p.is_dir() and p.name.startswith("Skin_")}
    if actual_dirs != expected_dirs:
        raise SystemExit(f"FAIL: only approved 16 theme directories may exist; found {sorted(actual_dirs)}")
    expected_ready = [item[2] for item in EXPECTED]
    if ready != expected_ready:
        raise SystemExit(f"FAIL: all 16 approved themes must be runtime-ready after exact-SHA SVG decode/package validation; got {ready}")
    print("PASS: exactly 16 named runtime-ready themes; all 32 preview/hero PNG dimensions and CRCs; all 48 SVG layers; all 21-token/28-entry manifests; no extra theme directories.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
