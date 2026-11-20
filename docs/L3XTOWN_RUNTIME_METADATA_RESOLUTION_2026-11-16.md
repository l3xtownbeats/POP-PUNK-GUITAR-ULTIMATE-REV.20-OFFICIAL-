# L3XTOWN GUITAR — Runtime Metadata and Path Resolution

Date: 2026-11-16
Repository: `l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE`

## Verified outcome

The runtime manifest was reconciled against `L3XTOWN_FULL_INVENTORY.csv` using exact SHA-256 identity. The full inventory contains 393 source path records representing 387 unique audio contents. All 387 runtime records now have technical metadata sourced from the matching WAV inventory record.

| Measure | Result |
|---|---:|
| Full inventory path records | 393 |
| Unique SHA-256 contents | 387 |
| Runtime manifest records | 387 |
| Previously ambiguous technical metadata conflicts resolved | 112 |
| Previously ambiguous-but-identical metadata matches upgraded to hash matches | 149 |
| Runtime records matched to one source path | 381 |
| Runtime records with duplicate-content path aliases | 6 |
| Unresolved metadata records | 0 |
| Missing SHA-256 matches | 0 |
| Source byte-count mismatches | 0 |
| WAV metadata disagreements between duplicate aliases | 0 |

## Two source-path corrections

Exact SHA-256 matching identified two stale runtime paths. Their paths and filenames have been corrected to the paths recorded by the current full WAV inventory:

| Sample ID | Previous runtime path | Corrected inventory path |
|---|---|---|
| `fbf8432be322b3fd` | `Гитары - Акустика/ALL TAYLOR/Кода/A maj кода (1).wav` | `Гитары - Акустика/ALL TAYLOR/Кода/A maj кода.wav` |
| `f47171e13cb0e0d6` | `Гитары - Акустика/ALL TAYLOR/Кода/A maj кода (2).wav` | `Гитары - Акустика/ALL TAYLOR/Сус/A maj cус.wav` |

## Duplicate-content aliases

Six hashes each occur at two source paths. Every alias pair has identical byte size, sample rate, channel count, bit depth, and duration. The runtime manifest retains one canonical path per unique content hash; all original paths remain in the full inventory.

| SHA-256 | Canonical runtime path | Alternate path |
|---|---|---|
| `EC0DCDE43FCF366CE36976D80CA9E7C506BF8696165F666CCABEF67F5AB8DF73` | `Гитары - Акустика/ALL MARTIN/A# maj.wav` | `Гитары - Акустика/ALL MARTIN/Вверх/A# maj верх.wav` |
| `7D7738437A779681BE518CC5FB2BF1C7EDF9C51343E5DF5F999BA9F5C1F7311A` | `Гитары - Акустика/ALL MARTIN/D# maj.wav` | `Гитары - Акустика/ALL MARTIN/Вверх/D# maj верх.wav` |
| `D466521CA52B6373C03EF475272832540DAB0F0BD67601DA97155683F5FB783D` | `Гитары - Акустика/ALL MARTIN/D# min.wav` | `Гитары - Акустика/ALL MARTIN/Вверх/D# min верх.wav` |
| `487A5E243CAD2D01F18B79713FB46BCD8807E81ADABA449A38FD4C6D60513BA7` | `Гитары - Акустика/ALL MARTIN/С min7.wav` | `Гитары - Акустика/ALL MARTIN/7/С min 7.wav` |
| `AAF5AD8FDC4E99278DB42A9E08B856D4AD88D57A2AD49AA7BDD411C0D5E7C145` | `Гитары - Акустика/ALL TAYLOR/D# maj.wav` | `Гитары - Акустика/ALL TAYLOR/вверх/D# maj верх.wav` |
| `1DAF89190FC14C20388657C065029E33DC5E9AB994B93CDBB78050079533E453` | `Гитары - Акустика/ALL TAYLOR/D# min.wav` | `Гитары - Акустика/ALL TAYLOR/вверх/D# min верх.wav` |

## Matching rules now encoded in the manifest

- `MATCHED_SHA256_UNIQUE_PATH`: exact SHA-256 match with one inventory path.
- `MATCHED_SHA256_DUPLICATE_CONTENT`: exact SHA-256 match with multiple source paths containing identical bytes and identical technical metadata.
- Sample rate, channels, bit depth, duration, source folder, filename, and relative path are taken from the full inventory record matched by SHA-256.
- Duration and size values use decimal-point numeric formatting in the runtime manifest.

## Safety and development gate

This was a metadata-only reconciliation. No original WAV file was moved, renamed, deleted, or modified. No audio audition, waveform quality test, plugin test, preset test, engine test, or final build test was run.

The approved gate remains unchanged: complete audio-library intake and BASIC LIBRARY integration (10–12 GB), then create and integrate all 500 core factory presets using BASIC LIBRARY alone. Plugin, preset, engine, sound-quality, and final-build tests remain blocked until those steps are complete.
