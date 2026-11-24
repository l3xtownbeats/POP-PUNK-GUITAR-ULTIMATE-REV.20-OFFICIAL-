# PATTERN CLIP PIPELINE — технический контракт REV.20

## Два разных режима, которые нельзя смешивать

1. **PATTERN MODE (одна MIDI-клавиша → одна нота).** Каждая клавиша запускает отдельный pitch-specific записанный note-event clip. Выбранная артикуляция/характер исполнения должна быть подтверждена реальной записью.
2. **PATTERN INSTRUMENT (аккорд → ритмическое исполнение).** Отдельная система coherent rhythm patterns / riffs / phrases с проверенными chord-adaptation maps. Это не тот же самый механизм, что одноклавишное воспроизведение ноты.

Текущий PatternClipRegistry относится только к первому режиму. Он не объявляет ритмические фразы готовыми и не заменяет будущий chord-driven Pattern Instrument.

## Что уже есть в LibraryManager

- audio_segmenter.py — монодические pitch-event кандидаты, dry-run по умолчанию; извлечение только в staging. Границы и pitch требуют прослушивания.
- candidate_builder.py — группирует акустические onset-события в preview-регионы. Не определяет подтверждённые музыкальные фразы, такты или loop seams.
- rhythm_analysis.py — гипотезы BPM/ритмических интервалов; не утверждает meter, downbeat или groove.
- asset_pipeline.py — извлекает WAV-диапазон по явно проверенным sample boundaries.
- manifest_reviewer.py — фиксирует человеческую музыкальную проверку; не одобряет лицензию автоматически.

Ни один из этих этапов сам по себе не делает клип READY для плагина.

## Gate перед публикацией в плагин

pattern_clip_registry.py проверяет каждый опубликованный clip:

- kind=note_event и engine_targets содержит PATTERN_MODE;
- исходный PCM WAV должен присутствовать в пакете по безопасному относительному пути; проверяются его SHA-256, PCM-формат, sample rate и то, что точный source sample range не выходит за число исходных кадров;
- наличие производного PCM WAV, совпадение его SHA-256, sample rate и frame count;
- MIDI trigger key и source pitch в диапазоне 0–127;
- articulation ID, velocity range и round-robin group;
- отдельное подтверждение музыкальной проверки границ;
- отдельное подтверждение лицензии, SPDX ID, HTTPS source URL и включённый в пакет license evidence file;
- отсутствие пересекающихся velocity zones в одной комбинации trigger/articulation/round-robin;
- безопасные относительные пути внутри пакета.

Загрузка возвращает неизменяемый набор mapping records. Пустой manifest считается валидным состоянием EMPTY_NO_APPROVED_CLIPS, но никогда не READY. Любая ошибка отклоняет весь manifest (fail closed).

Пример пустого manifest находится в LibraryManager/pattern_clips.example.json. Это шаблон схемы, не аудиоконтент и не готовая библиотека.

## Текущая граница готовности

В Git-дереве текущей ветки нет WAV/FLAC/OGG/MP3/SFZ/SF2/GIG payload-файлов. При этом в проекте сохранены инвентаризационные CSV/отчёты о внешней локальной библиотеке: acoustic audit сообщает 723 проанализированных файла (348 Nylon, 375 Steel); журнал L3XTOWN сообщает о 393 файлах с совпавшими размером, SHA-256 и читаемыми WAV-заголовками на внешнем пути Windows F:\POP PUNK GUITAR ULTIMATE\Samples\SourceLibraries\L3XTOWN GUITAR. Эти отчёты — полезные provenance/инвентаризационные свидетельства, но сами аудиофайлы не находятся в этом Git checkout, а музыкальная пригодность и права на распространение каждого источника не подтверждены этими цифрами.

Поэтому нельзя автоматически превращать эти CSV-записи в PATTERN clips или считать chord-named WAV полноценными гитарными note-event / rhythm performances. Следующий реальный контентный шаг — получить доступ к оригинальным аудиофайлам в локальной библиотеке, сверить их SHA-256 с inventory, проверить лицензионные права, затем прослушать/разметить подходящие материалы и только после этого извлекать клипы в staging.

## Real-time ограничения

Manifest parsing, SHA-256, license checks, file I/O, audio analysis and extraction выполняются только в offline/background LibraryManager. Исходный WAV включается в пакетный набор provenance-файлов и проверяется до публикации mapping; если источник отсутствует, изменён или диапазон выходит за его границы, registry отклоняется целиком. Audio callback должен получать заранее проверенный immutable mapping и не открывать файлы, не парсить JSON и не считать хэши. Runtime bridge, bounded clip cache, sample-offset scheduling, note-off/choke/release и host-sync transitions — отдельный следующий C++ этап; этот commit их не заявляет.
