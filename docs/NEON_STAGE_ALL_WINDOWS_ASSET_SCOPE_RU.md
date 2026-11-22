# NEON STAGE DEFAULT — полный визуальный охват всех окон REV.20

**Статус:** обязательный production scope / работа продолжается  
**Канонический источник решений:** `Info.txt`  
**Детальная спецификация графики:** `PPGU_REV20_NEON_STAGE_DEFAULT_ULTIMATE_ASSET_MASTER_PROMPT_RU.txt`  
**Главный визуальный эталон:** `01 INTERFACE  NEON STAGE DEFAULT .png`  
**Дополнительные эталоны:** макеты 02–07; каждый относится к своему окну/состоянию, а не к отдельной теме.  
**Активная оболочка:** SKIN-1 / NEON STAGE DEFAULT / `skin-053`.

## 1. Обязательный порядок приоритетов

1. Макеты 01–07 определяют композицию, размеры, геометрию, пропорции, материалы, свет, типографику и визуальную иерархию.
2. `Info.txt`, `PluginEditor.cpp/.h`, `PluginProcessor.cpp` определяют фактические функции, контролы и состояния. Визуал не должен обещать несуществующую функцию.
3. `theme.json`, control-state manifest и runtime manifests задают palette, control IDs, ресурсные пути и совместимость.
4. При конфликте — зафиксировать его в `ASSET_OPEN_ISSUES.md`; не решать самовольно редизайном.

## 2. Общий визуальный контракт

- SKIN-1: graphite `#080B14`, panel `#101827`, elevated `#17243A`, cyan `#00D9FF`, electric blue `#6B8CFF`.
- Никаких фиолетовых, пурпурных или magenta акцентов в SKIN-1.
- Материалы: matte graphite, precision anodized metal, restrained brushed metal, controlled bevels/specular/shadow/glow.
- UI font: Segoe UI semibold; технические значения: Consolas.
- Default lighting: MINIMAL. Glow — только для реального hover/focus/active/status.
- Динамические подписи, значения, preset names, status и meter readings рисуются живым JUCE text/value layer, а не запекаются в PNG.
- PNG RGBA — единственный формат production artwork: отдельные прозрачные PNG для каждой панели, аппаратной детали, иконки, ручки, переключателя и состояния; master не менее 4× относительно эталона 1024×700 для крупных панелей/деталей, runtime-варианты 1x/2x/3x, manifest с semantic ID, точными размерами, alpha, state, scale, master relationship и SHA-256. SVG запрещён как production master, промежуточный render source и runtime asset. Существующие SVG и SVG-derived PNG — только legacy placeholders; не засчитывать их как финальный визуал.
- Не использовать generic prototype atlases, старые цветовые палитры, случайные sci-fi HUD, fake meters или placeholder artwork как финальный ресурс.

## 3. Главное окно — reference 01

| Зона | Обязательные элементы | Реальные ограничения |
|---|---|---|
| Header | PPGU wordmark, L3XTOWN AUDIO LAB, IMPORT GUITAR, AUTOCHORDS, SETTINGS, SKIN, ABOUT | AUTO SOUND HUNTER/CURATOR не показывать, пока не реализованы; ABOUT disabled |
| Left Browser | FACTORY PRESET CATALOG, ALL PRESETS/MELODY/PATTERN, SEARCH PRESETS, список | Не выдавать частичный каталог за 500 playable presets |
| Center Playing Core | Guitar hero artwork, ровно MELODY/PATTERN, живые значения и девять существующих rotary bindings | Не вводить PUNK GROUP или третью mode |
| AMP & TONE | amp cabinet artwork; GAIN/TREBLE/MID/BASS | Четыре существующих параметра, без декоративных ручек |
| Performance strip | VELOCITY/DYNAMICS/SWING/HUMANIZE/ACCENT | Пять существующих APVTS bindings; никаких fake CPU/RAM |
| FX Chain | COMPRESSOR, EQ, DISTORTION, CHORUS, DELAY, REVERB, CABINET IR | Ровно семь main switches; FLANGER только в FX EDIT |
| Footer | MIDI keyboard 36–84 (49 keys), library/status text, существующий sync selector | sync_selector — служебная совместимость, не 28-й user control |

### Девять главных rotary controls

`GAIN/ampGain`, `TREBLE/eqHigh`, `MID/eqMid`, `BASS/eqLow`, `VELOCITY/velocity`, `DYNAMICS/dynamics`, `SWING/swing`, `HUMANIZE/humanize`, `ACCENT/accent`.

### Семь главных FX switches

`COMPRESSOR/compressorOn`, `EQ/eqOn`, `DISTORTION/distortionOn`, `CHORUS/chorusOn`, `DELAY/delayOn`, `REVERB/reverbOn`, `CABINET IR/cabinetOn`.

## 4. Все существующие вспомогательные окна

