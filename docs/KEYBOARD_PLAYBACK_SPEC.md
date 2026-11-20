# Keyboard Playback Specification — MELODY MODE & PATTERN MODE

**Status:** APPROVED / CANONICAL PRODUCT REQUIREMENT  
**Approved:** 2026-11-18  
**Project:** POP PUNK GUITAR ULTIMATE

## 1. Core interaction rule

The instrument follows the playable, sample-based guitar-instrument workflow associated with Native Instruments Session Guitarist as a usability and realism reference, while following the project's explicit keyboard rule:

**In BOTH MELODY MODE and PATTERN MODE, one MIDI key press selects and plays ONE specific note-sized audio segment extracted from the source recording.**

The key does not play the entire Guitar Sample, LOOP, RIFF, or a multi-bar phrase. It plays only the mapped segment containing the intended individual note/event.

The essential mapping is:

`MIDI key → mapped note/event → exact source time/sample range → standalone derived WAV clip → playback of that clip only`

This is the central requirement clarified and explicitly approved by the user.

## 2. MELODY MODE

- Each playable MIDI key addresses a specific individual note segment or a properly mapped note zone.
- Pressing one key triggers only the selected note clip.
- Different keys address their corresponding pitches/recorded note variants.
- Note-on/note-off, release behaviour, velocity layers, round robins and articulation selection are handled per note.
- Polyphony is supported according to the instrument's voice limit.
- No full-loop playback is triggered by an ordinary note key.

## 3. PATTERN MODE

PATTERN MODE is also a keyboard-playable note instrument, **not an automatic loop or phrase launcher**.

- Each MIDI key press selects and triggers one specific individual note/event clip.
- The note clip is extracted from an identified segment of rhythm-pattern, riff, loop or phrase source material.
- The mapping must identify the exact source recording and exact start/end sample positions for the selected note segment.
- The extractor writes or references a standalone derived WAV clip for that segment; playback reads that clip, not the entire parent recording.
- Pattern-derived notes retain useful performance character: attack, palm mute, pick articulation, note length, dynamics and other verified metadata.
- The key mapping may select different note articulations, velocity layers or performance variants, but one ordinary key press still produces one note.
- A complete source loop or riff must not play merely because a key was pressed.
- No whole-loop pitch shifting, tempo scaling or playback is allowed as a substitute for individual note mapping.

## 4. Source recordings, loops and derived assets

- Original Guitar Samples, WAV files, SFZ banks, loops and riffs remain preserved as source material.
- The analysis system may retain a whole-take/parent-loop asset for reference and preview.
- It may derive child assets at multiple resolutions: musical phrase, rhythm/articulation segment, individual note or chord event, and micro-event.
- Every derived clip must retain provenance: source asset ID/hash, parent asset ID, source start/end sample positions and times, derived clip hash, extractor version, confidence and review state.
- A keyboard note mapping must point to the standalone derived note/event clip and its exact source segment. It must never point to a heterogeneous full recording as the ordinary playback payload.
- A phrase or whole loop may be auditioned in the library browser as a separate preview action. Such preview behaviour is not the keyboard behaviour of MELODY MODE or PATTERN MODE.
- Uncertain note boundaries or classifications require confidence metadata and review; do not silently invent precise musical labels.
- If a source passage cannot be safely separated into an individual note/event without damaging a sustained note, chord, attack or musical context, flag it for review rather than assigning the entire mixed passage to a normal note key.

## 5. Separation of responsibilities

| Component | Responsibility |
|---|---|
| MELODY MODE | Play individual mapped guitar-note clips extracted from source segments. |
| PATTERN MODE | Play individual mapped note/event clips extracted from rhythm/riff-oriented source segments, retaining their articulation and performance character. |
| Library preview | Audition a selected whole take, phrase, loop or derived clip outside ordinary keyboard note triggering. |
| Extraction engine | Preserve parent recordings, identify source time/sample ranges and create independently addressable derived clips without destructive edits. |
| Preset mapping | Assign explicit derived note clips, velocity layers, articulations and variants to MIDI keys. |

