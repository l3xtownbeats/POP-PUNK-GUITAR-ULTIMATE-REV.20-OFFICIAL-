# ASSET_OPEN_ISSUES — NEON STAGE DEFAULT / SKIN-1

**Status:** reviewed against the exact repository reference and the REV.20 journal.  
**Reference 01 identity verified:** `01 INTERFACE  NEON STAGE DEFAULT .png`, Git blob SHA `747207e183c77e8b913a543b2dc40b29829e77da`, 2,359,486 bytes, 1672×941 px. The Library copy `Неоновый интерфейс PPGU для поп-панк гитары.png` has the same Git blob SHA.  
**Rule:** preserve the approved visual language and overall composition, but do not draw controls/functions that conflict with the current REV.20 journal, real APVTS bindings or the master asset prompt. Every conflict below remains visible to reviewers; none is silently "fixed" by inventing UI.

## Open issue 01 — third main mode in reference 01

- **Reference:** 01 visibly contains MELODY, PATTERN and PUNK GROUP.
- **REV.20 contract:** exactly two main modes, MELODY and PATTERN. PUNK GROUP is not a third main mode.
- **Current handling:** render only MELODY and PATTERN. Do not create a third tab, hidden third mode, alternate mode selector or new APVTS ID.
- **Authority:** current Info.txt journal and real processor/editor contract.

## Open issue 02 — twelve physical knobs in reference 01 vs nine actual rotary bindings

- **Reference:** 01 contains nine centre-row knobs plus three additional AMP & TONE knobs (12 visible rotary controls).
- **REV.20 contract:** nine user-facing rotary controls total, with the existing APVTS IDs: `ampGain`, `eqHigh`, `eqMid`, `eqLow`, `velocity`, `dynamics`, `swing`, `humanize`, `accent`.
- **Current handling:** preserve exactly nine bindings; use the journal's 4 AMP & TONE + 5 performance-strip distribution. Do not reproduce the extra three knobs as decorative or duplicate controls.
- **Authority:** PluginEditor.h / PluginProcessor parameter layout / master prompt.

## Open issue 03 — knob labels and parameter semantics differ

- **Reference 01 labels:** VOLUME, TONE, DRIVE, BASS, M.D, TREBLE, PRESENCE, REVERB, FX MIX, plus AMP GAIN/BASS/TREBLE.
- **REV.20 labels:** GAIN, TREBLE, MID, BASS, VELOCITY, DYNAMICS, SWING, HUMANIZE, ACCENT.
- **Current handling:** render the nine REV.20 labels and values as live JUCE text, not as text baked into knob artwork. No old labels or duplicate parameters.
- **Authority:** real APVTS IDs and master prompt.

## Open issue 04 — screenshot palette vs locked SKIN-1 palette

- **Reference 01/03/04:** hero paint, selected effect glyphs and some trim include magenta/purple/violet accents.
- **REV.20 theme contract:** graphite `#080B14/#101827`, cyan `#00D9FF`, electric blue `#6B8CFF`; no purple/violet/magenta in SKIN-1.
- **Current handling:** preserve the reference's hardware language, lighting hierarchy and guitar-stage composition, but use the exact locked SKIN-1 tokens. Danger/warning/success colors are only for truthful status semantics.
- **Authority:** theme.json and the approved SKIN-1 palette.

## Open issue 05 — unsupported telemetry and meters in screenshots

- **Reference 01/03:** shows CPU percentage, CPU meter, animated-looking level meters and spectrum/response visuals.
- **REV.20 contract:** do not fabricate CPU/RAM/latency/voice telemetry or a spectrum analyzer. The FX EDIT graph is a PROCESS RESPONSE / VISUAL GUIDE unless an actual measured signal is wired. A meter is allowed only when it reads a real processor value.
- **Current handling:** keep the actual library status, actual output meter only where the processor supplies it, and the documented static/guide graph. No fake CPU/RAM or analyzer.
- **Authority:** master prompt and functional gap audit.

## Open issue 06 — FX EDIT screenshot includes extra controls

- **Reference 03/04:** includes preset selector/save preset, gain-reduction meter, output-level meter, advanced/mode/knee controls and other extra controls.
- **REV.20 FX EDIT contract:** effect selector, POWER, PROCESS RESPONSE / VISUAL GUIDE, truthful APVTS status, and only the real parameters for the eight groups: COMPRESSOR, EQ, DISTORTION, CHORUS, FLANGER, DELAY, REVERB, CABINET IR.
- **Current handling:** render only controls with existing APVTS IDs. Do not add effect preset saving, advanced panels, knee/mode controls or meters without a real parameter/backend and explicit journal approval. FLANGER remains in FX EDIT, never an eighth main FX switch.
- **Authority:** PluginProcessor parameter layout and master prompt section 5.2.

## Open issue 07 — AutoChords screenshots show a complete generator

