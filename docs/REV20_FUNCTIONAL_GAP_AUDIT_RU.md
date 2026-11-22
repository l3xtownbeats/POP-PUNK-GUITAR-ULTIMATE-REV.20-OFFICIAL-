# REV.20 — ФУНКЦИОНАЛЬНЫЙ АУДИТ ENGINE / UI / PRESETS / IMPORT SOUNDS

Дата аудита: 10 ноября 2026  
База аудита: `feat/power-profiles-double-multicore`, HEAD `2c04b766aaf90b60798c5d7cc0a37c3960f9b6dd`.  
Основание: исходники `PluginProcessor.*`, `PluginEditor.*`, `SamplePool/SFZ`, CMake, preset catalog и утверждённые UI/preset/library specifications.

> Это статический аудит исходного кода и архитектуры. Он не заменяет сборку, CTest, pluginval и ручной тест в FL Studio 20. Функция считается готовой только после теста.

## Итог

| Область | Фактический статус | Вывод |
|---|---|---|
| Engine / MIDI / sampler | Частично реализовано | Есть реальный SFZ/WAV sampler и MIDI/performance code; полный гитарный production engine ещё не подтверждён |
| UI / Cover | Частично реализовано | Есть тёмно-розовый JUCE editor, но он не повторяет утверждённую композицию Cover Interface |
| Factory presets | Каталог есть, применение частичное | 300 записей читаются из JSON; текущий loader применяет только drive/tone/reverb/output и mode |
| User presets | Не реализовано в UI | Нет Save, Save As, Rename, Delete, Import/Export bank и реального user preset browser |
| Preset switching | Частично реализовано | ComboBox выбирает каталог и меняет ограниченный набор параметров; prev/next, audition и полное применение параметров отсутствуют |
| Import Sounds | Частично реализовано | Есть выбор одного SFZ и асинхронная загрузка; Folder/ZIP/WAV import, mapping editor, library browser и конвертация в библиотечный формат отсутствуют |
| Save/restore DAW state | Есть базовый APVTS state | Сохранение состояния проекта не равнозначно сохранению отдельного пользовательского preset-файла |

## 1. Engine

### Подтверждено исходниками
- VST3 instrument с MIDI input и stereo output.
- APVTS содержит параметры voices, play mode, articulation, velocity response, palm mute threshold, tuning, pan, scale/key, pattern transport, amp/tone и FX controls.
- SFZ parser / SamplePool / streaming page cache / streaming voice reader присутствуют в проекте.
- SFZ загрузка может выполняться через worker pool, вне audio callback.
- PatternScheduler и host transport clock подключены к processor.
- В PR #13 добавлены профили GOOD/NORMAL/NIGHT с voice caps 64/32/12 и preallocated DOUBLE short-delay thickener. DOUBLE — это widening/thickening, не независимый второй дубль.

### Что нельзя считать полностью готовым
- Наличие APVTS-параметра FX не доказывает, что каждый FX реализован и звучит как законченный DSP effect.
- Параметр Articulation/Palm Mute не доказывает полную выборку отдельных palm-mute sample zones во всех банках.
- Полноценные acoustic/electric/hybrid переключаемые банки не подтверждены текущим UI.
- Реальный пользовательский multicore control отсутствует. Нельзя запускать/ожидать потоки внутри audio callback.
- GOOD/NORMAL/NIGHT пока подтверждают voice caps, но не измеренную экономию CPU/энергии.
- Требуются audio regression tests: note-on/off, overlapping notes, sustain, pitch bend, velocity layers, palm mute, bank reload, underrun, clipping/phase и длинное воспроизведение.

## 2. Интерфейс и Cover Interface

### Уже есть
- Тёмный фон, magenta акцент, белые подписи.
- Header с preset/category/search, power profile, DOUBLE и Load SFZ.
- Melody/Pattern selector, amp/tone knobs, FX toggles, playback controls и MIDI keyboard.
- Hero зона нарисована векторной графикой.

### Несоответствия утверждённому Cover
- Текущая компоновка и размер editor 1040×790, а не эталонная широкая композиция 1402×1122.
- Вместо исходной hero artwork используется упрощённый векторный силуэт.
- Нет верхних Previous/Next, Save, Browser, CPU/RAM telemetry и Settings.
- Нет AutoChords, Key/Scale UI, Guitar Type Electric/Acoustic, полноценного Browser/Presets/Settings/About нижнего меню.
- Нет pitch/mod wheels.
- UI не должен показывать CPU/RAM числа, пока не подключены реальные измерения.
- Текущая кнопка LOAD SFZ не является полноценным Import Sounds manager.

