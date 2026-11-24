# PATTERN MODE — C++ runtime integration status

Статус: runtime, manifest loader, asynchronous publication и прямой MIDI-маршрут интегрированы в C++ процессор. Приёмка Windows x64/CTest и проверка в FL Studio 20 ещё не подтверждены.

## Scope boundary

Этот runtime обслуживает только approved per-key note-event clips:

- MIDI Note On выбирает mapping по trigger note, articulation и velocity zone.
- Выбранный clip воспроизводится как записанный one-shot фрагмент.
- MIDI Note Off адресуется по MIDI key и channel.
- Velocity layers и Round Robin являются частью mapping lookup.
- Choke/retrigger и ограничение голосов обрабатываются детерминированно.
- Chord-driven PATTERN INSTRUMENT (аккорд → riff/phrase) остаётся отдельным будущим движком.

Нельзя подменять реальные записанные фрагменты hard-coded rhythm masks. Legacy chord-driven PATTERN и AutoChords остаются отдельной веткой. MELODY не должен перехватываться direct PATTERN маршрутом.

## Реализованные компоненты

### 1. Registry и provenance

- `LibraryManager/pattern_clip_registry.py` — fail-closed проверка per-key note-event registry.
- Проверяются source/derived SHA-256, source range, PCM WAV, sample rate/frame count, MIDI key/source pitch, articulation, velocity, RR group, musical review и license evidence.
- Пустой registry валиден как конфигурация, но возвращает `EMPTY_NO_APPROVED_CLIPS` и `ready=False`.
- Перекрывающиеся velocity zones в одной комбинации trigger/articulation/RR group отклоняются.
- Реестр не объявляет клип готовым только на основании автоматической сегментации: музыкальная проверка и права на распространение подтверждаются отдельно.

### 2. C++ loader

- `Source/Performance/PatternClipLoader.h/.cpp`
- `PatternClipLoader::load(manifestFile)` возвращает snapshot, errors, ready и empty.
- Проверяются schema, размер manifest, безопасные пути, source/derived hashes, license evidence, musical review, engine target, note-event kind, PCM format, sample/frame limits, memory budget, finite PCM, mapping и pitch ratio.
- Ошибочная загрузка не публикует частичный snapshot.

### 3. Runtime

- `Source/Performance/PatternClipRuntime.h`
- Фиксированный пул из 32 голосов.
- Ограничения snapshot: до 512 mappings, до 256 clips и до 8,388,608 decoded frames.
- Preloaded PCM, sample-rate conversion и pitch ratio.
- Поиск mapping ограничен 512 записями; аудиопоток не выполняет file I/O, JSON parsing, hashing, динамические выделения или блокирующие mutex операции.
- Velocity zones выбирают соответствующий слой.
- Round Robin циклически выбирает совпавшие варианты. Счётчики изолированы по первому matching mapping, то есть по trigger key, articulation и velocity lane.
- Note Off учитывает MIDI channel; предусмотрены release/choke fade и ограниченное voice stealing.
- All Notes Off применяет release, All Sound Off немедленно завершает голоса.

### 4. Processor integration

- `Source/PluginProcessor.h/.cpp`
- READY snapshot подключается к direct PATTERN MODE маршруту.
- MIDI события обрабатываются с sample-offset сегментацией.
- Один MIDI key запускает один mapped clip, без расширения в аккорд через AutoChords.
- SFZ keyswitch события продолжают обслуживаться sampler.
- MELODY и legacy chord-driven PATTERN остаются отдельными ветками.
- При valid empty registry публикация очищается; при invalid registry предыдущий рабочий snapshot сохраняется.
- Async loader использует отдельный generation state от SFZ загрузки.

### 5. Асинхронность и срок жизни snapshot

- Фоновая загрузка выполняется в двухпоточном `sampleLoadPool`.
- Generation increment и публикация сериализованы `patternLoadPublicationMutex`; устаревшая загрузка A не может перезаписать более новую B.
- WAV decode выполняется вне publication mutex.
- Completion callback доставляется через JUCE Message Thread и проверяет актуальность generation.
- Snapshot остаётся доступным, пока активные audio calls и voices держат ссылки; сбор retired snapshots выполняется на не-аудиопотоке.
- Тестовая loader injection seam доступна только при `PPGU_ENABLE_TEST_HOOKS` в отдельной тестовой цели.

## Регрессионные проверки

В репозитории зарегистрированы:

- `ppgu_pattern_clip_registry_contract` — Python registry contract.
- `ppgu_pattern_clip_loader_contracts` — C++ manifest/PCM loader.
- `ppgu_pattern_clip_runtime_contracts` — runtime voice/mapping contract.
- `ppgu_processor_pattern_tests` — интеграция processor, MIDI и async publication.

Runtime tests охватывают snapshot validation/ownership, hot publication, velocity layers, Round Robin, независимость RR между velocity lanes и articulations, channel-specific Note Off, release, choke, voice cap, pitch ratio, All Notes Off и немедленный All Sound Off.

Processor integration tests охватывают audible baseline, invalid registry retention, valid empty registry clearing, Message Thread callback и deterministic A/B generation race (A задерживается управляемым loader seam, B публикуется первой, затем A завершается и должна быть отброшена).

Тесты добавлены в исходники и CMake. Это не равнозначно успешному выполнению: подтверждение компиляции и CTest должно быть получено из Windows CI.

## Оставшиеся gates

1. Успешная Windows x64 конфигурация и сборка VST3 + всех C++ test targets.
2. Успешный полный CTest, включая `ppgu_pattern_clip_runtime_contracts` и `ppgu_processor_pattern_tests`.
3. Проверка CI артефактов/skin registry.
4. Подключение реальных source/derived guitar clips с подтверждённой музыкальной пригодностью и лицензиями. На момент последнего аудита в Git tree нет готовой распространяемой аудиобиблиотеки.
5. Проверка MIDI Note On/Off, velocity, RR, All Notes Off и All Sound Off на настоящем контенте.
6. Ручной запуск Windows x64 VST3 в FL Studio 20; эта проверка не может быть заменена CTest.

## Отдельная будущая ветка

Chord-driven PATTERN INSTRUMENT (аккорд → согласованный riff/phrase, chord adaptation, groove и musical sections) не входит в текущий per-key registry. Его нельзя объявлять готовым на основании реализации note-event runtime.
