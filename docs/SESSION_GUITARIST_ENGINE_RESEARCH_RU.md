# SESSION GUITARIST — сравнительный технический разбор для POP PUNK GUITAR ULTIMATE

Статус: исследовательская спецификация. Основана на публичных страницах продуктов и руководствах Native Instruments. Это не копирование закрытого кода, семплов или proprietary-форматов. Внутренняя реализация NI публично не раскрыта; ниже описаны наблюдаемые функции и инженерная архитектура для самостоятельной реализации.

## 1. Исследованный продуктовый ряд

- Electric Sunburst — электрогитара, 154 паттерна: strumming, picked arpeggios и riffs; отдельные pickup-сигналы, артикуляции, timing/humanization.
- Electric Sunburst Deluxe — расширенная библиотека (237 паттернов по описанию Deluxe), дополнительные strumming/arpeggio/reverse варианты, voicing generator, chord-aware playback и расширенная обработка.
- Electric Vintage — винтажная solid-body, 230+ паттернов, strummed/picked/riffs/glissando/tremolo/dead notes и отдельный melody-инструмент.
- Electric Mint — развитые Pattern/Melody режимы, strum/arpeggio/phrase-типы, voicings, Phrase & One Pitch, MIDI drag-and-drop, dead notes/endings/slides, round-robin и performance-контролы.
- Electric Storm Deluxe, Electric Neon Essentials/Deluxe и Electric Ruby Deluxe — иные тембры и поколения интерфейса/движка. Возможности надо сверять по руководству конкретной редакции.
- Strummed Acoustic / Strummed Acoustic 2 — акустические strumming-паттерны, chord-aware transitions, fret noise и double tracking.
- Picked Acoustic — отдельный pattern-инструмент и melody-инструмент; 194 picking/strumming patterns, open/muted/flageolet/tremolo, finger/pick и несколько микрофонных позиций.
- Acoustic Sunburst Deluxe — новое поколение акустического движка с обновлённым sequencing strumming, плавной сменой паттернов и динамикой.

Количество паттернов относится к конкретному продукту/версии и не является целью копирования. Мы готовим собственные лицензированные материалы.

## 2. Наблюдаемая модель управления

### 2.1 Два независимых MIDI-потока
1. Control/keyswitch lane: выбирает слот паттерна, ending, slide или режим/артикуляцию.
2. Playable lane: ноты/аккорды/басовые ноты/мелодия формируют гармонию и высоту исполнения.

Клавиша выбора не должна одновременно звучать как обычная нота. Диапазоны раздельные и настраиваемые. Подписи C1–F1 недостаточно для MIDI-спецификации: сохраняем label, а реальный MIDI note number калибруем в FL Studio 20.

### 2.2 Разные модели паттернов
Руководства описывают как минимум три модели:
- Strumming: записанная ритмическая performance служит основой; входящий chord/voicing управляет дополнительными нотами/голосами. Это не простая транспозиция целого WAV.
- Arpeggio: входящий аккорд разбирается на отдельные ноты и распределяется по струнам/позициям; количество нот влияет на рисунок.
- Riff/Phrase: записанная фраза сохраняет ритм и характер, но интервалы адаптируются к входящему аккорду/voicing. Это не полное транспонирование исходной фразы.
Отдельный Melody-инструмент исполняет ноты и артикуляции как самостоятельную систему; некоторые продукты позволяют временно совмещать melody и patterns.

Следствие для Manager: одного типа PATTERN_WAV недостаточно. Нужны STRUMMING_PERFORMANCE, ARPEGGIO_EVENT_PATTERN, CHORD_AWARE_RIFF, MELODY_PHRASE и Sample Mode note zones. Анализатор только предлагает тип; человек подтверждает музыкальную функцию.

## 3. Исполнительный движок: функциональные блоки

Это наша проектная декомпозиция по наблюдаемому поведению, а не утверждение о внутреннем коде NI.

1. MIDI event router — разбирает note-on/off, velocity, keyswitches и CC; маршрутизирует selector и playable lanes.
2. Pattern state machine — выбранный слот, фаза/шаг, активный chord/voicing, latch/one-shot/loop, ending/slide requests.
3. Host clock / transport adapter — PPQ, tempo, time signature, transport; Sync-to-host и Start-on-key; start/stop/loop/jump/chase.
4. Pattern event representation — музыкальная позиция, атака, длительность/gate, направление удара, струна/голос, динамика, артикуляция, ghost/noise flags, sample zone.
5. Chord and voicing resolver — ноты аккорда, интервалы, инверсии, slash bass, диапазон и аппликатуры. Режимы AS_PLAYED, REVIEWED_VOICING_PRESET, AUTO_CHORDS; неоднозначные аккорды не угадывать молча.
6. String/fret allocator — распределяет ноты по струнам и позициям, минимизирует неестественные скачки, учитывает tuning, capo, fret range и доступность sample zone.
7. Articulation/sample selector — open/muted/palm mute, down/upstroke, pick/finger, dead note, harmonic, slide, hammer-on/pull-off, tremolo, velocity layer, round-robin и noise samples только при наличии размеченных записей.
8. Transition planner — заранее планирует смену аккорда/паттерна к музыкальной границе; anticipation, release/overlap/gate, fret noise и естественное затухание; штатное ending вместо резкого обрыва.
9. Performance dynamics — velocity/impact/accent, modulation/expression, swing/feel, timing shift, humanize. Humanize сохраняет микротайминг записи, а не добавляет случайный jitter.
10. Voice/sample playback engine — sample-accurate scheduling, streaming/preload, envelopes, voice stealing, polyphony cap, click-free release; никакого disk I/O, allocation или locks в audio callback.
11. Mixer/tone chain — pickups/mics, stereo/doubling, amp/cab, EQ/compression/saturation, modulation/delay/reverb. Это отдельный downstream слой.
12. MIDI phrase export — редактируемые MIDI события/прогрессия, если доступны проверенные event data; экспорт не подменяет provenance исходника.

