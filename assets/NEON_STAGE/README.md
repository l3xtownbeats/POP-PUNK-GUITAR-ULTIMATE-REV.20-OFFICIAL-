# NEON STAGE — Production Graphic Asset Set

This directory contains the first reusable vector asset set for the approved NEON STAGE visual design.

## Visual authority
The immutable source of truth is `../POP_PUNK_GUITAR_ULTIMATE_BANNER.svg` (the official GitHub-pinned master artwork). These assets derive their surface treatment, dark-stage environment, cyan/blue/violet/magenta lighting, borders, typography tone and control language from that artwork. They are not a redesign and do not replace the master banner.

## Files
- `neon_stage_tokens.json` — semantic design tokens sampled/derived from the master SVG.
- `neon_stage_surfaces.svg` — reusable stage background, panel, header, section, footer and frame symbols.
- `neon_stage_controls.svg` — reusable tabs, buttons, knobs, toggle and slider symbols.
- `neon_stage_indicators.svg` — signal trace, meter, LED, keyboard strip and status indicator symbols.

## Integration
Each SVG contains reusable `<symbol>` definitions and a visible preview artboard. Reference a symbol with SVG `<use href="neon_stage_controls.svg#ns-button-primary"/>` or inline the symbol definitions into the application's asset bundle if the host renderer does not support external references.

All labels and parameter names must come from the real plugin control model. Do not use decorative controls as substitutes for functioning parameters. Keep DSP, APVTS IDs, MIDI scheduling and audio-thread behavior outside the graphic asset layer.

## Fidelity and implementation rules
1. Preserve the master banner's visual identity and hierarchy.
2. Do not add new theme variants or recolour the master artwork.
3. Use semantic tokens rather than hard-coded colours in new UI code where practical.
4. Keep visual states legible: Default, Hover, Pressed, Disabled and Dragged.
5. Keep animation cosmetic and driven by UI-side data; never block or perform file I/O on the audio thread.
6. These are vector source assets, not proof of completed GUI integration or VST3 validation.
