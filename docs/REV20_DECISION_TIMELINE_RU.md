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


## 2026-11-22 — NEON STAGE: полный паспорт визуальных элементов и критерии 100% соответствия макетам 01–07

### Приоритет эталонов и правило коммерческого качества

1. **Макет 01 — главный и абсолютный эталон** главного экрана: композиция, пропорции, расположение секций, размеры, визуальная иерархия и плотность элементов. Нельзя самовольно переставлять, упрощать, добавлять или удалять элементы.
2. **Макеты 02–07 — эталоны соответствующих дополнительных экранов и состояний.** Применять каждый макет только к его экрану/модулю; не переносить элементы между экранами по догадке.
3. **Папка assets и Sprite/SpriteSheets** — источник утверждённых графических материалов, состояний, рамок, пиктограмм, дисплеев и контролов. Использовать исходные файлы и manifest; не заменять утверждённую графику случайными градиентами или временными заглушками.
4. Session Guitarist – Electric Sunburst Deluxe/Vintage — только ориентир UX: ясность навигации, тактильность контролов, preview/performance workflow. Не копировать его композицию, графику, бренд, названия, пресеты, риффы и аудиоматериалы.
5. Коммерческое качество означает точное выравнивание, согласованные интервалы, аккуратную типографику, реалистичные материалы, читаемость при любом поддерживаемом масштабе, отсутствие обрезки/артефактов и честную индикацию реального состояния. «Дорого» не означает чрезмерное свечение: графитовый металл — основа, cyan/electric blue — контролируемые акценты.

### Паспорт главного экрана — макет 01

