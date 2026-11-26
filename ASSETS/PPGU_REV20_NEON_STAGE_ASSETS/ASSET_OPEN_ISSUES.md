# NEON STAGE DEFAULT — ASSET OPEN ISSUES

## Reference handling — owner clarification (2026-11-26)
The owner explicitly excluded the repository-root image `01 INTERFACE  NEON STAGE DEFAULT .png` from the required visual reference set. It must not block asset production or be requested again. The visual reference set for this work is the stored PPGU mockup collection named:
- `Неоновый атлас UI-ассетов PPGU`
- `Неоновый интерфейс PPGU — поп-панк гитара`
- `Неоновый интерфейс гитарного плагина PPGU`

Use the stored mockups and the development journal as the visual/design evidence. Where older mockups disagree with the current REV.20 runtime contract (control names/count, panel availability, parameter semantics), preserve the current REV.20 source contract and record the discrepancy; do not silently copy obsolete REV.18 labels or behavior. Exact visual acceptance is based on the applicable stored mockup(s), source contract and a rendered JUCE comparison, not on the excluded repository-root image.

## Existing asset inventory vs requested production deliverables
The canonical Skin-053 manifest contains 307 records. These include hero/preview, 2560×1440 background, material texture, four FX overlay layers, 135 master and 135 runtime control-state records, six topbar icon families/atlases, and three SVG shell layers. This is not the complete separate export inventory requested by the master prompt.

Completed in this increment:
- 16 separate scalable SVG panel sources: seven main-console frames (header, preset browser, playing core, amp/FX rack, performance strip, MIDI keyboard bay, status footer); six auxiliary layouts with static guide text/control placeholders (guitar import, FX EDIT, pattern routing, AUTOCHORDS, workspace settings, skin gallery); and three dialog frames. The main-console and dialog files are primarily structural shells. Auxiliary guides are not finished interactive windows and do not replace live JUCE controls.

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
- FX EDIT rotary component layers and parameter-specific scale overlays
- remaining button/switch state work: current CI exports 27 button families × 5 states and seven dedicated FX OFF/ON pairs; the additional focus semantics, per-control source crop mapping and final runtime visual review are still open
- standalone LED state assets (OFF/ON/GLOW/WARNING/ERROR/SUCCESS/DISABLED)
- full display-state set (10 separate display/frame samples are exported; verify exact LCD empty/active/warning/error, numeric, harmony, notes-held and scale/key mapping and JUCE runtime states)
- keyboard hover/pressed states plus the final composed 49-key preview (neutral white/black keys and three separate active C/E/G overlays are already exported)
- additional hardware details beyond the current 13 exported 1x/2x component parts, with exact source-to-runtime mapping and visual approval
- button, FX toggle, LED, keyboard, meter and icon sprite atlases with extracted frames
- main interface previews 1024x700 and 1600x1100 and five contact sheets
- ZIP archive of the complete export package

## Sprite sheet manifest identity/palette conflict — resolved 2026-11-26
The old sprite generator/manifest used `NEON_STAGE_MANAGER_3_0` and a separate palette (`#05070E`, `#00D2FF`, `#00E5FF`, `#6B8CFF`, `#FFB454`). This was not the PPGU REV.20 runtime palette. The conflict is now resolved in the source generator, checked-in sprite manifest and `tools/validate_skin_registry_16.py`:
- project identity: `POP_PUNK_GUITAR_ULTIMATE_REV_20`;
- background: `#080B14`;
- panel: `#101827`;
- raised panel: `#17243A`;
- control border: `#31506F`;
- cyan accent: `#00D9FF`;
- blue accent/glow: `#6B8CFF`;
- warning: `#FFB454`.
The runtime theme remains the palette authority. The separate `danger` token conflict below remains open.

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

1. The repository-root image `01 INTERFACE  NEON STAGE DEFAULT .png` was explicitly excluded by the owner on 2026-11-26. It is not a required reference, must not be requested, and is not a blocker. Visual acceptance uses the stored PPGU mockups/atlases named by the owner, the applicable REV.20 source contract and rendered JUCE comparison.
2. The full standalone component export inventory listed above remains incomplete; the successful atlas export is a partial deliverable, not a complete asset pack.
3. The SVG supplemental atlas work has only partial visual review. The 135 button-state records and all 183 rotary frames have not each received exhaustive 100%/200% review.
4. FL Studio 20 manual host acceptance, including clean install, project save/reopen, automation, sustained playback and performance measurements, remains NOT RUN / NOT CONFIRMED.

