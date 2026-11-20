# L3XTOWN GUITAR — Unified Source Technical Passport (Metadata Stage)

## Purpose and status
This document defines the source-of-truth record and runtime-manifest rules for the 387 user-recorded L3XTOWN GUITAR WAV files. This is a metadata consolidation stage only. No audio audition, waveform inspection, pitch detection, transient analysis, tuning analysis, or plugin playback test has been performed. Filename-derived classifications remain provisional.

## Source authority
- `L3XTOWN_SAMPLE_MAP.csv`: per-file category, filename, original absolute path, byte size, SHA-256.
- `L3XTOWN_INVENTORY.csv`: per-file folder, filename, sample rate, channel count, bit depth, duration, and size.
- Both source CSVs currently contain 387 and 387 data rows respectively.
- The map records the full category hierarchy; the inventory's `Folder` field records only a folder label. This can be ambiguous where the same leaf folder name occurs under different guitar families. Do not join rows using filename alone or leaf folder alone where more than one candidate exists.

## Library-level inventory
- Total source records: 387.
- Declared technical format counts from inventory: sample rates {"44100":387}, channels {"2":387}, bit depths {"24":387}.
- Parsed duration total from inventory: 3196.74 seconds (53.28 minutes), where the source uses comma decimal separators.
- Inventory size values sum to 806.59 MB (source CSV decimal-MB values; this is not a substitute for the byte total in SAMPLE_MAP).
- Family counts from SAMPLE_MAP:
- ALL MARTIN: 117
- ALL TAYLOR: 118
- 01 ENGL: 43
- 02 MESA: 43
- 03 EVH: 12
- 04 MARSHALL GIBSON: 49
- 05 FX: 5

## Per-file identity contract
Every source WAV must be represented by:
1. immutable source identity: original filename, source category, byte size, SHA-256;
2. portable relative path beneath the library root (never store a machine-specific `F:\...` path in the runtime manifest);
3. technical metadata: sample rate, channels, bit depth, duration;
4. audio-derived metadata, initially unset: measured pitch/root, octave, tuning, content class, articulation, tempo, bar length, start offset, usable region, loop/one-shot/phrase role, velocity layer, round-robin group, confidence and reviewer status;
5. mapping metadata: instrument family, MIDI note/range, articulation key-switch or control, preset eligibility, and explicit exclusion reason if not playable.

## Data integrity and reconciliation
- Preserve the original WAV files and their SHA-256 values; never overwrite or destructively process them.
- Treat the SHA-256 in SAMPLE_MAP as the stable file identity.
- Before generating a runtime manifest, reconcile every inventory row to exactly one SAMPLE_MAP row using full folder hierarchy plus filename and, where necessary, size/hash. If the inventory's flattened folder field prevents a unique match, mark the row unresolved rather than guessing.
- Do not normalize or rewrite the original filenames. Store normalized note names, MIDI note numbers, and portable paths in separate derived fields.
- Any derived render, trim, loop, or processed sample must be stored separately and linked back to its original SHA-256.

## Classification policy
- Folder and filename labels (ALL MARTIN, ALL TAYLOR, ENGL, MESA, EVH, MARSHALL GIBSON, Квинты, Ноты, Кода, Слайды, FX, 75 bpm) are source hints only.
- Do not infer actual chord voicing, note, tuning, BPM, musical phrase length, articulation, or sound character from names alone.
- Do not silently transpose, duplicate, relabel, or fabricate missing coverage.
- EVH arpeggios and FX/transition files remain phrase/FX candidates until audio review; do not force them into single-note mapping slots.

## Runtime-manifest schema proposal
Recommended fields (one record per WAV):
`sample_id, source_family, source_subfolder, original_filename, relative_path, source_bytes, sha256, sample_rate, channels, bit_depth, duration_seconds, declared_label, measured_pitch, midi_root, octave, tuning_cents, content_type, articulation, tempo_bpm, bars, start_offset_seconds, usable_start_seconds, usable_end_seconds, playback_mode, velocity_layer, round_robin_group, midi_key_low, midi_key_high, key_switch, preset_tags, analysis_confidence, review_status, exclusion_reason`.

Use null/empty values for unknown fields; never use guessed values as if measured.

## Gate preservation
No plugin, preset, engine, sound-quality, or final-build testing may begin until all required audio libraries have been collected and integrated and all 500 core factory presets have been created and integrated. This passport does not count as library integration and does not authorize testing.
