#!/usr/bin/env python3
"""Render the 15 Skin Studio SVG material layers to verified 1x/2x/3x PNGs.

The source SVGs remain authoritative. This producer emits a build artifact and
rewrites only the workspace copies of theme.json so Windows CI/runtime tests
consume PNG paths without changing the committed design manifests.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
THEMES = range(103, 118)
LAYERS = {"texture": (512, 512), "bezel": (800, 450), "crest": (480, 168)}
SCALES = (1, 2, 3)

class ResvgWorker:
    def __init__(self):
        self.process = subprocess.Popen(
            ["node", str(ROOT / "tools" / "render_neon_stage_svg.cjs")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1,
        )

    def render(self, source: Path, output: Path, width: int, height: int):
        output.parent.mkdir(parents=True, exist_ok=True)
        request = {"source": str(source), "output": str(output), "width": width, "height": height}
        assert self.process.stdin and self.process.stdout
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        response = self.process.stdout.readline()
        if not response:
            stderr = self.process.stderr.read() if self.process.stderr else ""
            raise RuntimeError(f"Resvg worker exited without response: {stderr}")
        result = json.loads(response)
        if not result.get("ok"):
            raise RuntimeError(result.get("error", "Resvg render failed"))

    def close(self):
        if self.process.poll() is None:
            assert self.process.stdin
            self.process.stdin.write(json.dumps({"quit": True}) + "\n")
            self.process.stdin.flush()
            self.process.stdin.close()
            self.process.wait(timeout=60)
        if self.process.returncode != 0:
            stderr = self.process.stderr.read() if self.process.stderr else ""
            raise RuntimeError(f"Resvg worker failed: {stderr}")

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    worker = ResvgWorker()
    records = []
    errors = []
    try:
        for index in THEMES:
            folder = ROOT / "SKIN" / f"Skin_{index}"
            manifest_path = folder / "theme.json"
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                if manifest.get("id") != f"skin-{index}" or manifest.get("index") != index:
                    raise ValueError("theme identity mismatch")
                assets = manifest.get("assets", {})
                for layer, (width, height) in LAYERS.items():
                    source_rel = assets.get(layer, f"svg/{layer}.svg")
                    source = folder / source_rel
                    if not source.is_file() or source.suffix.lower() != ".svg":
                        raise ValueError(f"missing SVG source for {layer}: {source_rel}")
                    root = ET.fromstring(source.read_bytes())
                    if not root.tag.endswith("svg"):
                        raise ValueError(f"{layer} source root is not SVG")
                    variants = []
                    for scale in SCALES:
                        suffix = "" if scale == 1 else f"@{scale}x"
                        output = folder / "assets" / "png_migration" / f"{layer}{suffix}.png"
                        worker.render(source, output, width * scale, height * scale)
                        with Image.open(output) as image:
                            image.load()
                            if image.format != "PNG" or image.size != (width * scale, height * scale):
                                raise ValueError(f"{layer} {scale}x decoded dimensions mismatch: {image.size}")
                            rgba = image.convert("RGBA")
                            rgba.save(output, format="PNG", optimize=True)
                        variants.append({
                            "scale": f"{scale}x", "path": output.relative_to(ROOT).as_posix(),
                            "width": width * scale, "height": height * scale,
                            "sha256": sha256(output),
                        })
                    assets[layer] = f"assets/png_migration/{layer}.png"
                    records.append({
                        "theme": f"skin-{index}", "layer": layer,
                        "source": source.relative_to(ROOT).as_posix(),
                        "sourceSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                        "variants": variants,
                    })
                manifest["assets"] = assets
                manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            except Exception as exc:
                errors.append(f"Skin_{index}: {exc}")
    finally:
        try:
            worker.close()
        except Exception as exc:
            errors.append(f"Resvg shutdown: {exc}")

    report = {
        "schemaVersion": "1.0.0",
        "sourceThemes": 15,
        "sourceLayers": 45,
        "variantCount": len(records) * 3,
        "renderer": "@resvg/resvg-js",
        "records": records,
    }
    output = ROOT / "SKIN" / "skin_studio_png_migration_manifest.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Skin Studio SVG sources: 45; PNG variants: {len(records) * 3}; output: {output.relative_to(ROOT)}")
    if errors:
        print("SKIN STUDIO PNG MIGRATION: FAIL")
        for error in errors:
            print("ERROR:", error)
        return 1
    if len(records) != 45:
        print("SKIN STUDIO PNG MIGRATION: FAIL (expected exactly 45 layers)")
        return 1
    print("SKIN STUDIO PNG MIGRATION: PASS (15 themes x 3 layers x 1x/2x/3x; decoded RGBA; SHA-256)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