Do not mark the asset pack or REV.20 release as COMPLETE until these gates are closed. The canonical visual reference is still required before any claim of pixel-perfect matching or geometry changes based solely on visual inference.


## 2026-11-26 — owner requirement: exact 1:1 visual parity

The owner explicitly restated that the deliverable is a **1:1 visual copy of the applicable PPGU mockups**, not a merely similar neon skin. The required visual source set includes the stored items:
- `Неоновый атлас UI-ассетов PPGU` / `ppgu_atlas`;
- `Неоновый интерфейс PPGU — поп-панк гитара`;
- `Неоновый интерфейс гитарного плагина PPGU`;
- `02_ppgu_atlas_buttons_switches.png`;
- `03_ppgu_atlas_knob_strips.png`.

The owner additionally excluded only the repository-root `01 INTERFACE  NEON STAGE DEFAULT .png`; do not reintroduce it as a dependency.

### Visual audit of the current generated exports — NOT ACCEPTED AS 1:1

The successful 1x/2x atlas workflow produced files with the requested `02_ppgu_atlas_buttons_switches.png` and `03_ppgu_atlas_knob_strips.png` names. However, direct inspection of the rendered PNGs shows that they are **supplemental simplified vector drafts**, not yet faithful reproductions of the detailed stored asset references:
- the 27×5 button-state atlas currently renders mostly generic rectangular state swatches rather than the detailed glossy, beveled, icon-bearing controls shown in the button reference;
- the rotary atlas currently renders simplified small circular controls and does not yet match the reference's detailed metallic faces, knurled rims, segmented cyan arcs, slider thumbs and meter styling at equivalent fidelity;
- the 16 standalone panel-frame exports are predominantly empty panel shells. They do not yet reproduce the complete content-rich panels/composition shown in the PPGU interface mockups;
- the 1x/2x export and SHA-256 checks prove deterministic file generation/integrity only. They do not prove visual parity, correct cropping of every master asset, or runtime pixel match.

Therefore the current status remains **PARTIAL EXPORT / VISUAL PARITY NOT ACCEPTED / FULL ASSET PACK NOT COMPLETE**. Do not describe the current atlas or panel package as the 1:1 final UI.

### Mandatory completion sequence

1. Treat the stored PPGU UI mockups and source asset atlas as visual ground truth; build a component-by-component reference map with exact crop bounds, proportions, edge treatments, materials, lighting, typography and state variants.
2. Rework the button/switch, rotary, LED, meter, display, icon, keyboard, texture and hardware masters to match the supplied references—not generic substitutes. Preserve all declared state/frame counts and the real REV.20 runtime parameter contracts.
3. Export every individual asset and every required 1x/2x atlas with transparent alpha where appropriate; include exact dimensions, frame indexing, state naming, SHA-256 and source-to-export mapping.
4. Rebuild the standalone panels and complete main interface composition from the actual reference visual language. A panel frame alone is not a finished panel; live JUCE controls/text/telemetry must align with the reference without fake behavior or hit-region obstruction.
5. Render the JUCE plugin at 900×640, 1024×700 and 1600×1100; compare against the applicable mockup with registered overlays/difference images and review all critical crops at 100% and 200%.
6. Close each mismatch in the issue list before visual acceptance. Keep Windows x64 build, CTest, Pluginval and FL Studio 20 host acceptance as separate engineering gates.

No claim of 100% completion is allowed until the full asset inventory, runtime integration, visual comparison and host acceptance have evidence recorded here.


## 2026-11-26 — expanded 1x/2x standalone component export verified

**Status:** 484 COMPONENT FILES PER SCALE EXPORTED / HASH-VERIFIED; VISUAL PARITY AND JUCE INTEGRATION STILL OPEN.

GitHub Actions run `45831652470` completed successfully on commit `ecdd536898035111837452325994acabf05d0de5`. Artifact `15122163495` (`PPGU-NEON-STAGE-SVG-ATLAS-EXPORT`) was downloaded and inspected: 63,866,570 bytes; artifact SHA-256 `03f5bd283bbb33c58b339363819ea0cf27496d715a8b4b0e2d48dc06d6b8fe4d`.

