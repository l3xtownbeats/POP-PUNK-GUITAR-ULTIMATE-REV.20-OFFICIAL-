# REV.20 — ASSETS

This directory is the **navigation and handoff root** for the approved visual asset library. It does not duplicate binary artwork: the production files remain in the canonical runtime locations under `SKIN/`, where the current JUCE ThemeManager and package scripts expect them.

## Canonical asset sources

- **NEON STAGE DEFAULT / SKIN-1 / skin-053:** `SKIN/Skin_053/assets/` and `SKIN/Skin_053/svg/`
- **SKIN-2…SKIN-16:** each theme's `SKIN/Skin_NNN/assets/`, `SKIN/Skin_NNN/svg/`, and `SKIN/Skin_NNN/theme.json`
- **Closed 16-theme registry:** `SKIN/theme_manifest.json`
- **Exact approved sequence:** `SKIN/approved_theme_sequence.json`
- **Single development journal:** `Info.txt`
- **Production asset specification:** `PPGU_REV20_NEON_STAGE_DEFAULT_ULTIMATE_ASSET_MASTER_PROMPT_RU.txt`

## Contents of this handoff folder

- `theme_catalog.json` — machine-readable index of the 16 approved themes and canonical source paths.
- `NEON_STAGE_DEFAULT/ASSET_MAP.md` — maps the requested production folder taxonomy to the existing REV.20 runtime assets and identifies artwork that is rendered by JUCE rather than baked into static panels.
- `ASSET_OPEN_ISSUES.md` — visual-reference and production handoff items that must not be silently guessed.

## Important integration rules

1. Do not move or rename files in `SKIN/Skin_053/assets/`; manifests and runtime code use those paths.
2. Preserve stable ID `skin-053` and logical ordinal SKIN-1. Stable IDs `skin-103`…`skin-117` remain unchanged for SKIN-2…SKIN-16.
3. The product contains exactly 16 approved themes. Do not add a seventeenth theme.
4. Do not bake dynamic parameter labels, values, meters, LED states, keyboard states, or status text into static artwork. These remain live JUCE/UI layers.
5. A present asset or manifest is not by itself proof of visual approval, host acceptance, or release readiness.
