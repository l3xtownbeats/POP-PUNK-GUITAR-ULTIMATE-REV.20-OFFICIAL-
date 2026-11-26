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
No binary assets were committed into this export directory in this step. The new CI workflow is designed to produce downloadable PNG/contact-sheet artifacts from the supplemental SVG masters. Existing canonical runtime assets remain under `SKIN/Skin_053/`. No ZIP or 1024×700/1600×1100 final interface previews are claimed. Do not mark the pack COMPLETE.


## Vector-atlas source QA — 2026-11-26
A static source-structure pass was performed on the five supplemental SVG atlas masters. It is not a rendered/pixel-level visual QA pass and does not certify PNG exports or runtime compatibility.

- All five files declare explicit SVG dimensions and matching viewBox dimensions: 1920×1000, 1920×1020, 1920×8000, 1920×1040 and 1920×1020.
- The button sheet declares the intended 27 families × 5 states (135), plus seven FX switch pairs and five LED colors × two states. This is a source-structure check, not a per-pixel state-art review.
- The rotary sheet contains three 61-frame vertical strips (183 frames total) with 128px vertical pitch and 3° needle increments from 210° through 390°. The large sheet still requires rasterization and frame-by-frame visual inspection for clipping, cell alignment and animation continuity.
- The icon sheet was corrected in this pass: the prior 35 glyph bodies were duplicate plus-sign placeholders. They have been replaced by 35 distinct vector glyph bodies matching the declared icon names. The SVG source was re-fetched and checked for 35 icon groups, 35 distinct glyph bodies and all 35 labels.
- The display/keyboard atlas now contains a full 49-key layout (29 white + 20 black keys) and C/E/G active overlays. Standalone key-state assets and a separately composed 49-key preview remain outstanding.
- The atlas files remain supplemental vector masters. The deterministic PNG export script and CI workflow have now been added, but a successful run/artifact has not yet been verified. No pixel-level approval, ZIP package, or runtime registration is claimed.

### Next required QA gates
1. Render all five SVGs with a pinned renderer/version and transparent-background policy.
2. Inspect the CI-generated full-sheet previews and cropped cells at 100% and 200%; correct clipping, repeated/incorrect glyphs, text overflow and inconsistent visual weight.
3. Export standalone assets and atlases at the exact sizes required by the master prompt; record dimensions, byte counts and SHA-256 in the canonical manifest.
4. Integrate only assets that pass visual QA and have a verified JUCE consumer; then run Windows x64 build, CTest, Pluginval and FL Studio 20 host acceptance.


Additional source-preparation changes in the same pass:
- Removed the opaque full-sheet black canvas rectangle from all five SVG masters. The atlas canvases are now transparent at source level; individual background/material swatches remain as explicit artwork elements.
- Added `tools/validate_neon_stage_vector_atlases.py`, a standard-library structural validator for XML validity, declared dimensions/viewBoxes, transparent canvas, 27 button-family headings, 3×61 rotary frame positions/angles, and 35 distinct icon glyphs.
- Documented the supplemental atlas format and validator command in `README_ASSET_PACK_RU.md`.

The validator and raster exporter have been added but have not yet been observed completing in a repository runner. Their PASS output and PNG artifacts must not be assumed until the workflow completes. Pixel-level visual QA remains open.


### 49-key keyboard completion — 2026-11-26
The keyboard area in atlas 04 was replaced with a four-octave 49-key layout (29 white + 20 black) and C/E/G active overlays. The canonical NEON STAGE manifest and structural validator were updated to match. This is still atlas artwork only; it does not change the live JUCE keyboard's key count or behavior.

### Automated raster-export path — 2026-11-26
Added a pinned CairoSVG/Pillow export script and a dedicated GitHub Actions workflow. The workflow validates source contracts, exports transparent RGBA PNG atlases and three rotary frame-strip crops, creates a contact-sheet preview and records SHA-256 values. Visual acceptance remains a human review gate; the workflow has not yet been observed completing successfully.


