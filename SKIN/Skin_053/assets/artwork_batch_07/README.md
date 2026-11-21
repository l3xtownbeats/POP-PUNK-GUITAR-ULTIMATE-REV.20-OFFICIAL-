# NEON STAGE — Artwork Batch 07

Static SVG components for the existing MELODY/PATTERN mode selector and Preset Browser:

- `mode_tab_active.svg`, `mode_tab_inactive.svg` — 220×64 existing mode-tab states.
- `section_header.svg` — 520×58 section header backing.
- `section_divider.svg` — 600×12 section separator.
- `preset_browser_frame.svg` — 520×420 browser panel frame.
- `preset_row_normal.svg`, `preset_row_hover.svg`, `preset_row_selected.svg` — 480×48 preset-row visual states.

No new mode, preset category, preset name, parameter, control ID, or browser behavior is defined. The two mode labels remain exactly MELODY and PATTERN and must be drawn from the existing UI text/IDs. Preset row text and selection must be supplied by the actual preset engine; these SVGs are backgrounds only. No fake preset entries or search behavior are included.

Palette locked to graphite #080B14/#101827, cyan #00D9FF and electric blue #6B8CFF. No purple/violet/magenta.

**Status:** artwork source only; not wired into runtime, not rasterized, and not accepted as pixel-matched to the pinned NEON STAGE reference. Layout, typography, scaling, keyboard focus/accessibility and FL Studio 20 host validation remain open.