## 4. Playback и музыкальные переходы

В руководствах описаны: выбор паттерна keyswitch; запуск/смена гармонии playable chord; синхронизация с host либо старт с первого нажатия; latch и отдельные ending keys; legato-переходы к ближайшей допустимой музыкальной позиции; anticipation для переходных шумов; темповые отношения 1/2, 1:1, x2; timing shift; swing/feel по 8th/16th сетке; humanize от quantized до original performance; loop/one-shot в отдельных поколениях; velocity и дополнительные MIDI-контроллеры для динамики/акцента; double tracking и тембровая обработка.

Для нас: не делать MIDI note → play entire loop WAV. Нужны event sequence + нотно-аккордовая адаптация + sample selection по артикуляции/струне/velocity.

## 5. Что обязан подготовить POP PUNK GUITAR LIBRARY MANAGER

### Sample Mode
One-shot ноты, отдельные струны/позиции, power chords и подтверждённые voicings; open/palm mute/dead/harmonic/slide и down/upstroke варианты, если реально записаны; MIDI pitch, string, fret/position, tuning, velocity layer, round-robin, sample start/end/release и лицензия. SFZ может дать key/velocity mapping, но не доказывает гитарную природу/артикуляцию.

### Pattern Mode
Тип модели (strum/arpeggio/riff/phrase), source asset и точные frame offsets; музыкальные события с position ticks, onset, duration/gate, stroke/string/articulation/velocity только при подтверждении; chord adaptation profile (as-played, voicing preset, chord-aware interval adaptation); loop boundaries, pickup/lead-in, ending candidates, transition/noise events; tempo/time signature/grid с confidence, неизвестное остаётся null; humanize profile только из достоверных временных данных; selector slot отдельно от playable chord range.

### Melody Mode
Отдельные ноты/фразы и артикуляции, pitch events, длительности, legato/slides/hammer-ons/pull-offs/vibrato и provenance. Не смешивать melodic phrases с selector keys и не выдавать ритмический фрагмент за нотно-точную мелодию.

### Review and legal gates
Acoustic/ML результат — candidate, не доказательство. REVIEWED и LICENSE_APPROVED с доказательством обязательны до FACTORY. Исходники read-only; offsets и hashes сохраняются; похожесть не основание удалять/объединять.

## 6. Обязательная начальная раскладка

| Label | MIDI control function |
|---|---|
| C1 | Pop Punk Downstroke |
| C#1 | Palm Mute 8th Notes |
| D1 | Power Chord Rhythm |
| D#1 | Punk Rock Rhythm |
| E1 | Fast Downstroke |
| F1 | Alternative Punk Rhythm |

Это стартовая раскладка, не ограничение числа паттернов. MIDI note numbers не фиксировать до проверки FL Studio 20. Playable chord lane обязана быть отдельной.

## 7. Приоритет реализации

Manager сейчас:
1. Versioned performance manifest и шаблоны selector slots.
2. Разделение кандидатов one-shot / strumming / arpeggio / riff / irregular phrase / melody.
3. События и точные offsets; envelope onsets нельзя выдавать за ноты или strum events без ручной проверки.
4. Review-форма/CSV для подтверждения pattern type, chord model, articulation, tempo/grid, transition markers и license evidence.
5. Проверка полноты sample zones и пробелов, например отсутствия palm mute для нужных pitch/velocity.
6. Не экспортировать factory manifest до REVIEWED + LICENSE_APPROVED.

VST3 позже:
1. MIDI router + host transport.
2. Chord/voicing resolver и string/fret allocator.
3. Pattern event scheduler + transition planner.
4. Sample engine с realtime-safe streaming/voice management.
5. Performance controls and effects.
6. FL Studio 20 tests: keyswitch mapping, host sync, note chase, loop jumps, stop, chord transitions, low CPU/RAM.

## 8. Ограничения исследования

Изучены публичные страницы и руководства Electric Sunburst, Deluxe, Electric Mint, Picked Acoustic, Acoustic Sunburst Deluxe, Strummed Acoustic и playback documentation. Закрытый исходный код, proprietary sample mapping, точные алгоритмы chord recognition/string allocation и внутренний DSP NI публично не раскрыты. Нельзя утверждать, что известна внутренняя реализация побайтно. Возможности различаются между продуктами и поколениями; каждую функцию перед реализацией сверять по руководству соответствующего инструмента.

## 9. Публичные первоисточники

- Electric Sunburst manual: https://www.native-instruments.com/ni-tech-manuals/electric-sunburst-manual/en/index-en.html
- Electric Sunburst playback page: https://docs.native-instruments.com/ni-tech-manuals/electric-sunburst-manual/en/the-playback-page
- Electric Sunburst Deluxe manual: https://www.native-instruments.com/fileadmin/ni_media/downloads/manuals/Electric_Sunburst_Deluxe/Electric_Sunburst_Deluxe_Manual_2020_03_12.pdf
- Electric Mint manual: https://docs.native-instruments.com/pdf-guides/Electric_Mint/ELECTRIC_MINT_Manual_v2.pdf
- Picked Acoustic: https://www.native-instruments.com/products/session-guitarist-picked-acoustic
- Acoustic Sunburst Deluxe: https://docs.native-instruments.com/ni-tech-manuals/acoustic-sunburst-deluxe-manual/en/about-session-guitarist---acoustic-sunburst-deluxe
- Strummed Acoustic: https://www.native-instruments.com/products/session-guitarist-strummed-acoustic
