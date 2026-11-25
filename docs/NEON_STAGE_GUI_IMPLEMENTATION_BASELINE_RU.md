# NEON STAGE DEFAULT — базовый контракт графического интерфейса REV.20

Статус: implementation baseline / не является подтверждением готовности UI.

## Источники истины
- `Source/PluginEditor.cpp` — фактическая JUCE-компоновка и привязки компонентов.
- `SKIN/Skin_053/theme.json` — идентификатор, палитра, типографика, материалы и карта ассетов.
- `Info.txt` и журнал разработки — ограничения релиза и статус функций.

При расхождении макета с этими источниками не добавлять элементы из макета: сначала уточнить спецификацию в журнале.

## Утверждённая оболочка
Главное окно — JUCE AudioProcessorEditor, стартовый размер 1024×700, изменение размера включено, границы 900×640 — 1600×1100.

Композиция:
1. Верхняя строка управления — 48 px.
2. Рабочая область — три зоны: слева браузер пресетов, в центре Playing Core, справа AMP & TONE / FX.
3. Нижняя полоса производительности — 132 px: статус, Performance Display и MIDI-клавиатура.
4. Внутренние отступы оболочки — 14 px; промежутки между зонами — 10 px.

## Левая зона — PRESETS
Сохранять существующие компоненты и порядок:
- фильтр категорий: ALL PRESETS / MELODY / PATTERN;
- SEARCH PRESETS;
- каталог FACTORY PRESET CATALOG;
- chord reference показывается только в PATTERN-режиме.
Поиск и фильтрация не должны незаметно загружать другой пресет.

## Центральная зона — PLAYING CORE
Верхняя строка содержит MELODY, PATTERN, существующий mode selector и start-mode selector.
Ниже — ровно девять действующих APVTS-регуляторов в сетке 3×3.
Не менять идентификаторы, порядок, параметрические связи, значения и поведение регуляторов ради оформления.

## Правая зона — AMP & TONE
- Существующий заголовок AMP & TONE.
- Существующий заголовок FX.
- Ровно семь существующих FX-переключателей.
Не добавлять усилители, кабинеты, эффекты или дополнительные органы управления, если они не описаны в runtime-контракте.

## Верхняя строка
Сохранять существующие действия и их доступность: PPGU / L3XTOWN AUDIO LAB, LOAD / Import Guitar, AUTO CHORDS, AUTO SOUND HUNTER, CURATOR, SETTINGS, ABOUT, SKIN.
AUTO SOUND HUNTER и CURATOR остаются disabled, пока backend не реализован. Не имитировать их работоспособность.

## Нижняя полоса
- Status label;
- Performance Display;
- существующая MIDI-клавиатура (49 клавиш).
Не добавлять транспорт, секвенсор, waveform editor или другие неподтверждённые элементы.

## Визуальная система SKIN-1
Источник: `SKIN/Skin_053/theme.json`.

Палитра:
- window_bg #080B14; panel #101827; panel_elevated #17243A;
- control_bg #0C1422; control_face #1A2940; control_border #31506F;
- text_primary #F4F7FF; text_secondary #B5C4DC;
- accent #00D9FF; accent_glow #6B8CFF;
- lcd_bg #050D1B; lcd_text #8DEBFF;
- led_on #00E5FF; led_off #263B55.

Типографика: Segoe UI / Consolas, scale 1.0, letter spacing 0.35.
Материалы: матовый графит и точный анодированный металл.
Glow: opt-in; в минимальном режиме по умолчанию выключен.
Eco mode: учитывать reduceInEco=true.

## Инженерные ограничения
- Не менять DSP, Sample Engine, MIDI routing, APVTS IDs или preset semantics.
- Не подменять реальные JUCE-компоненты декоративной графикой.
- Artwork рисуется под/вокруг интерактивных компонентов и не перекрывает hit regions.
- Использовать предусмотренные theme artwork layers и asset manifest.
- Не добавлять UI-функции, которых нет в журнале и runtime-контракте.

