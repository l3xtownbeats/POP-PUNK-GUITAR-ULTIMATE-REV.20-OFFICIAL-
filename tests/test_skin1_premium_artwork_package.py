#!/usr/bin/env python3
"""Verify Skin-1's premium runtime artwork is staged byte-for-byte beside the VST3."""
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIN_ID = "Skin_053"
RUNTIME_ASSETS = {
    "assets/background/main.png": (2560, 1440),
    "assets/textures/material.png": (1024, 1024),
    "assets/fx_layers/stage_glow.png": (800, 450),
    "assets/fx_layers/edge_highlight.png": (800, 450),
    "assets/fx_layers/specular.png": (800, 450),
    "assets/fx_layers/shadow.png": (800, 450),
    "assets/spritesheets/neon_stage_rotary_black_disc_61frame_atlas.png": (1024, 1024),
    "assets/spritesheets/neon_stage_rotary_knurled_steel_61frame_atlas.png": (1024, 1024),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        if stream.read(8) != b"\x89PNG\r\n\x1a\n":
            raise AssertionError(f"not a PNG file: {path}")
        stream.read(8)
        return struct.unpack(">II", stream.read(8))


def main() -> int:
    source_skin = ROOT / "SKIN" / SKIN_ID
    with tempfile.TemporaryDirectory(prefix="ppgu-skin1-premium-") as temp:
        staged_root = Path(temp) / "Skins"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "package_active_skins.py"),
                "--root",
                str(ROOT / "SKIN"),
                "--output",
                str(staged_root),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            sys.stderr.write(result.stdout)
            sys.stderr.write(result.stderr)
            return result.returncode

        staged_skin = staged_root / SKIN_ID
        for relative, dimensions in RUNTIME_ASSETS.items():
            original = source_skin / relative
            staged = staged_skin / relative
            if not original.is_file() or not staged.is_file():
                raise AssertionError(f"missing Skin-1 runtime artwork: {relative}")
            if png_dimensions(original) != dimensions:
                raise AssertionError(f"unexpected source dimensions for {relative}")
            if png_dimensions(staged) != dimensions:
                raise AssertionError(f"unexpected staged dimensions for {relative}")
            if sha256(original) != sha256(staged):
                raise AssertionError(f"staged artwork changed bytes: {relative}")

        # Every control/state image is shipped exactly as authored and remains Skin-1-only.
        control_manifest_path = source_skin / "assets" / "controls" / "control_states_manifest.json"
        control_manifest = json.loads(control_manifest_path.read_text(encoding="utf-8"))
        expected_states = {"default", "hover", "pressed", "disabled", "dragged"}
        control_ids = control_manifest["controlIds"]
        records = control_manifest["records"]
        if len(control_ids) != 27 or len(set(control_ids)) != 27:
            raise AssertionError("expected 27 unique Skin-1 control IDs")
        if set(control_manifest["states"]) != expected_states or len(records) != 135:
            raise AssertionError("expected five states for each Skin-1 control")
        seen = set()
        for record in records:
            key = (record["controlId"], record["state"])
            if key in seen or key[0] not in control_ids or key[1] not in expected_states:
                raise AssertionError(f"duplicate or invalid control state: {key}")
            seen.add(key)
            relative = record["runtime"]
            original = source_skin / relative
            staged = staged_skin / relative
            if not original.is_file() or not staged.is_file():
                raise AssertionError(f"missing control-state asset: {relative}")
            if png_dimensions(original) != (256, 256) or png_dimensions(staged) != (256, 256):
                raise AssertionError(f"unexpected control-state dimensions: {relative}")
            if sha256(original) != sha256(staged):
                raise AssertionError(f"control-state asset changed during staging: {relative}")
        if len(seen) != 135:
            raise AssertionError(f"expected 135 unique control states, found {len(seen)}")
        staged_controls_manifest = staged_skin / "assets" / "controls" / "control_states_manifest.json"
        if not staged_controls_manifest.is_file():
            raise AssertionError("control-state manifest was not packaged")
        if (staged_root / "Skin_103" / "assets" / "controls").exists():
            raise AssertionError("Skin-2 must not receive Skin-1 control artwork")

        skin_folders = sorted(
            path.name for path in staged_root.iterdir()
            if path.is_dir() and path.name.startswith("Skin_")
        )
        if len(skin_folders) != 16:
            raise AssertionError(f"expected 16 staged skins, found {len(skin_folders)}")

        # Premium layers are deliberately introduced for Skin-1 first.
        if (staged_root / "Skin_103" / "assets" / "background" / "main.png").exists():
            raise AssertionError("Skin-2 must not receive Skin-1 artwork in this first phase")

    print("PASS — Skin-1 premium artwork is packaged byte-for-byte with correct dimensions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
