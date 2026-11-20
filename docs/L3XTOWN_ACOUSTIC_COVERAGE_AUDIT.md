# L3XTOWN GUITAR — Acoustic Chord Coverage Audit (Filename Metadata)

Status: deterministic filename/manifest audit only. No audio was auditioned or analyzed. This report identifies coverage and naming gaps; it does not certify the sounding pitch, chord voicing, or articulation.

## Scope and source
- Source: `L3XTOWN_FULL_INVENTORY.csv` and reconciled `L3XTOWN_SAMPLE_MAP.csv`, 393 source path records / 387 unique SHA-256 contents.
- Acoustic families: ALL MARTIN (120 after the owner-confirmed additions) and ALL TAYLOR (121 after the owner-confirmed additions), 241 files total. The current full inventory contains 393 path records; six exact duplicate-content pairs are retained as aliases.
- Chord roots normalized for comparison: A, A#, B, C, C#, D, D#, E, F, F#, G, G#.
- Cyrillic `С` at the beginning of a filename was treated as Latin `C` for analysis only. Original filenames remain unchanged.

## Coverage by family and folder label

| Family | Folder label | Files | Filename-labelled coverage |
|---|---|---:|---|
| ALL MARTIN | ROOT | 25 | 12 major + 12 minor roots, plus one C minor 7-labelled file |
| ALL MARTIN | 7 | 24 path records / 23 unique hashes | 12 maj7 labels + 12 min7 labels; C min7 is an exact-content alias of the ROOT C min7 file |
| ALL MARTIN | Вверх | 24* | 12 major + 12 minor labels (owner-confirmed correction) |
| ALL MARTIN | кода | 24 | 12 major + 12 minor labels |
| ALL MARTIN | сус | 24 | 12 major + 12 minor labels |
| ALL TAYLOR | ROOT | 24 | 12 major + 12 minor labels |
| ALL TAYLOR | 7 | 24 | 12 maj7 + 12 min7 roots |
| ALL TAYLOR | вверх | 24* | 12 major + 12 minor labels (owner-confirmed correction) |
| ALL TAYLOR | Кода | 25 | 13 major + 12 minor labels; A major has two takes |
| ALL TAYLOR | Сус | 24 | 12 major + 12 minor labels (A maj filename is `A maj cус.wav`) |

Folder labels such as `сус` are retained as source-folder labels only. They do not prove that the recordings contain sus2/sus4 voicings; filenames in these folders are predominantly labelled maj/min.

## Missing filename-labelled combinations

### ALL MARTIN
- ROOT: none in the 12-root major/minor set; one additional C min7-labelled file is present.
- 7: C min7 filename is present as `ALL MARTIN/7/С min 7.wav`; however, its SHA-256 is identical to `ALL MARTIN/С min7.wav` in ROOT. This is a path alias, not an independent seventh-folder recording. Keep the label match, but do not count it as a unique performance or independent variation.
- Вверх: none; A# maj, D# maj, and D# min are now present (owner-confirmed correction).
- кода: none in the 12-root major/minor set.
- сус: none in the 12-root major/minor set.

### ALL TAYLOR
- ROOT: none in the 12-root major/minor set.
- 7: none in the 12-root maj7/min7 set.
- вверх: none; D# maj and D# min are now present (owner-confirmed correction).
- Кода: none; A maj has two takes.
- Сус: A maj filename is present as `ALL TAYLOR/Сус/A maj cус.wav` (mixed Latin/Cyrillic spelling in the filename). Its inventory record has matching size and SHA-256; audio voicing remains unverified.

## User-confirmed coverage notes (2026-11-16)

The project owner has separately confirmed the following filename-level gaps and variation candidate:
- ALL MARTIN / 7: C min7 is present by filename; exact SHA-256 duplicates the ROOT C min7 asset, so it is not an independent take.
- ALL MARTIN / Вверх: A# maj, D# maj, and D# min are now present; the previous missing-coverage entries are closed.
- ALL TAYLOR / вверх: D# maj and D# min are now present; the previous missing-coverage entries are closed.
- ALL TAYLOR / Сус: A maj is present by filename as `A maj cус.wav`; the mixed-script suffix is preserved.
- ALL TAYLOR / Кода: two A maj takes are present and should be retained as separate candidates for performance variation.

The inventory cross-check corrects the two earlier missing-label conclusions: both filenames are present in the requested folders. The ALL MARTIN C min7 path is byte-identical to the ROOT C min7 file, while the ALL TAYLOR A maj entry is a distinct hash in the Сус folder. These are filename/hash findings only; they do not establish audio-verified chord content. See `L3XTOWN_ACOUSTIC_COVERAGE_GAPS.csv` for the corrected statuses. The two A maj takes remain candidates only until their waveforms/audio are compared; if genuinely distinct and musically usable, they can be mapped as round-robin or alternate takes.

## Engineering implications
1. Do not synthesize missing coverage by simply relabelling another chord or assuming transposition is safe. First verify the source audio and decide whether pitch-shifted variants are musically acceptable.
2. Keep original file names and SHA-256 hashes immutable. Store normalized root/quality fields in a separate manifest.
3. The extra ALL MARTIN C min7 file in ROOT must not be silently merged with the dedicated 7 folder.
4. Preserve the two ALL TAYLOR A major coda takes as separate source assets; later they may support round-robin variation if their audio is genuinely different.
5. Upstroke/coda/sus folder names are provisional technique/role labels. Confirm by listening and waveform/transient inspection.
6. These coverage counts describe labels only, not the number of playable MIDI notes or verified chord voicings.

## Next non-destructive analysis stage
For each acoustic file, generate measured duration, peak/RMS, silence boundaries, transient profile, and audio-derived pitch/chord confidence. Then audition representative files and mark each record `UNREVIEWED`, `AUDIO_REVIEWED`, `APPROVED_FOR_MAPPING`, or `EXCLUDED`.

## Release gate
Do not test the plugin, presets, sound engine, sound quality, or final build until all audio libraries are integrated and all 500 core factory presets are created and integrated.
