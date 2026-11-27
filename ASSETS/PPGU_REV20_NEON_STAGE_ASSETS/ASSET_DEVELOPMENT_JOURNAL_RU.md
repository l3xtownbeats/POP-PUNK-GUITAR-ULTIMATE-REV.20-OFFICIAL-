# NEON STAGE ASSETS — ЖУРНАЛ РАЗРАБОТКИ

**Проект:** PPGU REV.20  
**Ветка:** `assets/ppgu-rev20-atlas04-display-led-meter-states`  
**PR:** #29 — расширение атласа 04  
**Тема:** SKIN-1 / NEON STAGE DEFAULT / `skin-053`  
**Канонический runtime-пакет:** `SKIN/Skin_053/`  
**Статус:** SOURCE ATLAS VALIDATED + EXPORTED; VISUAL / RUNTIME ACCEPTANCE IN PROGRESS.

## 1. Утверждённая база

1. Визуальный эталон — утверждённые PPGU mockups и актуальный журнал. Исключённый файл `01 INTERFACE  NEON STAGE DEFAULT .png` не использовать.
2. Композиция главного окна: LEFT — Factory Preset Browser; CENTER — Playing Core; RIGHT — AMP & TONE и семь FX-переключателей.
3. Девять регуляторов идут одной горизонтальной строкой: GAIN, TREBLE, MID, BASS, VELOCITY, DYNAMICS, SWING, HUMANIZE, ACCENT.
4. Главных режима ровно два: MELODY и PATTERN. AUTOCHORDS — вспомогательное окно PATTERN.
5. Нижняя зона содержит Performance Display и существующую MIDI-клавиатуру на 49 клавиш.
6. Сохранять 27 стабильных control IDs, девять APVTS-привязок и семь FX bypass-привязок. Не менять DSP, MIDI, значения/диапазоны параметров и runtime-семантику в рамках asset-only работ.
7. Визуальный стиль SKIN-1: графит, анодированный металл, сдержанный cyan/blue accent; динамические значения и состояния остаются под управлением JUCE.
8. Запрещены новые элементы, функции, состояния и подписи, не подтверждённые журналом, макетами и runtime-контрактом.

## 2. Утверждённый состав ASSETS

- Отдельные качественные прозрачные artwork-файлы; SVG — мастер-исходник, PNG — проверенный экспорт.
- Фоны, материалы и 9-slice панели.
- Кнопки и их состояния по каноническому control-state manifest.
- Девять основных rotary-контролов; слои BASE / RIM / FACE / POINTER / SCALE / GLOW.
- Семь FX-переключателей с отдельными OFF/ON состояниями.
- LCD/display artwork и состояния.
- LED artwork и состояния.
- Стерео meter artwork.
- MIDI-клавиатура 49 клавиш (29 белых + 20 чёрных), C/E/G active overlays.
- Иконки и элементы существующего preset browser.
- Экспорт 1×/2×, manifests, размеры, byte counts и SHA-256 для каждого поставляемого файла.

Динамические тексты, числовые значения, реальные LED/метры, MIDI-подсветка и интерактивные hit regions не запекаются в статичную графику.

## 3. Зафиксированные решения

### 2026-11-25 — геометрия
- Девять регуляторов: одна горизонтальная строка вместо старой сетки 3×3.
- Stage/banner выделен в отдельную область.
- Семь FX-переключателей остаются в правой зоне AMP & TONE.
- Визуальные слои не перекрывают интерактивные области.

### 2026-11-26 — источник и качество
- Исключённый корневой PNG не является блокирующим эталоном.
- Пять SVG-атласов используются как дополнительные source masters, не как доказательство полной runtime-интеграции.
- 49-клавишный диапазон подтверждён: 29 white + 20 black.
- Подтверждённые визуальные дефекты и экспортные ограничения должны отражаться в gap list, а не скрываться.

