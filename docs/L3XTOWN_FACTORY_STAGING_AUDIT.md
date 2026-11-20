# L3XTOWN GUITAR — FACTORY Staging Audit

Status: source-map reconciliation and non-destructive staging plan. This is NOT audio-content analysis.

## Current SAMPLE_MAP snapshot

The current `L3XTOWN_SAMPLE_MAP.csv` contains **393 source-path records** and **387 distinct SHA-256 contents**. The sum of the per-path file sizes is **857,164,526 bytes** (approximately 817.4 MiB). The prior inventory/runtime-manifest snapshot contains 387 records because it represents the 387 unique audio contents, while the current map retains all 393 path/name entries.

This reconciles as follows:
- 393 path/name records are retained.
- 387 unique byte-identical contents are represented by SHA-256.
- 6 exact duplicate-content groups each have two path/name records.
- No duplicate is automatically deleted or omitted from FACTORY staging.

## Exact duplicate-content pairs

The current map reports these pairs with identical SHA-256 values:

| Source family | First path label | Second path label | Interpretation |
|---|---|---|---|
| ALL MARTIN | Root `A# maj.wav` | `Вверх/A# maj верх.wav` | Exact byte duplicate |
| ALL MARTIN | Root `D# maj.wav` | `Вверх/D# maj верх.wav` | Exact byte duplicate |
| ALL MARTIN | Root `D# min.wav` | `Вверх/D# min верх.wav` | Exact byte duplicate |
| ALL MARTIN | Root `С min7.wav` | `7/С min 7.wav` | Exact byte duplicate |
| ALL TAYLOR | Root `D# maj.wav` | `вверх/D# maj верх.wav` | Exact byte duplicate |
| ALL TAYLOR | Root `D# min.wav` | `вверх/D# min верх.wav` | Exact byte duplicate |

These are exact file-content matches, not merely similar names. Keep both source records and both filenames for traceability, but do not treat the pair as two independent performances, round-robin takes, or confirmed separate articulations.

## Source group counts (393 path records)

| Source group | Records |
|---|---:|
| ALL MARTIN | 121 |
| ALL TAYLOR | 120 |
| 01 ENGL | 43 |
| 02 MESA | 43 |
| 03 EVH | 12 |
| 04 MARSHALL GIBSON | 49 |
| 05 FX | 5 |
| **Total** | **393** |

The source-folder labels and filenames provide an initial organisational structure only. They do not prove actual guitar tone, pitch, chord voicing, tuning, articulation, tempo, or usable loop boundaries.

## FACTORY staging taxonomy

The staging script routes files into a copy-only tree:

- `FACTORY/ACOUSTIC/ALL_MARTIN/`
  - `ROOT_CHORD_LABELS`
  - `SEVENTH_CHORD_LABELS`
  - `UPSTROKE_LABELS`
  - `CODA_LABELS`
  - `SUS_LABELS`
- `FACTORY/ACOUSTIC/ALL_TAYLOR/` — same subfolders.
- `FACTORY/ELECTRIC/ENGL/`
  - `POWER_CHORD_LABELS`, `CODA_LABELS`, `NOTE_LABELS`
- `FACTORY/ELECTRIC/MESA/` — same labelled groups.
- `FACTORY/ELECTRIC/EVH/ARPEGGIO_75BPM_LABEL/`
- `FACTORY/ELECTRIC/MARSHALL_GIBSON/`
  - `POWER_CHORD_LABELS`, `CODA_LABELS`, `NOTE_LABELS`, `SLIDE_LABELS`
- `FACTORY/ELECTRIC/FX/FX_SOURCE_LABELS/`

The suffix `_LABELS` is intentional: it prevents a folder name from being mistaken for an audio-verified articulation or content type.

## Local execution

The repository tool `tools/prepare_l3xtown_factory_staging.py`:
1. Reads the current SAMPLE_MAP.
2. Resolves each source file under the specified library root.
3. Rechecks byte size and SHA-256 against the map.
4. Performs a read-only preflight by default.
5. With explicit `--copy`, copies all 393 path records to FACTORY, verifies each copy, and writes `FACTORY_SOURCE_ROUTING.csv`.
6. Never moves, renames, deletes, or modifies original WAV files.
7. Flags duplicate-content groups in the routing manifest.
8. Marks all content `UNREVIEWED` for audio classification.

Example:
```powershell
py .\prepare_l3xtown_factory_staging.py
py .\prepare_l3xtown_factory_staging.py --copy
```

Use the actual path to the downloaded script if it is not in the current directory. If the map is not on the Desktop, pass `--map "FULL\\PATH\\TO\\L3XTOWN_SAMPLE_MAP.csv"`.

## What remains unverified

No audio was auditioned or analysed in this audit. The next true sound-classification stage requires access to the WAV audio itself and should measure/listen for:
- actual instrument/tone character (not infer it from ENGL/MESA/EVH/MARSHALL folder names);
- actual pitch, chord voicing, tuning and octave;
- articulation and stroke direction;
- transient, silence, decay, usable region and loop/one-shot/phrase role;
- actual tempo and bar length for tempo-labelled material.

Only after that review should final sonic categories such as clean, crunch, overdrive, distortion, palm mute, lead, rhythm, acoustic steel/nylon, slide, and FX be assigned.

## Preservation and project gate

- Keep the source library immutable.
- Keep every source path and original filename in the routing manifest.
- Never invent SHA-256, size, audio metadata, or licence status.
- This staging work is library intake only. Do not test the plugin, presets, sound engine, sound quality, or final build until all required audio libraries are integrated and all 500 core factory presets have been created and integrated.
