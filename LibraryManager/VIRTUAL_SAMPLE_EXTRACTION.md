# Virtual Sample Extraction

The `virtual_sample_extractor.py` module performs a first-pass scan of a long, already guitar-filtered PCM WAV. It detects broad sound-active regions and writes optional JSON sidecars beneath:

`Samples/Import Sample Guitar/VIRTUAL_CANDIDATES/RIFF_CANDIDATES/`

It does **not** split, copy, move, rename, overwrite, or modify audio. Each sidecar stores the original file path and SHA-256, sample-accurate start/end offsets, format metadata, and a deterministic RMS/ZCR envelope fingerprint. Playback reads the selected frame range from the original WAV and should verify the source hash first.

## Run

```bash
python LibraryManager/virtual_sample_extractor.py "path/to/guitar_riff.wav" --guitar-source-confirmed --import-root "Samples/Import Sample Guitar"
```

The confirmation flag is mandatory: Piano, Bell and Drum must be excluded by the upstream instrument filter before this stage. The current version detects sound-active regions only; it does not claim verified riffs, chord names, note maps, articulations, bars or loop points. Every result remains `NEEDS_MUSICAL_REVIEW` and `UNREVIEWED` for licensing.

No item is automatically moved to `Samples/FACTORY`. Physical WAV extraction and final categorization require a later reviewed/approved step. The existing top-level `Samples` structure is unchanged.
