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


## 2026-11-22 — NEON STAGE main-window visual polish checkpoint

Scope: visual shell only. Audio engine, DSP, sampler, MIDI routing, APVTS parameter IDs/ranges and preset data are unchanged.

- Main panel chrome now uses the approved REV.20 hierarchy: **PRESETS / PLAYING CORE / AMP & TONE / FX CHAIN**. The auxiliary AutoChords and FX Edit functions remain separate windows/pages, not main panel identities.
- Header discovery action is named **AUTO DISCOVER**, matching the approved control vocabulary; it remains disabled until a real discovery backend exists.
- **ABOUT** is disabled with an explicit tooltip until a verified information panel is implemented; no placeholder action is exposed as a finished feature.
- MELODY/PATTERN tabs now mirror the actual APVTS play-mode selection with explicit selected/unselected visual states. The selected state is refreshed on mode changes and at editor initialization.
- The authored Skin-1 five-state artwork is now resolved for the six header controls that have matching control-state assets: Import_Guitar, Auto_Discover, Curator, Settings, About and SKIN_button. Hover/pressed/disabled rendering remains in the JUCE LookAndFeel; no control art is substituted for live text or actions.
- The canonical 1024×700 initial editor size and existing resize limits remain unchanged. No new visual layout, parameter, or control ID was invented.

**Verification status:** source changes committed to main; Windows x64 VST3 build, CTest, pluginval and FL Studio 20 host acceptance remain pending. This is a visual-source checkpoint, not a release-ready claim.


## 2026-11-22 — Постоянный индекс расположения исходников и утверждённых материалов (обязательная точка входа)

Пользователь потребовал фиксировать в журнале точные пути к исходникам и материалам, чтобы не запрашивать повторно уже имеющиеся в репозитории файлы. Проверено непосредственно по GitHub API: репозиторий `l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-`, ветка `main`.

**Корень проекта:** `/` (корень указанного GitHub-репозитория).

**Главный утверждённый визуальный макет — уже находится в репозитории, повторно у пользователя не запрашивать:**
- `/01 INTERFACE  NEON STAGE DEFAULT .png` — canonical NEON STAGE DEFAULT, единственный visual source of truth. Git blob SHA: `747207e183c77e8b913a543b2dc40b29829e77da`.
- Дополнительные утверждённые экраны: `/02 INTERFACE  NEON STAGE DEFAULT AUTOCHORDS .png`, `/03 INTERFACE  NEON STAGE DEFAULT .png`, `/04 INTERFACE  NEON STAGE DEFAULT .png`, `/05 INTERFACE  NEON STAGE DEFAULT .png`, `/06 INTERFACE  NEON STAGE DEFAULT .png`, `/07 INTERFACE  NEON STAGE DEFAULT .png`. Это отдельные reference/mockup-файлы; не подменять ими главный экран 01.

**Ключевые исходники приложения:**
- `/CMakeLists.txt` — корневая конфигурация сборки.
- `/Source/PluginEditor.cpp`, `/Source/PluginEditor.h` — главный JUCE editor и UI.
- `/Source/PluginProcessor.cpp`, `/Source/PluginProcessor.h` — audio processor/APVTS/MIDI integration.
- `/Source/UI/` — UI/workspace/theme/sprite/control-state implementation: `AuxiliaryPanelLayout.*`, `PPGUControlState.h`, `PPGUDiscoveryRadar.*`, `PPGUMultiWindowWorkspace.*`, `PPGUStageSpriteSheet.*`, `SkinGallerySelection.h`, `ThemeManager.*`.
- `/Source/Performance/` — `AutoChordGenerator.h`, `ChordTransitionPolicy.h`, `ChordTransitionTimeline.h`, `PatternScheduler.h`.
- `/Source/Sampler/` — SFZ parser, SamplePool, metadata index, streaming service/readers, PageCache and bounded queue; конкретные файлы перечислены в дереве этой папки.
- `/Assets/3D/References/` — authored 3D/UI source references and master prompt `PPGU_REV20_NEON_STAGE_DEFAULT_ULTIMATE_ASSET_MASTER_PROMPT_RU.txt`. Не считать все файлы в References финальными runtime assets без проверки.
- `/SKINS/` — skin artwork/source package tree.
- `/assets/` — product/library/sound-asset registry sources; включая `assets/library/library_tiers.json`, `assets/sound_hunter/registry.json` и `assets/POP_PUNK_GUITAR_ULTIMATE_BANNER.svg`.
- `/presets/` — factory/examples/binding-plan sources; включая `presets/factory_bank_300.json`, `presets/rev20_sound_hunter_binding_plan.json`, `presets/examples/`.
- `/tests/` — C++ и Python tests, включая SFZ/Sampler/Pattern/UI/Theme/FX/skin/library contracts.
- `/tools/` — build, inventory, sprite generation, packaging, validation and audit scripts.
- `/docs/` — технические спецификации, решения, аудиты, acceptance checklists и журналы проекта.
- `/.github/workflows/` — CI/workflows: `neon-stage-native-ci.yml`, `rev20-windows-vst3-skin-validation.yml`, `rev20-sound-hunter-import.yml`, `skin1-control-state-ci.yml`, `library-manager-tests.yml`.

**Основные журналы/контрольные документы:**
- `/docs/REV20_DECISION_TIMELINE_RU.md` — основной журнал решений и истории изменений.
- `/docs/REV20_FUNCTIONAL_GAP_AUDIT_RU.md` — функциональный аудит и незакрытые gaps.
- `/docs/REV20_ENGINEERING_WORKSTREAM_REGISTER_RU.md` — реестр инженерных направлений.
- `/docs/REV20_FL20_ACCEPTANCE_CHECKLIST_RU.md` — проверка FL Studio 20.
- `/docs/REV20_ACCEPTED_BASELINE_RU.md` — принятая базовая конфигурация.
- `/docs/PPGU_REFERENCE_DESIGN_ASSET_REGISTER.md` — реестр визуальных исходников.
- `/docs/NEON_STAGE_NATIVE_INTEGRATION_RU.md` — интеграция NEON STAGE.

**Рабочее правило для всех следующих сессий:** прежде чем просить пользователя повторно приложить файл или сообщать, что файл отсутствует, проверить этот индекс, GitHub tree и Library. Canonical 01 PNG уже подтверждён в корне репозитория; не запрашивать его повторно. Если инструмент не умеет отобразить бинарный PNG, это ограничение чтения/рендеринга инструмента, а не отсутствие файла. Для анализа сначала получить/открыть уже существующий GitHub/Library asset доступным способом. Новые точные пути, созданные файлы, commit SHA, CI run IDs и статусы дописывать сюда же.

## 2026-11-22 — визуальный аудит по мастер-промпту и исправление блокирующей сборку ошибки

Проверены непосредственно /Assets/3D/References/PPGU_REV20_NEON_STAGE_DEFAULT_ULTIMATE_ASSET_MASTER_PROMPT_RU.txt, /Source/PluginEditor.cpp, /Source/PluginProcessor.cpp и GitHub Actions run 44998253820 на SHA 7863c648da180e63c7a2fd60d24d67d826ad50aa.

**Подтверждённое расхождение главного layout:**
- Мастер-промпт, раздел 4, определяет трёхзонную структуру: слева FACTORY PRESET BROWSER; в центре PLAYING CORE с девятью регуляторами в сетке 3×3 и режимами MELODY/PATTERN; справа AMP & TONE / FX CHAIN с семью переключателями.
- Текущий PluginEditor.cpp пока размещает девять регуляторов в правой зоне, FX Edit в центральной зоне, а семь FX switches — отдельной горизонтальной полосой снизу. Поэтому заголовки панелей уже обновлены, но фактическая геометрия ещё не соответствует обязательному мастер-промпту.
- Это не следует маскировать косметической сменой заголовков. Следующий layout-pass должен перенести 3×3 controls в центр, собрать семь FX switches в правую rack-зону и оставить FX EDIT вспомогательным окном/панелью. При этом сохранить 1024×700 исходный размер, resize limits, APVTS IDs, attachments и рабочие действия переключателей.
- Не использовать новый/альтернативный дизайн. Порядок и визуальные пропорции проверять только по canonical /01 INTERFACE  NEON STAGE DEFAULT .png и его утверждённому asset master prompt.

**CI диагностика и исправление:**
- Run 44998253820 завершился FAILURE на Windows x64 при компиляции Source/PluginProcessor.cpp:326: вызов JUCE MidiKeyboardState::noteOff передавал два аргумента вместо требуемых трёх.
- Исправлено вызовом keyboardState.noteOff(channel, noteNumber, 0.0f) для очистки transient keyswitch visualization. Commit: cab4f58e8a2fc0109ed85f1c1f8c14e0b7b2e686.
- Повторная Windows x64 сборка и CTest после исправления обязательны; до завершения нового CI run успех не заявляется.

**Статус:** визуальное соответствие layout — OPEN / NOT VERIFIED; исправление compile blocker — COMMITTED / CI PENDING.
## 2026-11-22 — главный layout переведён на утверждённую трёхзонную композицию