- **Reference 02/04/06:** show AutoChords ON, custom mode, chord progression, fretboard, playback mode, rhythm modes, preview, speed and related controls.
- **REV.20 contract:** setup-only warning: `SETUP ONLY — MIDI CHORD GENERATION / CUSTOM MODE / PREVIEW ENGINE NOT CONNECTED`; AUTOCHORDS OFF disabled; KEY, SCALE/QUALITY and RHYTHM PATTERN SLOT selectors remain.
- **Current handling:** render the setup-only panel and disabled generator state. Do not show an active chord generator, progression pads, preview engine, speed controls or custom mode.
- **Authority:** Info.txt functional status and master prompt section 5.4.

## Open issue 08 — Import Guitar screenshot includes unsupported import workflows

- **Reference 04:** shows drag-and-drop, file browsing, library preview, guitar identity, sample counts and a Load Library action.
- **REV.20 contract:** existing SFZ loading only; show LICENSED GUITAR LIBRARY, LOAD SFZ and truthful idle/loading/success/warning/error status. Do not invent folder/ZIP import, mapping editor, auto-convert or sample-preview functionality.
- **Current handling:** expose only the current SFZ workflow and real status.
- **Authority:** PluginEditor.cpp and master prompt section 5.1.

## Open issue 09 — Settings screenshot includes unrelated tabs and toggles

- **Reference 04:** shows General/Audio/MIDI/GUI tabs, MIDI Learn, Tooltips, Auto Save Presets, High Quality Graphics, UI scale and Buffer Size.
- **REV.20 contract:** WORKSPACE SETTINGS exposes auxiliary panel scale (0.5x–1.5x), panel gap (0–32 px), RESTORE NEON STAGE DEFAULT and OPEN SKIN GALLERY.
- **Current handling:** do not expose undocumented tabs or settings without actual backend/state.
- **Authority:** current SettingsPanel implementation and master prompt section 5.5.

## Open issue 10 — Skin Gallery reference count differs

- **Reference 04:** preview board shows eight sample theme cards.
- **REV.20 contract:** exactly 16 approved skins with immutable stable IDs.
- **Current handling:** Gallery renders the 16 registry entries; no eighth-only gallery, 17th theme or renamed ID.
- **Authority:** SKIN/theme_manifest.json and master prompt section 6.

## Open issue 11 — Auto Discover, Curator and About

- **Reference 01/04:** shows these controls/panels as if functional.
- **REV.20 contract:** these functions are unavailable. Master prompt requires disabled semantics; the latest Info.txt cover journal says unfinished Auto Sound Hunter/Curator controls are hidden from the main cover. About remains disabled.
- **Current handling:** follow the latest Info.txt cover decision for hidden Auto Sound Hunter/Curator; About is visible but disabled. No active auxiliary windows or fake backend content.
- **Authority:** latest Info.txt journal entry plus master prompt section 4A/27-control contract. This remains recorded because visibility differs between the older reference and latest journal.

## Open issue 12 — reference geometry differs from approved runtime geometry

- **Reference 01/03/04 source images:** 1672×941 px (approximately 16:9).
- **REV.20 runtime contract:** default 1024×700 px; minimum 900×640; maximum 1600×1100.
- **Current handling:** main editor uses 1024×700 with the approved resize limits. Responsive layout must preserve the reference's visual hierarchy and not crop live controls.
- **Authority:** master prompt section 4 and current branch journal.

## Open issue 13 — auxiliary reference pixel review (corrected 2026-11-21)

- **Repository presence verified on main:** all seven root reference files 01–07 exist. References 05 and 07 are confirmed as standalone files:
  - 05 — Git blob SHA `eabdf6b150b81fdf819f31ad9a7d91de3f8c68e2`, 2,239,241 bytes.
  - 07 — Git blob SHA `bfdc755ea9a3a3f8377f7dc55d9469f0c48ba759`, 2,198,527 bytes.
- **Additional source inventory:** `Assets/3D/References` is present on main; its button/switch, knob/meter, frame/panel and icon sheets plus the master prompt were inventoried. Duplicate files with identical hashes are not independent source assets.
- **Pixel-level review status:** 05 and 07 have not yet been inspected visually because the GitHub connector did not return their binary image payloads at these sizes. Presence/hash verification is not visual approval.
- **Current handling:** treat 01 as the locked main composition reference and 02–07 as mandatory window/state references. Use the master prompt, current runtime source and approved palette to fill missing artwork. Do not derive final production assets from legacy purple/magenta screenshots or unverified source sheets.

## Production consequence

The current branch may implement the real runtime modules and integrate existing approved individual control PNGs, but the complete asset pack is **not complete** until Batch 01–10 are delivered as separate assets with a valid manifest, dimensions, alpha validation, checksums, visual review and exact-reference audit. The current hero is still a legacy placeholder. The existing 5-state control PNG set does not satisfy every applicable NORMAL/HOVER/PRESSED/ACTIVE/INACTIVE/FOCUSED/DISABLED state. Window-specific 9-slice panel frames, LCD/LED assets, independent keyboard keys, FX knob layers, icon library, hardware details and compliant sprite sheets remain production work.
