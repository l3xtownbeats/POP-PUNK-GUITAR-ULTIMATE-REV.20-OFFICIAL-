# NEON STAGE — объединённый план ассетов и интеграции REV.20

Дата аудита: 2026-11-21  
Целевая ветка: `feat/rev20-neon-stage-graphite-magenta-integration`  
PR: #8  
Источник дополнительных материалов: `l3xtownbeats/SKINS-THEME-` (main, tree `85342c038c13a7be52eee58448a4629ecc065236`).

## 1. Неподвижная БАЗА

Единственный визуальный источник истины — утверждённый GitHub master banner NEON STAGE:
- `assets/POP_PUNK_GUITAR_ULTIMATE_BANNER.svg`
- зафиксированный master SHA: `82854d433e3a4183c13fbd6d3c131d565a621f46`
- геометрия 1800×720, viewBox 0 0 1800 720, отношение 5:2.
- мастер-файл не перекрашивать, не деформировать, не обрезать и не заменять.

Все элементы интерфейса и все производные assets должны воспроизводить сам утверждённый макет: композицию, геометрию, пропорции, размеры, иерархию, поверхности, свет и детали. Не создавать альтернативную оболочку, новый GUI или конкурирующий скин.

## 2. Разделение визуального мастер-источника и runtime-палитры

Для runtime default skin-053 использовать утверждённую палитру из `SKIN/Skin_053/theme.json` / текущего theme manifest:
- графит и тёмные панели;
- machined silver;
- purple / magenta / crimson акценты;
- функциональные danger / warning / success цвета.

Не использовать cyan / blue / teal / turquoise как DEFAULT runtime palette. Не переносить в Skin_053 холодную палитру из исходного `SKINS-THEME-/NEON_STAGE_DEFAULT_SKIN_1/ASSET_MANIFEST.json`. Это не разрешение менять master banner: master остаётся неизменным, а runtime assets должны быть согласованы с Skin_053 без нарушения его геометрии и художественной базы.

Основные runtime tokens Skin_053:
```json
{
  "window_bg":"#08090D","panel":"#14161B","panel_elevated":"#20232B",
  "control_bg":"#0E1015","control_face":"#292D36","control_border":"#656B76",
  "text_primary":"#F2F0F4","text_secondary":"#B9B5BF","text_disabled":"#77727D",
  "accent":"#E6007E","accent_glow":"#7B2C91","danger":"#D7264D",
  "warning":"#F2A900","success":"#55C98A","lcd_bg":"#08090D",
  "lcd_text":"#F0DCE8","led_on":"#E6007E","led_off":"#38313B",
  "shadow":"#030305","highlight":"#D9D7DF","lowlight":"#090A0E"
}
```

## 3. Что уже есть в основном REV.20

В целевой ветке уже существует полноценный Skin_053 runtime asset tree, включая:
- `SKIN/Skin_053/theme.json`;
- `SKIN/Skin_053/assets/asset_manifest.json` (манифест сообщает 308 записей);
- `SKIN/Skin_053/assets/artwork_manifest.json`;
- background, textures, FX layers, atlas, controls, control states и связанные runtime resources.

Это основной runtime asset registry. Не создавать второй независимый каталог Skin_053 и не подменять имеющиеся утверждённые файлы необработанными исходниками из второго репозитория.

В REV.20 уже есть единый native editor `Source/PluginEditor.cpp/.h`, ThemeManager, sprite-sheet loader и реальная система управления с APVTS attachments. CMake target уже включает `Source/PluginEditor.cpp`, `Source/UI/ThemeManager.cpp` и `Source/UI/PPGUStageSpriteSheet.cpp`. Отдельный JUCE слой из SKINS-THEME- не следует добавлять параллельно без проверки необходимости: он частично дублирует существующую архитектуру.

## 4. Инвентаризация SKINS-THEME-

Проверен recursive Git tree `85342c038c13a7be52eee58448a4629ecc065236`.

В репозитории есть:
- `NEON_STAGE_DEFAULT_SKIN_1/ASSET_MANIFEST.json`;
- `NEON_STAGE_DEFAULT_SKIN_1/DESIGN_CONTRACT.md`;
- PNG-источники ручек, кнопок, переключателей, рамок/панелей, метров и иконок;
- отдельные изображения Amp/Tone, AutoChords/Fretboard, Console Panel Background, FX Chain Bar, Master Rotary Knob и Piano Keyboard;
- JUCE prototype layer: `PPGUStageLookAndFeel`, `PPGURev20Attachments`, `PPGUStageLayout`, `PPGUAssetManager`, `PPGUSpriteRenderer`, `PPGUKnobAtlas`;
- audit notes по Python prototypes.

