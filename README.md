<div align="center">

# POP PUNK GUITAR ULTIMATE — REV.20 OFFICIAL

**L3XTOWN AUDIO LAB · Windows 10 x64 · VST3 · JUCE · C++20**

**NEON STAGE DEFAULT · MELODY · PATTERN**

<img src="01%20INTERFACE%20%20NEON%20STAGE%20DEFAULT%20.png" alt="POP PUNK GUITAR ULTIMATE — NEON STAGE DEFAULT main plugin interface" width="100%">

<sub>APPROVED MAIN INTERFACE · NEON STAGE DEFAULT · SKIN-1</sub>

</div>

REV.20 is the single canonical home for all continuing development. Approved decisions, preserved implementation, engineering work, tests, assets, sample inventories and future validation evidence are maintained here.

## Product

A sample-based pop-punk guitar VST3 instrument for Windows 10 x64, with FL Studio 20 x64 as the required host acceptance target. The product has exactly two main playing modes: **MELODY** and **PATTERN**. **AUTOCHORDS** is an auxiliary window within PATTERN, never a third main mode.

Both modes follow the approved one-key/one-note-event rule: each ordinary MIDI key triggers one mapped note/event clip, not a complete parent loop or phrase.

## Visual identity

The canonical visual shell and default theme is **SKIN-1 / NEON STAGE DEFAULT / `skin-053`**. The complete approved set is exactly 16 named premium graphical shells: SKIN-1 through SKIN-16. All 15 additional shells have individual manifests, vector material layers and preview/hero artwork. Their artwork asset pack has passed strict source-branch validation; enabling them in the REV.20 runtime remains gated on REV.20 exact-SHA build and host acceptance. No legacy skin batches or additional themes are part of the product.

## Repository map

- `Info.txt` — single canonical project journal and locked decisions.
- `docs/REV20_ACCEPTED_BASELINE_RU.md` — consolidated approved product baseline.
- `docs/REV20_MIGRATION_MANIFEST.md` — migration scope, retained work and exclusions.
- `docs/DEVELOPMENT_STATUS.md` — evidence-based implementation and readiness status.
- `Source/` — VST3 processor, editor, sampler, pattern and auxiliary UI source.
- `tests/` — C++ and Python regression tests.
- `SKIN/` — exactly the approved 16 logical theme shells and runtime registry.
- `presets/` — current partial 300-definition catalog and portable examples.
- `LibraryManager/` and L3XTOWN inventory files — pre-existing non-destructive source-library intake work, retained without overwrite.

## Sound library and presets

The core target is 500 playable factory presets: 250 MELODY and 250 PATTERN, all usable from the included 15 GB BASIC LIBRARY. The initial EXPANDED add-on contributes another 15 GB (30 GB combined at the initial tier) and may grow without a product-imposed ceiling. The 250 PATTERN presets must be organized by the PATTERN workspace's sections/windows/functions, not dumped into one flat 250-item screen. The imported 300-entry catalog is a partial 150+150 definition set, not 500 finished/playable presets. All shipped sample content must have explicit redistribution/embedding rights, provenance and SHA-256 evidence.

## Build and acceptance

The source uses CMake, JUCE 7.0.12 and C++20. The REV.20 Windows validation workflow is manual and gated on the BASIC LIBRARY and 500 core factory preset milestones. A successful build, full tests, pluginval, package integrity and FL Studio 20 acceptance must be recorded against the exact REV.20 commit. No release package is declared approved here.

**All future project work belongs only in this repository, on `main`.**
