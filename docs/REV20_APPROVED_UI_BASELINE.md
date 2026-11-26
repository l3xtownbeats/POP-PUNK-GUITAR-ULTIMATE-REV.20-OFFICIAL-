# REV.20 — Approved UI Baseline

Status: APPROVED / FIXED BASELINE

This document records the approved functional and visual implementation contract for the REV.20 plugin UI.

## Functional authority

REV.20 source code, APVTS parameter definitions, DSP, MIDI/audio callbacks, and the current development log are authoritative. Legacy mockups are visual references only and must never override current REV.20 behavior.

## Mode scope

- Supported play modes: MELODY and PATTERN only.
- PUNK GROUP is excluded and must not be reintroduced.
- Do not add legacy or invented modes, parameters, controls, or simulated functionality.

## Control and behavior invariants

- Preserve the nine current REV.20 controls, their actual labels, order, APVTS IDs/attachments, ranges, and DSP behavior.
- Preserve the seven existing functional FX bypass controls, their APVTS bindings, states, and FX EDIT behavior.
- Preserve HOST / HOST START / INTERNAL synchronization selection and existing MIDI/audio behavior.
- Any UI restyling must retain real callbacks, parameter attachments, automation, accessibility, and hit targets.

## Visual implementation

The approved NEON STAGE reference defines the composition and visual language: left preset browser, central playing core and guitar artwork stage, right AMP & TONE / FX rack, and lower performance display / MIDI keyboard.

The approved asset atlas and skin production assets define the hardware appearance: authored frames, knob strips, button/switch states, LEDs, meters, textures, panels, and iconography. Use the real assets and sprite states where available; do not substitute generic JUCE primitives when authored assets exist.

## Explicit exclusions

- No PUNK GROUP tab or mode.
- No legacy VOLUME / TONE / DRIVE parameter row from obsolete mockups.
- No fabricated controls, telemetry, meters, or functionality.
- No alteration of REV.20 DSP or parameter semantics for visual similarity.

## Acceptance rule

Do not claim 1:1 visual parity until the plugin has been built, captured at the target sizes, and compared against the approved references with a documented pixel-level review. Report any remaining asset, rendering, host-acceptance, or runtime gaps honestly.

This baseline is the governing contract for subsequent UI implementation and review.
