# SIGNALS — SKIN-001

## Identity
- Display name: SIGNALS
- Stable ID: `skin-001`
- Directory: `SKIN/Skin_001/`
- Role: independent additional theme (17th slot); never replaces an existing skin.
- Reference: supplied `01 INTERFACE  NEON STAGE DEFAULT .png` mockup.

## Art direction
Dark brushed-metal chassis, precision graphite panels, cyan/electric-blue neon edge accents and high-contrast typography. Reference geometry: top navigation; preset browser at left; central electric-guitar/graffiti hero; nine illuminated metal knobs; separate AMP & TONE module; seven FX modules; full-width MIDI keyboard; bottom MIDI/CPU/tempo/Sync status strip.

## Artwork inventory
| Asset | Dimensions | Purpose |
|---|---:|---|
| `assets/background/main.png` | 1920×1080 | Full console background |
| `assets/hero/hero.png` | 1600×900 | Hero artwork |
| `assets/preview.png` | 360×240 | Gallery preview |
| `assets/textures/brushed_graphite_1024.png` | 1024×1024 | Brushed graphite tile |
| `assets/controls/signals_controls_sheet.png` | 1024×512 | Navigation/control panel artwork |
| `assets/spritesheets/signals_knobs_9x3.png` | 1440×480 | 9 columns × 3 knob states; 160×160 cells |
| `assets/spritesheets/signals_meters_8frame.png` | 512×256 | 8 meter frames; 64×256 cells |
| `assets/fx_layers/signals_fx_7tile.png` | 1792×192 | 7 FX tiles; 256×192 cells |
| `svg/bezel.svg` | scalable | Chassis bezel |
| `svg/crest.svg` | scalable | SIGNALS crest |
| `svg/texture.svg` | scalable | Fine-line metal overlay |

## Technical contract
- PNG is the primary raster format; preserve alpha and lossless encoding for UI elements.
- Raster assets use sRGB. Downsample with high-quality filtering; do not upscale the gallery preview.
- Sprite atlases are row-major: knobs 9×3 (160 px cells), FX 7×1 (256×192), meters 8×1 (64×256).
- SVG is reserved for scalable overlays.
- Keep the canonical control IDs and `control_schema.json` bindings.
- Visual-only: no APVTS IDs, DSP, sampler, MIDI, presets, parameter ranges, or audio callback changes.
- Preserve all original 16 skins and stable IDs. `skin-053 / Skin_053` remains NEON STAGE DEFAULT and default.
- Registry/gallery selection, packaging, CI validation, Windows x64 build, CTest and FL Studio 20 host validation remain separate integration gates.

## Status
Artwork pack generated and manifest supplied in the downloadable package. Binary PNG upload to this repository and runtime integration are pending; this skin is not declared runtime-ready.