| Элемент | Назначение и поведение | Визуальное состояние / источник истины | Проверка приёмки |
|---|---|---|---|
| Корпус NEON STAGE | Единая оболочка плагина; задаёт границы и иерархию секций | Matte graphite/anodized metal, рамки, фаски и утверждённые artwork layers | Сверка скриншота с макетом 01 по геометрии, отступам и пропорциям |
| Заголовок/брендовая зона | Идентификация инструмента и навигационный контекст | Тема Skin-1, primary/secondary text; без постороннего брендинга | Масштаб, кернинг, baseline, отсутствие обрезки |
| PRESETS selector | Выбор текущего заводского/пользовательского пресета | Выбранное имя синхронно с preset state | Выбор, повторный выбор, длинное имя, смена категории |
| PRESETS category | Фильтрация библиотеки по категории | Реальная выбранная категория | Переключение категорий, пустой результат, сохранение текущего выбора |
| PRESETS search | Поиск по доступным названиям/метаданным | Введённый запрос и число результатов | Частичный запрос, очистка, отсутствие совпадений |
| PLAYING CORE — 9 rotary controls | Девять независимых параметров исполнения/тона; значение меняется drag/host automation | Световая дуга и tooltip вычисляются из фактического нормализованного APVTS value; кадр rotary atlas не должен расходиться со значением | Каждый из 9 контролов отдельно: min/mid/max, быстрый/медленный drag, double-click/reset если предусмотрено, automation и focus |
| PLAYING CORE — MELODY/PATTERN | Два взаимоисключающих режима исполнения | Подсветка только активного режима, синхронно с параметром/состоянием | Переключение в обе стороны, повторный выбор, смена пресета |
| MODE selector | Выбор режима playMode | Отображаемое значение синхронно с APVTS attachment | UI → APVTS и host automation → UI |
| START/SYNC mode | Определяет режим запуска/синхронизации | Значение syncMode, без декоративной анимации | Проверить каждый пункт, смену пресета и automation |
| FX CHAIN — 7 switches | Независимое включение/выключение семи эффектных модулей | Реальное toggle state; cyan LED при ON, приглушённый LED при OFF | Все 7 отдельно, все комбинации поочерёдно, сохранение состояния, host automation |
| FX labels | Подписи семи FX модулей | Контраст primary/secondary text, состояние не кодируется только цветом | Читаемость и соответствие каждому переключателю |
| FX EDIT entry | Открывает редактор выбранного эффекта | Выбранная группа и включённый POWER отражают действительный FX state | Навигация между 8 группами, повторное открытие, возврат |
| MIDI INPUT LED | Индикация удерживаемых входящих MIDI нот | Горит только пока есть реальные held notes | Note-on, note-off, несколько нот, panic/all-notes-off |
| MIDI Keyboard | Визуальное исполнение/мониторинг MIDI клавиш | Реальные key-down/key-up события; подсветка снимается при note-off | Нажатие/отпускание каждой тестовой клавиши, sustain, несколько одновременных нот |
| Performance Display | Показывает фактическую ноту/аккорд/тональность/исполнительскую информацию, которую поддерживает backend | Только данные processor/backend; неизвестные значения не подменяются фиктивными | MIDI вход, смена нот и аккордов, пустое состояние, быстрые переходы |
| Output Meters | Визуализируют фактический выходной уровень | Реальный signal level; нулевой сигнал — нулевой meter; peak/hold только при реальном измерении | Silence, тихий сигнал, пик, спад, отсутствие MIDI/audio |
| AUTOCHORDS control/LED | Включает/отключает преобразование одной MIDI ноты в аккордовый корень | Реальный APVTS singleMidiNoteAsChordRoot; текст ON/OFF совпадает с toggle | UI, MIDI behavior и automation должны совпадать |
| Import Guitar entry/status | Открывает импорт SFZ; отображает фактический статус библиотеки | STANDBY/LOADING/READY/ERROR; путь проверяется, fake progress запрещён | Пустой путь, валидный SFZ, отсутствующий файл, ошибка чтения, повторная загрузка |
| Auto Sound Hunter | Будущий поиск звуков | Disabled до существования backend | Disabled state, tooltip и отсутствие ложной активности |
| Curator | Будущая функция сортировки/кураторства | Disabled до существования backend | Disabled state, tooltip и отсутствие фальшивых результатов |
| Skin Gallery entry | Открывает выбор темы | Текущая тема помечена ACTIVE | Открытие/закрытие, повторный вход |
| Settings entry | Открывает параметры workspace | Текущее значение масштаба/интервалов | Открытие, применение, повторное открытие |
| About entry | Открывает информационное окно | Кнопка активна только при наличии реального диалога | Открытие/закрытие, клавиатурный фокус |

### Паспорт FX EDIT — 8 групп

Каждая группа имеет собственное выбранное состояние, POWER, подпись, набор доступных параметров и status/output indication. Группа должна открываться по выбору пользователя, а не по случайному hover. POWER управляет только соответствующим модулем и отображает его фактическое состояние.

| Группа | Что проверяется |
|---|---|
| FX group 1 | Выбор, POWER ON/OFF, значения параметров, повторный вход |
| FX group 2 | То же; значения не должны наследоваться от другой группы |
| FX group 3 | То же; выбранная группа явно обозначена |
| FX group 4 | То же; disabled/недоступные параметры визуально различимы |
| FX group 5 | То же; значения и подписи читаемы на 1x/2x/3x |
| FX group 6 | То же; переключение не меняет соседний FX state |
| FX group 7 | То же; meter/status только при наличии реальных данных |
| FX group 8 | То же; выбранная группа синхронна с FX CHAIN entry |

Общие элементы FX EDIT:
- **Effect selector:** выбор одной из восьми групп; отображает действительное имя выбранного эффекта.
- **POWER:** отдельный toggle выбранного эффекта; LED и подпись следуют processor/APVTS.
- **Parameter controls:** каждая ручка/ползунок имеет подпись, единицы, реальное значение, границы, tooltip и host automation mapping.
- **Status/output meter:** обновляется из реального состояния/сигнала; при отсутствии данных показывает idle, а не fake activity.
- **Graph/display:** отображает реальную характеристику только если её вычисляет DSP; иначе не имитирует спектр/кривую.
- **Navigation:** смена группы не создаёт дубликат окна и не сбрасывает несвязанные параметры.