**Решение REV.20:** главный визуальный источник — 01 INTERFACE NEON STAGE DEFAULT .png; изображения 02–07 — дополнительные эталоны AUTOCHORDS, FX EDIT и multi-window. SVG banner — только брендовый баннер, не runtime UI. Перестроить главный editor под его иерархию и пропорции; не заменять его generic JUCE layout. Все элементы — реальные контролы, фиктивные метрики/кнопки запрещены.

## 3. Factory presets, switching и сохранение

### Фактическое состояние
- CMake встраивает `presets/factory_bank_300.json` в BinaryData.
- Editor загружает массивы melodyPresets и patternPresets в каталог.
- Текущий `applyFactoryPreset()` применяет только четыре значения: distortionDrive, tone, reverbMix, output; затем переключает playMode.
- Для Pattern UI прямо показывает сообщение `PERFORMANCE ENGINE REQUIRED`; каталог сам по себе не доказывает, что все pattern presets задают реальные паттерны.
- В UI нет отдельного сохранения пользовательского пресета. APVTS host state (если сохранён в DAW) — это не preset browser и не файл .ppgm/.ppgp.

### Требуемая реализация
- Полный параметрический preset schema с validation и versioning.
- Загрузка factory/user presets атомарно: при ошибке прежнее состояние остаётся.
- Previous/Next, категории, поиск, Favorites, audition/preview, double-click load.
- Save / Save As, Rename, Delete только для User; Factory read-only.
- Файлы .ppgm/.ppgp и .ppgbank по утверждённой спецификации; хранить sampleProfile/libraryId, не абсолютные пути к сэмплам.
- Проверить 300 factory definitions: каждая запись должна быть валидной, менять ожидаемые параметры и соответствовать Melody/Pattern engine.

## 4. Import Sounds — целевой pipeline

Пользователь выбирает Import Sounds; система должна провести активы через безопасную подготовку, а не просто скопировать их в SamplePool.

1. **Выбор источника:** Import Folder, Import ZIP, Add SFZ Instrument; поддержка WAV, OGG, MP3, FLAC, AIFF/AIF как пользовательских источников. NCW не поддерживается.
2. **Безопасный scan:** ограничение размера/количества файлов, проверка путей, ZIP traversal, symlinks, повреждённых файлов и дубликатов.
3. **Metadata:** codec, sample rate, bit depth, channels, duration, size, SHA-256, source/license, errors.
4. **Decode/prepare:** background workers читают/декодируют source assets; нормализованный внутренний PCM/cache строится вне audio thread и помечается версией формата + hash исходника. Lossy imports помечаются как lossy.
5. **Mapping:** SFZ maps читаются как есть. Для raw WAV Auto Mapping — только предложение. Неоднозначные файлы требуют подтверждения в Mapping Editor: root/low/high key, velocity range, articulation, round-robin, gain/pan/tune/release.
6. **Validation:** проверка gaps/overlaps в key/velocity zones, отсутствующих файлов, лицензий, checksum и лимитов.
7. **Atomic publish:** сначала staging, затем только после полной проверки добавление библиотеки в Library Browser. При ошибке текущая активная библиотека не меняется.
8. **Engine integration:** создать manifest/libraryId и внутренний индекс; engine загружает готовую карту/кэш, а не выполняет файловое сканирование или decode в processBlock.
9. **Preset binding:** preset ссылается на libraryId/profile; если банк отсутствует — warning, настройки пресета сохраняются.
10. **Export:** разрешать только при подтверждённом redistribution permission для каждого asset.

### Что есть сейчас
- Один SFZ file chooser и асинхронный вызов `loadSfzFileAsync`.
- В текущем UI отсутствуют Import Folder/ZIP, список библиотек, preview, metadata, auto-mapping, Mapping Editor и отдельный staging/publish UI.
- Следовательно, Import Sounds нельзя рекламировать как готовую функцию.

## 5. Проверочный план и критерии закрытия

### Engine
- [ ] CTest + отдельные regression tests на MIDI, sampler, pattern dispatch, note-off/release, voices и concurrent reload.
- [ ] Проверка velocity layers / palm mute / articulations на реальных лицензированных sample maps.
- [ ] Проверка всех включённых FX на аудиовыходе, отсутствие NaN/clipping/denormals.
- [ ] CPU/RAM/underrun benchmark при 1/8/16/32/64 voices и GOOD/NORMAL/NIGHT.
- [ ] DOUBLE: phase/mono compatibility, transient, clipping и latency tests.
- [ ] Безопасное управление фоновыми worker threads; никакого blocking/thread spawn в audio callback.

