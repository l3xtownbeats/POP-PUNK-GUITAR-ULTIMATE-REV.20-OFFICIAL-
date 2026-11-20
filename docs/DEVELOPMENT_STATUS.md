# POP PUNK GUITAR ULTIMATE — REV.20 Development Status

Last updated: 2026-11-20  
Canonical repository: `l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-`  
Canonical branch: `main`  
Canonical journal: `/Info.txt`

## Consolidated repository baseline

The REV.20 main branch contains the selected production VST3 source, CMake build definition, focused regression tests, the exactly 16 named graphical-shell registry, NEON STAGE assets, the 30 premium preview/hero PNG files for SKIN-2…SKIN-16, sample/preset validation utilities and the required product/license specifications. The repository's pre-existing LibraryManager and L3XTOWN sample-inventory work are retained.

Migration commit: `2bd623a666090d4ef017296f52fdb568808a227b`  
Source engineering snapshot: REV.19 Build.03, `7b540ff9cddbc2b0327c83611b49e222bce51d2b`  
GitHub Actions migration run: [44702430411](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/44702430411) — SUCCESS. The run reports 457 copied source/resource files and a successful push to `main`.

## Verified existing REV.20 library work

The pre-migration target repository already contained:
- 393 L3XTOWN source path records and 387 unique SHA-256 audio contents.
- Six exact duplicate-content pairs retained as aliases.
- Source inventory, runtime manifest, sample map, factory integration plan and hash manifests.
- Acoustic/electric filename and signal audits, plus a non-destructive LibraryManager with its own tests.

These are verified repository metadata artifacts only. They do not mean that local source WAV files were copied into FACTORY or approved for playable mapping. Original WAVs remain untouched.

## Current VST3 import status

| Area | REV.20 status at consolidation |
|---|---|
| CMake/JUCE VST3 source | PRESENT |
| PluginProcessor / PluginEditor | PRESENT; skin lookup now separates logical ordinal from immutable stable ID |
| Shared sampler / SFZ / WAV / streaming / cache source | PRESENT |
| Pattern scheduler / chord transition source | PRESENT |
| UI auxiliary workspace / theme manager source | PRESENT |
| Regression tests | PRESENT; not yet run on the REV.20 migration SHA |
| Factory catalog | 300 definitions (150 MELODY + 150 PATTERN); partial catalog only |
| 500 core presets (250 MELODY + 250 PATTERN) | NOT COMPLETE; PATTERN must be distributed across its own windows/sections, not one flat list |
| BASIC LIBRARY (minimum 15 GB included; no hard cap) | CONTRACT PRESENT; AUDIO PAYLOAD NOT COMPLETE |
| L3XTOWN local copy preflight / FACTORY copies | NOT CONFIRMED |
| SKIN registry | exactly 16 logical entries; only SKIN-1 currently marked runtime-ready |
| SKIN-2…SKIN-16 | named premium manifests + 45 SVG layers + 30 PNG preview/hero assets PRESENT; source asset audit/build/CTest PASS; REV.20 runtime/host acceptance PENDING |
| Windows x64 Release build on REV.20 SHA | PASS on `142013dbeb315b95246fdcd476f4485af0aa659b`; full CTest then failed 12/14 and fixes are in progress |
| Full CTest on REV.20 SHA | FAILED 12/14 on `142013dbeb315b95246fdcd476f4485af0aa659b`; two test-only defects fixed, rerun pending |
| pluginval strictness 5 on REV.20 SHA | NOT RUN / NOT CONFIRMED |
| FL Studio 20 host acceptance on REV.20 SHA | NOT RUN / NOT CONFIRMED |

## Premium skin asset evidence (source branch; not yet REV.20-host accepted)\n\n- PR #43 merged 2026-11-15 establishes NEON STAGE DEFAULT as SKIN-1 / skin-053; it is a visual integration checkpoint, not a full release pass.\n- Draft PR #58 source SHA `10e590c8a3fdfed90cc7ae05e0ff74d8875ac88a` contains the completed named sequence SKIN-1…SKIN-16 and the 30 preview/hero PNG files for SKIN-2…SKIN-16.\n- Source artwork audit run [43835887953](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-/actions/runs/43835887953) passed. Source Windows x64 configure/build, full CTest, strict 16-skin asset/registry checks and 16-only package run [43835886032](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-/actions/runs/43835886032) passed.\n- These results are tied to the source branch SHA, not the REV.20 commit. Runtime host acceptance in FL Studio 20 and pluginval strictness 5 remain pending.\n\n## Approved production sequence and gates

1. Preserve and reconcile source inventories and licensing.
2. Run local preflight against the actual Windows L3XTOWN source folder; never overwrite or destructively alter originals.
3. Complete the included 15 GB BASIC LIBRARY from redistributable/owned recordings.
4. Complete 500 core factory presets (250 MELODY + 250 PATTERN) from BASIC LIBRARY alone.
5. Review sample mapping, provenance, rights, hashes, performance and human listening.
6. After the approved content gate, run exact-SHA Windows Release build, CTest, pluginval, package checks and separate FL Studio 20 acceptance.

