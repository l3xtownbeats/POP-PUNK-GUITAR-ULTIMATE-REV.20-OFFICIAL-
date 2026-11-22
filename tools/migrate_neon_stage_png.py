#!/usr/bin/env python3
"""Create audited 1x/2x/3x RGBA PNG derivatives for NEON STAGE SVG batches."""
from __future__ import annotations
import hashlib, json, re, sys, subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "SKIN" / "Skin_053" / "assets"
BATCHES = [ASSETS / f"artwork_batch_{i:02d}" for i in range(1, 9)]
OUTPUT = ASSETS / "png_migration"
SCALES = (1, 2, 3)

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def dimensions(root: ET.Element) -> tuple[int, int]:
    def number(value):
        if not value: return None
        match = re.match(r"^\s*(\d+(?:\.\d+)?)", value)
        return round(float(match.group(1))) if match else None
    width, height = number(root.get("width")), number(root.get("height"))
    if not width or not height:
        view = (root.get("viewBox") or "").replace(",", " ").split()
        if len(view) == 4:
            width = width or round(float(view[2])); height = height or round(float(view[3]))
    if not width or not height: raise ValueError("SVG has no usable width/height or viewBox")
    return width, height

def purple_pixel_diagnostics(image: Image.Image, limit: int = 12) -> tuple[int, list[str]]:
    """Vectorized exact-threshold HSV audit with reproducible pixel samples."""
    rgba = image.convert("RGBA")
    pixels = np.asarray(rgba, dtype=np.uint8)
    rgb = pixels[..., :3].astype(np.float64) / 255.0
    red, green, blue = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maximum = rgb.max(axis=2)
    minimum = rgb.min(axis=2)
    delta = maximum - minimum

    hue = np.zeros_like(maximum)
    chroma = delta > 0.0
    red_max = chroma & (red == maximum)
    green_max = chroma & (~red_max) & (green == maximum)
    blue_max = chroma & (~red_max) & (~green_max)

    hue[red_max] = np.mod((green[red_max] - blue[red_max]) / delta[red_max], 6.0) / 6.0
    hue[green_max] = (2.0 + (blue[green_max] - red[green_max]) / delta[green_max]) / 6.0
    hue[blue_max] = (4.0 + (red[blue_max] - green[blue_max]) / delta[blue_max]) / 6.0

    saturation = np.divide(delta, maximum, out=np.zeros_like(delta), where=maximum > 0.0)
    alpha = pixels[..., 3]
    rejected = (
        (alpha >= 16) & (saturation >= 0.38) & (maximum >= 0.18)
        & (hue >= 0.76) & (hue <= 0.94)
    )
    count = int(np.count_nonzero(rejected))
    samples: list[str] = []
    if count:
        for y, x in np.argwhere(rejected)[:limit]:
            r, g, b, a = (int(value) for value in pixels[y, x])
            h, s, v = float(hue[y, x]), float(saturation[y, x]), float(maximum[y, x])
            samples.append(
                f"(x={int(x)},y={int(y)},rgba={r},{g},{b},{a},hsv={h:.3f},{s:.3f},{v:.3f})"
            )
    return count, samples


def purple_pixels(image: Image.Image) -> int:
    return purple_pixel_diagnostics(image)[0]


