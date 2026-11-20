# Generate the authoritative full-path L3XTOWN inventory

The current source inventory has flattened folder names. This script rebuilds the inventory from the actual local WAV files, so each row contains the complete relative path and measured WAV header values.

## Files
- Script: `tools/build_l3xtown_full_inventory.py`
- Input map: `L3XTOWN_SAMPLE_MAP.csv`
- Library root on the user's Windows PC: `F:\POP PUNK GUITAR ULTIMATE\Samples\SourceLibraries\L3XTOWN GUITAR`

## Run on Windows

Open Command Prompt in the repository root and run:

```bat
py tools\build_l3xtown_full_inventory.py --root "F:\POP PUNK GUITAR ULTIMATE\Samples\SourceLibraries\L3XTOWN GUITAR" --sample-map "L3XTOWN_SAMPLE_MAP.csv" --out "L3XTOWN_FULL_INVENTORY.csv" --report "L3XTOWN_INVENTORY_RECONCILIATION.csv"
```

If the repository is not on the PC, copy the script and `L3XTOWN_SAMPLE_MAP.csv` into a working folder first. Adjust only the `--root` value if the library has moved.

## What it does
- Reads the exact full relative path from each SAMPLE_MAP category plus filename.
- Locates each WAV under the supplied library root.
- Recalculates file byte size and SHA-256.
- Reads sample rate, channels, bit depth, frame count, and duration from the WAV header.
- Writes a full inventory and a reconciliation report as UTF-8 with BOM for convenient Excel opening.
- Never modifies, renames, trims, converts, or deletes source WAV files.

## Review rules
- Expected SHA-256 must match actual SHA-256 before treating a file as the original source.
- Missing files, byte mismatches, SHA mismatches, and unsupported WAV headers must be reviewed.
- The script uses Python's standard `wave` module. If a WAV uses an unsupported header encoding, its row is retained and flagged rather than guessed.
- Upload the generated `L3XTOWN_FULL_INVENTORY.csv` and `L3XTOWN_INVENTORY_RECONCILIATION.csv` to the repository root when complete. The manifest can then be regenerated with exact full-path matching.

## Development gate
This inventory generation is not plugin testing or audio audition. The existing project gate remains unchanged: do not test the plugin, presets, engine, sound quality, or final build until the required libraries are integrated and all 500 core factory presets are created and integrated.
