# NEON STAGE — Artwork Batch 04

Static SVG source components for keyboard/hardware visual language.

| File | Size | Purpose |
|---|---:|---|
| keyboard_chassis.svg | 1200×250 | Keyboard bed/chassis frame |
| key_white.svg | 100×190 | Individual white-key source |
| key_black.svg | 68×118 | Individual black-key source |
| status_led.svg | 96×48 | Decorative status indicator artwork only |
| lcd_readout.svg | 360×110 | Display frame/typography artwork only |
| hardware_detail.svg | 160×160 | Generic fastener/hardware detail |

Palette is restricted to graphite, cyan #00D9FF and electric blue #6B8CFF. These are artwork primitives, not functional controls. LED/LCD visuals must not be wired as telemetry unless driven by real processor state. Keyboard keys are not yet mapped to note events or integrated into the editor. No new parameters, MIDI features, or audio behavior are introduced.

**Status:** SVG source assets only. PNG/alpha export, per-key range layout, reference-image parity, runtime integration, accessibility states and host visual QA remain open.