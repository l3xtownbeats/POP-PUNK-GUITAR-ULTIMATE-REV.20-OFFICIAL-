# STILLWATER — графические ресурсы SKIN-10

Эта папка содержит векторную основу темы STILLWATER для REV.20.

## Создано
- `svg/background.svg` — фон главного окна.
- `svg/hero.svg` — фирменная hero-графика.
- `svg/preview.svg` — концептуальный preview-композит.
- `svg/controls.svg` — образцы визуального языка rotary/button/LCD/LED; это не runtime spritesheet.
- `svg/texture.svg`, `svg/bezel.svg`, `svg/crest.svg` — поверхности и фирменные рамки.

## Состояние
Это SVG foundation, а не завершённый PNG export pack и не подтверждение runtime-интеграции. Перед выпуском нужны raster exports, production state assets, decode/CRC/dimension validation и точная REV.20 проверка.

## Ограничения
- STILLWATER — SKIN-10, stable ID `skin-111`, index 111; всего тем остаётся ровно 16.
- Не менять APVTS, DSP, MIDI, аудиодвижок, control IDs и геометрию layout.
- Главные режимы только MELODY и PATTERN; AUTOCHORDS — дополнительное окно внутри PATTERN.
