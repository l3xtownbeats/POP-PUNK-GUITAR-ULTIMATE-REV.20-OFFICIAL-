# REV.20 Theme Engine Upgrade — Approved BASE

Status: APPROVED / implementation contract  
Product: POP PUNK GUITAR ULTIMATE REV.20  
Visual system: NEON STAGE  
Main visual theme / skin / complete plugin GUI: NEON STAGE

## Non-negotiable architecture

- One VST3 product, one editor, one unified NEON STAGE main visual theme/skin and complete functional GUI.
- Theme code is visual-only. It must not modify APVTS parameter IDs, processor state, DSP, sampler, MIDI scheduling or audio-thread behaviour.
- MELODY and PATTERN remain the only top-level musical modes. AutoChords 2.0 remains a PATTERN sub-feature.
- All interactive controls remain real controls bound to existing functionality. No decorative fake controls.
- Approved NEON STAGE palette: graphite/black, metallic silver, purple, magenta and crimson; functional meters may use green/amber/orange/red. No blue/cyan/teal/turquoise palette or lighting.
- Theme parsing, file access, image decoding, cache mutation and theme replacement run only on the message/UI thread. The audio thread must never parse manifests, load files, decode images, allocate theme assets or wait on theme locks.

## Seven approved engineering engines

### E1 — Theme Validation Engine
Deeply validate manifest schema/version, identity, required semantic palette tokens, typography ranges, canonical control IDs, asset declarations, dimensions, formats, safe relative paths, file sizes, image decoding and compatibility contract. Reject duplicate/missing state records, malformed images and path traversal. Validation must be deterministic and return actionable diagnostics. Validate into a candidate object; publish only after the entire package passes.

### E2 — Asset Manager
Centralise theme asset resolution, safe file access, decoding, dimensions, byte budgets, ownership and cache lifetime. Enforce theme-root containment after resolving links; reject escaping symlinks. Cache decoded immutable images by canonical path + file identity/size/mtime (or content digest where practical). Avoid duplicate decode of the same asset. Bound per-asset and total decoded-memory use. Never perform asset I/O on the audio thread.

### E3 — Palette Engine
Keep the 21 approved semantic tokens as the single source of truth. All NEON STAGE panels, controls, labels, meters, status indicators and fallback rendering must obtain colours through semantic tokens. No hard-coded theme colours in component paint code, except explicitly documented status semantics or transparent utility colours. Palette changes must update all theme-aware components consistently.

### E4 — Theme State Engine
Support the canonical visual states: Default, Hover, Pressed, Disabled and Dragged. State resolution must be deterministic and consistent across knobs, FX switches, buttons, sliders and indicators. Missing optional state art falls back to a defined vector/state treatment; it must never leave a control invisible. State rendering must not change the underlying parameter value or interaction semantics.

### E5 — Hot Swap Engine
Allow Preview / Apply / Cancel and live theme switching without restarting the plugin. Load and fully validate a candidate theme before replacing the active theme. Apply atomically on the message thread, preserve editor layout and all APVTS values, and use the declared 150 ms visual transition contract where supported. Failed candidates leave the previously active theme intact (or use the canonical fallback only when the active theme itself is invalid). Never block or synchronise the audio thread for a visual theme change.

### E6 — Performance Layer
Decode once, reuse immutable images, cache pre-scaled/control-state assets where justified, avoid repeated JSON parsing and image resampling during paint, and keep paint operations allocation-light. Add explicit limits for manifest bytes, individual asset bytes, decoded dimensions and aggregate cache footprint. Profile editor open, theme switch, resize, repaint and repeated control interaction. ECO mode reduces optional glow/texture layers while preserving control legibility and state feedback.

### E7 — Fallback Recovery (mandatory cross-cutting gate)
Keep a canonical NEON STAGE DEFAULT fallback. Any malformed manifest, unsafe path, decode failure, missing mandatory asset or failed candidate activation must produce a clear diagnostic and a safe visual result. Recovery must be transactional: never publish a half-loaded palette or half-loaded asset set. Preserve the last known-good theme on failed hot swap. Reset-to-default must also clear stale error/state consistently.

