# REV.20 UI Baseline — NEON STAGE DEFAULT

Status: approved product/UI contract; implementation and visual parity are not yet accepted.
Baseline branch point: main commit bdcbfddcaec3e5ae48e6a82cad0955ddb935c297 (verify current main before implementation).

## 1. Authoritative references

The following repository artwork is the visual source of truth for composition and appearance:
- `01 INTERFACE  NEON STAGE DEFAULT .png` — primary full-interface reference.
- `02_ppgu_atlas_buttons_switches.png` — button and switch artwork.
- `03_ppgu_atlas_knob_strips.png` — rotary artwork.
- `04_ppgu_atlas_displays_keyboard.png` — displays and keyboard artwork.
- `Неоновый атлас UI-ассетов PPGU.png`
- `Неоновый интерфейс PPGU — поп-панк гитара.png`
- `Неоновый интерфейс гитарного плагина PPGU.png`

These references define visual composition, geometry, materials, textures, lighting, and component appearance. Legacy labels or controls shown in any artwork do not override the REV.20 functional contract.

## 2. Mandatory product structure

- The only play modes are `MELODY` and `PATTERN`.
- `PUNK GROUP` is excluded.
- Main layout: preset browser on the left; guitar hero/stage in the center; AMP & TONE and FX CHAIN on the right.
- Preserve the performance strip, MIDI keyboard, displays, LEDs, frames, and hardware details shown in the approved reference.
- The interface must use separate assets/atlases and stateful components. A single flattened background image is not an acceptable implementation.

## 3. Controls and parameter integrity

- The approved faceplate contains exactly nine primary rotary controls.
- Every rotary must be attached to an existing, verified REV.20 APVTS parameter and must affect its existing DSP destination.
- Do not invent parameter IDs or silently substitute unrelated controls to fill the nine positions.
- Seven FX switches must remain functional and expose truthful on/off states.
- Preserve existing APVTS IDs, parameter ranges/defaults, DSP, MIDI, audio processing, automation, and state serialization.
- No decorative-only controls, fake meters, fake status indicators, or placeholder actions.
- Do not reintroduce obsolete `VOLUME`, `TONE`, or `DRIVE` as legacy UI labels or functions. Existing internal parameters may only be retained where required for compatibility; do not rename or repurpose them without a separate approved migration.

## 4. Visual acceptance — 1:1 requirement

Compare runtime captures against the approved reference at matching dimensions. Acceptance covers:
- window geometry, panel placement, proportions, margins, and spacing;
- central guitar scene and hardware treatment;
- left preset browser and right AMP & TONE / FX CHAIN sections;
- all nine rotary controls and seven FX switches, including interaction states;
- MIDI keyboard, performance strip, displays, LEDs, frames, bevels, shadows, textures, and lighting;
- correct asset crops, sprite states, and scaling without distortion.

A claim of 100% visual parity is prohibited until pixel-level comparison has been reviewed and documented. Runtime screenshots and a human visual review are required; CI success alone does not establish visual parity.

## 5. Implementation guardrails

- Keep functional changes separate from artwork/layout changes where practical.
- Use the existing SKIN-053 assets only after verifying each asset's contents, dimensions, intended crop, and state.
- Do not replace approved hardware artwork with generic JUCE primitives.
- Do not merge broad legacy UI branches wholesale; port only reviewed, compatible assets or changes.
- Do not change audio-thread behavior, MIDI routing, DSP, or parameter semantics as part of a visual-only task.

## 6. Current verified APVTS inventory excerpt

The current `Source/PluginProcessor.cpp` defines the following relevant IDs (this is an inventory excerpt, not a claim that these are the nine faceplate assignments):
- Global/performance: `master`, `voices`, `velocity`, `dynamics`, `palmMuteThreshold`, `tuning`, `pan`, `output`.
- Mode: `playMode` with choices `Melody` and `Pattern`.
- Pattern feel: `bpm`, `swing`, `humanize`, `accent`.
- Amp/tone compatibility parameters currently present in the processor: `ampGain`, `tone`.
- FX on/off parameters include `compressorOn`, `eqOn`, `distortionOn`, `chorusOn`, `flangerOn`, `delayOn`, `reverbOn`, `cabinetOn`, and `doubleTrackOn`.

The live editor header `Source/PluginEditor.h` defines the exact nine rotary labels and APVTS IDs, and `Source/PluginEditor.cpp` attaches each index directly to `processor.parameters`:

| Faceplate label | APVTS ID | Processor parameter label |
|---|---|---|
| GAIN | `ampGain` | Amp Gain |
| TREBLE | `eqHigh` | EQ High |
| MID | `eqMid` | EQ Mid |
| BASS | `eqLow` | EQ Low |
| VELOCITY | `velocity` | Velocity Response |
| DYNAMICS | `dynamics` | Velocity Dynamics |
| SWING | `swing` | Swing |
| HUMANIZE | `humanize` | Humanize |
| ACCENT | `accent` | Accent |

The seven visible FX buttons and their APVTS toggle IDs are also verified in `PluginEditor.h` and attached in `PluginEditor.cpp`:

| Visible FX switch | APVTS ID |
|---|---|
| COMPRESSOR | `compressorOn` |
| EQ | `eqOn` |
| DISTORTION | `distortionOn` |
| CHORUS | `chorusOn` |
| DELAY | `delayOn` |
| REVERB | `reverbOn` |
| CABINET IR | `cabinetOn` |

The processor parameter layout defines all nine IDs and all seven boolean toggles. The visible seven-effect chain intentionally does not expose FLANGER as an eighth switch. The detailed editor currently maps the seven switches to detail groups `0, 1, 2, 3, 5, 6, 7`; verify this index mapping against the FX editor's group definitions before changing it. This confirms APVTS attachments, not by itself complete DSP correctness or pixel-level visual acceptance.

## 7. Definition of done

1. Runtime layout matches the primary reference at target sizes.
2. All visible controls map to real APVTS/DSP behavior and report truthful state.
3. MELODY/PATTERN only; no PUNK GROUP.
4. All seven FX switches operate the intended FX functions.
5. No regression to APVTS, DSP, MIDI, audio, automation, or preset/state handling.
6. Pixel-level reference comparison is reviewed; deviations are listed and resolved before claiming 1:1.
7. CI is green on the exact proposed commit, and host acceptance is recorded separately.