В Source/PluginEditor.cpp опубликован layout commit 3dcea2a245b8b287ddf80958c6ea1f6fd55dcd5e:
- LEFT: FACTORY PRESET BROWSER с категориями, поиском и каталогом.
- CENTER: PLAYING CORE; MELODY/PATTERN и все девять APVTS-linked rotary controls теперь размещаются сеткой 3×3.
- RIGHT: AMP & TONE / FX CHAIN; ровно семь существующих FX switches размещаются вертикально в rack.
- LOWER: performance display, горизонтальная MIDI keyboard (36–84) и library status.
- FX EDIT больше не занимает центральную поверхность; каждый из семи FX switches открывает вспомогательное FX EDIT окно через openFxEditPanel(). FLANGER остаётся отдельной страницей FX EDIT, а не восьмым главным переключателем.
- Сохранены размеры 1024×700, limits 900×640–1600×1100, существующие APVTS IDs/attachments и component IDs. Заголовок правой стойки приведён к AMP & TONE отдельным commit 039e9faf178eaf73cfbfd1a46139d5cf67c33a13.

**Дополнительная CI находка:** run 45000503467 собрал VST3 и тестовые targets успешно, но CTest завершился 21/22: ppgu_sample_pool_contracts обнаружил, что прямой SamplePool::findRegion без explicit keyswitch не выбирал SFZ default articulation. Исправлено: при activeSwitch < 0 используется snapshot->defaultKeySwitch. Commit 6c495692fba2cdeb99e4c8fb841027ffe16930e6.

**Проверка:** layout и SamplePool fixes committed; CI для финального HEAD ещё ожидается. Не заявлять visual acceptance, VST3 package или pluginval pass до завершения нового run.
## 2026-11-22 — интерактивная детализация NEON STAGE controls

В Source/PluginEditor.cpp опубликован commit d5a750d6896797cdd4cf8cdda4721b7992c41312:
- Девять rotary controls получили осмысленные component names и подсказки с текущим назначением и пояснением числового readout; APVTS attachments и параметрические ID не менялись.
- Семь FX rack switches получили индивидуальные подсказки: назначение каждого эффекта, состояние enable/bypass и возможность открыть детальное окно. Имена компонентов синхронизированы с отображаемыми подписями.
- Заголовки AMP & TONE и FX CHAIN получили поясняющие подсказки.
- Существующая state artwork pipeline (default/hover/pressed/dragged/disabled), sprite atlas и APVTS toggle bindings сохранены.

Проверка run 45001201289 на HEAD 6c495692fba2cdeb99e4c8fb841027ffe16930e6: sprite atlas generation прошла; Windows configure выполнялся. Этот run не включает последующие layout/documentation/tooltip commits. Требуется CI на актуальном HEAD d5a750d6896797cdd4cf8cdda4721b7992c41312. Не заявлять сборку успешной до точного HEAD check.

## 2026-11-22 — подготовка production-вектора для rotary controls NEON STAGE

- Сверена структура существующих ассетов Skin_053: `assets/asset_manifest.json` содержит 308 записей; имеется 27-control × 5-state система (135 PNG), включая девять knob01…knob09; master-контроли 512×512 и runtime 256×256.
- Существующий `neon_stage_rotary_61frame_atlas.png` — 1024×1024, 61 кадр, 128×128 ячейка, диапазон −135°…+135° с шагом 4,5°. Он уже используется в rotary renderer; нельзя подменять его отдельной статичной ручкой или накладывать второй указатель поверх существующего кадра.
- Добавлен масштабируемый векторный мастер `SKIN/Skin_053/assets/vector/rotary_knob_master.svg` (512×512, прозрачный фон): многослойный графитово-стальной корпус, фаска, тёмная эмаль, шкала, сдержанная cyan-подсветка и металлический указатель. Текст и значения не запечены в графику.
- Добавлена спецификация `SKIN/Skin_053/assets/vector/ROTARY_ARTWORK_PRODUCTION_SPEC.md`: состояния default/hover/pressed/dragged/disabled, размеры master/runtime, правила экспорта, список существующих PNG/atlas и обязательные проверки перед заменой.
- Канонический внешний ориентир не меняется: `/01 INTERFACE  NEON STAGE DEFAULT .png`. Новый SVG — исходный производственный компонент, а не новый макет/скин. Перед интеграцией необходимо визуальное сравнение PNG-экспорта с canonical mockup и обновление SHA-256/CRC/asset manifests.
- Изменения не затрагивают JUCE bindings, APVTS, DSP и аудио-путь. Это source artwork/spec addition; не считать production runtime asset integration или visual acceptance завершёнными.


## 2026-11-22 — обновление генератора premium rotary atlas

- Обновлён `tools/generate_neon_stage_spritesheets.py`: генератор 61-кадрового атласа теперь рисует единый machined graphite/steel control с inset enamel face, металлической шкалой, сдержанной cyan sweep, металлическим указателем и центральной подсветкой.
- Рендер выполняется в 2× разрешении с последующим Lanczos downsample до 120×120 внутри 128×128 ячейки; сохраняются 61 кадр, диапазон −135°…+135°, шаг 4,5°, прозрачный RGBA и непрерывное APVTS значение.
- Обновлён `SKIN/Skin_053/assets/spritesheets/neon_stage_spritesheet_manifest.json`: добавлен artworkProfile с указанием SVG master, генератора и характеристик атласа.
- Canonical layout `/01 INTERFACE  NEON STAGE DEFAULT .png` остаётся неизменным. Не добавлялись baked labels и не менялись control geometry, APVTS, DSP или аудио-путь.
- Изменения генератора: commit `a89904886c7d54c46c74c63fb6d8f4ebf78792e9`. Manifest: commit `7d02e657ad385a95d95296df87f4778651c5d3e8`.
- Генератор ещё должен быть исполнен CI; обновлённый PNG atlas и визуальная сверка результата не объявляются готовыми до успешной генерации и проверки артефакта.


## 2026-11-22 — аудит FX controls и генерация production sprite atlases

Проверено текущее дерево GitHub на main HEAD `0b8aa7df2be3c302a07b257a386aee2b237ab8ca`.

- Подтверждено наличие семи отдельных FX switches и пяти runtime states для каждого: `default`, `hover`, `pressed`, `dragged`, `disabled`. Пути: `SKIN/Skin_053/assets/controls/fx_switch01_*.png` … `fx_switch07_*.png`.
- Для тех же семи switches существуют отдельные master PNG в `SKIN/Skin_053/assets/master/controls/`; это 35 master + 35 runtime изображений. Существующие ассеты и manifests сохраняются, повторно не генерируются и не заменяются без pixel-level сравнения с canonical mockup.
- Control state registry `SKIN/Skin_053/assets/controls/control_states_manifest.json` перечисляет 27 control IDs и пять состояний. Artwork manifest `SKIN/Skin_053/assets/artwork_manifest.json` описывает master/runtime layers и основные графические ресурсы.
- GitHub Actions run `45001532775`, workflow `rev20-windows-vst3-skin-validation.yml`: шаги установки Python, Pillow, генерации NEON STAGE atlas и commit generated atlases завершились success. Автоматический commit генератора: `0b8aa7df2be3c302a07b257a386aee2b237ab8ca`; rotary atlas PNG присутствует в дереве: `SKIN/Skin_053/assets/spritesheets/neon_stage_rotary_61frame_atlas.png` (1024×1024, 61 кадр по manifest).
- На момент записи Windows configure ещё выполнялся; build VST3, CTest, 16-skin validation, pluginval strictness 5 и upload artifact ещё не завершены. Этот этап не объявляется release-ready.
- Главный visual reference остаётся неизменным: `/01 INTERFACE  NEON STAGE DEFAULT .png`. Все новые runtime assets должны быть разложены по отдельным master/runtime fragments и states, без baked labels/values, с сохранением реальных JUCE/APVTS state bindings.


## 2026-11-22 — повторная сверка всех макетов 01–07 и Library

- По текущему Git tree проверено, что все семь корневых PNG-макетов существуют и сохранены без изменения. Их точные blob SHA, размеры и назначение внесены в `docs/PPGU_REFERENCE_DESIGN_ASSET_REGISTER.md`.
- Зафиксировано назначение: 01 — единственный источник композиции главного окна; 02 — AutoChords; 03 — FX EDIT / компрессор и MIDI presentation; 04–07 — дополнительные экранные/компонентные ориентиры, которые нельзя механически объединять с главным экраном.
- Проверено хранилище `/PPGU/REFERENCE_ASSETS/`: доступен инвентаризированный набор из 38 оригинальных файлов. Оригиналы не дублируются вслепую в runtime; сначала сравниваются похожие экспорты, далее создаются отдельные производные PNG-фрагменты с provenance и SHA-256.
- Дополнительные исходники `Assets/3D/References/` включают master prompt, Meshy renders, sheets кнопок, ручек, панелей, измерителей и иконок. Они учтены как source artwork для извлечения фрагментов и последующей сверки.
- Текущий `Source/PluginEditor.cpp` уже имеет три зоны, 9 APVTS knobs, 7 FX switches, нижний performance strip и MIDI keyboard; однако в нём пока не найдено подключение отдельного `heroArtwork` в центральной зоне. Полное pixel parity с макетом 01 не подтверждено.
- Открытые PR #11/#12 описывают дополнительные visual QA и main-editor gaps, но не слиты в main; не объявлять их функции внедрёнными. Текущий Windows run `45001532775` ещё выполняет build на SHA `7d02e657ad385a95d95296df87f4778651c5d3e8`; CTest, 16-skin package и pluginval ожидают.
- Пути: `/01 INTERFACE  NEON STAGE DEFAULT .png` … `/07 INTERFACE  NEON STAGE DEFAULT .png`; `/02 INTERFACE  NEON STAGE DEFAULT AUTOCHORDS .png`; `/Assets/3D/References/`; `/SKIN/Skin_053/assets/`; `/Source/PluginEditor.cpp`; `/Source/UI/`; `/docs/PPGU_REFERENCE_DESIGN_ASSET_REGISTER.md`.