### Паспорт вспомогательных экранов — макеты 02–07

| Экран | Элементы управления | Обязательное поведение |
|---|---|---|
| PRESETS | Search, category filter, preset list/selector, selected state | Поиск/фильтр не ломают выбор; выбранный preset загружается; пустой результат корректно обозначен |
| PATTERN / Pattern Section Routing | 8 слотов (2×4), выбор секции/паттерна/источника/тона, PREVIEW, APPLY, CANCEL, переход к AutoChords | PREVIEW не фиксирует изменения; APPLY подтверждает; CANCEL возвращает исходное состояние; выбранный слот синхронен с patternBox |
| AUTOCHORDS | ON/OFF, Key, Mode, Pattern, chord diagram/state | Toggle связан с APVTS; key/mode/pattern отражают действительные значения; диаграмма обновляется только от реального chord state |
| Import Guitar | Load/Import, путь/имя файла, статус STANDBY/LOADING/READY/ERROR | Реальный async load, обработка ошибки/отмены/несуществующего пути; нет фальшивого процента загрузки |
| Skin Gallery | Search, family filter, count, theme cards, Favorite, Preview, Apply, Cancel, keyboard navigation | Preview временный; Apply фиксирует; Cancel откатывает; ровно 16 зарегистрированных тем; ACTIVE/AVAILABLE корректны |
| Workspace Settings | Scale slider, gap slider, Restore defaults, Open Skin Gallery | Ползунки показывают реальные значения; изменения применяются к workspace; reset действительно возвращает defaults; значения сохраняются/восстанавливаются согласно контракту |
| About | Информация о продукте/версии/лицензиях и доступных сведениях | Диалог открывается, закрывается, читаем и не содержит выдуманных технических заявлений |

### Паспорт всех интерактивных состояний

Каждый Button/Toggle/ComboBox/Slider/Rotary/Window control проверяется отдельно по следующим состояниям:
- **Normal:** нейтральный вид, без свечения активного действия.
- **Hover:** локальное наведение; не стирает выбранное/включённое состояние.
- **Pressed:** визуальная реакция только пока удерживается кнопка/мышь.
- **Active/Toggled:** постоянное состояние включённой функции.
- **Selected:** текущий выбранный пункт/режим/карточка.
- **Focused:** заметная cyan focus ring при keyboard navigation.
- **Disabled:** приглушённый текст/контрол, нет активного свечения, понятная причина через tooltip/status.
- **Loading:** только при настоящей асинхронной операции.
- **Error/Warning:** amber/red только для фактической ошибки/предупреждения.

Для rotary controls дополнительно: drag direction, fine adjustment, double-click behavior если реализован, normalized value, display value, arc angle, sprite frame, tooltip, APVTS value и host automation должны быть согласованы. Для sliders: track/fill/thumb, drag/focus/disabled, min/max и единицы измерения согласованы с параметром.

### Паспорт окон и оболочки

- **Title bar:** имя экрана, theme typography, читаемый контраст, корректное сокращение длинного названия.
- **Close:** закрывает только текущее окно; имеет tooltip, component ID/name и keyboard focus.
- **Maximize/Restore:** две различимые пиктограммы/состояния; сохраняет исходную геометрию для Restore.
- **Resize grip:** видимая зона изменения размера не перекрывает дочерние элементы; минимальный размер не обрезает критичные controls.
- **Drag header:** перемещение окна работает за заголовок, не перехватывает нажатия по кнопкам.
- **Focus:** активное окно и keyboard focus визуально различимы.
- **Persistence:** геометрия восстанавливается корректно и ограничивается видимой областью экрана.
- **DPI/scale:** текст, hit areas, рамки, sprite sheets и controls не размываются/не обрезаются при поддерживаемых масштабах.
- **Theme propagation:** смена темы обновляет уже открытые окна, не только вновь созданные.