## Критерии приёмки следующего UI-прохода
1. Windows x64 VST3 собирается без новых ошибок.
2. Существующие тесты параметров и полный CTest проходят.
3. Layout проверен на 900×640, 1024×700 и 1600×1100.
4. Проверены видимость всех контролов и отсутствие перекрытий.
5. Проверены MELODY/PATTERN и PATTERN-only chord reference.
6. Проверены disabled-состояния AUTO SOUND HUNTER и CURATOR.
7. Проверено переключение SKIN-1 и Eco mode.
8. Pluginval проходит; затем требуется ручное host acceptance в FL Studio 20.

До прохождения проверок статус остаётся IN PROGRESS.


## 2026-11-25 — дополнительно предоставленные визуальные эталоны PPGU

Получены и непосредственно просмотрены два пользовательских изображения (1536×1024, RGBA):
- `Неоновый интерфейс гитарного плагина PPGU.png`, SHA-256 `83964d6e8316c0c3deef7dd7217492b396e36ed3ae448e1b6659ba1904207a26`.
- `Неоновый атлас UI‑ассетов PPGU.png`, SHA-256 `0ad003b6cfb4d7d8d0f219ca12ef9a49627f5f221a07d46999b0578772e71e99`.

Первое изображение задаёт визуальный ориентир для единой PPGU-оболочки и видимых вспомогательных рабочих областей:
- верхняя панель бренда и действий;
- браузер Factory Preset Catalog с фильтрами ALL PRESETS / MELODY / PATTERN и поиском;
- центральный гитарный баннер и переключение MELODY / PATTERN;
- девять регуляторов с подписями GAIN, TREBLE, MID, BASS, VELOCITY, DYNAMICS, SWING, HUMANIZE, ACCENT;
- AMP & TONE и семь FX-переключателей;
- LIVE HARMONY / CHORD / SCALE-KEY / NOTES HELD;
- MIDI-клавиатура и статус библиотеки;
- вспомогательные области NEON STAGE / FX EDIT, AUTOCHORDS / HARMONY SETUP и LICENSED GUITAR LIBRARY / IMPORT GUITAR.

Второе изображение — визуальный атлас из 12 групп: backgrounds/materials; 9-slice frames; button states; семь FX switches; rotary knob layers; FX EDIT rotary family; toggles/power/LED states; display elements; MIDI keyboard; consistent icon family; hardware details; sprite-sheet examples. Это полный перечень групп для визуального аудита, а не утверждение, что каждый показанный спрайт уже подключён к renderer.

### Обязательная сверка перед изменением геометрии

Обнаружено одно явное расхождение между новым главным изображением и ранее зафиксированным implementation baseline:
- новый скриншот визуально показывает девять регуляторов одной горизонтальной полосой под гитарным баннером;
- текущий baseline и `PluginEditor.cpp::resized()` задают девять регуляторов сеткой 3×3 в центральной зоне.

Не менять APVTS IDs, порядок, значения или DSP. Не менять геометрию регуляторов вслепую: горизонтальная полоса из нового изображения и сетка 3×3 из прежнего контракта требуют явного разрешения в журнале разработки. До разрешения продолжать безопасную сверку ассетов, материалов, рамок, состояний и оформления вспомогательных панелей.

Вспомогательные панели на референсе показаны одновременно как визуальная композиция. Runtime-контракт REV.20 описывает AutoChords, FX EDIT и Import Guitar как вспомогательные окна/workspace, а не новые главные режимы. Не превращать их в отдельные top-level modes и не выдавать setup-only AutoChords за подключённый preview/playback engine.

Статус: reference received and inspected; implementation alignment in progress; pixel comparison, responsive layout verification and FL Studio 20 host acceptance remain open.


## 2026-11-25 — решение по компоновке девяти регуляторов

Пользователь подтвердил, что новый визуальный референс с девятью регуляторами в одной горизонтальной полосе заменяет прежнее требование сетки 3×3. Геометрия `PluginEditor.cpp::resized()` обновлена: девять реальных APVTS-регуляторов размещаются в одной равномерной горизонтальной строке; подписи находятся под регуляторами. Размеры адаптируются к доступной ширине редактора.

Изменена только компоновка UI. APVTS IDs, порядок массива регуляторов, attachments, диапазоны, значения параметров, DSP и MIDI-контракты не менялись. Требуется подтвердить визуальную компоновку сборкой и проверкой на минимальном/стандартном/максимальном размерах, затем в FL Studio 20.

