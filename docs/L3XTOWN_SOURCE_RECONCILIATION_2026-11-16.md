# L3XTOWN GUITAR — Source Reconciliation Update
Date: 2026-11-16
Repository: l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE
Branch: main

## Scope
Read-only reconciliation of the committed `L3XTOWN_SAMPLE_MAP.csv`, `L3XTOWN_INVENTORY.csv`, and `L3XTOWN_RUNTIME_MANIFEST.csv`. No WAV audio was opened, auditioned, modified, moved, renamed, deleted, or uploaded. No plugin, preset, engine, sound-quality, or final-build tests were run.

## Verified current counts

| Artifact / measure | Verified result |
|---|---:|
| SAMPLE_MAP path/name records | 393 |
| Distinct SHA-256 contents in SAMPLE_MAP | 387 |
| Exact duplicate-content groups | 6 |
| Duplicate path records participating in those groups | 12 |
| INVENTORY rows | 387 |
| RUNTIME_MANIFEST rows | 387 |
| Distinct SHA-256 values in RUNTIME_MANIFEST | 387 |
| SAMPLE_MAP unique hashes missing from RUNTIME_MANIFEST | 0 |
| RUNTIME_MANIFEST hashes absent from SAMPLE_MAP | 0 |

The runtime manifest therefore covers every unique audio content hash represented by the current sample map exactly once. The six duplicate-content groups remain represented as separate source paths in SAMPLE_MAP; the runtime manifest is a unique-content manifest, not a complete path-alias manifest.

## Current source-family path counts

| Source family | Path records |
|---|---:|
| ALL MARTIN | 121 |
| ALL TAYLOR | 120 |
| 01 ENGL | 43 |
| 02 MESA | 43 |
| 03 EVH | 12 |
| 04 MARSHALL GIBSON | 49 |
| 05 FX | 5 |
| **Total** | **393** |

## Runtime metadata-match status

| Status | Rows |
|---|---:|
| MATCHED_UNIQUE | 126 |
| MATCHED_AMBIGUOUS_IDENTICAL_METADATA | 149 |
| AMBIGUOUS_METADATA_CONFLICT | 112 |
| **Total** | **387** |

The 112 conflicting matches still have blank technical metadata by design. Do not fill them using sibling files or filename guesses. The 149 identical-metadata ambiguous matches have safe copied technical values, but their exact inventory-row identity remains unresolved.

## Documentation drift identified

Some earlier documents still describe the older 387-path snapshot or earlier family counts. They should be treated as historical snapshots until individually refreshed:
- `docs/SAMPLE_LIBRARY_REGISTER.md` says SAMPLE_MAP has 387 entries.
- `docs/L3XTOWN_UNIFIED_SOURCE_TECHNICAL_PASSPORT.md` says both source CSVs have 387 rows and lists older acoustic family counts.
- `docs/L3XTOWN_RUNTIME_MANIFEST_README.md` describes the earlier 387-row source-map snapshot.
- `docs/L3XTOWN_ACOUSTIC_COVERAGE_AUDIT.md` describes older acoustic counts (117 Martin / 118 Taylor), whereas the current map has 121 / 120 path records.
- `docs/L3XTOWN_FACTORY_STAGING_AUDIT.md` already records the current 393 path records and 387 unique contents and is consistent with this reconciliation.

This update does not silently rewrite those documents; it records the verified current baseline and identifies the files needing a controlled refresh.

## Next permitted work
1. Refresh stale metadata documentation against the current CSV files, preserving historical notes where needed.
2. Resolve the 112 inventory conflicts by regenerating a full-relative-path inventory or reading each source WAV header directly.
3. Preserve all six duplicate-content path pairs for traceability; do not delete or treat them as independent performances.
4. Continue non-destructive audio metadata and content review only when the actual WAV payload is available.

## Development gate and preservation
The approved production sequence remains unchanged: complete audio-library intake, license review, BASIC LIBRARY integration (10–12 GB target), then create and integrate all 500 core factory presets using BASIC LIBRARY alone. Only after those steps may plugin, preset, audio-engine, sound-quality, and final-build testing begin.

All original source files and SHA-256 identities remain immutable. This report is a metadata reconciliation only and is not an audio-content or sound-quality certification.