A future dedicated phrase/loop playback feature, if ever approved, must be a separate clearly named function (for example, RIFF/LOOP PLAYER) with its own controls. It must not change the one-key/one-note contract of these two modes.

## 6. Acceptance criteria

The implementation is not accepted unless all of the following pass:

1. In MELODY MODE, pressing one MIDI key triggers only its mapped standalone note segment.
2. In PATTERN MODE, pressing one MIDI key triggers only its mapped standalone note segment extracted from pattern/riff-oriented material.
3. The key mapping resolves to an exact source asset and start/end sample range.
4. Playback uses the derived clip, not the complete parent LOOP/RIFF/source recording.
5. Different MIDI keys can trigger different mapped notes independently.
6. Releasing a key follows the mapped note's release behaviour without restarting or continuing an unrelated source recording.
7. Pattern-derived notes preserve their intended articulation and sample character.
8. No ordinary note mapping references a full source recording as its playback payload unless that recording was explicitly and intentionally approved as a single note asset.
9. Full loops and phrases remain available for separate library preview and future separately approved features.
10. Tests cover both modes and explicitly fail if a key mapping launches a multi-event source loop.

## 7. Non-goals / prohibited behaviour

- Do not turn PATTERN MODE into a one-key-per-loop trigger system.
- Do not play the complete Guitar Sample/LOOP on every key press.
- Do not pitch-shift a heterogeneous loop across the keyboard to simulate individual guitar notes.
- Do not force a variable-tempo or changing-melody loop into one fixed BPM or one note mapping.
- Do not discard the parent loop after extracting child notes or phrases.

**This document records the user's explicit approval of the one-key/one-note rule for BOTH MELODY MODE and PATTERN MODE, clarified as playback of one specific extracted source segment per key. It is a product requirement; it does not claim that the corresponding extraction or plugin playback engine has already been implemented or tested.**


## 8. Primary product reference: SESSION GUITARIST — ELECTRIC SUNBURST DELUXE

**User-approved primary reference:** Native Instruments SESSION GUITARIST — ELECTRIC SUNBURST DELUXE.

This is the project's principal reference for the feel and quality of a playable, realistic sampled electric-guitar instrument: expressive guitar performance, convincing recorded articulations, responsive keyboard playability and coherent musical phrasing. It is a design and quality benchmark, not permission to copy proprietary samples, code, UI assets or protected content.

The user's explicit product distinction is essential: POP PUNK GUITAR ULTIMATE must not be reduced to a basic sampler in which a key merely starts a prerecorded melody or complete riff.

### PATTERN MODE — playable performance, not a fixed recording

- The user plays the notes. MIDI input determines which notes are performed and in what order.
- Each key press triggers one specific pitch-appropriate, independently mapped note segment.
- Changing the key changes the note/pitch and its corresponding recorded guitar sound.
- The selected playing character remains consistent across notes wherever matching source material exists: for example palm-muted, open, picked/downstroke or another selected articulation.
- The same performance style can therefore be played as different note sequences chosen by the user. It is not one prerecorded melody assigned to a key.
- Use matching recorded multisamples/note zones for different pitches and articulations wherever available. Do not rely on crude transposition of one unrelated sample or a heterogeneous loop to fake natural guitar notes.
- Preserve note-specific attack, dynamics, duration, release and verified articulation. Velocity may select dynamics/articulation layers according to the approved mapping.
- If a suitable pitch/articulation recording is missing, report the missing zone or use a documented, quality-controlled fallback. Never silently launch a whole riff or unrelated recording.

### MELODY MODE

MELODY MODE remains a playable note-by-note instrument: each key triggers its mapped individual note clip, with pitch-appropriate samples and expressive note behaviour. It does not launch a prerecorded melody.

### Additional acceptance criteria

1. In PATTERN MODE, a player can hold the selected playing style and perform a freely chosen sequence of different MIDI pitches.
2. Changing pitch selects the corresponding pitch-appropriate note asset/zone while retaining the selected articulation/performance character where mapped.
3. The resulting notes follow the player's MIDI sequence; they do not continue a fixed prerecorded melody or loop.
4. Both modes remain note-triggered: one key press selects and plays one mapped note segment only.
5. Automated tests verify pitch-dependent asset selection, consistent articulation selection across mapped pitches, and rejection of whole-loop/multi-note playback on an ordinary key event.

