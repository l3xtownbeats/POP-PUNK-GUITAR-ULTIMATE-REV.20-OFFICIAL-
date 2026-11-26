#!/usr/bin/env python3
"""Validate REV.20's exact 16-theme registry without accepting legacy skins."""
from __future__ import annotations
import json
import hashlib
import struct
import zlib
import xml.etree.ElementTree as ET
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
    ("SKIN-10", "STILLWATER", "skin-111", 111, "Skin_111"),
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




def validate_svg(path: Path) -> None:
    """Reject malformed, oversized, or externally-referencing theme SVGs."""
    if not path.is_file() or path.is_symlink() or path.stat().st_size <= 0 \
            or path.stat().st_size > 256 * 1024:
        raise SystemExit(f"FAIL: missing, linked, empty, or oversized SVG: {path}")
    try:
        root = ET.fromstring(path.read_bytes())
    except (ET.ParseError, OSError) as exc:
        raise SystemExit(f"FAIL: malformed SVG {path}: {exc}")
    if root.tag.split("}")[-1] != "svg":
        raise SystemExit(f"FAIL: SVG root element is not <svg>: {path}")
    forbidden = {"script", "foreignObject", "image", "iframe", "object", "embed"}
    for element in root.iter():
        if element.tag.split("}")[-1] in forbidden:
            raise SystemExit(f"FAIL: unsupported active/embedded SVG element in {path}")
        for key, value in element.attrib.items():
            local_key = key.split("}")[-1].lower()
            text_value = value.strip().lower()
            if local_key in {"href", "src"} and not (
                    text_value.startswith("#") or text_value.startswith("data:")):
                raise SystemExit(f"FAIL: external SVG reference in {path}")
            if "url(" in text_value and not (
                    "url(#" in text_value or "url('#" in text_value
                    or 'url("#' in text_value):
                raise SystemExit(f"FAIL: external SVG URL reference in {path}")



