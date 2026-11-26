# NEON STAGE — production control artwork source

## Canonical visual reference
- Visual authority: the owner-designated PPGU mockups and atlases stored in Library/GitHub. The repository-root `01 INTERFACE  NEON STAGE DEFAULT .png` is explicitly excluded by the owner and is not a required dependency.
- Skin: `SKIN/Skin_053` / `skin-053`.
- Palette authority: `SKIN/Skin_053/theme.json`. Use `window_bg #080B14`, `panel #101827`, `panel_elevated #17243A`, `control_border #31506F`, `accent #00D9FF`, `accent_glow #6B8CFF`, `danger #FF665E`, `warning #FFB454`, and the remaining exact theme tokens. Do not substitute the NEON STAGE Manager 3.0 palette.
- This vector master is a reusable rotary-control face source, not a new skin or a replacement mockup.

## Rotary master
- Source: `SKIN/Skin_053/assets/vector/rotary_knob_master.svg`.
- Canvas: 512×512 transparent SVG; labels, parameter names and live values are intentionally excluded and must be rendered by JUCE.
- Construction: cast-shadow layer, machined graphite/steel outer bezel, inset dark enamel face, radial index marks, restrained cyan arc, metallic pointer and illuminated center hub.
- Preserve the same physical design across all nine controls. Only the live pointer/value and interaction state may change.
- The APVTS value remains continuous. If rasterized to a frame atlas, derive each frame from this single master with pointer rotation; do not draw unrelated knobs per frame.
- Target production exports: 512×512 master PNG per state where required; 128×128 or 256×256 runtime images according to existing loader contract; transparent RGBA; sRGB; no baked text.

## Required states
- default: neutral graphite/steel, restrained cyan index.
- hover: brighter edge reflection, no geometry change.
- pressed: subtle inward shadow / compressed highlight, no geometry change.
- dragged: value pointer follows the continuous APVTS value; do not bake a fixed angle into a shared state PNG.
- disabled: reduced luminance/contrast while retaining legibility.

## Existing assets to audit before replacement
- `SKIN/Skin_053/assets/controls/knob01..knob09_{default,hover,pressed,disabled,dragged}.png`
- `SKIN/Skin_053/assets/master/controls/knob01..knob09_{default,hover,pressed,disabled,dragged}.png`
- `SKIN/Skin_053/assets/spritesheets/neon_stage_rotary_61frame_atlas.png`
- `SKIN/Skin_053/assets/spritesheets/neon_stage_spritesheet_manifest.json`
- `SKIN/Skin_053/assets/asset_manifest.json`

## Integration constraints
- Inspect the current 61-frame renderer and artwork lookup before wiring new images. Do not overlay a static pointer on top of an atlas frame that already contains one.
- Do not replace approved files until image comparison against the canonical mockup, PNG dimensions, alpha bounds, CRC/SHA-256, manifest and package tests are updated.
- Never add baked labels, fake LEDs, decorative relays or controls that do not correspond to real JUCE/APVTS behavior.


## REV.20 layer extraction / runtime mapping — 2026-11-26

- The six semantic layers are `BASE`, `RIM`, `FACE`, `POINTER`, `SCALE`, `GLOW`.
- `tools/rotary_master_layers.py` splits the canonical SVG source elements into independently addressable SVG groups. It validates the expected source geometry before extraction so a changed SVG structure stops the export rather than silently creating a different knob.
- The Ubuntu atlas/export pipeline rasterizes those exact separated SVG groups with pinned CairoSVG. The Windows runtime build uses a portable Pillow renderer whose radii, paths, colors, ticks and layer roles mirror the same 512×512 master; this avoids requiring a native Cairo DLL on the Windows VST3 runner. The Pillow output is a raster counterpart, not a claim of vector-identical Cairo pixels.
- The runtime atlas is 9 columns × 6 rows at 128×128 per cell. The nine columns keep the fixed REV.20 parameter order; physical hardware is shared, while labels and values remain JUCE text. The live pointer is drawn by JUCE from the continuous APVTS value; no static pointer is layered over it.
- The FX EDIT controls remain on their separate 61-frame material-family atlases. No FX EDIT rotary was replaced by the main control design.
- Atlas project identity and palette are `POP_PUNK_GUITAR_ULTIMATE_REV_20` and the exact `SKIN/Skin_053/theme.json` tokens.
