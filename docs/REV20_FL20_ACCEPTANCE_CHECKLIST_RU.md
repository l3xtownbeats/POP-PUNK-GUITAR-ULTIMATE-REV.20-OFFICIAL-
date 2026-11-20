# REV.20 — CLEAN INSTALL / MINIMUM PC / FL STUDIO 20 HOST ACCEPTANCE

Target baseline: Windows 10 x64 version 1809 (build 17763) or newer; FL Studio 20 VST3 host.

## Clean install
- [ ] Start from a clean Windows user profile or VM snapshot.
- [ ] Install the VST3 bundle to the standard Common Files\VST3 location.
- [ ] Install/copy only redistributable sample banks; preserve license and attribution manifests.
- [ ] Launch FL Studio 20 and rescan VST3 plugins.
- [ ] Insert the instrument; verify first-open behavior and missing-library messaging.
- [ ] Select an Electric Melody preset and verify MIDI note-on/note-off.
- [ ] Select an Acoustic preset and verify its actual mapped sample profile.
- [ ] Save project, close FL Studio, reopen project and verify plugin state and library restoration.
- [ ] Test preset switching during playback, host automation, transport start/stop/seek, and audio-device change.
- [ ] Run at least 20 minutes of playback with repeated notes and concurrent voices; record audible glitches.

## Performance evidence
Record the exact CPU model, RAM, Windows build, FL Studio version, plugin commit, and sample bank/version.
- [ ] Cold start time (plugin insert to playable state).
- [ ] Preset-switch latency (median and worst case across 20 switches).
- [ ] Peak and steady-state process RAM with no preset loaded and with a large bank.
- [ ] Idle and playback CPU at 1, 8, and 32 voices.
- [ ] Cache misses/page underruns during sustained playback.
- [ ] Confirm no UI freeze or audio glitch while scanning/browsing/loading.
- [ ] Attach FL Studio logs, test result, and a short screen/audio capture where permitted.

Do not mark M13 complete from CI alone. This checklist requires a real Windows 10 x64 / FL Studio 20 test machine.


## REV.20 additional mandatory checks
- [ ] Verify the canonical default NEON STAGE DEFAULT / SKIN-1 loads on first launch and after Reset to Default.
- [ ] Open the Skin Gallery and verify exactly 16 items, the approved names and ordinals SKIN-1…SKIN-16, no legacy/extra theme entries.
- [ ] Preview a theme, Cancel and verify the original active skin is restored; Preview then Apply and verify persistence after closing/reopening the plugin and the DAW project.
- [ ] Confirm all 16 texture/bezel/crest layers are rendered without blank panels, clipping, missing files or errors.
- [ ] Compare the main editor with the approved NEON STAGE reference 01; compare auxiliary windows with references 02–07. Record exact plugin SHA and captures.
- [ ] Confirm exactly two top-level modes, MELODY and PATTERN; AutoChords remains within PATTERN.
- [ ] Verify 250 MELODY + 250 PATTERN core preset targets and that every core preset resolves using BASIC alone (once delivered); PATTERN entries appear within their functional sections/windows.
- [ ] Confirm the installed BASIC package is at least 15 GB and included; optional EXPANDED is additive and not needed to play core presets.
- [ ] Run pluginval strictness 5 on the exact target VST3 and record the binary hash.
- [ ] Verify plugin editor close during scan/load, repeated bank switching, missing asset, corrupt SFZ, audio-device change, DAW project save/reopen and automation.
- [ ] Run sustained 20-minute playback with repeated notes and concurrent voices; record underruns, peak CPU/RAM, cold start and preset switch latency.
- [ ] Verify no disk I/O, blocking, thread creation or unbounded allocation occurs in processBlock/audio callback.

**Acceptance status as of 2026-11-20:** CI verifies target VST3 and all 16 theme runtime resources; FL Studio 20 host acceptance and pluginval remain NOT RUN / NOT CONFIRMED.


## Latest CI evidence — PageCache target correction

As of target SHA 974c5877d1a0375100539d2513329a38feb84871, workflow 44719521911 passed Windows x64 VST3 build, full CTest 15/15, 16-skin validation, 16-only package and artifact upload. This does not satisfy pluginval or FL Studio 20 manual acceptance.