## 2026-11-22 — подключение индивидуальных PNG-состояний девяти rotary controls

- Исправлен приоритет отрисовки в `Source/PluginEditor.cpp`: раньше ветка 61-frame rotary atlas завершалась `return` до поиска индивидуальных `knob01…knob09` state PNG. В результате atlas вращался, но PNG-состояния ручек не участвовали в рендеринге при наличии rotary atlas.
- Теперь для каждого knob runtime сохраняет 61-позиционную непрерывную анимацию атласа, а его state artwork из `PPGUThemeManager::Palette::findControlArtwork(controlId, stateName)` добавляется как отдельный прозрачный overlay для hover/pressed/dragged/disabled. Default не накладывается повторно; disabled дополнительно получает читаемое затемнение. APVTS value и pointer animation не меняются.
- Изменение: commit `afb637c44764342d589e0dd846cd5d6a428f47dc`. Путь: `Source/PluginEditor.cpp`.
- Runtime PNG mapping остаётся через Skin-1 `control_states_manifest.json` и `ThemeManager.cpp`; FX switch states уже рисуются через индивидуальные control artwork и реальные JUCE button states.
- Это source-level integration, а не заявление о пройденной Windows-сборке. Требуется дождаться CI на актуальном SHA и проверить CTest/pluginval/визуально в FL Studio 20.


## 2026-11-22 — runtime-подключение atlas icons к управляющим кнопкам

- В `Source/PluginEditor.cpp`, внутри `PPGUPremiumLookAndFeel::drawButtonBackground`, добавлен renderer `drawAtlasIcon`, читающий `Palette::iconsSpriteSheet` и использующий подтверждённые координаты из `SKIN/Skin_053/assets/spritesheets/neon_stage_spritesheet_manifest.json`.
- Подключены иконки FX: wave/EQ/distortion/chorus/delay/reverb/cabinet к семи `fx_switch01…07`; навигационные иконки settings/info/palette/guitar/antenna/crown к соответствующим кнопкам Settings/About/SKIN_button/Import_Guitar/Auto_Discover/Curator. Иконка рисуется поверх фонового state PNG, текст кнопки и JUCE hit target остаются штатными.
- Источник: `SKIN/Skin_053/assets/spritesheets/neon_stage_icons_sheet.png`, 1024×1024; atlas decoded уже существующим загрузчиком `ThemeManager.cpp`. Никакие PNG-источники не изменялись.
- Коммит: `48ccf027f69d782e86345b5dd04965c5202e8d56`.
- Это runtime source integration; требуется Windows CI и проверка компоновки/контраста в host. Контролы без активного backend остаются disabled; наличие иконки не активирует недоступную функцию.


## 2026-11-22 — исправление расхождения палитры NEON STAGE в skin validator

- Проверен Windows workflow run `45002098314` на source SHA `48ccf027f69d782e86345b5dd04965c5202e8d56`.
- Windows x64 configure и build завершились успешно; все 22/22 CTest прошли. Workflow остановился на шаге `tools/validate_skin_registry_16.py`, до staging/package/pluginval/upload, из-за устаревшего ожидания `accent_magenta: #FF007F`.
- Реальный canonical manifest `SKIN/Skin_053/assets/spritesheets/neon_stage_spritesheet_manifest.json` уже задаёт утверждённую палитру `semantic_warning: #FFB454` и не содержит magenta в base palette. Ошибка была в validator, не в runtime artwork.
- Исправлен `tools/validate_skin_registry_16.py`: ожидаемый palette token теперь `semantic_warning: #FFB454`, в точном соответствии с manifest и утверждённым правилом: cyan/blue основной UI, amber/red только warning/error, без purple/magenta.
- Commit исправления: `38ba76fbe1e10c4860bf01d0fe49340c013ab977`.
- Важно: исходный run остаётся failed по validator; это исправление ещё должно пройти новый полный Windows workflow на новом HEAD. Pluginval strictness 5 и VST3 artifact пока не подтверждены.
- Дополнительно проверено подключение визуальных атласов: `framesPanelsSpriteSheet` уже используется в `drawPanel()` для header chrome; `metersSlidersSpriteSheet` уже используется в `drawLinearSlider()` для track/thumb; `iconsSpriteSheet` подключён к FX/navigation controls. Performance display пока рисует собственную живую harmony/status информацию JUCE, а не отдельный VU meter atlas — не подменять его декоративным фейковым измерителем.


## 2026-11-22 — утверждена визуальная база NEON STAGE и следующий этап реализации

Пользователь явно подтвердил и зафиксировал как обязательную базу следующие требования:

- Главное окно воспроизводит утверждённый корневой макет `01 INTERFACE  NEON STAGE DEFAULT .png` без изменения его композиции и геометрии. Это единственный source of truth для главного экрана.
- Все органы управления должны иметь реальное взаимодействие: непрерывное изменение параметров ручек с визуальным вращением, состояния ON/OFF переключателей, реакцию кнопок, hover/focus/pressed/disabled и dragged там, где состояние применимо.
- Рамки, панели, разделители, дисплеи, металлические поверхности и световые акценты должны быть интегрированы как единая тема NEON STAGE, а не как несвязанные декоративные элементы.
- MIDI-клавиатура должна визуально отражать реальные MIDI key-down/key-up события.
- Вспомогательные окна AutoChords, FX EDIT, Import Guitar, Settings, Skin Gallery, Pattern Section и About должны пройти отдельную проверку оформления, размеров, интерактивных элементов и доступности управления.
- Все изменения должны соответствовать ранее утверждённым макетам и описаниям этого журнала. Для функционального UX допустимо использовать NI Session Guitarist – Electric Sunburst Deluxe/Vintage как ориентир удобства и поведения инструментов; не копировать их брендинг, графику, пресеты, записи или музыкальный материал.
- Визуальный этап приоритетен: не переходить к расширению звукового backend до завершения и проверки темы, главного окна, состояний контролов и вспомогательных окон. Auto Sound Hunter и Curator остаются disabled, пока их backend не готов.

**CI checkpoint:** run `45006282828` на SHA `38ba76fbe1e10c4860bf01d0fe49340c013ab977`: Windows x64 configure — success; VST3 и C++ build — success; CTest — 22/22 success. Skin validation остановилась на ошибочном условии валидатора: он ожидал ровно четыре sprite sheets, хотя canonical manifest и ThemeManager содержат пять, включая `neon_stage_rotary_61frame_atlas.png`. Исправление валидатора должно учитывать пятый 61-frame atlas и проверять его геометрию. Из-за остановки на этом шаге staging, pluginval strictness 5 и upload artifact не запускались; VST3 build success не равен pluginval/release acceptance.

**Следующий этап:** устранить только validator mismatch, повторить полный Windows workflow, затем продолжить visual implementation: FX EDIT selection update при уже открытом окне; проверка/подключение LCD, LED и MIDI-keyboard artwork с реальными состояниями; поочерёдный аудит всех auxiliary windows; pixel/geometry review по canonical mockup и журналу. Не заявлять визуальное завершение до реальной проверки.


## 2026-11-22 — визуальная полировка главного и вспомогательных окон (ветка review)

В отдельной review-ветке `visual/neon-stage-polish`, commit `71aad83ef647d417ea23aa934deba95acdd2d5f7`, подготовлены следующие source changes:

- `Source/PluginEditor.cpp`: добавлен 9-slice renderer для утверждённого `neon_stage_frames_panels_sheet.png`; рамки/углы/верхняя и нижняя кромки/боковые грани подключены к трём основным панелям без изменения их layout bounds, размеров или APVTS bindings.
- `Source/UI/PPGUMultiWindowWorkspace.h/.cpp`: добавлен безопасный UI-thread accessor `getPanelContent(id)`; оконная оболочка использует те же 9-slice frame assets, чтобы вспомогательные панели соответствовали общей NEON STAGE chrome.
- `Source/PluginEditor.cpp`: устранено игнорирование выбранного FX при повторном клике на FX switch, когда FX EDIT уже открыт: существующий `PPGUFXEditPanel::setSelectedGroup()` теперь вызывается для уже открытого content-компонента, без создания дублирующего окна.
- About button включён, поскольку в текущем editor уже существует рабочий информационный диалог; прежний disabled state делал обработчик onClick недостижимым. Auto Sound Hunter и Curator остаются disabled из-за отсутствующего backend.
- Не изменялись canonical mockup 01, параметры APVTS, аудио/DSP, основная геометрия или список семи FX switches.

**Статус:** изменения находятся в review-ветке и не считаются прошедшими компиляцию/визуальную приёмку. Перед переносом в main необходимы Windows x64 build, CTest, skin validation, pluginval strictness 5 и проверка отсутствия артефактов отрисовки (особенно 9-slice на разных размерах окна). Это не завершение всего visual stage: LCD/LED/MIDI keyboard state artwork и полный визуальный аудит всех вспомогательных окон остаются открытыми задачами.

