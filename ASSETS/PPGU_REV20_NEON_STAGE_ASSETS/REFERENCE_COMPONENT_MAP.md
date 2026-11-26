# NEON STAGE — reference component extraction map

**Product:** POP PUNK GUITAR ULTIMATE REV.20 / SKIN-1 / `skin-053`  
**Purpose:** traceable crop map from detailed source-reference sheets to individual review assets.  
**Status:** reference extraction pipeline added; crops are review/source material, not yet approved JUCE runtime assets.

## Source sheets

| Source file | Role | Original size |
|---|---|---:|
| `Assets/3D/References/Meshy_AI_neon_stage_buttons_and_switches.png` | button face materials, button states, mode tabs, toggles, actions and status LEDs | 1536×864 RGBA |
| `Assets/3D/References/Meshy_AI_neon_stage_knobs_and_meters (1).png` | rotary examples, mini amp knobs, slider rails/thumbs, progress bars and level meters | 1536×864 RGBA |

The extractor records each source SHA-256, crop rectangle `[x0,y0,x1,y1]`, exported dimensions, byte size and SHA-256 in `PPGU_REFERENCE_COMPONENT_CROP_MANIFEST.json`. The generated archive contains source-faithful 1× crops and 2× LANCZOS review enlargements. The 2× files are not native 2× artwork and do not add detail.

## Extracted component groups

| Group | Unique crops | Contents |
|---|---:|---|
| FX chain card | 5 | Compressor reference card: normal, hover, pressed, active, disabled |
| Major/Minor/Custom selectors | 6 | three normal and three active button treatments |
| Rhythm selectors | 6 | Strum, Arp, Latch normal/active treatments |
| Mode buttons | 6 | MELODY and PATTERN normal/active; PUNK GROUP pair marked reference-only |
| Toggles and action buttons | 4 | ON/OFF toggle, Apply All, Load Library |
| Status LEDs | 4 | green ON, red ERROR, cyan ACTIVE, gray OFF |
| Rotary controls | 9 | five positions (0/25/50/75/100%) and four mini amp-style knob examples |
| Slider components | 10 | five horizontal slider examples and five thumb styles |
| Meters/progress | 8 | two vertical meters, five horizontal progress/meter styles and one multicolor segment strip |
| Individual meter segments | 12 | separate vertical segment crops from the multicolor strip |
| **Total** | **70** | **140 PNGs across 1× and 2×** |

## Important separation from the current SVG atlas drafts

`02_ppgu_atlas_buttons_switches.svg` and `03_ppgu_atlas_knob_strips.svg` remain the generated vector-sheet masters and their PNG exports. Those sheets define geometry/count contracts, but the detailed source-reference crops above preserve richer button/knob visual treatments. The crop pipeline does not silently replace the vector masters or assert that every reference sample is a valid REV.20 runtime control.

## Runtime safety and mapping rules

- Static source references may include fixed words, state labels, numeric scales or other baked text. The crop manifest flags these with `baked_text_or_scale=true`; such files must not replace JUCE live text/value layers.
- The PUNK GROUP controls are present in a reference image but are not promoted to a third REV.20 top-level mode.
- Compressor card samples are visual examples, not seven independent FX button families. The seven real REV.20 FX bindings remain authoritative.
- Rotary poses are visual examples, not 61-frame animated strips. The SVG 61-frame rotaries remain a separate source family pending detailed visual matching.
- The 12 individual level-segment crops are source artwork only. Runtime meters must display real processor telemetry, not pre-rendered values.
- Every crop requires a pixel-edge review at 100% and 200%, then a source-to-runtime mapping and hit-region check before JUCE registration.
- Preserve APVTS IDs, parameter values, audio/DSP, MIDI routing and processor contracts. Do not create controls simply because a reference sheet contains an example.

## Pipeline

Run locally or in CI:

```bash
python tools/extract_neon_stage_reference_components.py \
  --buttons "Assets/3D/References/Meshy_AI_neon_stage_buttons_and_switches.png" \
  --knobs "Assets/3D/References/Meshy_AI_neon_stage_knobs_and_meters (1).png" \
  --output build/neon_stage_reference_components
```

The output includes:
- `reference_components_1x/` and `reference_components_2x/`;
- `PPGU_REFERENCE_COMPONENT_CROP_MANIFEST.json`;
- `PPGU_REFERENCE_COMPONENTS_CONTACT_SHEET.jpg`;
- `PPGU-NEON-STAGE-REFERENCE-COMPONENTS.zip`;
- `README_RU.txt`.

**Acceptance status:** source-faithful crop export only. Visual parity, native-resolution master reconstruction, runtime integration and FL Studio 20 host acceptance remain open.
