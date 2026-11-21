# REV.20 × NEON STAGE integration record

Status: integration patch prepared on an isolated branch; not merged.
Target: existing REV.20 VST3 project, not a second plugin.

## Existing native integration discovered

REV.20 already contains the NEON STAGE shell in its native JUCE editor:
- `Source/PluginEditor.cpp/.h` owns the single editor and its controls.
- `Source/UI/ThemeManager.cpp/.h` loads the selected skin manifest and provides semantic palette tokens.
- `Source/UI/PPGUStageSpriteSheet.cpp/.h` slices atlases in memory on the UI thread.
- `SKIN/Skin_053/theme.json` is the stable skin-053 manifest.
- `CMakeLists.txt` already compiles the native editor, theme manager and sprite-sheet helper.

Therefore this integration does not introduce a duplicate editor, new VST3 target,
new parameter registry, or parallel attachment system.

## Parameter wiring verified in REV.20

The editor already attaches its nine visible controls directly to APVTS:
- GAIN -> `ampGain`
- TREBLE -> `eqHigh`
- MID -> `eqMid`
- BASS -> `eqLow`
- VELOCITY -> `velocity`
- DYNAMICS -> `dynamics`
- SWING -> `swing`
- HUMANIZE -> `humanize`
- ACCENT -> `accent`

Seven primary FX switches attach to:
`compressorOn`, `eqOn`, `distortionOn`, `chorusOn`,
`delayOn`, `reverbOn`, `cabinetOn`.

The editor creates JUCE SliderAttachment/ButtonAttachment objects against the
existing processor APVTS. No new APVTS IDs are required for this skin integration.
MELODY/PATTERN remains the existing `playMode` choice; AutoChords remains an
auxiliary PATTERN workflow, not a third musical mode.

## Changes in this branch

- Align the canonical skin-053 manifest palette with the approved graphite,
  silver, purple, magenta and crimson palette.
- Align the ThemeManager fallback palette with the same semantic colours.
- Update the ThemeManager regression expectation for the canonical window colour.
- Preserve skin ID `skin-053`, display name, index 53, layout metadata, asset paths,
  and all existing APVTS attachments.
- No processor, DSP, sampler, state, MIDI, or audio-thread source is changed.

## Explicit remaining gates

- Existing binary artwork and sprite atlases have not been recoloured by this patch.
  Any blue/cyan pixels in baked artwork remain a visual compliance blocker.
- Runtime image files are not copied from the separate source-art repository.
- Redistribution permissions are not verified.
- Windows x64 build, CTest, pluginval, and FL Studio 20 host acceptance have not
  been run by this patch. Do not call this a tested release.
- Merge only after CI and a visual asset audit confirm the final appearance.