## 2026-11-22 — утверждена база подсветки активных элементов NEON STAGE

Пользователь утвердил и зафиксировал в качестве обязательной части визуальной базы NEON STAGE следующие правила подсветки:

- **FX ON/OFF:** включённый модуль имеет отчётливое cyan-свечение и активное состояние; выключенный — приглушённое состояние без свечения.
- **MELODY/PATTERN:** выбранный режим визуально выделен.
- **Ручки:** световая дуга/индикатор положения показывает реальное значение параметра; поворот меняет соответствующий APVTS-параметр.
- **Кнопки и переключатели:** состояния hover, pressed, active, focus и disabled различимы; активное состояние не подменяет нажатие или hover.
- **LED:** светится только при подтверждённом рабочем состоянии связанной функции; не использовать декоративную ложную активность.
- **MIDI-клавиатура:** подсветка отражает реальные MIDI note-on/note-off и состояние клавиш.
- **Дисплеи:** показывают реальные значения/состояния, без фиктивной телеметрии.
- **FX EDIT:** выделяет выбранный эффект и показывает действительное состояние его модулей.
- **SFZ Import:** показывает реальные busy/success/error состояния загрузки.
- Общая палитра: графитовый/анодированный металл, cyan `#00D9FF`, electric blue `#6B8CFF`; amber/red только для предупреждения/ошибки. Фиолетовый/пурпурный не использовать.

Подсветка должна быть связана с реальным состоянием параметра/функции и корректно обновляться при включении, выключении, изменении значения и MIDI-событиях. Это утверждённая визуальная спецификация и база приёмки, а не заявление о том, что все состояния уже реализованы или протестированы.

Главный экран остаётся строго привязан к утверждённому `01 INTERFACE  NEON STAGE DEFAULT .png`; геометрию и композицию не менять. Session Guitarist – Electric Sunburst Deluxe/Vintage допустим только как ориентир UX/поведения, без копирования брендинга, графики, пресетов и аудиоматериала.

## 2026-11-22 — PATTERN cards, AutoChords state LED и FX EDIT audit (review branch)

В review-ветке `visual/neon-stage-polish` внесены следующие визуальные изменения:

- `Source/PluginEditor.cpp`: восемь PATTERN slots представлены интерактивной сеткой из двух колонок и четырёх строк. Выбранная карточка синхронизируется с существующим выбором slot; PREVIEW/APPLY/CANCEL продолжают использовать прежние processor routing методы. Карточки названы именно слотами, а не готовыми ритмическими библиотеками: интерфейс не заявляет о наличии записанного материала там, где его наличие не подтверждено.
- В PATTERN panel добавлена кнопка `OPEN AUTOCHORDS`, открывающая существующую AutoChords workspace через безопасный callback редактора. Минимальный размер окна повышен до 500×420, чтобы сохранить читаемость карточной сетки.
- AutoChords получил реальный LED и текстовый статус, читающие APVTS `singleMidiNoteAsChordRoot`. Обновление выполняется таймером только при изменении состояния; декоративная анимация не используется.
- FX EDIT: проверена существующая привязка POWER через APVTS ButtonAttachment; индикатор уже отражает фактическое состояние выбранного bypass-параметра, а статус показывает ACTIVE/BYPASSED. Смена выбранного FX в открытом окне обновляет текущую группу.
- Исправлена палитра About: доступная кнопка больше не окрашивается токенами disabled/lowlight.
- Основной макет и его геометрия не менялись; DSP, audio callbacks, MIDI routing и идентификаторы параметров не менялись.

**Проверка:** эти новые коммиты пока не имеют подтверждённого CI-результата. Предыдущий CI на SHA `dd3c4694cfccb152de97c0589468c6d1f5948f00` проходил Windows x64 build, CTest, 16-skin validation и staging/upload; он не подтверждает компиляцию последних изменений. Для текущей ревизии требуется повторить Windows x64 VST3 build, contract tests, полный CTest, skin registry validation и package/artifact staging. Отдельно остаются pluginval strictness 5 на текущем SHA и ручная проверка UI в FL Studio 20 при нескольких размерах окна.

## 2026-11-22 — FX EDIT и SFZ import: аудит начального состояния (review branch)

- В FX EDIT устранён случай, когда при первом открытии или выборе эффекта с выключенным bypass-параметром строка статуса могла оставаться общей/устаревшей. Теперь ACTIVE/BYPASSED синхронизируется с текущим APVTS значением независимо от того, изменился ли bool относительно предыдущей группы; LED по-прежнему перерисовывается при реальном изменении состояния.
- Import Guitar теперь получает начальный статус из фактического пути SFZ, уже загруженного процессором. Существующий файл показывается как SAVED LIBRARY/READY, отсутствующий путь — как LIBRARY FILE NOT FOUND/ERROR.
- Классификатор LED импорта различает LOADING, READY/SAVED LIBRARY, STANDBY и явные ошибки (FAILED/ERROR/NOT FOUND); произвольные непустые сообщения загрузчика не маскируются под READY. Светодиод остаётся steady-state, без искусственной анимации.
- Аудио/DSP, формат SFZ и существующие callbacks не изменялись.

**Проверка:** SHA `64e02d7498ddd6a1721c7f204fa3690fc6680299`. На момент записи GitHub connector не возвращает workflow runs или commit statuses для этого SHA. Изменения исходников проверены чтением актуального файла, но компиляция не подтверждена; необходим повтор Windows x64 CI и ручная проверка импортных состояний на стенде.

## 2026-11-22 — пользовательское утверждение базовой реализации NEON STAGE

Пользователь явно утвердил в качестве базовой реализации review-ветки текущие решения по PATTERN (8 карточек, 2 колонки, существующие PREVIEW/APPLY/CANCEL и OPEN AUTOCHORDS), AutoChords (реальное APVTS ON/OFF и LED), FX EDIT (POWER/LED/ACTIVE/BYPASSED и переключение выбранного эффекта в уже открытом окне), оболочке (состояния доступных элементов и корректные статусы), а также ведение этого журнала.

Это утверждение фиксирует продуктовую/визуальную базу для следующих изменений. Оно не заменяет техническую приёмку: текущая ветка должна пройти Windows x64 configure/build VST3, C++ contract tests, полный CTest, 16-skin validation, runtime staging и pluginval strictness 5; после этого нужна ручная проверка в FL Studio 20 при разных размерах окна. До получения этих результатов merge в `main` не выполнять.

## 2026-11-22 — NEON STAGE: полный контракт визуальных состояний и интерактивности (review branch)

### Новая реализация в этом checkpoint

- `Source/PluginEditor.cpp`: linear-slider renderer для Skin-1 теперь явно отображает четыре состояния: normal, hover, drag и keyboard focus; disabled получает отдельное приглушение дорожки и thumb. Световой fill продолжает вычисляться из фактической позиции JUCE Slider/APVTS; декоративное движение и таймерная анимация не добавлены.
- Включённый slider показывает cyan/electric-blue акцент; hover/drag/focus рамка отделена от значения параметра. При disabled значение остаётся видимым в форме положения thumb, но трек/ручка визуально приглушаются и не выглядят активными.
- Изменение не затрагивает APVTS IDs, ranges, attachments, processor/DSP, MIDI, preset state или геометрию главного макета.

### Полный контракт визуальной приёмки по зонам