**The user explicitly approved SESSION GUITARIST — ELECTRIC SUNBURST DELUXE as the primary product reference and confirmed this playable-instrument behaviour as a fixed project requirement. This approval records the specification only; it does not claim the plugin engine has already implemented or passed these behaviours.**


## 9. PATTERN MODE — same rhythmic feel across changing notes

The user further confirms this exact behaviour:

**When the player changes between different MIDI notes in PATTERN MODE, the selected rhythmic performance character must stay the same, while the actual guitar note/pitch and its corresponding sound change.**

- The selected pattern defines the consistent rhythmic/playing feel and articulation behaviour (for example palm-muted punk rhythm, tight downstroke feel, or another selected performance style).
- The player can perform different notes while that same feel remains active.
- Each key press still plays only one individual note segment at the pitch requested by that key. The key does not start a prerecorded riff, melody, loop or multi-note sequence.
- The note's sound changes naturally with its pitch and pitch-appropriate recorded sample; the common rhythmic feel/articulation remains consistent across the mapped notes.
- The rhythm of the player's performed sequence follows the timing of the MIDI notes being played. PATTERN MODE must not impose a fixed prerecorded melody or override the player's note sequence.
- This is not merely one sample transposed to every key: use corresponding pitch-specific recordings/round robins/velocity layers for the selected articulation wherever available, with documented fallbacks for missing zones.
- If a selected performance style cannot be maintained at a particular pitch because no suitable source recording exists, flag the missing mapping or use a clearly defined quality-controlled fallback; do not silently change to an unrelated articulation.

### Acceptance tests

1. Select one PATTERN MODE performance style and play a sequence of different MIDI pitches: every key triggers its own pitch-appropriate single note clip.
2. The selected articulation/rhythmic character remains consistent across those notes wherever corresponding samples are mapped.
3. Changing pitch changes the note and its recorded tonal character; it does not change the selected rhythmic feel.
4. The timing and order of notes follow the incoming MIDI performance, not a prerecorded loop.
5. A single key event never triggers a multi-note recording or fixed melody.

**This requirement supplements and does not replace the one-key/one-note rule or the approved SESSION GUITARIST — ELECTRIC SUNBURST DELUXE reference.**


## 10. Explicit user confirmation — 2026-11-18

The user explicitly reconfirmed and approved the PATTERN MODE behaviour in this specification:

- one selected performance/rhythmic style remains active while the player changes MIDI pitches;
- each different key selects and plays its own pitch-appropriate individual guitar note clip;
- the selected articulation and rhythmic playing character remain consistent across mapped notes;
- the player's MIDI note order and timing determine the performed sequence;
- no ordinary key press launches a prerecorded melody, riff, loop or multi-note recording.

This is a confirmed product requirement. It does not imply that the playback engine, sample mappings or acceptance tests have already been implemented or passed.


## 11. Independent note playback and pitch-specific keyboard mapping in BOTH modes

The user clarifies that the instrument must do more than trigger a selected source fragment in either mode. **MELODY MODE and PATTERN MODE must both behave as genuinely playable note-by-note instruments: each MIDI key must trigger its own mapped note, not make every key play the same sound.**

### Required behaviour

