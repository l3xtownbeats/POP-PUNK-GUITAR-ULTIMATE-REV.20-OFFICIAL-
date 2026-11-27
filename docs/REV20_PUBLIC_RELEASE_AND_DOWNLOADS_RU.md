# REV.20 — официальные загрузки, сборки и выпуск

**Канонический репозиторий:** [POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-)  
**Основная ветка:** `main`  
**Статус:** постоянные Releases ещё не опубликованы. Actions artifacts — временные CI-выгрузки, не официальный канал релизов.

## 1. Последняя проверенная Windows x64 VST3-сборка

GitHub Actions run: [REV.20 Windows x64 VST3 and 16-skin validation — #842](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/45941370562)

- Проверенный commit: `781205287eac13d7a2392a85721463040a7ea217`.
- Текущий `main` на момент подготовки страницы: `438d59ba07e9b92e9579e9893eac7887dfbe5d5e`, прямой дочерний commit проверенного SHA; он добавил сохранённые визуальные референсы.
- Windows x64 configure и Release build: PASS.
- Полный CTest: PASS.
- Генерация NEON STAGE UI snapshots: PASS.
- Проверка 16 тем и artwork: PASS.
- Сборка VST3-пакета с 16 скинами: PASS.
- pluginval strictness level 5: PASS.

### Файлы сборки

- [Скачать VST3 + 16-skin pack (Actions artifact)](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/45941370562/artifacts/15173197005)  
  Artifact: `PPGU-REV20-Windows-x64-VST3`; размер 11,739,145 bytes; SHA-256 `8c6bbe8851d0d2a5341e0ea025cfa6b02d5d44722db3970c411e4fbee2bcf716`.
- [Скачать NEON STAGE UI snapshots](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/actions/runs/45941370562/artifacts/15172667912)  
  Artifact: `PPGU-NEON-STAGE-JUCE-UI-SNAPSHOTS`; размер 236,996 bytes; SHA-256 `2cdd6db7cb0460d56baada01525754278d7b25d1adeb0ee6db5066e790edf7a7`.

**Срок хранения этих Actions artifacts — до 11 декабря 2026 года (UTC).** После истечения срока ссылки перестанут работать. Это CI artifacts, а не постоянные GitHub Releases.

## 2. Исходный код

- [Скачать ZIP основной ветки](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/archive/refs/heads/main.zip)
- [Скачать TAR.GZ основной ветки](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/archive/refs/heads/main.tar.gz)
- [Открыть исходники на GitHub](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/tree/main)

Source archives содержат исходный код и ресурсы. Они **не являются** готовым установщиком или собранным VST3.

## 3. Отдельные визуальные материалы

Эти файлы — графические референсы/пакеты, не программный плагин:

- [NEON STAGE panel frames 1× / 2× (ZIP)](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/raw/main/PPGU-NEON-STAGE-PANEL-FRAMES-1X-2X.zip)
- [PPGU NEON STAGE interface references (ZIP)](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/raw/main/Неоновый%20интерфейс%20PPGU.zip)
- [UI asset atlas (PNG)](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/raw/main/Неоновый%20атлас%20UI%E2%80%91ассетов%20PPGU.png)

## 4. Постоянные Releases

На момент обновления в репозитории нет опубликованных GitHub Releases и нет постоянного установочного пакета. Legacy GitHub Downloads отключены. Это не блокирует GitHub Releases: Releases являются единственным рекомендуемым постоянным каналом загрузки. Пока нет проверенного релизного пакета, официальный бинарный релиз не публикуется.

Не используйте временный CI artifact как обещание стабильного релиза. Постоянный релиз должен появиться только после:
1. exact-SHA Windows x64 Release build и полного CTest;
2. pluginval strictness 5;
3. package integrity / clean-install test;
4. ручной проверки в FL Studio 20 x64 на Windows 10 x64;
5. проверки состояния пресетов, библиотеки, сэмплов, лицензий и redistributable payload;
6. публикации versioned Git tag, Release notes, SHA-256 и permanent asset.

## 5. Установка временного VST3 artifact

1. Скачайте `PPGU-REV20-Windows-x64-VST3` из Actions artifact.
2. Распакуйте архив.
3. Найдите `.vst3` bundle внутри архива.
4. Скопируйте bundle в пользовательскую или системную папку VST3, которую сканирует ваша DAW.
5. Убедитесь, что папка `Skins` из того же пакета расположена рядом с VST3 bundle в предусмотренной структурой пакета позиции.
6. Перезапустите сканирование плагинов в DAW.

Это инженерная CI-сборка для проверки, а не релизный installer. Совместимость с FL Studio 20 должна подтверждаться отдельным host acceptance; успешный pluginval не заменяет проверку в DAW.

## 6. Настройка публичной страницы\n\nDescription, Homepage, Topics и Social Preview подготовлены в [GitHub About configuration](REV20_GITHUB_ABOUT_METADATA_RU.md). Реальные значения этих полей ещё требуют сохранения в Settings → General → About; автоматическая запись repository metadata недоступна через используемый GitHub connector. Homepage предлагается направить на страницу Releases. Legacy Downloads не использовать как второй канал.\n\n## 7. Текущая технологическая линия

- Основная ветка `main` на момент этой записи: JUCE 7.0.12 + C++20.
- Отдельная миграционная review-ветка: [PR #31 — JUCE 9.0.6 / C++23 / C++26 evaluation](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-/pull/31). Пока PR не принят и не прошёл все проверки, JUCE 9/C++23 нельзя описывать как текущую production-базу main.
- C++26 — экспериментальный режим компилятора, не production-гарантия.

## 8. Лицензия и права

В корне текущей основной ветки не обнаружен файл `LICENSE`. Не следует предполагать, что исходники или sample assets автоматически лицензированы как open source или могут свободно распространяться. Права на сторонние аудиозаписи и графику проверяются отдельно. До публикации постоянного релиза необходимо явно определить лицензию исходного кода и права на каждый распространяемый audio asset.