| Зона/элемент | Источник состояния | Обязательное отображение | Текущий source-level статус |
|---|---|---|---|
| Главная рамка и фон | Skin-1 theme.json + frame/background/material artwork | графитовая металлическая поверхность, чёткая рамка, аккуратные кромки, согласованные световые слои | подключено; pixel parity с макетом 01 требует визуальной host-проверки |
| PRESETS | реальные catalog/search/category controls | поиск, фильтр/категория, выбранный preset, доступные/недоступные состояния | существующие controls; нужна поэлементная проверка кликов/resize |
| PLAYING CORE | APVTS mode + 9 SliderAttachments | две вкладки MELODY/PATTERN; девять ручек; вращение 61-frame atlas; value arc и numeric readout по реальным значениям | привязки и renderer существуют; linear-slider state enhancement добавлен этим checkpoint |
| Ручки | Slider state + APVTS value | normal/hover/drag/focus/disabled; кадр ручки и дуга соответствуют фактическому значению | Skin-1 rotary path подключён; проверить девять назначений и hit areas в host |
| FX CHAIN | семь APVTS ButtonAttachments | семь утверждённых основных bypass switches; cyan LED только при ON; disabled не светится; клик открывает соответствующий FX EDIT | source binding существует; семь основных switch IDs намеренно не включают FLANGER |
| FX EDIT | выбранная группа + восемь APVTS enabled-параметров | реальный selector, POWER, ACTIVE/BYPASSED, LED, параметрические контролы и реальный output meter | реализовано в исходнике; проверить все восемь групп и смену группы при открытом окне |
| MIDI keyboard | processor.keyboardState | note-on подсвечивает конкретную клавишу, note-off снимает подсветку; mouse hover отдельно различим | JUCE MidiKeyboardComponent связан с processor.keyboardState; host-проверка обязательна |
| Performance display | реальные held notes, scale root/mode и chord detection | LIVE HARMONY, NOTES HELD, SCALE/KEY и MIDI LED без фиктивных данных | source polling подключён; проверить MIDI note-on/off и chord transitions |
| Output meters | реальные processor output peaks | L/R сегменты показывают сигнал и release/decay; amber/red только на верхних уровнях/предупреждении | source polling подключён; проверить реальный звук и отсутствие ложного движения в тишине |
| PATTERN / Song Section | существующие pattern/section routing methods | 8 слотов в сетке 2×4, выбранный слот подсвечен, PREVIEW/APPLY/CANCEL; пустой слот не изображается как записанный riff | реализовано; проверить каждую кнопку и сохранение/отмену |
| AUTOCHORDS | APVTS `singleMidiNoteAsChordRoot` + scale parameters | ON/OFF text+LED, выбранные key/mode/pattern, chord diagram; изменение обновляется без ложного blinking | source bindings/LED существуют; проверить только PATTERN behavior и host automation |
| Import Guitar | processor SFZ loader/path/status | STANDBY/LOADING/READY/ERROR; сохранённый путь проверяется на существование; кнопка запускает существующий async loader | source integration существует; проверить success/failure/cancel и missing sample paths |
| Skin Gallery | 16-entry registry + selection transaction | search, favorites, preview, apply, cancel, ACTIVE/AVAILABLE labels; ровно 16 тем | existing UI; нужна проверка каждой транзакции и runtime assets |
| Workspace Settings | panel scale/gap callbacks + persisted settings | sliders показывают реальные значения; reset/gallery actions работают; изменение влияет только на workspace | existing callbacks; проверить persistence после перезапуска |
| About | реализованный info dialog | доступная кнопка открывает существующее окно; нет ложного disabled state | включено; проверить открытие/закрытие |
| Auto Discover / Curator | backend availability | до готового backend элементы явно disabled и не имитируют активность | намеренно disabled; это корректное состояние, а не недоделанный визуальный ON |
| Все окна/рамки | shared frame atlas + workspace sizing | общий язык рамок/заголовков, корректные clipping/hit areas на минимальном/максимальном размере | 9-slice подключён; нужны screenshot review на разных размерах/DPI |

### Эталон и границы

- Главный экран: только `01 INTERFACE  NEON STAGE DEFAULT .png`; вспомогательные 02–07 используются только для соответствующих вспомогательных экранов/деталей.
- Session Guitarist – Electric Sunburst Deluxe/Vintage допустим как UX-reference для читаемости, навигации, ощущения аппаратных контролов, preview и performance workflow. Запрещено копировать UI-композицию, бренд, графику, тексты, presets, riffs, samples или записи.
- Внешний стиль: premium studio hardware, matte graphite/anodized metal, точные фаски/рамки, cyan `#00D9FF`, electric blue `#6B8CFF`; amber/red только для warning/error. Без purple/pink. Дизайн остаётся дорогим и реалистичным, не игровым HUD.
- Любая подсветка должна отражать фактическое состояние; не использовать fake progress, decorative blinking или фиктивную performance telemetry.

### Техническая приёмка

Изменение linear-slider renderer опубликовано в commit `f1a5fdce15683e522c593cb8ce148b71b35d2732`. Документация этого контракта добавляется отдельным commit. Для нового HEAD необходимы Windows x64 configure/build VST3, C++ contract tests, полный CTest, 16-skin validator, runtime package staging и pluginval strictness 5. Затем обязательны ручные проверки в FL Studio 20: все 9 ручек, 7 FX switches, 8 FX EDIT groups, MIDI key-down/up, все auxiliary panels, min/max window sizes и DPI. До exact-SHA CI и host acceptance визуальный этап не объявлять завершённым.

### 17. AUTO SOUND HUNTER / CURATOR
- **Текущее состояние:** обе функции остаются disabled, пока не существует рабочего backend и достоверного источника результатов.
- **Визуально:** disabled state должен быть явно читаемым (приглушённый контраст, нет cyan glow, курсор/tooltip объясняет недоступность); никаких фальшивых сканирований, процентов, найденных звуков или карточек.
- **Когда backend появится:** состояния IDLE → SCANNING → RESULTS/EMPTY → ERROR должны быть привязаны к реальному процессу; отмена должна останавливать задачу; список результатов должен отражать реально найденные/проиндексированные данные.
- **Приёмка:** до backend проверяется только корректное disabled поведение; после backend — все переходы и cancel/error paths.

### 18. Общий контракт всех кнопок, переключателей и rotary controls
- Каждая интерактивная область должна иметь соответствующий cursor, tooltip при необходимости, keyboard focus и доступное имя/подпись.
- Hover, pressed, toggled/active, selected, focused и disabled — независимые состояния. Hover не должен стирать active, а active не должен выглядеть как зажатая мышью кнопка.
- Toggle state меняется только после успешного изменения реальной функции/параметра. LED и текстовый статус читают один источник состояния.
- Rotary: значение, дуга, кадр atlas, tooltip и host automation должны быть синхронны. Нельзя анимировать значение независимо от APVTS.
- Для недоступного backend — disabled с ясным объяснением; не подменять заглушку фальшивой работой.

### 19. Общий контракт окон и навигации
- Каждое auxiliary окно получает единый title bar, frame atlas, close, maximize/restore и resize affordance; рамка не перекрывает интерактивные дочерние компоненты.
- Перемещение окна за заголовок, resize за угол, maximize/restore, закрытие, повторное открытие и сохранение геометрии должны быть доступны и визуально понятны.
- Окна не должны дублироваться при повторном выборе уже открытого модуля; активная группа обновляется в существующем окне.
- При изменении DPI/масштаба заголовок, hit areas, labels и controls остаются читаемыми и не перекрываются.

### 20. Единый контракт палитры, материалов и подсветки
- Корпус/панели: graphite, matte black, anodized metal; материал и текстура не должны ухудшать контраст текста.
- Основные активные акценты: cyan `#00D9FF`; вторичный electric blue `#6B8CFF`. Amber/red зарезервированы для warning/error. Purple/pink запрещены.
- Свечение должно быть локальным и умеренным: вокруг активного LED/кнопки/выбранного режима, а не заливать весь модуль.
- Любой визуальный индикатор имеет документированный источник состояния; если источника нет, индикатор выключен/disabled.
- Микроанимация допустима только для реального перехода/занятости (например, реальный async SFZ load). Не добавлять бесконечное мигание, fake waveform, fake meter или fake progress.

### 21. Матрица реализации и проверки по каждому модулю
Каждый модуль считается **визуально завершённым** только после четырёх независимых проверок:
1. **Artwork/layout:** материалы, рамки, отступы, типографика, контраст и pixel comparison с утверждённым макетом/вспомогательным reference.
2. **Interaction:** каждый control реально нажимается/перетаскивается/выбирается, имеет правильный hit area, focus, hover, pressed и disabled state.
3. **State binding:** LED, подпись, дисплей, значение и визуальная подсветка синхронизированы с фактическим APVTS/processor/backend state.
4. **Runtime:** модуль проверен в Windows VST3 host на минимальном/максимальном размере, нескольких DPI и при повторном открытии; результат зафиксирован скриншотом/тестом.
  
### 22. Порядок выполнения визуального этапа
1. **Foundation:** main chassis, frame atlas, typography, palette, shared button/slider/LED states; сверка главного экрана с макетом 01.
2. **Main screen:** PRESETS, PLAYING CORE, nine rotary controls, AMP & TONE, seven FX switches, MIDI/performance/output displays.
3. **Auxiliary screens:** FX EDIT (8 групп), PATTERN, AutoChords, Import Guitar, Skin Gallery, Workspace Settings, About.
4. **Workspace/runtime:** окна, resize/maximize/restore, сохранение геометрии, clipping, keyboard navigation, DPI.
5. **Acceptance:** exact-SHA Windows build + contract tests + full CTest + 16-skin validator + runtime skin staging + pluginval strictness 5; затем ручная проверка в FL Studio 20 и запись фактических результатов.
  
### 23. Текущий статус на момент записи
- GitHub Actions для checkpoint `6ae2bab1b4ce775567fc33ad0d99c986cbbf2bdd`: Windows x64 configure, VST3 build, C++ contract tests, full CTest, 16-skin validation и runtime skin staging завершились успешно в доступных workflow runs.
- Эти workflow не выполняют pluginval strictness 5; отдельный pluginval запуск ещё требуется.
- Успешный CI не заменяет визуальную host-приёмку. Проверка в FL Studio 20, скриншотная сверка с макетом 01 и DPI/resize матрица остаются открытыми.
- Следующий рабочий проход — поэлементная проверка реальных контролов/состояний в исходниках и закрытие обнаруженных несоответствий, а не изменение утверждённой композиции. До фактической проверки соответствующие строки матрицы остаются «требует host-проверки».


## 2026-11-22 — единая тема вспомогательных окон: title bar и аппаратные controls

В `Source/UI/PPGUMultiWindowWorkspace.cpp` выполнена следующая source-level доработка:
- заголовок вспомогательного окна теперь использует typeface, font scale, weight и letter spacing текущей темы вместо постоянного системного шрифта;
- Close и Maximize/Restore получили отдельные component IDs и имена, подсказки и keyboard focus;
- при смене Skin их цвета обновляются из текущей палитры (panel/elevated, primary text, accent), поэтому уже открытые окна не остаются в старой цветовой теме;
- кнопка maximize/restore получает согласованное состояние оформления, а геометрия окна, hit areas и существующие callbacks не меняются.