- A selected source passage/fragment may be used as source material for extraction and mapping, but ordinary keyboard performance must trigger the individual note asset mapped to the pressed MIDI key.
- Each MIDI key maps to a specific musical pitch and its own suitable recorded note clip/zone, with its own source range and playback metadata.
- Pressing C, D, E, F, etc. must produce the corresponding different notes and pitch-appropriate guitar sounds. Do not trigger the same unpitched recording identically on every key.
- Do not treat a whole multi-note phrase, riff or loop as the note asset for every key. A phrase may be retained as a library asset/preview reference, while its verified child note assets are mapped for keyboard play.
- In MELODY MODE, the note mappings provide the playable melodic range.
- In PATTERN MODE, the selected performance style/articulation (such as palm mute or downstroke character) remains consistent across the pitch-specific note mappings, while the player chooses the note sequence and timing.
- Use actual pitch-appropriate multisamples and velocity/articulation layers wherever available. Do not disguise a single sample repeated across keys as independent recorded notes. Any pitch-shift fallback must be explicit, bounded, quality-controlled and reported in mapping metadata.
- If a pitch has no suitable note asset for the selected mode/style, report the missing key zone or documented fallback. Never silently substitute the same unrelated sample or trigger a whole phrase.
- Note-on and note-off must be handled per voice so independently played notes can overlap and release correctly according to the instrument's polyphony/voice settings.

### Acceptance tests for both modes

1. Press several different MIDI keys in MELODY MODE: each selects and plays its own pitch-appropriate note asset.
2. Repeat in PATTERN MODE with one selected articulation: pitches change with the keys while the selected playing character remains consistent wherever mapped.
3. Confirm that two different keys do not merely replay the identical same-pitch source clip unless the mapping explicitly identifies a documented fallback.
4. Confirm each key event plays one note voice, not an entire multi-note source passage.
5. Confirm overlapping notes have independent voice state and note-off/release handling.
6. Confirm missing pitch/articulation zones are reported rather than silently mapped to an unrelated sound.

**This section clarifies and strengthens the existing one-key/one-note and pitch-responsive PATTERN MODE requirements. It is a specification, not a claim that the sampler engine or tests are already implemented.**


## 12. Explicit confirmation and Library Manager responsibility

**User-approved and fixed requirement:** the pitch-specific, independent note extraction and mapping described in this specification is a responsibility of BOTH the plugin architecture and POP PUNK GUITAR LIBRARY MANAGER ULTIMATE.

The Library Manager must prepare the actual source material needed by the instrument; this is not solely a plugin-side feature.

- Analyse source recordings, loops, riffs and phrases to identify individual note events and their exact source sample ranges wherever reliable.
- Produce independently addressable derived WAV note clips in staging, with pitch/note estimate, confidence, articulation, velocity/dynamic layer where detectable, source provenance and review state.
- Build pitch-specific note-zone/mapping candidates for MELODY MODE and PATTERN MODE. The mapping must not assign the same unrelated audio clip to every key.
- For PATTERN MODE, group compatible pitch-specific note assets under a shared performance-style/articulation definition so the playing character remains consistent while MIDI pitch changes.
- Preserve parent recordings, complete loops and musical phrases; extracted note clips are linked children, not destructive replacements.
- Flag uncertain boundaries, uncertain pitch/chord estimates and missing pitch/articulation zones for review. Do not fabricate note identities or silently fill missing zones with unrelated samples.
- Keep extraction outputs in staging until the user reviews and approves them. Promotion into Samples/FACTORY requires the established audio, classification, duplicate and license checks.
- The plugin consumes the Manager's approved note assets and mappings, then performs per-key, per-voice playback with independent note-on/note-off and release handling.

**Responsibility split:** Library Manager = analyse, extract, label, validate and prepare pitch-specific note assets/mappings. Plugin = load the approved mappings and play the corresponding individual note voice. Both are required for the intended behaviour.

The user explicitly confirmed this combined requirement on 2026-11-18. This is an approved specification only; it does not claim the extraction, mapping, or plugin playback implementation is complete or tested.


## 13. Selectable extracted rhythm segments versus the complete source recording

The user clarifies that the Library Manager must identify and extract the guitar part or rhythmic passage that is actually useful, rather than automatically treating the entire source WAV as one playable asset.