Static validation utilities and focused contract tests may be used for engineering diagnostics where appropriate, but they are not audio-quality, playable-preset or host acceptance. Release readiness remains blocked until every applicable gate has exact evidence.

## CI

- The pre-existing `library-manager-tests.yml` workflow is retained unchanged.
- `.github/workflows/rev20-windows-vst3-skin-validation.yml` is the REV.20 Windows x64 workflow. It checks out the exact `main` commit, installs JUCE 7.0.12, configures/builds VST3, runs full CTest, validates the exact 16 named skins including every preview/hero PNG CRC/dimension, and uploads the VST3 artifact.
- This workflow was added in the current consolidation sequence; its exact latest-SHA run is pending until a completed Actions result is observed.
- `pluginval` strictness 5, package distribution checks, DPI 100/125/150% and FL Studio 20 host acceptance are not covered by this initial CI job and remain explicit release gates.
- The one-time consolidation workflow and importer were removed after the migration commit.


## Latest exact-SHA diagnostic (2026-11-20)

- Run [44707491026](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/44707491026) on SHA `38796efe971847cd7b3d9f843995ed3e45f3c8de`: Windows runner and CMake configure passed; build failed on ambiguous JUCE `var == false` in the newly expanded ThemeManager test. CTest, skin validator and VST3 upload were skipped.
- Fixed the test to explicitly convert `runtimeReady` to bool. Fixed the strict PNG signature parser to compare the real PNG signature bytes. These changes are being pushed and require a new Windows run.
- No successful REV.20 VST3 build/CTest is claimed yet.


## Library tier contract

- `assets/library/library_tiers.json` is the machine-readable v1.2.0 contract: BASIC 15 GB minimum included, EXPANDED +15 GB initial optional add-on (30 GB combined), all 500 core presets usable from BASIC alone.
- `tools/validate_library_tiers.py` and `tests/TestLibraryTierContract.py` validate the actual v1.2.0 field names; the test is registered in CTest.
- This is contract/test coverage, not evidence that 15 GB of licensed samples or 500 playable presets exist in the repository.


## Latest source-branch decisions reconciled (2026-11-18 / 2026-11-19)

- The complete user-approved Library Manager acceptance contract is now preserved at `docs/REV20_LIBRARY_MANAGER_APPROVED_REQUIREMENTS.md`; it requires full scan → analyze → classify → register → verify → plugin access → playback → READY, plus safe physical distribution and reconciliation. Its v1.5 audit findings remain implementation gaps unless separately evidenced.
- The latest skin quality direction (source main commits 9dc719b…662ff905, 2026-11-19): NEON STAGE is the premium finish benchmark, not a template to copy. Every other shell must be equally premium while distinctly original. OBSIDIAN SKIN-2 must use its own restrained blackened-metal/luxury visual direction, not neon/cyberpunk treatment.
- The current logical theme names, count and stable IDs remain the explicit 16-item REV.20 registry. No theme count or label changed in this update.


## Latest REV.20 Windows evidence

- On exact SHA `142013dbeb315b95246fdcd476f4485af0aa659b`, Windows x64 configure and VST3/all C++ target build passed. CTest ran 14 tests: 12 passed, 2 failed.
- Failure 1 was a test assertion using unpadded stable IDs and incorrect artwork path resolution. Failure 2 was a test importing a missing module. Both are corrected in the next REV.20 commit; a narrowly scoped SFZ path-safety helper is added, not a full sample-library audit engine.
- The skin asset validator and artifact upload were skipped due to CTest failures. Do not claim CI green until a fresh exact-SHA run completes every step.


## 16-skin runtime artwork integration (2026-11-20)

- Imported the safe SVG asset loader and reference-counted palette artwork from the source PR #58 work branch, preserving the REV.20 default label `NEON STAGE DEFAULT` and current 16-theme identity mapping.
- Main editor, auxiliary panels, gallery, Pattern/AutoChords, performance and floating workspace now draw the selected skin's texture/bezel/crest layers. Gallery shows only ALL SKINS and FAVORITES ONLY. Existing preview/apply/cancel workflow and favorite persistence remain.
- Added ThemeManager test decoding all three SVG layers for each of the 16 manifests. Exact-SHA workflow 44717722638 passed the Windows build, full CTest, all 16 SVG decodes and 16-only package stage; all registry runtimeReady flags are now true.
- Added 16-only package staging and included the matching SKIN directory in the VST3 artifact. Exact-SHA workflow 44717722638 passed; artifact 14621145514 has digest e1dead01c61d7ace25362bc4c76dc55a03280ada746f9c242c39841d406ff006. FL Studio 20 host acceptance, pluginval and DPI/performance gates remain open.


