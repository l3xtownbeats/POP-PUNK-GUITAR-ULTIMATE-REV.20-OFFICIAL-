<div align="center">

# POP PUNK GUITAR ULTIMATE
## REV.20 OFFICIAL

**L3XTOWN AUDIO LAB**  
**Sample-based Pop-Punk Guitar Instrument · Windows x64 · VST3**

**NEON STAGE DEFAULT · MELODY · PATTERN**

<img src="Неоновый%20интерфейс%20PPGU%20%E2%80%94%20поп-панк%20гитара.png" alt="PPGU NEON STAGE visual reference" width="100%">

<sub>REV.20 · 16 APPROVED SKINS · ONE CANONICAL PROJECT</sub>

[![Windows VST3 validation](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/workflows/rev20-windows-vst3-skin-validation.yml/badge.svg?branch=main)](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/workflows/rev20-windows-vst3-skin-validation.yml)
[![NEON STAGE native CI](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/workflows/neon-stage-native-ci.yml/badge.svg?branch=main)](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/workflows/neon-stage-native-ci.yml)

### [DOWNLOAD VERIFIED VST3 BUILD](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/45941370562/artifacts/15173197005)
### [DOWNLOAD UI SNAPSHOTS](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/45941370562/artifacts/15172667912)
### [DOWNLOADS & INSTALLATION GUIDE](docs/REV20_PUBLIC_RELEASE_AND_DOWNLOADS_RU.md)

</div>

---

## About

**POP PUNK GUITAR ULTIMATE (PPGU) REV.20** is a Windows VST3 virtual guitar instrument under development by **L3XTOWN AUDIO LAB**. Its design direction combines a dedicated pop-punk guitar performance engine with the NEON STAGE interface system, a sample-based sound architecture, MIDI performance workflows and a curated 16-skin visual collection.

This repository is the single canonical REV.20 engineering workspace. It contains the plugin source, CMake build, regression tests, UI assets, skin manifests, sound-library intake tools, product specifications and the development journal.

> **Project status:** active engineering build. A verified Windows x64 VST3 CI artifact is available temporarily. A permanent public release/installer has not yet been published. FL Studio 20 host acceptance and final sound-library delivery remain separate release gates.

## Product identity

