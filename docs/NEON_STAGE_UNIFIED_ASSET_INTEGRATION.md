# NEON STAGE — Unified Master / Asset Integration Contract

**Status:** consolidation contract; source-art audit and runtime integration remain gated.  
**Product:** POP PUNK GUITAR ULTIMATE REV.20  
**Canonical identity:** NEON STAGE / SKIN-1 / skin-053 / Skin_053

This document unifies the immutable visual master, canonical runtime theme, SKINS-THEME- source artwork, REV.20 native controls, and the existing 4K vector asset library. It is the single integration contract for subsequent asset work; it does not claim pending source artwork has already been approved, sliced, or connected to the runtime editor.

## 1. Two authorities — never conflate them

1. **Visual/layout authority:** `assets/POP_PUNK_GUITAR_ULTIMATE_BANNER.svg`, SHA `82854d433e3a4183c13fbd6d3c131d565a621f46`. Immutable 100% layout/composition master. Preserve geometry, composition, proportions, hierarchy, placement and visual language. Never edit, recolor, stretch, crop or reinterpret it.
2. **Runtime DEFAULT theme authority:** `SKIN/Skin_053/theme.json`, SHA `7181d5bd7d7bd98787aaf461d4657524938538cb`. All runtime default colors come from this theme.

The banner is not a second skin. NEON STAGE is not a redesign inspired by it. All runtime surfaces, panels, controls, meters, labels, keyboard, FX modules and details must look like components of the same approved master.

## 2. Canonical DEFAULT palette

Use Skin_053 tokens only: graphite `#08090D`, `#14161B`, `#20232B`; control surfaces/borders `#0E1015`, `#292D36`, `#656B76`; text `#F2F0F4`, `#B9B5BF`, `#77727D`; accent/glow `#E6007E`, `#7B2C91`; danger/warning/success `#D7264D`, `#F2A900`, `#55C98A`; LCD/LED `#08090D`, `#F0DCE8`, `#E6007E`, `#38313B`; metal/shadow `#030305`, `#D9D7DF`, `#090A0E`.

No blue, cyan, teal or turquoise in DEFAULT runtime assets. The SKINS-THEME- manifest's earlier blue/cyan palette is source metadata only, not authoritative. Any palette adaptation must be a controlled non-destructive derivative after visual QA; preserve originals and alpha. Never use luminance-to-alpha removal that destroys dark metal, shadows or edge detail.

## 3. Source repository, artwork and licensing

Primary source repository: https://github.com/l3xtownbeats/SKINS-THEME-

Artwork families include gain/tone knobs and knob sheets; buttons/switches; frames/panels/backgrounds; VU meters; UI icons; Amp/Tone, AutoChords/Fretboard, Full FX Chain and piano keyboard module concepts. The REV.20 repo has reference copies under `Assets/3D/References/`; these are source/reference material, not automatically runtime-ready. Identical Git blob SHA means duplicate content: do not copy it again. Retain source provenance and hashes.

**Licensing gate:** source manifest says `license_status: not_verified` and `redistribution_cleared: false`; the source repository has no root `LICENSE` file. Keep artwork reference-only; do not embed in a distributed VST3, installer or release until written redistribution rights and applicable generator/service terms are verified. GitHub ownership or presence is not proof of redistribution permission.

## 4. Unified composition

Preserve TopHeaderBar; AutoChordsFretboard (left); FXEditModule (centre); AmpToneModule (right); FullFXChainBar; NeonPianoKeyboard (bottom). MELODY and PATTERN remain the two musical modes. AUTOCHORDS is a helper inside PATTERN, not a third mode. No alternate GUI, parallel shell, competing skin or substitute layout.

## 5. Native control truth — existing IDs only

Artwork skins existing JUCE controls; it never becomes the interaction or parameter source of truth.