### UI / Cover
- [ ] Перестроить editor по Cover Interface.jpg.
- [ ] Проверить 100%, 125%, 150% scaling и resize; ничего не обрезается.
- [ ] Проверить каждую кнопку/ручку/селектор: реальная APVTS или реальное действие.
- [ ] CPU/RAM только измеренные.
- [ ] Основные действия доступны без отдельного Settings окна.

### Presets
- [ ] Все 300 factory entries parse/validate.
- [ ] Полный preset application, включая mode, performance/style data и все supported parameters.
- [ ] Previous/Next, поиск, фильтры, preview, favorites.
- [ ] Save As -> close/reopen -> reload с побитово/численно эквивалентным parameter state.
- [ ] Rename/Delete user preset, Factory read-only.
- [ ] Import/export bank и missing-library warning.
- [ ] DAW project save/reopen.

### Import Sounds
- [ ] WAV/SFZ folder import, затем ZIP import с ZIP-slip tests.
- [ ] metadata + SHA-256 + duplicate detection.
- [ ] mapping editor и подтверждение auto mapping.
- [ ] corrupt/unsupported/missing sample не заменяет активную библиотеку.
- [ ] импорт и preview не делают disk I/O/allocations/locks в audio callback.
- [ ] Повторный импорт не дублирует SamplePool.
- [ ] Проверка лицензии и происхождения каждого распространяемого factory asset.

### Release validation
- [ ] Windows x64 Release build.
- [ ] CTest.
- [ ] VST3 bundle verification.
- [ ] pluginval strictness 5.
- [ ] Проверка установки/загрузки/звучания в FL Studio 20 x64 на Windows 10.
- [ ] Запись результатов отдельно; CI не заменяет DAW test.

## Приоритет следующей реализации

1. Preset service: полный loader + Save As/Load User preset + prev/next, с тестами round-trip.
2. Cover UI: переразметить основной editor и добавить реальные действия Browser/Presets/Settings.
3. Import Sounds phase 1: folder scan + SFZ/WAV metadata + staging + validation + atomic library publish.
4. Mapping Editor / raw WAV auto-mapping.
5. ZIP import/export, checksum/manifest, license reports.
6. Дальнейшие engine benchmarks и аудио-регрессии.

Статус документа: **аудит выполнен по исходникам; перечисленные незакрытые функции не считаются реализованными.**


---

## REV.20 — актуальная проверка целевого main (2026-11-20)

Проверены файлы REV.20 main на SHA 974c5877d1a0375100539d2513329a38feb84871.

### Подтверждено кодом / CI
- VST3 x64, JUCE 7.0.12, Windows x64 build и full CTest имеют green evidence на предыдущем exact SHA 8cfd11ecce3c8039360c1c194be5251e716c9015 (run 44717722638). На следующем SHA 974c5877... проходит повторная сборка с дополнительной PageCache правкой.
- Существует 16-theme runtime gallery. На exact SHA 8cfd11e прошли загрузка manifests, ThemeManager decode трёх SVG layers для всех 16 тем, 32 PNG CRC/dimension checks, exact registry audit и package stage; все 16 записей помечены runtimeReady.
- Главная оболочка содержит 9 rotary attachments и 7 FX toggle attachments; 27-control contract остаётся зафиксированным.
- Skin Gallery содержит Preview / Apply / Cancel / Favorite, фильтр ALL SKINS / FAVORITES ONLY, stable-ID сохраняется, ordinal 1–16 показывает logical position.
- MELODY и PATTERN доступны как единственные основные playing modes. AutoChords, FX EDIT, Pattern Rhythm, Import Guitar, Settings и Skin Gallery открываются как вспомогательные окна.

