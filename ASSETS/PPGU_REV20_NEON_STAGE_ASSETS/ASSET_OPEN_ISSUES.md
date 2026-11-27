# NEON STAGE DEFAULT — АКТУАЛЬНЫЕ ОТКРЫТЫЕ ЗАДАЧИ

**Дата сверки:** 2026-11-28  
**Ветка:** `assets/ppgu-rev20-atlas04-display-led-meter-states`  
**Тема:** SKIN-1 / NEON STAGE DEFAULT / `skin-053`  
**Общий статус:** PARTIAL — source atlas CI passed; full visual/runtime/host acceptance is open.

## P0 — визуальная приёмка

- [ ] Просмотреть свежий CI-export всех атласов и standalone exports целиком и покадрово при 100%/200%.
- [ ] Проверить LCD/LED/meter образцы: clipping, alignment, labels, contrast, state differentiation.
- [ ] Подтвердить прозрачность PNG и корректные размеры после raster export.
- [ ] Зафиксировать screenshot/contact sheet review; не объявлять pixel-perfect без сравнения с утверждёнными PPGU references.

## P1 — отдельные production assets

- [ ] Завершить/проверить production backgrounds и materials по SKIN-1.
- [ ] Довести семь основных panel compositions; shell SVG и guide placeholders не считать готовыми панелями.
- [ ] Сверить восстановленные три rotary strips с утверждёнными knob mockups при 100%/200%; подтвердить точность металла, насечки, шкалы, бликов и указателя.
- [ ] Завершить FX EDIT-specific rotary layers/scales, не менять APVTS bindings.
- [ ] Довести недостающие button focus/disabled, LED, keyboard hover/pressed и per-control state mappings по каноническому manifest.
- [ ] Проверить отдельные preset-browser assets и иконки на соответствие существующим действиям.

## P2 — manifests и runtime

- [ ] Для каждого нового standalone export записать path, format, dimensions, byte count и SHA-256 в manifest.
- [ ] Проверить mapping каждого asset на существующий JUCE component/consumer.
- [ ] Новые семь LED samples и шесть LCD samples пока считать source-art coverage, а не автоматически подключёнными runtime states.
- [ ] Динамические тексты, MIDI, LED, meters и значения оставлять JUCE-driven.
- [ ] Не добавлять новые controls, функции или UI-состояния без утверждения и source/runtime contract.

## P3 — интеграция и приёмка

- [ ] JUCE editor screenshot/overlay/difference review при 900×640, 1024×700 и 1600×1100.
- [ ] Exact-head Windows x64 VST3 build и полный CTest.
- [ ] Pluginval strictness 5.
- [ ] Ручная проверка в FL Studio 20 x64.
- [ ] Только после всех применимых gates менять общий статус на COMPLETE.

## Подтверждено на текущем head