### Матрица 100% приёмки по каждому элементу

Ни один элемент не получает отметку COMPLETE только за наличие исходного кода. Для каждого ID в тест-реестре фиксируются четыре результата:
1. **Artwork/layout:** скриншот и сверка с соответствующим макетом 01–07 или утверждённым asset/sprite.
2. **Interaction:** hit area, hover, pressed, drag, focus, keyboard, disabled и повторные действия.
3. **State binding:** источник истины (APVTS/processor/backend), двусторонняя синхронизация и отсутствие fake state.
4. **Runtime:** exact-SHA Windows x64 VST3, FL Studio 20, min/max size, 1x/2x/3x, повторное открытие и скриншоты.

Статусы в журнале: **SOURCE IMPLEMENTED** (код найден), **CI PASS** (автоматические проверки на точном SHA прошли), **HOST VERIFIED** (ручная проверка в FL Studio 20 с доказательствами), **BLOCKED** (нет backend/ресурса/host), **NOT STARTED**. Эти статусы не взаимозаменяемы.

### Порядок закрытия оставшихся работ

1. Зафиксировать визуальное соответствие главной оболочки макету 01, не меняя геометрию.
2. Проверить девять rotary controls по отдельности и два режима PLAYING CORE.
3. Проверить семь FX switches и LED по отдельности и вместе.
4. Пройти все восемь групп FX EDIT.
5. Проверить MIDI key-down/key-up, Performance Display и Output Meters.
6. Пройти PRESETS и PATTERN включая Preview/Apply/Cancel.
7. Проверить AUTOCHORDS и полный цикл Import Guitar.
8. Пройти все 16 тем Skin Gallery: Preview → Apply → Cancel, поиск, фильтр, избранное и возврат к Skin-1.
9. Проверить Settings и About.
10. Пройти все вспомогательные окна: drag, resize, maximize/restore, close/reopen, focus, clipping, DPI и производительность.
11. Для каждого найденного дефекта открыть отдельную проверяемую задачу/PR, выполнить exact-SHA CI и обновить журнал фактическим результатом.

### Подтверждённый CI checkpoint 2026-11-22

GitHub Actions run **45015637797 / run #407**, commit `30aa6cda6a205fb3338112a5eda959e5b2d94bfa`, завершился **success**. Успешны: Windows x64 configure, VST3 + C++ contract build, full CTest, validation ровно 16 тем и artwork assets, staging 16 skin folders, pluginval strictness 5, upload VST3 + skin pack. Артефакт workflow: `PPGU-REV20-Windows-x64-VST3` (artifact ID `14751807040`, размер 11,250,391 bytes). Это подтверждает автоматический build/package checkpoint именно для указанного SHA. Это **не** доказывает 100% pixel parity с макетами и не заменяет ручную проверку в FL Studio 20, DPI и реальном визуальном поведении. Host acceptance остаётся открытой до предоставления/получения скриншотов и результатов тестирования.

## 2026-11-22 — Проверка эталонных файлов и безопасная оценка PR #12

### Подтверждённый состав эталонов на main

Проверено дерево репозитория main (805 записей, Git tree не усечён). В корне присутствуют все семь утверждённых макетов:

- 01 INTERFACE  NEON STAGE DEFAULT .png
- 02 INTERFACE  NEON STAGE DEFAULT AUTOCHORDS .png
- 03 INTERFACE  NEON STAGE DEFAULT .png
- 04 INTERFACE  NEON STAGE DEFAULT .png
- 05 INTERFACE  NEON STAGE DEFAULT .png
- 06 INTERFACE  NEON STAGE DEFAULT .png
- 07 INTERFACE  NEON STAGE DEFAULT .png