### First rendered PNG visual-QA pass — 2026-11-26
The first successful CI render produced five transparent RGBA PNG atlases and three separate 61-frame rotary strips. Inspection exposed defects not detectable by source-structure checks: carbon-weave strokes escaped their swatch, the three rotary columns were visually near-identical despite different style names, and a green meter sample overlapped the status/keyboard area. Corrections now clip the weave, give the black-disc and knurled-steel strips distinct materials, replace the stray meter with a 12-segment cyan/blue sample, and reduce long icon-label size. The corrected revision requires a fresh render and review before artwork acceptance.

Initial export CI run `45696342834`, artifact `15061271846`, predates these corrections and is not the final pack.


### Corrected 1x/2x PNG export and manual review — 2026-11-26
The corrected source passed the structural validator and both 1x and 2x CairoSVG raster exports. GitHub Actions run `45697271165` completed successfully and uploaded artifact `15062120847` (17,491,765 bytes; SHA-256 `d4f5ec747eb0b85df7a2d01a0cca474fe8a8b1bfcee7dffddb5f0466b1872995`). The artifact contains five transparent RGBA PNG atlases at native dimensions and at 2x, three separate rotary strips at both scales, two contact sheets and two SHA-256 export reports. Manual review of contact sheets and full-size 1x images confirmed the carbon-weave clipping, distinct rotary materials, corrected meter placement and full 49-key keyboard. This is a partial visual pass, not exhaustive per-pixel review of all 135 button states and 183 rotary frames.

See `NEON_STAGE_ATLAS_EXPORT_CI_REPORT.json` for dimensions, hashes and remaining gates. Runtime JUCE integration, VST3/Pluginval validation on the current final head and FL Studio 20 acceptance remain open.

### Runtime integration and current validation — 2026-11-26

The earlier status above is historical. The following work has since completed on PR #20 head `adb1e26a2dad4d0bc96fb075202f35c4fc8c0489`:

- The corrected SVG atlas export was verified in GitHub Actions run `45697271165`; downloadable 1x/2x outputs are recorded above.
- The three rotary families are now represented in the generated runtime artwork: the original conical-chrome family plus dedicated 61-frame black-disc and knurled-steel atlases for FX EDIT. The two FX EDIT atlases are 1024×1024, 8×8 cells, 128×128 per cell, with 61 valid frames covering 210°–390° in 3° steps.
- `ThemeManager` loads the two FX EDIT atlases; the editor selects black-disc for compressor group 0 and knurled-steel for EQ group 1. The package stage includes the generated sheets in Skin_053. Existing APVTS parameter ranges and IDs remain unchanged.
- Automated validation was extended to check the additional runtime sheets and their geometry.

Current CI evidence on head `adb1e26a2dad4d0bc96fb075202f35c4fc8c0489`:
- NEON STAGE native integration CI run `45698878074`: generator, CMake configure, build, full CTest, registry/skin validation and package stages passed.
- SKIN-1 control-state runtime CI run `45698877634`: passed.
- Windows x64 VST3 validation run `45698878057`: build, tests, package and Pluginval strictness 5 passed.
- A Windows x64 VST3 package was produced as artifact `15062258237`.

These results supersede the earlier statements that the raster export and current-head Windows build/Pluginval had not yet been verified. They do **not** close the following acceptance gates:

1. The canonical repository reference `01 INTERFACE  NEON STAGE DEFAULT .png` has not yet been visually decoded in this session. Exact pixel geometry and parity therefore remain unverified.
2. The full standalone component export inventory listed above remains incomplete; the successful atlas export is a partial deliverable, not a complete asset pack.
3. The SVG supplemental atlas work has only partial visual review. The 135 button-state records and all 183 rotary frames have not each received exhaustive 100%/200% review.
4. FL Studio 20 manual host acceptance, including clean install, project save/reopen, automation, sustained playback and performance measurements, remains NOT RUN / NOT CONFIRMED.

Do not mark the asset pack or REV.20 release as COMPLETE until these gates are closed. The canonical visual reference is still required before any claim of pixel-perfect matching or geometry changes based solely on visual inference.
