# NEON STAGE MANAGER 3.0 — native integration map

This document maps the supplied Tkinter/Pillow prototype to the JUCE VST3 implementation. The Python files remain visual/reference material; none of the Tkinter code is embedded in the plugin.

## Native component mapping

| Prototype | REV.20 native implementation |
|---|---|
| `NeonStageUltimate` | `PopPunkGuitarUltimateAudioProcessorEditor` with the six-part responsive layout |
| `TopHeaderBar` | Existing JUCE editor title, preset/library navigation and system actions |
| `AutoChordsFretboard` | `PPGUChordDiagram`, with open, fretted and muted-string notation |
| `NeonPianoKeyboard` | JUCE `MidiKeyboardComponent` connected to the existing `MidiKeyboardState` |
| `FXEditModule` | `PPGUFXEditPanel`, using existing APVTS parameter attachments |
| `NeonVUMeter` | `PPGUOutputMeter` and `PPGUNeonVUMeter`, driven by lock-free post-master L/R peak snapshots |
| `NeonKnob` | Existing JUCE sliders with Skin-1 control-state artwork and a live position indicator |
| `NeonFXButton` / `NeonToggle` | Existing JUCE buttons with APVTS attachments and distinct normal, hover, pressed, active and disabled rendering |
| `SkinsGalleryPanel` / `SkinCard` | Existing 16-skin JUCE gallery, including search, favorites, preview, Apply and Cancel |
| `SettingsModule` / `NeonCheckBox` | Existing settings workspace controls for panel scale, panel spacing, restoring the default theme and opening the gallery |
| `FullFXChainBar` | Seven horizontal primary FX switches, bound to the seven locked REV.20 IDs |
| `SpriteSheetLoader` | `PPGUStageSpriteSheet`, with strict bounds validation and source-alpha preservation |
| `NeonRadar` | `PPGUDiscoveryRadar`, safely stopped by default and reserved for a future discovery backend |

## Fixed integration rules

- The nine existing parameter IDs remain `ampGain`, `eqHigh`, `eqMid`, `eqLow`, `velocity`, `dynamics`, `swing`, `humanize`, and `accent`.
- The primary FX chain remains Compressor, EQ, Distortion, Chorus, Delay, Reverb and Cabinet IR. Flanger remains an optional detail-editor page only.
- DSP, sampler, MIDI scheduler, preset catalogue, parameter ranges, automation and state serialization remain processor-owned.
- The audio callback publishes only two atomic peak values. UI timers and image drawing run on the message thread.
- Skin-1 state artwork is used when present; LookAndFeel fallback remains available for other skins or missing art.

## Intentionally not simulated

- The fretboard's default A-major diagram is a reference voicing. It does not claim that the unfinished AutoChords MIDI-generation backend is active. The separate AutoChords generator UI remains disabled.
- Auto Sound Hunter, Curator and About remain disabled until their backends/content are implemented. The radar component is not started by the plugin.
- CPU/RAM figures are not hard-coded. The new VU meters show measured output peaks instead.
- The DAW owns audio buffer size and host configuration; the plugin settings panel does not pretend to change those host-level values.
- The compressor response window remains explicitly labelled as a visual guide until live compressor gain-reduction telemetry is exposed.

## Validation gates

1. Windows x64 JUCE/VST3 build.
2. Full CTest suite, including sprite-sheet bounds tests and existing processor/UI contracts.
3. 16-skin registry and package validation.
4. FL Studio 20 manual acceptance for layout, resize, DPI, parameter automation, MIDI keyboard, FX selection and theme switching.

A successful source commit or CI build alone is not a claim of FL Studio acceptance or release readiness.
