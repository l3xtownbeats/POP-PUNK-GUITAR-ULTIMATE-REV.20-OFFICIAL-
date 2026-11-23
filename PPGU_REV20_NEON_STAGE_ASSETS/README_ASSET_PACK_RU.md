# PPGU REV.20 — NEON STAGE DEFAULT ASSET PACK

**Статус:** production workspace / частично заполнен; не объявлять финальным комплектом.  
**Целевая оболочка:** SKIN-1 / NEON STAGE DEFAULT / `skin-053`.  
**Ветка:** `main`.  
**Назначение:** отдельная производственная папка для графических исходников, экспортов, превью, контактных листов и проверки ассетов.

## 1. Источник истины

В REV.20 уже существует канонический runtime-набор ресурсов:

- `../SKIN/Skin_053/theme.json` — тема, палитра, типографика, 27 UI control IDs и runtime-пути.
- `../SKIN/Skin_053/assets/asset_manifest.json` — инвентаризация исходных/исполняемых ресурсов SKIN-1.
- `../SKIN/Skin_053/assets/controls/control_states_manifest.json` — 27 контролов × 5 состояний.
- `../SKIN/Skin_053/assets/spritesheets/neon_stage_spritesheet_manifest.json` — геометрия и координаты спрайтов.
- `../SKIN/Skin_053/assets/spritesheets/` — PNG sprite atlases, используемые текущим runtime.
- `../SKIN/Skin_053/svg/` — SVG material layers.
- `../SKIN/Skin_053/assets/preview/`, `hero/`, `background/`, `controls/`, `fx_layers/`, `icons/`, `textures/` — отдельные визуальные ресурсы.

Бинарные runtime-ассеты не дублируются в этой папке: это предотвращает расхождение копий. Папка содержит производственный индекс и точки подготовки экспорта; канонические файлы остаются в SKIN/Skin_053/assets и загружаются существующим ThemeManager.

## 2. Структура пакета

Подкаталоги ниже подготовлены как целевые места для независимых экспортов. В них нельзя помещать макеты с запечённым динамическим текстом, параметрами или ложной индикацией.

- `previews/` — главные превью 1024×700 и 1600×1100, contact sheets.
- `backgrounds/` — фон 1024×700 и отдельные текстуры graphite / anodized / brushed metal / LCD / recessed control.
- `panels/main/` — header, preset browser, playing core, amp/FX rack, performance strip, keyboard bay, footer.
- `panels/import_guitar/`, `fx_edit/`, `pattern_routing/`, `autochords/`, `settings/`, `skin_gallery/`, `dialogs/` — только реально существующие вспомогательные окна.
- `buttons/` — primary, secondary, navigation, mode, actions, disabled.
- `knobs/main/`, `knobs/fx_edit/`, `knobs/layers/`, `knobs/frames/` — отдельные слои base/rim/face/pointer/scale/glow.
- `switches/`, `leds/`, `displays/`, `meters/`, `keyboard/`, `icons/`, `hardware/`, `sprites/`, `svg/`, `source/` — отдельные производственные компоненты.

## 3. Дизайн-контракт

- Matte graphite / precision anodized metal; минимальное свечение по умолчанию.
- Палитра и реальные runtime IDs берутся из `SKIN/Skin_053/theme.json`; не создавать новые APVTS IDs.
- Главные музыкальные режимы — только MELODY и PATTERN. AUTOCHORDS — вспомогательное окно внутри PATTERN.
- Девять rotary controls и семь главных FX bypass controls остаются строго в утверждённой семантике.
- FLANGER — только группа FX EDIT, не восьмой главный FX-переключатель.
- Динамический текст и числовые значения рисуются JUCE, а не запекаются в PNG.
- Auto Discover, Curator и About сохраняют disabled-семантику, пока их backend не реализован.
- Никаких дополнительных тем: в продукте ровно 16 утверждённых SKIN-1…SKIN-16.

## 4. Что уже есть

- Runtime sprite atlases: controls, meters/sliders, frames/panels, icons, rotary.
- Отдельные PNG control-state ресурсы для всех 27 control IDs и пяти состояний.
- Background, hero, preview, FX material layers, icons, texture и master artwork.
- ThemeManager-compatible SVG texture/bezel/crest и текущий runtime theme manifest.
- 16 утверждённых тем с неизменяемыми именами и stable IDs.

См. полный список существующих runtime-файлов в `../SKIN/Skin_053/assets/asset_manifest.json`. Не считать наличие control-state PNG доказательством, что все 27 изображений уже используются как интерактивные runtime-спрайты: часть отрисовки остаётся native JUCE.

## 5. Что ещё не готово

Полный перечень блокеров — `ASSET_OPEN_ISSUES.md`. В частности, производственный пакет ещё не содержит подтверждённые отдельные экспорты всех панелей и вспомогательных окон, всех отдельных knob layers, всех FX ON/OFF/hover/pressed/disabled вариантов, всех MIDI keyboard states и контактных листов. Отсутствующие файлы нельзя заменять коллажом или фиктивными placeholders.

## 6. Правила пополнения

1. Сначала сверить файл с `Source/PluginEditor.cpp/.h`, `Source/PluginProcessor.cpp`, `theme.json` и утверждённым макетом.
2. Экспортировать PNG RGBA или self-contained SVG без внешних ссылок и активного содержимого.
3. Каждому файлу назначить уникальный `asset_id`, размеры, формат, контроль/состояние и SHA-256.
4. Добавить запись в `ASSET_MANIFEST.json`; отсутствующие или спорные активы фиксировать в `ASSET_OPEN_ISSUES.md`.
5. Обновлять runtime-пути только после проверки совместимости с ThemeManager.
6. Не запускать сборку/CI в рамках текущего этапа без отдельного разрешения.

## 7. Статус

Это подготовленная рабочая структура и индекс, а не заявление о завершении полного production pack или визуальной приёмки по референсу. Главный PNG-макет должен быть доступен для реального визуального сравнения перед pixel-level approval.