def validate_neon_stage_asset_manifest() -> int:
    """Verify every inventoried NEON STAGE source/runtime asset against its manifest."""
    theme_root = SKIN / "Skin_053"
    manifest_path = theme_root / "assets" / "asset_manifest.json"
    if not manifest_path.is_file():
        raise SystemExit("FAIL: missing NEON STAGE asset integrity manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = manifest.get("records", [])
    if manifest.get("assetCount") != len(records) or not records:
        raise SystemExit("FAIL: NEON STAGE asset manifest count mismatch")

    seen = set()
    for record in records:
        relative = record.get("path")
        if (not isinstance(relative, str) or not relative
                or relative.startswith("/") or chr(92) in relative
                or any(part in ("", ".", "..") for part in relative.split("/"))):
            raise SystemExit(f"FAIL: unsafe asset manifest path: {relative!r}")
        if relative in seen:
            raise SystemExit(f"FAIL: duplicate asset manifest path: {relative}")
        seen.add(relative)

        asset = theme_root / relative
        resolved_root = theme_root.resolve()
        resolved_asset = asset.resolve()
        if (not asset.is_file() or asset.is_symlink()
                or not resolved_asset.is_relative_to(resolved_root)):
            raise SystemExit(f"FAIL: missing, linked, or out-of-theme asset: {asset}")

        data = asset.read_bytes()
        # Windows Git checkouts may expand LF to CRLF for text assets. Integrity
        # metadata describes the canonical Git blob, so normalize checkout-only
        # line-ending conversion before checking byte count and digests.
        if record.get("format") in ("JSON", "SVG"):
            data = data.replace(b"\r\n", b"\n")
        if len(data) != record.get("bytes"):
            raise SystemExit(f"FAIL: asset byte count mismatch: {asset}")
        actual_sha256 = hashlib.sha256(data).hexdigest()
        expected_sha256 = record.get("sha256")
        if actual_sha256 != expected_sha256:
            raise SystemExit(
                f"FAIL: asset SHA-256 mismatch: {asset}; "
                f"expected={expected_sha256}; actual={actual_sha256}; "
                f"bytes={len(data)}; format={record.get('format')!r}"
            )
        actual_crc = f"{zlib.crc32(data) & 0xFFFFFFFF:08X}"
        if actual_crc != str(record.get("crc32", "")).upper():
            raise SystemExit(f"FAIL: asset CRC32 mismatch: {asset}")

        asset_format = record.get("format")
        suffix = asset.suffix.lower()
        expected_suffix = {"PNG": ".png", "SVG": ".svg", "JSON": ".json"}.get(asset_format)
        if expected_suffix is None or suffix != expected_suffix:
            raise SystemExit(f"FAIL: asset format/extension mismatch: {asset}")
        if asset_format == "PNG":
            dimensions = record.get("dimensions", "")
            try:
                width, height = (int(value) for value in dimensions.split("x", 1))
            except (TypeError, ValueError):
                raise SystemExit(f"FAIL: invalid PNG dimensions metadata: {asset}")
            validate_png(asset, (width, height))

    return len(records)


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
        required_svg_layers = ["texture", "bezel", "crest"]
        if stable_id != "skin-053":
            required_svg_layers.extend(["controls", "fxLayers", "decorative"])
        for key in required_svg_layers:
            relative_svg = assets.get(key)
            if (not isinstance(relative_svg, str) or not relative_svg
                    or relative_svg.startswith("/") or chr(92) in relative_svg
                    or any(part in ("", ".", "..") for part in relative_svg.split("/"))):
                raise SystemExit(f"FAIL: {label} has an unsafe or missing SVG path for {key}")
            svg_path = manifest_path.parent / relative_svg
            if not svg_path.resolve().is_relative_to(manifest_path.parent.resolve()):
                raise SystemExit(f"FAIL: {label} SVG escapes its theme directory: {key}")
            validate_svg(svg_path)
        if entry.get("runtimeReady") is True:
            ready.append(stable_id)
        elif entry.get("runtimeReady") is not False:
            raise SystemExit(f"FAIL: runtimeReady must be explicit for {label}")
    expected_dirs = {entry[4] for entry in EXPECTED}
    actual_dirs = {p.name for p in SKIN.iterdir()
                   if p.is_dir() and p.name.startswith("Skin_")}
    if actual_dirs != expected_dirs:
        raise SystemExit(f"FAIL: only approved 16 theme directories may exist; found {sorted(actual_dirs)}")
    verified_asset_count = validate_neon_stage_asset_manifest()
    # NEON STAGE DEFAULT's dedicated sprite atlas package is validated
    # independently from the other 15 skins; the registry remains exactly 16.
    atlas_dir = SKIN / "Skin_053" / "assets" / "spritesheets"
    atlas_names = (
        "neon_stage_controls_spritesheet.png",
        "neon_stage_meters_sliders_sheet.png",
        "neon_stage_frames_panels_sheet.png",
        "neon_stage_icons_sheet.png",
        "neon_stage_rotary_61frame_atlas.png",
        "neon_stage_rotary_black_disc_61frame_atlas.png",
        "neon_stage_rotary_knurled_steel_61frame_atlas.png",
        "neon_stage_main_knob_layers_atlas.png",
    )
    for atlas_name in atlas_names:
        atlas_path = atlas_dir / atlas_name
        if not atlas_path.is_file():
            raise SystemExit(f"FAIL: missing NEON STAGE sprite atlas: {atlas_path}")
        expected_size = (1152, 768) if atlas_name == "neon_stage_main_knob_layers_atlas.png" else (1024, 1024)
        validate_png(atlas_path, expected_size)
    atlas_manifest_path = atlas_dir / "neon_stage_spritesheet_manifest.json"
    default_theme = json.loads((SKIN / "Skin_053" / "theme.json").read_text(encoding="utf-8"))
    if default_theme.get("assets", {}).get("spriteSheetManifest") != "assets/spritesheets/neon_stage_spritesheet_manifest.json":
        raise SystemExit("FAIL: NEON STAGE theme manifest does not reference the atlas manifest")
    if not atlas_manifest_path.is_file():
        raise SystemExit("FAIL: missing NEON STAGE sprite atlas manifest")
    atlas_manifest = json.loads(atlas_manifest_path.read_text(encoding="utf-8"))
    expected_palette = {
        "background": "#05070E",
        "metal_border": "#00D2FF",
        "glow_cyan": "#00E5FF",
        "glow_blue": "#6B8CFF",
        "semantic_warning": "#FFB454",
    }
    if atlas_manifest.get("project") != "NEON_STAGE_MANAGER_3_0" \
            or atlas_manifest.get("theme") != "NEON_STAGE_DEFAULT_SKIN_1" \
            or atlas_manifest.get("canvas") != [1024, 1024] \
            or atlas_manifest.get("base_palette") != expected_palette:
        raise SystemExit("FAIL: NEON STAGE sprite atlas manifest identity/palette mismatch")
    sheets = atlas_manifest.get("sheets", {})
    if set(sheets) != set(atlas_names):
        raise SystemExit("FAIL: NEON STAGE sprite atlas manifest must define exactly eight sheets")
    if sheets.get("neon_stage_rotary_61frame_atlas.png", {}).get("resolution") != [1024, 1024] \
            or sheets["neon_stage_rotary_61frame_atlas.png"].get("cell_size") != [128, 128] \
            or sheets["neon_stage_rotary_61frame_atlas.png"].get("grid") != [8, 8] \
            or sheets["neon_stage_rotary_61frame_atlas.png"].get("frame_count") != 61 \
            or sheets["neon_stage_rotary_61frame_atlas.png"].get("angle_range_deg") != [-135, 135] \
            or sheets["neon_stage_rotary_61frame_atlas.png"].get("angle_step_deg") != 4.5:
        raise SystemExit("FAIL: NEON STAGE 61-frame rotary atlas geometry mismatch")
    main_layers = sheets.get("neon_stage_main_knob_layers_atlas.png", {})
    expected_parameters = [
        "GAIN", "TREBLE", "MID", "BASS", "VELOCITY",
        "DYNAMICS", "SWING", "HUMANIZE", "ACCENT",
    ]
    expected_layers = ["BASE", "RIM", "FACE", "POINTER", "SCALE", "GLOW"]
    if main_layers.get("resolution") != [1152, 768] \
            or main_layers.get("cell_size") != [128, 128] \
            or main_layers.get("grid") != [9, 6] \
            or main_layers.get("parameter_order") != expected_parameters \
            or main_layers.get("layer_order") != expected_layers:
        raise SystemExit("FAIL: nine-control main-knob layer atlas contract mismatch")
    main_frames = main_layers.get("frames", [])
    if len(main_frames) != 54:
        raise SystemExit("FAIL: main-knob layer atlas must declare 54 parameter/layer cells")
    for parameter_index, parameter in enumerate(expected_parameters):
        for layer_index, layer in enumerate(expected_layers):
            frame_index = parameter_index * 6 + layer_index
            frame = main_frames[frame_index]
            x, y = parameter_index * 128, layer_index * 128
            if frame.get("parameter") != parameter \
                    or frame.get("control_id") != f"knob{parameter_index + 1:02d}" \
                    or frame.get("layer") != layer \
                    or frame.get("bbox") != [x, y, x + 128, y + 128]:
                raise SystemExit(
                    f"FAIL: main-knob layer atlas cell mismatch: {parameter}/{layer}"
                )
    default_sheets = default_theme.get("assets", {}).get("spriteSheets", {})
    if default_sheets.get("main_knob_layers") != \
            "assets/spritesheets/neon_stage_main_knob_layers_atlas.png":
        raise SystemExit("FAIL: NEON STAGE theme does not register its main-knob layer atlas")

    for variant_name in ("neon_stage_rotary_black_disc_61frame_atlas.png",
                         "neon_stage_rotary_knurled_steel_61frame_atlas.png"):
        variant = sheets.get(variant_name, {})
        if variant.get("resolution") != [1024, 1024] \
                or variant.get("cell_size") != [128, 128] \
                or variant.get("grid") != [8, 8] \
                or variant.get("frame_count") != 61 \
                or variant.get("angle_range_deg") != [210, 390] \
                or variant.get("angle_step_deg") != 3.0:
            raise SystemExit(f"FAIL: {variant_name} geometry mismatch")
        frames = variant.get("frames", [])
        if len(frames) != 61:
            raise SystemExit(f"FAIL: {variant_name} must declare 61 frames")
        for frame_index, frame in enumerate(frames):
            expected_angle = 210.0 + frame_index * 3.0
            expected_x = (frame_index % 8) * 128
            expected_y = (frame_index // 8) * 128
            if frame.get("frame") != frame_index \
                    or frame.get("angle_deg") != expected_angle \
                    or frame.get("bbox") != [expected_x, expected_y, expected_x + 128, expected_y + 128]:
                raise SystemExit(f"FAIL: {variant_name} frame {frame_index} geometry mismatch")

    controls = sheets["neon_stage_controls_spritesheet.png"]["elements"]
    if controls.get("knobs", {}).get("frames") != 8 \
            or controls.get("knobs", {}).get("angle_step_deg") != 45 \
            or controls.get("knobs", {}).get("size") != [100, 100] \
            or controls.get("knobs", {}).get("row_y") != [120, 220]:
        raise SystemExit("FAIL: NEON STAGE rotary frame geometry mismatch")
    if controls.get("toggle_switch", {}).get("states", {}).get("OFF", {}).get("bbox") != [65, 430, 465, 600] \
            or controls.get("toggle_switch", {}).get("states", {}).get("ON", {}).get("bbox") != [535, 430, 935, 600]:
        raise SystemExit("FAIL: NEON STAGE toggle switch atlas bounds mismatch")
    expected_buttons = {
        "normal": [25, 690, 250, 815],
        "hover": [265, 690, 490, 815],
        "pressed": [505, 690, 730, 815],
        "active": [745, 690, 970, 815],
    }
    actual_buttons = {
        key: value.get("bbox")
        for key, value in controls.get("buttons", {}).get("states", {}).items()
    }
    if actual_buttons != expected_buttons:
        raise SystemExit("FAIL: NEON STAGE button state atlas bounds mismatch")
    if sheets["neon_stage_meters_sliders_sheet.png"]["elements"].get("vu_meters", {}).get("levels_count") != 8:
        raise SystemExit("FAIL: NEON STAGE VU meter must contain exactly eight levels")
    if len(sheets["neon_stage_icons_sheet.png"]["elements"].get("fx_icons", [])) != 7 \
            or len(sheets["neon_stage_icons_sheet.png"]["elements"].get("nav_icons", [])) != 10:
        raise SystemExit("FAIL: NEON STAGE icon atlas must contain 7 FX and 10 navigation icons")

    expected_knob_boxes = [
        [65, 120, 165, 220], [175, 120, 275, 220],
        [285, 120, 385, 220], [395, 120, 495, 220],
        [65, 220, 165, 320], [175, 220, 275, 320],
        [285, 220, 385, 320], [395, 220, 495, 320],
    ]
    knob_frames = controls.get("knobs", {}).get("frames_bbox", [])
    if [frame.get("bbox") for frame in knob_frames] != expected_knob_boxes \
            or [frame.get("angle_deg") for frame in knob_frames] != list(range(0, 360, 45)):
        raise SystemExit("FAIL: NEON STAGE rotary frame positions/angles mismatch")

    meters = sheets["neon_stage_meters_sliders_sheet.png"]["elements"]
    if meters.get("vu_meters", {}).get("bbox_area") != [30, 25, 970, 350] \
            or len(meters.get("vu_meters", {}).get("instances", [])) != 8:
        raise SystemExit("FAIL: NEON STAGE VU meter atlas geometry mismatch")
    sliders = meters.get("sliders", {})
    if sliders.get("types") != ["long_slider", "short_slider"] \
            or sliders.get("bbox_area") != [30, 380, 970, 760]:
        raise SystemExit("FAIL: NEON STAGE slider atlas area/types mismatch")
    slider_instances = sliders.get("instances", {})
    if slider_instances.get("long_slider", {}).get("track_bbox") != [60, 445, 880, 467] \
            or slider_instances.get("short_slider", {}).get("track_bbox") != [60, 570, 450, 592] \
            or slider_instances.get("thumb", {}).get("bbox") != [910, 640, 942, 672]:
        raise SystemExit("FAIL: NEON STAGE slider track/thumb geometry mismatch")
    leds = meters.get("status_leds", {})
    # Warning LEDs are amber (#FFB454); purple/magenta states are intentionally excluded.
    expected_led_states = ["off", "cyan", "blue", "warning"]
    if leds.get("round", {}).get("states") != expected_led_states \
            or leds.get("square", {}).get("states") != expected_led_states \
            or leds.get("round", {}).get("row_y") != [810, 920] \
            or leds.get("square", {}).get("row_y") != [810, 920]:
        raise SystemExit("FAIL: NEON STAGE status LED states/rows mismatch")
    for shape in ("round", "square"):
        rows = leds.get(shape, {}).get("instances", {})
        if set(rows) != {"810", "920"} or any(set(row) != set(expected_led_states) for row in rows.values()):
            raise SystemExit(f"FAIL: NEON STAGE {shape} LEDs must have all four states in both rows")

    panels = sheets["neon_stage_frames_panels_sheet.png"]["elements"]
    if set(panels.get("9_slice_corners", {})) != {
        "top_left", "top_right", "bottom_left", "bottom_right"
    } or set(panels.get("borders", {})) != {
        "top_border", "bottom_border", "left_border", "right_border"
    } or set(panels.get("dividers", {})) != {
        "horizontal_thin", "horizontal_thick", "vertical_thin", "vertical_thick"
    } or set(panels.get("header_bars", {})) != {"standard_header", "compact_header"}:
        raise SystemExit("FAIL: NEON STAGE frame/panel atlas components are incomplete")
    display = panels.get("display_bg", {})
    if display.get("grid") is not True or display.get("tint") != "dark_translucent_cyan":
        raise SystemExit("FAIL: NEON STAGE display background specification mismatch")

    icons = sheets["neon_stage_icons_sheet.png"]["elements"]
    if icons.get("fx_icons") != ["wave", "eq", "distortion", "chorus", "delay", "reverb", "cabinet"] \
            or icons.get("nav_icons") != ["crown", "power", "settings", "info", "folder", "search", "guitar", "antenna", "palette", "play"]:
        raise SystemExit("FAIL: NEON STAGE icon names/order mismatch")

    # STILLWATER is intentionally host-acceptance-gated. Its embedded six-layer
    # artwork package, preview/hero PNGs and all required SVGs are validated above,
    # but it must not be advertised as runtime-ready until FL Studio 20 acceptance.
    expected_ready = [item[2] for item in EXPECTED if item[2] != "skin-111"]
    if ready != expected_ready:
        raise SystemExit(f"FAIL: expected the 15 host-ready themes and a separately gated STILLWATER slot; got {ready}")
    stillwater = next(entry for entry in entries if entry.get("id") == "skin-111")
    if stillwater.get("runtimeReady") is not False or "FL_STUDIO_20_HOST_ACCEPTANCE_PENDING" not in stillwater.get("status", ""):
        raise SystemExit("FAIL: STILLWATER must remain explicitly gated until FL Studio 20 host acceptance")
    print(f"PASS: exactly 16 approved theme slots; 15 runtime-ready themes plus host-acceptance-gated STILLWATER; all theme artwork/SVGs; {verified_asset_count} NEON STAGE assets match byte counts, SHA-256, CRC32 and PNG dimensions; five 1024x1024 sprite atlases and exact atlas geometry; no extra theme directories.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
