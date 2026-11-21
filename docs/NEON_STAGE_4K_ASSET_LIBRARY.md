# NEON STAGE — 4K asset library

## Absolute visual authority

`assets/POP_PUNK_GUITAR_ULTIMATE_BANNER.svg` is the immutable master sample. It is the 100% reference for the NEON STAGE layout: left brand stage, right instrument-console presentation, overall geometry, spacing, framing, visual hierarchy and proportions. This asset pack is a reusable component library for that exact visual identity; it is not a redesign, alternative skin or replacement layout.

The master banner is not modified by this commit.

## Canonical runtime palette

Runtime DEFAULT palette is sourced from `SKIN/Skin_053/theme.json` (NEON STAGE DEFAULT / skin-053): graphite, machined silver, purple, magenta and crimson. No blue, cyan, teal or turquoise is permitted in DEFAULT runtime artwork. The banner remains the immutable layout reference; the Skin_053 theme remains the runtime palette authority.

## 4K and aspect-ratio policy

The source banner is 1800×720 (5:2). Its undistorted 4K vector export is 3840×1536 (5:2). For a 3840×2160 UHD delivery canvas, center the complete 3840×1536 composition and letterbox vertically. Never stretch the 5:2 design to 16:9, crop the source composition, or alter the original banner's viewBox. SVG masters are resolution-independent; raster exports are derivatives.

## Included catalogues

- `neon_stage_4k_surfaces.svg`: stage background, instrument-console frame, panels, header/footer strips, cards, dividers and microtexture.
- `neon_stage_4k_controls.svg`: rotary control, button, toggle, slider/fader, tabs and selector states.
- `neon_stage_4k_indicators.svg`: LEDs, meter bars, signal trace, LCD frame, MIDI key shapes and status pill.
- `neon_stage_4k_details.svg`: brand mark, metal trim, screws, light line and decorative corner details.
- `neon_stage_default_tokens.json`: canonical Skin_053 colors and export restrictions.
- `neon_stage_4k_asset_manifest.json`: symbol catalogue, artboard sizes and verified GUI/APVTS mapping references.

## Binding and behavior contract

The assets are visual resources, not interactive controls. Existing native JUCE components continue to handle user input, accessibility, MIDI, meters and APVTS attachment. Verified visible parameter bindings are listed in the manifest and in `neon_stage_control_map.json`. No new UI control or APVTS parameter is created by this asset-only change. Decorative symbols are explicitly identified as decorative.

## States and effects

The control atlas provides default, hover, pressed and disabled variants where applicable. Dragged is a native interaction state: render it using the active control artwork plus the native component's live position/value; do not bake a fake dragged control into a static atlas. Glow is restrained and opt-in; default state remains visually restrained as required by Skin_053.

## Integration status

This commit adds and documents vector assets only. It does **not** claim that the new SVGs are loaded by `PluginEditor.cpp`, does not claim that the native editor now matches the master screenshot, and does not claim Windows build, CTest, pluginval or FL Studio 20 acceptance. Native integration and validation remain separate steps. No audio-thread work is introduced.