The package contains **484 individual RGBA PNG components at 1x and the same 484 at 2x**:
- 5 background/material samples;
- 7 bezel/frame elements;
- 135 button state components (27 families × 5 declared atlas states);
- 14 dedicated main FX switch states (7 × OFF/ON);
- 10 LED samples (5 colour families × DIM/LIT);
- 183 rotary animation frames (3 styles × 61);
- 35 individual icon tiles;
- 10 display/frame components;
- 12 meter sample segments;
- 29 white keys, 20 black keys and 3 independent C/E/G active overlays;
- 8 pitch/mod fader parts;
- 13 hardware parts (3 bracket forms, vent grille, cyan rail and 8 fasteners).

Archive verification found 1,018 ZIP entries: 984 PNG, 30 contact-sheet JPG and 4 JSON reports/manifests. Both per-scale component manifests report 484 records. Every record path exists inside the ZIP; all 968 component PNG byte counts and SHA-256 hashes match their manifests (0 missing paths, 0 hash/size mismatches). The exported contact sheets for backgrounds, panels, displays, keyboard, faders, hardware, LEDs, switches, buttons, icons, meters and each rotary style were inspected.

### Corrections from visual inspection after this successful run

The contact-sheet review exposed two export/source details not detectable by count/hash validation:
1. White-key crops from the composite atlas contained adjacent black-key overdraw. The exporter is now changed to draw clean standalone white-key faces, while C/E/G active overlays remain independent transparent layers.
2. The hardware light bar referenced a non-existent cyan gradient. The atlas now defines a dedicated `cyanLight` gradient.

These two changes were committed after the successful artifact run (`a5d93c9`, `8ccbd5e`) and are **awaiting a fresh CI render and visual re-review**. Do not attribute them to artifact `15122163495`.

### Remaining 1:1 and runtime gaps

- Main rotary: per-parameter independent BASE/RIM/FACE/POINTER/SCALE/GLOW layers for all nine real parameters are still not separately exported. The 183 filmstrip frames are a separate deliverable and do not satisfy that layered-file requirement by themselves.
- FX EDIT rotary: parameter-specific scale/marking overlays and individually extracted layers remain incomplete.
- Button and FX-switch state inventory: the current 27×5 atlas and seven OFF/ON pairs do not yet cover every master-prompt FOCUS / hover / pressed / disabled variant for every required button/switch family. Preserve the distinct REV.20 five-state runtime contract; record and map any additional artwork-only states instead of silently changing the runtime contract.
- LEDs: full OFF/ON/GLOW/WARNING/ERROR/SUCCESS/DISABLED variants are not all exported as separate assets.
- Icons: 35 distinct icon tiles are present; the master prompt calls for 41 named icons in SVG plus 16/24/32/48 px outputs. Six items and the complete size matrix remain outstanding.
- Keyboard: the 49-key contact proof and neutral/active keys exist, but separate per-key HOVER and PRESSED states and a final 49-key composition preview remain outstanding.
- The 16 panel SVGs are currently scalable frame shells, not complete content-rich reproductions of the reference panels. Standalone 1x/2x renders of these frames are not equivalent to finished panels.
- Full interface previews at 1024×700 and 1600×1100, and rendered JUCE reference overlays/difference review at 900×640, 1024×700 and 1600×1100, remain outstanding.
- Runtime use of every new standalone asset, Windows x64 build/CTest/Pluginval on the final visual branch head, and FL Studio 20 manual host acceptance are separate gates.

The 484-component export is a verified intermediate asset package, **not** final 1:1 visual acceptance and **not** a complete release asset library.


## 2026-11-26 — detailed source-reference crop pipeline added

A new review-export path now extracts separate components directly from the detailed reference sheets stored in `Assets/3D/References/`:
- `Meshy_AI_neon_stage_buttons_and_switches.png`;
- `Meshy_AI_neon_stage_knobs_and_meters (1).png`.

Added `tools/extract_neon_stage_reference_components.py` and `REFERENCE_COMPONENT_MAP.md`. The extractor defines **70 unique crop rectangles**: five FX-card states; six selector states; six rhythm-button states; six mode-button states including the reference-only Punk Group pair; ON/OFF toggle; two action buttons; four status LEDs; nine rotary examples; ten slider/thumb elements; eight meter/progress elements; and twelve individual meter segments. Each crop is exported at source-native 1x and a documented 2x LANCZOS review enlargement (140 PNGs total), with per-crop source coordinates, dimensions, baked-label flag, byte count and SHA-256.

