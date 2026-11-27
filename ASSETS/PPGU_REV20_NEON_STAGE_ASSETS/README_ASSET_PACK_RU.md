# PPGU REV.20 — NEON STAGE DEFAULT / ASSET PACK

**Тема:** SKIN-1 / NEON STAGE DEFAULT / `skin-053`  
**Runtime source of truth:** `SKIN/Skin_053/`  
**Asset source:** `ASSETS/PPGU_REV20_NEON_STAGE_ASSETS/`  
**Статус:** SOURCE ATLAS VALIDATED + EXPORTED; FULL ASSET / VISUAL / RUNTIME ACCEPTANCE OPEN.

## Назначение

Каталог содержит дополнительные векторные мастера, схемы компонентов, manifests и средства экспорта. Канонические runtime-файлы темы остаются в `SKIN/Skin_053/`. Не создавать дубли runtime-ассетов без необходимости и не подменять реальные JUCE-компоненты декоративными картинками.

## Утверждённая композиция

- LEFT: Factory Preset Browser.
- CENTER: Playing Core / stage banner.
- RIGHT: AMP & TONE / семь FX switches.
- Девять rotary-контролов в одной горизонтальной строке.
- Нижняя зона: Performance Display и существующая MIDI-клавиатура на 49 клавиш.
- Главные режимы: только MELODY и PATTERN; AUTOCHORDS — вспомогательное окно PATTERN.

## Контракт графики

- SKIN-1 palette/materials берутся из `SKIN/Skin_053/theme.json`.
- Отдельные прозрачные SVG/PNG; экспорт 1×/2×.
- 9-slice frames используют согласованные insets.
- Основные rotary: девять параметров, слои BASE/RIM/FACE/POINTER/SCALE/GLOW.
- FX: семь существующих переключателей, OFF/ON.
- Display: шесть LCD source-art states.
- LED: семь source-art samples.
- Meter: три 12-сегментных stereo samples.
- Keyboard: 49 клавиш, 29 white + 20 black, C/E/G overlays.
- Иконки и browser elements только для уже существующих действий.

Динамические данные, тексты, MIDI-состояния, meter peaks и интерактивные области остаются JUCE runtime слоями.

## Atlas 04 — актуальная версия

Файл `04_ppgu_atlas_displays_keyboard.svg`: **1920×1880**, viewBox `0 0 1920 1880`.

Содержит 6 LCD states, 7 LED states, 3 stereo meter samples, 49-key keyboard и pitch/mod faders. Это source artwork; runtime mapping не заявляется.

## Проверка и экспорт

Из корня репозитория:

```bash
python tools/validate_neon_stage_vector_atlases.py
python tools/export_neon_stage_vector_atlases.py --scale 1.0
```

Локальный экспорт требует CairoSVG 2.7.1 и Pillow 10.4.0. CI workflow проверяет структуру и экспортирует атласы. Успешный CI не заменяет ручную визуальную проверку кадров и проверку JUCE/host.

## Канонические документы

- `ASSET_DEVELOPMENT_JOURNAL_RU.md` — утверждённая база, решения, текущая проверка и статусы.
- `ASSET_OPEN_ISSUES.md` — только актуальные незакрытые задачи.
- `REFERENCE_COMPONENT_MAP.md` — карта источников/компонентов.
- `ASSETS/PPGU_REV20_NEON_STAGE_ASSETS/ASSET_MANIFEST.json` — индекс исходного asset pack.
- `SKIN/Skin_053/assets/asset_manifest.json` — канонический runtime manifest темы.
- `SKIN/Skin_053/theme.json` — тема, palette и runtime links.
- `SKIN/Skin_053/assets/controls/control_states_manifest.json` — control-state contract.
- `Source/PluginProcessor.cpp` — фактические APVTS IDs и processor contract.

## Приёмка

Полный список блокеров находится в `ASSET_OPEN_ISSUES.md`. До прохождения визуальных, runtime, exact-head CI, Pluginval и FL Studio 20 gates пакет не обозначается COMPLETE.
