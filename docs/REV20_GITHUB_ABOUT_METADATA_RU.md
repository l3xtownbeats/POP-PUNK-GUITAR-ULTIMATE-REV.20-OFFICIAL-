# GitHub About — готовые настройки REV.20

Цель: короткая, точная карточка проекта без неподтверждённых обещаний.

## Repository Description

Вставить в **Settings → General → About → Description**:

`Pop-punk guitar VST3 instrument for Windows x64. MELODY & PATTERN modes, NEON STAGE interface, 16 skins. JUCE 9 / C++23 migration in review.`

Текст описывает проект и не выдаёт незавершённую миграцию за уже принятую базу main.

## Homepage

Установить:

`https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/releases`

Это постоянная точка входа для официальных версий. Пока Releases пусты, ссылка ведёт на страницу релизов без выдуманного сайта или несуществующего installer.

## Topics

Добавить только эти релевантные topics:

`vst3` · `audio-plugin` · `virtual-instrument` · `guitar-plugin` · `pop-punk` · `juce` · `cpp` · `cmake` · `windows` · `music-production`

Не добавлять `open-source`, `commercial`, `free-download`, `500-presets`, `15gb-library`, `juce-9` или `cpp23-production`: лицензия не опубликована, целевой playable bank и BASIC payload ещё не закрыты, JUCE 9/C++23 пока в отдельном PR.

## Social Preview

Использовать утверждённый сохранённый референс:

`Неоновый интерфейс PPGU — поп-панк гитара.png`

Загрузить в **Settings → General → Social preview → Edit**. Выбрать широкий crop, чтобы название PPGU и NEON STAGE оставались читаемыми в маленькой карточке. Не использовать исключённый файл `01 INTERFACE  NEON STAGE DEFAULT .png`.

## Releases и Downloads

- Официальный канал постоянных версий — **GitHub Releases**: versioned tag, Release notes, VST3 package, SHA-256 и чёткая инструкция установки.
- GitHub **Downloads** — устаревший отдельный раздел загрузок; он не заменяет Releases. Не размещать там дублирующие ZIP и не поддерживать два конкурирующих канала.
- Не создавать пустой Release и не публиковать старый Actions artifact как финальный продукт. Последняя подтверждённая сборка относится к прежнему JUCE 7/C++20 SHA; JUCE 9/C++23 PR ещё проходит CI. Кроме того, остаются FL Studio 20 host acceptance, лицензирование/комплектность аудиобиблиотеки и финальная проверка пакета.
- После закрытия release gates создать первый постоянный Release с версией, checksum, release notes и готовым VST3-пакетом.

## Текущая граница доступа

GitHub connector в этой сессии позволяет читать repository metadata и менять файлы/ветки/PR, но не предоставляет операции записи для Description, Homepage, Topics, Social Preview, флага Downloads, создания Release или удаления branch. Поэтому этот документ подготовлен как точная конфигурация; он не утверждает, что настройки уже переключены на GitHub.

## Cleanup policy

- Не удалять открытые PR и их head branches: это активные рабочие линии, даже если они не обновлялись неделю.
- Не удалять ветку только по возрасту. Сначала проверить, что она не является base/head открытого PR, не содержит уникальных коммитов и не нужна для воспроизводимого CI.
- Не дублировать бинарные файлы в Releases, Actions artifacts и legacy Downloads одновременно.
- Временные Actions artifacts использовать только для CI; после истечения срока не оставлять мёртвые ссылки в README.
- Не удалять исходные референсы/экспорты только из-за даты или названия `file (N).*`: сначала проверить manifest, journal и runtime references.
- В репозитории оставить один актуальный README, один канонический `Info.txt`, действующие документы baseline/build/release и только подтверждённые asset manifests. Устаревшие инструкции исправлять или удалять после проверки ссылок и потребителей.