Также подтверждены рабочие ресурсы Skin_053: asset_manifest.json, controls/control_states_manifest.json, neon_stage_spritesheet_manifest.json, controls atlas, frames/panels sheet, icons sheet, meters/sliders sheet и rotary 61-frame atlas. Эталонные файлы не перемещать, не переименовывать и не перегенерировать в рамках косметических исправлений.

### Результат проверки PR #12

PR #12 NEON STAGE DEFAULT — visual asset and performance QA baseline не переносить и не сливать целиком: сравнение его ветки с текущим main показывает divergence, 14 commits ahead и 73 commits behind. Его старый набор файлов нельзя принимать поверх актуальной реализации без выборочного переноса и повторной адаптации.

Обнаружены конкретные причины повторного аудита перед любым переносом:
- старые контрактные тесты фиксируют восемь кадров rotary atlas, тогда как текущий main уже содержит отдельный 61-frame rotary atlas;
- в старой ветке изменена палитра accent blue на #0048FF, тогда как утверждённый Skin-1 контракт использует electric blue #6B8CFF;
- asset audit в PR #12 изначально описан как report-only и не является строгим release gate;
- PR #12 не подтверждает ручную работу в FL Studio 20, визуальное совпадение с макетами или реальные performance measurements.

Решение: сохранить PR #12 как источник QA-идей, но не сливать его ветку. QA следует адаптировать непосредственно к текущему main и актуальным manifest/atlas, не откатывая визуальные изменения и не меняя палитру.

### Текущие границы подтверждения

- ASSET INVENTORY VERIFIED: семь файлов 01–07 и перечисленные manifest/sprite assets присутствуют в main.
- SOURCE IMPLEMENTED: в PluginEditor присутствуют APVTS-linked rotary controls, live value indicator, linear slider hover/drag/focus/disabled rendering, FX toggle LED, MIDI-held-note indication, output meter, performance display и state-driven auxiliary panels.
- CI VERIFIED: относится только к точному SHA и workflow run, указанным в checkpoint выше.
- HOST / PIXEL ACCEPTANCE: остаётся открытой до получения скриншотов/записей проверок в Windows VST3 host, FL Studio 20, DPI 1x/2x/3x и интерактивной матрицы всех 14 областей.

Следующий source-level этап: проверить и закрыть несоответствия каждого компонента относительно его макета и текущего manifest; сначала главная оболочка и rotary/button states, затем FX EDIT и остальные панели. Любое исправление должно сохранять геометрию макета 01–07 и проходить Windows CI.

## 2026-11-22 — ПОЛЬЗОВАТЕЛЬСКАЯ ФИКСАЦИЯ БАЗЫ NEON STAGE: ОБОСНОВАННЫЕ УЛУЧШЕНИЯ РАЗРЕШЕНЫ

Пользователь явно подтвердил и утвердил следующий базовый контракт. Эта запись является более поздним решением и **заменяет любые прежние формулировки, которые запрещали менять композицию или требовали неизменно сохранять геометрию макета**.

### Разрешённые улучшения
- Композиция и пропорции: размеры элементов, отступы, расположение отдельных блоков, пропорции панелей и организация рабочих областей.
- Материалы и рендеринг: реалистичность графитового металла, анодированные поверхности, фаски, отражения, глубина, объём и световые эффекты.
- Анимация: плавность поворота ручек, нажатия переключателей, переходы между окнами и реакция подсветки.
- UX и доступность: навигация, читаемость, доступность элементов, управление мышью и клавиатурой.

### Обязательные ограничения качества
- Каждая кнопка, ручка, переключатель, реле, LED и индикатор должны выполнять назначенную функцию и отражать реальное состояние системы. Декоративная имитация функциональности запрещена.
- Фирменный стиль сохраняется: графитовый металл, cyan `#00D9FF`, electric blue `#6B8CFF`. Фиолетовый и розовый не использовать в NEON STAGE.
- Производительность, стабильность, корректная работа состояний и доступность обязательны.
- Макеты 01–07 и утверждённые assets/sprites остаются первоисточником идентичности и визуального направления, но не являются запретом на улучшение композиции.
- Изменения должны иметь понятное обоснование и проверяться на читаемость, функциональность, DPI, hit areas, runtime и производительность. Не допускается ухудшение UX или регрессия функций.
- Session Guitarist и другие продукты могут служить только ориентиром удобства; их защищённые UI-композиции, графика и брендинг не копировать.

