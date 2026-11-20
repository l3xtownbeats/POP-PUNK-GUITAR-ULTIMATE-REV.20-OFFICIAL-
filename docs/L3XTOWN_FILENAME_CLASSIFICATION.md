# L3XTOWN GUITAR — Filename-Based Technical Classification

Status: preliminary metadata classification from `L3XTOWN_INVENTORY.csv` (387 rows). This is not audio analysis. No sample was auditioned, waveform-inspected, pitch-detected, or altered. All musical labels below are inferred from folder/file names and must be verified later.

## Ownership and preservation
- Source: user-confirmed original guitar recordings made by the user on their own guitars.
- Preserve original WAV files and recorded SHA-256 values unchanged.
- Use portable relative paths in all future manifests; do not use the original absolute `F:\...` paths as runtime references.

## Technical format snapshot
- 387 WAV files.
- Inventory reports 44,100 Hz, stereo, 24-bit.
- The inventory reports approximately 6.86 seconds for the standard chord/note files and approximately 10.29 seconds for many coda files. These are metadata values, not confirmed usable loop lengths.

## Filename/folder classification

### Acoustic — ALL MARTIN (117 files)
| Subfolder label | Count | Preliminary interpretation |
|---|---:|---|
| Root / ALL MARTIN | 25 | Chord-labelled recordings; filenames include major/minor chords and one C minor 7 label |
| 7 | 47 | Seventh-chord-labelled recordings |
| Вверх | 21 | Upstroke-labelled chord recordings |
| кода | 24 | Coda-labelled chord recordings |
| сус | 24 | Sus-labelled chord recordings |

### Acoustic — ALL TAYLOR (118 files)
| Subfolder label | Count | Preliminary interpretation |
|---|---:|---|
| Root / ALL TAYLOR | 24 | Major/minor chord-labelled recordings |
| 7 | 24 | Seventh-chord-labelled recordings |
| вверх | 22 | Upstroke-labelled chord recordings |
| Кода | 25 | Coda-labelled chord recordings; includes two A major coda takes |
| Сус | 23 | Sus-labelled chord recordings |

### Electric / fifths and related material (152 files)
| Folder family | Subfolder label | Count | Preliminary interpretation |
|---|---|---:|---|
| 01 ENGL | Квинты | 45 | Fifth/power-chord-labelled recordings |
| 02 MESA | Квинты | 43 | Fifth/power-chord-labelled recordings |
| 03 EVH | Переборы 75 bpm | 12 | Arpeggio/picking-labelled recordings with 75 BPM folder label |
| 04 MARSHALL GIBSON | Ноты | 45 | Note-labelled recordings |
| 04 MARSHALL GIBSON | Слайды | 6 | Slide-labelled recordings |
| 05 FX | Root / FX | 5 | Transition/slide-labelled effects |

## Immediate observations / mapping cautions
1. Filename labels are not proof of the sounding pitch or chord voicing. Treat all root notes, chord qualities, and articulation labels as `UNVERIFIED` until audio-derived verification.
2. Some labels use Cyrillic `С` (visually similar to Latin C). Normalize for analysis only; never rename or overwrite original files.
3. Naming and whitespace are inconsistent (for example, extra spaces, `верх` vs `вверх`, and duplicate take suffixes). Keep the original filename as immutable source metadata and add normalized fields separately.
4. The two acoustic families have broadly parallel categories, but their counts and coverage differ. Do not silently fill missing chord/technique combinations by relabelling or stretching another sample.
5. The `Переборы 75 bpm` folder label is a tempo hint only; verify actual tempo and timing from audio before using tempo-synced playback.
6. `Квинты`, `Ноты`, `Слайды`, and `FX` are provisional semantic roles, not confirmed articulation mappings.

## Required next metadata fields
For every source asset, add separate fields without changing the source file:
- `source_relative_path`
- `source_sha256`
- `instrument_family` (acoustic/electric/unknown)
- `source_folder_label`
- `filename_original`
- `filename_normalized`
- `root_note_detected` and `root_note_confidence`
- `chord_quality_detected` and `chord_confidence`
- `articulation_detected` and `articulation_confidence`
- `tempo_bpm_detected` and `tempo_confidence`
- `duration_sec`, `sample_rate_hz`, `channels`, `bit_depth`
- `peak_dbfs`, `rms_dbfs`, leading/trailing silence
- `review_status` (UNREVIEWED / AUDIO_REVIEWED / APPROVED_FOR_MAPPING / EXCLUDED)
- `notes`

## Processing constraints
- Non-destructive analysis only; original WAVs remain untouched.
- Do not run plugin, preset, sound-engine, sound-quality, or final-build tests yet.
- Continue library intake and metadata work first. The release gate remains: all audio libraries integrated and all 500 core factory presets created/integrated before any such testing.
