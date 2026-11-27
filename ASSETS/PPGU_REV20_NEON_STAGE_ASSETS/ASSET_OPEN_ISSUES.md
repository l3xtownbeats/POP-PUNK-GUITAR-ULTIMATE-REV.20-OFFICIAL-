# NEON STAGE DEFAULT — АКТУАЛЬНЫЕ ОТКРЫТЫЕ ЗАДАЧИ

**Дата сверки:** 2026-11-27  
**Ветка:** `assets/ppgu-rev20-atlas04-display-led-meter-states`  
**Тема:** SKIN-1 / NEON STAGE DEFAULT / `skin-053`  
**Общий статус:** PARTIAL — source atlas CI passed; full visual/runtime/host acceptance is open.

## P0 — визуальная приёмка

- [ ] Просмотреть свежий CI-export atlas 04 целиком и покадрово при 100%/200%.
- [ ] Проверить LCD/LED/meter образцы: clipping, alignment, labels, contrast, state differentiation.
- [ ] Подтвердить прозрачность PNG и корректные размеры после raster export.
- [ ] Зафиксировать screenshot/contact sheet review; не объявлять pixel-perfect без сравнения с утверждёнными PPGU references.

## P1 — отдельные production assets

- [ ] Завершить/проверить production backgrounds и materials по SKIN-1.
- [ ] Довести семь основных panel compositions; shell SVG и guide placeholders не считать готовыми панелями.
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

- [x] Atlas 04 source расширен: 6 LCD, 7 LED, 3 stereo meter samples.
- [x] Существующая 49-key keyboard (29 white + 20 black) и pitch/mod faders сохранены.
- [x] SVG размер 1920×1880 и viewBox согласованы.
- [x] GitHub Actions run `45944877122` на SHA `5fac4ae532e70e26600ef12764cb008d850df3e7`: SUCCESS.
- [x] Artifact `PPGU-NEON-STAGE-SVG-ATLAS-EXPORT`, ID `15174501574`, 88,281,866 bytes.

## Не является подтверждением

CI export не означает pixel-perfect approval, полную самостоятельную PNG-библиотеку, JUCE runtime mapping, pluginval, FL Studio 20 acceptance или завершённость всего asset pack.

## Единственное известное дизайн-расхождение

В master prompt и текущем `SKIN/Skin_053/theme.json` ранее отмечено расхождение semantic tokens `danger` / `warning`. До отдельного решения владельца сохранять runtime `theme.json` как источник текущего runtime поведения; не выпускать новые semantic-color assets на спорных значениях.