### Правило применения
При обнаружении реального улучшения интерфейса допускается изменить макет/композицию. В PR необходимо указать проблему исходного решения, причину изменения, затронутые области и критерии проверки; по возможности приложить сравнение до/после. Проверка каждого элемента по-прежнему включает artwork/layout, interaction, state binding и runtime. Наличие кода само по себе не означает завершённую приёмку.

**Статус решения: USER APPROVED / BASELINE LOCKED.** Это обязательная база для дальнейшей визуальной разработки NEON STAGE. Аудиодвижок и сэмпловая работа не входят в текущий приоритет, пока визуальная оболочка не будет завершена.

### Уточнение набора визуальных и UX-образцов — 2026-11-22

Пользователь дополнительно подтвердил, что при разработке NEON STAGE образцами/референсами являются:
- утверждённые макеты **01–07**;
- дополнительные макеты и вспомогательные визуальные материалы проекта;
- **Session Guitarist – Electric Sunburst Deluxe** как дополнительный референс продукта.

Session Guitarist учитывается не только как абстрактный пример удобства, но и как ориентир премиального уровня исполнения, организации рабочего процесса гитарного инструмента, поведения контролов, навигации, читаемости и визуальной проработки. Его можно анализировать для поиска удачных UX-решений и идей улучшения.

При этом NEON STAGE сохраняет собственную идентичность, утверждённую графитовую материальную базу и палитру. Нельзя копировать защищённые графические материалы, логотипы, тексты, фирменные элементы, конкретные пресеты/риффы/записи или воспроизводить чужой интерфейс как точную копию. Любое заимствование идеи должно быть переосмыслено и реализовано оригинально в системе NEON STAGE.

Этот набор образцов применяется совместно с правилом обоснованных улучшений композиции: макеты 01–07 и дополнительные материалы задают исходное направление, а Session Guitarist – Electric Sunburst Deluxe служит дополнительным сравнительным референсом качества и UX. Ни один референс не отменяет обязательных требований к функциональности, производительности, стабильности и фирменной палитре.

### Повторное подтверждение пользователем — визуальная база и набор референсов LOCKED (2026-11-22)

Пользователь явно подтвердил формулировку набора образцов:
1. Макеты 01–07 — основные утверждённые образцы NEON STAGE.
2. Дополнительные макеты и материалы проекта — вспомогательные визуальные ориентиры.
3. Session Guitarist – Electric Sunburst Deluxe — дополнительный референс премиального исполнения, организации гитарного интерфейса, навигации, контролов и UX.

**Статус: USER APPROVED / CONFIRMED / BASELINE LOCKED.** Набор референсов обязателен для дальнейшей визуальной разработки NEON STAGE и применяется совместно с ранее утверждённым разрешением на обоснованные улучшения композиции, материалов, анимации и UX. Сохраняются оригинальность NEON STAGE, фирменная палитра, реальная функциональность, производительность и стабильность.


## 2026-11-22 — ВИЗУАЛЬНЫЙ ПРОХОД NEON STAGE: ПРИОРИТЕТ ОБОЛОЧКИ, АНИМАЦИИ И PERFORMANCE QA

Пользователь повторно подтвердил: до закрытия визуальной приёмки запрещено переключать приоритет на аудиодвижок, DSP или расширение библиотеки сэмплов. Текущий этап — исключительно внешний вид, тема/скин, материалы, рамки, контролы, вспомогательные окна, анимация, state binding и производительность графической оболочки.

