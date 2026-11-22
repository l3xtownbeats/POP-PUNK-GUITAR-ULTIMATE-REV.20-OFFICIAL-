# REV.20 — ХРОНОЛОГИЯ УТВЕРЖДЁННОЙ БАЗЫ И ПЕРЕНОСОВ

**Канонический проект:** `l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-`  
**Каноническая ветка:** `main`  
**Период сверки:** 2026-11-13 — 2026-11-20  
**Правило:** каждый следующий подтверждённый пункт уточняет предыдущие; самая свежая пользовательская фиксация — действующая база.

## 2026-11-15 — NEON STAGE / SKIN-1

Исходный PR #43 в репозитории `POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-` был merged 2026-11-15.

- Каноническая оболочка: **NEON STAGE DEFAULT**.
- Логический номер: **SKIN-1**.
- Стабильная идентичность: `skin-053` / `Skin_053` / index 53.
- NEON STAGE определяет общий визуальный язык интерфейса, типографику и палитру существующих реальных контролов.
- Скоуп визуальный: не изменять Audio Engine, DSP, MIDI, APVTS, parameter IDs, sampler, preset content, audio callbacks и существующие control bindings.
- PR #43 был интеграционным visual checkpoint. Его описание прямо оставляло Windows build, полный CTest, pluginval, runtime package и FL Studio 20 host acceptance открытыми.

## 2026-11-15 — 2026-11-16 — утверждение полного набора из 16 имён

В ветках REV.18/REV.19 и последующем 16-skin registry work зафиксирована полная логическая последовательность. Это **ровно 16 оболочек всего**, а не 16 дополнительных поверх главной:

| Logical ordinal | Утверждённое имя | Stable ID | Stable index |
|---:|---|---|---:|
| SKIN-1 | NEON STAGE DEFAULT | `skin-053` | 53 |
| SKIN-2 | OBSIDIAN GOLD | `skin-103` | 103 |
| SKIN-3 | CARBON FORGE | `skin-104` | 104 |
| SKIN-4 | MIDNIGHT CRIMSON | `skin-105` | 105 |
| SKIN-5 | ARCTIC PLATINUM | `skin-106` | 106 |
| SKIN-6 | VIOLET NOIR | `skin-107` | 107 |
| SKIN-7 | TITANIUM STORM | `skin-108` | 108 |
| SKIN-8 | EMERALD CIRCUIT | `skin-109` | 109 |
| SKIN-9 | SOLAR FLARE | `skin-110` | 110 |
| SKIN-10 | DEEP OCEAN | `skin-111` | 111 |
| SKIN-11 | ROSE CHROME | `skin-112` | 112 |
| SKIN-12 | DESERT AMBER | `skin-113` | 113 |
| SKIN-13 | GLACIER TEAL | `skin-114` | 114 |
| SKIN-14 | PHANTOM GRAPHITE | `skin-115` | 115 |
| SKIN-15 | ULTRAVIOLET DRIVE | `skin-116` | 116 |
| SKIN-16 | VOLCANIC STEEL | `skin-117` | 117 |

Stable IDs and indices are immutable source identities. They are **not** logical gallery ordinals. The gallery order must always use ordinal 1…16. No other themes or legacy batches may be active or selectable.

## 2026-11-16 — premium artwork / draft PR #58

Source branch: `work/approved-16-skins-completion`  
Source SHA: `10e590c8a3fdfed90cc7ae05e0ff74d8875ac88a`  
PR #58 remains a draft/open source PR; REV.20 imports the approved assets selectively, not the branch wholesale.

The source branch completed the named premium visual pack:

- 15 distinct additional material/art-direction briefs for SKIN-2…SKIN-16.
- 45 SVG foundations: per theme `texture.svg`, `bezel.svg`, `crest.svg`.
- 30 PNG assets: 15 `preview.png` at 360×240 and 15 `hero.png` at 800×450.
- All 15 additional preview images were visually reviewed; ARCTIC PLATINUM vs GLACIER TEAL and VIOLET NOIR vs ULTRAVIOLET DRIVE were specifically differentiated.
- Strict source asset and 16-entry registry audit: 0 errors / 0 warnings, according to the PR and workflow result.

Source evidence on the exact SHA:

- Artwork generation + strict audit [workflow 43835887953](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-/actions/runs/43835887953) — SUCCESS.
- Windows x64 configure/build + full CTest + strict 16-skin asset/registry checks + 16-only VST3/Skins packaging [workflow 43835886032](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-/actions/runs/43835886032) — SUCCESS.
- Artifact: `PPGU-Windows-x64-VST3-REV19-16-SKINS`.

