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

## Сценарии приёмки

| Режим | Вход MIDI | AutoChords | Ожидаемое поведение |
|---|---|---|---|
| MELODY | C4 | ON | Только C4 |
| MELODY | C4 | OFF | Только C4 |
| PATTERN / C major | C4 | ON | C4–E4–G4 |
| PATTERN / C major | D4 | ON | D4–F4–A4 |
| PATTERN / A minor | A3 | ON | A3–C4–E4 |
| PATTERN | C4, E4, G4 | ON | Входной аккорд без расширения |
| PATTERN | C4 | OFF | Только входной C4 |

Эта версия генерирует внутренние ноты для движка паттерна/семплера. MIDI-события обратно в DAW не передаются. AutoChords не меняет прямой режим MELODY.

Перед выпуском остаются ручные проверки переключения AutoChords, удержания/отпускания MIDI-ноты и смены тональности во время удержания ноты в FL Studio 20.