Реализация: commit `9c1b214b8a2dcec06cb68fdcf3b1f04039dfaae1`. Статус: source change committed; build/CTest/host verification pending.


## 2026-11-25 — main-screen layout alignment pass 2

После подтверждения горизонтального ряда девяти регуляторов внесён следующий source-backed layout pass:
- выделена отдельная верхняя stage/banner-зона для существующего `Palette::heroArtwork`; изображение больше не растягивается полупрозрачным фоном за всей зоной регуляторов;
- девять существующих APVTS-регуляторов остаются одной горизонтальной строкой под stage/banner;
- семь существующих FX bypass-кнопок размещены горизонтальной цепочкой, каждая сохраняет прежний APVTS attachment и ID;
- stage/banner — декоративный слой и не перекрывает hit-targets контролов;
- высота banner рассчитывается согласованно в `paint()` и `resized()`, с ограничением для компактного окна.

Не добавлялись фиктивные AMP-контролы, новые эффекты, AutoChords generation или несуществующие backend-функции. AMP & TONE в runtime пока представлен заголовком/визуальной зоной; полноценная amp image/control parity остаётся отдельным gap, пока не найден подтверждённый runtime asset/parameter contract. LIVE HARMONY / CHORD / SCALE-KEY / NOTES HELD отображаются существующим read-only Performance Display; никакие новые MIDI/scale writes не добавлялись.

Source commits: `954c1d9cf9970c4a0bf524d3c4dfd8c09c00bc1a` (stage/banner + horizontal FX chain), `bd7ecb2bdb5c150e85d54df894f8ca9ec2f25089` (paint/layout stage geometry sync). Build, CTest, screenshots at 900×640 / 1024×700 / 1600×1100, package asset validation and FL Studio 20 acceptance remain pending.


## 2026-11-25 — три вспомогательные панели в одной строке

Согласно новому визуальному эталону, расширен алгоритм `AuxiliaryPanelLayout`: он рассматривает до трёх колонок вместо максимум двух, чтобы FX EDIT, AutoChords и Import Guitar могли отображаться рядом при достаточной ширине workspace. Обновлены `tests/AuxiliaryPanelLayoutTests.cpp` и `PPGUMultiWindowWorkspace_README_RU.md`. Изменения не затрагивают DSP/APVTS/MIDI. Коммиты: `3817616`, `e7574d6`, `a00130b`. CI/CTest на новом SHA ожидают проверки.


## 2026-11-25 — техническая чистка workspace window

Проверена оболочка вспомогательных окон: theme palette, текстуры/рамка, frames/panels atlas, заголовок, close/maximize, resize grip и content bounds уже поддерживаются. Удалены дублирующиеся назначения цветов closeButton. Коммит `aa75ce2814f77bcdf38b06499ba98d3ccaa7be91`. Изменение не меняет внешний вид, геометрию или runtime-контракты. Проверки после изменения ожидают выполнения.


## 2026-11-25 — FX EDIT: telemetry-gated response display

The FX EDIT graph remains intentionally read-only and does not draw an invented response curve. Its caption now identifies the area as DSP response telemetry, and the empty-state message states that the processor does not yet expose this feed. The selected-effect status reports ACTIVE/BYPASSED plus the actual count of APVTS controls in the selected group. No parameter IDs, attachments, DSP, MIDI or audio-thread behavior changed. Exact-SHA build and runtime validation remain required.


## 2026-11-25 — AutoChords: no fabricated guitar fingering

The chord diagram no longer starts with a hard-coded A-major shape that could be mistaken for the currently selected harmony. It now displays an explicit “NO VERIFIED GUITAR VOICING DATA” state until a real voicing is passed to setVoicing. The renderer still supports drawing supplied six-string positions. This is a UI truthfulness correction only; chord generation, APVTS, MIDI and DSP are unchanged. A verified fingering database and musical validation remain outstanding.


## 2026-11-25 — Import Guitar: truthful SFZ diagnostics

The Import Guitar completion panel now displays the selected SFZ filename, actual LoadReport region/sample totals, warning/error counts, and up to three messages from each non-empty diagnostics list. It labels the selection as one SFZ definition rather than claiming an inferred instrument count. The asynchronous loader and sampler behavior are unchanged; no synthetic progress or filesystem-derived WAV count was introduced. Build and runtime layout validation remain outstanding.


