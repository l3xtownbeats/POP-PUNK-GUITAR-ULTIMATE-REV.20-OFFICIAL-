# NEON STAGE → SIGNAL FORGE control map

**Product:** POP PUNK GUITAR ULTIMATE REV.20  
**Visual authority:** `assets/POP_PUNK_GUITAR_ULTIMATE_BANNER.svg`  
**Interface:** SIGNAL FORGE  
**Theme/art direction:** NEON STAGE

This document maps the existing native editor to verified processor parameters and existing GUI components. It is an implementation contract, not a claim that every vector asset is already wired into the editor.

## Visual and engineering rules

- The GitHub master banner is the immutable NEON STAGE visual source. Preserve its composition, hierarchy, lighting language and identity.
- SIGNAL FORGE remains the single functional control deck in the single VST3 GUI.
- Existing APVTS IDs are canonical. Never rename or silently replace them.
- Every control must provide real interaction and visual feedback. No decorative fake knobs, meters or switches.
- No file I/O, image decoding, JSON parsing or blocking synchronization on the audio thread.
- These mappings do not authorize DSP or MIDI scheduling changes.

## Main rotary controls

| Visible label | APVTS ID | Native component | Binding status |
|---|---|---|---|
| GAIN | `ampGain` | `knobs[0]` | SliderAttachment |
| TREBLE | `eqHigh` | `knobs[1]` | SliderAttachment |
| MID | `eqMid` | `knobs[2]` | SliderAttachment |
| BASS | `eqLow` | `knobs[3]` | SliderAttachment |
| VELOCITY | `velocity` | `knobs[4]` | SliderAttachment |
| DYNAMICS | `dynamics` | `knobs[5]` | SliderAttachment |
| SWING | `swing` | `knobs[6]` | SliderAttachment |
| HUMANIZE | `humanize` | `knobs[7]` | SliderAttachment |
| ACCENT | `accent` | `knobs[8]` | SliderAttachment |

All nine controls use the NEON STAGE rotary asset family (`ns-knob`) with existing parameter attachments preserved.

## Primary FX chain

| Visible slot | APVTS enable ID | Native component | Detail editor |
|---|---|---|---|
| COMPRESSOR | `compressorOn` | `fx_switch01` | Compressor |
| EQ | `eqOn` | `fx_switch02` | EQ |
| DISTORTION | `distortionOn` | `fx_switch03` | Distortion |
| CHORUS | `chorusOn` | `fx_switch04` | Chorus |
| DELAY | `delayOn` | `fx_switch05` | Delay |
| REVERB | `reverbOn` | `fx_switch06` | Reverb |
| CABINET IR | `cabinetOn` | `fx_switch07` | Cabinet IR |

Each slot has a confirmed APVTS ButtonAttachment. Clicking a slot also selects its matching detail group in `PPGUFXEditPanel`. FLANGER is available as an auxiliary detail group, not as an eighth primary-chain slot.

## Other confirmed GUI components

| UI element | Native component / parameter | Verified behavior |
|---|---|---|
| MELODY / PATTERN | `melodyTab`, `patternTab`, `modeBox` / `playMode` | Switches the play mode |
| START / SYNC MODE | `startModeBox` / `syncMode` | Host, Host Start, Internal |
| MIDI keyboard | `keyboard` | JUCE keyboard, MIDI 36–84 |
| Performance display | `performanceDisplay` | Processor-backed `PPGUPerformanceDisplay` |
| Preset library | `presetBox` | Loads selected factory preset |
| Category filter | `categoryBox` | All Presets / Melody / Pattern |
| Preset search | `presetSearch` | Filters catalog; must not silently change the loaded preset |
| Import guitar | `loadButton` | Opens import panel; SFZ panel provides LOAD SFZ callback |
| Skin | `skinButton` | Opens skin gallery |
| AutoChords | `autoChordsButton` | Opens chord/harmony workspace |
| Settings | `settingsButton` | Opens workspace settings |
| About | `aboutButton` | Plugin/runtime information |

## Auxiliary FX detail parameters

- **COMPRESSOR:** `compressorThreshold`, `compressorRatio`, `compressorAttack`, `compressorRelease`, `compressorAmount`; enable `compressorOn`.
- **EQ:** `eqLow`, `eqMid`, `eqHigh`, `eqLowFreq`, `eqMidFreq`, `eqMidQ`, `eqHighFreq`; enable `eqOn`.
- **DISTORTION:** `distortionDrive`, `distortionTone`, `distortionMix`; enable `distortionOn`.
- **CHORUS:** `chorusRate`, `chorusDepth`, `chorusMix`; enable `chorusOn`.
- **FLANGER (auxiliary detail page):** `flangerRate`, `flangerDepth`, `flangerFeedback`, `flangerMix`; enable `flangerOn`.
- **DELAY:** `delayTime`, `delayFeedback`, `delayMix`; enable `delayOn`.
- **REVERB:** `reverbRoomSize`, `reverbDamping`, `reverbMix`; enable `reverbOn`.
- **CABINET IR:** `cabinetMix`, `cabinetLowCut`, `cabinetHighCut`; enable `cabinetOn`.

## Existing APVTS parameters without a confirmed main-editor binding

The processor exposes additional parameters including `master`, `voices`, `palmMuteThreshold`, `tuning`, `pan`, `output`, `articulation`, `pickStyle`, `pitchBendTarget`, `vibrato`, `slideTime`, `legato`, `hammerPull`, scale controls, melody and pattern controls, Style DNA controls, FX slot selectors, `bpm`, `startOnFirstChord`, `patternQuantize`, and `tone`.

Their presence in APVTS is **not** proof of a visible editor control. The machine-readable `neon_stage_control_map.json` lists the exact inspected IDs. Add a control only after its actual editor component, attachment and interaction are implemented and verified.

## Disabled / unavailable UI

- **AUTO SOUND HUNTER:** disabled; backend not implemented.
- **CURATOR:** disabled; backend not implemented.

Keep both visibly unavailable until their real backends exist.

## Asset library references

- Surfaces: `assets/NEON_STAGE/neon_stage_surfaces.svg`
- Controls: `assets/NEON_STAGE/neon_stage_controls.svg`
- Indicators: `assets/NEON_STAGE/neon_stage_indicators.svg`
- Design tokens: `assets/NEON_STAGE/neon_stage_tokens.json`
- Machine-readable map: `assets/NEON_STAGE/neon_stage_control_map.json`

Use the existing SVG symbol families for stage/panels, rotary controls, buttons/tabs, toggles/sliders, signal trace, meters, LEDs and keyboard strip. If JUCE's runtime renderer cannot load external SVG references directly, bundle/parse them on the UI/resource side using the project's established asset-loading path; do not move decoding or file access onto the audio thread.

## Remaining verification gates

This mapping commit does not establish that the assets are integrated into the native GUI. Still required: native editor asset hookup, Windows x64 build, CTest, pluginval, visual comparison against the master banner, and FL Studio 20 host acceptance. Do not mark REV.20 production-ready until those checks have actual passing results.
