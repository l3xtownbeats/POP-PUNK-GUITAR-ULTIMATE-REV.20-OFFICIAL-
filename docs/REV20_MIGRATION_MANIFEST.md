# REV.20 — consolidation manifest

## Source selection

- Primary engineering source: `POP-PUNK-GUITAR-ULTIMATE-VST-REV.19-Build.03`, HEAD `7b540ff9cddbc2b0327c83611b49e222bce51d2b`.
- REV.18-only decision commits reconciled into the baseline: `738edc6151a6e75d25ef361fc60c9178fbde4360`, `c20cc6b76d4c66b70bcfcec27d8e79514ada147b`, `bf6465c6d1613a2b04728f9f91ee32c4b6f12983` and `6ac4276c26d84ffb7e60d95cea3909401db00cea`.
- Destination main before migration: `2aeffd1c594232a933e9e5577ffad4efb6877263`.
- REV.20 migration commit: `2bd623a666090d4ef017296f52fdb568808a227b`.

## Additional approved skin-artwork transfer (2026-11-20)\n\n- NEON STAGE / SKIN-1 remains sourced from merged PR #43 (2026-11-15).\n- The named 16-shell sequence and premium artwork for SKIN-2…SKIN-16 were reconciled from draft PR #58, source branch `work/approved-16-skins-completion`, exact SHA `10e590c8a3fdfed90cc7ae05e0ff74d8875ac88a`.\n- Selectively added the 30 missing raster files: `preview.png` (360×240) and `hero.png` (800×450) for each of Skin_103…Skin_117. Existing stable IDs, ordinals, names and manifests remain in place and are normalized to the same 16-name table.\n- Source artwork/strict audit run [43835887953](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-/actions/runs/43835887953) and source Windows x64 build/full CTest/16-only packaging run [43835886032](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-/actions/runs/43835886032) both passed on that source SHA. This evidence is preserved as provenance only; REV.20 exact-SHA runtime/host checks remain pending.\n\n## Preserved in REV.20

- Production VST3 source under `Source/`, CMake project, focused regression tests, SFZ/sample validators, factory catalog and portable preset examples.
- Only the approved 16 skin shells: `Skin_053` and `Skin_103` through `Skin_117`.
- NEON STAGE component assets/manifests and the seven approved interface reference captures.
- Approved MIDI/Melody, sample streaming, bank/preset, auxiliary panel, reference asset and licensing specifications.
- Meta Open Sound license-clearance record and sound asset registry seed.
- All pre-existing REV.20 L3XTOWN inventories, hash manifests, acoustic/electric reports, LibraryManager source and tests remain intact.

## Intentionally excluded from active product

- Legacy/experimental skin directories outside the 16 approved shells, including the old 102-theme registry and generated 50-theme batches.
- Duplicate/repeated prompts, continuation dumps, parallel journals, temporary screenshots and stale copies of specifications.
- Old root-level prototype duplicates where a maintained `Source/` implementation exists.
- The historical `Info.txt` copied as-is: it contained competing REV.17/18/19 branch instructions. A clean REV.20 `Info.txt` is the only active journal.
- Sample audio files not actually present/cleared for redistribution. Existing L3XTOWN originals remain on source storage; metadata manifests are not treated as audio copies.

## Known evidence limitations

- The latest inspected REV.19 workflow run (#2241, SHA `2df2a566b489198bd3ec646bdf6c78deef8c8f06`) failed. That run is not evidence for the selected source HEAD or REV.20.
- A historical REV.18 interim CI package passed at SHA `877a0c8d96dc6ef3bdd620f8af0a75a79fa067ec`; FL Studio 20 manual host acceptance was explicitly not run.
- The REV.20 migration workflow passed, but that workflow copied files and pushed a commit; it did not compile the plugin or execute the VST3 regression suite.
- Therefore imported code is PRESENT; a successful REV.20 build, full CTest, pluginval, package audit and FL Studio 20 host acceptance remain unverified.

## Migration policy

This is a selective consolidation, not a merge of old branches. Old repositories and branches remain available as historical provenance, but all new implementation, changes, validation evidence and releases belong only to this repository's `main` branch.


## 2026-11-20 approved product decisions reconciled

- Exactly 16 graphical shells total: NEON STAGE DEFAULT (SKIN-1) + the 15 named additional shells (SKIN-2…SKIN-16). No 17th theme, legacy batch or extra gallery is permitted.
- Exactly two top-level product modes: MELODY and PATTERN. AUTOCHORDS and other tools remain auxiliary windows/functions within these modes.
- Core bank target: 500 playable presets, 250 MELODY + 250 PATTERN. The PATTERN 250 are distributed across PATTERN's own windows, sections and functions, not one flat list.
- BASIC LIBRARY is 15 GB and included. Initial EXPANDED add-on is +15 GB (30 GB combined at initial tier), optional for core presets and extensible without a product cap.
