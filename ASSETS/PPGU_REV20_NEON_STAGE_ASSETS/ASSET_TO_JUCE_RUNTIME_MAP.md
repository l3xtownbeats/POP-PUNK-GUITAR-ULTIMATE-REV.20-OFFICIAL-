# NEON STAGE — карта asset → JUCE runtime

Статус: **PARTIAL / проверяемая карта текущего кода**, не декларация полной интеграции.
Каноническая тема: `SKIN/Skin_053/theme.json` — `skin-053 / NEON STAGE DEFAULT`.
Карта составлена по `Source/PluginEditor.cpp`, `Source/PluginEditor.h`, `Source/UI/ThemeManager.cpp`, `Source/UI/ThemeManager.h` и theme manifest на ветке PR #29.

## 1. Основные девять регуляторов

Порядок и APVTS IDs из `PluginEditor.h`:

| Индекс | UI label | APVTS ID | Component ID | Artwork path / runtime source |
|---:|---|---|---|---|
| 1 | GAIN | `ampGain` | `knob1` | `assets/spritesheets/neon_stage_main_knob_layers_atlas.png`, column 0 |
| 2 | TREBLE | `eqHigh` | `knob2` | тот же atlas, column 1 |
| 3 | MID | `eqMid` | `knob3` | тот же atlas, column 2 |
| 4 | BASS | `eqLow` | `knob4` | тот же atlas, column 3 |
| 5 | VELOCITY | `velocity` | `knob5` | тот же atlas, column 4 |
| 6 | DYNAMICS | `dynamics` | `knob6` | тот же atlas, column 5 |
| 7 | SWING | `swing` | `knob7` | тот же atlas, column 6 |
| 8 | HUMANIZE | `humanize` | `knob8` | тот же atlas, column 7 |
| 9 | ACCENT | `accent` | `knob9` | тот же atlas, column 8 |

Main-knob layer atlas contract in the renderer: 128×128 cells, 9 columns × 6 rows. Layer rows: BASE, RIM, FACE, POINTER, SCALE, GLOW. Renderer paints BASE → GLOW → RIM → FACE → SCALE; POINTER is drawn live from the continuous slider value. The runtime loader expects a PNG of 1152×768. The main-knob paint path does not quantize APVTS values.

## 2. FX EDIT rotary controls

The theme loader reads three dedicated 1024×1024 sprite sheets from `theme.json`:

- `assets/spritesheets/neon_stage_rotary_61frame_atlas.png`
- `assets/spritesheets/neon_stage_rotary_black_disc_61frame_atlas.png`
- `assets/spritesheets/neon_stage_rotary_knurled_steel_61frame_atlas.png`

Renderer chooses material sheet by component ID prefix: `FXEdit_0_` → black-disc; `FXEdit_1_` → knurled-steel; other FX EDIT rotary controls → default rotary. The expected runtime sheet is 8×8 cells, each 128×128, 61 authored positions. Frame index is `round(normalizedValue × 60)`; APVTS value remains continuous. This is the runtime contract currently in code.

**Integration gap:** the new supplemental vector atlas `03_ppgu_atlas_knob_strips.svg` is a 1920×8000 master with three vertical 61-frame strips. Its CI standalone strip exports are 128×7808. That is not itself the 1024×1024 runtime sprite sheet. A dedicated packing/conversion step and source-to-runtime visual QA are required before replacing the current three runtime PNGs. Do not copy the full 1920×8000 master to any runtime path.

## 3. Seven FX switches

Order and APVTS IDs from `PluginEditor.h`:

1. COMPRESSOR — `compressorOn`
2. EQ — `eqOn`
3. DISTORTION — `distortionOn`
4. CHORUS — `chorusOn`
5. DELAY — `delayOn`
6. REVERB — `reverbOn`
7. CABINET IR — `cabinetOn`

Theme control artwork families are `fx_switch01` … `fx_switch07`; each family has default/hover/pressed/dragged/disabled state PNGs in the existing Skin_053 controls directory. The SVG atlas 02 provides source-state artwork, but per-family crops must be matched to the existing control manifest and loader before replacing runtime files.

## 4. Theme runtime sprite-sheet contract

From `SKIN/Skin_053/theme.json` and `ThemeManager.cpp`:

