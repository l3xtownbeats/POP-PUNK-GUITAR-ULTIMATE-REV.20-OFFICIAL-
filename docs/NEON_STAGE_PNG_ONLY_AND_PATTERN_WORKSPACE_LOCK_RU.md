# NEON STAGE DEFAULT — PNG-only production and PATTERN workspace lock

Date: 2026-11-22  
Product: POP PUNK GUITAR ULTIMATE REV.20  
Skin: NEON STAGE DEFAULT / SKIN-1 / `skin-053`  
Applies to: main screen, all auxiliary windows, all controls, all states, all UI artwork.

## 1. Absolute asset-format rule

**PNG is the only permitted artwork format.**

- Do not author, deliver, bundle, load, or use SVG artwork.
- Existing SVG batches are legacy placeholders only. They are not production masters, cannot be used as a visual-quality sign-off, and must not be the source of final artwork.
- Do not use SVG as an intermediate rendering format in the final production pipeline.
- Deliver every panel, control, knob layer, switch state, key, icon, LCD/LED housing, texture, glow, shadow, and decorative hardware part as its own PNG.
- Use lossless RGBA PNG with clean alpha edges. Keep text, live values, labels, meters, focus rings and dynamic status as JUCE runtime layers wherever they can change.
- Provide high-resolution master PNGs at a minimum of 4x the 1024x700 reference scale for panels and detailed controls. Supply runtime variants at 1x, 2x and 3x. Use higher master resolution where fine metal machining, bevels, labels or micro-detail require it.
- Every file must have exact pixel dimensions, alpha validation, SHA-256, semantic asset ID, state, scale and source/master relationship in the manifest.
- No one-piece screenshot may replace separate functional UI components. No fake static controls, values, LEDs, LCD readouts or status text.

## 2. Visual quality and art direction

NEON STAGE DEFAULT must read as a finished premium studio guitar instrument, not a wireframe, generic dashboard, low-detail mockup or cheap sci-fi HUD.

- Match approved reference 01 for the main screen composition and references 02–07 for the corresponding auxiliary/workspace details.
- Use precision industrial hardware construction: matte graphite, anodized metal, controlled brushed-metal grain, machined bevels, layered glass/LCD, accurate shadows and restrained edge reflections.
- Locked palette: graphite `#080B14` / `#101827` / `#17243A`, cyan `#00D9FF`, electric blue `#6B8CFF`, with semantic warning/success/error colours only for their actual states.
- No purple, violet or magenta accents. Do not flood every edge with glow.
- Keep a clear visual hierarchy, generous spacing, legible labels and precise alignment. Main editor reference size remains 1024×700, with approved resize range 900×640 to 1600×1100.
- The hero guitar artwork must be a high-quality, approved original image asset. The preserved placeholder is not acceptable as final artwork.
- Use the same coherent hardware language across all six auxiliary windows, dialogs, controls and state variants.

## 3. PATTERN mode interaction

### Immutable main-editor layout and preset contract — USER CONFIRMED

The approved NEON STAGE main editor composition is immutable during this work:
- Preserve the existing main-screen zones and columns, including PRESETS / preset browser, PLAYING / playing core, AMP & TONE, FX CHAIN, performance strip and footer/keyboard exactly as defined by the approved reference and current implementation.
- Do not rename, reorder, replace, resize, relocate or repurpose those main-screen columns or their controls.
- Preserve the existing factory preset catalog, category structure, names, ordering, filtering/search, selection callbacks, preset loading and sound-selection behavior byte-for-byte in intent. PATTERN work must not add Pattern 1–8 as entries to the main preset list or change any preset selection path.
- PATTERN is an existing main mode/tab, not a new main-editor column and not a third mode. Selecting it may open its dedicated auxiliary workspace while leaving the main editor composition intact.
- The two selection areas described below belong only inside the auxiliary PATTERN workspace. They must never be used to replace or restructure the main PRESETS / PLAYING / AMP & TONE / FX CHAIN columns.
- Session Guitarist – Electric Sunburst Deluxe is strictly a usability benchmark for pattern/section/harmony workflow, never a source for visual design, labels, branding, samples or copied assets.