Nine rotary controls: GAIN `ampGain`; TREBLE `eqHigh`; MID `eqMid`; BASS `eqLow`; VELOCITY `velocity`; DYNAMICS `dynamics`; SWING `swing`; HUMANIZE `humanize`; ACCENT `accent`.

Seven primary FX: COMPRESSOR `compressorOn`; EQ `eqOn`; DISTORTION `distortionOn`; CHORUS `chorusOn`; DELAY `delayOn`; REVERB `reverbOn`; CABINET IR `cabinetOn`.

Flanger remains in its existing auxiliary FX editor; do not add an eighth primary switch. Preserve APVTS IDs, ranges, defaults, attachments, automation, MIDI mapping, state serialization, DSP, sampler, preset behavior, scheduling and audio callback.

Other existing native UI includes Melody/Pattern selector, sync selector, preset browser, Pattern chord display, FX editor, MIDI keyboard (36–84), performance display, SFZ import, skin gallery, AutoChords, Settings and About. Do not present disabled/unimplemented features as functional.

## 6. Asset quality and states

Final curated assets require visual audit against the immutable master and Skin_053: panels/frames/backgrounds/materials; metallic knobs/buttons/switches/sliders/faders; LEDs/meters/scales/waveforms/displays; keyboard/modules; icons/labels/dividers/screws/trims/decorative details.

Interactive components need Normal, Hover, Pressed, Active and Disabled states; drag feedback where relevant. Decorative-only assets must be explicitly marked decorative. Inspect dimensions, alpha, atlas cell geometry, frame counts, duplicates, edge quality and crop bounds before creating runtime derivatives. Do not infer atlas geometry from filenames.

The existing `assets/NEON_STAGE/neon_stage_4k_*.svg` collection (38 symbols) is a starter vector library, not a quality-approved premium pack. Refine or replace it through master-referenced visual QA.

## 7. 4K contract

Master is 1800×720 (5:2). Exact 4K is 3840×1536 (5:2). On a 3840×2160 canvas, centre the complete 3840×1536 composition with vertical letterboxing. Never stretch to 16:9 or crop.

## 8. JUCE integration and real-time safety

SKINS-THEME- JUCE files are an integration scaffold, not proof of integration or successful compilation in this product. Audit dependencies before adoption and integrate only against actual `Source/PluginEditor.cpp/.h`, retaining existing native components and attachments.

Load/decode images, parse theme JSON and build caches only on a safe UI/setup path. Never perform file I/O, image decoding, JSON parsing, blocking locks or asset discovery in `processBlock`. Missing/invalid artwork falls back safely. Theme replacement is atomic; invalid input cannot partially replace the active theme, and failed hot swap retains last-known-good. Preserve source alpha. Every visible control remains a real native JUCE component wired to an existing function/parameter.

## 9. Acceptance gates

1. Written source-art redistribution rights verified.
2. Visual audit and atlas geometry completed against immutable master.
3. Skin_053 palette derivatives approved; no forbidden hues in DEFAULT.
4. Manifest, hashes, dimensions, alpha, state coverage and native mappings validated.
5. Actual PluginEditor integration completed without fake controls or parameter/DSP changes.
6. JSON/SVG/artwork validators and CTest pass.
7. Windows x64 VST3 build passes.
8. pluginval passes.
9. FL Studio 20 host acceptance completed.

CI success alone does not prove artwork quality, pluginval or FL Studio host acceptance. Do not merge PR #8 until all required checks and review gates are satisfied.

## 10. Verified status at consolidation

- PR #8 is open and draft.
- Before this documentation change, branch head `b65ec5c4dad716e470d116a9977cb5595841b464` had two `windows-x64` check runs completed successfully.
- Source-art redistribution is not cleared.
- SKINS-THEME- scaffold has not been proven integrated into `Source/PluginEditor.cpp`.
- 38-symbol 4K SVG collection remains a starter library.
- pluginval and FL Studio 20 host acceptance remain pending.

This contract consolidates design and engineering rules. It does not waive acceptance gates or imply pending work is complete.
