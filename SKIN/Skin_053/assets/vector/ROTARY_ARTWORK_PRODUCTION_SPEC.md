# NEON STAGE — production control artwork source

## Canonical visual reference
- Main approved composition: `/01 INTERFACE  NEON STAGE DEFAULT .png` (repository root; do not replace or reinterpret).
- Skin: `SKIN/Skin_053` / `skin-053`.
- Palette anchor: graphite `#05070E`, metal border `#00D2FF`, cyan glow `#00E5FF`, blue glow `#0048FF`; warning amber only for warning/error.
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
