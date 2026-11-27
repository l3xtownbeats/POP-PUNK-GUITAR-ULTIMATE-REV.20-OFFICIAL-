# NEON STAGE DEFAULT — АКТУАЛЬНЫЕ ОТКРЫТЫЕ ЗАДАЧИ

**Дата сверки:** 2026-11-27  
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
