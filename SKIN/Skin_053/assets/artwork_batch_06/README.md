# NEON STAGE — Artwork Batch 06

FX artwork primitives, each supplied as an independent SVG source:

- `fx_knob_base.svg` — 180×180 rotary body.
- `fx_knob_pointer.svg` — 180×180 pointer overlay.
- `fx_scale_arc.svg` — 240×140 scale arc.
- `fx_tick_marks.svg` — 180×180 scale marks.
- `fx_value_lcd.svg` — 260×76 neutral numeric display frame; placeholder only.
- `fx_module_frame.svg` — 420×260 module panel frame.

Intended only for the already-approved FX EDIT surface and existing effect parameter presentation. No new main FX switches or APVTS IDs are introduced. FLANGER remains available only inside FX EDIT; the main editor retains exactly seven FX switches. No DSP, parameter mapping, automation, telemetry, or audio behavior has been added. Numeric LCD placeholder must be replaced by actual parameter values if integrated; never display fabricated values.

Palette: graphite #080B14/#101827, cyan #00D9FF and electric blue #6B8CFF only.

**Status:** static vector artwork sources only. Not integrated, not rasterized, and not visually accepted against the pinned 1672×941 NEON STAGE reference. Pointer rotation, value binding, hover/focus/disabled states, alpha checks and host QA remain outstanding.