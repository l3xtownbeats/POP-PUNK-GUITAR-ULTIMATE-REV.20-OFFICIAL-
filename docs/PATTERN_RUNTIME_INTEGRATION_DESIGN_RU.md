# PATTERN MODE — C++ runtime integration design

Статус: implementation design / not yet wired into the audio processor.

## Scope boundary

This runtime handles only the approved per-key note-event clips:

- MIDI Note On selects a mapping by trigger note, articulation, and velocity zone.
- The selected clip plays as a recorded one-shot event.
- MIDI Note Off releases the matching active clip voice; it must not be confused with a generated pattern step.
- Choke/retrigger behavior is deterministic and channel-aware.
- Chord-driven PATTERN INSTRUMENT phrases remain a separate future engine.

The existing chord-driven rhythm-mask path in `PluginProcessor::processBlock` is legacy behavior. It must not be silently relabeled as recorded clip playback. Until the clip runtime is enabled and has approved content, the product must expose its unavailable state honestly.

## Existing architecture findings

- `SamplerEngine` already owns fixed-capacity voices and renders into the output buffer.
- `SamplePool` publishes immutable region snapshots from a non-audio loader and retains their owners so audio-thread region pointers remain valid.
- Production SFZ samples use a bounded streaming page cache. That streaming path is not automatically suitable for short PATTERN clips: cache misses can produce missing audio and the PATTERN contract requires a bounded, fully preloaded clip cache.
- `processBlock` currently owns MIDI sample-accurate segmentation, MELODY routing, PATTERN chord tracking, AutoChords, and transport scheduling. New clip routing must not intercept MELODY or alter AutoChords semantics.

## Required runtime shape

1. **Offline/background validation and load**
   - Parse the manifest and run the existing fail-closed provenance, source hash, derived hash, PCM, frame-range, license, and musical-review checks off the audio thread.
   - Decode every selected derived WAV into a bounded in-memory representation.
   - Reject the candidate snapshot as a whole if any selected clip is invalid or exceeds configured memory/clip/voice limits.
   - Never publish a partially loaded registry.

2. **Safe publication and lifetime**
   - Publish only a fully constructed immutable snapshot.
   - The audio thread reads a stable snapshot without a mutex, file access, JSON parsing, hashing, allocation, or reference-count destruction.
   - Snapshot ownership must outlive every voice that references its clip data. Retired snapshots are reclaimed only on a non-audio thread after audio use has ended; a raw atomic pointer alone is not a lifetime strategy.

3. **Bounded voice engine**
   - Use fixed-capacity voice storage and preallocated clip data.
   - Each voice records trigger note, MIDI channel, clip identity, playback cursor, gain/envelope state, and choke group.
   - Apply sample-rate conversion using the clip's declared source sample rate.
   - Use deterministic voice stealing when the configured voice cap is reached.
   - No dynamic allocation, blocking lock, disk/network I/O, or unbounded work in `processBlock`.

4. **MIDI lifecycle**
   - Note On chooses the velocity zone and starts the mapped clip at the event's exact sample offset.
   - Repeated Note On for the same key/channel follows a documented retrigger policy.
   - Note Off releases only the matching key/channel voices; release must not cut unrelated notes.
   - Choke groups stop prior matching voices with a short de-click fade, not an abrupt discontinuity.
   - All Notes Off / All Sound Off and play-mode transitions clear clip voices safely.

5. **Processor integration**
   - Keep the current MELODY branch unchanged.
   - Add an explicit PATTERN MODE clip route only when a READY snapshot is installed.
   - Preserve AutoChords as its own chord interpretation feature; do not let it transform a one-key clip trigger into a chord or alter clip mapping.
   - If no approved registry is installed, do not fabricate audio or report the feature as ready.

## Acceptance tests before enabling the route

- Manifest rejection: missing source, source/derived hash mismatch, invalid PCM, bad sample range, license evidence missing, unreviewed clip, overlapping velocity zones.
- Cache bounds: maximum clip count, maximum total decoded bytes, oversized clip, failed decode, failed candidate load leaves previous snapshot active.
- Audio-thread safety: no allocations, locks, file access, JSON parsing, or hashing in render path.
- MIDI: sample-accurate Note On, matching Note Off, repeated trigger, same-sample off/on, channel isolation, velocity-zone selection, choke, voice stealing, panic.
- Audio: expected output, sample-rate conversion, no out-of-bounds reads, no click at release/choke, finite output.
- Regression: MELODY playback and AutoChords behavior remain unchanged.
- Host: Windows x64 VST3 build, CTest, pluginval, then manual FL Studio 20 acceptance.

## Current status

The registry validator exists in Python and validates packaged source/derived WAVs offline. The C++ clip runtime, manifest-to-runtime bridge, bounded preloaded cache, and MIDI clip routing are not implemented yet. No approved real clip payload is currently present in the repository. This document is a design gate, not a claim of completed integration.


## Implementation progress — isolated C++ runtime prototype

Added:
- `Source/Performance/PatternClipRuntime.h`
- `tests/PatternClipRuntimeTests.cpp`
- CTest target `ppgu_pattern_clip_runtime_contracts`

The prototype has a fixed 32-voice array, a 512-mapping lookup bound, a 256-clip/8,388,608-frame snapshot budget, offline PCM/mapping validation, sample-rate-aware linear interpolation, channel-specific Note Off, release and choke fades, and oldest-voice stealing. Its render and MIDI methods use fixed storage and do not allocate or lock.

The prototype is intentionally not connected to `PluginProcessor::processBlock`. Snapshot attach/detach requires audio suspension, and the snapshot owner must retain immutable clip memory until all voices are reset and the runtime is detached. A production publisher/retirement mechanism and manifest-to-PCM loader are still required. Tests have been authored and registered but are not yet reported as passing; Windows CI/build confirmation is pending.
