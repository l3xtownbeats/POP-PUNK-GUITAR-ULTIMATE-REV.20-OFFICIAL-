# REV.20 — EXACTLY 16 APPROVED PREMIUM GRAPHICAL SHELLS

**Locked product count: 16 total. No more and no less.**

- **SKIN-1 — NEON STAGE DEFAULT** is the principal/default shell and the visual identity of the plugin.
- **SKIN-2 through SKIN-16** are the only 15 additional approved premium shells.
- All 16 names and identities are fixed. Do not generate replacement names, extra themes, legacy galleries or 50/102-theme packs.
- Logical ordinals 1…16 are separate from immutable source IDs/indices.

| Logical ordinal | Approved name | Stable ID | Stable index | Artwork assets in REV.20 |
|---:|---|---|---:|---|
| SKIN-1 | NEON STAGE DEFAULT | `skin-053` | 53 | Preview + hero + SVG layers |
| SKIN-2 | OBSIDIAN GOLD | `skin-103` | 103 | Preview + hero + SVG layers |
| SKIN-3 | CARBON FORGE | `skin-104` | 104 | Preview + hero + SVG layers |
| SKIN-4 | MIDNIGHT CRIMSON | `skin-105` | 105 | Preview + hero + SVG layers |
| SKIN-5 | ARCTIC PLATINUM | `skin-106` | 106 | Preview + hero + SVG layers |
| SKIN-6 | VIOLET NOIR | `skin-107` | 107 | Preview + hero + SVG layers |
| SKIN-7 | TITANIUM STORM | `skin-108` | 108 | Preview + hero + SVG layers |
| SKIN-8 | EMERALD CIRCUIT | `skin-109` | 109 | Preview + hero + SVG layers |
| SKIN-9 | SOLAR FLARE | `skin-110` | 110 | Preview + hero + SVG layers |
| SKIN-10 | DEEP OCEAN | `skin-111` | 111 | Preview + hero + SVG layers |
| SKIN-11 | ROSE CHROME | `skin-112` | 112 | Preview + hero + SVG layers |
| SKIN-12 | DESERT AMBER | `skin-113` | 113 | Preview + hero + SVG layers |
| SKIN-13 | GLACIER TEAL | `skin-114` | 114 | Preview + hero + SVG layers |
| SKIN-14 | PHANTOM GRAPHITE | `skin-115` | 115 | Preview + hero + SVG layers |
| SKIN-15 | ULTRAVIOLET DRIVE | `skin-116` | 116 | Preview + hero + SVG layers |
| SKIN-16 | VOLCANIC STEEL | `skin-117` | 117 | Preview + hero + SVG layers |

## Design basis and provenance

- PR #43 (merged 2026-11-15) is the source integration checkpoint for NEON STAGE DEFAULT / SKIN-1 / `skin-053`.
- The completed 16-theme artwork source is draft PR #58, branch `work/approved-16-skins-completion`, source SHA `10e590c8a3fdfed90cc7ae05e0ff74d8875ac88a`.
- Every additional theme has its own individual art direction, 21-token palette and three distinct SVG foundations: texture, bezel and crest.
- The source artwork workflow passed strict checks for the exact 16-theme registry and all artwork assets. All 15 preview images were visually reviewed; ARCTIC PLATINUM / GLACIER TEAL and VIOLET NOIR / ULTRAVIOLET DRIVE were specifically differentiated.
- Source Windows x64 build and full CTest passed on the same source SHA, together with strict 16-skin asset/registry validation and 16-only package staging. This is source-branch evidence, not REV.20 exact-SHA host acceptance.

## Runtime and safety contract

- Only these 16 skins may appear in the product gallery. Logical labels are SKIN-1…SKIN-16.
- Stable IDs/indices must never be parsed as logical ordinal numbers.
- Theme changes are visual-only. Preserve the 27 required control IDs, seven approved FX bypass IDs, APVTS, DSP, sampler, MIDI, presets, functional geometry and audio callback.
- Preserve the shared NEON STAGE component language and the same control semantics across all 16.
- No fake controls, hidden extra themes, legacy theme batches or accidental duplicate gallery entries.
- Source CI evidence does not make skins HOST-VERIFIED in REV.20. Runtime loader, 16-only package, preview/apply/cancel/persistence, hot-swap, ECO/memory behaviour, DPI 100/125/150%, pluginval strictness 5 and FL Studio 20 checks must pass against the exact REV.20 SHA before marking all 16 runtime-ready.