## Current implementation observed before this BASE

- ThemeManager already parses and validates legacy/Skin Studio manifest forms and the 21-token palette.
- Manifest input has a 1 MiB cap; empty and oversized manifests are rejected.
- SVG and PNG helpers already check basic relative-path safety, file sizes, dimensions and some symlink cases.
- NEON STAGE loads four sprite atlases, premium background/material/effect layers and 135 control-state records for 27 controls × 5 states.
- Palette stores decoded images and exposes control-state lookup.
- Theme loading builds a candidate palette before publishing.
- The NEON STAGE interface uses theme-aware rendering and the current branch contains a first visual upgrade to panel chrome and rotary controls.

These are existing foundations, not proof that every engine is complete. In particular, cache deduplication/aggregate memory budgets, complete resolved-path/symlink hardening, transactional hot swap with Preview/Apply/Cancel, consistent state fallback, full palette audit and performance profiling still require implementation and verification.

## Required implementation order

1. Establish contract tests and document current behaviour.
2. Complete E1 validation and safe asset-path tests.
3. Implement E2 Asset Manager with bounded cache and lifecycle tests.
4. Complete E3 palette audit and remove accidental hard-coded theme colours.
5. Complete E4 state resolver and missing-art fallback tests.
6. Implement E5 transactional Preview/Apply/Cancel and live hot swap.
7. Implement E6 cache/performance/ECO behaviour and profiling.
8. Run E7 fault-injection recovery tests.
9. Run Windows x64 build, CTest, VST3 validation and FL Studio 20 host verification.

## Acceptance gates

- No processor/DSP/APVTS/audio-thread changes caused by theme work.
- No theme file I/O, JSON parsing, image decoding or blocking locks on the audio thread.
- Invalid theme cannot partially replace the active theme.
- Failed hot swap preserves the last known-good theme.
- Every required control renders a visible, legible state.
- All semantic palette tokens are validated and consistently consumed.
- Memory/cache limits are enforced and regression-tested.
- Windows x64 VST3 builds; all CTest tests pass; plugin validation succeeds; editor opens, resizes, switches themes and preserves parameters in FL Studio 20.
- Never report a gate as passed without actual recorded evidence.

## Scope discipline

This BASE authorises implementation of the theme engine only. It does not authorise a second editor, new VST3 target, new musical mode, parameter-ID changes, DSP changes, redistribution of unlicensed art, or merging PR #8 before conflicts and all required checks are resolved.

## Canonical terminology — NEON STAGE (approved BASE)

For REV.20, **NEON STAGE** is the single canonical name for the plugin's
entire main visual theme / skin and complete graphical interface.

When the project refers to the plugin's interface, graphical interface, shell,
visual shell, theme, skin, main window, main panel, control panel, appearance,
visual style, visual identity, graphical design, colour palette, graphics,
textures, artwork, controls, meters, indicators, typography, animations or
visual states, all of these are parts of **NEON STAGE**. They are not separate
systems, products, interfaces or skins.

NEON STAGE includes both:
- the complete visual presentation: layout, backgrounds, panels, colours,
  typography, textures, artwork, graphics, lighting and visual effects;
- every functional control presented by that interface: knobs, buttons,
  switches, sliders, selectors, meters, indicators, labels and their states.

**Functional meaning:** NEON STAGE is not merely decorative artwork. It is the
one unified plugin GUI whose visual elements are connected to the plugin's
real controls and existing functionality. Adding a control or a graphical
element to the plugin interface means integrating it into NEON STAGE.

Architecture constraints:
1. REV.20 has exactly one main visual theme/skin and one complete plugin GUI:
   NEON STAGE.
2. All plugin GUI surfaces, functional controls and visual resources belong
   to NEON STAGE.
3. E1–E7 are internal engineering subsystems supporting NEON STAGE; they do
   not create additional themes, skins, shells, panels or interfaces.
4. Do not introduce a parallel shell, duplicate main window, independently
   named control-deck interface, or second visual product.
5. Palette, assets, controls, states, fallback, layout and theme switching
   must remain coherent across the entire NEON STAGE interface.
