# Миграция PPGU REV.20 на JUCE 9.0.6 и C++23

Дата начала: 2026-11-27  
Рабочая ветка: `upgrade/juce-9.0.6-cpp23-cpp26-evaluation`  
База: `main` на SHA `438d59ba07e9b92e9579e9893eac7887dfbe5d5e`

## Целевая конфигурация

- JUCE: **9.0.6**, закреплённый Git tag `9.0.6`.
- Основной стандарт проекта: **C++23**.
- C++26: только экспериментальная конфигурация проверки совместимости; не является release gate.
- CMake: минимум **3.30** — для корректной работы C++26 experimental configuration.
- Целевая платформа остаётся Windows 10 x64, VST3 x64; обязательный ручной host acceptance — FL Studio 20 x64.

## Что уже изменено в этой ветке

1. `CMakeLists.txt`: введён параметр `PPGU_CXX_STANDARD`, по умолчанию 23; разрешены только 23 и 26; выбранный стандарт обязателен, без автоматического отката на более старый.
2. Windows VST3 workflow: JUCE checkout закреплён на tag `9.0.6`.
3. Основная Windows job остаётся production gate: C++23, VST3, полный CTest, 16 skins, package staging и pluginval strictness 5.
4. Добавлена отдельная Windows job для C++26: полный configure/build/CTest, но `continue-on-error: true`, пока поддержка компилятора и стандартной библиотеки экспериментальна.
5. README отражает целевую production-конфигурацию.

## Основания и ограничения

- JUCE 9.0.6 официально поддерживает Windows 10 (версия 1607 и новее); README JUCE указывает C++17 как минимум для сборки, поэтому C++23 — стандарт проекта, а не требование самого JUCE.
- JUCE 9.0.6 требует CMake 3.22 или новее; минимум 3.30 выбран проектом из-за C++26 экспериментального режима.
- В JUCE 9 есть изменения API и поведения относительно JUCE 7. До объявления миграции завершённой необходимы сборка всех targets и исправление всех ошибок/предупреждений, а также ревизия `BREAKING_CHANGES.md`.
- JUCE 9.0.5 содержит защиту от некорректных WAV/AIFF и ряда других повреждённых входных файлов; это полезно для sampler, но само по себе не доказывает безопасность или корректность нашего декодирования.
- Совместимость VST3 с FL Studio 20 нельзя подтвердить только компиляцией или pluginval. Нужен отдельный ручной host acceptance на Windows 10/11.
- До коммерческого релиза требуется отдельная проверка JUCE licensing: коммерческая лицензия либо выполнение применимых условий AGPLv3. Не делать вывод о лицензировании только по факту успешной сборки.

## Обязательные критерии завершения

- [ ] CI C++23: Windows x64 configure/build, VST3, полный CTest, 16-skin validation, package stage и pluginval strictness 5 — PASS на точном SHA.
- [ ] C++26 compatibility job: зафиксирован реальный результат; если не проходит, перечислены точные ограничения toolchain/API, C++23 остаётся production.
- [ ] Проверены API изменения JUCE 8/9 и устранены найденные несовместимости.
- [ ] Проверены WAV, AIFF, MP3 и SFZ decode/streaming на реальных fixtures.
- [ ] Проверены сохранение/загрузка состояния, MIDI, PATTERN, AutoChords, UI, DPI и окна.
- [ ] FL Studio 20 x64 host acceptance на Windows 10 x64 — PASS.
- [ ] Проверена JUCE licensing model для планируемой дистрибуции.

## Текущий статус

**MIGRATION STARTED — NOT VERIFIED.** Изменения внесены в отдельную feature-ветку. CI ещё не запускался на её HEAD; сборка, CTest, pluginval и FL Studio 20 acceptance не заявляются как пройденные.

## Первый source-level API аудит

- В двух местах `Source/UI/ThemeManager.cpp` обнаружен удалённый в JUCE 9 API `Drawable::createFromSVG(const XmlElement&)`. Оба вызова заменены на `Drawable::createFromSVGString(svgText)`; предварительная проверка XML root и существующая SVG sanitization остаются перед декодированием.
- Два вызова `ThreadPool::addJob` в `Source/PluginProcessor.cpp` используют void-returning lambdas, что соответствует ограничению JUCE 9.0.2+ (callable должен возвращать ровно `void` или `ThreadPoolJob::JobStatus`).
- Поиск по основным processor/editor/theme/workspace/Pattern файлам и ключевым JUCE breaking API не выявил использования `createFocusTraverser`, `audioProcessorChanged` override, `NativeMessageBox::show`, `addToDesktop` override, `createNewPeer` override, `getMidiInputSelectorListBox` или `setImageCacheSize`. Это точечный аудит, не замена полной компиляции и проверки всего JUCE changelog.
- Окончательное подтверждение — CI C++23/C++26 на точном SHA.
