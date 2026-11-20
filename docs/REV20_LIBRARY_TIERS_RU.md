# REV.20 — BASIC / EXPANDED LIBRARY CONTRACT

**Status:** approved product/distribution contract; audio payload and 500 playable factory presets are not yet delivered.

## 1. BASIC LIBRARY — standard package

- Minimum target: **15 GB decimal** (15,000,000,000 bytes).
- Included in the standard product package; mandatory and independently playable.
- Must provide everything needed to play all **500 core factory presets** (250 MELODY + 250 PATTERN).
- 15 GB is a minimum, not a hard ceiling. Final size is driven by sound quality, full note/root-key coverage, velocity layers, round-robin, articulations and licensed unique audio.
- Quality may not be degraded just to meet a nominal package-size target.

## 2. EXPANDED LIBRARY — optional add-on

- Initial add-on target: **+15 GB**.
- Initial combined total: **30 GB (15 + 15)**.
- Additive only: does not replace BASIC and must not be required by any of the 500 core presets.
- May grow beyond the initial 30 GB without a hard cap; the catalog and content may expand.

## 3. Library intake and engine safety

- Automatic discovery, analysis and distribution; classification may use confidence and human-review gates.
- No mandatory manual per-WAV assignment.
- Hashing and indexing execute on background workers.
- Audio callback must not perform disk I/O, blocking operations or unbounded allocation.
- Preserve source provenance, licenses, redistribution clearance and SHA-256.
- Detect exact duplicates by SHA-256; acoustic similarity is a review hint, not automatic deletion authority.
- Never use duplicate/padded content to meet the size target.

## 4. Quality-first sample replacement

Any replacement of an existing sample requires comparison evidence and a dependency audit. It must preserve or improve note coverage, velocity response, round-robin variation, articulations, technical quality, preset tone/mix-readiness and license rights. Update mapping references, checksums and license records atomically. Never delete user-imported source files.

## 5. Factory preset bank structure

- Exactly two top-level plugin modes: MELODY and PATTERN.
- 500 core factory presets: 250 MELODY + 250 PATTERN.
- PATTERN's 250 presets must be distributed across PATTERN windows, sections and functions. Do not present them as a single flat 250-row screen.
- EXPANDED may add tone variations, performances, articulations and additional presets; the 500 core set remains fully usable from BASIC.

## 6. Delivery status and release gates

The current REV.20 source contains the tier contract and regression tests only. It does **not** currently prove the 15 GB BASIC or +15 GB EXPANDED payload is present, that all sample licenses are cleared, or that 500 factory presets are playable.

Release acceptance requires measured package sizes, all 500 preset mappings resolving against BASIC, no reliance on EXPANDED for core playback, verified redistribution rights, SHA-256/provenance, listening/quality review, exact-SHA Windows build/tests, pluginval, package integrity and FL Studio 20 host acceptance.