| Theme key | Relative PNG | Required dimensions |
|---|---|---:|
| controls | `assets/spritesheets/neon_stage_controls_spritesheet.png` | 1024×1024 |
| meters_sliders | `assets/spritesheets/neon_stage_meters_sliders_sheet.png` | 1024×1024 |
| frames_panels | `assets/spritesheets/neon_stage_frames_panels_sheet.png` | 1024×1024 |
| icons | `assets/spritesheets/neon_stage_icons_sheet.png` | 1024×1024 |
| rotary | `assets/spritesheets/neon_stage_rotary_61frame_atlas.png` | 1024×1024 |
| rotary_black_disc | `assets/spritesheets/neon_stage_rotary_black_disc_61frame_atlas.png` | 1024×1024 |
| rotary_knurled_steel | `assets/spritesheets/neon_stage_rotary_knurled_steel_61frame_atlas.png` | 1024×1024 |
| main_knob_layers | `assets/spritesheets/neon_stage_main_knob_layers_atlas.png` | 1152×768 |

The runtime loader rejects incorrect sheet dimensions. Keep paths and dimensions synchronized with the theme manifest and loader contract.

## 5. Required next integration gates

- [ ] Export exact-head SVG atlas PNGs and inspect all three rotary materials at 0/25/50/75/100%.
- [ ] Pack the three vertical rotary strips into the exact 8×8 runtime sheets (61 cells + 3 empty cells), 1024×1024 RGBA, correct row-major frame order.
- [ ] Verify alpha bounds, no clipped highlights, identical static rim/face/scale across frames, and marker-only movement where required.
- [ ] Compare packed 61-frame sheets with source reference crops and existing runtime PNGs before replacement.
- [ ] Verify all nine main-knob six-layer atlas cells against the 1152×768 loader contract.
- [ ] Match atlas 02 button/switch crops to existing state manifest; preserve stable component IDs and APVTS IDs.
- [ ] Capture JUCE editor screenshots at 900×640, 1024×700 and 1600×1100; perform overlay/difference review.
- [ ] Run exact-head Windows x64 VST3 build, CTest, Pluginval strictness 5 and manual FL Studio 20 acceptance.

## 6. Status discipline

CI export success proves that source masters can be validated and rasterized. It does not prove that the newly exported PNGs are installed in Skin_053, loaded by ThemeManager, visually accepted, or verified in a DAW host. Mark each gate independently.


## 7. Exact-head export and first visual QA — 2026-11-28

- GitHub Actions run #177 completed successfully on branch head 8dbea7b3edbc199c765b2bcf28a5bd9eb817d890.
- Artifact: PPGU-NEON-STAGE-SVG-ATLAS-EXPORT, artifact ID 15232889173, archive size 79,318,951 bytes; SHA-256 7f302e6c38721b2cbc9dc8ee0a65a766d57a87c8a98e5f3bde5ffb5716319738.
- Confirmed fresh 1× and 2× raster outputs, 490 standalone components at each scale, 41 SVG icon families, 70 source-reference crops, nine six-layer main knobs and three 61-frame rotary strips. All workflow steps passed.
- All three fresh rotary strips decode as RGBA, exactly 128×7808 (61 frames × 128 px).

**Visual QA result: NOT ACCEPTED against the approved rotary reference yet.** The new raster does render, including its radial-brush reusable layer, but direct inspection against reference_components_1x/knobs/rotary_50_percent.png shows material differences:
1. The reference has a prominent cyan segmented arc concentrated across roughly three quarters of the upper/left perimeter; the current export distributes small cyan segments around the full circumference.
2. The reference's bright cyan position marker is near 12 o'clock at the 50% reference state; the current frame 30 marker is visibly left of top.
3. The face/rim treatment is still a reconstruction and does not yet reproduce the reference's polished bright radial-metal face and stronger cyan arc.

Therefore the export pipeline is PASS, but rotary visual acceptance and runtime integration remain BLOCKED. Do not pack or replace the three JUCE runtime rotary sheets from this iteration. Correct the LED arc geometry/progression and marker angle against the reference, rerun exact-head CI, then compare all 0/25/50/75/100% positions before packing. This finding supersedes any earlier implication that the rotary artwork was visually accepted.
