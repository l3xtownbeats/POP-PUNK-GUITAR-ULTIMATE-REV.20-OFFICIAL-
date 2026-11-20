# L3XTOWN Acoustic Local Preflight — Windows quick start

## Files required
Keep this layout together in one project folder:

- `RUN_L3XTOWN_ACOUSTIC_PREFLIGHT.bat`
- `L3XTOWN_FULL_INVENTORY.csv`
- `tools/preflight_l3xtown_acoustic_sources.py`

Download the BAT file and inventory from the repository root, and the Python script from the `tools` folder. Preserve the folder layout.

## Expected source library
The launcher uses the previously supplied path:

`F:\POP PUNK GUITAR ULTIMATE\Samples\SourceLibraries\L3XTOWN GUITAR`

If the library is stored elsewhere, edit the `LIBRARY_ROOT` line in the BAT file before running.

## Run
1. Install Python 3.10 or newer for Windows, with the Python Launcher (`py`).
2. Double-click `RUN_L3XTOWN_ACOUSTIC_PREFLIGHT.bat`.
3. Wait for the scan to finish. It may take a while because SHA-256 reads every selected WAV.
4. Send these two reports back for review:
   - `ACOUSTIC_LOCAL_PREFLIGHT.csv`
   - `ACOUSTIC_LOCAL_PREFLIGHT_SUMMARY.json`

Reports are written to:

`F:\POP PUNK GUITAR ULTIMATE\Reports\AcousticPreflight`

## Safety
- Read-only source scan.
- No source WAV is edited, moved, renamed, deleted, or copied.
- Reports are written outside the source library.
- A PASS confirms path, byte size, SHA-256 and a readable WAV header. It does not confirm musical correctness, tuning, chord identity, articulation, or listening quality.
- Unsupported WAV formats are marked for review; no conversion is attempted.

## Scope
Default mode checks ALL MARTIN and ALL TAYLOR acoustic paths from the inventory. The Python script also supports `--family all` for every inventory row.