| Окно / модуль | Обязательная графика и UI | Состояние/ограничения |
|---|---|---|
| IMPORT GUITAR / LICENSED GUITAR LIBRARY | Заголовок, SFZ/WAV information surface, LOAD SFZ, status plate | Только существующий SFZ file-load workflow; idle/loading/success/warning/error; не рисовать Folder/ZIP/Mapping Editor как доступные функции |
| FX EDIT | Effect selector, POWER, PROCESS RESPONSE / VISUAL GUIDE, APVTS status, rotary controls | Восемь групп: Compressor, EQ, Distortion, Chorus, Flanger, Delay, Reverb, Cabinet IR; граф — visual guide, не fake spectrum |
| PATTERN / SONG SECTION ROUTING | SONG SECTION, RHYTHM CATALOG, status, PREVIEW/APPLY/CANCEL | INTRO/VERSE/CHORUS/BRIDGE/OUTRO; Pattern 1–8; не рисовать waveform/timeline без реализации |
| AUTOCHORDS / HARMONY SETUP | KEY, SCALE/QUALITY, RHYTHM PATTERN SLOT, state notice, AUTOCHORDS OFF | Setup-only до подключения MIDI chord generation/custom mode/preview engine; generator button disabled |
| WORKSPACE SETTINGS | Auxiliary panel scale, spacing, restore default, open gallery | Scale 0.5x–1.5x; gap 0–32 px |
| VISUAL SKIN GALLERY | Search, ALL SKINS/FAVORITES ONLY, count, 16 cards, preview/favorite/apply/cancel | Ровно 16 утверждённых оболочек и stable IDs |
| ABOUT | Кнопка/disabled state | Не открывать фальшивое окно; остаётся disabled, пока утверждённый About module не реализован |

## 5. Control artwork / состояния

Закрытый список — 27 пользовательских control IDs из `theme.json` и control-state manifest. Служебный `sync_selector` не добавляет 28-й control.

Для каждого элемента подготовить независимые RGBA ресурсы и runtime mapping для состояний NORMAL, HOVER, PRESSED, ACTIVE/ON, DISABLED, FOCUS, где эти состояния применимы. Существующие `dragged` PNG не считать автоматически эквивалентом ACTIVE или FOCUS. Динамический текст остаётся live text. Для семи FX — независимые ON/OFF artwork plus hover/pressed/disabled. Для rotary — корпус/rim/face/pointer/scale/glow как отдельные слои либо проверенная геометрически корректная анимация; не использовать низкокачественный quantized atlas как замену.

## 6. Asset groups, которые должны быть отдельно доступны

- Background/materials: main graphite surface, graphite texture, anodized/brushed metal, LCD dark, recessed control surface.
- Main frames: header, Browser, Playing Core, Amp & Tone rack, Performance strip, FX chain, MIDI bay, footer/status.
- Auxiliary frames: Import Guitar, FX Edit, Pattern Routing, AutoChords, Settings, Skin Gallery, dialog base/warning/error.
- Buttons: primary/secondary, import/load, mode, AutoChords, settings, skin gallery, preview/apply/cancel/favorite/restore, power, disabled-feature.
- FX switches: семь независимых effect IDs, ON/OFF states.
- Main knobs: девять независимых IDs, layered hardware parts.
- FX EDIT knobs: parameter-family variants for frequency/time/ratio/threshold/mix/drive/rate/depth/feedback/room/damping/cutoff.
- Indicators: LCD/LED artwork only when tied to a real runtime state; no decorative/fake telemetry.
- Keyboard: separate white/black key artwork, separators, hover and pressed overlays.

## 7. Реализация и проверки

- UI artwork decode/cache/paint только на UI/message thread; никаких файловых операций, GPU resource creation, blocking, allocations или image decoding в audio callback.
- GPU/native renderer must preserve fallback and pass Windows 10 x64 / FL Studio 20 x64 host review.
- Every auxiliary panel keeps stable PanelId, close/maximize/restore/resize behavior, safe bounds, DPI scaling and lifetime ownership.
- Verify all modules at 100%, 125%, 150% DPI; compare main window to reference 01 and auxiliary windows to 02–07.
- Run exact-SHA Windows VST3 build, full CTest, asset audit, pluginval strictness 5; then manual FL Studio 20 acceptance.
- Do not declare artwork complete from file presence alone. Record exact asset hash, dimensions, alpha, visual review and reference match.

## 8. Explicitly excluded from this UI pass

No changes to DSP, sampler, MIDI scheduler, APVTS IDs/ranges, 500-preset content, SoundBank, audio callback or library source files. No invented controls, third main mode, eighth FX switch, fake CPU/RAM, false chord generation, fake preset totals, waveform/timeline, or unfinished Auto Sound Hunter/Curator panels.


## 9. PNG-only precedence and reference set (user reaffirmed 2026-11-22)

- The current user-approved lock `docs/NEON_STAGE_PNG_ONLY_AND_PATTERN_WORKSPACE_LOCK_RU.md` takes precedence over any older sentence in this document that allowed SVG under an earlier runtime contract.
- Visual authority is the exact seven-image set in the REV.20 repository: `01 INTERFACE  NEON STAGE DEFAULT .png`, `02 INTERFACE  NEON STAGE DEFAULT AUTOCHORDS.png`, and `03` through `07 INTERFACE  NEON STAGE DEFAULT .png`. Reference 01 governs the main editor composition; 02–07 govern their respective auxiliary/workspace views and states. Do not replace or reinterpret them as separate themes.
- Supporting materials in `Assets/3D/References/`, the canonical theme `SKIN/Skin_053/theme.json`, the accepted baseline, current `PluginEditor.cpp/.h`, processor bindings and the master asset prompt remain mandatory cross-checks. Where references and real functionality conflict, record the issue in `ASSET_OPEN_ISSUES.md`; never depict unavailable functions as working.
- This clarification is a documentation/authority correction only. It does not claim that the production PNG library has been authored, visually matched, integrated, or accepted in FL Studio 20.