These results prove the source-branch pack/build gates on that SHA, not an exact-SHA REV.20 build or FL Studio 20 host acceptance.

## 2026-11-16 — Library size decision, newer than the earlier 10–12 GB planning estimate

Draft PR #59 records the newer library-tier baseline:

- BASIC LIBRARY: **15 GB**, included in the standard product.
- EXPANDED ADD-ON: **+15 GB**, optional.
- Initial combined tier: **30 GB total** (15 + 15), not 30 GB added on top of BASIC.
- EXPANDED may grow beyond the initial 30 GB without a product-imposed cap.
- The 500 core presets must be usable from BASIC alone.
- PR #59 explicitly states this is a requirements/contract change, not proof that payloads or 500 playable presets have already been delivered.

## 2026-11-20 — final user-approved REV.20 product baseline

The user reconfirmed and locked the following as the canonical basis:

### Visual shell system

- Exactly **16 graphical shells total**.
- Main/default shell: **NEON STAGE DEFAULT / SKIN-1**.
- Exactly 15 additional shells: **SKIN-2…SKIN-16**, using the fixed names in the table above.
- No 17th theme, no extra packs, no 50-theme batch and no 102-theme gallery.
- All future skin work must preserve the named 16-item sequence and stable-ID mapping.

### Main product modes and preset bank

- Exactly **two main modes**: **MELODY** and **PATTERN**.
- AUTOCHORDS, FX EDIT, Import Guitar, Settings, library tools and other panels are auxiliary windows/functions, not separate top-level modes.
- Core factory bank: **500 presets total** — **250 MELODY + 250 PATTERN**.
- All 500 core presets must operate from the 15 GB BASIC LIBRARY alone.
- The 250 PATTERN presets must be distributed across relevant PATTERN windows, sections and functions. They must not be placed in a single flat list/screen of 250 items.
- The 500 presets define the primary included bank; the catalog can expand beyond 500.
- The existing 300-entry authored catalog (150 + 150) is partial work, not proof of 500 complete/playable presets.

## Current evidence interpretation

- **APPROVED / LOCKED:** user has approved the product decision and identity.
- **ARTWORK PRESENT:** manifests, SVG and PNG files are present.
- **SOURCE-CI VERIFIED:** named source SHA passed the source branch audit/build/tests indicated above.
- **REV.20 VERIFIED:** only after a successful check against the exact current REV.20 commit SHA.
- **HOST-VERIFIED:** only after actual FL Studio 20 validation and evidence.
- **RELEASE-READY:** only after build, full tests, pluginval, package, licensing and host gates pass.

A source-branch pass must never be reported as a REV.20 pass. A design preview must never be described as a running VST3 screenshot.


## 2026-11-16 — PR #59 library capacity contract (newest library sizing baseline)

Draft PR #59, branch `feat/factory-library-15gb-expanded-30gb`, source SHA `c2f52959fd509d7a0bd247e4ea0f7bf836fb9fe3`, records:

- BASIC minimum 15 GB decimal, included in standard product package; 500 core presets playable from BASIC alone.
- EXPANDED +15 GB optional add-on; 30 GB initial combined total; no hard maximum, never replaces BASIC.
- Automatic sample discovery, analysis, classification with review gates and automatic distribution; no required manual per-WAV assignment.
- SHA-256/provenance/license retention, exact duplicate handling, no disk/blocking/unbounded allocation in audio callback.
- Quality-first payload selection and replacement; don't pad with duplicate audio or degrade quality to satisfy a nominal size.

REV.20 selectively imported the v1.2.0 machine-readable tier contract, validator and tests. The PR's original validator/test used inconsistent schema version/property names; REV.20 corrected them to match the committed JSON contract and registered the test in CTest. The PR remains a draft; neither the audio payload nor 500 playable presets is claimed delivered.

## 2026-11-20 — first REV.20 Windows CI diagnostics

- Run 44707491026 on SHA `38796efe971847cd7b3d9f843995ed3e45f3c8de` configured successfully but the build failed because a JUCE `var` was compared directly with `false` in the expanded skin test (C2666). This was fixed with explicit boolean conversion. The PNG signature validator was also corrected to test the real eight-byte signature.
- Run 44715731925 was started on SHA `142013dbeb315b95246fdcd476f4485af0aa659b`; check its final result separately. It is not a completed pass until a terminal GitHub Actions conclusion is recorded.


## 2026-11-18 — Library Manager approved requirements extended to full operational acceptance

Latest source main sequence: commits `2843ebf` → `d8eacc0` → `ba0abfa` → `dc1fc8d` → `47364a4` → `bba98cc` → `9fdab47` → `3b84d2e` → `a7c05ba`.