**Current REV.20 asset/runtime state:** all 16 names/manifests are defined; all 30 additional PNGs are included; all 48 SVG texture/bezel/crest layers decode in the REV.20 ThemeManager test; exact-SHA Windows x64 build, full CTest, PNG/registry validation and 16-only package staging passed on SHA `8cfd11ecce3c8039360c1c194be5251e716c9015` (run `44717722638`). All 16 skins are runtime-ready/selectable. FL Studio 20 host acceptance, pluginval strictness 5, DPI/hot-swap and performance acceptance remain separate.


## 2026-11-19 — Global premium-quality standard (newest approval)

NEON STAGE is the quality and premium-finish benchmark for all 15 additional themes. Each theme must look equally expensive, polished, modern, stylish and commercially competitive, but must have its own original visual identity. Match quality, not NEON STAGE's exact palette, layout, motifs or artwork.

### SKIN-2 — OBSIDIAN GOLD

The 2026-11-19 approved OBSIDIAN direction is premium/luxury: deep obsidian, graphite, satin black metal, brushed/polished metal, refined typography, precise control surfaces and restrained metallic highlights. No acid-neon palette, loud saturated glow or cyberpunk/gamer styling. The current logical name OBSIDIAN GOLD remains unchanged; the approved distinction is its visual identity, not a new theme slot.

These are design approvals with runtime readiness separately verified on REV.20. Preserve the 27-control parity, nine rotary bindings, seven approved FX bypass IDs and all real UI/functionality restrictions.


## Runtime gate passed — 2026-11-20

All 16 approved shells are now selectable in REV.20. Exact target workflow 44717722638 passed Windows x64 VST3 build, full CTest, ThemeManager load and three SVG-layer decode for all themes, all 32 PNG CRC/dimension checks, registry validation and 16-only package staging. Only manual host and release gates remain.


## NEON STAGE DEFAULT sprite atlas package — 2026-11-20

SKIN-1 / `skin-053` now declares four 1024x1024 transparent PNG atlases under `Skin_053/assets/spritesheets/`:

- `neon_stage_controls_spritesheet.png`: eight rotary frames, OFF/ON toggle art and normal/hover/pressed/active button states. Rotary and button backgrounds are consumed by the JUCE LookAndFeel; parameter values and button bindings remain native.
- `neon_stage_meters_sliders_sheet.png`: eight-segment VU samples, long/short slider artwork and round/square status LED states.
- `neon_stage_frames_panels_sheet.png`: 9-slice corners, borders, dividers, header bars and display grid.
- `neon_stage_icons_sheet.png`: seven FX and ten navigation icons.

The source-of-truth layout and bounding boxes are recorded in `neon_stage_spritesheet_manifest.json`. Regenerate with `python tools/generate_neon_stage_spritesheets.py` (requires Pillow), then run `python tools/validate_skin_registry_16.py`. The generator is also run by the Windows x64 VST3 workflow before compilation and package staging. The sprite atlases are visual-only and do not change the APVTS, DSP, sampler, MIDI, preset catalogue, control geometry or audio callback.


## Extended per-skin artwork layers (REV.20 runtime)

- The shared theme runtime accepts optional `assets.controls`, `assets.fxLayers`, and `assets.decorative` SVG paths. Each declared SVG is sandbox-validated and decoded on the UI thread; missing optional paths preserve compatibility with earlier theme packages.
- `fxLayers` and `decorative` are now authored and registered for SKIN-5 through SKIN-16 (stable IDs `skin-106`…`skin-117`). Their palette-specific accents are rendered by the shared shell without changing component geometry, control IDs, APVTS, DSP, MIDI, or sampler behavior.
- The optional `controls` SVG slot is reserved for per-skin vector control atlases. Existing NEON STAGE sprite atlases remain the fully authored control-state package; other themes still use the shared vector control renderer until their control atlas art is added.
- These additions are source-level artwork integration only. No build, CI, host acceptance, or installer validation was run as part of this work.