## Exact target CI: all 16 premium skins runtime-ready

- Workflow [44717722638](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/44717722638), SHA `8cfd11ecce3c8039360c1c194be5251e716c9015`: SUCCESS.
- Windows x64 VST3 build: PASS; full CTest: PASS; ThemeManager manifest load and three SVG layer decodes for all 16 themes: PASS; 32 PNG dimension/CRC and exact registry validation: PASS; 16-only package staging and combined VST3/Skins artifact upload: PASS.
- Artifact ID `14621145514`, size 5,855,768 bytes, SHA-256 `e1dead01c61d7ace25362bc4c76dc55a03280ada746f9c242c39841d406ff006`.
- All 16 themes are now selectable in the REV.20 gallery (`runtimeReady=true`). This does not claim manual FL Studio 20 host acceptance or pluginval strictness 5.

## PageCache publish rollback — selectively ported from source PR #2

- Exact-key rollback fix and regression cases have been added to the next target integration commit.
- Invalid page geometry now returns the matching loading reservation to empty only after confirming that the slot still contains the same PageKey. A stale worker with a mismatched key must not reset a newer reservation.
- Await exact-SHA Windows build/CTest after this current patch is pushed.


## PageCache publish rollback — target exact-SHA verified

Workflow [44719521911](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/44719521911) on `974c5877d1a0375100539d2513329a38feb84871` completed SUCCESS. Windows x64 VST3 build, full CTest 15/15, exact 16-skin validator, 16-only package staging and artifact upload all passed. This run includes the PageCache invalid geometry rollback and stale PageKey regression tests.

Artifact ID `14620284899`, size 5,857,503 bytes, SHA-256 `59b87d1caaa6aaf3b72b89edce6fd2311c23d673960b0c5459658e1a1aab0f30`.

## Next code slice — live AMP TONE / EQ Frequency / Compressor Amount

Selective source-main DSP patch and automated CTest guard are staged for the next commit. They add no APVTS IDs. New target build/CTest is required; do not mark this slice verified until it passes.


## DSP parameter wiring — PORTED, exact-SHA validation pending

- Live eqLowFreq / eqHighFreq crossover, AMP TONE high-band tilt, and compressorAmount dry/processed blend have been added to the existing processor DSP block.
- New Python test checks parameter declaration + consumption and that compressor Amount is not loaded inside the per-sample loop; registered with CTest. Expected CTest count is now 16.
- Previous commit 974c5877… remains green at 15/15 including PageCache fix; the new DSP patch requires its own successful exact-SHA build and 16/16 CTest run.


## Live DSP control wiring — target exact-SHA PASS

Workflow [44721066388](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/44721066388), SHA `7ea16a30f8abaaae6edf8f0c4e58814864cf4fc2`, completed SUCCESS: Windows x64 VST3 build, full CTest 16/16, all-16 skin validation, 16-only package staging and artifact upload. The new `ppgu_fx_dsp_parameter_wiring` test passed. EQ crossover frequencies and AMP TONE now have live DSP effect, and compressor Amount controls the processed/dry blend with its parameter read once per block.

Artifact ID `14622101740`, SHA-256 `086eba4ad405db45d2674603d07bfbbe3d083091e4d9638f7806494e623858b4`.

## Sound Hunter CC0 acquisition subsystem — added; payload gate pending

- Added pinned-source repository archive acquisition, SHA-256 provenance, safe archive member validation, fail-closed existing library hashing and current-run rollback on failure.
- Added importer regression tests, soundbank policy audit and split-artifact integrity tests. These are registered in CTest; target suite is now expected to contain 19 tests.
- Added independent Ubuntu workflow `.github/workflows/rev20-sound-hunter-import.yml` to fetch allowlisted CC0-1.0 real guitar sources and upload split payload + registry/provenance. The artifact, measured unique size, license records and mappings must be audited before any content is promoted to BASIC/EXPANDED.
- The new workflow's first actual acquisition run is pending. No payload size or 500 playable preset completion is claimed.

## CI pluginval update

The Windows VST3 workflow now runs official pluginval Windows 1.0.4 at strictness level 5 after CTest, skin validation and package staging. Pass/fail is pending on the new target SHA. Manual FL Studio 20 remains separate.


## Sound Hunter acquisition retry — API quota hardening

- Run 44722128778 failed with GitHub HTTP 403 rate limit exceeded at the first unauthenticated repo metadata request. No audio payload or sample package was created.
- The importer now adds the Actions job's read-only `GITHUB_TOKEN` to GitHub API requests and Git LFS batch requests. The Ubuntu workflow passes `github.token`; tests cover both token-enabled and public/no-token header cases.
- Importer, policy and artifact splitter test suites passed on the first run; re-run the acquisition workflow on the updated main SHA before claiming any source acquisition.