Это затрагивает общую оболочку всех auxiliary modules, а не только один экран. Коммит: `aa55dc3bf50289f5e2e6267e02ec7b90f0e1246d`.

**Проверка:** изменение опубликовано в review branch; Windows CI для этого нового SHA ещё должен завершиться. Отдельно остаются host-проверка keyboard focus, hover/pressed rendering, resize/maximize/restore и DPI. Предыдущие успешные workflow относятся к предыдущему checkpoint и не являются доказательством компиляции этого нового коммита.


## 2026-11-22 — user-locked PATTERN two-window architecture (canonical)

The user explicitly approved and fixed this as the baseline. This supersedes the earlier interpretation that ARTICULATION should be a standalone button or a third subsection/tab inside the PATTERN window.

PATTERN is one of the two top-level product modes. Its workflow is organised into **two coordinated working windows**:

1. **PATTERN PRESETS** — first window:
   - choose a preset group/category;
   - show the fragments belonging to the selected group;
   - select a specific fragment;
   - preview and select the required pattern;
   - preserve the selected group, fragment and pattern when navigating between the two PATTERN windows or returning to the mode.

2. **PLAYING STYLE / ARTICULATION** — second window:
   - choose the playing style;
   - browse the articulations belonging to the selected style/source;
   - select an articulation for performance;
   - visibly show the genuinely active selection/state;
   - expose as available only articulations backed by real, verified, legally usable recordings and valid mappings. Missing/unverified mappings must remain unavailable and must never be represented by fabricated names, synthetic substitutes or false READY states.

The two windows are coordinated parts of PATTERN, not extra top-level modes. **ARTICULATION is a functional area within the second PLAYING STYLE window, not a separate button in the first PATTERN/PATTERN PRESETS window.** The first window owns group/fragment/pattern selection; the second owns playing style/articulation selection. Keep tone preset, pattern/fragment choice and performance articulation independent; changing one must not silently overwrite the others.

Both windows must follow the approved NEON STAGE visual system and the complete per-element acceptance contract: graphite materials and frames, approved cyan/electric-blue palette, real active/hover/pressed/focus/disabled states, keyboard/mouse parity, persistence and return transitions, accessible hit areas/tooltips, responsive layout/DPI, and performance-conscious animation. Session Guitarist remains a workflow/UX quality reference only; do not copy its UI, assets, branding or content.

Implementation note: an earlier source experiment added a standalone ARTICULATION button to the pattern panel. The user corrected that interpretation. That standalone button is explicitly rejected and must not be retained as the architecture. The source branch cleanup removes that button; the two coordinated windows described above are the canonical target. This decision records the approved architecture, not a claim that both windows are already implemented or host-verified.


## 2026-11-22 — PATTERN playing-style entry requested: PALM MUTE - 8TH

The user supplied the exact entry/path label: **PLAYING / PATTERN — PALM MUTE - 8TH**. Treat PALM MUTE - 8TH as a requested PATTERN playing-style/articulation entry in the second **PLAYING STYLE / ARTICULATION** window, not as a separate top-level mode or a control in the PATTERN PRESETS window.

The label is a user-approved catalog requirement, not proof that a playable recording or mapping currently exists. Show it as selectable/available only after a real, legally usable palm-muted eighth-note performance recording and its note/range/velocity/keyswitch mappings have been inspected and verified. Until then, preserve the requested entry in the catalog specification but show an honest unavailable / source mapping required state in the UI. Do not synthesize a false READY state or imply that the audio engine already plays it.


## 2026-11-22 — NEON STAGE PATTERN: первый source-level проход двухоконной навигации

### Реализовано в review branch `visual/neon-stage-playing-style-window`

- В первом окне PATTERN добавлен явный переход **OPEN PLAYING STYLE**. Он открывает отдельную рабочую область второго окна через общий `PPGUMultiWindowWorkspace`, с собственным ID, заголовком, минимальным и желаемым размером.
- Первое окно сохраняет назначение PATTERN PRESETS / song-section routing; информация о playing style больше не представлена как отдельная вкладка/кнопка ARTICULATION.
- Создано второе окно **PLAYING STYLE / ARTICULATION** с темой NEON STAGE, общей системой панелей/рамок workspace и отдельными визуальными областями PLAYING STYLE и ARTICULATION.
- Каталожная позиция **PALM MUTE - 8TH** отображается как явно недоступная. Она не активируется, пока не будет проверена реальная легальная запись и полный mapping. Никакие синтетические подмены или фиктивный READY не используются.
- Источник SFZ и сведения о switch label обновляются из processor. Наличие одного keyswitch label не трактуется как доказательство существующей playable zone; статус позиции остаётся unavailable до появления проверяемого source-map registry.
- Добавлена точка входа редактора `openPlayingStylePanel()`; окно не создаётся повторно при повторном открытии, если уже существует в workspace.

### Границы текущего результата

Это первый вертикальный source-level проход навигации и визуального каркаса второго окна, а не завершение всей PATTERN архитектуры и не закрытие общего NEON STAGE visual acceptance. В первом окне ещё предстоит полноценная реализация групп пресетов/фрагментов и сохранение выбора между переходами; независимое persistent-state для группы/фрагмента/паттерна/артикуляции также остаётся отдельной задачей. Визуальная pixel-сверка с макетами 01–07, взаимодействие мышью/клавиатурой, смена skin на уже открытом окне, resize/DPI и runtime performance ещё не подтверждены.

### Проверки

Изменены `Source/PluginEditor.cpp` и `Source/PluginEditor.h`. Изменение опубликовано в review branch; на момент записи exact-HEAD Windows CI, CTest, skin validation, pluginval и FL Studio 20 host acceptance ещё не подтверждены. Не считать это окно CI PASS или HOST VERIFIED.


## 2026-11-22 — user correction: canonical two-mode hierarchy (MELODY / PATTERN)

This entry clarifies and takes precedence over any wording that could imply PATTERN is the only mode or that the two PATTERN workspaces are the two top-level modes. The product has exactly **two top-level modes**. Each mode has its own preset context and its own playing/performance workflow.

### MODE 1 — MELODY

1. **PRESETS** — choose a musical preset family/style and song-part context. Example requested catalog path: `POP PUNK → BLINK-182 → CHORUS`.
2. **PLAYING** — choose the lead/performance approach for that melody preset. Examples include `LEAD`, `OPEN CHORDS`, and other verified playing approaches.

### MODE 2 — PATTERN

1. **PRESETS** — choose a rhythmic/song-section preset context. Example requested catalog path: `POP PUNK → BLINK-182 → VERSE`.
2. **PLAYING / PATTERN / ARTICULATIONS** — choose the playing style, rhythmic figure/pattern and articulation used to perform the selected PATTERN preset. Examples/catalog entries include `PALM MUTE - 8TH` and other styles/figures as they are actually supported by verified source recordings and mappings.

### Interaction and state rules

- The top-level mode switch is exactly **MELODY ↔ PATTERN**.
- MELODY and PATTERN have separate PRESETS contexts. Selecting `BLINK-182 → CHORUS` in MELODY must not overwrite `BLINK-182 → VERSE` in PATTERN, and vice versa.
- MELODY's PLAYING selection is independent of its PRESETS selection.
- PATTERN's PLAYING / PATTERN / ARTICULATIONS selection is independent of its PRESETS selection.
- Switching between MELODY and PATTERN preserves each mode's last selected preset, song section, playing style, and relevant UI state. Returning to a mode restores its context.
- `ARTICULATIONS` is a functional catalog/selection area within PATTERN's second workflow. It is not a third top-level mode and not a standalone top-level tab.
- The two-window implementation detail for PATTERN remains valid: PATTERN PRESETS is the preset/section/pattern workspace; PLAYING / PATTERN / ARTICULATIONS is the coordinated performance workspace. These are two workspaces **inside PATTERN**, not the product's two top-level modes.
- Session Guitarist may inform quality of navigation, responsiveness and workflow only. NEON STAGE retains its own approved 01–07 layouts, artwork, branding, palette and control design.
- A playing style, pattern or articulation may be shown as available only when its underlying playable content and mappings are verified. Requested catalog labels such as `PALM MUTE - 8TH` remain visible as unavailable until evidence exists; do not fabricate playback or active states.

### Required visual hierarchy

The main shell must visibly communicate the two top-level modes, with each mode exposing the correct PRESETS and PLAYING workflow. Labels, active cyan/electric-blue illumination, selected-state borders, display text, focus/hover/pressed/disabled states and window navigation must make the current mode and current sub-workspace unambiguous. Mode-specific preset and playing selections must not leak across modes.

This is the canonical user-approved information architecture for further NEON STAGE visual implementation. It does not claim that the full hierarchy, persistent state model, visual parity, performance QA or host acceptance is already implemented.


## 2026-11-22 — пользователь утвердил расширенный MASTER STANDARD MELODY / PATTERN

Пользователь явно подтвердил и зафиксировал расширенную редакцию требований NEON STAGE. Эта запись является обязательным уточнением канонической архитектуры MELODY / PATTERN и дополняет предыдущую запись о двух верхнеуровневых режимах.

### Утверждённая структура

