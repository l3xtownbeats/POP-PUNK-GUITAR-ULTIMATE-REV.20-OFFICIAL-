<div align="center">

# POP PUNK GUITAR ULTIMATE — REV.20 OFFICIAL

**L3XTOWN AUDIO LAB · Windows 10 x64 · VST3 · JUCE · C++20**

**NEON STAGE DEFAULT · MELODY · PATTERN**

<img src="01%20INTERFACE%20%20NEON%20STAGE%20DEFAULT%20.png" alt="POP PUNK GUITAR ULTIMATE — NEON STAGE DEFAULT main plugin interface" width="100%">

<sub>APPROVED MAIN INTERFACE · NEON STAGE DEFAULT · SKIN-1</sub>

</div>

REV.20 is the single canonical home for continuing development. Approved decisions, preserved implementation, engineering work, tests, assets, sample inventories and validation evidence are maintained here.

## Product

A sample-based pop-punk guitar VST3 instrument for Windows 10 x64, with FL Studio 20 x64 as the required host acceptance target. The product has exactly two main playing modes: **MELODY** and **PATTERN**. **AUTOCHORDS** is an auxiliary window within PATTERN, never a third main mode.

Both modes follow the approved one-key/one-note-event rule: each ordinary MIDI key triggers one mapped note/event clip, not a complete parent loop or phrase.

## Visual identity

The complete approved set is exactly 16 premium graphical shells: **SKIN-1 / NEON STAGE DEFAULT** plus SKIN-2…SKIN-16. All 16 are runtime-ready in the REV.20 gallery. Exact target SHA `974c5877d1a0375100539d2513329a38feb84871` passed Windows x64 VST3 build, full CTest (15/15), the all-16 theme validator and the 16-only package stage. The main Playing Core hero-PNG display and full pixel/layout parity against mockup 01 are still open UI tasks; the package containing hero assets is not by itself proof of the hero being rendered in the main console. No legacy skin batches or additional themes are part of the product.

## Repository map

- `Info.txt` — single canonical journal of decisions, transfers, tests and remaining gates.
- `docs/REV20_ACCEPTED_BASELINE_RU.md` — locked product baseline and all 16 skin names.
- `docs/REV20_DECISION_TIMELINE_RU.md` — chronological decision/source history.
- `docs/REV20_ENGINEERING_WORKSTREAM_REGISTER_RU.md` — M1–M13 source PR audit and selective integration order.
- `docs/REV20_FUNCTIONAL_GAP_AUDIT_RU.md` — actual code-level UI, preset, Engine and Import Sounds gaps.
- `docs/REV20_FL20_ACCEPTANCE_CHECKLIST_RU.md` — manual Windows 10 / FL Studio 20 host acceptance.
- `docs/REV20_LIBRARY_TIERS_RU.md` and `assets/library/library_tiers.json` — BASIC/EXPANDED specification.
- `docs/REV20_LIBRARY_MANAGER_APPROVED_REQUIREMENTS.md` — complete approved Library Manager workflow and acceptance requirements.
- `docs/REV20_SKIN_APPROVAL_STANDARD_RU.md` — premium visual-quality rules for all 16 shells.
- `docs/REV20_MIGRATION_MANIFEST.md` — selected transfers and excluded legacy material.
- `docs/DEVELOPMENT_STATUS.md` — evidence-based implementation/readiness matrix.
- `Source/`, `tests/`, `tools/` — plugin source, tests and validators.
- `SKIN/` — exactly 16 logical themes and runtime art resources.
- `presets/` — current partial 300-definition catalog, not the final 500 playable bank.
- `LibraryManager/` and L3XTOWN inventories — pre-existing non-destructive library intake work.

## Sound library and presets

The core target is **500 playable factory presets: 250 MELODY + 250 PATTERN**. All must be usable from the included BASIC LIBRARY, minimum 15 GB. The optional EXPANDED tier adds an initial 15 GB (30 GB combined initially) and may grow without a product-imposed ceiling. The 250 PATTERN presets must be organized across PATTERN windows, sections and functions, not dumped into one flat list. The current 300-entry catalog is partial 150+150 definitions, not 500 finished/playable presets. The 15 GB audio payload, full legal clearance and all 500 playable presets are not yet delivered.

## Latest Windows validation

Workflow [44719521911](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/44719521911) passed on exact SHA `974c5877d1a0375100539d2513329a38feb84871`: Windows x64 configure/build, VST3, CTest 15/15, 16-skin validator, 16-only package stage and upload. Artifact ID `14620284899`, SHA-256 `59b87d1caaa6aaf3b72b89edce6fd2311c23d673960b0c5459658e1a1aab0f30`.

A subsequent DSP patch for live AMP TONE, EQ crossover frequencies and compressor amount is being added with its own regression test; its target exact-SHA run must pass separately. Pluginval strictness 5, manual FL Studio 20 host acceptance, DPI/performance, full preset service and licensed audio delivery remain open. No release package is declared approved.

**All future project work belongs only in this repository, on `main`.**