### 2026-11-27 — atlas 04
- `04_ppgu_atlas_displays_keyboard.svg` имеет точный размер **1920×1880**, viewBox `0 0 1920 1880`.
- Добавлены шесть LCD-модулей: ACTIVE, HARMONY, NOTES HELD, NUMERIC, WARNING, ERROR.
- Добавлены семь LED-образцов: OFF, ON, GLOW, WARNING, ERROR, SUCCESS, DISABLED.
- Добавлены три 12-сегментных стерео meter-примера: idle, signal, peak.
- Существующая 49-key keyboard и pitch/mod faders сохранены.
- Обновлены exporter, structural validator и документация.
- Изменение относится к source artwork. Оно само по себе не создаёт runtime mapping и не подтверждает pixel-perfect качество.

## 4. Проверяемое состояние на 2026-11-27

- Ветка PR #29: `5fac4ae532e70e26600ef12764cb008d850df3e7`.
- GitHub Actions run `45944877122`: SUCCESS на точном SHA ветки.
- Job `validate-and-export`: SUCCESS.
- Artifact: `PPGU-NEON-STAGE-SVG-ATLAS-EXPORT`, ID `15174501574`, размер 88,281,866 bytes; срок хранения до 2026-12-11.
- Structural validator подтверждает пять SVG masters, размеры/viewBox, прозрачные холсты, 27 button-family headings, rotary strips, 49-key keyboard, 6 LCD states, 7 LED states, 3 meter states и 41 уникальную иконку.
- Это подтверждает source validation и CI export, но не ручную визуальную приёмку каждого кадра, JUCE mapping, Windows VST3/CTest на новом head, Pluginval или FL Studio 20.


### 2026-11-27 — rotary atlas 03 восстановлен
- При продолжении работ обнаружен дефект: `03_ppgu_atlas_knob_strips.svg` присутствовал в ветке как пустой файл (0 bytes), несмотря на то что structural validator уже требовал три полосы по 61 кадру.
- Файл заполнен самостоятельным SVG-мастером 1920×8000: три визуальных варианта rotary (main, black-disc, knurled-steel), 61 кадр каждый, 128 px pitch, диапазон -135°…+135° с шагом 4.5°? Нет: контракт supplemental atlas validator задаёт 210°…390° с шагом 3°; кадры следуют именно этому контракту.
- Для каждого кадра сохранены неподвижная шкала и отдельный вращаемый указатель; холст прозрачный, подписи и значения не запекаются.
- Новый файл пока имеет статус SOURCE-PRESENT. Structural CI, PNG export, визуальное сравнение с утверждёнными rotary references и runtime mapping ещё не подтверждены.
- Важно: это восстановленный supplemental vector atlas по существующему контракту, а не доказанная 1:1 копия всех предоставленных knob mockups. Для pixel-perfect статуса требуется отдельное визуальное сравнение и корректировки по исходным образцам.

## 5. Открытые задачи

См. единственный актуальный список: `ASSET_OPEN_ISSUES.md`. Ключевые блокеры:
1. Визуальная проверка нового atlas 04 и его отдельных кадров на 100%/200%.
2. Подтверждение размеров, альфа-канала, byte count и SHA-256 отдельных экспортов в manifest.
3. Проверка соответствия каждого asset существующему JUCE consumer; отсутствие выдуманных runtime states.
4. Доведение отдельных production backgrounds/materials и content-rich panel artwork; текущие shell SVG не считать готовыми панелями.
5. FX EDIT-specific rotary layers/scales и полный mapping оставшихся LED/button/keyboard states.
6. Снимки JUCE editor и overlay/difference review при 900×640, 1024×700 и 1600×1100.
7. Exact-head Windows x64 VST3 build, полный CTest, Pluginval и ручная FL Studio 20 host acceptance.

## 6. Правила статусов

- **APPROVED** — решение утверждено пользователем.
- **SOURCE-PRESENT** — исходник присутствует в ветке.
- **CI-VERIFIED** — конкретная проверка прошла на указанном commit SHA.
- **VISUAL-ACCEPTED** — выполнена ручная проверка изображения/кадров по эталону.
- **RUNTIME-INTEGRATED** — подтверждён реальный JUCE consumer и корректное состояние.
- **HOST-VERIFIED** — проверено в FL Studio 20.
- **COMPLETE** — закрыты все применимые gates.

Не повышать статус автоматически. Успешный экспорт не равен визуальной или host-приёмке.
