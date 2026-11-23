# ASSET OPEN ISSUES — NEON STAGE DEFAULT / SKIN-1

Эти вопросы нельзя разрешать художественным предположением. Закрывать issue только после проверки первичного источника и обновления соответствующего manifest.

## ASSET-001 — недоступен визуальный просмотр утверждённого PNG-макета

- **Файл:** `01 INTERFACE  NEON STAGE DEFAULT .png` в корне репозитория.
- **Проблема:** текстовый GitHub connector не возвращает бинарное PNG-изображение; визуальное содержимое макета в этой сессии не было прочитано.
- **Риск:** нельзя честно подтвердить pixel-level совпадение композиции, пропорций и координат отдельных панелей.
- **Источник истины:** сам утверждённый PNG. После предоставления изображения в доступном для визуального чтения виде сравнить его с 1024×700 UI и закрыть issue.
- **Статус:** OPEN.

## ASSET-002 — расхождение semantic palette между master prompt и theme.json

- **Master prompt:** `danger #FF557A`, `warning #FFBE55`.
- **Runtime theme.json:** `danger #FF665E`, `warning #FFB454`.
- **Риск:** неодинаковая окраска warning/danger индикаторов в статическом artwork и runtime.
- **Предложение:** считать `SKIN/Skin_053/theme.json` источником runtime-палитры до отдельного подтверждения; не переписывать цвета без решения владельца дизайна.
- **Статус:** OPEN.

## ASSET-003 — sprite-sheet manifest содержит чужой project label и palette snapshot

- **Файл:** `SKIN/Skin_053/assets/spritesheets/neon_stage_spritesheet_manifest.json`.
- **Проблема:** поле `project` содержит `NEON_STAGE_MANAGER_3_0`, а base palette содержит `#05070E` / `#00D2FF`; PPGU REV.20 master prompt запрещает переносить Obsidian Neon Purple/чужую палитру.
- **Риск:** неоднозначная provenance и ошибочная регенерация atlas.
- **Предложение:** перед следующей регенерацией подтвердить происхождение atlas и привести project/theme/palette metadata к PPGU SKIN-1 tokens, сохранив текущие координаты и runtime-файлы до проверки.
- **Статус:** OPEN.

## ASSET-004 — не все production-компоненты представлены отдельными экспортами

- **Проблема:** runtime assets и sprite atlases уже есть, но master prompt требует более детальную независимую библиотеку: отдельные panel exports, auxiliary window panels, layered knobs, отдельные состояния всех FX controls, отдельные keyboard states и extracted sprite frames.
- **Риск:** нельзя выдавать текущий runtime комплект за полный production asset pack.
- **Предложение:** производить партиями согласно мастер-промпту; после каждой партии обновлять manifest и проверять наличие/размеры/форматы.
- **Статус:** OPEN.

## ASSET-005 — 16 theme skins и SKIN-1 asset pack имеют разные объёмы работ

- **Проблема:** 16 утверждённых тем уже присутствуют в registry/runtime; этот production pack предназначен только для полного исходного комплекта SKIN-1 / skin-053.
- **Риск:** ошибочно создать дополнительные theme IDs или смешать assets разных тем.
- **Предложение:** оставить 16 утверждённых имён и stable IDs неизменными; сначала завершить NEON STAGE DEFAULT, затем адаптировать совместимые компоненты для остальных 15 без копирования его уникальной палитры/art direction.
- **Статус:** OPEN.
