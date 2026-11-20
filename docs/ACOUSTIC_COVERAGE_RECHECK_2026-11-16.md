# Acoustic Coverage Recheck — User Corrections
Date: 2026-11-16
Branch: tool/library-manager-mvp
Source snapshot: `L3XTOWN_FULL_INVENTORY.csv` on `main`

## User-confirmed corrections

The user explicitly confirmed that the following previously reported missing entries have been corrected:

- ALL TAYLOR / Вверх: D# maj, D# min.
- ALL MARTIN / Вверх: A# maj, D# maj, D# min.

These are treated as present at the path/filename level. Do not reopen them as missing-source gaps.

## Repository inventory cross-check

The currently committed full inventory contains all five corresponding paths. Their WAV headers are readable and each row reports SIZE_MATCH and SHA256_MATCH.

| Family | Folder | Filename | Path status | Content identity |
|---|---|---|---|---|
| ALL TAYLOR | вверх | D# maj верх.wav | Present | Exact SHA-256 alias of ALL TAYLOR ROOT/D# maj.wav |
| ALL TAYLOR | вверх | D# min верх.wav | Present | Exact SHA-256 alias of ALL TAYLOR ROOT/D# min.wav |
| ALL MARTIN | Вверх | A# maj верх.wav | Present | Exact SHA-256 alias of ALL MARTIN ROOT/A# maj.wav |
| ALL MARTIN | Вверх | D# maj верх.wav | Present | Exact SHA-256 alias of ALL MARTIN ROOT/D# maj.wav |
| ALL MARTIN | Вверх | D# min верх.wav | Present | Exact SHA-256 alias of ALL MARTIN ROOT/D# min.wav |

## Interpretation

- The corrections are accepted: all five requested path/filename entries exist in the committed inventory.
- The five files are byte-identical to their respective ROOT counterparts according to SHA-256. They are therefore path aliases, not independently recorded alternate performances in this inventory snapshot.
- Preserve every source path record for traceability, but do not count these aliases as separate takes, round-robin variations, or independent upstroke performances.
- The filename/folder labels do not prove the actual playing articulation. Upstroke status and chord voicing remain **UNREVIEWED** until the audio is inspected/listened to.
- This report does not alter source WAVs, staging copies, the sample map, or the integration plan.

## Next action

Run a fresh read-only local preflight against the user's actual Windows source folder and current sample map. Confirm the same file sizes and hashes. If the user intended genuinely different upstroke performances, the five paths need to point to distinct recordings; do not manufacture or rename audio to make the map appear complete.
