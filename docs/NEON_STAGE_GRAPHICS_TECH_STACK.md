# NEON STAGE — graphics technology architecture

**Status:** staged technology upgrade; JUCE 9 validation required before changing the production dependency.
**Target:** Windows 10 x64, VST3, FL Studio 20.
**Visual authority:** the approved `01 INTERFACE NEON STAGE DEFAULT` reference and the locked NEON STAGE palette. This document does not authorize a redesign.

## Decision

Keep JUCE as the VST3/audio/MIDI/plugin-host integration framework. Validate JUCE **9.0.6** as the next framework baseline in an isolated Windows CI lane before changing the production checkout. JUCE 9.0.6 is the current stable release selected for this validation pass.

For Windows UI rendering, prefer JUCE's native **Direct2D** renderer. JUCE 8 introduced Direct2D as the default Windows renderer, with GPU-backed windows and images; JUCE 9.0.6 includes further Direct2D and Windows VST3 scaling fixes. This is a more direct fit for this native JUCE component UI than introducing a second independent renderer.

## Rendering policy

1. **Primary candidate — Direct2D (JUCE 9):** GPU-accelerated native 2D drawing, text, paths and image compositing on Windows.
2. **Compatibility fallback — JUCE software renderer:** retain a tested fallback for host/GPU-driver combinations where Direct2D has visual or stability regressions.
3. **OpenGL:** do not attach an OpenGLContext to the root editor by default. JUCE documents that doing so switches the attached component's painting to OpenGL rather than the native renderer. Keep it out of the default path unless a measured feature requires it and FL Studio 20 host tests pass.
4. **WebView/WebGL, Skia, Dawn:** do not add these as parallel UI runtimes in this phase. They introduce another rendering stack and, for WebView, a WebView2 runtime dependency. Reconsider only if a concrete UI requirement cannot be met by Direct2D and a measured prototype demonstrates a net benefit.

## Asset and visual pipeline

- Keep the approved reference as the single source of truth; no palette drift (graphite `#080B14/#101827`, cyan `#00D9FF`, electric blue `#6B8CFF`; no violet/purple/magenta).
- Use independently addressable RGBA PNG files for every production visual asset: panels, hardware details, controls, icons, state artwork, textures, and material layers. PNG is the only shipped/runtime artwork format. SVG is not permitted as a production master, intermediate render source, or runtime asset. Legacy SVG and PNG files previously rendered from SVG remain quarantined placeholders and must not be promoted into the production asset pipeline.
- Every production asset must have 1x/2x/3x runtime variants where applicable, a 4x-or-higher source master for large panels/details relative to the 1024x700 reference canvas, and a manifest record with semantic ID, dimensions, RGBA/alpha validation, state, scale, master relationship, and SHA-256.
- Decode/load artwork on the message/UI thread only. Never perform image I/O, allocation-heavy work, GPU resource creation, or UI rendering in the audio callback.
- Cache decoded images and pre-rendered static layers. Repaint only dirty regions; avoid continuous animation when nothing is moving.
- Keep all nine existing rotary bindings and seven existing main FX switches unchanged. Do not add controls or change DSP, MIDI, APVTS IDs/ranges, presets, or SoundBank as part of the graphics upgrade.
- Treat asset provenance and redistribution rights as a release gate. Unverified Meshy/source artwork must not be bundled as cleared production content. Reference screenshots 01–07 are layout/visual guidance, not assets to crop and ship. Each production component must be authored and reviewed as its own PNG.

## Validation gates

The new `NEON STAGE JUCE 9.0.6 GPU renderer validation` workflow builds the existing VST3 and runs the CTest suite using JUCE 9.0.6 on Windows x64. A green CI run is necessary but not sufficient.

Before promoting JUCE 9.0.6 to the production build:
- compare the exact approved reference against the plugin at 100%, 125%, 150% and 200% DPI;
- test resize, popup menus, floating AutoChords/FX EDIT windows, preset browsing and skin changes;
- test repeated open/close and host reload in FL Studio 20;
- test Direct2D and software fallback on integrated and discrete GPU systems;
- run pluginval strictness 5 and full sound/MIDI regression tests.

**No production framework switch, GPU-performance claim, pixel-parity claim, or FL Studio acceptance is made until these gates pass.**
