# Миграция REV.20 на JUCE 9.0.6, C++23 и экспериментальный C++26

**Дата обновления:** 2026-11-27  
**Канонический репозиторий:** `l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-`  
**Каноническая база:** `main`  
**Рабочая review-ветка:** `upgrade/juce-9.0.6-cpp23-cpp26-evaluation`  
**Pull request:** [#31 — JUCE 9.0.6 / C++23 production / C++26 evaluation](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/pull/31)

## 1. Целевая конфигурация

| Слой | Основная конфигурация | Эксперимент |
|---|---|---|
| Framework | JUCE **9.0.6**, pinned tag `9.0.6` | тот же JUCE |
| Язык | **C++23** — production baseline | **C++26 latest/draft mode** |
| CMake | 3.30+ | 3.30+ |
| Compiler CI | Visual Studio 2026 / MSVC 14.52 | тот же toolchain, `/std:c++latest` |
| Target | Windows 10 x64 / VST3 x64 | Windows x64 / VST3 compatibility |
| Host acceptance | FL Studio 20 x64 | требуется та же ручная проверка |

C++23 является обязательной производственной конфигурацией. C++26 не подменяет C++23 и не объявляется полностью реализованным стандартом: экспериментальный режим использует наиболее свежий language mode компилятора.

## 2. Реализованные изменения в ветке

1. JUCE закреплён на официальном релизном теге **9.0.6** в Windows build workflows.
2. CMake использует **C++23** по умолчанию и принимает только явно выбранные режимы 23 или 26.
3. Для MSVC в режиме 26 CMake оставляет собственные compiler-identification / `try_compile` проверки на поддерживаемом диалекте C++23, а реальные C++ translation units получают `/std:c++latest`. Это устраняет ранний отказ JUCE CMake probe на неизвестном CXX26 dialect. Для других компиляторов используется нативный CMake CXX26 mode.
4. C++26 остаётся отдельной non-blocking compatibility job; C++23 остаётся production gate.
5. Мигрированы два вызова удалённого JUCE 7 API `Drawable::createFromSVG(XmlElement)` на JUCE 9 `Drawable::createFromSVGString`, с сохранением предварительной проверки и SVG sanitization.
6. README, навигация и верхний блок репозитория приведены к REV.20: pinned JUCE, стандарты C++, approved NEON STAGE reference, канонический журнал и ссылки на требования/проверки.
7. В журнал добавляется запись о ветке и о статусе C++26 probe; main не изменяется напрямую.

## 3. Проверка C++26 и исправление

Первый экспериментальный запуск на SHA `e5166695b0543478a8c5b7e57ea131bf8411b5b7` завершился на этапе CMake configure. Лог показал, что JUCE architecture probe запрашивал dialect `CXX26`, который CMake/MSVC 19.52 не распознавал. Это был отказ конфигурации, а не ошибка исходного C++ кода.

В текущем обновлении `CMakeLists.txt` изменён на MSVC-specific latest mode (`/std:c++latest`) с сохранением CMake configure checks на C++23. Повторная exact-SHA CI проверка обязательна; успешный результат пока не заявляется.

## 4. NEON STAGE — обязательный визуальный контракт

Визуальные источники — хранящаяся коллекция [основного макета PPGU](../Неоновый%20интерфейс%20PPGU%20%E2%80%94%20поп-панк%20гитара.png), [макета гитарного плагина](../Неоновый%20интерфейс%20гитарного%20плагина%20PPGU.png), [атласа UI-ассетов](../Неоновый%20атлас%20UI%E2%80%91ассетов%20PPGU.png), [полного asset master prompt](../Assets/3D/References/PPGU_REV20_NEON_STAGE_DEFAULT_ULTIMATE_ASSET_MASTER_PROMPT_RU.txt), утверждённый журнал `Info.txt` и [NEON STAGE GUI implementation baseline](NEON_STAGE_GUI_IMPLEMENTATION_BASELINE_RU.md). Отдельный repository-root файл `01 INTERFACE  NEON STAGE DEFAULT .png` явно исключён реестром открытых asset issues и не используется как эталон. Для визуальной реализации обязательны следующие решения:

- Ровно два главных режима: MELODY и PATTERN. AUTOCHORDS — только вспомогательное окно PATTERN.
- Главная композиция: header / left preset browser / center Playing Core / right AMP & TONE / lower performance strip.
- Девять реальных APVTS-регуляторов — **одна горизонтальная строка**, порядок: GAIN, TREBLE, MID, BASS, VELOCITY, DYNAMICS, SWING, HUMANIZE, ACCENT. Решение от 2026-11-25 заменило прежнюю сетку 3×3.
- Семь основных FX-переключателей: COMPRESSOR, EQ, DISTORTION, CHORUS, DELAY, REVERB, CABINET IR. FLANGER — только внутри FX EDIT.
- Нижняя зона: live performance display, MIDI keyboard 49 keys (MIDI 36–84), реальный library status.
- AUTO SOUND HUNTER, CURATOR и ABOUT визуально disabled до появления настоящих backend-функций.
- Не добавлять фальшивые CPU/RAM метры, псевдо-анализатор, вымышленные preset counts или декоративные неработающие контролы.
- Сохранить все 27 утверждённых user-facing control IDs, семь FX bypass APVTS IDs, значения параметров и hit targets.

Текущий `PluginEditor.cpp::resized()` уже размещает девять APVTS-регуляторов горизонтально, выделяет stage/banner, сохраняет семь FX attachments и три зоны. В рамках этой документационной/технологической синхронизации геометрия не переписывалась заново, чтобы не нарушить принятый layout. Pixel parity по мастер-макету всё ещё требует проверки реальных UI snapshots и ручной оценки.

## 5. Навигация и визуальные источники

- [Главная страница проекта](../README.md)\n- [Основной сохранённый макет PPGU](../Неоновый%20интерфейс%20PPGU%20%E2%80%94%20поп-панк%20гитара.png)\n- [Атлас UI-ассетов](../Неоновый%20атлас%20UI%E2%80%91ассетов%20PPGU.png)\n- [Asset master prompt](../Assets/3D/References/PPGU_REV20_NEON_STAGE_DEFAULT_ULTIMATE_ASSET_MASTER_PROMPT_RU.txt)
- [Единый журнал](../Info.txt)
- [Утверждённая база продукта](REV20_ACCEPTED_BASELINE_RU.md)
- [Хронология решений](REV20_DECISION_TIMELINE_RU.md)
- [NEON STAGE GUI baseline](NEON_STAGE_GUI_IMPLEMENTATION_BASELINE_RU.md)
- [UI baseline](../Docs/REV20_UI_BASELINE.md)
- [Skin approval standard](REV20_SKIN_APPROVAL_STANDARD_RU.md)
- [NEON STAGE asset pack](../ASSETS/PPGU_REV20_NEON_STAGE_ASSETS/README_ASSET_PACK_RU.md)
- [FL Studio 20 host checklist](REV20_FL20_ACCEPTANCE_CHECKLIST_RU.md)
- [Windows VST3 validation workflow](../.github/workflows/rev20-windows-vst3-skin-validation.yml)
- [CMake configuration](../CMakeLists.txt)

## 6. Обязательные gates завершения

- [ ] C++23 exact-SHA Windows x64 configure/build — PASS.
- [ ] Полный CTest — PASS.
- [ ] Все 16 skin registry/assets validation — PASS.
- [ ] VST3 package staging — PASS.
- [ ] pluginval strictness 5 — PASS.
- [ ] C++26 latest-mode configure/build/CTest — результат зафиксирован; если не поддерживается — точное ограничение описано, C++23 остаётся production.
- [ ] Проверены WAV, AIFF, MP3 и SFZ decode/streaming на реальных fixtures.
- [ ] Проверены MIDI, PATTERN, AutoChords, state persistence, UI snapshots и 100/125/150% DPI.
- [ ] FL Studio 20 x64 host acceptance на Windows 10 x64 — PASS.
- [ ] Проверена модель лицензирования JUCE для планируемой дистрибуции.

## 7. Текущий статус

**MIGRATION ACTIVE — NOT VERIFIED.** JUCE 9.0.6 и C++23 внесены в review-ветку. Исправление C++26 CMake probe внесено, но его повторный exact-SHA запуск ещё не прошёл. До завершения CI, pluginval и FL Studio 20 host acceptance миграция не считается завершённой. Release-ready статус не заявляется.