- Analyse the full source recording and locate coherent sections with a specific guitar role, rhythm, articulation or musical pattern.
- Extract each useful section as its own standalone derived WAV asset, using musical boundaries and preserving the complete rhythmic figure/phrase where possible.
- If the rhythmic figure changes within the source, split it into separate meaningful sections at reliable musical boundaries; do not combine different patterns into one misleading asset.
- Do not cut a coherent pattern arbitrarily or reduce it to isolated notes unless useful child note events can be identified without destroying the pattern's musical context.
- The complete original WAV/whole take may also be retained as a separate selectable asset or library preview, but it must not be forced into every preset or keyboard mapping.
- In the library browser/preset assignment workflow, the user must be able to choose between an extracted rhythm/pattern segment, another extracted phrase/clip, an individual note asset, or the complete recording when deliberately desired.
- Every selectable derived segment retains its exact source offsets, parent relationship, hash, classification confidence and review/license state.
- The plugin loads the exact asset selected for that assignment. A selected rhythm segment is not silently replaced by the entire source WAV; a whole recording is loaded only when the user explicitly chooses it for a separately supported playback/preview use.

This selection rule does not change the MELODY MODE/PATTERN MODE keyboard contract: ordinary key presses in those modes still trigger one mapped individual note clip each, not a full rhythm segment or complete recording. Full rhythm segments and whole takes are selectable library/preset assets for separate preview or any separately approved playback feature.

## 14. Approved overall instrument architecture — SESSION GUITARIST workflow reference

**User approval: confirmed and fixed on 2026-11-18.** The primary workflow and usability reference for POP PUNK GUITAR ULTIMATE is Native Instruments SESSION GUITARIST — ELECTRIC SUNBURST DELUXE. The project should follow the same broad instrument organization and player-facing logic, adapted to pop-punk guitar and implemented with original code, original UI assets and legally distributable source recordings. This is a functional/product reference only; it does not authorize copying proprietary samples, code, protected UI assets or other content.

### 14.1 Two complementary instrument engines

The product is organized around two complementary playing engines, not an arbitrary collection of unrelated modes:

**A. PATTERN INSTRUMENT — chord-driven guitar performance**
- The player selects a rhythm/pattern/performance style in the Pattern Browser.
- The player supplies chord input on the MIDI keyboard (or uses the supported chord-input/Auto Chord workflow).
- The engine interprets the incoming chord and performs it using the selected guitar pattern, preserving the pattern's rhythmic identity while adapting the notes/voicing to the played chord.
- Pattern performance is synchronized to the host DAW tempo where the selected pattern and source material support reliable synchronization.
- The engine must support appropriate pattern variations, chord changes, transitions/endings and performance articulations when corresponding approved material and mappings exist.
- This is the chord-triggered performance workflow. It is distinct from the one-key/one-note keyboard contract defined for MELODY MODE and the note-playable PATTERN MODE below.

**B. MELODY INSTRUMENT — note-by-note guitar performance**
- The player performs individual notes directly from MIDI keys.
- Each key triggers its own pitch-appropriate mapped note asset/zone, with independent note-on/note-off and voice handling.
- The player can perform freely chosen melodies, riffs and arpeggios; the instrument must not substitute a fixed prerecorded melody for the player's note sequence.
- Articulations and playing styles can be selected using the supported performance controls and MIDI Key Switches.

### 14.2 Keep the already-approved keyboard PATTERN MODE contract

The existing MELODY MODE and PATTERN MODE requirements in sections 1–13 remain in force and are not silently redefined by the new PATTERN INSTRUMENT engine:
- In both keyboard note-playable modes, one ordinary MIDI note key triggers one pitch-specific individual note clip only.
- In note-playable PATTERN MODE, the selected note articulation/performance character remains consistent across different pitches wherever suitable mappings exist; the player's MIDI notes determine the sequence.
- The chord-driven PATTERN INSTRUMENT is a separate engine/workflow that interprets chord input and performs a selected pattern. It must not be confused with the note-playable PATTERN MODE contract.
- Do not add a third standalone CHORD/PERFORMANCE instrument merely to represent chord-driven pattern playing. That capability belongs inside PATTERN INSTRUMENT.

### 14.3 Player-facing workflow and controls

