# AutoChords and About — native implementation

## AutoChords

The existing APVTS control `singleMidiNoteAsChordRoot` now drives a real, bounded chord generator.

- It is applied only in **PATTERN** mode.
- A single held MIDI note expands to a close-position triad using `scaleRoot` and `scaleMode`.
- Major and natural-minor diatonic qualities are derived from the selected scale degree.
- Chromatic mode and notes outside the selected diatonic scale use a major-triad fallback without moving the played root.
- Invalid MIDI/scale values are rejected; generated notes never exceed MIDI note 127.
- Holding two or more notes leaves the incoming chord untouched.
- **MELODY** mode remains strictly one input key to one played note.
- The AutoChords workspace toggle is attached to the existing APVTS parameter; no parameter ID was renamed or removed.

This is a first functional AutoChords engine, not a full guitar voicing database. The fretboard drawing remains explicitly labelled as a reference voicing and is not presented as a live fingering solver.

## About

The About action now opens a native JUCE information dialog with the plugin identity, version, format, core features and host-owned buffer/sample-rate note.

## Still gated

Auto Sound Hunter and Curator remain disabled. This change does not perform uncontrolled disk scans, download content, approve samples or import unreviewed libraries. These features require a dedicated backend and licence-aware review workflow.

## Tests

`ppgu_autochord_contracts` covers:
- Major/minor diatonic triads across several scale degrees.
- Chromatic and out-of-scale fallback behaviour.
- Invalid key/note rejection.
- Upper MIDI range handling without note overflow.