**Ровно два верхнеуровневых режима:**
- **MELODY** — собственный PRESETS workflow (музыкальное направление → стиль/исполнитель → композиция/часть) и независимый PLAYING workflow (например, LEAD, OPEN CHORDS и другие подтверждённые варианты).
- **PATTERN** — собственный PRESETS workflow (направление → стиль/исполнитель → композиция/часть/ритмический пресет) и независимый performance workflow PLAYING / PATTERN / ARTICULATIONS.

В PATTERN сохраняется координация двух рабочих окон: PATTERN PRESETS отвечает за группу/фрагмент/паттерн; PLAYING STYLE / ARTICULATION отвечает за стиль исполнения и артикуляции. Это внутренние рабочие окна PATTERN, а не дополнительные верхнеуровневые режимы.

### Обязательные правила независимого состояния

- Контексты PRESETS у MELODY и PATTERN независимы и не перезаписывают друг друга.
- PLAYING не изменяет выбранный PRESETS.
- PATTERN pattern/articulation не изменяют выбранную группу/фрагмент PRESETS.
- Переключение MELODY ↔ PATTERN сохраняет последний контекст каждого режима и восстанавливает его при возвращении.
- Изменение одного параметра не должно молча сбрасывать или изменять другой параметр.
- Состояния выбора и геометрия рабочих окон должны сохраняться в рамках поддерживаемой модели состояния проекта.

### Достоверность доступности

Playing styles, patterns и articulations разрешено показывать как доступные только при подтверждённых playable recordings, корректных диапазонах нот, velocity layers (если применимо), полных MIDI/SFZ mappings и правах на использование/распространение. Непроверенные позиции остаются явно недоступными с объяснением причины. Запрещены фиктивные READY/ACTIVE состояния, вымышленные mappings и незаявленная синтетическая подмена.

### Визуальный и интерактивный контракт

- Активный верхнеуровневый режим должен быть мгновенно различим по реальному selected/active state и утверждённой cyan/electric-blue подсветке.
- Для каждого интерактивного элемента независимы NORMAL, HOVER, PRESSED, ACTIVE, SELECTED, FOCUSED, DISABLED, LOADING и ERROR там, где состояние применимо.
- Подсветка, LED, подписи и дисплеи обязаны отражать фактическое состояние функции; декоративная имитация состояния запрещена.
- Сохраняются утверждённые макеты 01–07, палитра, оригинальная идентичность NEON STAGE и правила использования Session Guitarist только как UX/workflow ориентира.
- Навигация должна быть понятна мышью и клавиатурой; окна должны поддерживать корректное открытие/закрытие, повторное открытие, resize, maximize/restore, DPI и восстановление контекста.
- Анимации допустимы только как производительная визуализация реального состояния/перехода; не создавать fake progress, meters или waveform.

### Критерии завершения и доказательства

Архитектура не считается реализованной только по факту документации или статического макета. Для каждого модуля отдельно подтверждаются: (1) artwork/layout относительно утверждённых макетов; (2) реальные interaction states и hit areas; (3) binding визуального состояния к реальным параметрам/processor/backend; (4) runtime-проверка Windows VST3, размеров окна, DPI и повторного открытия с фиксируемыми результатами.

Приёмка включает независимость и восстановление контекстов MELODY/PATTERN, независимость PRESETS/PLAYING, корректность навигации, подсветки и disabled/unavailable состояний, а затем точный Windows x64 build, contract tests, CTest, skin validation/staging, pluginval strictness 5 и отдельную ручную host-проверку в FL Studio 20.

**Порядок работ остаётся неизменным: сначала полная визуальная оболочка NEON STAGE и её проверка; аудиодвижок, DSP и интеграция сэмплов не входят в этот этап и не должны начинаться до завершения визуального этапа.**

**Статус записи:** пользовательское утверждение требований зафиксировано. Это фиксация спецификации, а не заявление о завершённой реализации или успешной приёмке.


## 2026-11-22 — пользователь утвердил окончательную структуру PATTERN: два рабочих раздела

Пользователь явно подтвердил и зафиксировал следующую структуру PATTERN. Она уточняет ранее утверждённую двухоконную архитектуру и становится обязательной информационной базой для дальнейшей визуальной реализации.

```text
PATTERN
│
├── 01 PRESETS
│   ├── GENRE
│   ├── STYLE
│   ├── ARTIST / SOUND
│   └── SECTION
│
└── 02 PLAYING / PATTERN / ARTICULATIONS
    ├── PLAYING
    ├── PATTERN
    └── ARTICULATIONS
```

### Назначение разделов

**01 PRESETS — что выбрать / какой музыкальный материал использовать**
- GENRE — жанровая категория.
- STYLE — музыкальное направление или характер звучания.
- ARTIST / SOUND — оригинальная стилистическая подборка/звуковая направленность; не копировать защищённые записи, риффы, пресеты, брендинг или оформление исполнителей.
- SECTION — композиционная часть: INTRO, VERSE, PRE-CHORUS, CHORUS, BRIDGE, OUTRO и другие фактически поддерживаемые разделы.

**02 PLAYING / PATTERN / ARTICULATIONS — как исполнять выбранный материал**
- PLAYING — характер и техника исполнения.
- PATTERN — конкретный ритмический рисунок и его параметры.
- ARTICULATIONS — артикуляции и способы звукоизвлечения.

### Архитектурные правила

- В продукте остаются ровно два верхнеуровневых режима: MELODY и PATTERN.
- У PATTERN ровно два основных рабочих раздела: **01 PRESETS** и **02 PLAYING / PATTERN / ARTICULATIONS**.
- GENRE, STYLE, ARTIST / SOUND и SECTION являются подразделами каталога PRESETS.
- PLAYING, PATTERN и ARTICULATIONS являются функциональными областями второго рабочего раздела, а не дополнительными верхнеуровневыми режимами.
- Сохраняется ранее утверждённая координация двух рабочих окон PATTERN: окно PRESETS отвечает за выбор каталога/раздела материала; второе рабочее окно — за PLAYING, PATTERN и ARTICULATIONS. Оба окна принадлежат режиму PATTERN.
- Выбор в PRESETS не должен молча перезаписывать настройки исполнения; изменения PLAYING, PATTERN или ARTICULATIONS не должны изменять выбранный PRESETS.
- Состояния выбора должны сохраняться при переходах между окнами и режимами MELODY ↔ PATTERN.
- Доступность PATTERN/ARTICULATIONS определяется только реально проверенными записями, законностью использования и корректными playable mappings. Непроверенные позиции остаются unavailable; фиктивные READY/ACTIVE состояния запрещены.
- Визуальная реализация следует утверждённым макетам NEON STAGE 01–07, палитре и правилам реальных интерактивных состояний. Session Guitarist остаётся только UX/workflow ориентиром.

**Статус:** структура утверждена пользователем и зафиксирована как обязательная база. Эта запись фиксирует архитектуру и требования, но сама по себе не означает, что все перечисленные каталоги, состояния и взаимодействия уже реализованы или прошли runtime/host-приёмку. Аудиодвижок и сэмплы остаются вне текущего визуального этапа.


## 2026-11-22 — NEON STAGE visual UX reference: SESSION GUITARIST – ELECTRIC SUNBURST DELUXE

Пользователь подтвердил **SESSION GUITARIST – ELECTRIC SUNBURST DELUXE** как основной ориентир качества UX/workflow для дальнейшей визуальной реализации NEON STAGE. Это уточнение не заменяет и не отменяет утверждённые макеты NEON STAGE 01–07, дополнительные assets/Sprite/SpriteSheets, палитру, оригинальную композицию и ранее утверждённую архитектуру MELODY/PATTERN.

### Что перенимаем как UX-принципы

1. **Song / Preset Browser:** быстрый поиск, понятная группировка музыкального материала, быстрый выбор song/preset-контекста, видимое текущее значение и быстрый возврат в каталог.
2. **Pattern Browser:** быстрый поиск ритмических рисунков по атрибутам (жанр, стиль исполнения, размер/ритмическая сетка и другие реально поддерживаемые метаданные); понятное разделение каталога и выбранного рисунка; карточки/слоты с однозначным selected state.
3. **Song Sections / Pattern Slots:** удобная организация материала по INTRO, VERSE, PRE-CHORUS, CHORUS, BRIDGE, OUTRO; быстрый просмотр и смена рисунка в контексте выбранной части; Preview до Apply и явный Cancel.
4. **Разделение свободной мелодической игры и pattern-based workflow:** MELODY и PATTERN остаются двумя верхнеуровневыми режимами NEON STAGE с независимым состоянием. У PATTERN остаётся утверждённая структура:
   - 01 PRESETS: GENRE → STYLE → ARTIST / SOUND → SECTION.
   - 02 PLAYING / PATTERN / ARTICULATIONS: PLAYING, PATTERN, ARTICULATIONS.
5. **Performance controls:** крупные, быстро читаемые органы управления; мгновенная обратная связь; понятные значения и диапазоны; плавные переходы; точная реакция на MIDI и изменение параметров.
6. **Guitar / Playback settings:** логично сгруппированные параметры исполнения и воспроизведения, включая timing, swing/humanize, latch/sync и tempo ratio — только если соответствующие функции реально реализованы и привязаны к processor/APVTS.
7. **Effects workflow:** ясная цепочка эффектов, быстрый переход к подробной настройке выбранного эффекта, отчётливые ON/OFF состояния и реальные LED-индикаторы.
8. **Info / Mapping feedback:** контекстная информация о выбранном паттерне, его диапазоне/назначении и доступных mappings. Не показывать несуществующие mappings или ложную доступность.
9. **MIDI / preview workflow:** мгновенная и достоверная реакция на ноты, клавиши, preview и transport; отсутствие фиктивных индикаторов активности.