The product architecture must provide, subject to available approved content:
- a Pattern Browser for discovering and selecting guitar patterns and performance styles;
- MIDI Key Switches or an equivalent clearly documented MIDI control scheme for pattern selection, articulation changes and supported special performance commands;
- chord input and chord/voicing interpretation for PATTERN INSTRUMENT;
- articulation/performance controls for the MELODY INSTRUMENT;
- dynamics and expressive performance controls;
- host-tempo synchronization for compatible patterns;
- an effects and tone section for the project's own guitar processing, amp/cabinet and effects design.

Controls must have explicit MIDI mappings, documented ranges/defaults and visible state. Do not claim a control is implemented until it exists and passes tests. Do not assume proprietary internal behaviour of the reference product where public documentation does not establish it; implement and document our own technically sound equivalent.

### 14.4 Library Manager preparation responsibilities

The Library Manager must prepare the content and mappings required by both engines:
- For MELODY INSTRUMENT and note-playable PATTERN MODE: extract and validate pitch-specific individual note clips, articulation variants, velocity/dynamic layers where detectable, and key-zone mapping candidates.
- For PATTERN INSTRUMENT: identify coherent guitar rhythm/pattern/phrase candidates, chord changes and chord-event candidates where reliably detectable, phrase boundaries, tempo/meter estimates with confidence, performance style/articulation and suitable transposition/voicing metadata.
- Preserve each parent recording and maintain exact source offsets, parent/child relationships, hashes, extractor version, confidence and review/license status.
- Prepare pattern/chord mapping candidates that allow the performance engine to adapt the selected rhythmic identity to incoming chord input. Do not claim automatic chord recognition is reliable until measured and tested; uncertain chord labels must be marked for review.
- Keep derived assets in staging. Promotion to Samples/FACTORY requires the established human review, audio validation, duplicate checks and license approval. Never modify or relocate source recordings automatically.
- If a source recording cannot safely support a requested note, chord, pattern or articulation mapping, report the missing/uncertain content instead of fabricating it or silently substituting an unrelated clip.

### 14.5 Product acceptance criteria

1. PATTERN INSTRUMENT accepts chord input and performs the selected compatible guitar pattern using the corresponding chord tones/voicing mapping.
2. A chord change changes the harmonic content while retaining the selected pattern identity wherever the mapping supports it.
3. Compatible patterns follow host tempo without destroying their musical phrasing; unsupported/uncertain tempo behaviour is reported.
4. MELODY INSTRUMENT plays independently mapped pitch-specific notes from ordinary MIDI keys.
5. The existing note-playable PATTERN MODE still plays one mapped note per ordinary MIDI key and retains the selected articulation across pitches where mapped.
6. Pattern selection and articulation commands use documented controls/Key Switches and do not accidentally trigger ordinary notes.
7. Missing chord, pitch, articulation or pattern mappings are reported; no silent unrelated sample substitution.
8. Library Manager outputs preserve source provenance and remain staged until review and license approval.
9. Tests distinguish chord-triggered pattern performance from note-triggered single-note playback and verify that neither workflow accidentally invokes the other.

**Status note:** This section records the user's approved product architecture and requirements. It is not a claim that the chord engine, MIDI controls, browser, chord recognition, extraction pipeline, plugin playback or acceptance tests have already been implemented or passed.

## 15. Explicit library preparation split for the two instrument engines

**User-confirmed requirement — 2026-11-18:** the most important Library Manager outcome is to prepare the material so the chord-driven PATTERN INSTRUMENT can perform the available guitar patterns and chord-based parts, while the MELODY INSTRUMENT plays individual guitar notes across the keyboard.

These are two different playback jobs and must have distinct asset mappings.

### 15.1 PATTERN INSTRUMENT content

The Manager must identify and prepare coherent playable guitar patterns, riffs, rhythm parts, arpeggios, chord performances and progressions. It must analyse all supported and relevant guitar styles and techniques, not only pop-punk. Tags may include genre/subgenre, rhythmic feel, chord type/quality, articulation, guitar role and recorded tone.

Where reliable, the Manager must identify chord events and changes within a phrase, record timestamps and confidence, and prepare compatibility metadata for chord-driven performance. It must preserve the musical phrase as a coherent asset and must not reduce every pattern to disconnected notes. Child note/chord events may be extracted as linked analysis/mapping assets where boundaries are reliable.