- One shared standalone/in-plugin scanner engine and workflow, identical trigger semantics and diagnostics.
- Mandatory completion certificate and full reconciliation: every source file accounted for; normal exclusions are not treated as technical failures; critical errors are explicitly reported.
- Full scan/analyse/classify/register/verify/plugin-access/playback/READY flow.
- Physical FACTORY/Other distribution must be transactional, no-overwrite, checksum-verified, dependency-safe and recoverable. Preview/dry-run alone does not constitute completion.
- Stable IDs, portable relative paths, database schema migration/governance, secure optional GitHub handoff, no audio payload/secrets in metadata uploads.
- v1.5 source audit findings are documented honestly: scan prototype lacks physical distribution, complete SFZ parsing, RF64 handling, broad audio decoding, persistent IDs, transactional relational DB, connected license review and full end-to-end recovery tests.

The complete frozen source contract is preserved in `docs/REV20_LIBRARY_MANAGER_APPROVED_REQUIREMENTS.md`. It is a requirements/acceptance baseline, not a statement that these capabilities are complete in REV.20.

## 2026-11-19 — Global premium skin quality standard confirmed

Source commits `9dc719bc4929516c00a00c3b5025859328812d2f`, `d3c26c39eafd432440bff425151ff5004495c9b0`, `fd2c5529fa46b561521b9e44e35e89737631e871`, and `662ff9054c120ed0e0b41726ff4f1a0673c251ca` record the final user confirmation:

- NEON STAGE is the quality/finish benchmark for all 15 additional skins.
- Equal perceived premium quality, detail, polish and commercial appeal; not a copy of NEON STAGE.
- Every additional theme needs its own original material, palette and identity.
- OBSIDIAN SKIN-2 is specifically a premium/luxury blackened-metal theme with restrained metallic highlights; no acid neon, saturated glow or gamer/cyberpunk treatment.

This 2026-11-19 direction is newer than the initial PR #58 theme concept notes and is now carried as an explicit quality requirement in REV.20. It does not change the fixed 16 theme names or stable ID mapping.


## 2026-11-20 — REV.20 exact-SHA runtime verification of all 16 skins

Run [44717722638](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/44717722638) on SHA `8cfd11ecce3c8039360c1c194be5251e716c9015`: SUCCESS for Windows x64 VST3 build, full CTest, exact 16-skin registry, all preview/hero PNG CRC/dimensions, ThemeManager load and all 48 SVG-layer decodes, 16-only sibling package staging and combined artifact upload. Artifact `14621145514`, SHA-256 `e1dead01c61d7ace25362bc4c76dc55a03280ada746f9c242c39841d406ff006`. All 16 skins are runtimeReady in REV.20. FL Studio 20 host acceptance and pluginval strictness 5 remain separate release gates.

## 2026-11-20 — PageCache publish rollback from source PR #2 ported

REV.20 selectively ports the exact-key rollback fix and regression tests. Invalid page geometry releases only the slot reservation whose PageKey still matches; stale/mismatched worker operations cannot cancel a newer reservation. The target build/CTest for this patch is still pending.


## 2026-11-20 — PageCache correction passes on exact REV.20 target

Run [44719521911](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/44719521911) on SHA `974c5877d1a0375100539d2513329a38feb84871` completed SUCCESS: Windows x64 configure/build, full CTest 15/15, 16-skin exact registry/PNG/SVG validation, 16-only package and artifact upload. PageCache invalid-geometry rollback and stale-key regression were included in the passing target suite. Artifact `14620284899`, SHA-256 `59b87d1caaa6aaf3b72b89edce6fd2311c23d673960b0c5459658e1a1aab0f30`.


## 2026-11-20 — live AMP TONE / EQ Frequency / Compressor Amount DSP slice

Selective port from source main: eqLowFreq/eqHighFreq now control crossover cutoff; AMP TONE independently tilts high band and remains active when 3-band EQ is bypassed; Compressor Amount is block-snapshotted outside the sample loop and blends dry/processed gain. Existing APVTS IDs retained. Added `tests/test_fx_dsp_parameter_wiring.py` and CTest registration. Previous target commit `974c5877...` passed 15/15 tests; this addition raises the suite to 16 and requires the next exact-SHA Windows run.


## 2026-11-20 — AMP TONE / EQ / Compressor DSP slice validated in REV.20

