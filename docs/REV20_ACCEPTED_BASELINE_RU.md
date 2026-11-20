# REV.20 — УТВЕРЖДЁННАЯ БАЗА ПРОДУКТА

**Статус:** USER APPROVED · CONFIRMED · LOCKED  
**Рабочее место:** `POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-` / `main`  
**Единственный журнал:** `/Info.txt`

## 1. Продукт

POP PUNK GUITAR ULTIMATE — sample-based VST3 guitar instrument для Windows 10 x64. Обязательная DAW для host acceptance — FL Studio 20 x64. Приоритеты: быстрое открытие, низкая CPU/RAM-нагрузка, мгновенная MIDI-реакция, безопасное состояние и real-time audio path.

## 2. Музыкальные режимы

В главном интерфейсе ровно два режима:

- **MELODY** — одна MIDI-клавиша запускает одну соответствующую ноту/сегмент исполнения.
- **PATTERN** — одна MIDI-клавиша запускает один отдельный note/event clip, извлечённый из pattern/riff-oriented источника. PATTERN не превращает клавишу в запуск полного лупа.

**AUTOCHORDS** относится только к PATTERN и открывается в отдельном дополнительном окне внутри этого режима. Это не третий главный режим.

Клавиатурный контракт для обоих режимов: MIDI key → mapped note/event → точный source asset и sample range → отдельный derived clip → playback только этого clip. Полные записи, loops и phrases доступны для отдельного preview в библиотеке. Исходники сохраняются и не разрушаются при анализе или нарезке.

## 3. Визуальная база — 16 оболочек

Активная логическая последовательность только SKIN-1…SKIN-16. **SKIN-1 / NEON STAGE DEFAULT / `skin-053`** — каноническая тема и визуальный образец. SKIN-2…SKIN-16 — единственные остальные утверждённые оболочки. Все legacy/generated skin batches и каталоги вне этой последовательности исключены из продукта.

Logical ordinal 1..16 отделён от immutable ID/index: `skin-053` (53), затем `skin-103`…`skin-117` (103…117). Нельзя использовать suffix stable ID как logical ordinal.

| Логическая тема | Название | Stable ID | Index |
|---|---|---|---:|
| SKIN-1 | NEON STAGE DEFAULT | skin-053 | 53 |
| SKIN-2 | OBSIDIAN GOLD | skin-103 | 103 |
| SKIN-3 | CARBON FORGE | skin-104 | 104 |
| SKIN-4 | MIDNIGHT CRIMSON | skin-105 | 105 |
| SKIN-5 | ARCTIC PLATINUM | skin-106 | 106 |
| SKIN-6 | VIOLET NOIR | skin-107 | 107 |
| SKIN-7 | TITANIUM STORM | skin-108 | 108 |
| SKIN-8 | EMERALD CIRCUIT | skin-109 | 109 |
| SKIN-9 | SOLAR FLARE | skin-110 | 110 |
| SKIN-10 | DEEP OCEAN | skin-111 | 111 |
| SKIN-11 | ROSE CHROME | skin-112 | 112 |
| SKIN-12 | DESERT AMBER | skin-113 | 113 |
| SKIN-13 | GLACIER TEAL | skin-114 | 114 |
| SKIN-14 | PHANTOM GRAPHITE | skin-115 | 115 |
| SKIN-15 | ULTRAVIOLET DRIVE | skin-116 | 116 |
| SKIN-16 | VOLCANIC STEEL | skin-117 | 117 |

Статус ресурсов: для SKIN-1…SKIN-16 имеются утверждённые manifests и индивидуальные имена. Для SKIN-2…SKIN-16 включены 45 SVG material layers (texture/bezel/crest) и 30 PNG artwork assets (preview 360×240 + hero 800×450); source strict asset audit и 16-entry registry contract прошли. Windows x64 build и full CTest также прошли на source branch SHA `10e590c8a3fdfed90cc7ae05e0ff74d8875ac88a`. REV.20 exact-SHA runtime loader/package, pluginval, DPI and FL Studio 20 acceptance остаются отдельными gates. До их прохождения дополнительные оболочки считаются artwork-approved, но не HOST-VERIFIED.

Все оболочки меняют только визуальную подачу. Запрещено менять APVTS IDs, семантику контролов, MIDI, presets, sampler, DSP, audio callback или функциональную геометрию.

## 4. Audio Engine

Один общий Sample Engine для MELODY и PATTERN. Инженерная база включает WAV/SFZ mapping, key/velocity/channel zones, round-robin там, где есть реальные takes, worker-backed sample streaming, bounded SPSC queues, page cache, sample metadata index и заранее выделенные voice slots.

