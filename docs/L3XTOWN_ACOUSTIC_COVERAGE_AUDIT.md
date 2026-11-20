# L3XTOWN GUITAR — Acoustic Chord Coverage Audit (Filename Metadata)

Status: deterministic filename/manifest audit only. No audio was auditioned or analyzed. This report identifies coverage and naming gaps; it does not certify the sounding pitch, chord voicing, or articulation.

## Scope and source
- Source: `L3XTOWN_SAMPLE_MAP.csv`, 387 rows.
- Acoustic families: ALL MARTIN (120 after the owner-confirmed additions) and ALL TAYLOR (121 after the owner-confirmed additions), 241 files total. The committed source-map snapshot predates these additions. The committed source-map snapshot predates these additions.
- Chord roots normalized for comparison: A, A#, B, C, C#, D, D#, E, F, F#, G, G#.
- Cyrillic `С` at the beginning of a filename was treated as Latin `C` for analysis only. Original filenames remain unchanged.

## Coverage by family and folder label

| Family | Folder label | Files | Filename-labelled coverage |
|---|---|---:|---|
| ALL MARTIN | ROOT | 25 | 12 major + 12 minor roots, plus one C minor 7-labelled file |
| ALL MARTIN | 7 | 23 | 12 maj7 roots; 11 min7 roots |
| ALL MARTIN | Вверх | 24* | 12 major + 12 minor labels (owner-confirmed correction) |
| ALL MARTIN | кода | 24 | 12 major + 12 minor labels |
| ALL MARTIN | сус | 24 | 12 major + 12 minor labels |
| ALL TAYLOR | ROOT | 24 | 12 major + 12 minor labels |
| ALL TAYLOR | 7 | 24 | 12 maj7 + 12 min7 roots |
| ALL TAYLOR | вверх | 24* | 12 major + 12 minor labels (owner-confirmed correction) |
| ALL TAYLOR | Кода | 25 | 13 major + 12 minor labels; A major has two takes |
| ALL TAYLOR | Сус | 23 | 11 major + 12 minor labels |

Folder labels such as `сус` are retained as source-folder labels only. They do not prove that the recordings contain sus2/sus4 voicings; filenames in these folders are predominantly labelled maj/min.

## Missing filename-labelled combinations

### ALL MARTIN
- ROOT: none in the 12-root major/minor set; one additional C min7-labelled file is present.
- 7: C min7 is absent.
- Вверх: none; A# maj, D# maj, and D# min are now present (owner-confirmed correction).
- кода: none in the 12-root major/minor set.
- сус: none in the 12-root major/minor set.

### ALL TAYLOR
- ROOT: none in the 12-root major/minor set.
- 7: none in the 12-root maj7/min7 set.
- вверх: none; D# maj and D# min are now present (owner-confirmed correction).
- Кода: none; A maj has two takes.
- Сус: A maj is absent.

## User-confirmed coverage notes (2026-11-16)

The project owner has separately confirmed the following filename-level gaps and variation candidate:
- ALL MARTIN / 7: C min7 absent.
- ALL MARTIN / Вверх: A# maj, D# maj, and D# min are now present; the previous missing-coverage entries are closed.
- ALL TAYLOR / вверх: D# maj and D# min are now present; the previous missing-coverage entries are closed.
- ALL TAYLOR / Сус: A maj absent.
- ALL TAYLOR / Кода: two A maj takes are present and should be retained as separate candidates for performance variation.

These confirmations agree with the filename audit above. They do not change the source files or establish audio-verified chord content. The two A maj takes remain candidates only until their waveforms/audio are compared; if genuinely distinct and musically usable, they can be mapped as round-robin or alternate takes.

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
