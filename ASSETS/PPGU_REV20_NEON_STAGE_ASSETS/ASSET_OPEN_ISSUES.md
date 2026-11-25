# NEON STAGE DEFAULT — ASSET OPEN ISSUES

## Reference image — not visually reviewed
The exact repository reference `01 INTERFACE  NEON STAGE DEFAULT .png` has not been decoded/visually inspected in this session. Therefore exact geometry, proportions, spacing and pixel parity are not certified. The master prompt explicitly forbids inventing the mockup. Closure requires a directly viewable upload of the reference image and comparison with the 1024×700 editor.

## Existing asset inventory vs requested production deliverables
The canonical Skin-053 manifest contains 307 records. These include hero/preview, 2560×1440 background, material texture, four FX overlay layers, 135 master and 135 runtime control-state records, six topbar icon families/atlases, and three SVG shell layers. This is not the complete separate export inventory requested by the master prompt.

Completed in this increment:
- 16 separate scalable SVG panel frames: header, preset browser, playing core, amp/FX rack, performance strip, MIDI keyboard bay, status footer, guitar import, FX edit, pattern routing, AUTOCHORDS, workspace settings, skin gallery, and three dialog frames.

Outstanding deliverables:
- PPGU_SKIN053_BG_MAIN_1024x700.png
- PPGU_SKIN053_BG_GRAPHITE_TEXTURE.png
- PPGU_SKIN053_BG_ANODIZED_METAL.png
- PPGU_SKIN053_BG_BRUSHED_METAL.png
- PPGU_SKIN053_BG_LCD_DARK.png
- PPGU_SKIN053_BG_CONTROL_RECESSED.png
- PPGU_SKIN053_PANEL_HEADER.png
- PPGU_SKIN053_PANEL_PRESET_BROWSER.png
- PPGU_SKIN053_PANEL_PLAYING_CORE.png
- PPGU_SKIN053_PANEL_AMP_FX_RACK.png
- PPGU_SKIN053_PANEL_PERFORMANCE_STRIP.png
- PPGU_SKIN053_PANEL_MIDI_KEYBOARD_BAY.png
- PPGU_SKIN053_PANEL_STATUS_FOOTER.png
- PPGU_SKIN053_PANEL_IMPORT_GUITAR.png
- PPGU_SKIN053_PANEL_FX_EDIT.png
- PPGU_SKIN053_PANEL_PATTERN_ROUTING.png
- PPGU_SKIN053_PANEL_AUTOCHORDS.png
- PPGU_SKIN053_PANEL_WORKSPACE_SETTINGS.png
- PPGU_SKIN053_PANEL_SKIN_GALLERY.png
- PPGU_SKIN053_PANEL_DIALOG_BASE.png
- PPGU_SKIN053_PANEL_DIALOG_WARNING.png
- PPGU_SKIN053_PANEL_DIALOG_ERROR.png
- separate main rotary component layers for all 9 controls (BASE/RIM/FACE/POINTER/SCALE/GLOW)
- FX EDIT rotary component layers and parameter-specific scale overlays
- standalone per-state export for all required buttons and seven FX switches
- standalone LED state assets (OFF/ON/GLOW/WARNING/ERROR/SUCCESS/DISABLED)
- separate display frame assets (LCD empty/active/warning/error, numeric, harmony, notes-held, scale/key)
- individual white/black keyboard key states, separator, active-note overlay, and 49-key preview
- individual SVG icon family (41 icons × 16/24/32/48 sizes)
- hardware details as separate PNG/SVG assets
- button, FX toggle, LED, keyboard, meter and icon sprite atlases with extracted frames
- main interface previews 1024x700 and 1600x1100 and five contact sheets
- ZIP archive of the complete export package

## Sprite sheet manifest conflict
`SKIN/Skin_053/assets/spritesheets/neon_stage_spritesheet_manifest.json` identifies its project as `NEON_STAGE_MANAGER_3_0` and specifies base colors `#05070E`, `#00D2FF`, `#00E5FF`, `#6B8CFF`, `#FFB454`. PPGU REV.20 master prompt and `theme.json` define a different authoritative palette and PPGU product identity. Treat this manifest as unapproved for PPGU until reconciled; do not silently overwrite either source.

