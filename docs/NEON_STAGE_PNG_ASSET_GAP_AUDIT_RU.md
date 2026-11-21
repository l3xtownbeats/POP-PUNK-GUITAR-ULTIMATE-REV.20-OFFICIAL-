# NEON STAGE — PNG asset gap audit (Batch 01–08)

**Audit scope:** tracked SVG sources in `SKIN/Skin_053/assets/artwork_batch_01` … `artwork_batch_08`.
**Repository revision inspected:** `eaf437ec03d17d15fade90ed994def59c0306f07`.
**Result:** 61 SVG source files found. This is an inventory and contract-gap review, not a claim that PNG conversion or JUCE integration has completed.

## Source inventory

| Batch | SVG count | Contents |
|---|---:|---|
| 01 | 3 | panel frame, one rotary sample, one FX switch sample |
| 02 | 16 | nine rotary illustrations and seven FX switch illustrations |
| 03 | 5 | five auxiliary-window mockups |
| 04 | 6 | keyboard chassis, generic white/black key, LCD, LED, hardware detail |
| 05 | 5 | generic button state samples: normal, hover, pressed, active, disabled |
| 06 | 6 | FX knob base/pointer/arc/ticks/value LCD/module frame |
| 07 | 8 | mode tabs, section headers/dividers, preset browser and row states |
| 08 | 12 | auxiliary-window controls, icons, notice banner, skin-slot card |
| **Total** | **61** | **61 SVG sources; runtime PNG derivatives not yet verified** |

## Gaps before the assets meet the approved production baseline

1. **Per-control state separation:** Batch 05 contains five generic button examples, not a complete state set for every registered control. Combined OFF/ON switch artwork must be split into independent state PNGs.
2. **Per-control rotary artwork:** Batch 02 has nine rotary illustrations, but runtime assets must be registered individually against the existing nine APVTS IDs. Batch 06 layers must not be treated as complete controls until pointer/value rendering is bound to real parameters.
3. **Keyboard:** Batch 04 contains generic white/black key art, not individual runtime key assets or verified key-state variants.
4. **Auxiliary windows:** Batch 03 and 08 contain visual components/mockups. They do not yet prove that every real auxiliary window has a complete panel, controls, and all required states.
5. **Resolution variants:** source dimensions vary by asset. Production delivery needs consistent 1x/2x/3x exports or a documented scale policy that supports the editor's approved resize range and HiDPI.
6. **Palette audit:** source colors include graphite/blue/cyan gradients plus neutral metallic/text colors. Audit must reject off-brand purple/violet/magenta accents without incorrectly rejecting anti-aliased pixels or neutral highlights.
7. **Manifest:** a single generated manifest must record source path, runtime PNG path, pixel dimensions, RGBA mode, alpha extrema, state/control ID, scale variant, and SHA-256.
8. **Runtime integration:** the existing JUCE resource loader and editor bindings still need explicit PNG registration. A successful SVG-to-PNG conversion is not JUCE integration.
9. **Visual parity:** the approved NEON STAGE DEFAULT reference remains the visual source of truth. Structural validation cannot certify pixel-level similarity; a visual review against the reference is still required.

## Canonical runtime naming

The approved machine-readable contract is `png_asset_contract.json`.

- Controls: `assets/png_runtime/controls/<controlId>/<state>.png`
- Panels: `assets/png_runtime/panels/<panelId>/<scale>.png`
- Icons: `assets/png_runtime/icons/<iconId>/<state>.png`
- State names: `default`, `hover`, `pressed`, `active`, `disabled`, `focus`, `dragged`
- Scale variants: `1x`, `2x`, `3x`
- Each PNG is independently addressable and has its own SHA-256 record.

## Explicit non-claims

- No claim that all 61 SVG files have already been converted.
- No claim that PNGs are connected to JUCE controls.
- No claim that VST3 or FL Studio 20 has passed after this migration.
- No claim of pixel-perfect match until a reference comparison has been performed.
