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

## Canonical architecture — NEON STAGE (approved BASE)

**NEON STAGE** is the unified top-level system for the plugin's complete
visual theme, skin, graphical interface, functional controls, visual assets
and the internal theme-engine modules that manage and support them.

Its components are parts of one system, not separate products, interfaces,
skins or independently named visual systems:

- **MAIN THEME** — the plugin's main visual theme.
- **SKIN** — the complete visual appearance and graphical styling.
- **GUI** — the complete plugin graphical interface.
- **CONTROLS** — all functional controls, including knobs, buttons, switches,
  sliders, selectors and other interactive elements.
- **ASSETS** — images, textures, artwork, icons, atlases and other visual
  resources.
- **PALETTE** — the shared semantic colour-token system.
- **STATES** — visual control states such as Default, Hover, Pressed,
  Disabled and Dragged.
- **ANIMATIONS & EFFECTS** — visual animations, transitions, lighting and
  presentation effects.
- **E1–E7** — the internal engineering modules that validate, load, manage,
  render, switch, optimise and recover the NEON STAGE system.

**Functional rule:** NEON STAGE is not decorative artwork alone. Its GUI
controls must remain connected to the plugin's real, existing functionality.
Adding a graphical element or a functional control to the plugin interface
means adding and integrating it as a component of NEON STAGE.

Architecture constraints:
1. REV.20 has one unified NEON STAGE system for its main theme, skin and
   complete plugin GUI.
2. All visual presentation, assets, palette, states, animations and functional
   interface controls belong to NEON STAGE.
3. E1–E7 are internal NEON STAGE subsystems; they do not create additional
   themes, skins, shells, panels or interfaces.
4. Do not introduce a parallel shell, duplicate main window, separately
   branded control-deck interface, or second visual product.
5. Keep all NEON STAGE components coherent and integrated while preserving
   the existing plugin parameter IDs, processor state, DSP, MIDI scheduling
   and audio-thread constraints.