A pattern may be adapted to incoming chord input only when its recorded/mapped material and voicing metadata support that adaptation. Unsupported chord qualities or uncertain analysis must be reported for review rather than fabricated.

### 15.2 MELODY INSTRUMENT content

The Manager must separately prepare a playable library of individual guitar notes:
- each ordinary MIDI key maps to one pitch-appropriate individual recorded guitar note/zone;
- notes are grouped by available tone family and verified articulation/performance character;
- available velocity/dynamic layers, round robins, string/fret/source-note details are retained;
- missing pitch/articulation zones are explicitly reported.

An ordinary Melody key press plays one individual guitar note only. It must not launch a riff, chord, progression, pattern or whole source recording. Do not fill missing keys by silently repeating an unrelated sample or using uncontrolled transposition.

### 15.3 Shared source, separate engine mappings

One source recording may supply both Pattern and Melody assets. The Manager stores the audio only once where possible, creates linked derived assets with exact source offsets and parent-child provenance, and exposes separate engine-specific mappings. A single derived asset may carry multiple verified descriptive tags, but it must never be routed to an incompatible playback job merely to fill a category.

### 15.4 Acceptance criteria

1. Pattern Instrument receives coherent pattern/phrase assets and reviewed chord/performance compatibility metadata.
2. Melody Instrument receives pitch-specific single-note assets and key-zone mappings.
3. Pattern content is not substituted for individual Melody notes; individual note assets are not mistaken for complete chord-driven patterns.
4. Both engines can use suitable derived material from the same parent recording while retaining source hashes, offsets, confidence, review and license state.
5. Unsupported chord adaptation and missing Melody key zones are reported clearly.
6. Preview and mapping tools identify which engine each asset is intended for.

**This section records the user's approved product requirement. It does not claim that the extraction, chord analysis, mapping or playback functions are implemented yet.**


## 16. Explicit PATTERN MODE confirmation — preserve the rhythmic pattern while changing pitch

**User clarification — 2026-11-18:** in the keyboard-playable PATTERN MODE, the selected rhythmic/playing pattern must remain recognizably the same while the played guitar note changes according to the MIDI key.

- The selected pattern defines the repeated/consistent rhythmic feel, articulation and performance character (for example a tight palm-muted eighth-note feel or a downstroke punk rhythm).
- When the player presses a different MIDI key, the pitch and corresponding pitch-specific guitar note sound change; the selected rhythmic feel and articulation remain consistent wherever mapped.
- The player's MIDI note sequence determines which pitches are played. The engine must not replace the player's sequence with a fixed prerecorded melody or riff.
- Each ordinary MIDI key still triggers one pitch-specific note event/clip. Pattern identity is expressed through consistent timing/feel/articulation across the player's notes, not by launching a multi-note loop on every key.
- If the selected feel cannot be represented at a particular pitch because the required note sample is missing, report the missing mapping or use only an explicitly documented quality-controlled fallback.

**Acceptance test:** select one pattern/feel, play a sequence of different MIDI pitches, and verify that the notes change to the requested pitches while the same rhythmic articulation/feel is retained; verify that each key triggers one note only.


## 17. Mandatory Session Guitarist-inspired PATTERN MODE interaction

**User requirement — 2026-11-18:** PATTERN MODE must follow the recognizable player workflow and playing mechanics of the Pattern mode in Native Instruments SESSION GUITARIST – ELECTRIC SUNBURST DELUXE. This is a mandatory product-level reference, not an optional visual inspiration.

Implement an original, legally independent instrument that follows the same high-level interaction principles:
- Select/browse a playing pattern or performance style, then play it from the keyboard using the instrument's defined playable-key and key-switch layout.
- The selected rhythmic identity must remain consistent as the player changes the played pitch: rhythm/feel and selected articulation stay; the actual guitar pitch follows the MIDI note.
- The user remains in control of the notes and their timing. Do not turn an ordinary playable-key press into an unrelated fixed prerecorded riff or melody.
- Pattern selection, playable-note range, key switches, velocity/dynamics, note-off/release and transitions must behave coherently as one playable instrument, not as a disconnected sample audition list.
- Use suitable pitch-specific source material/mappings for each playable note. Missing mappings must be reported; any pitch-shift fallback must be bounded, quality-controlled and disclosed.
- Preserve the separate PATTERN INSTRUMENT chord-driven workflow specified elsewhere. Do not conflate it with this note-by-note PATTERN MODE.