Изображения-кандидаты и SHA:
| Назначение | Исходный файл | Git blob SHA |
|---|---|---|
| Amp/Tone module | `Meshy_AI_NeonStage_AmpTone_Module.png` | `087dfb49eba0a037e07585a6bfa6c5022e5662d0` |
| AutoChords/Fretboard | `Meshy_AI_NeonStage_AutoChords_Fretboard.png` | `b3048a05031618f739fbadf80a7c6fee3dd69efd` |
| Console panel background | `Meshy_AI_NeonStage_Console_Panel_Background.png` | `90bb4d9d2aece2b583a24a57962ada66130221b0` |
| FX switch source | `Meshy_AI_NeonStage_FX_Switch_OFF.png` | `3c8baab15145e938770268383200c9323f0f0886` |
| Full FX chain bar | `Meshy_AI_NeonStage_Full_FX_Chain_Bar.png` | `26bc1d80d94316cb21996411cacb85ec41d3fe16` |
| Master rotary knob | `Meshy_AI_NeonStage_Master_Rotary_Knob.png` | `c6f2e1c666e6cabf3d9f3590c5f47f928e81f7e6` |
| Piano keyboard module | `Meshy_AI_NeonStage_Piano_Keyboard_Module.png` | `f2cd738f3ca9fd90622a968a369b6591c62d8fed` |
| Buttons/switches sheet | `Meshy_AI_neon_stage_buttons_and_switches.png` | `4b7c6b2611aedb7e00f3a7d746805be0af3a3be5` |
| Knob/meter sheet | `Meshy_AI_neon_stage_knobs_and_meters.png` | `fd639e613f23d96ede299fbe02011e95b54f00c7` |
| Frames/panels sheet | `Meshy_AI_neon_stage_frames_and_panels.png` | `d7499e74cab2cefa68e6e52fbb7007e0f8230b62` |
| Knob sheet | `Meshy_AI_neon_stage_knobs_sheet.png` | `ba9aafa398a2d65bcb8ee6ad2a223309e11bd138` |
| Meter sheet | `Meshy_AI_neon_stage_meters_sheet.png` | `4363e8e2fb901db0a882740e18e433c03456becc` |
| UI icons sheet | `Meshy_AI_neon_stage_ui_icons_set.png` | `3494a4f2c7be8b5225175d726e933e0f86dde334` |

Повторяющиеся имена с суффиксами (1)/(2) и некоторые `image_*.png` имеют те же blob SHA, что и именованные исходники. Не копировать дубликаты в runtime package.

## 5. Лицензия и визуальный контроль — блокирующие ворота

В исходном manifest все source images имеют `visual_audit_pending` и `license_status: not_verified`; `licensing.redistribution_cleared=false`. В корне SKINS-THEME- нет файла LICENSE (root README — только краткая строка). Права на распространение исходных изображений внутри коммерческого/публично распространяемого VST3 этим аудитом не подтверждены.

Поэтому:
- исходные PNG/JPG/DDS пока не копировать в распространяемый VST3;
- не объявлять artwork production-ready или визуально утверждённым;
- до использования подтвердить автора, происхождение, условия генератора/сервиса и явное право модификации и redistribution/embedding;
- отдельно проверить все изображения визуально против immutable master, размеры, alpha, crop boundaries, atlas grid/frame count и наличие cyan/blue;
- сохранять исходный alpha channel; запрещено удалять фон по яркости, поскольку это может уничтожить металл, тени и отражения;
- только после QA создавать производные Skin_053 assets с согласованной палитрой и фиксировать их SHA/размеры/происхождение в runtime manifest.

## 6. Реальные функции и неизменяемый параметрный контракт

Сохранять только существующие bindings:
| UI | APVTS ID |
|---|---|
| GAIN | `ampGain` |
| TREBLE | `eqHigh` |
| MID | `eqMid` |
| BASS | `eqLow` |
| VELOCITY | `velocity` |
| DYNAMICS | `dynamics` |
| SWING | `swing` |
| HUMANIZE | `humanize` |
| ACCENT | `accent` |

