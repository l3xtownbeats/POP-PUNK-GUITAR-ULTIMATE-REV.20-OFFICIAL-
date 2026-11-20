# L3XTOWN GUITAR — Preliminary Sample Map Analysis

Status: metadata analysis only. The user has confirmed that these are their own guitar recordings. No audio audition, transient detection, pitch verification, articulation verification, sample conversion, plugin testing, or build testing has been performed.

## Source and ownership declaration
- Library designation: USER-OWNED ORIGINAL SOURCE MATERIAL.
- The user explicitly confirms that the 387 WAV recordings were recorded by the user on their own guitars.
- This is a user-declared ownership/source statement, not an independent legal audit.
- No third-party sample-library licence is required for the user's own recordings. Before redistribution, still check that no third-party backing tracks, loops, compositions, or other protected material are embedded in the recordings.

## Source snapshot
- Inventory CSV rows: 387
- Sample map rows: 387
- File type counts: {"wav":387}
- Distinct SHA256 values: 387 / 387
- Total bytes from sample map: 846265382 (about 807 MiB)
- The CSV reports are committed in the repository root as `L3XTOWN_INVENTORY.csv` and `L3XTOWN_SAMPLE_MAP.csv`.
- Source paths point to the user's local Windows drive and are not portable runtime paths.

## Top-level content groups
- `Гитары - Акустика\ALL MARTIN`: 117 files
- `Гитары - Акустика\ALL TAYLOR`: 118 files
- `Гитары - Квинты\01 ENGL`: 43 files
- `Гитары - Квинты\02 MESA`: 43 files
- `Гитары - Квинты\03 EVH`: 12 files
- `Гитары - Квинты\04 MARSHALL GIBSON`: 49 files
- `Гитары - Квинты\05 FX`: 5 files

## Interpretation limits
Folder names and filenames are useful intake metadata only. They do not establish exact pitch, root note, tempo, key, articulation, loop boundaries, tuning, velocity layer, or legal status of any third-party material captured in a recording. These fields must remain UNKNOWN until verified from audio and source review.

## Next intake work
1. Preserve original recordings and hashes unchanged.
2. Build a portable relative-path manifest; do not rely on `F:\...` absolute paths.
3. Add audio-derived metadata (duration, sample rate, channels, bit depth, peak/RMS, leading/trailing silence, pitch/key where reliably detectable).
4. Listen to representative samples in each folder and confirm actual playing technique.
5. Flag any third-party backing material or protected content, if present.
6. Map the verified user-owned recordings into BASIC LIBRARY design.

## Release gate
The approved rule remains: do not test the plugin, presets, engine, sound quality, or final build until all audio libraries are integrated and all 500 core factory presets are created and integrated.