## 3A. PATTERN mode interaction details

PATTERN is one of exactly two main modes: MELODY and PATTERN. It is not a third mode.

### Entry flow

1. The user clicks the main-screen `PATTERN` mode button.
2. PATTERN becomes the visibly selected main mode.
3. The dedicated `PATTERN / SONG SECTION ROUTING` workspace opens.
4. The workspace header contains a separate, prominent `OPEN AUTOCHORDS` button.
5. Clicking `OPEN AUTOCHORDS` opens the separate `AUTOCHORDS / HARMONY SETUP` auxiliary window. It does not change the main mode.

### Two-column layout

**Left column — SONG SECTION**
- INTRO
- VERSE
- CHORUS
- BRIDGE
- OUTRO

**Right column — RHYTHM CATALOG**
- Pattern 1
- Pattern 2
- Pattern 3
- Pattern 4
- Pattern 5
- Pattern 6
- Pattern 7
- Pattern 8

Both columns must have their own clearly labelled panel, selected/hover/focus states and readable row/card treatment. Do not collapse the two columns into one vertical stack at the reference layout size.

### Bottom action row

- `PREVIEW`: arms only the supported real pattern preview; status must explain exactly what is previewed.
- `APPLY`: assigns the selected Pattern slot to the selected song section.
- `CANCEL`: clears preview and restores the prior selected section/selection state.
- A live status area reports selection, preview, applied assignment, cancellation and errors. Do not bake status copy into PNG.

### AutoChords window

The separate AutoChords window must be visually discoverable from the PATTERN workspace and match approved reference 02. It contains the real Key, Scale/Quality and Rhythm Pattern Slot setup fields, plus an honest generator state. If the complete Pattern MIDI/chord/preview workflow is not connected and verified, the generator remains visibly OFF/disabled and the window states SETUP ONLY. Never depict a working generator when the backend is unavailable.

## 4. Session Guitarist usability reference

Use Native Instruments Session Guitarist – Electric Sunburst Deluxe only as a high-level usability reference for:
- immediate discoverability of pattern/section selection;
- clean separation of section and pattern choices;
- a distinct AutoChords/harmony entry point;
- premium sampled-instrument presentation and clear performance workflow.

Do not copy its proprietary UI artwork, brand marks, product text, samples, preset content or exact visual assets. NEON STAGE remains the approved PPGU design.

## 5. Functional and visual acceptance

- [ ] All final UI artwork is PNG only; no SVG remains in the production asset manifest or runtime path.
- [ ] Main screen matches reference 01 and all six auxiliary windows match their approved references and journal definitions.
- [ ] All controls are separate interactive JUCE components layered over PNG artwork.
- [ ] All required states have separate PNGs: normal, hover, pressed, active/on, disabled and focus where applicable.
- [ ] Knob artwork includes body, rim, face, pointer, scale, highlight, shadow and controlled glow as separate compositing layers where appropriate.
- [ ] LCD/LED, MIDI keys, buttons, FX switches, icons, panels and dialogs have their complete required states.
- [ ] PATTERN click opens the two-column workspace and selects PATTERN mode.
- [ ] OPEN AUTOCHORDS opens the separate harmony setup window.
- [ ] PREVIEW/APPLY/CANCEL behavior is truthful and verified.
- [ ] No DSP, sampler, APVTS IDs/ranges, MIDI scheduler or audio callback changes are made merely to satisfy artwork.
- [ ] PNG manifests, dimensions, alpha, SHA-256, contact sheets and visual review records are complete.
- [ ] FL Studio 20 manual visual and interaction acceptance is completed before release claims.

**Current status:** the PNG migration batch is a technical rasterization milestone, not final art approval. The existing SVG artwork must be replaced by bespoke, high-resolution PNG production masters before NEON STAGE can be called visually complete.