Cache miss не должен блокировать audio thread. File scanning, hashing, SFZ parse/load и asset analysis выполняются вне callback.

Зафиксированные ограничения и риски исходного аудита: до 128 snapshots и до 8 streaming roots на экземпляр; 64 заранее выделенных voice slots; остаются требования к snapshot reclamation, worker failure recovery, queue/cache pressure, cancellation и processor shutdown stress. Наличие классов не заменяет стресс-тест.

## 5. MIDI, articulations и эффекты

Базовые требования: polyphony/voices control, velocity layers, palm-mute threshold, round robin при наличии дублей исполнения, note-on/note-off/release, pitch bend/sustain, electric и acoustic profiles. Не объявлять slide/hammer/pull-off или другие артикуляции записанными, если нет соответствующих исходников.

FX scope включает reverb, chorus, flanger, delay, distortion и существующий amp/tone/DSP. Сохранять действующие FX slot/bypass IDs; не придумывать новые APVTS IDs. Все эффекты должны быть подключены к аудиотракту, UI должен отражать реальное состояние.

## 6. Factory presets и sample rights

Цель — 500 playable factory presets: 250 MELODY + 250 PATTERN, все работают на включённой BASIC LIBRARY 15 GB без зависимости от EXPANDED. EXPANDED ADD-ON добавляет ещё 15 GB (начальный combined total 30 GB) и может расширяться без продуктового лимита. Все 250 PATTERN presets распределяются по окнам/разделам/функциям PATTERN, а не показываются одним плоским списком. Каталог 300 definitions, перенесённый из инженерной базы, является частичной заготовкой 150+150, не выполнением цели 500 и не доказательством playability.

Для каждого sound asset нужны source/provenance, точная лицензия, SHA-256, корректный mapping, technical check и human listening review. В plugin bundle попадают только CC0/public domain или лицензии/письменные разрешения, которые прямо допускают redistribution/embedding исходных сэмплов в сторонний виртуальный инструмент. Session Guitarist/Kontakt и другие проприетарные библиотеки — только tonal/playability references, не источники для копирования.

## 7. Контракты интерфейса

Сохраняются 27 утверждённых пользовательских control IDs; `sync_selector` остаётся служебным полем, а не 28-м пользовательским контролом. Сохраняются семь утверждённых FX bypass IDs. NEON STAGE является эталоном общего набора контролов. Mockup — визуальная спецификация, не доказательство работающего UI.

## 8. Платформа и gates

Windows 10 x64; VST3 x64; FL Studio 20 x64. CMake + JUCE 7.0.12 + C++20 в импортированной инженерной базе.

Нужны exact-SHA Windows Release build, все зарегистрированные CTest, pluginval strictness 5, portable package integrity и отдельная ручная FL Studio 20 host acceptance. Нельзя называть plugin собранным, проверенным или готовым к релизу без доказательств.

## 9. Статус исходных данных REV.20

В целевом репозитории до переноса были сохранены L3XTOWN inventory/manifest/routing документы, hash manifests, acoustic/electric signal audit и LibraryManager. Их не заменяли исходниками старых веток. Инвентаризация содержит 393 source paths / 387 unique audio contents / 6 exact duplicate-content pairs. Локальный FACTORY preflight и реальное копирование WAV ещё не подтверждены. Не перемещать, не перезаписывать и не удалять оригиналы.


## 10. BASIC / EXPANDED LIBRARY — locked distribution contract

- **BASIC LIBRARY:** minimum target 15 GB decimal, included in standard package, mandatory, independently playable; all 500 core factory presets must resolve against BASIC alone. 15 GB is a minimum, not a cap: audio quality, complete mapping, velocity layers, round-robin, articulations and license-cleared unique content determine the final size.
- **EXPANDED LIBRARY:** optional additive +15 GB initial tier; initial combined total 30 GB (15 + 15). It cannot replace BASIC, is not required for any of the 500 core presets, and may grow without a hard cap.
- Sample discovery, analysis and classification/distribution are automatic with confidence/review gates. Manual per-WAV assignment is not required. Indexing/hashing run on background workers.
- No disk I/O, blocking, or unbounded allocation in the audio callback. Keep provenance, redistribution clearance, SHA-256 and license records. Exact duplicates are measured by SHA-256; potential acoustic duplicates require review.
- Never pad content with duplicates or lower-quality samples to hit a size number. Any sample replacement must preserve or improve note coverage, velocity layers, round-robin, articulations, technical quality, mix readiness and legal rights, with listening/objective evidence and atomic mapping/checksum updates.
- Current delivery status is NOT COMPLETE: the JSON contract and tests specify the requirement; neither the 15 GB payload nor the 500 playable presets is claimed delivered.