Семь primary FX:
`compressorOn`, `eqOn`, `distortionOn`, `chorusOn`, `delayOn`, `reverbOn`, `cabinetOn`.

Не добавлять восьмой primary FX switch для Flanger: его существующие параметры/интерфейс относятся к auxiliary FX. Не менять APVTS IDs, ranges, defaults, MIDI mapping, DSP, sampler, presets, automation, state serialization, processor или audio callback.

MELODY и PATTERN остаются двумя музыкальными режимами. AutoChords — вспомогательная функция PATTERN, не третий режим.

## 7. Интеграционная карта

| Визуальный участок master | Source artwork candidate | Целевой runtime участок | Статус |
|---|---|---|---|
| Header / console frame | frames & panels sheet; console background | существующий Skin_053 background/panels | candidate only |
| Nine rotary controls | master rotary; knob sheet; knob/meter sheet | существующие 9 SliderAttachment controls | candidate only |
| Seven FX toggles | buttons/switches sheet; FX switch | существующие 7 ButtonAttachment controls | candidate only |
| FX chain strip | Full FX Chain Bar | существующий FX section/editor | candidate only |
| Amp/Tone module | AmpTone Module | существующая native Amp/Tone area | candidate only |
| AutoChords fretboard | AutoChords Fretboard | существующая PATTERN helper area | candidate only |
| Piano keyboard | Piano Keyboard Module | существующая MIDI keyboard area | candidate only |
| Meters / status | meter sheet; UI icons | existing performance/status components | candidate only |

Это карта соответствия, а не утверждение, что изображения уже встроены или что layout из прототипа заменил реальный редактор.

## 8. Правила JUCE/runtime

- Одна VST3, один native PluginEditor, один NEON STAGE.
- Использовать существующие ThemeManager/asset registry/sprite loader; не создавать параллельную систему загрузки без технической необходимости.
- Image decode, JSON parsing, disk I/O и блокирующие locks — только вне audio callback (инициализация/UI thread).
- Audio callback не должен читать файлы, декодировать изображения или ждать mutex.
- Отсутствующий/повреждённый asset должен давать безопасный fallback.
- При неудачной смене темы сохранять last-known-good state.
- Каждый интерактивный визуальный элемент обязан быть реальным JUCE component с существующей функцией/attachment; декоративные assets маркировать decorative-only.
- Для 4K master artwork сохранять 5:2. Экспорт 3840×1536; если нужен холст 3840×2160 — центрировать исходное изображение с полями, не растягивать и не обрезать.

## 9. Что уже изменено этим объединением

Этот документ объединяет:
1. утверждённую NEON STAGE БАЗУ и её immutable master rule;
2. runtime Skin_053 palette;
3. существующий 308-entry runtime asset registry;
4. исходные candidate assets из SKINS-THEME- с blob SHA и назначениями;
5. JUCE prototype findings и безопасные границы интеграции;
6. существующие APVTS/UI contracts;
7. licensing, visual QA и release gates.

Он намеренно НЕ копирует неочищенные source binaries и НЕ заявляет об их подключении к PluginEditor.cpp. Это предотвращает распространение artwork без подтверждённых прав и предотвращает подмену уже существующих runtime assets неподтверждёнными исходниками.

## 10. Следующие обязательные этапы до production

1. Подтвердить права на все конкретные source assets и зафиксировать evidence.
2. Провести визуальную инспекцию оригинальных PNG/DDS и сравнить с master banner.
3. Выбрать только подходящие исходники, устранить дубликаты, проверить alpha/размеры/atlas geometry.
4. Создать согласованные Skin_053 runtime derivatives, не меняя immutable master.
5. Подключить их к существующим native components и существующей asset pipeline.
6. Запустить Windows x64 build, CTest, pluginval и ручную проверку в FL Studio 20 x64.
7. Только после всех обязательных проверок снимать Draft и рассматривать merge.

## 11. Проверки PR на момент аудита

Для HEAD `b65ec5c4dad716e470d116a9977cb5595841b464` GitHub check-runs `windows-x64` вернули `completed / success` для двух job records. Это относится только к этому HEAD и не заменяет отдельные visual artwork audit, redistribution clearance, pluginval или FL Studio 20 acceptance. После нового commit CI должен быть запущен повторно.