### Текущие функциональные gaps (проверено в REV.20 source)
- Default editor size в коде — 1024×700; resize limits — 900×640…1600×1100. Это не доказывает соответствие композиции главному mockup 01; требуется сравнение в собранном VST3 на FL Studio 20 и тесты DPI 100/125/150%.
- Main editor рисует панели/skin material layers, но в Source/PluginEditor.cpp нет загрузки/display active-skin hero PNG в Playing Core. Главный mockup требует hero artwork в центральной зоне. PR #54 предлагал этот strip, но не принят целиком: он переименовывал SKIN-1 в NEON FORGE и нёс legacy 102-theme tree. Нужна отдельная безопасная реализация без конфликта идентичности.
- Текущий applyFactoryPreset() меняет только четыре параметра (distortionDrive, tone, reverbMix, output) плюс mode. Это не полная атомарная загрузка полного preset schema и не доказательство всех 500 presets playable.
- PATTERN preset отображает статус PERFORMANCE ENGINE REQUIRED; каталог сам по себе не создаёт performance/riff assets. 250 PATTERN core presets ещё не выполнены и должны группироваться по окнам/разделам PATTERN, не одним 250-item списком.
- User preset Save / Save As / Rename / Delete, portable .ppgm/.ppgp/.ppgbank browser round-trip, favorites и Import/Export bank actions не найдены в активном Editor source. Host project state не заменяет user preset browser.
- Import Guitar в target открывает один SFZ file chooser и вызывает async SFZ loader. Import Folder/ZIP, multi-format metadata scan, auto mapping + Mapping Editor, atomic publish, library browser, physical distribution, license gating/export и recovery flow не считаются завершёнными.
- CPU/RAM telemetry и actual performance values в интерфейсе отсутствуют. Не добавлять фиктивные цифры; показывать только измерения от реального backend.
- AutoChords window содержит configuration/scale controls, но M4 chord voicing/fingering foundation из source PR #4 не интегрирована как полноценный live Pattern MIDI→voicing→sample workflow.
- True multicore worker-count control, GOOD/NORMAL/NIGHT measured power profile, two independent takes Double Track и measured ECO memory performance остаются не подтверждены; source PR #13 — draft.

### 500 factory preset delivery status
- Target factory catalog currently has 300 authored definitions (150 MELODY + 150 PATTERN), not the final 500 playable presets.
- applyFactoryPreset() covers only the four parameter assignments listed above.
- No claim of 15 GB BASIC audio payload or all-500 license-cleared/mapped/listening-verified presets is made.
- BASIC minimum is 15 GB included; EXPANDED is optional +15 GB initial tier (30 GB combined), but all 500 core presets must work from BASIC alone.

### Release / host gates
- Exact REV.20 Windows x64 build and CTest are green on SHA 8cfd11e; latest current PageCache+docs commit requires its own CI completion.
- pluginval strictness 5 is still pending on the current target SHA.
- FL Studio 20 on Windows 10 manual host acceptance remains pending; the CI artifact alone does not close this gate.
- Full 16-theme gallery visual inspection, Preview/Apply/Cancel/persistence, 150 ms hot-swap, ECO/memory/audio invariance and DPI 100/125/150% remain host/performance tasks.


## CI corrections after functional audit — 2026-11-20

- PageCache publish rollback/stale-key regression tests are now proven in REV.20 exact-SHA run 44719521911 (974c5877...), full CTest 15/15 PASS.
- The live EQ/AMP TONE/compressor DSP patch is staged separately and is not part of the 974c target run; it needs the next exact-SHA validation.


## DSP audit update — 2026-11-20

The following audio-path wiring has now been selectively ported into REV.20 (target test pending): live `eqLowFreq` / `eqHighFreq` crossover cutoffs, independent AMP TONE high-band tilt that remains active when EQ is bypassed, and Compressor Amount blend snapshotted once per block outside the sample loop. A new CTest guard checks declarations/consumption and ensures no APVTS atomic load inside the per-sample compressor loop. This does not change the separate finding that factory preset application currently writes only four preset values plus mode.


## 2026-11-22 — Session Guitarist-inspired workflow checkpoint (user approved)