class ResvgWorker:
    """One long-lived Node process for all artwork variants in this migration."""
    def __init__(self) -> None:
        self.process = subprocess.Popen(
            ["node", str(ROOT / "tools" / "render_neon_stage_svg.cjs")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1,
        )

    def render(self, source: Path, output: Path, width: int, height: int) -> None:
        if self.process.poll() is not None:
            stderr = self.process.stderr.read() if self.process.stderr else ""
            raise RuntimeError(f"Resvg worker exited early: {stderr}")
        output.parent.mkdir(parents=True, exist_ok=True)
        request = {"source": str(source), "output": str(output),
                   "width": width, "height": height}
        assert self.process.stdin is not None and self.process.stdout is not None
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        response = self.process.stdout.readline()
        if not response:
            stderr = self.process.stderr.read() if self.process.stderr else ""
            raise RuntimeError(f"Resvg worker returned no response: {stderr}")
        result = json.loads(response)
        if not result.get("ok"):
            raise RuntimeError(result.get("error", "Unknown Resvg render error"))

    def close(self) -> None:
        if self.process.poll() is None:
            assert self.process.stdin is not None
            self.process.stdin.write(json.dumps({"quit": True}) + "\n")
            self.process.stdin.flush()
            self.process.stdin.close()
            self.process.wait(timeout=60)
        if self.process.returncode not in (0, None):
            stderr = self.process.stderr.read() if self.process.stderr else ""
            raise RuntimeError(f"Resvg worker shutdown failed: {stderr}")


_RENDERER: ResvgWorker | None = None


def render_png(source: Path, output: Path, width: int, height: int) -> None:
    """Render with one persistent Resvg worker for deterministic HiDPI output."""
    global _RENDERER
    if _RENDERER is None:
        _RENDERER = ResvgWorker()
    _RENDERER.render(source, output, width, height)

def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records, errors, source_count = [], [], 0
    for batch in BATCHES:
        if not batch.is_dir():
            errors.append(f"Missing batch directory: {batch.relative_to(ROOT)}")
            continue
        for source in sorted(batch.rglob("*.svg")):
            source_count += 1
            try:
                svg = source.read_bytes()
                root = ET.fromstring(svg)
                if not root.tag.endswith("svg"): raise ValueError("Root XML element is not <svg>")
                width, height = dimensions(root)
                source_record = {"source": source.relative_to(ROOT).as_posix(),
                                 "sourceSha256": sha256(svg), "variants": []}
                for scale in SCALES:
                    out = OUTPUT / batch.name / f"{source.stem}{'@'+str(scale)+'x' if scale > 1 else ''}.png"
                    out.parent.mkdir(parents=True, exist_ok=True)
                    render_png(source, out, width*scale, height*scale)
                    with Image.open(out) as im:
                        im.load()
                        rgba = im.convert("RGBA")
                        if rgba.size != (width*scale, height*scale):
                            raise ValueError(f"{scale}x dimensions mismatch: {rgba.size}")
                        alpha_min, alpha_max = rgba.getchannel("A").getextrema()
                        bad, samples = purple_pixel_diagnostics(rgba)
                        if bad:
                            raise ValueError(
                                f"{bad} visible purple/violet/magenta pixels detected at {scale}x; "
                                f"first pixel samples: {'; '.join(samples)}"
                            )
                        if rgba.mode != "RGBA": raise ValueError("RGBA conversion failed")
                        rgba.save(out, format="PNG", optimize=True)
                    payload = out.read_bytes()
                    source_record["variants"].append({
                        "scale": f"{scale}x", "png": out.relative_to(ROOT).as_posix(),
                        "width": width*scale, "height": height*scale, "format": "PNG",
                        "mode": "RGBA", "alphaExtrema": [alpha_min, alpha_max],
                        "purplePixelCount": 0, "pngSha256": sha256(payload)
                    })
                records.append(source_record)
            except Exception as exc:
                errors.append(f"{source.relative_to(ROOT)}: {exc}")
    # Convert canonical Skin-1 runtime layers to the exact dimensions consumed by ThemeManager.
    core_artwork = [
        ("texture", ROOT / "SKIN" / "Skin_053" / "svg" / "texture.svg", 512, 512),
        ("bezel", ROOT / "SKIN" / "Skin_053" / "svg" / "bezel.svg", 800, 450),
        ("crest", ROOT / "SKIN" / "Skin_053" / "svg" / "crest.svg", 480, 168),
    ]
    core_records = []
    for name, source, width, height in core_artwork:
        try:
            svg = source.read_bytes()
            root = ET.fromstring(svg)
            if not root.tag.endswith("svg"):
                raise ValueError("Root XML element is not <svg>")
            out = OUTPUT / "runtime_artwork" / f"{name}.png"
            out.parent.mkdir(parents=True, exist_ok=True)
            render_png(source, out, width, height)
            with Image.open(out) as im:
                im.load()
                rgba = im.convert("RGBA")
                if rgba.size != (width, height):
                    raise ValueError(f"runtime dimensions mismatch: {rgba.size}")
                alpha_min, alpha_max = rgba.getchannel("A").getextrema()
                bad, samples = purple_pixel_diagnostics(rgba)
                if bad:
                    raise ValueError(
                        f"{bad} visible purple/violet/magenta pixels detected; "
                        f"first pixel samples: {'; '.join(samples)}"
                    )
                rgba.save(out, format="PNG", optimize=True)
            payload = out.read_bytes()
            core_records.append({
                "name": name, "source": source.relative_to(ROOT).as_posix(),
                "sourceSha256": sha256(svg), "png": out.relative_to(ROOT).as_posix(),
                "width": width, "height": height, "format": "PNG", "mode": "RGBA",
                "alphaExtrema": [alpha_min, alpha_max], "pngSha256": sha256(payload)
            })
        except Exception as exc:
            errors.append(f"{source.relative_to(ROOT)}: {exc}")
    if _RENDERER is not None:
        try:
            _RENDERER.close()
        except Exception as exc:
            errors.append(f"Resvg worker shutdown: {exc}")

    # Dedicated 13-piece production panel library. SVG sources stay editable;
    # runtime receives deterministic transparent PNGs at 1x/2x/3x.
    panel_names = [
        "PPGU_SKIN053_PANEL_HEADER",
        "PPGU_SKIN053_PANEL_PRESET_BROWSER",
        "PPGU_SKIN053_PANEL_PLAYING_CORE",
        "PPGU_SKIN053_PANEL_AMP_FX_RACK",
        "PPGU_SKIN053_PANEL_PERFORMANCE_STRIP",
        "PPGU_SKIN053_PANEL_MIDI_KEYBOARD_BAY",
        "PPGU_SKIN053_PANEL_STATUS_FOOTER",
        "PPGU_SKIN053_PANEL_IMPORT_GUITAR",
        "PPGU_SKIN053_PANEL_FX_EDIT",
        "PPGU_SKIN053_PANEL_PATTERN_ROUTING",
        "PPGU_SKIN053_PANEL_AUTOCHORDS",
        "PPGU_SKIN053_PANEL_WORKSPACE_SETTINGS",
        "PPGU_SKIN053_PANEL_SKIN_GALLERY",
    ]
    panel_records = []
    for name in panel_names:
        source = ASSETS / "panel_sources" / f"{name}.svg"
        try:
            svg = source.read_bytes()
            root = ET.fromstring(svg)
            if not root.tag.endswith("svg"):
                raise ValueError("SVG root element is invalid")
            width, height = dimensions(root)
            record = {"name": name, "source": source.relative_to(ROOT).as_posix(),
                      "sourceSha256": sha256(svg), "variants": []}
            for scale in SCALES:
                suffix = "" if scale == 1 else f"@{scale}x"
                out = ASSETS / "panels" / f"{name}{suffix}.png"
                out.parent.mkdir(parents=True, exist_ok=True)
                render_png(source, out, width * scale, height * scale)
                with Image.open(out) as im:
                    im.load()
                    rgba = im.convert("RGBA")
                    if rgba.size != (width * scale, height * scale):
                        raise ValueError(f"{scale}x dimensions mismatch: {rgba.size}")
                    alpha_min, alpha_max = rgba.getchannel("A").getextrema()
                    bad, samples = purple_pixel_diagnostics(rgba)
                    if bad:
                        raise ValueError(f"{bad} forbidden purple pixels: {'; '.join(samples)}")
                    rgba.save(out, format="PNG", optimize=True)
                payload = out.read_bytes()
                record["variants"].append({
                    "scale": f"{scale}x", "png": out.relative_to(ROOT).as_posix(),
                    "width": width * scale, "height": height * scale,
                    "format": "PNG", "mode": "RGBA",
                    "alphaExtrema": [alpha_min, alpha_max],
                    "purplePixelCount": 0, "pngSha256": sha256(payload)
                })
            panel_records.append(record)
        except Exception as exc:
            errors.append(f"panel {name}: {exc}")

    manifest = {"schemaVersion":"1.1.0","skinId":"skin-053","theme":"NEON STAGE DEFAULT",
                "conversion":"SVG -> PNG RGBA; 1x/2x/3x","sourceCount":source_count,
                "convertedSourceCount":len(records),"variantCount":sum(len(x["variants"]) for x in records),
                "records":records,"runtimeArtwork":core_records,"productionPanels":panel_records}
    path = OUTPUT / "png_manifest.json"
    path.write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(f"SVG sources: {source_count}; converted sources: {len(records)}; PNG variants: {manifest['variantCount']}")
    print(f"Manifest: {path.relative_to(ROOT)}")
    print(f"Runtime artwork layers: {len(core_records)}/3")
    print(f"Dedicated production panels: {len(panel_records)}/{len(panel_names)}; PNG variants: {sum(len(x['variants']) for x in panel_records)}")
    if errors:
        print("PNG MIGRATION AUDIT: FAIL")
        for error in errors: print("ERROR:", error)
        return 1
    if source_count == 0: print("PNG MIGRATION AUDIT: FAIL (no SVG sources)"); return 1
    if len(core_records) != 3: print("PNG MIGRATION AUDIT: FAIL (runtime artwork incomplete)"); return 1
    if len(panel_records) != len(panel_names): print("PNG MIGRATION AUDIT: FAIL (production panel library incomplete)"); return 1
    print("PNG MIGRATION AUDIT: PASS (batch HiDPI + 3 runtime layers; RGBA, dimensions, alpha, palette scan, SHA-256)")
    print("Runtime texture/bezel/crest paths are PNG-backed; batch control artwork still requires individual JUCE component bindings.")
    return 0

if __name__ == "__main__": sys.exit(main())