### Что НЕ копируем

- Не копировать графический интерфейс, расположение экранов, artwork, иконки, названия, брендинг, типографику, цветовую схему, визуальные ассеты или proprietary content Native Instruments.
- Не копировать паттерны, риффы, MIDI, аудиозаписи, пресеты, mappings или sample content Session Guitarist.
- Не менять утверждённую NEON STAGE композицию и макеты 01–07 ради визуального сходства с референсом.
- Session Guitarist — только ориентир удобства, логики навигации, скорости работы и полноты feedback. Визуальная идентичность NEON STAGE остаётся оригинальной.

### Приоритет визуального этапа

Работать по утверждённым макетам 01–07 и дополнительным ресурсам проекта. Для каждого элемента довести до завершённого состояния:
- точную геометрию, пропорции, материалы, рамки, фаски, тени и световые слои;
- реалистичные ручки, кнопки, реле/переключатели, дисплеи, LED и индикаторы;
- реальные NORMAL / HOVER / PRESSED / ACTIVE / SELECTED / FOCUSED / DISABLED / LOADING / ERROR состояния там, где они применимы;
- динамическую cyan/electric-blue подсветку, привязанную к фактическому состоянию;
- mouse/keyboard interaction parity, tooltips, hit areas и доступную навигацию;
- корректную работу при resize, повторном открытии окон и DPI scaling;
- экономные анимации без лишней перерисовки и без фиктивной активности.

### Порядок и критерии завершения

Визуальный этап остаётся первым и обязательным. Не переходить к аудиодвижку, DSP, сэмплам или новым аудиофункциям до завершения визуальной оболочки и её проверок.

Для каждого из 14 модулей отдельно нужны доказательства artwork/layout, interaction, state binding и Windows VST3 runtime. Финальное визуальное завершение требует сверки с исходными макетами/ресурсами, прохождения релевантных automated checks, проверки размеров/DPI/окон и ручной приёмки в FL Studio 20. Документация или статический макет не считаются завершённой реализацией.

**Статус:** пользователь утвердил SESSION GUITARIST – ELECTRIC SUNBURST DELUXE как UX/workflow reference. Эта запись фиксирует применяемые принципы и ограничения; она не заявляет о завершении визуальной реализации или runtime QA.


## 2026-11-22 — ПОДТВЕРЖДЕНИЕ ПОЛЬЗОВАТЕЛЯ: ПРОСТАЯ ОРГАНИЗАЦИЯ NEON STAGE

Пользователь подтвердил визуальную базу повторно. Дополнительное обязательное условие: интерфейс должен быть легко организован и понятен, несмотря на богатую коммерческую графику.

- Сохранять утверждённую композицию макетов NEON STAGE 01–07 и связанные assets/Sprite/SpriteSheets.
- Верхний уровень: только MELODY и PATTERN.
- В PATTERN: 01 PRESETS (GENRE, STYLE, ARTIST / SOUND, SECTION) и 02 PLAYING / PATTERN / ARTICULATIONS (PLAYING, PATTERN, ARTICULATIONS).
- Не вводить лишние уровни каталога, дублирующие вкладки или ненужные промежуточные окна.
- Всегда показывать понятный текущий раздел, выбранный preset и фактические состояния функций.
- Переключение режимов и окон сохраняет независимый контекст и параметры; PLAYING не меняет PRESETS.
- Основные действия должны быть доступны очевидно и с минимальным количеством переходов; названия и назначение контролов читаемы, значения параметров доступны сразу.
- Preview / Apply / Cancel должны иметь ясную и последовательную семантику.
- Session Guitarist – Electric Sunburst Deluxe используется только как UX/workflow reference: удобство навигации, preview, организации библиотек, управления исполнением и обратной связи. Не копировать его графику, брендинг, компоновку или защищённый контент.
- Все состояния, подсветка, LED, дисплеи и анимации отображают реальные данные. Никакой декоративной имитации активности.

**Статус:** требование утверждено как часть визуального контракта. Это фиксация требований, а не заявление о завершённой реализации или runtime-приёмке.


## 2026-11-22 — NEON STAGE: визуальная иерархия второго окна PATTERN

В `PPGUPlayingStylePanel` добавлена трёхколоночная рабочая композиция с отдельными карточками:
- `01 / PLAYING` — отдельная функциональная область исполнения;
- `02 / PATTERN` — отдельная область ритмического рисунка; пока без подтверждённого каталога отображается честный статус `NO VERIFIED PATTERN DATA`;
- `03 / ARTICULATIONS` — статус доступности артикуляций, активного исполнения и текущего источника.

Карточки получили общую глубину, тонкую металлическую рамку и верхнюю cyan/electric-blue маркировку; центральная область визуально выделена как рабочий фокус. Существующая палитра и архитектура двух окон PATTERN сохранены. Не добавлялись фиктивные selectable элементы, playable patterns или articulation mappings.

**Статус проверки:** изменение записано в код и ожидает CI. Визуальная pixel-parity сверка, Windows VST3 runtime, DPI/resize и ручная проверка в FL Studio 20 ещё не подтверждены. Это ограниченное улучшение иерархии, не завершение визуального этапа.

## 2026-11-22 — NEON STAGE: премиальная отделка карточек PERFORMANCE WORKSPACE

В PPGUPlayingStylePanel::paint() улучшена материальная отделка трёх рабочих карточек:
- вертикальный графитовый градиент между panel_elevated и panel;
- тонкая верхняя грань и внутренняя затемнённая рамка для металлической глубины;
- отдельная акцентная кромка центральной карточки electric-blue и cyan для боковых карточек;
- свечение ограничено контуром карточки и не имитирует состояние функции.

Изменение не затрагивает DSP, параметры, sample playback или неподтверждённые mappings. Используются существующие theme tokens, поэтому отделка остаётся совместимой с темизацией.

**Статус проверки:** исходник обновлён в PR #17. Компиляция и Windows VST3 runtime для нового коммита ожидают CI; визуальная проверка в FL Studio 20, DPI и resize не выполнены. Предыдущие CI-запуски на SHA 4e4af10 не являются проверкой нового коммита.

## 2026-11-22 — NEON STAGE: отделка селекторов и обратная связь взаимодействия

В PPGUPremiumLookAndFeel::drawComboBox() обновлена отрисовка выпадающих селекторов:
- вертикальный градиент поверхности с отдельной реакцией на нажатие и disabled;
- тонкая верхняя фаска и внутренняя затемнённая кромка;
- усиленная cyan/electric-blue подсветка стрелки при keyboard focus или нажатии;
- hover/focus/pressed остаются привязаны к реальным состояниям JUCE, значение выбора и APVTS не подменяются графикой.

Изменение относится к визуальному слою и не меняет DSP или аудиопоток. Применяется единообразно ко всем ComboBox, использующим PPGUPremiumLookAndFeel.

**Статус проверки:** код записан в PR #17. Требуются CI для нового SHA, визуальная проверка на всех размерах окна и DPI, а также ручная приёмка в FL Studio 20. Динамические состояния пока не объявляются runtime-проверенными.

## 2026-11-22 — NEON STAGE fallback palette parity

Исправлены значения резервной палитры PPGUThemeManager::Palette::Tokens в Source/UI/ThemeManager.h: danger теперь #FF665E, warning — #FFB454. До исправления fallback palette расходилась с каноническим SKIN/Skin_053/theme.json и использовала розово-красный оттенок для danger. Это затрагивало состояние сброса темы/резервной палитры, а не загруженные корректные JSON-темы.

Изменение сохраняет утверждённый cyan/graphite визуальный язык и приводит fallback к значениям канонического SKIN-1. Аудиодвижок, DSP, MIDI, APVTS и bindings не затронуты.

**Проверка:** исходный diff и соответствующие HEX-значения сверены с SKIN/Skin_053/theme.json. Коммит исходника: 2aa3ecd29e5b96a7e86511999716ebf2250f44d0. Компиляция и Windows CI для этого SHA ещё не подтверждены; runtime/FL Studio 20 визуальная приёмка не выполнялась.

## 2026-11-22 — SKIN-1 artwork palette cleanup

В трёх канонических SVG-ресурсах SKIN-1 убраны пурпурные акценты D46BFF: texture.svg, bezel.svg и crest.svg. Они приведены к утверждённому electric-blue #6B8CFF. В sprite-sheet manifest значение glow_blue #0048FF также приведено к #6B8CFF, чтобы спецификация атласов не противоречила канонической теме.

Вместе с предыдущей правкой fallback danger/warning это устраняет обнаруженные расхождения между частью artwork/manifest/fallback и утверждённой палитрой NEON STAGE DEFAULT. Это точечная очистка Skin-1, а не заявление о завершении аудита всех 16 тем.

**Проверка:** все четыре исходных файла повторно получены с рабочей ветки и обновлены последовательными GitHub commits. Проверено отсутствие заменяемых прежних HEX в соответствующих исходных строках. Проверка рендеринга SVG в JUCE, компиляция Windows и runtime visual acceptance ещё не выполнены.