### Приоритет референсов
- Макеты 01–07 — основные образцы NEON STAGE; дополнительные макеты, assets, Sprite/SpriteSheets и manifest — обязательная исходная база визуального анализа.
- Session Guitarist – Electric Sunburst Deluxe — референс коммерческого уровня исполнения, понятности гитарного workflow, навигации и тактильности контролов. Использовать принципы UX, не копировать чужую композицию, брендинг, artwork или защищённые материалы.
- Более позднее пользовательское решение разрешает улучшать композицию/пропорции, интервалы и организацию рабочих областей, когда это даёт проверяемый выигрыш в UX/читаемости. Старый запрет на изменение геометрии макета считать отменённым.
- Фирменная палитра: graphite, cyan #00D9FF, electric blue #6B8CFF; purple/pink запрещены. Amber/red — только реальные warning/error.

### Обязательный контракт состояний и анимации
- Rotary: плавное визуальное следование непрерывному значению APVTS; sprite frame, value arc, tooltip и automation должны быть согласованы. Не добавлять фальшивое движение при неизменном значении.
- Switch/button: независимые Normal/Hover/Pressed/Active/Selected/Focused/Disabled; короткая плавная реакция допустима, но состояние LED всегда отражает реальное состояние функции.
- FX ON/OFF: яркая cyan индикация только при ON, OFF — приглушённый LED.
- MELODY/PATTERN: выбранный режим выделен и синхронизирован с реальным состоянием.
- MIDI keyboard/input: подсветка только на реальные note-on/note-off; корректно очищать удерживаемые ноты при all-notes-off.
- Performance display и meters: только реальные MIDI/audio данные, никаких fake telemetry/peak/progress.
- FX EDIT: выбранная группа, POWER и параметры синхронизированы с соответствующим эффектом.
- SFZ import: STANDBY/LOADING/READY/ERROR только по фактическому процессу/результату.
- Auxiliary windows: плавные, но лёгкие переходы; close/maximize/restore/resize/focus работают, геометрия сохраняется, окна не перекрывают рабочие контролы.

### Производительность — обязательная матрица проверки
1. Idle repaint/CPU: при отсутствии взаимодействия не должно быть постоянного тяжёлого repaint без необходимости.
2. Rotary drag: визуальная реакция непрерывная, без заметного запаздывания; изменение значения не должно запускать тяжёлую загрузку изображений.
3. MIDI activity: LED/key states обновляются без блокировки аудиопотока и без аллокаций/тяжёлой работы на audio thread.
4. Meter/display refresh: ограниченная частота обновления, без избыточного декодирования artwork.
5. Window open/close: измерять задержку первого открытия, повторного открытия и переключения между окнами.
6. Skin Gallery: сохранять lazy-loading previews; не декодировать все карточки при открытии.
7. DPI/layout: проверить 1x/2x/3x, min/max window, resize, длинные подписи и отсутствие clipping/hit-area regressions.
8. Regression: повторно запустить Windows x64 VST3 build, CTest, skin/artwork validators и pluginval; отдельно отметить, что CI не заменяет ручной FL Studio 20 host test.

### Порядок реализации и приёмки
A. Корпус/главная оболочка, материалы, 9-slice рамки, фоновые слои и палитра.
B. Девять rotary, два режима, hover/pressed/focus/disabled и непрерывная value feedback.
C. Семь FX switches и реальные LED.
D. Все восемь FX EDIT групп и параметры.
E. MIDI keyboard, Performance Display и Output Meters.
F. PRESETS и PATTERN: навигация, выбор, preview/apply/cancel.
G. AUTOCHORDS и Import Guitar status.
H. Все 16 skins: preview/apply/cancel, typography, assets и согласованность palette.
I. Settings/About и все auxiliary windows.
J. DPI, стабильность, runtime и performance acceptance.