- User approved the functional direction: use Session Guitarist – Electric Sunburst Deluxe/Vintage as a usability benchmark while retaining NEON STAGE DEFAULT as the only visual source of truth. No NI assets, branding, presets, recordings, riffs or protected composition are copied.
- PATTERN panel now displays three separate dimensions: loaded SFZ source (live filename + existing Import Guitar action), current factory tone label, and recorded-articulation map verification status. Existing section routing, rhythm slot selection and Preview/Apply/Cancel are retained. Commits: dbb05b8872746ad31fd0bce3103bb94e6f45358a, a9021d4a16fb3d4a7a1b3fa186acee3b49fd123c.
- This is a UI workflow checkpoint only. The articulation choice and palmMuteThreshold APVTS parameters are declared, but static inspection did not find them consumed in PluginProcessor.cpp audio path. Do not count articulation switching or velocity-triggered palm mute as implemented.
- Sampler already has SFZ key/velocity zones, seq_length/seq_position round-robin selection, group/off_by choking, sample streaming and bounded voice count. Existing SamplePoolTests.cpp covers round-robin cycles, independent sets, incomplete-set fallback, invalid sequence positions, streamed playback and voice limits. Remaining gap is recorded articulation identity/zone routing and its integration with PatternScheduler, not basic SFZ round-robin support.
- Next workstream: define a provenance-safe articulation metadata contract; map only verified source zones to Open/Palm Mute/Muted/Legato/Slide/etc.; route velocity threshold only when matching zones exist; test note-on/off, choke/release, RR, pattern transitions and host-sync without audio-thread I/O/locks. Unavailable techniques must remain unavailable.
- Verification: run 44997292780 targeted source SHA a9021d4a16fb3d4a7a1b3fa186acee3b49fd123c was observed in progress; current main has a later journal update. Exact-HEAD Windows VST3/CTest, pluginval strictness 5 and FL Studio 20 acceptance remain open.


## 2026-11-22 — SFZ keyswitch metadata foundation (implementation checkpoint)

- Added parser support for SFZ sw_lokey, sw_hikey, sw_last, sw_default and sw_label with bounded note parsing and validation of selector ranges/defaults.
- Carried authored keyswitch range/default/label metadata into immutable SamplePool::RegionView and added SfzParserTests/SamplePoolTests coverage.
- This is metadata ingestion only. MIDI keyswitch state, per-channel active articulation, audio-thread region filtering, and UI availability/selection are still NOT IMPLEMENTED. No articulation is to be marked playable until those steps and recorded-map verification pass.


## 2026-11-22 — SamplerEngine keyswitch selector (implementation checkpoint)

- SamplePool region lookup now accepts an active keyswitch and filters SFZ sw_last regions. It exposes switch-range detection and the source-authored sw_default.
- SamplerEngine initializes per-channel active switch state from the loaded bank default, updates it through lock-free atomics, and uses it during noteOn region selection. Regression tests cover selected labels/defaults and out-of-range rejection.
- Still open: intercept keyswitch MIDI notes in PluginProcessor so they do not become melody notes or PATTERN chord notes; publish current articulation state to UI; connect pattern changes with sample-offset scheduler events; verify against real licensed SFZ maps. This is not yet an end-user-complete articulation workflow.


## 2026-11-22 — MIDI keyswitch event routing (implementation checkpoint)

- PluginProcessor now recognizes note-on/off events inside the active SFZ switch range in both MELODY and PATTERN. Note-on updates the sampler's per-channel active switch at the event position; keyswitches are excluded from guitar triggering and PATTERN held-chord state. Keyswitch note-off does not release a guitar voice.
- JUCE keyboard held-state and the editor's held-note snapshot clear/exclude these control notes.
- Sampler tests now check independent per-channel switch state.
- Still open: expose the current sw_label in the UI, validate complete real-bank articulation zones/velocity maps, and test switching while host-synced pattern events are already scheduled. FL Studio 20 host acceptance remains pending.


## 2026-11-22 — Real-time keyswitch lookup optimization

- SFZ snapshot construction now precomputes a fixed 128-note keyswitch mask and default selector. processBlock queries this immutable mask in O(1), avoiding a linear scan of large sample maps for each MIDI event. No allocation or lock is introduced on the audio thread.


## 2026-11-22 — Live articulation label in PATTERN workspace

- SamplerEngine/SamplePool expose the source-authored sw_label corresponding to the active per-channel switch; the processor publishes it as a read-only UI query.
- PATTERN workspace now refreshes the active articulation label and switch note using its existing 2 Hz timer. If no switch map exists, it explicitly displays NO RECORDED ARTICULATION MAP. If a switch exists without sw_label, it says SOURCE LABEL NOT PROVIDED.
- This is metadata visibility only; no invented technique names. The label does not certify recording provenance, license, or technique fidelity. Those require source-bank inspection and runtime audition.


## 2026-11-22 — Velocity-triggered Palm Mute routing (implementation checkpoint)

- The immutable SFZ snapshot caches a Palm Mute selector only when a region declares a source-authored sw_label containing "Palm". SamplerEngine noteOn selects this switch for velocities at/below palmMuteThreshold and restores sw_default for higher velocities.
- PluginProcessor passes the existing threshold in both MELODY and PATTERN. The selection is channel-local and still passes through normal note/velocity/channel region matching.
- If the loaded bank has no Palm-labeled switch zone, the feature safely does nothing; no synthetic Palm Mute sample is created. Tests cover low/high velocity selection and channel isolation.
- Still required: validate with a real, licensed guitar bank that has correctly mapped Palm Mute and open articulations; audition transitions in FL Studio 20; verify whether a source bank uses another label convention and document explicit aliases only after inspection.

