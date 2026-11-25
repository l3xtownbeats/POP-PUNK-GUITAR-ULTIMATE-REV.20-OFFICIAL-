# PPGU REV.20 — NEON STAGE DEFAULT Asset Pack

**Theme:** SKIN-1 / NEON STAGE DEFAULT / `skin-053`  
**Status:** SOURCE INDEX PREPARED — EXPORT NOT COMPLETE  
**Canonical runtime source:** `SKIN/Skin_053/`

## What is prepared

- `ASSET_MANIFEST.json` indexes all 307 records in the canonical Skin-053 asset manifest, preserving source paths, sizes, SHA-256 and CRC32 values.
- 16 standalone SVG panel frames have now been created in `panels/`, each with a documented 9-slice inset and no baked-in dynamic UI.
- 27-control state contract and five declared states are retained in the canonical `assets/controls/control_states_manifest.json`.
- Nine main rotary and seven main FX switch APVTS bindings are recorded only after checking the IDs against `Source/PluginProcessor.cpp`.
- Existing background, material, FX overlay, control-state, icon, atlas and vector assets remain in their canonical runtime locations. This pack does not move or duplicate them.

## Exact style contract

Use the SKIN-1 theme tokens in `SKIN/Skin_053/theme.json`: dark graphite surfaces, anodized-metal edges, restrained cyan accent and controlled glow. Typography and dynamic readouts stay live in JUCE. Keep exactly two main modes (MELODY/PATTERN), nine main rotary controls, seven main FX switches, and AUTOCHORDS as a PATTERN auxiliary window. Preserve all 27 control IDs and stable ID `skin-053`.

## Important source conflict

The current sprite sheet manifest declares project `NEON_STAGE_MANAGER_3_0` and a palette that differs from PPGU REV.20. Do not treat it as an approved PPGU palette source. Its geometry may be used only after a dedicated reconciliation against `theme.json` and the approved reference. The SKIN-1 palette itself is authoritative.

## Export limitations

This commit does not fabricate missing images or pretend that existing atlases are equivalent to individually exported components. The exact outstanding deliverables are listed in `ASSET_OPEN_ISSUES.md`. The reference PNG at repository root has not yet been visually inspected in this session, so pixel-perfect layout approval is still open. No ZIP is produced until the source assets have been copied, audited and the missing component assets completed.

## Source references

- `Info.txt` — unified development journal and approved design decisions.
- `PPGU_REV20_NEON_STAGE_DEFAULT_ULTIMATE_ASSET_MASTER_PROMPT_RU.txt` — complete asset production contract.
- `SKIN/Skin_053/theme.json` — exact palette, control map and runtime asset links.
- `SKIN/Skin_053/assets/asset_manifest.json` — canonical asset hashes and source inventory.
- `SKIN/Skin_053/assets/controls/control_states_manifest.json` — 27 controls × 5 states.
- `Source/PluginProcessor.cpp` — actual APVTS parameter identifiers.


## Дополнительные SVG-мастера NEON STAGE
В папке находятся пять вспомогательных SVG-атласов. Они сохранены с прозрачным холстом, чтобы фон листа не попадал в извлекаемые спрайты. Это векторные исходники, а не готовые PNG-экспорты и не подтверждение подключения к JUCE.

- В атласе кнопок задекларированы 27 семейств × 5 состояний.
- В атласе регуляторов — три вертикальные киноленты по 61 кадру (128×128 на кадр).
- В атласе иконок — 35 отдельных именованных векторных глифов.
- Атлас клавиатуры расширен до полного 49-клавишного диапазона: 29 белых + 20 чёрных клавиш, четыре октавы, отдельные активные оверлеи C/E/G.

Для повторяемой проверки структуры из корня репозитория запусти:

```bash
python tools/validate_neon_stage_vector_atlases.py
```

Проверка использует только стандартную библиотеку Python. Она проверяет XML, размеры, прозрачный холст, контракты 27 семейств кнопок, 3×61 кадров регуляторов и уникальность 35 глифов. Она не заменяет визуальную проверку рендера, PNG-экспорт, проверку альфа-канала после экспорта или тестирование в плагине.


PNG-пакет можно сформировать скриптом `tools/export_neon_stage_vector_atlases.py`; в CI экспорт запускается автоматически и публикуется как артефакт проверки. Для повторения локально установи CairoSVG 2.7.1 и Pillow 10.4.0, затем запусти `python tools/export_neon_stage_vector_atlases.py --scale 1.0`. Экспорт включает пять PNG-атласов, три отдельные 61-кадровые полосы регуляторов, контактный лист и SHA-256-отчёт. Это проверка формата и прозрачности, а не художественное одобрение каждого кадра.


### Visual QA correction pass
The first rendered contact sheet revealed carbon-weave overflow, duplicate-looking rotary materials and a misplaced green meter. The source now clips the weave swatch, differentiates black-disc and knurled-steel filmstrips, replaces the stray meter with a 12-segment cyan/blue sample, and reduces icon-label size to fit. Re-run the atlas CI export and inspect its new artifact before accepting the artwork.


### Runtime FX EDIT rotary variants
The Skin-1 runtime pack now includes two additional 1024×1024 61-frame atlases: black-disc for the compressor FX EDIT group and knurled-steel for the EQ FX EDIT group. Their 128×128 cells cover 210°–390° in 3° steps. The corresponding controls use the matching 180° rotary interaction arc; APVTS parameter ranges remain unchanged. The generator creates these assets before build and the package stage copies them only into Skin_053.