The atlas CI workflow now runs this extractor and includes the review package in the `PPGU-NEON-STAGE-SVG-ATLAS-EXPORT` artifact. The two reference sources have different repository byte sizes from the earlier Library copies used for local crop-bound design; therefore the GitHub Actions output/contact sheet must be reviewed before any crop coordinates or visual fidelity are accepted. First workflow run for this integration is pending.

This is a traceable reference-extraction deliverable, **not** runtime integration. Baked labels/scales are explicitly flagged; 2x files are resampled, not native 2x; dynamic JUCE text and meters must remain live. The crops are not yet accepted as standalone final artwork, and they do not close the 1:1 visual parity, 9-knob layered asset, complete panel, main-interface preview or FL Studio 20 gates.


## 2026-11-26 — 41 icons, 70 source crops and nine six-layer main knobs verified

**Status:** EXTENDED ARTWORK EXPORT VERIFIED / FULL 1:1 UI PARITY AND JUCE RUNTIME INTEGRATION STILL OPEN.

GitHub Actions atlas export run `45834419111` succeeded on source commit `f0c1807c6a89f735bec71461456f9b51f3fec0e5`. The branch then advanced to `1ceca6e5124e1308364c97087c9d06e93b7276a2` with a documentation-only correction to the accepted baseline; the asset source files used in this export were not changed by that follow-up.

Artifact `15124661281`, `PPGU-NEON-STAGE-SVG-ATLAS-EXPORT`: 88,485,111 bytes; SHA-256 `7577b9c1550dff7e872209850164914ee07d084f6d23d1ae3e1eb3687cf91ede`.

### Verified output inventory

- **490 independent components at 1x and 490 at 2x**: backgrounds/materials, panel-frame motifs, 27×5 button-state artwork, seven FX switch pairs, LED sample states, 183 rotary frames, 41 icon tiles, display frames, meter samples, 49 keys, three independent active-key overlays, fader parts and hardware details.
- **41 standalone SVG icon masters + 164 transparent RGBA PNGs** at 16, 24, 32 and 48 px. All 205 manifest records resolve to an archive file and all byte counts/SHA-256 values match.
- **70 source-faithful reference crops** from the stored button/switch and knob/meter reference sheets, each at 1x and 2x (140 PNG records). The 2x files are explicitly marked as LANCZOS-resampled versions of the source pixels; they are not native 2x artwork. Baked labels/scales are flagged in the manifest.
- **Nine main rotary controls × six separate layers** (BASE, RIM, FACE, POINTER, SCALE, GLOW): 54 SVG masters and 108 RGBA PNGs at 192 and 384 px. The layers are separately addressable; they have not yet been registered as the JUCE renderer's runtime drawing path.
- Contact sheets are included for the 41 icons, nine composite main knobs, source-reference crops and component categories.

The downloaded ZIP was independently inspected: 1,545 entries (1,410 PNG, 95 SVG, 31 JPG, 7 JSON, 1 TXT and 1 nested ZIP). All manifest records across the two component exports, icon export, knob-layer export and source-reference export were checked: **0 missing paths and 0 size/SHA-256 mismatches**. The 41-icon and nine-knob contact sheets were visually reviewed.

### Remaining work — not yet 1:1 accepted

1. Continue runtime registration of approved standalone artwork groups beyond the main rotary controls. The nine main controls now use the six-layer atlas in JUCE; retain APVTS bindings, live pointer/value, meter telemetry, note states, hit regions and automation.
2. Create separate FX EDIT knob layers and parameter-specific scales/overlays; review the three rotary styles against the exact FX EDIT mockup crops.
3. Complete the full LED state set (OFF/ON/GLOW/WARNING/ERROR/SUCCESS/DISABLED), all additional button focus/state variants and independent keyboard hover/pressed states; the current atlas only covers its declared 27×5, seven OFF/ON pairs and five LED colour DIM/LIT samples.
4. Complete content-rich panel artwork. The existing 16 SVG panels remain scalable shell frames, not finished compositions containing all visible reference content.
5. Produce full-interface previews at 1024×700 and 1600×1100, then render the JUCE editor at 900×640, 1024×700 and 1600×1100 for registered overlay/difference review against the stored mockups.
6. Continue current-head Windows x64 VST3/CTest/Pluginval validation and separately perform FL Studio 20 manual host acceptance. These are not proven by the atlas-export workflow.

