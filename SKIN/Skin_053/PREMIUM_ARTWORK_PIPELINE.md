# SKIN-1 / NEON STAGE DEFAULT — Premium Artwork Pipeline

**Scope:** first integration phase only: `skin-053` / `Skin_053`. The other 15 themes remain unchanged.

## Runtime artwork stack

The Skin-1 editor canvas now composites the existing local artwork in this order:

1. `assets/background/main.png` — 2560×1440 base stage canvas.
2. `assets/textures/material.png` — 1024×1024 graphite/material texture.
3. `assets/fx_layers/shadow.png` — 800×450 depth/shadow pass.
4. `assets/fx_layers/stage_glow.png` — 800×450 accent-lighting pass.
5. `assets/fx_layers/specular.png` — 800×450 metallic/specular pass.
6. Existing SVG texture, bezel and crest layers.
7. `assets/fx_layers/edge_highlight.png` — 800×450 edge-lighting pass.

The full stack is drawn only on the main Skin-1 canvas. Floating panels continue to use their existing compact surfaces so the full-screen layers are not repeatedly redrawn into child windows.

## Gallery preview and remaining artwork gate

- The Skin-1 gallery card now uses `assets/background/main.png` instead of the legacy green `assets/preview.png` placeholder.
- `assets/hero.png` is still a legacy placeholder and is not treated as final premium hero artwork.
- The large `Meshy_AI_*` PNG sheets from `SKINS-THEME-` are not copied into this phase: their binary payloads were not available through the repository connector for visual inspection and checksum/license review. The reference JPEGs are composite UI mockups, not isolated production controls.

## Runtime and package contract

- All PNG files are loaded from the local theme directory by `PPGUThemeManager` on the UI/message thread.
- The audio callback, DSP, sampler, MIDI processing and scheduler do not access artwork.
- The runtime packager copies all six layers only for `skin-053`.
- The runtime packager also stages the complete 27-control × 5-state image set (135 PNGs) and its manifest only for `skin-053`.
- `PPGUThemeManager` validates the control IDs, state names, record count, safe relative paths and 256×256 PNG dimensions, then caches 128×128 UI images.
- The nine rotary controls and seven FX switches resolve their authored default/hover/pressed/disabled/dragged images by component ID. Rotary indicators remain driven by the live slider value.
- The existing four Skin-1 sprite atlases, their manifest, the approved theme identity and the existing parameter bindings are preserved.
- No APVTS IDs, ranges, audio behaviour, plugin layout geometry or theme IDs are changed.

## Verification

- `ppgu_theme_contracts` checks decoding and the exact dimensions of all six added layers.
- `ppgu_skin1_premium_artwork_package_contract` stages the factory skin pack and checks the six PNGs are copied byte-for-byte with the expected dimensions.
- CI build/CTest and FL Studio 20 host acceptance must pass before this phase is called complete.

## Rollout sequence

Skin-1 is the quality and packaging reference. SKIN-2 through SKIN-16 are intentionally not modified in this phase; their premium asset work starts only after Skin-1 is accepted.
