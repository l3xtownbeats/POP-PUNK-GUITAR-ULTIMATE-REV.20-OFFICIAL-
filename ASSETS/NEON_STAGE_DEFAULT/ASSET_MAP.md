# NEON STAGE DEFAULT — production asset map

**Logical theme:** SKIN-1  
**Stable ID / registry index:** `skin-053` / `53`  
**Runtime source:** `SKIN/Skin_053/assets/`  
**Theme definition:** `SKIN/Skin_053/theme.json`

The approved production specification is `PPGU_REV20_NEON_STAGE_DEFAULT_ULTIMATE_ASSET_MASTER_PROMPT_RU.txt`. It defines the visual language, real control IDs, actual parameter names, auxiliary-window scope, state rules and export requirements. `Info.txt` and the REV.20 accepted-baseline documents override any older or experimental source.

## Existing canonical package inventory

The current `assets/asset_manifest.json` declares **307 records**, including:
- hero and preview artwork;
- master and runtime background/material/lighting layers;
- 135 master control-state images and 135 runtime control-state images for the 27-control state contract;
- top-bar icon masters/runtime assets and icon atlas/map;
- artwork and control-state manifests;
- source vector material artwork.

The actual directory currently contains additional files beyond manifest records (including sprite sheets and supporting assets). Always use the manifests as the authoritative file map; do not infer a file from its name alone.

## Requested folder taxonomy → canonical runtime source

| Requested group | Canonical source / handling |
|---|---|
| `Background/` | `assets/background/main.png`, `assets/master/background/`, plus `svg/texture.svg` |
| `Panels/` | Panel geometry and live content are composed by JUCE. Use the theme shell, material layers and relevant `svg/bezel.svg` / `svg/crest.svg`; do not invent five unrelated static panel screenshots. |
| `Controls/buttons/` | `assets/controls/` and `assets/master/controls/`; state names are in `control_states_manifest.json`. |
| `Controls/switches/` | The seven `fx_switch01…07` control-state families under `assets/controls/` and master equivalents. |
| `Controls/knobs/` | `knob01…knob09` state families; rotary atlas and sheet in `assets/spritesheets/`. |
| `Controls/sliders/` | `assets/spritesheets/neon_stage_meters_sliders_sheet.png` plus native JUCE slider rendering. |
| `FX_Layers/` | `assets/fx_layers/` (stage glow, edge highlight, specular, shadow); effect-specific live parameter panels are rendered in FX EDIT. |
| `Meters/` | Meter/slider sprite sheet and native live meter rendering. Dynamic levels must never be pre-rendered as fixed PNG values. |
| `Spritesheets/` | `assets/spritesheets/` and `assets/atlas/`; see `neon_stage_spritesheet_manifest.json` and atlas map. |
| `Icons/` | `assets/icons/` and the icon atlas/runtime sheet. |
| `Typography/` | Theme tokens in `theme.json`: Segoe UI semibold for UI and Consolas for technical/display values. Text stays live JUCE text, not raster artwork. |
| `Hero/` | `assets/hero.png`, `assets/hero/hero.png` and master artwork variants. |
| `Decorative/` | Material/vector artwork, shell bevel/crest, edge highlight and controlled stage glow. |
| `Textures/` | `assets/textures/material.png`, master material and `svg/texture.svg`. |
| `Keyboard/` | `midi_keyboard` control states plus live JUCE keyboard rendering. Keys 36–84 and note-down/hover states remain dynamic. |

## Locked visual and functional constraints

- Matte dark graphite / precision anodized metal; restrained cyan `#00D9FF` and electric-blue `#6B8CFF`.
- Default mode is minimal: no full-surface neon wash. Glow is opt-in for active/hover/focus/status states.
- Preserve all 27 control IDs and all five declared states: default, hover, pressed, disabled, dragged.
- Preserve exactly nine main rotary controls and seven main FX bypass switches.
- Preserve only MELODY and PATTERN as the two main modes. AUTOCHORDS is a PATTERN auxiliary window.
- Keep parameter labels, values, LCD text, LED activity, keyboard highlights and status text live.
- `Auto_Discover`, `Curator` and `About` must remain visually disabled while their backend is unavailable.
- FLANGER remains an FX EDIT group, not an eighth main FX switch.
- No APVTS, DSP, sampler, MIDI, preset, audio-callback or functional-layout changes are permitted as part of skin artwork work.

## Package integrity

Do not rename/move the canonical files to imitate the illustrative folder tree from the request. The map above provides the requested logical grouping while retaining the exact paths expected by REV.20 runtime and packaging.