- [x] Atlas 03 восстановлен из пустого файла: 3 rotary strips × 61 frame; source-contract validation и export прошли на exact head.
- [x] Atlas 04 source расширен: 6 LCD, 7 LED, 3 stereo meter samples.
- [x] Существующая 49-key keyboard (29 white + 20 black) и pitch/mod faders сохранены.
- [x] SVG размер 1920×1880 и viewBox согласованы.
- [x] GitHub Actions run `46036878566` (run #159) на exact head SHA `a8a39ddd930e11a956899c2ac772745c652a1ceb`: SUCCESS.
- [x] Экспорт 490 standalone components в 1×/2×, 41 SVG icon и PNG-вариантов 16/24/32/48, 70 source-faithful reference components в 1×/2×, девяти rotary controls × шесть независимых слоёв.
- [x] Artifact `PPGU-NEON-STAGE-SVG-ATLAS-EXPORT`, ID `15218795470`, 52,259,439 bytes; SHA-256 `ba6ba0076baf32e366208149fcb11821104c388fd7c362c91ad18a05d9f30691`.

## Не является подтверждением

Atlas 03 и экспортный конвейер прошли exact-head source-contract validation и PNG export. Ручная визуальная приёмка всё ещё не выполнена. CI export не означает pixel-perfect approval, JUCE runtime mapping, pluginval, FL Studio 20 acceptance или завершённость всего asset pack.

## Единственное известное дизайн-расхождение

В master prompt и текущем `SKIN/Skin_053/theme.json` ранее отмечено расхождение semantic tokens `danger` / `warning`. До отдельного решения владельца сохранять runtime `theme.json` как источник текущего runtime поведения; не выпускать новые semantic-color assets на спорных значениях.


## Новая находка — rotary strip export

- [x] Повторный CI export после исправления crop координат atlas 03 выполнен: run `46056184780` (#164), exact head `627e751b3130486ad7c598427fce4df0c5c6979d`, SUCCESS. Новый artifact `15227070722`.
- [x] Проверены все 183 кадра в трёх standalone полосах на 1× и 2×: размеры полос 128×7808 / 256×15616, каждый кадр имеет полный alpha-bounds knob и RGBA transparency.
- [x] Выполнен первичный визуальный просмотр контактного листа и полосы rotary strip 1× после исправленного экспорта: кадры теперь целые, обрезания по краям не видно.
- [ ] Выполнить художественную проверку каждого типа регулятора и отдельных кадров при 100%/200% относительно утверждённых rotary references; текущий контактный лист не доказывает pixel-level сходство.

## Проверка rotary crop — 2026-11-28

- Старый artifact `15218795470` остаётся отклонённым для standalone rotary strips из-за неверных crop origins.
- Новый artifact `15227070722`, размер 62,326,595 bytes, SHA-256 `e27af7693f843ea050d69a1b99a419cd567e0bedcf14c62abc1739891634cc45`.
- Run `46056184780` (#164) успешно прошёл source validation, raster export 1×/2×, 490 standalone components в каждом масштабе, 41 icon family, 70 reference components и девять rotary controls × шесть слоёв.
- Ручная оценка художественного соответствия, pixel-level comparison и runtime/host acceptance остаются открытыми.


## Визуальный QA экспортного пакета — 2026-11-28

- Просмотрен новый контактный лист `NEON_STAGE_ATLAS_CONTACT_SHEET.jpg` и полоса `rotary_strip_1_61_frames.png` после исправления crop.
- Все три 1× полосы имеют размер 128×7808; каждый из 61 кадров содержит alpha bounds (3,3)–(125,127), без прежнего обрезания. Аналогичные автоматические per-frame проверки прошли на 2× в CI.
- Проверены 490 standalone PNG в каталоге 1× и 490 в каталоге 2×: все читаются как RGBA; ошибок формата не обнаружено.
- Контактный лист показывает полный набор исходных атласов и экспортных групп, однако это обзорная картинка, а не сопоставление с утверждёнными master mockups. Сходство формы/материала/освещения/типографики с эталоном не принято.
- Результат: export integrity — PASS; художественная visual parity — NOT ACCEPTED; runtime/host integration — NOT VERIFIED.


## P0 — найдено расхождение rotary artwork с утверждённым reference sheet — 2026-11-28

- При сопоставлении `reference_components_1x/knobs/rotary_50_percent.png` с кадром 30 текущей полосы `rotary_strip_1_61_frames.png` обнаружено существенное художественное расхождение.
- В source reference: выраженная металлическая лицевая поверхность с радиальной шлифовкой, яркая сегментная cyan LED-шкала по внешней дуге и отдельный световой маркер положения. В текущем SVG strip: упрощённая тёмная плоская лицевая поверхность, обычные деления шкалы и центральный указатель; отсутствует соответствующая сегментная LED-дуга и характерная металлическая фактура.
- Геометрическая целостность исправленных 183 кадров подтверждена, но художественное соответствие эталону — FAIL / NOT ACCEPTED. Успешный CI не меняет этот статус.
- Следующая задача: перестроить rotary atlas на базе утверждённого source treatment (и существующего `SKIN/Skin_053/assets/vector/rotary_knob_master.svg` как дополнительного master), разделив вращаемый marker/pointer и неподвижные face/rim/LED scale layers. Затем повторить 61-frame render и сравнить 0/25/50/75/100% позы с исходными reference crops.
- До этой работы не подключать текущий atlas 03 как финальный pixel-matched rotary artwork и не заявлять 1:1.


## Черновая переработка rotary artwork — 2026-11-28

- [x] Перестроены все 183 face instances в трёх 61-frame strips: добавлен металлический радиальный градиент лицевой поверхности и тонкие radial-brush highlights.
- [x] Добавлена сегментная cyan LED-дуга из 20 отдельных сегментов; количество активных сегментов изменяется синхронно с индексом кадра (0–100%).
- [ ] Проверить свежий CI export и визуально сопоставить 0/25/50/75/100% кадры с source crops. Это промежуточная реконструкция: она ещё не подтверждена как pixel-perfect и не заменяет ручную приёмку.
- [ ] Отдельно проверить соответствие положения светового маркера/указателя исходному эталону; при необходимости заменить текущую стрелку на marker geometry из утверждённого knob artwork.


### Rotary reconstruction — compacted revision (2026-11-28)

- Reworked the 183 face instances (3 strips × 61 frames) with a shared radial-metal gradient and a reusable radial-brush highlight group. The shared definition avoids duplicating the 72 highlight paths in every frame.
- Replaced the previous triangular pointer with a separate luminous cyan position dot at the end of the rotating transform, matching the visible indicator language in the 50% source crop more closely.
- Replaced the simple thin cyan arc with 20 discrete LED segments distributed across a 270° sweep; active segment count follows the 61-frame position index. Segment geometry is shared through reusable SVG definitions to keep the source atlas below 1 MB.
- Structural verification on the committed SVG: 183 brushed faces, 183 radial-brush uses, 183 rotating marker groups, 3,660 segment instances (3,050 on / 610 off across the three strips). This is source-structure QA only; a fresh raster export and visual comparison are still required.
- **Visual acceptance remains open.** The 50% source crop is available, but the complete source design is not supplied as editable layers. The rebuilt metal/LED treatment is a reconstruction, not a proven pixel-perfect reproduction. Do not mark rotary art accepted or wire it as final runtime art until raster comparison at 0/25/50/75/100% is reviewed.
