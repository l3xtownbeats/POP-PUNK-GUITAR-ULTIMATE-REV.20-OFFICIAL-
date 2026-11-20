# POP PUNK GUITAR ULTIMATE — Pattern Mode Specification

Status: **APPROVED / LOCKED BY USER**
Target: VST3 instrument, Windows x64, FL Studio 20.

## 1. Core behavior

Pattern Mode follows the performance model of Native Instruments Session Guitarist: MIDI keys in a dedicated pattern-selector range select a guitar playing pattern. The instrument then performs that pattern using the chord supplied by the playable MIDI range. Pattern Mode is not a simple WAV loop player and must not pitch-shift an entire recorded loop to fake different chords.

## 2. Approved pattern-selector key map

The following mapping is the approved initial factory layout (key labels must be interpreted using the plugin's documented MIDI octave convention and verified in FL Studio 20):

| Selector key | Pattern |
|---|---|
| C1 | Pop Punk Downstroke |
| C#1 | Palm Mute 8th Notes |
| D1 | Power Chord Rhythm |
| D#1 | Punk Rock Rhythm |
| E1 | Fast Downstroke |
| F1 | Alternative Punk Rhythm |

The layout must be extensible for additional factory patterns and user patterns. Pattern selector keys are control keys; they are not ordinary pitched notes for the guitar part.

## 3. Chord performance

A separate playable MIDI range supplies the chord/root/voicing. When the player changes the chord while a pattern is selected, the engine must render the selected rhythmic performance with the new chord. Examples: select Pop Punk Downstroke, then play C, G, or Am; the rhythmic articulation remains the selected pattern while the harmonic content follows the played chord.

The engine must use reviewed note/chord sample maps, voicings and articulation data. It must not assume that a single full-loop WAV can be transposed to produce every chord.

## 4. Pattern performance requirements

- Downstroke and alternate strumming, including upstroke/downstroke direction where source data supports it.
- Palm-muted and open/normal articulations.
- Power-chord and other reviewed chord voicings.
- Velocity layers and velocity-sensitive attack/dynamics.
- Natural timing and performance variation where supported by recorded material.
- Clean pattern changes: stop or release the previous pattern musically, avoid unintended overlap, clicks and abrupt mid-note cuts.
- Preserve the recorded rhythm and phrase boundaries; do not force quantization or tempo normalization when the source is expressive or irregular.
- Tempo is metadata only when supported by reliable evidence; otherwise mark it unknown/unverified.

## 5. Library Manager responsibilities

Prepare and index the assets needed by this engine:
- reviewed one-shot notes, chord voicings and articulations for Sample Mode;
- reviewed pattern performances and their event/timing data for Pattern Mode;
- separate melodic phrases for Melody Mode.

For every derived candidate preserve source file path, source hash, exact source start/end frame offsets, sample rate, channels, sample format, candidate type, review state and license state. Pattern candidates must also retain their event/onset timing, duration, and tempo with confidence or an explicit unknown value.

The Manager may propose candidates but must never claim that acoustic detection alone proves a guitar note, chord, articulation, musical role, or usable pattern. No automatic promotion to FACTORY.

## 6. MIDI selector and chord-range separation

The VST3 must define and document a non-overlapping pattern-selector range and playable chord range. The approved labels C1–F1 are the initial selector labels; the implementation must verify the actual MIDI note numbers/octave naming in FL Studio 20 and provide a configurable mapping if host octave conventions differ. Selector keys must not accidentally trigger pitched guitar notes.

## 7. Safety and source integrity

Original library files remain read-only during scanning and analysis. No automatic move, rename, overwrite or deletion. Only manually reviewed WAV assets with explicit license approval may be promoted to FACTORY.
