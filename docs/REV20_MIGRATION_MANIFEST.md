# REV.20 — consolidation manifest

## Source selection

- Primary engineering source: `POP-PUNK-GUITAR-ULTIMATE-VST-REV.19-Build.03`, HEAD `7b540ff9cddbc2b0327c83611b49e222bce51d2b`.
- REV.18-only decision commits reconciled into the baseline: `738edc6151a6e75d25ef361fc60c9178fbde4360`, `c20cc6b76d4c66b70bcfcec27d8e79514ada147b`, `bf6465c6d1613a2b04728f9f91ee32c4b6f12983` and `6ac4276c26d84ffb7e60d95cea3909401db00cea`.
- Destination main before migration: `2aeffd1c594232a933e9e5577ffad4efb6877263`.
- REV.20 migration commit: `2bd623a666090d4ef017296f52fdb568808a227b`.

## Additional approved skin-artwork transfer (2026-11-20)

- NEON STAGE / SKIN-1 remains sourced from merged PR #43 (2026-11-15).
- The named 16-shell sequence and premium artwork for SKIN-2…SKIN-16 were reconciled from draft PR #58, source branch `work/approved-16-skins-completion`, exact SHA `10e590c8a3fdfed90cc7ae05e0ff74d8875ac88a`.
- Selectively added the 30 missing raster files: `preview.png` (360×240) and `hero.png` (800×450) for each of Skin_103…Skin_117. Existing stable IDs, ordinals, names and manifests remain in place and are normalized to the same 16-name table.
- Source artwork/strict audit run [43835887953](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-/actions/runs/43835887953) and source Windows x64 build/full CTest/16-only packaging run [43835886032](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-/actions/runs/43835886032) both passed on that source SHA. This evidence is preserved as provenance only; REV.20 exact-SHA runtime/host checks remain pending.

## Preserved in REV.20

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
- A dedicated `.github/workflows/rev20-windows-vst3-skin-validation.yml` has now been added for exact-main-SHA Windows x64 configure/build, full CTest, 16-skin PNG/SVG/registry validation and VST3 artifact upload. The latest run must be checked before claiming it passed.
- `pluginval` strictness 5, final package distribution, DPI and FL Studio 20 host acceptance remain separate release gates.

## Migration policy

This is a selective consolidation, not a merge of old branches. Old repositories and branches remain available as historical provenance, but all new implementation, changes, validation evidence and releases belong only to this repository's `main` branch.


## 2026-11-20 approved product decisions reconciled

- Exactly 16 graphical shells total: NEON STAGE DEFAULT (SKIN-1) + the 15 named additional shells (SKIN-2…SKIN-16). No 17th theme, legacy batch or extra gallery is permitted.
- Exactly two top-level product modes: MELODY and PATTERN. AUTOCHORDS and other tools remain auxiliary windows/functions within these modes.
- Core bank target: 500 playable presets, 250 MELODY + 250 PATTERN. The PATTERN 250 are distributed across PATTERN's own windows, sections and functions, not one flat list.
- BASIC LIBRARY is 15 GB and included. Initial EXPANDED add-on is +15 GB (30 GB combined at initial tier), optional for core presets and extensible without a product cap.


## Selective runtime artwork integration (2026-11-20)

From source PR #58, the following artwork-only code was integrated into current REV.20 files without wholesale branch merge:

- `Source/UI/ThemeManager.cpp/.h`: safe local SVG loading for texture/bezel/crest and bounded image rendering, with path/content validation. REV.20 retains the exact default name NEON STAGE DEFAULT.
- `Source/PluginEditor.cpp`: artwork drawing in the main editor and auxiliary surfaces; 16-skin-only gallery filtering; stable-ID/logical-ordinal labels; prior Preview/Apply/Cancel interaction retained.
- `Source/UI/PPGUMultiWindowWorkspace.cpp`: subtle theme texture layer for workspace background/floating windows.
- `tests/ThemeManagerTests.cpp`: exact-SHA regression test now decodes all 3 SVG assets for every one of the 16 theme manifests.
- `tools/package_active_skins.py`: stages exactly the 16 active themes and five required assets each; adapted to REV.20 registry `defaultStableId` key. Windows workflow uploads the .vst3 bundle plus matching `Skins/` pack.