Для каждого модуля обязательны четыре независимых результата: (1) artwork/layout review по референсу с записью обоснования layout deviations; (2) interaction; (3) state binding; (4) runtime/performance. Нельзя объявлять модуль завершённым только по наличию исходного кода. В отчёте отдельно указывать SOURCE IMPLEMENTED, CI PASS и HOST VERIFIED.

### Инвентаризация ресурсов и текущий source baseline
На main подтверждено наличие семи PNG-макетов 01–07, Skin_053 premium artwork pipeline, control state artwork, FX layers, 9-slice frame/controls/meters/icons/61-frame rotary atlases, 16-theme registry и исходников PluginEditor/ThemeManager/MultiWindowWorkspace. В PluginEditor уже присутствуют 61-frame rotary rendering с реальной value arc, linear slider state rendering, FX toggle LED, иконки из atlas, live MIDI/performance monitor и SFZ status polling; Skin Gallery использует lazy-loaded card previews. Это фиксирует исходный baseline, но само по себе не закрывает полную визуальную, host или performance приёмку.

**Статус этапа:** VISUAL-FIRST / IN PROGRESS. Аудиодвижок и сэмпловые задачи отложены до закрытия визуального acceptance matrix. Никаких заявлений о 100% визуальном совпадении, ручном FL Studio 20 тесте или измеренных performance numbers без соответствующих артефактов.


## 2026-11-22 — УТВЕРЖДЁННАЯ СТРУКТУРА ДВУХ РЕЖИМОВ PLAYING CORE

Пользователь утвердил точное назначение двух режимов. Это обязательная база навигации и визуального состояния NEON STAGE:

1. **MELODY** — рабочая цепочка/представление: **PRESETS / PLAYING / PATTERN**. В режиме MELODY доступны выбор пресета, обычное исполнение (PLAYING) и переход к PATTERN как к связанному разделу рабочего процесса. Выбранный подраздел должен быть однозначно виден, подсвечен и синхронизирован с активной панелью.
2. **PATTERN** — отдельный режим/рабочая цепочка: **PRESETS / PLAYING-PATTERN**. В нём PRESETS относится к паттерновому workflow, а PLAYING-PATTERN — к исполнению выбранного паттерна. Не подменять этот режим обычным PLAYING и не показывать элементы обычного исполнения как активные, если они не относятся к паттерновому режиму.

**Ключевое различие:** MELODY содержит три представления PRESETS, PLAYING и PATTERN; PATTERN содержит два представления PRESETS и PLAYING-PATTERN. Это не две одинаковые вкладки и не просто два визуальных скина. Переключение MELODY ↔ PATTERN обязано менять доступную навигацию/рабочее представление и отражать фактический выбранный режим.

### Поведение интерфейса и проверка
- Две основные кнопки MELODY и PATTERN имеют независимые состояния hover/pressed/focus и однозначную подсветку активного режима.
- В MELODY отображаются/доступны PRESETS, PLAYING, PATTERN; активный подраздел выделяется cyan-состоянием.
- В PATTERN отображаются/доступны PRESETS и PLAYING-PATTERN; активный подраздел выделяется cyan-состоянием.
- При переключении режима не теряются выбранный пресет, выбранный pattern slot и релевантные настройки; состояние не должно случайно переноситься между обычным PLAYING и PLAYING-PATTERN.
- Навигация клавиатурой и мышью должна приводить к тому же состоянию, что и нажатие кнопки; фокус не равен активному режиму.
- LED/индикаторы показывают реальное состояние режима и активности, а не только hover или декоративное свечение.
- Artwork/layout, interaction, state binding и runtime проверяются отдельно для обеих цепочек. В тестах обязательно проверить все переходы: MELODY→PRESETS, MELODY→PLAYING, MELODY→PATTERN, PATTERN→PRESETS, PATTERN→PLAYING-PATTERN и MELODY↔PATTERN.

Эта запись уточняет прежнюю краткую формулировку «два режима PLAYING CORE»: точная структура выше имеет приоритет при дальнейшей реализации и приёмке.
