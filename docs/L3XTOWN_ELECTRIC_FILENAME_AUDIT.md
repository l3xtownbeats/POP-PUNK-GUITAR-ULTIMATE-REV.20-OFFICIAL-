# L3XTOWN GUITAR — Electric Library Filename Audit

Status: filename and folder metadata audit only. No electric WAV was auditioned, waveform-inspected, pitch-detected, or altered. The labels below are provisional source labels, not verified notes, chord voicings, playing techniques, or tempos.

## Scope
- Source: `L3XTOWN_SAMPLE_MAP.csv`
- Electric/related source groups: 152 files.
- 01 ENGL: 43 files (15 Квинты, 13 Кода, 15 Ноты).
- 02 MESA: 43 files (15 Квинты, 13 Кода, 15 Ноты).
- 03 EVH: 12 files (Переборы 75 bpm).
- 04 MARSHALL GIBSON: 49 files (15 Квинты, 13 Кода, 15 Ноты, 6 Слайды).
- 05 FX: 5 files.

## 01 ENGL
- Квинты (15): filenames cover the 12 chromatic pitch-class labels, with separate E upper/lower and D#/D lower variants represented in the naming.
- Кода (13): 12 pitch-class labels are represented; E and several other labels have octave/spacing naming variants.
- Ноты (15): 12 pitch-class labels, with E upper and D#/D lower variants.
- Naming is inconsistent: examples include `До .wav`, `Фа .wav`, and `Ми верхняя.wav`. Do not rename originals.

## 02 MESA
- Квинты (15): 12 pitch-class labels, plus E and D# octave variants.
- Кода (13): 12 pitch-class labels, with octave/spacing variants.
- Ноты (15): 12 pitch-class labels, plus E and D# octave variants.
- The filename pattern broadly parallels ENGL, but the sound and exact tuning/voicing must be verified independently.

## 03 EVH
- Переборы 75 bpm (12): one filename for each of the 12 chromatic note names.
- The folder's 75 BPM label is a tempo hint only. Confirm actual tempo, bar length, start offset, and timing stability from audio before tempo-synced playback.

## 04 MARSHALL GIBSON
- Квинты (15): 12 pitch-class labels, with E and D#/D lower variants.
- Кода (13): 12 pitch-class labels with spelling/spacing variants.
- Ноты (15): 12 pitch-class labels, with E and D#/D lower variants.
- Слайды (6): six numbered slide files; no direction, interval, source/target pitch, or articulation can be inferred from filenames.

## 05 FX
Five files:
- `Переход 75 bpm.wav`
- `Слайд 1.wav` through `Слайд 3.wav`
- `Слайд дабл.wav`

These are provisional transition/slide FX labels. The 75 BPM label requires audio timing verification. The three numbered slides and double slide require audition and classification for direction, duration, pitch span, and musical context.

## Cross-family findings
1. The three main amp-labelled families (ENGL, MESA, MARSHALL GIBSON) have similarly shaped Квинты/Кода/Ноты groups, but similar filenames do not establish identical performances or identical tuning.
2. The note-name sets cover the chromatic pitch classes by filename. Some files additionally indicate octave variants (upper/lower E and lower D/D#); verify the actual fundamental and register from audio.
3. Original Cyrillic note labels must be preserved exactly. A normalized MIDI-note/pitch field belongs in a separate analysis manifest.
4. Do not automatically classify all files in Квинты as single-note power chords, or all files in Ноты as isolated single notes. Confirm the recorded content by listening.
5. Do not treat the EVH or FX tempo labels as validated BPM.
6. Keep all source WAVs and SHA-256 values unchanged.

## Required next analysis
For each electric file, derive and review:
- actual fundamental/pitch class and octave, with confidence;
- whether the file is a single note, power chord, full chord, riff, arpeggio, slide, or transition;
- tuning and any detuning;
- transient/start offset, duration, decay, silence, peak and RMS;
- tempo and bar length where relevant;
- whether it is a one-shot, sustained note, loop, or phrase;
- mapping role, playable range, and any exclusions.

## Mapping policy
- ENGL, MESA, and MARSHALL GIBSON are source-family labels only. They may become distinct tone families after audio review, not merely because of their folder names.
- Preserve EVH arpeggios and all FX as separate phrase/FX candidates; do not force them into chromatic note slots.
- Where a required note or articulation is missing, record a coverage gap. Do not silently relabel, duplicate, or pitch-shift another recording to make the map look complete.

## Release gate
Do not test the plugin, presets, sound engine, sound quality, or final build until all audio libraries are integrated and all 500 core factory presets are created and integrated.