Do not mark the UI, asset pack or release COMPLETE until the runtime rendering and screenshot comparisons close the remaining visual mismatches. Source-reference crops are comparison aids; do not automatically register crops with baked labels/scales as production controls.


## 2026-11-26 — main-knob layer atlas is now wired into the JUCE renderer

**Implementation status:** SOURCE INTEGRATION COMMITTED / WINDOWS BUILD AND RUNTIME TESTS PENDING.

The canonical SKIN-1 sprite-sheet generator now also emits `neon_stage_main_knob_layers_atlas.png`, 1152×768 RGBA, with a 9-column × 6-row grid. Columns are the REV.20 parameter order `GAIN, TREBLE, MID, BASS, VELOCITY, DYNAMICS, SWING, HUMANIZE, ACCENT`; rows are `BASE, RIM, FACE, POINTER, SCALE, GLOW`. Atlas geometry is declared in `neon_stage_spritesheet_manifest.json`.

The eighth atlas is declared in `SKIN/Skin_053/theme.json`, loaded by `PPGUThemeManager` with safe local-path checks and exact dimension validation, and included by `tools/package_active_skins.py`. `tests/ThemeManagerTests.cpp` requires the decoded image to be valid and exactly 1152×768. `tools/validate_skin_registry_16.py` validates the 54 atlas cells, their parameter IDs, layer names and coordinates.

`PPGUPremiumLookAndFeel::drawRotarySlider` now assembles the nine main controls from the independent BASE/GLOW/RIM/FACE/SCALE rows and paints the POINTER and live value arc from the actual JUCE Slider position. The 61-frame rotary atlas path remains intact for FX EDIT. The FX EDIT controls retain their current three material-family mapping. No APVTS parameter IDs, value ranges, DSP or audio-thread code were changed.

The main SKIN-1 sweep has been aligned to 210°–390° across the six-layer scale, JUCE slider and live pointer. Other themes explicitly retain their previous JUCE sweep so they do not inherit the SKIN-1 geometry.

GitHub Actions on source commit `bffd02d9ac0c01427517258e659f71cbbc4d03dd`:
- `45836777081` NEON STAGE atlas render/export: 1×/2× atlas renders, 490 component exports at both scales and 41 icon exports completed; source-reference extraction was still running at last check, followed by the six-layer pack and artifact upload.
- `45836777135` NEON STAGE native integration CI: atlas generator and Windows configure passed; VST3/C++ build was running.
- `45836777085` SKIN-1 runtime CI: atlas generator and Windows configure passed; build was running.
- `45836777065` Windows x64 workflow was queued/pending at last check.

Do not mark this integration build-verified until all three current-head build/test workflows finish successfully. Rendered JUCE screenshot comparison against the stored mockups at 900×640, 1024×700 and 1600×1100, plus manual FL Studio 20 host acceptance, remain open.


## 2026-11-26 — canonical rotary master and palette-source correction

The prior generated six-layer main-knob atlas used a separate Pillow-drawn silhouette. That was visually serviceable as a draft but was not tied to the canonical PPGU rotary master. This has now been corrected at source level:
- Added `tools/rotary_master_layers.py` to validate and extract `BASE/RIM/FACE/POINTER/SCALE/GLOW` groups from `SKIN/Skin_053/assets/vector/rotary_knob_master.svg`. The extractor rejects unexpected SVG child structure instead of silently creating different artwork.
- The Ubuntu atlas export produces independent SVG layer masters from the original source elements and rasterizes them at 192/384 px through pinned CairoSVG.
- The Windows build keeps its dependency surface portable: `draw_rotary_master_layer_pillow` mirrors the same source geometry, radii, marks, paths and source colors using Pillow only; it does not require a Cairo DLL on the Windows runner. This raster counterpart is not claimed to be pixel-identical to the CairoSVG render.
- The nine columns use one consistent physical control design from the master; labels, values and live pointer angle remain dynamic JUCE layers.
- The former project/palette mismatch with NEON STAGE Manager 3.0 is resolved; the generator, checked-in sprite manifest and validator now use PPGU REV.20 identity and SKIN-1 theme tokens.
- The SVG icon atlas contained two malformed, duplicated fragment strings (duplicate CANCEL/NOTES labels). Those two stray fragments have been removed; the sheet now declares 41 transform groups and 41 unique icon labels.