Workflow [44721066388](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/44721066388) on exact SHA `7ea16a30f8abaaae6edf8f0c4e58814864cf4fc2` completed SUCCESS: Windows x64 VST3 build, full CTest 16/16, 16-skin validator, 16-only package staging and artifact upload. The new `ppgu_fx_dsp_parameter_wiring` test passed. Artifact `14622101740`, SHA-256 `086eba4ad405db45d2674603d07bfbbe3d083091e4d9638f7806494e623858b4`.

## 2026-11-20 — Sound Hunter acquisition pipeline staged

REV.20 now includes the source's 11-source CC0-1.0 real guitar catalog and an importer improved for source SHA pinning, archive digests, fail-closed existing hashes, cross-platform ZIP path safety and per-run rollback. A separate Ubuntu workflow executes the acquisition and produces a split, checksum-verified artifact with a provenance registry. First acquisition run and measured payload size remain pending; this does not yet satisfy the 15 GB BASIC or 500 playable preset gate.


## 2026-11-20 — Sound Hunter first acquisition attempt blocked by API rate limit

Run [44722128778](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/44722128778) passed discovery and all three Python test suites but failed at initial GitHub API lookup with unauthenticated HTTP 403 rate limit. No asset archive was acquired, and package/upload were skipped. The importer/workflow were updated to use the Actions read-only GITHUB_TOKEN for GitHub API and Git LFS batch calls, with new header tests. Retry on the next exact main SHA is required.


## 2026-11-20 — Sound Hunter pipeline reconciliation
Source main contains a real-recorded-guitar acquisition tool, catalog and manual workflow. The importer verifies actual license text, release SHA256SUMS, LFS payload SHA-256, file sizes, safe paths and duplicate-content suppression. The target workflow is manual-only with an explicit acquire_samples boolean. The copied 300-entry binding plan remains planning-only and READY=0. No completed source Sound Hunter run was found, so no sample payload is claimed acquired.


## 2026-11-20 — Sound Hunter CI diagnostic / correction

Workflow 44722586113 (SHA 9ed8a44...) executed the imported Sound Hunter pipeline. Discovery and all regression contracts passed, then the real download phase stopped because the Meta Open Sound repository archive contained multiple LICENSE files. The importer treated that structure as ambiguous and exited. This was corrected by selecting the repository-root-most LICENSE deterministically and adding a regression test for nested LICENSE files. The acquisition workflow is now manual opt-in; a fresh run is required for real audio acquisition.


## 2026-11-20 — final current automated target baseline

Workflow 44729083554 on exact SHA `10b05a0117366cf33afeb194b3c28456f30fef80` completed SUCCESS. It passed Windows x64 VST3 build, full 19/19 CTest, exact 16-theme validator, 16-only package staging and pluginval strictness 5. Artifact 14625308194 / SHA-256 `72e31eb39e36301c2f3dfa070e9ef277c6d5a360d2907db12f4e4a25e219e864`.

This is the latest automated baseline. Host/manual and content gates remain separate.


## 2026-11-22 — user approval: NEON STAGE / Session Guitarist-inspired guitar workflow

The user explicitly approved and locked the functional direction. The approved reference is limited to the usability concept of Session Guitarist – Electric Sunburst Deluxe/Vintage; NEON STAGE DEFAULT remains the only approved visual source of truth. No NI branding, artwork, proprietary presets, recordings, riffs or protected UI composition may be copied.

- Exactly two top-level modes remain: MELODY and PATTERN. Auxiliary functions/windows do not become additional modes.
- PATTERN keeps instrument source/profile, tone preset, and recorded performance articulation/variation as three independent choices. Tone/FX never replace playing technique.
- Only recorded, mapped, legally usable articulations may be exposed as available. Unmapped techniques remain unavailable; no synthetic substitute may be represented as recorded guitar.
- Original pop-punk vocabulary, host-sync switching, clean transitions, bounded polyphony and optional non-default layering remain binding.
- Preserve the approved NEON STAGE palette, composition, controls, parameter IDs and visual language. All new UI must be native to that system.
- UI checkpoint commits: dbb05b8872746ad31fd0bce3103bb94e6f45358a, a9021d4a16fb3d4a7a1b3fa186acee3b49fd123c. This does not mean the audio performance engine is complete.
- Current static audit confirms articulation and palmMuteThreshold are declared in APVTS but were not found consumed by the processor audio path. Next engineering workstream is recorded articulation metadata/routing into SamplerEngine and PatternScheduler with velocity selection and note lifecycle tests.
- CI run 44997292780 for source SHA a9021d4a16fb3d4a7a1b3fa186acee3b49fd123c was in progress at the time of this entry; no exact-HEAD pass, pluginval pass or FL Studio 20 host acceptance is claimed.