**Reference boundary:** SESSION GUITARIST is a workflow/mechanics benchmark only. Do not copy proprietary code, samples, protected assets, or exact UI artwork. Build original code, mappings, samples with valid redistribution rights, and original UI.

**Acceptance test:** choose a pattern, play a varied sequence of MIDI pitches and note lengths, and confirm that the pitches follow the keys while the chosen rhythmic/playing identity remains recognizable; switch patterns/key-switch articulations and confirm the expected change without breaking note control or triggering a fixed riff.


## 18. Locked PATTERN MODE performance-preservation contract

**User confirmation — 2026-11-18: approved and fixed.** PATTERN MODE must preserve and respond to the full musical performance character, not merely retain a rough rhythm label. The implementation and asset-preparation pipeline must account for all of the following dimensions wherever supported by the source material:

1. **Loudness and dynamics:** MIDI velocity layers and response, note-to-note accents, dynamic intensity, and supported expression controls. Velocity must select or shape an appropriate performance layer; do not treat it as only a crude volume knob. Where a source has a real palm-muted/soft-picked velocity transition, preserve and map it rather than inventing one.
2. **Phrasing:** note grouping, accents, rests, articulation lengths, phrase direction, attack/release character and musical continuity. Preserve phrase context when preparing pattern assets.
3. **Rhythmic identity:** subdivision, groove, timing feel, swing/shuffle where present, syncopation, gallop, straight/even feel, strumming/picking motion, stops and accents. Do not flatten meaningful rhythmic differences into one generic pattern.
4. **Selected articulation:** palm mute, open, downstroke, upstroke, alternate picking, tremolo, slides, bends, harmonics, sustain and other articulations only when supported by mapped source material. Switching articulation must change the relevant performance characteristic, not merely its UI label.
5. **Performance dynamics and nuances:** pick attack, note emphasis, muting, sustain, decay, transitions and other audible playing details that can be reliably identified and mapped.
6. **Pitch and note identity:** the MIDI key determines the requested pitch; each playable key must use its corresponding pitch-specific guitar note/sample or an explicitly disclosed, bounded and quality-controlled fallback.
7. **Specific note timbre:** retain the appropriate note's recorded tone, velocity layer, articulation, string/fret/source-note identity and round-robin variation when available. Do not replace every key with the same unrelated recording or erase meaningful note-to-note timbral differences.
8. **Musical consistency:** changing pitch must not accidentally reset or alter the selected groove, phrasing, articulation, dynamic character or playing style. Conversely, changing the selected pattern/articulation/dynamics must produce the expected audible change while preserving the player's control of note sequence and timing.

**Control and mapping requirements**
- Keep pattern/feel selection, articulation selection, velocity/dynamics, expression, note pitch, note length and release as distinct but coordinated dimensions.
- Store per-asset metadata and mapping coverage for pitch, velocity, articulation, string/fret (when known), timing/phrase, source provenance and confidence.
- Never fabricate missing performance layers or claim an articulation/technique that the audio or trustworthy source metadata does not support.
- If a dimension is unavailable for a particular note, mark that mapping as missing/limited and report it; use only explicitly documented fallback behavior.
- This contract applies to PATTERN MODE's note-by-note keyboard workflow and must remain distinct from the chord-driven PATTERN INSTRUMENT.

**Acceptance test:** select a pattern and articulation; play a sequence across different pitches, velocities and note lengths. Verify that pitch and appropriate note timbre change per key, while groove, phrasing, articulation and performance identity remain consistent; verify that velocity/dynamics produce the mapped changes; verify that changing the selected pattern or articulation produces a deliberate audible change; verify missing layers/notes are reported rather than silently fabricated.