| Property | Current definition |
|---|---|
| Product | POP PUNK GUITAR ULTIMATE |
| Revision | REV.20 OFFICIAL |
| Developer / label | L3XTOWN AUDIO LAB |
| Product type | Sample-based virtual guitar instrument |
| Plugin format | VST3 x64 |
| Target OS | Windows 10 x64 |
| Required host acceptance | FL Studio 20 x64 |
| Main playing modes | MELODY and PATTERN only |
| Auxiliary performance tool | AUTOCHORDS inside PATTERN |
| Visual system | NEON STAGE DEFAULT / SKIN-1 |
| Approved visual shells | Exactly 16: SKIN-1…SKIN-16 |
| Current main toolchain | JUCE 7.0.12 + C++20 |
| Modernization proposal | JUCE 9.0.6 + C++23; C++26 experimental — [PR #31](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/pull/31) |
| Build system | CMake |
| Canonical branch | `main` |

The JUCE 9 / C++23 migration is under separate review. It is not labelled as the production main baseline until the migration is accepted and its own exact-SHA validation succeeds.

## Verified build & downloads

The latest successful Windows validation linked below was run against commit `781205287eac13d7a2392a85721463040a7ea217`. Current `main` is commit `438d59ba07e9b92e9579e9893eac7887dfbe5d5e`, a direct child that adds visual reference files.

**Successful workflow steps on the validated commit:**
- Windows x64 CMake configure and Release build;
- complete registered CTest suite;
- NEON STAGE UI snapshot generation;
- exactly 16 skin manifests/artwork validation;
- VST3 + matching 16-skin package staging;
- pluginval strictness level 5;
- upload of the VST3 package and UI snapshots.

**Download now (temporary GitHub Actions artifacts):**
- [PPGU Windows x64 VST3 + 16-skin pack](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/45941370562/artifacts/15173197005)
- [NEON STAGE rendered UI snapshots](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/45941370562/artifacts/15172667912)
- [Full workflow log and test steps](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/45941370562)

These CI artifacts expire **2026-12-11 UTC**. They are temporary test outputs, not a permanent release or installer. There are currently no published GitHub Releases and the repository's Downloads feature is disabled. See the [full download, installation and release policy](docs/REV20_PUBLIC_RELEASE_AND_DOWNLOADS_RU.md).

### Source downloads

- [Download source ZIP](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/archive/refs/heads/main.zip)
- [Download source TAR.GZ](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/archive/refs/heads/main.tar.gz)
- [Browse source on GitHub](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/tree/main)

Source archives are not compiled plugin installers.

### Visual asset downloads

The following are design/reference assets, not the VST3:
- [NEON STAGE panel frames 1× / 2×](PPGU-NEON-STAGE-PANEL-FRAMES-1X-2X.zip)
- [PPGU interface reference collection](Неоновый%20интерфейс%20PPGU.zip)
- [UI asset atlas](Неоновый%20атлас%20UI%E2%80%91ассетов%20PPGU.png)
- [NEON STAGE asset pack documentation](ASSETS/PPGU_REV20_NEON_STAGE_ASSETS/README_ASSET_PACK_RU.md)

## Playing modes

### MELODY
MIDI-driven single-note guitar performance. A normal MIDI key is mapped to its corresponding note/event; it does not launch an entire parent loop or phrase.

### PATTERN
A note/event-clip performance workflow. A normal MIDI key triggers its mapped clip, not a complete loop. Pattern sections, windows and routing are part of the approved product architecture.

### AUTOCHORDS
An auxiliary harmony/chord tool available from PATTERN. It is not a third main playing mode.

## NEON STAGE visual system

The canonical theme is **NEON STAGE DEFAULT / SKIN-1 / `skin-053`**. The approved collection contains exactly 16 logical skins:

1. NEON STAGE DEFAULT
2. OBSIDIAN GOLD
3. CARBON FORGE
4. MIDNIGHT CRIMSON
5. ARCTIC PLATINUM
6. VIOLET NOIR
7. TITANIUM STORM
8. EMERALD CIRCUIT
9. SOLAR FLARE
10. STILLWATER
11. ROSE CHROME
12. DESERT AMBER
13. GLACIER TEAL
14. PHANTOM GRAPHITE
15. ULTRAVIOLET DRIVE
16. VOLCANIC STEEL

All themes are visual shells. They must not alter APVTS identifiers, MIDI behavior, presets, sampler, DSP or audio-thread behavior. See the [skin approval standard](docs/REV20_SKIN_APPROVAL_STANDARD_RU.md) and [NEON STAGE GUI implementation baseline](docs/NEON_STAGE_GUI_IMPLEMENTATION_BASELINE_RU.md).

## Sound library & factory bank

The approved content target is:
- **500 playable factory presets:** 250 MELODY + 250 PATTERN.
- **BASIC LIBRARY:** at least 15 GB, included in the standard product; every core preset must work with BASIC alone.
- **EXPANDED LIBRARY:** optional initial +15 GB tier (30 GB combined initially), expandable without a product-imposed ceiling.
- Every redistributed audio asset requires provenance, SHA-256 and explicit redistribution rights.

**Honest current status:** the repository contains a partial 300-definition catalog (150 MELODY + 150 PATTERN). This is not the final 500 playable preset bank. The full 15 GB licensed BASIC audio payload and complete playable preset set have not yet been delivered. Do not treat inventory CSVs, filenames or metadata as proof of playable mappings or redistribution rights.

## Build from source

The current `main` baseline uses JUCE 7.0.12 and C++20. The Windows CI build uses Visual Studio 2022 / Windows Server 2022 x64 and CMake.

PowerShell example:

```powershell
git clone --branch main https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-.git
cd POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-

git clone --depth 1 --branch 7.0.12 https://github.com/juce-framework/JUCE.git JUCE

cmake -S . -B build -A x64
cmake --build build --config Release --parallel
ctest --test-dir build -C Release --output-on-failure
```

See the [Windows VST3 validation workflow](.github/workflows/rev20-windows-vst3-skin-validation.yml) for the authoritative CI procedure.

## Project map & documentation

| Resource | Purpose |
|---|---|
| [Info.txt](Info.txt) | Single canonical development journal |
| [Accepted product baseline](docs/REV20_ACCEPTED_BASELINE_RU.md) | Locked product requirements and 16-skin sequence |
| [Decision timeline](docs/REV20_DECISION_TIMELINE_RU.md) | Decision history and source authority |
| [Development status](docs/DEVELOPMENT_STATUS.md) | Evidence-based implementation/readiness matrix |
| [Functional gap audit](docs/REV20_FUNCTIONAL_GAP_AUDIT_RU.md) | Implemented code paths vs remaining UI/engine gaps |
| [Engineering workstream register](docs/REV20_ENGINEERING_WORKSTREAM_REGISTER_RU.md) | Source PR audit and integration sequence |
| [NEON STAGE GUI baseline](docs/NEON_STAGE_GUI_IMPLEMENTATION_BASELINE_RU.md) | Main UI composition and behavior contract |
| [Skin approval standard](docs/REV20_SKIN_APPROVAL_STANDARD_RU.md) | Quality and identity rules for 16 skins |
| [Sound Hunter baseline](docs/REV20_SOUND_HUNTER_REAL_GUITAR_BASELINE_RU.md) | Recorded guitar acquisition, rights and verification |
| [Library tier contract](docs/REV20_LIBRARY_TIERS_RU.md) | BASIC / EXPANDED library definition |
| [Library Manager requirements](docs/REV20_LIBRARY_MANAGER_APPROVED_REQUIREMENTS.md) | Approved library scan, validation and distribution workflow |
| [FL Studio 20 acceptance checklist](docs/REV20_FL20_ACCEPTANCE_CHECKLIST_RU.md) | Manual DAW/host verification |
| [Public downloads & release policy](docs/REV20_PUBLIC_RELEASE_AND_DOWNLOADS_RU.md) | Artifacts, install notes, release status and expiry |
| [Windows VST3 CI](.github/workflows/rev20-windows-vst3-skin-validation.yml) | Exact-SHA Windows build and plugin validation |
| [CMake build definition](CMakeLists.txt) | Project targets and dependencies |
| [Factory preset definitions](presets/) | Current partial catalog |
| [Skin registry and assets](SKIN/) | Exactly 16 logical themes |
| [Sampler and processor source](Source/) | VST3 implementation |
| [Regression tests](tests/) | C++ and Python contract tests |

## Quality, compatibility and release gates

A successful build and pluginval run are important engineering evidence, not a substitute for host acceptance or content completeness.

Remaining release gates include:
- manual FL Studio 20 x64 acceptance on Windows 10 x64;
- clean-install and VST3/skin package verification on a separate Windows environment;
- DPI and UI scale checks at 100%, 125% and 150%;
- performance, memory, long-session, MIDI and audio regression checks;
- completion and listening review of the 500 playable factory presets;
- delivery and license review of the included BASIC sound library;
- explicit source-code and third-party asset licensing.

## License & third-party rights

No root `LICENSE` file is currently published. Do not assume this repository is open-source licensed or that third-party sample files may be redistributed. Each bundled audio asset must have explicit rights for redistribution/embedding in a commercial virtual instrument. A permanent public release requires a clear source-code license decision and per-asset rights audit.

## Contributing / development rules

- `main` is the canonical product line.
- Use focused branches and pull requests; do not force-push or bypass protected-branch review.
- Preserve the approved 16-skin count and immutable IDs.
- Do not invent completion claims, preset counts, library size, licensing or host compatibility.
- Keep disk I/O, scanning, hashing, decoding and blocking work off the audio callback.
- Record meaningful engineering decisions and exact-SHA validation results in [Info.txt](Info.txt).

---

<div align="center">

**L3XTOWN AUDIO LAB · POP PUNK GUITAR ULTIMATE · REV.20**

[Repository](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-) · [Actions](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions) · [Releases](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/releases)

</div>
