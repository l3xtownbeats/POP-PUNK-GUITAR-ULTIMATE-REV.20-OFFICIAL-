# ALL MARTIN / ALL TAYLOR — Acoustic Folder Matrix Audit
Date: 2026-11-16
Source: `L3XTOWN_FULL_INVENTORY.csv` on `main`
Audit type: read-only inventory/path and SHA-256 cross-check; no audio listening or pitch analysis.

## Coverage matrix

| Family | Folder | Inventory paths | Unique SHA-256 | Path/header state |
|---|---|---:|---:|---|
| ALL MARTIN | ROOT | 25 | 25 | Present in committed inventory |
| ALL MARTIN | 7 | 24 | 24 | Present in committed inventory |
| ALL MARTIN | Вверх | 24 | 21 | Present; 3 cross-folder hash aliases |
| ALL MARTIN | кода | 24 | 24 | Present in committed inventory |
| ALL MARTIN | сус | 24 | 24 | Present in committed inventory |
| ALL TAYLOR | ROOT | 24 | 24 | Present in committed inventory |
| ALL TAYLOR | 7 | 24 | 24 | Present in committed inventory |
| ALL TAYLOR | вверх | 24 | 22 | Present; 2 cross-folder hash aliases |
| ALL TAYLOR | Кода | 24 | 24 | Present in committed inventory |
| ALL TAYLOR | Сус | 24 | 24 | Present in committed inventory |
| **TOTAL** | | **241** | **235** | **6 repeated-hash pairs** |

## Exact cross-folder SHA-256 aliases

The following path pairs have identical file contents. They must remain separate source-path records for traceability, but must not be counted as separate recordings or round-robin takes.

| Family | First path | Alias path | Interpretation |
|---|---|---|---|
| ALL MARTIN | ROOT/A# maj.wav | Вверх/A# maj верх.wav | Same bytes; upstroke take not independently represented |
| ALL MARTIN | ROOT/D# maj.wav | Вверх/D# maj верх.wav | Same bytes; upstroke take not independently represented |
| ALL MARTIN | ROOT/D# min.wav | Вверх/D# min верх.wav | Same bytes; upstroke take not independently represented |
| ALL MARTIN | ROOT/С min.wav | 7/С min 7.wav | Same bytes; seventh-folder entry is an alias, not a separate take |
| ALL TAYLOR | ROOT/D# maj.wav | вверх/D# maj верх.wav | Same bytes; upstroke take not independently represented |
| ALL TAYLOR | ROOT/D# min.wav | вверх/D# min верх.wav | Same bytes; upstroke take not independently represented |

## User-confirmed corrections retained

Do not reopen these as missing files:
- ALL TAYLOR / вверх: D# maj, D# min.
- ALL MARTIN / Вверх: A# maj, D# maj, D# min.

All five paths are present in the committed inventory. The hash audit above adds a separate warning: each is byte-identical to its matching ROOT file. This is a content-identity observation, not a missing-file finding.

## Findings and limits

1. All ten acoustic folders have the expected inventory path count shown in the matrix (24 each, except ALL MARTIN ROOT with 25).
2. 241 acoustic path records resolve to 235 unique byte contents; six exact duplicate pairs occur across folders.
3. No source WAV was changed, moved, renamed, deleted, or copied by this audit.
4. The committed inventory reports readable WAV headers and matching size/SHA-256 for its 393 source records. This audit relies on that stored snapshot; it does not freshly inspect the user's F: drive.
5. Filenames and folder labels do not prove chord voicing, tuning, upstroke direction, coda performance, or sus voicing. All such audio-content attributes remain **UNREVIEWED**.
6. The five user-corrected upstroke paths are present, but the current snapshot does not contain distinct performances for those labels. If distinct upstroke recordings were intended, the local files must be checked and new distinct source takes supplied; do not duplicate or fabricate recordings.

## Next gate

Perform a fresh local, read-only preflight on the user's Windows PC against the actual source folder. Compare all 241 acoustic paths and hashes to this inventory. Only after that preflight should audio-content review begin. Do not start plugin, preset, sound-engine, sound-quality, or final-build tests before the established BASIC LIBRARY / 500-preset release gate is met.
