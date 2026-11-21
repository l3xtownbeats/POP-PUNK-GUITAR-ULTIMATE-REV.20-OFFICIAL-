# NEON STAGE — Artwork Batch 05

Five independent reusable button-state SVG source assets (240×72):

- `button_normal.svg`
- `button_hover.svg`
- `button_pressed.svg`
- `button_active.svg`
- `button_disabled.svg`

These are neutral visual templates. The word BUTTON is a replaceable artwork placeholder, not a new control label or feature. Map them only onto already-approved existing controls and IDs in the REV.20 UI (for example the existing Import Guitar, Skin Gallery, Settings, About and mode-selector surfaces where applicable). Do not create additional APVTS parameters, control IDs, modes, or behavior. About remains disabled; AutoChords remains setup-only and disabled.

Palette: graphite #080B14/#101827, cyan #00D9FF and electric blue #6B8CFF only. No violet, purple or magenta.

**Status:** static SVG source artwork only. No runtime wiring, hit-testing, keyboard focus implementation, accessibility semantics, PNG export, alpha validation, reference-image parity review or host QA has been performed. The five visual states must be connected to actual component state before they can be considered functional.