These code changes were validated on REV.20 exact SHA `8cfd11ecce3c8039360c1c194be5251e716c9015`: Windows x64 VST3 build, full CTest, all 16 ThemeManager SVG decodes, PNG/registry validation and 16-only package staging passed (run `44717722638`). All 16 registry entries are now `runtimeReady=true`; FL Studio 20 host acceptance and pluginval remain pending. No APVTS/DSP/MIDI/sampler/audio callback changes were intended.


## PageCache publish rollback correction from source PR #2 (2026-11-20)

- Selectively integrated only the corrected PageCacheSlots::publish() state handling and regression coverage.
- After the worker's slot and PageKey are confirmed, invalid channels/frames cause a CAS rollback loading→empty for that reservation. Mismatched/stale PageKeys return false without touching the active reservation.
- Current REV.20 build/CTest for this correctness patch is still pending; do not inherit source PR results as target evidence.


## PageCache rollback exact-SHA evidence — 2026-11-20

- Workflow [44719521911](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/44719521911), SHA `974c5877d1a0375100539d2513329a38feb84871`: SUCCESS.
- The new invalid-page-geometry and stale-worker-PageKey rollback regression cases passed as part of full CTest (15/15). Windows VST3 build, 16-skin validation, exact 16-only package staging and artifact upload also passed.
- Artifact 14620284899 / SHA-256 `59b87d1caaa6aaf3b72b89edce6fd2311c23d673960b0c5459658e1a1aab0f30`.


## Live AMP TONE / EQ / compressor DSP correction — 2026-11-20

- Source-main DSP behavior is now selectively ported into REV.20 `Source/PluginProcessor.cpp`.
- Existing `eqLowFreq` / `eqHighFreq` APVTS values now drive EQ cutoffs; `tone` applies independent high-band tilt; EQ bypass leaves this tone stage active; `compressorAmount` controls dry/processed blend and is loaded once per block, outside the per-sample loop.
- New Python wiring test is registered with CTest; exact target build/test is pending after this code commit. No APVTS IDs were added or renamed.


## Sound Hunter real-guitar acquisition subsystem imported (2026-11-20)

- Selectively imported the 11-entry CC0-1.0 catalog and the acquisition/splitter/audit tools from source main.
- Improved the importer to pin each repository snapshot to an immutable commit SHA, record archive SHA-256/bytes, validate both POSIX and Windows archive paths, fail closed when an existing audio file cannot be hashed, atomically write registry metadata and remove only the current failed run folder on error.
- Added Python regression tests for path safety and hash fail-closed behaviour, plus soundbank policy and split-artifact tests; registered all three with CTest.
- Added a separate Ubuntu workflow that fetches verified sources, splits/checksums the payload and uploads the registry and sample artifact. Actual acquisition, measured unique audio size, and human quality/mapping verification remain pending.

## Pluginval strictness 5 added to target Windows workflow

The Windows VST3 workflow now locates the built bundle and invokes the official pluginval Windows 1.0.4 archive at strictness level 5. First exact-SHA result pending; FL Studio 20 host acceptance remains manual.


## Sound Hunter selective transfer (2026-11-20)
Transferred from source main: SoundHunter importer/catalog/production notes, importer/policy/splitter tests, soundbank audit, bounded artifact splitter and a REV.20-named 300-entry sample-binding planning baseline. The source pipeline verifies actual license text, release SHA256SUMS, LFS payload SHA-256, safe paths and duplicates. The target workflow is manual-only with explicit acquire_samples. No Sound Hunter payload is declared acquired or playable until a real target artifact and listening/runtime QA exist.


## Sound Hunter acquisition defect correction (2026-11-20)

- Target run 44722586113 exposed an importer assumption: GitHub zipballs can contain multiple LICENSE files. The importer previously required exactly one and stopped before admitting any audio.
- Selectively corrected the importer to select the root-most expected LICENSE by path depth. Added a regression test and changed the canonical target workflow to workflow_dispatch with explicit acquire_samples.
- The failed run remains historical evidence of the defect; it is not evidence of sample acquisition.


## Current target evidence — 2026-11-20

- Exact SHA `10b05a0117366cf33afeb194b3c28456f30fef80` passed Windows x64 build, 19/19 CTest, exact 16-skin validator, 16-only package stage and pluginval Strictness 5 (run 44729083554).
- Latest artifact ID 14625308194, size 5,857,765 bytes, digest 72e31eb39e36301c2f3dfa070e9ef277c6d5a360d2907db12f4e4a25e219e864.
- This automated baseline is not a substitute for FL Studio 20 host acceptance.