Verification is running on the current branch head. Do not mark the update build-verified until atlas generation, Windows configure/build, CTest, asset validation, Pluginval and visual review complete successfully. The 1:1 full-interface comparison and FL Studio 20 host acceptance remain open.


## 2026-11-26 — latest verified asset export and updated gap classification

### Verified intermediate deliverable

Atlas workflow `45838805335` succeeded on source commit `432db3c5d398b7ad86f57120ed87e3c4a60a09bf`. Artifact `15126143428` (`PPGU-NEON-STAGE-SVG-ATLAS-EXPORT`) is 87,923,180 bytes; SHA-256 `4d59b08cb1c06bbf316c3583239623721ffc679f42edbd48f757a7ace82a9e17`.

Independent ZIP inspection found 1,545 entries. Manifest-based integrity verification across both standalone component manifests, the icon manifest, the six-layer knob manifest and the source-reference crop manifest reported **0 missing files and 0 byte-size/SHA-256 mismatches**:
- 490 individual components at 1x and 490 at 2x;
- 41 SVG icons plus 164 transparent PNG variants (16/24/32/48 px);
- 54 standalone main-knob SVG layers and 108 corresponding PNG renders (192/384 px), 9 parameters × 6 layers;
- 70 source-sheet crops at source-native 1x and 70 review enlargements at 2x.

The 2x source-reference crops are LANCZOS enlargements and do not add source detail. Crops with labels/scales baked in are flagged in their manifest and are review-only until mapped around dynamic JUCE text. The main-knob SVG files are extracted from the canonical 512×512 rotary SVG master; the Pillow PNG counterpart is a portable raster approximation with the same source geometry/colors, not pixel-identical to an SVG/CairoSVG render.

### Runtime and build status at source commit 432db3c

- The nine-control 9×6 main-knob atlas is registered in the Skin-1 theme and rendered by JUCE. The live pointer and value arc are painted from the actual continuous APVTS value; the static POINTER row is retained in the atlas for full component separability but is not drawn over the live pointer.
- The SKIN-1 main rotary sweep is `-135°..+135°`; the `210°..390°` sweep is reserved for FX EDIT material variants.
- A regression test now checks that all 54 layer cells have at least one non-transparent pixel.
- Windows configure passed in SKIN-1 runtime CI `45838807152`, native integration CI `45838805325` and Windows x64 VST3 validation `45838805387`; VST3/C++ builds were still running at the time of this audit. CTest, 16-skin validation, VST3 packaging and Pluginval remained pending.
- Atlas export and panel-frame export completed successfully. Successful panel-frame export only verifies rasterized shell/guide files, not that the panels are visually complete or integrated as live JUCE windows.

### Remaining acceptance gaps

1. Complete the production background/material family (main 1024×700 background; graphite, brushed/anodized metal, LCD and recessed-control textures) from the approved samples, not generic substitutes.
2. Replace/finish the seven main-console shell panels with the reference-faithful panel composition and spacing. The six auxiliary SVGs have useful static layout guides/placeholders, but they still require live JUCE controls, real status/data, final scaling and overlay review. Dialog frames remain structural.
3. Build separate FX EDIT knob layers and parameter-specific scales/markings against the exact effect-panel reference crops; keep the existing FX parameter IDs/APVTS attachments.
4. Complete the LED state matrix (OFF/ON/GLOW/WARNING/ERROR/SUCCESS/DISABLED), explicit focus states where required, and the per-control mapping of the current 27×5 state art and seven FX OFF/ON pairs.
5. Finish independent keyboard hover/pressed states and the 49-key composition preview; keep live note/pressed states driven by MIDI.
6. Map the 41 icons to the correct REV.20 actions/states and verify their visual match; the 41 SVG/164 PNG exports themselves are present and hash-verified.
7. Produce full-editor previews and registered JUCE screenshot overlays/difference images at 900×640, 1024×700 and 1600×1100. No pixel-level 1:1 acceptance has yet been recorded.
8. Finish current-head Windows x64 build, CTest, 16-skin validation, Pluginval, VST3 packaging and separate manual FL Studio 20 host acceptance.

The UI, main-screen 1:1 parity and complete release asset pack remain **IN PROGRESS**. Do not call the work complete until the visual comparison and host gates pass.
