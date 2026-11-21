# NEON STAGE DEFAULT — Visual and performance QA baseline

This document defines repeatable checks for Skin-1 / skin-053. The approved NEON STAGE DEFAULT reference artwork remains the visual source of truth; do not redesign or rearrange it during QA.

## Automated checks

- 27 control IDs, including exactly 9 rotary controls and 7 FX switches.
- Every declared control/state pair has both master and runtime PNG files.
- Four 1024×1024 sprite sheets; the control atlas declares eight rotary frames.
- Atlas manifest and generator use graphite, cyan, electric blue, and neutral white only.
- PNG decode, dimensions, alpha-channel presence, decoded-memory estimates, and SHA-256 are emitted by `tools/audit_neon_stage_assets.py`.
- The asset audit report is currently informational (`--report-only`) while remaining legacy SVG references are migrated to approved raster assets. Do not interpret a generated report as a clean pass while it contains errors.

## Manual host acceptance matrix

Run on Windows 10 x64 in FL Studio 20 with the same VST3 build and skin pack:

| Test | Procedure | Record |
|---|---|---|
| Main interface | Cold-open plugin; repeat 10 times | open latency, CPU idle/peak |
| OFF/ON/HOVER/PRESSED | Exercise all 7 FX switches individually and in combination | wrong/missing frames, response latency |
| Knobs | Sweep all 9 knobs slowly and rapidly | frame continuity, dropped textures |
| Auxiliary windows | Open Import Guitar, FX EDIT, Pattern Section Routing, AutoChords, Settings, Skin Gallery; open several together | open latency, CPU, memory |
| Window redraw | Move, resize, maximize/restore each window repeatedly | black rectangles, stale regions, flicker |
| Indicators | Observe output meters and harmony monitor for 60 seconds | update rate, visual jitter |
| Theme switching | Switch away from NEON STAGE and back 20 times | stale palette, texture loss, freeze |
| Scaling | Test 1x, 2x, 3x at supported host DPI settings | clipping, blur, aspect-ratio drift |
| Preset switching | Change 100 presets while UI is visible | UI stalls, missing controls |
| Audio-thread isolation | Run MIDI/audio while opening windows and switching themes | audio dropouts, callback stalls |

## Measurement protocol

- Capture baseline host CPU with the editor closed, then open idle, then with all six auxiliary windows visible.
- Record process working set and private bytes before opening the editor, after opening, and after closing all windows.
- Measure UI frame/repaint rate separately from the audio callback. Meter timers are expected to remain at 30 Hz (output level) and 20 Hz (harmony monitor); do not increase rates without evidence.
- Record median and 95th-percentile window-open latency over 10 trials.
- Repeat each visual test at 1x/2x/3x and retain screenshots or screen recordings.
- Confirm no image decoding, file I/O, allocation-heavy work, or UI calls occur in the audio callback.

## Release gates

- No missing or corrupt PNGs; SHA-256 manifest matches committed assets.
- Every switch presents distinct OFF/ON/HOVER/PRESSED visuals.
- No black rectangles, missing textures, flicker, or clipped UI in the host.
- No audio dropouts or callback work caused by UI repainting.
- CPU, memory, open latency, and repaint measurements are attached to the QA run.
- FL Studio 20 host acceptance is a separate manual gate; CTest or pluginval cannot replace it.