- Follow-up hardening: Palm label detection is case-insensitive and the sampler regression uses the public active-label query.

- Case-insensitive label matching normalizes the copied SFZ label string during off-thread snapshot construction; no temporary-iterator lifetime issue remains.


## 2026-11-22 — UI visual checkpoint supplement

The main-window visual pass has addressed the following source-level gaps without changing the approved geometry or audio contracts:

- Corrected the visible main panel titles to PRESETS, PLAYING CORE, AMP & TONE and FX CHAIN.
- Corrected AUTO DISCOVER naming and retained its disabled state; CURATOR remains disabled.
- Disabled ABOUT until a verified About panel exists.
- Added real selected-state feedback to the MELODY/PATTERN tabs, synchronized from the attached playMode ComboBox/APVTS state.
- Connected the existing Skin-1 default/hover/pressed/disabled artwork lookup to the Import Guitar, Auto Discover, Curator, Settings, About and SKIN header controls.
- Preserved the 1024×700 launch size, current responsive layout, 9 APVTS rotary bindings, 7 FX bindings, 16-theme registry and Skin-1 asset set.

Still open: visually inspect the actual canonical 01 INTERFACE image against a runtime screenshot at 1024×700; verify the 27-control state map end-to-end (including preset browser, mode selector, keyboard, LCD and LED); test 100/125/150% scaling and resizing; then pass exact-HEAD Windows x64 build, CTest, pluginval strictness 5 and FL Studio 20 host acceptance. No visual or build gate is marked complete solely from these source edits.


## 2026-11-22 — Source-location index cross-reference

Permanent source and approved-asset path index is recorded in `docs/REV20_DECISION_TIMELINE_RU.md`. Repository: `l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-`, branch `main`. Canonical NEON STAGE DEFAULT image is already present at repository root: `/01 INTERFACE  NEON STAGE DEFAULT .png` (blob SHA `747207e183c77e8b913a543b2dc40b29829e77da`). Main implementation paths: `/Source/PluginEditor.cpp`, `/Source/PluginEditor.h`, `/Source/PluginProcessor.cpp`, `/Source/PluginProcessor.h`, `/Source/UI/`, `/Source/Performance/`, `/Source/Sampler/`; supporting trees: `/Assets/3D/References/`, `/SKINS/`, `/assets/`, `/presets/`, `/tests/`, `/tools/`, `/docs/`, `/.github/workflows/`. Check the permanent index and live GitHub tree before requesting any existing asset from the user. Tool inability to render a binary image must not be reported as file absence.

## 2026-11-22 — NEON STAGE main layout discrepancy (confirmed against asset master prompt)

**Priority: P0 visual composition / implementation gap.**

The approved master prompt at Assets/3D/References/PPGU_REV20_NEON_STAGE_DEFAULT_ULTIMATE_ASSET_MASTER_PROMPT_RU.txt, section 4, specifies:
1. LEFT: factory preset browser.
2. CENTER: PLAYING CORE with the nine APVTS-backed rotary controls in a 3×3 grid and the MELODY/PATTERN mode controls.
3. RIGHT: AMP & TONE / FX CHAIN with exactly seven APVTS-backed FX switches.
4. LOWER: performance display, MIDI keyboard and live status/footer.

Current Source/PluginEditor.cpp instead puts the nine rotary controls in the right zone, the FX Edit component in the center, and the seven FX switches in a separate horizontal strip. The panel captions alone therefore do not establish layout compliance.

**Required implementation sequence:** map canonical 01 mockup geometry to component bounds; move the 3×3 knob group to center; compose the seven FX switches in the right rack; preserve the auxiliary FX EDIT workflow; retain all existing APVTS parameter IDs, slider/button attachments, component IDs, accessibility/hover/pressed/disabled states and resize constraints; verify at 1024×700 and minimum 900×640. Do not invent a replacement composition or add controls.

**Build gate:** Windows run 44998253820 failed at PluginProcessor.cpp:326 because JUCE MidiKeyboardState::noteOff requires the velocity argument. Corrected on main by commit cab4f58e8a2fc0109ed85f1c1f8c14e0b7b2e686; new exact-HEAD CI/CTest result pending. No build pass is claimed.