## Palette conflict
The master prompt specifies `danger #FF557A` and `warning #FFBE55`; `theme.json` currently specifies `danger #FF665E` and `warning #FFB454`. The theme manifest is currently consumed by runtime; product owner must decide whether to update the theme tokens or amend the prompt. Until resolved, preserve runtime tokens and do not create new semantic-color assets from the conflicting values.

## Export state
No binary assets were copied into this export directory in this step. Existing source assets remain under `SKIN/Skin_053/`. No ZIP, contact sheets, or 1024×700/1600×1100 final previews are claimed. Do not mark the pack COMPLETE.


## Vector-atlas source QA — 2026-11-26
A static source-structure pass was performed on the five supplemental SVG atlas masters. It is not a rendered/pixel-level visual QA pass and does not certify PNG exports or runtime compatibility.

- All five files declare explicit SVG dimensions and matching viewBox dimensions: 1920×1000, 1920×1020, 1920×8000, 1920×1040 and 1920×1020.
- The button sheet declares the intended 27 families × 5 states (135), plus seven FX switch pairs and five LED colors × two states. This is a source-structure check, not a per-pixel state-art review.
- The rotary sheet contains three 61-frame vertical strips (183 frames total) with 128px vertical pitch and 3° needle increments from 210° through 390°. The large sheet still requires rasterization and frame-by-frame visual inspection for clipping, cell alignment and animation continuity.
- The icon sheet was corrected in this pass: the prior 35 glyph bodies were duplicate plus-sign placeholders. They have been replaced by 35 distinct vector glyph bodies matching the declared icon names. The SVG source was re-fetched and checked for 35 icon groups, 35 distinct glyph bodies and all 35 labels.
- The display/keyboard sheet is still a compact two-octave 24-white-key atlas, not the final 49-key preview/export requested by the master prompt.
- The atlas files remain supplemental vector masters. No PNG export, preview/contact sheet, ZIP package, pixel-level approval, or runtime registration is claimed.

### Next required QA gates
1. Render all five SVGs with a pinned renderer/version and transparent-background policy.
2. Inspect full-sheet previews and cropped cells at 100% and 200%; correct clipping, repeated/incorrect glyphs, text overflow and inconsistent visual weight.
3. Export standalone assets and atlases at the exact sizes required by the master prompt; record dimensions, byte counts and SHA-256 in the canonical manifest.
4. Integrate only assets that pass visual QA and have a verified JUCE consumer; then run Windows x64 build, CTest, Pluginval and FL Studio 20 host acceptance.


Additional source-preparation changes in the same pass:
- Removed the opaque full-sheet black canvas rectangle from all five SVG masters. The atlas canvases are now transparent at source level; individual background/material swatches remain as explicit artwork elements.
- Added `tools/validate_neon_stage_vector_atlases.py`, a standard-library structural validator for XML validity, declared dimensions/viewBoxes, transparent canvas, 27 button-family headings, 3×61 rotary frame positions/angles, and 35 distinct icon glyphs.
- Documented the supplemental atlas format and validator command in `README_ASSET_PACK_RU.md`.

The validator has been added but has not yet been executed in a repository runner. Its PASS output must not be assumed until it runs. Raster export and visual QA remain open.


### 49-key keyboard completion — 2026-11-26
The keyboard area in atlas 04 was replaced with a four-octave 49-key layout (29 white + 20 black) and C/E/G active overlays. The canonical NEON STAGE manifest and structural validator were updated to match. This is still atlas artwork only; it does not change the live JUCE keyboard's key count or behavior.

### Automated raster-export path — 2026-11-26
Added a pinned CairoSVG/Pillow export script and a dedicated GitHub Actions workflow. The workflow validates source contracts, exports transparent RGBA PNG atlases and three rotary frame-strip crops, creates a contact-sheet preview and records SHA-256 values. Visual acceptance remains a human review gate; the workflow has not yet been observed completing successfully.
