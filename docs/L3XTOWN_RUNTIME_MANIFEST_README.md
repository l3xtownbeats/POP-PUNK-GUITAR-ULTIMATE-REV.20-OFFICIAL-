# L3XTOWN Runtime Manifest — Readme

File: `L3XTOWN_RUNTIME_MANIFEST.csv`

## Purpose
Portable per-content runtime manifest for the user-owned L3XTOWN GUITAR WAV library. It consolidates stable identity from `L3XTOWN_SAMPLE_MAP.csv`, exact source paths and WAV technical metadata from `L3XTOWN_FULL_INVENTORY.csv`, and one canonical path per unique SHA-256 content hash.

## Current reconciliation (2026-11-16)
- Full inventory: 393 source path records.
- Unique SHA-256 contents: 387.
- Runtime manifest: 387 rows, one per unique content hash.
- `MATCHED_SHA256_UNIQUE_PATH`: 381 rows.
- `MATCHED_SHA256_DUPLICATE_CONTENT`: 6 rows. Each of these hashes exists at two source paths with identical bytes and identical WAV technical metadata.
- Unresolved metadata rows: 0.
- Missing hash matches: 0.
- Source byte-count mismatches: 0.
- All 112 previously conflicting metadata rows were resolved by exact SHA-256 matching.
- All 149 previously ambiguous-but-identical metadata rows were upgraded to exact hash matches.
- Two stale runtime paths were corrected against the full inventory.

## Matching authority
The full inventory is authoritative for:
- exact relative source path and original filename;
- sample rate, channel count, bit depth, duration, and file size;
- WAV header readability.

The SHA-256 hash is the join key. Do not join by filename or leaf folder alone. For duplicate-content hashes, the manifest keeps one canonical path; alternate paths remain recorded in the full inventory for traceability.

## Status values
- `MATCHED_SHA256_UNIQUE_PATH`: the hash resolves to exactly one source path.
- `MATCHED_SHA256_DUPLICATE_CONTENT`: the hash resolves to multiple paths with identical file bytes and matching technical metadata.

## Preservation and development gate
This is a metadata manifest, not an audio-quality certification. Original WAV files are immutable: do not move, rename, delete, or modify them during metadata processing. No plugin, preset, audio-engine, sound-quality, or final-build tests may run until audio-library intake and BASIC LIBRARY integration (10–12 GB) are complete and all 500 core factory presets have been created and integrated using BASIC LIBRARY alone.

See `docs/L3XTOWN_RUNTIME_METADATA_RESOLUTION_2026-11-16.md` for the detailed reconciliation record.
