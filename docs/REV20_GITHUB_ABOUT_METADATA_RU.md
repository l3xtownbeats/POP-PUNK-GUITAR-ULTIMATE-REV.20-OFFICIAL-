# GitHub About / social preview — REV.20 metadata

Этот файл содержит согласованный публичный текст для блока **About** и параметры оформления репозитория. Это не заменяет реальные настройки GitHub: доступный GitHub connector умеет менять файлы/PR, но не предоставляет запись в repository metadata, topics, homepage или Social Preview.

## About description (copy/paste)

`Sample-based pop-punk guitar VST3 instrument for Windows x64. NEON STAGE interface, MELODY & PATTERN modes, 16 approved skins. CMake/JUCE project in active development.`

## Website / homepage

Пока не указывать сторонний сайт или несуществующую страницу продукта. До появления постоянного сайта оставить поле пустым. После выпуска можно направить на публичную release/download page.

## Suggested topics

`vst3` · `audio-plugin` · `virtual-instrument` · `guitar-plugin` · `pop-punk` · `juce` · `cpp` · `cmake` · `windows` · `music-production`

Не добавлять `commercial`, `open-source`, `free-download`, `500-presets`, `15gb-library` или `juce-9` как утверждённые характеристики: лицензия не опубликована, контентные цели ещё не закрыты, а JUCE 9 пока в отдельном migration PR.

## Social Preview image

Рекомендуемый кандидат — сохранённый основной NEON STAGE interface mockup:
`Неоновый интерфейс PPGU — поп-панк гитара.png`

Перед загрузкой в Settings → Social Preview проверьте crop и читаемость в маленьком превью. Не используйте исключённый `01 INTERFACE  NEON STAGE DEFAULT .png` как эталон. README hero image уже ссылается на сохранённый mockup из репозитория.

## Repository settings that remain manual

1. Откройте **Settings → General → Social preview** и загрузите проверенный hero crop.
2. В блоке **About** вставьте description выше.
3. Добавьте topics из списка.
4. Не включайте GitHub Pages, пока нет поддерживаемого сайта.
5. Не включайте/объявляйте Downloads как постоянный канал: используйте GitHub Releases после release gates. Сейчас Downloads выключены, Releases отсутствуют.
6. После утверждения лицензии добавьте корректный `LICENSE` и настройте отображение лицензии GitHub.

## Release policy

До публикации постоянного релиза используйте только workflow artifacts с указанием exact commit SHA, SHA-256 и срока истечения. Не ставьте ссылки на временные artifacts в качестве постоянного installer download.