The async completion captures the selected file by value before the chooser callback exits, ensuring the displayed filename is valid for the deferred completion callback. Follow-up source commit: 0642e82c860ccc7e9165f8c62a9b37e9fbe31dce.


## 2026-11-25 — Settings and Performance: NEON STAGE polish

The Performance Display now includes a live held-MIDI-note count alongside the chord, scale/key and note-name readouts. It is computed from the processor's existing lock-free display snapshot, using the established 20 Hz UI timer; it does not write MIDI/APVTS state or add audio-thread work. Workspace Settings now draws theme-aware elevated cards and accent framing behind the existing scale, spacing, restore-default and skin-gallery controls. Settings ranges and callbacks are unchanged. Exact-head build and runtime validation are still required.



## 2026-11-25 — VU meter: authored atlas states wired to runtime

The live stereo output meter now uses the eight authored VU states in the NEON STAGE meters/sliders sprite atlas when Skin-1 is active. It selects the nearest of eight artwork states from the real post-output peak level and crops the manifest-defined 82×286 px cells (x=43+117*n, y=34). Zero level and the other 15 themes continue to use the existing semantic vector meter, preserving cross-skin behavior. Peak acquisition remains the processor's lock-free UI snapshot; no audio/DSP behavior changed. A built-plugin visual check is still required.


## 2026-11-26 — SFZ import status LED uses authored atlas

The Import Guitar panel's real asynchronous loader indicator now uses the authored round status-LED cells from the NEON STAGE meters/sliders atlas when Skin-1 is active: OFF for standby, blue for loading, cyan for ready, warning for error. Cells are 40×40 at y=810 and x=50/160/270/380, per the sprite-sheet manifest. Text status remains visible; other themes and missing-atlas cases retain the semantic vector LED fallback. The indicator reflects the existing loader state and does not invent progress.


## 2026-11-26 — 16-theme validation gate corrected without false readiness

The previous Windows validation failure was traced: all 26 CTest cases passed, but the registry validator demanded 16 runtimeReady=true entries even though STILLWATER (skin-111) is intentionally gated pending FL Studio 20 host acceptance. The validator now checks all 16 approved theme slots and validates their required artwork/SVG packages, while requiring 15 runtime-ready themes and exactly one explicitly gated STILLWATER slot. The registry status now says its embedded artwork package is validated and FL Studio 20 host acceptance remains pending. runtimeReady remains false; no acceptance was fabricated. This does not waive any visual/runtime host test.


## 2026-11-26 — NEON STAGE: подключение atlas folder/power icons
- Сверены реальные координаты иконок со `neon_stage_spritesheet_manifest.json` (144×144): `power` [360,360,504,504] и `folder` [852,360,996,504]. Эти два ранее неиспользованных кадра подключены к существующим кнопкам FX EDIT POWER и LOAD SFZ в окне Licensed Guitar Library.
- Для кнопок заданы стабильные component IDs `FX_Edit_Power` и `Import_Guitar_Load`; отрисовка остаётся внутри существующих bounds и не меняет hit targets, callbacks, APVTS, DSP, MIDI или загрузчик SFZ.
- Также расширена таблица runtime-координат атласа оставшимися документированными кадрами `search` и `play`; новые функции/кнопки не добавлялись, пока для них нет соответствующих подтверждённых действий в текущем интерфейсе.
- Проверка сборкой/CTest и визуальный снимок после запуска ещё не выполнены для нового commit. FL Studio 20 host acceptance остаётся отдельным gate.


## 2026-11-26 — NEON STAGE: иконка поиска в каталоге пресетов
- Подключён кадр `search` из утверждённого `neon_stage_icons_sheet.png` по координатам manifest [32,645,176,789] (144×144) к существующему полю `SEARCH PRESETS...`.
- Рендер выполняется в `fillTextEditorBackground()` только для стабильного component ID `Preset_Search`; левый текстовый отступ 28 px резервирует место для значка, не перекрывая текст, каретку и ввод. При отсутствии atlas используется штатный вид поля без ошибки.
- Не добавлялись новые компоненты/действия; фильтрация, поиск, callbacks и данные каталога не менялись. Визуальная проверка нового поля после запуска и CI для нового commit ещё ожидаются.
