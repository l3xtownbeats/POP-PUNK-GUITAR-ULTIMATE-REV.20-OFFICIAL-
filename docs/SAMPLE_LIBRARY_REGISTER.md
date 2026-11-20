# Sample Library Register

## L3XTOWN GUITAR

**Classification: USER-OWNED ORIGINAL SOURCE MATERIAL (owner-confirmed)**

The user has explicitly confirmed that the recordings in this library were recorded by the user on their own guitars. This is a user-declared ownership/source statement, not an independent legal audit.

| Field | Recorded value |
|---|---|
| Library owner/source | User-recorded original guitar performances; user-confirmed |
| Library designation | USER-OWNED ORIGINAL SOURCE MATERIAL |
| Original archive path (user's Windows PC) | `F:\\POP PUNK GUITAR ULTIMATE\\Temp\\L3XTOWN GUITAR.zip` |
| Extracted path (user's Windows PC) | `F:\\POP PUNK GUITAR ULTIMATE\\Samples\\SourceLibraries\\L3XTOWN GUITAR` |
| Source path records | 393 WAV paths |
| Unique audio contents | 387 unique SHA-256 hashes |
| Exact duplicate-content aliases | 6 pairs (12 path records) |
| Total size across all source paths | 857,164,526 bytes |
| Unique-content size | 846,265,382 bytes (approximately 807 MiB) |
| Audio format | 44.1 kHz, stereo, 24-bit (WAV-header inspection) |
| Total duration | Approximately 53.28 minutes as previously reported; duration is metadata, not usable musical length |
| Inventory integrity | 393/393 size matches; 393/393 SHA-256 matches; 393/393 WAV headers readable |
| Ownership/source status | User-confirmed original recordings |
| Third-party content screening | Check separately for any third-party compositions, backing tracks, loops, or other protected material captured in the recordings |
| Repository asset status | WAV audio files are not uploaded; inventory, sample maps, runtime manifest, and integration plan are present in the repository |

## Reported folder families

- Acoustic guitars:
  - ALL MARTIN
  - ALL TAYLOR
- Electric and related material:
  - 01 ENGL
  - 02 MESA
  - 03 EVH
  - 04 MARSHALL GIBSON
  - 05 FX

The folder families are source-organization hints only. They do not prove exact notes, chord voicings, articulations, velocity layers, tempo, or musical usability. Those properties must be established through non-destructive inspection and listening before final sample mapping.

## Repository intake reports and integration artifacts

- `L3XTOWN_SAMPLE_MAP.csv` — original path/name/hash map.
- `L3XTOWN_FULL_INVENTORY.csv` — 393 source path records with SHA-256 and WAV-header metadata.
- `L3XTOWN_RUNTIME_MANIFEST.csv` — 387 unique-content runtime records.
- `L3XTOWN_FACTORY_INTEGRATION_PLAN.csv` — 393 proposed source-to-FACTORY path mappings.
- `docs/L3XTOWN_BASIC_LIBRARY_INTEGRATION_READINESS.md` — integration readiness and remaining gates.

Absolute Windows paths are source provenance only. Runtime references must use portable relative paths and stable content identity.

## Rights and usage handling

Because the user confirms these are their own guitar recordings, a third-party sample-library licence review is not required for these recordings. Preserve the user's ownership/source declaration in project records. Before redistribution, still check that the recordings do not contain third-party backing tracks, loops, compositions, or other protected material, and document any relevant performer/recording rights.

## Next intake actions

1. Preserve the original WAVs and recorded SHA-256 values unchanged.
2. Run the local read-only staging preflight against the actual Windows source folder and compare it with the committed integration plan.
3. Only after explicit approval, create verified FACTORY copies without moving or modifying originals.
4. Verify audio content non-destructively: pitch, voicing, tuning, articulation, tempo, transient, usable region, and musical role.
5. Map only approved content into BASIC LIBRARY; keep EXPANDED LIBRARY optional.
6. Track actual installed bytes toward the 10–12 GB BASIC LIBRARY target.

## Release gate

Do not test the plugin, presets, engine, sound quality, or final build until all required audio libraries are integrated and all 500 core factory presets are created and integrated using BASIC LIBRARY alone.
