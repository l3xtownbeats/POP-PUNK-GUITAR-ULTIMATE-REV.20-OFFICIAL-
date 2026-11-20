# One-click L3XTOWN full inventory

Use `RUN_L3XTOWN_FULL_INVENTORY.bat` from the repository root on the Windows workstation.

The launcher:
- uses the portable Python at `%LOCALAPPDATA%\PythonPortable\python.exe`, falling back to the Windows `py` launcher;
- scans `F:\POP PUNK GUITAR ULTIMATE\Samples\SourceLibraries\L3XTOWN GUITAR`;
- reads `L3XTOWN_SAMPLE_MAP.csv` from the same folder as the launcher;
- runs the standard-library-only full inventory script;
- writes `L3XTOWN_FULL_INVENTORY.csv` and `L3XTOWN_INVENTORY_RECONCILIATION.csv` beside the launcher.

## Safety
This is a metadata/hash inventory only. It does not audition audio, run plugin/preset/engine tests, or modify, move, rename, delete, convert, or copy original WAV files. Existing outputs are replaced by the newly generated reports; keep a copy of any report you need to preserve before rerunning.

If the source folder is at a different location, stop and update only the `LIBRARY_ROOT` line in the BAT after confirming the correct path. Do not guess a replacement path.
