# Melody Mode — Session Guitarist-style Playability

Product: POP PUNK GUITAR L3XTOWN VST3

## Goal

Melody mode is a playable, note-by-note guitar instrument for MIDI keyboards and the FL Studio Piano Roll. It must feel like playing a sampled guitar instrument, not triggering a generic synth or a pre-recorded phrase. Every incoming MIDI note selects and plays the corresponding pitched guitar sample/articulation.

## Required behavior

- Each MIDI note-on triggers the correct pitch; note-off ends or releases the voice according to the selected articulation and sample envelope.
- Support the full configured playable range with correct MIDI note-to-sample mapping and pitch tracking.
- Use multisampled WAV material across the range. Do not rely on pitch-shifting one sample across the entire keyboard.
- Velocity layers must select distinct recorded dynamics/attacks where available; velocity also controls response and may trigger palm-muted articulations according to a user-adjustable threshold.
- Round-robin sample selection prevents identical repeated-note playback where multiple takes exist.
- Articulations: picked/open, palm mute, muted/dead note, sustained, and (only where source recordings exist) legato, slide, hammer-on and pull-off. Never fake unavailable articulations by claiming recorded realism.
- Provide configurable voice count/polyphony, voice stealing, and a low-CPU mode.
- Support electric and acoustic instrument/sample profiles.
- Expose attack/release and basic tone/amp/FX controls without blocking the audio thread.
- MIDI pitch bend and modulation behavior must be documented and tested; do not assume a guitar bend sample exists.
- Save and restore all mode, articulation, velocity, and instrument settings with plugin state.

## Sample engine requirements

- Sample lookup and disk streaming must not block the audio callback.
- Preload attack/transient portions where needed; stream long tails from a worker/background reader with bounded buffering.
- Provide sample purge by instrument/articulation/unused range, with safe reference counting so active voices are never invalidated.
- Validate sample paths, sample rate, channels, root key, key range, velocity range, loop points, and license metadata.
- Provide graceful missing-sample reporting; do not silently substitute a synth voice and label it as recorded guitar.

## Session Guitarist-like performance expectations

The goal is comparable ease of play and convincing sampled-guitar response, not copying proprietary NI recordings or software. Only legally redistributable or user-owned recordings may be bundled. A convincing result requires purpose-recorded, edited, mapped multisamples with multiple velocity layers and round robins. A basic SFZ parser or Karplus–Strong fallback is not sufficient for the final quality target.

## Acceptance tests

1. Trigger chromatic MIDI notes across the supported range and verify pitch/root-key mapping.
2. Verify note-on/note-off, overlapping notes, sustain/release, voice stealing, and configured polyphony.
3. Verify velocity layer transitions and palm-mute threshold behavior.
4. Verify round-robin variation with at least two takes per mapped zone.
5. Verify electric/acoustic profile switching and state recall.
6. Stress-test CPU, memory, and streaming under dense MIDI playback; confirm the audio callback performs no disk I/O or blocking locks.
7. Test MIDI input and audio output in FL Studio 20 x64; pluginval alone does not count as host validation.

## Preset-bank relationship

The planned minimum is 150 Melody presets plus 150 Pattern presets. Melody presets must select actual sample profiles and articulations available in the installed library. A preset definition without mapped samples is a catalog entry, not a finished playable guitar preset.


## PATTERN mode companion workflow — user approved 2026-11-22

The Session Guitarist – Electric Sunburst Deluxe/Vintage reference is approved as a functional/usability benchmark, not as source material to copy. Keep the NEON STAGE DEFAULT shell, palette and layout as the only visual identity.

PATTERN must present three independent choices:
1. Instrument source/profile: the actually loaded electric/acoustic SFZ profile and its verified mapped content.
2. Tone preset: selected from the existing factory catalog; tone and FX remain independent of performance technique.
3. Performance articulation/variation: only real recorded zones/one-shots/loops, with velocity and note lifecycle behavior supported by the mapped source.

Original pop-punk performance vocabulary includes downstroke-driven power chords, octave hooks, palm-muted verses, open chorus lift, sustained/ambient lead textures, alternate picking, arpeggios and stop-start/syncopated changes. These are implementation targets, not permission to reproduce protected riffs or proprietary recordings.

Pattern variations must be switchable during playback with host sync and clean transitions. Optional layering is not the default and must obey polyphony/CPU limits. Any technique without a verified recording/map is visibly unavailable; no synthetic substitute may be described as a recorded guitar articulation.

This PATTERN companion does not alter the MELODY requirements above. The initial UI checkpoint in Source/PluginEditor.cpp displays the SFZ filename, opens the existing import workflow, shows the selected factory tone label and reports map-verification status. It is not proof of a complete performance engine. Current static source audit did not find the APVTS articulation or palmMuteThreshold values consumed by the audio path. Next task: verified articulation metadata and recorded-zone selection through SamplerEngine/PatternScheduler, with exact-SHA regression tests.
