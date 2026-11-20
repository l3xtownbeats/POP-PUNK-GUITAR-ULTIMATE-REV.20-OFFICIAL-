# POP PUNK GUITAR LIBRARY MANAGER ULTIMATE

## Library Manager 3.0.0-dev5 — integrated multi-mode library preparation

This is a read-only inventory and SFZ audit stage. It never moves, renames, deletes, rewrites, or overwrites source audio or SFZ files.

### Required library layout

```
Samples/
├── FACTORY/
├── Import Sample Guitar/
└── OTHER/
``

Keep this as the single approved Samples root. Put new incoming WAV, SFZ and archive files in `Samples/Import Sample Guitar`.

### Run on Windows

1. Keep this LibraryManager folder inside the project.
2. Confirm the three folders above exist under the single Samples root.
3. Put incoming WAV, SFZ and archive files inside `Samples/Import Sample Guitar`.
4. Double-click `RUN_LIBRARY_MANAGER.bat`.

Python 3.10+ is required. The scanner uses only the Python standard library.

### Reports

Reports are written beside the tool in `reports/`:
- `inventory.csv` — file inventory, SHA-256, WAV header metadata and conservative filename hints.
- `sfz_sample_references.csv` — per-region SFZ sample resolution, note/velocity ranges, group label, trigger and loop hints.
- `exact_duplicates.json` — exact SHA-256 duplicate groups; nothing is removed.
- `summary.json` — scan totals and SFZ reference totals.
- `scan_cache.sqlite3` — resumable metadata/hash cache.

### SFZ support in 0.2.0

- Handles multiple regions per SFZ.
- Reads quoted and unquoted opcodes, inline tags and comments.
- Resolves relative sample paths and `control/default_path`.
- Reads `#include` files and reports missing include files and include cycles.
- Applies conservative inherited values from global/master/group scopes.
- Exports lokey/hikey and lovel/hivel ranges plus group_label, trigger, loop_mode and pitch_keycenter hints.
- Does not execute SFZ scripts or claim full compliance with every vendor extension. Review parser output before using it as final sample mapping.

### Tests

The GitHub Actions workflow `.github/workflows/library-manager-tests.yml` compiles the Python modules and runs SFZ regression tests on Windows with Python 3.11.

### Safety

- Original files are never changed.
- Automatic filename hints are not treated as final musical classification.
- Archives are inventoried only; they are not extracted.
- Unsupported files are skipped, not deleted.
- Copy/sort mode remains a separate future stage requiring preview, collision checks, checksum verification, a transaction journal and rollback.


## Critical rule: duplicates are not the same as similar sounds

The Library Manager must distinguish exact file duplicates from similar guitar tones, performances and musical sequences. **It is forbidden to delete, merge or suppress files because their timbre, notes, chords, rhythm, riff or melody is similar.** Same riff in a different tone, take, articulation, velocity layer, voicing, octave or performance is a separate valuable asset. Similarity is for tagging, linking, filtering and auditioning only.

The current exact-duplicate report uses SHA-256 identity and reports identical bytes; it does not delete anything. Any future perceptual near-duplicate detector must produce review-only candidates and must not perform automatic cleanup. Timbre similarity, rhythmic similarity, melodic/interval similarity, chord-sequence similarity and performance similarity must be represented as separate relationship dimensions. See [DUPLICATE_AND_SIMILARITY_POLICY.md](../docs/DUPLICATE_AND_SIMILARITY_POLICY.md) for the mandatory rules.

## Required preparation for MELODY MODE and PATTERN MODE

The Library Manager is responsible for preparing pitch-specific playable note material for the plugin; it must not merely catalogue a long source recording or assign one identical clip to every MIDI key.

The planned extraction/mapping stage must:

- identify individual note events inside WAV/SFZ-backed recordings, riffs, loops and longer phrases where boundaries are reliable;
- export each approved candidate as an independently addressable derived WAV clip in staging, preserving the source recording untouched;
- record exact source start/end sample positions, source and derived SHA-256, estimated MIDI pitch/note and confidence, articulation/performance character, velocity/dynamic layer where detectable, parent asset and review/license status;
- prepare distinct pitch-specific note-zone candidates for both MELODY MODE and PATTERN MODE;
- for PATTERN MODE, associate compatible pitch-specific notes with the same selected articulation/performance style (for example palm mute or downstroke), so changing MIDI pitch changes the note sound without changing the selected playing character;
- retain whole takes, parent loops and coherent phrases as parent/reference assets, with child note clips linked to their exact source offsets;
- report uncertain boundaries, uncertain note estimates and missing pitch/articulation zones for human review rather than inventing labels or silently reusing unrelated sounds.

The Manager's output is consumed by the plugin's per-key playback engine: MIDI key → pitch-specific approved note clip → independent voice playback. The plugin handles real-time note-on/note-off, polyphony and release; the Manager handles source analysis, extraction, metadata, review and mapping preparation.

**Current implementation (2.4.0):** the optional full cycle now runs the physical extraction paths for pitch-specific Sample/Melody assets, repeated Pattern occurrences, and review-only chord/Power Chord sample candidates. Derived PCM WAVs and manifests are written only under LibraryManager/staging, then audited and indexed into the VST3 plugin asset catalog. Riff/Phrase remain review candidates unless the source evidence and musical review establish their identity. Chord analysis also feeds ARPEGGIO with bounded fretboard voicing hypotheses under an explicitly unconfirmed standard-tuning assumption. During explicit staged-asset review, the operator can assign one or more of the ten approved modes; this is how evidence-backed Strumming, Articulations and Ending material enters those queues without automatic guessing. Original source files remain read-only and are never moved or deleted by this workflow.


## Extract meaningful guitar patterns; keep full recordings optional

The Manager must not simply add every full WAV as the default asset. It must inspect the recording and identify coherent guitar sections by musical role and changing rhythm/articulation.

- Extract each useful, internally coherent rhythmic guitar passage or pattern as a separate derived WAV clip.
- When the rhythm or articulation changes, create separate candidates at reliable musical boundaries rather than bundling unlike sections into one asset.
- Preserve complete phrases and their natural attack/decay; do not arbitrarily chop a pattern into tiny events.
- Also derive child note/chord events where boundaries and pitch estimates are reliable, retaining parent/child provenance.
- Retain the complete original recording as an optional whole-take asset/reference. It may be offered as a separate user-selectable item, but it is not the default substitute for extracted patterns.
- The user must be able to choose the exact extracted pattern/phrase, an individual note asset, or the complete recording where that is deliberately wanted.
- Store extracted candidates in staging for preview and approval. Do not copy them into FACTORY automatically.

This does not make a full pattern or whole WAV the payload for ordinary MELODY MODE/PATTERN MODE key presses: those modes continue to use their individual pitch-specific note mappings. Full rhythm excerpts and whole takes remain separately selectable library assets for preview or other explicitly supported uses.

## Approved instrument architecture reference

The approved product direction follows the broad player-facing workflow of Native Instruments SESSION GUITARIST — ELECTRIC SUNBURST DELUXE, implemented with original code and legally distributable source material. The architecture has two complementary engines:

- **PATTERN INSTRUMENT:** chord input drives a selected guitar rhythm/pattern performance; chord changes adapt the harmony while retaining the selected pattern identity wherever mappings support it.
- **MELODY INSTRUMENT:** ordinary MIDI keys play pitch-specific individual note clips. The already-approved note-playable PATTERN MODE remains distinct: one key triggers one note clip with the selected articulation/performance character.

Do not create a third standalone CHORD/PERFORMANCE instrument: chord-driven pattern performance belongs to PATTERN INSTRUMENT. Do not confuse that chord-driven engine with the existing one-key/one-note PATTERN MODE contract. Pattern Browser, documented MIDI Key Switches, articulation/performance controls, host-tempo sync where supported, and the project's own effects/tone section are planned player-facing capabilities.

The Manager must prepare both kinds of content: pitch-specific note assets/mappings for MELODY INSTRUMENT and note-playable PATTERN MODE; coherent rhythm/pattern/phrase assets plus reviewed chord/performance mapping candidates for PATTERN INSTRUMENT. It must preserve provenance, confidence and license/review state, and keep derived audio in staging until approval.

**This is an approved target architecture, not a statement that the chord-performance engine, chord recognition, Pattern Browser, Key Switches or extraction pipeline are implemented.** See docs/KEYBOARD_PLAYBACK_SPEC.md, section 14, for the full requirements and acceptance criteria.

## 15. Two distinct playable content sets — PATTERN INSTRUMENT and MELODY INSTRUMENT

The Manager must prepare and classify source material according to the actual playback job it can serve. It is not enough to put every guitar WAV into one generic folder or make one universal mapping.

### A. PATTERN INSTRUMENT — chord-driven guitar patterns

Prepare coherent, musically useful performances for the chord-driven Pattern Instrument:
- full rhythm patterns, riffs, strumming figures, arpeggios and multi-bar phrases;
- power-chord and open-chord performances, chord progressions and chord changes;
- palm-muted, open, partially muted and mixed muted/open parts;
- downstroke, upstroke, alternate picking, chugging, syncopation, gallop, stops, accents and other verified rhythmic feels;
- genre/style tags across pop-punk and related guitar styles, plus tone and articulation tags;
- phrase boundaries, tempo/meter estimates, chord-event timelines and confidence where analysis supports them.

Keep the coherent pattern/phrase as a selectable asset. Where reliable, also create linked child chord, note and articulation events. Preserve the parent phrase and exact source offsets. Pattern Instrument mappings must identify which patterns can adapt to which chord qualities/voicings. Do not claim a pattern is chord-adaptable merely because it has a chord label; flag unsupported or uncertain chord mappings for review.

### B. MELODY INSTRUMENT — individual guitar notes

Prepare a separate pitch-specific playable note collection:
- each MIDI key maps to one appropriate individual recorded guitar note/zone;
- include clean, crunch, overdrive, distortion, acoustic and other available tone families;
- include verified articulation variants such as palm-muted, open, downstroke, alternate-picked, slide, bend, harmonic and sustain where actual samples exist;
- retain velocity/dynamic layers, round robins, string/fret/source-note information when present or reliably detectable;
- generate key-zone maps and explicit missing-note/articulation reports.

The Melody Instrument must not receive a whole riff, chord progression or rhythm loop as the payload for an ordinary note key. A key press plays one mapped guitar note only. Do not fill the keyboard by repeating one unrelated sample across all keys; any bounded pitch-shift fallback must be explicit and quality-controlled.

### C. Cross-library organization

A source recording may contribute to both engines, but the derived assets and mappings must remain distinct and linked to the same source provenance. One audio asset may have multiple verified style/category tags without making duplicate physical copies. Keep the user's single approved Samples root and its three folders unchanged. All newly derived assets remain in LibraryManager/staging until review and license approval.

### Acceptance checks

1. Pattern Instrument browser exposes coherent rhythm/phrase assets and their verified chord/performance compatibility.
2. Melody Instrument mapping exposes pitch-specific individual guitar notes, not full patterns or chord progressions.
3. The same source may produce linked assets for both engines without losing parent/child provenance.
4. Missing pitch zones or unsupported chord adaptations are reported, never silently fabricated.
5. Pattern and Melody assets can be previewed independently and are routed to the correct engine.


## 16. Mandatory PATTERN MODE product workflow reference

The PATTERN MODE player workflow must be designed and implemented to follow the high-level interaction mechanics of Native Instruments SESSION GUITARIST – ELECTRIC SUNBURST DELUXE Pattern mode. This is a mandatory functional benchmark, not merely a visual reference. The selected pattern/playing feel remains consistent while the player's MIDI notes determine the changing pitches. Pattern selection, playable keys, key switches, dynamics, note lengths/release and articulation changes must work as one coherent playable instrument. Do not trigger a fixed prerecorded riff on every key. Prepare pitch-specific note assets and mappings for the playable range, report missing notes, and disclose any bounded pitch-shift fallback. Keep this separate from the chord-driven PATTERN INSTRUMENT workflow. Use only original implementation, original UI and properly licensed audio; do not copy proprietary code or protected assets. See `docs/KEYBOARD_PLAYBACK_SPEC.md`, section 17, for acceptance criteria.


## 17. First implemented extraction primitive — reviewed WAV ranges (0.1.0)

`asset_pipeline.py` now provides a real, tested foundation for creating derived audio clips without touching the source:
- extracts an explicitly reviewed sample-frame range from uncompressed PCM WAV;
- preserves source sample rate, channels and sample width;
- writes the derived clip only to `LibraryManager/staging/clips`;
- creates a JSON sidecar with source/derived SHA-256, exact sample/time offsets, parent ID, asset kind, engine targets, extractor version and review/license status;
- allows one derived clip to target more than one engine without making duplicate audio copies;
- rejects invalid ranges, unsupported engines and unsupported compressed WAV input.

This is intentionally a **reviewed-boundary extraction primitive**, not automatic musical segmentation. It does not yet detect notes, chords, bars, loops, tempo, articulation or phrase boundaries by listening to audio. Those require subsequent analysis modules and dedicated test fixtures. Source files remain unchanged, and staged clips are not promoted to FACTORY.


## 18. First-pass acoustic WAV analysis (0.1.0)

`audio_analysis.py` adds a dependency-free first-pass analysis report for uncompressed PCM WAV:
- decodes 8/16/24/32-bit PCM and down-samples analysis workload for long files;
- reports duration, sample format, peak and frame-RMS level statistics;
- reports zero-crossing-rate evidence;
- estimates a dominant monophonic pitch candidate with confidence when the signal supports it;
- reports onset/energy-change timestamps as **evidence only**;
- reports an approximate tempo candidate when the onset envelope supports one;
- writes JSON to stdout or a requested report path.

Run:
`python audio_analysis.py "path/to/guitar.wav" --output reports/audio_analysis.json`

**Limitations:** this is not yet polyphonic guitar transcription, chord recognition, key detection, reliable meter/bar inference, articulation classification, musical phrase segmentation or automatic clip extraction. Distorted/polyphonic material can confuse pitch estimation. Onsets are not automatically treated as phrase boundaries. Results are candidates and must carry confidence/review status. No source audio is modified.


## 19. Conservative preview-region candidate builder (0.1.0)

`candidate_builder.py` converts onset timestamps from an `audio_analysis.py` JSON report into bounded preview-region candidates. Nearby onset evidence is grouped; each region receives a short pre-roll and tail. Very long groups are split only to cap preview duration.

This is a real candidate-generation step, but it is deliberately **not musical segmentation**. The output uses `kind=audio_region_candidate`, `review_status=NEEDS_MUSICAL_REVIEW`, `license_status=UNREVIEWED`, and no fabricated confidence score. It may miss sustained/legato passages that have no detected onset evidence. Candidate boundaries must be listened to and approved before passing exact sample offsets to `asset_pipeline.extract_reviewed_wav`.

Run after acoustic analysis:
`python candidate_builder.py reports/audio_analysis.json --output reports/region_candidates.json`

No source audio is modified, no candidate is automatically extracted, and nothing is promoted to FACTORY.


## Monophonic pitch-event candidates (0.3.0 development stage)

`pitch_events.py` adds a bounded frame-based YIN-style pitch tracker for WAV review:
- estimates a pitch hypothesis for short overlapping frames;
- groups stable adjacent estimates into time-bounded note-event candidates;
- exports MIDI-note candidates, note names, timing and confidence to JSON;
- marks every event `NEEDS_MUSICAL_REVIEW` and every source license `UNREVIEWED`.

Run from `LibraryManager`:

```bat
python pitch_events.py "path\\to\\guitar.wav" --output reports\\pitch_events.json
```

This stage is deliberately monophonic. It is useful for isolated notes and some clean single-note passages, but it is not chord recognition or reliable transcription of dense/distorted guitar. Octave errors, harmonics, overlapping notes and frame-boundary uncertainty must be reviewed. It does not classify palm mute, picking direction, string, velocity layer or instrument role. It never changes source audio; only the separate reviewed extraction tool may create derived files in staging.

Regression coverage: `test_pitch_events.py` checks a 440 Hz tone, a two-note pitch change, silence and invalid parameters. GitHub Actions runs the full `test_*.py` suite on push and pull request.


## Experimental polyphonic pitch candidates (0.1.0)

`polyphonic_candidates.py` adds a dependency-free spectral candidate stage:
- evaluates MIDI-range fundamentals with weighted harmonic support using a bounded Goertzel analysis;
- tracks simultaneous pitch hypotheses across overlapping frames;
- exports time-bounded pitch-event candidates with salience/confidence and provenance;
- marks every event `NEEDS_MUSICAL_REVIEW` and every source license `UNREVIEWED`.

Run from `LibraryManager`:

```bat
python polyphonic_candidates.py "path\\to\\guitar.wav" --output reports\\polyphonic_candidates.json
```

This is **not chord recognition or verified polyphonic transcription**. Spectral peaks and harmonic support can be misleading on distorted guitars, dense mixes, detuned notes and phase-cancelled recordings. The module does not assign chord names, inversions, strings, frets, articulations, velocity layers or engine roles. All results require listening and human review. It reads source WAV only and never extracts, moves or modifies audio. Regression tests use synthetic simultaneous tones and silence.


## Conservative WAV asset-kind classifier (0.1.0)

`asset_classifier.py` adds a first-pass distinction between short one-shot sounds and longer sample assets using duration plus frame-RMS envelope evidence.

- Short recording + one/few attacks + decaying tail → `ONE_SHOT / NOTE_ONE_SHOT` candidate.
- Longer recording + repeated reasonably regular envelope attacks → `SAMPLE / RHYTHMIC` candidate.
- Longer recording with several separated attacks → `SAMPLE / MULTI_HIT` candidate.
- Longer sustained energy without repeated attacks → `SAMPLE / SUSTAIN` candidate.
- Ambiguous or silent material → `UNKNOWN`.
- `loop_candidate` is separate from `SAMPLE`; it is only raised for strongly repeated rhythmic evidence and never means a seamless loop has been confirmed.

Run:
`python asset_classifier.py "path/to/guitar.wav" --output reports/asset_classification.json`

The classifier returns confidence, evidence, onset timestamps, review status and license status. It does not infer melody/chord labels or guitar articulations; those require their dedicated analysis stages. All classifications remain `NEEDS_MUSICAL_REVIEW`, all licenses remain `UNREVIEWED`, and source audio is read-only. Thresholds can be adjusted with `--short-max` and `--long-min`.

Regression tests cover a short decaying note, a long repeated pulse train, a sustained tone, silence and source-file immutability.


### Rhythm patterns, guitar melodies and note-fragment proposals

The asset classifier now keeps the fact that a file is a `SAMPLE` separate from the musical content inside it:

- `RHYTHM_PATTERN` / `REPEATING_GUITAR_RHYTHM`: repeated, relatively stable pitch content with recurring attacks.
- `RHYTHMIC_MELODY` / `GUITAR_MELODY_WITH_RHYTHMIC_PULSE`: recurring rhythmic attacks while the detected pitch sequence changes.
- `MELODIC` / `GUITAR_MELODY`: changing note candidates without a sufficiently stable repeated pulse.
- `SUSTAIN`, `MULTI_HIT` and `UNKNOWN`: retained as separate content candidates.

Where the monophonic pitch tracker detects note events, the report includes `fragment_candidates`: suggested start/end times, note names, MIDI candidates and confidence. These are cut-point proposals for later library preparation, not exported audio clips yet. The next processing stage must validate boundaries, preserve tails/decays, avoid cutting attacks, and write derived clips only into the approved staging area while leaving originals untouched. Polyphonic chords and distorted guitar phrases must remain review candidates until a suitable polyphonic/segmentation stage can validate them.

## Conservative Audio Segmenter (0.1.0)

`audio_segmenter.py` is the first opt-in extraction stage for monophonic note-event candidates.

- Dry-run is the default: it reports proposed source sample ranges and creates no audio files.
- It consumes the existing pitch-event candidates and adds configurable pre-roll/post-roll so the pick attack and note decay are less likely to be cut off.
- Extraction requires the explicit `--extract` flag and is restricted to `LibraryManager/staging`.
- Derived PCM WAV clips preserve the source sample rate, channel count and sample width. Each clip receives a JSON sidecar with exact sample/time offsets, source and derived SHA-256, pitch candidate, confidence, parent provenance and review/license status.
- Stable content-derived IDs make a repeated extraction refuse to overwrite an existing clip or manifest.
- Source hashes are checked before and after extraction. Originals are never modified and staged material is never promoted to FACTORY.

Dry-run:
`python audio_segmenter.py "path/to/guitar.wav" --output reports/segment_proposals.json`

Explicit staging extraction:
`python audio_segmenter.py "path/to/guitar.wav" --extract`

**Important limitations:** this is a conservative monophonic note-event segmenter, not complete musical transcription. It does not yet identify polyphonic chord boundaries, reliable reverb-tail endpoints, bars, coherent rhythm phrases, repeated riffs, strings, frets, palm mute or picking articulation. Pre-roll/post-roll are safeguards, not proof that every attack or effect tail is preserved. All outputs remain `NEEDS_MUSICAL_REVIEW` and `UNREVIEWED`; listen before approval. Use the reviewed-range extraction workflow when exact musical boundaries have been approved.



## Experimental spectral landmark fingerprints (0.1.0)

`audio_fingerprint.py` adds the first deterministic, dependency-free fingerprint foundation:
- computes windowed FFT spectral peaks and pairs nearby peaks into versioned time-frequency landmark hashes;
- compares landmark hashes and estimates a coarse time offset;
- reports a possible shared recorded passage only when there is sufficient aligned evidence;
- keeps every result in `NEEDS_MUSICAL_REVIEW` and explicitly marks comparison as report-only.

Run:
`python audio_fingerprint.py "path/to/guitar.wav" --output reports/fingerprint.json`

Compare a new WAV against a previously generated fingerprint JSON:
`python audio_fingerprint.py "path/to/other.wav" --compare reports/fingerprint.json`

**Important boundary:** this is an experimental fingerprint foundation, not a production-grade Shazam implementation. It is intended to find possible shared recorded material or derivatives. It does not identify that two different performances play the same riff, and it does not calculate timbre/rhythm/melody/chord/riff similarity. Those remain separate analysis dimensions. A fingerprint match is never permission to delete, merge, suppress or automatically route assets. Originals remain untouched.


## Read-only batch fingerprint index (0.1.0)

`fingerprint_index.py` applies the experimental landmark fingerprint stage to an incoming folder:
- recursively discovers WAV/WAVE files;
- fingerprints files in parallel with a bounded worker count;
- builds an inverted landmark index to shortlist possible shared-recording candidates without comparing every file pair;
- reports exact SHA-256 duplicate groups separately from possible audio-passage relationships;
- records per-file analysis errors and a safety declaration;
- never changes, moves, deletes, merges or routes source files.

Run from `LibraryManager`:

```bat
python fingerprint_index.py "..\\Samples\\Import Sample Guitar" --output reports\\fingerprint_relationships.json
```

The index currently uses in-memory candidate generation and has a hard cap of 100,000 candidate pairs. It is an initial batch foundation, not yet a persistent/resumable fingerprint database. Fingerprint relationships remain review-only. Similar riffs, tones, rhythms, melodies and performances are not duplicates; musical similarity analysis is a separate future subsystem.


## Primary organization target: sound, musical content and guitar identity

The Manager's main job is to prepare a deeply classified, searchable and playable guitar sample library—not merely to find duplicate files. Classification is multi-axis: one asset may carry several verified tags without creating duplicate copies.

Required independent dimensions:
- **Asset/content:** one-shot, individual note, chord, note sequence, melody phrase, rhythmic melody, rhythm pattern, riff, loop candidate/confirmed loop, multi-hit, sustain, full take and ambience/effect.
- **Instrument:** electric guitar, acoustic guitar, nylon guitar, steel-string guitar, bass guitar and unknown/other.
- **Tone:** clean, edge-of-breakup, crunch, overdrive, distortion, fuzz, natural acoustic, processed and DI.
- **Playing/articulation:** open, palm mute, muted, downstroke, upstroke, alternate/tremolo picking, chugging, arpeggio, strum, finger-picked, slide, bend, harmonic, legato, staccato and sustain.
- **Musical role and style:** rhythm guitar, lead, melody, chords, arpeggio, bass line, texture; pop-punk, punk rock, skate punk, alternative rock, power pop, pop rock, emo and related styles.
- **Musical coordinates:** note/pitch, chord/root/quality, key and mode candidates, tuning, BPM/range, meter, beat unit and groove.
- **Arrangement structure:** intro, verse, pre-chorus, chorus, post-chorus, bridge, breakdown, solo, interlude, outro, fill and turnaround, each with exact source time bounds when evidence supports them.

The module classification_schema.py defines a controlled multi-axis metadata schema. Unknown or unverified fields stay explicitly UNKNOWN/null; it is forbidden to invent a key, chord, tempo, guitar type, style or song section merely to fill a folder. Every proposed label carries confidence/evidence and remains review-pending until checked. The schema validates source provenance, review/license states and the no-destructive-action rule.

### Segmentation and library preparation order

1. Preserve and inventory the incoming original; calculate SHA-256 and retain provenance.
2. Analyze the complete recording before cutting: instrument/tone evidence, attacks, notes, simultaneous pitches, rhythm, tempo, tonal center/key, chord candidates and arrangement changes.
3. Identify coherent musical regions: individual sounds/notes, chords, rhythmic hits, riffs, melody phrases, rhythm patterns, loops and larger song sections.
4. Propose boundaries with pre-roll and natural decay/reverb tails; preserve full parent recording and exact sample/time offsets.
5. Generate child clips/manifests only in LibraryManager/staging; link every child to its parent and retain hashes, confidence, analyzer version and license state.
6. Tag and group assets by all verified dimensions. Do not make physical copies merely to place one sound in several searches/categories.
7. Human review confirms musical labels, loop boundaries, tonalities, style and license before a staging asset can be considered for FACTORY.

A loop is not confirmed just because attacks repeat. A key/scale or chord is not confirmed from one uncertain pitch estimate. Structure labels require change/boundary evidence. Similarity helps find and group candidates but never authorizes deletion or merging. Original files are never moved, renamed, overwritten or deleted.


## Rhythm evidence analyzer (0.1.0)

`rhythm_analysis.py` adds a separate rhythm-analysis stage that consumes the onset evidence from `audio_analysis.py`:
- calculates inter-onset intervals and a rhythmic-regularity candidate;
- ranks plausible BPM hypotheses, retaining half-time/double-time ambiguity instead of asserting one definitive tempo;
- creates a quantized interval-contour descriptor for search and grouping;
- marks stable pulse patterns as candidates only, with musical review required.

Run:
`python rhythm_analysis.py reports/audio_analysis.json --output reports/rhythm_analysis.json`

The descriptor is **not a duplicate identifier** and must never be used to delete, merge or suppress assets. Repeated attacks do not prove a loop seam, meter, downbeat, groove, riff or identical performance. Results inherit the limitations of onset detection and remain review-pending and license-unreviewed. This module reads reports only and does not alter audio.


## Explicit musical-tag review bridge (0.1.0)

`manifest_reviewer.py` connects staged clip manifests to the FACTORY curator without inventing missing classification data. A human must listen to/review the clip and explicitly supply all three primary folder tags: instrument family, asset role and tone family.

Example (run from `LibraryManager`):

```bat
python manifest_reviewer.py "staging\\clips\\<asset-id>.json" --instrument ELECTRIC_GUITAR --role RHYTHM_PATTERN --tone DISTORTION --reviewed-by "your reviewer ID" --confirm-musical-review
```

The command:
- validates the manifest and derived WAV are inside staging and that the WAV SHA-256 matches;
- accepts only the controlled FACTORY folder vocabulary;
- preserves all existing musical metadata and adds the three explicitly supplied primary tags;
- marks musical review complete only after the explicit confirmation flag;
- records who reviewed the tags and when;
- **does not change license_status**. A separate license review must set `LICENSE_APPROVED` before the curator will accept the asset;
- writes the manifest atomically and never edits the staged WAV or original source.

Then run `factory_curator.py` in dry-run mode to inspect the proposed folder and gates. Actual copying still requires a separate explicit `--approve`. No automatic promotion or overwrite is allowed.


## Development release 1.8.0

The v1.8 development branch adds a dedicated OTHER audit and explicit decision-file based routing, whole-Import dependency audit for cleanup, corrected pattern extraction report integration, transactional extraction rollback, and a Windows x64 PyInstaller packaging workflow.

See [V1_8_RELEASE_NOTES_RU.md](V1_8_RELEASE_NOTES_RU.md) for implemented behavior, safety rules, launch/build steps and remaining limitations. A passing CI suite does not establish musical correctness or replace real-library listening tests.


## Журнал задач 2.1.0

История фоновых задач, этапов, успешных завершений и ошибок описана в [TASK_JOURNAL_RU.md](TASK_JOURNAL_RU.md). Журнал расположен в `LibraryManager/reports/task_history.jsonl` и не возобновляет прерванные операции автоматически.


## VST3 integration catalog — Library Manager 2.4.0

The full preparation cycle now produces a versioned `plugin_asset_catalog.json` after extraction and staging audit. The catalog contains all ten approved Manager/VST3 mode sections, analysis-only candidates, staged WAV references, source hashes, exact source sample offsets, pitch/chord hypotheses, articulation and velocity metadata where available, and explicit review/license/integrity states.

- SAMPLE MODE receives pitch-specific note clips plus review-only chord and Power Chord sample clips.
- PATTERN MODE receives repeated-rhythm pattern clips and note-event zones that are explicitly marked for this note-playable mode.
- MELODY MODE receives grouped melody phrase candidates and pitch-specific source notes.
- RIFF MODE and PHRASE MODE receive only evidence-backed candidate references; irregular onset groups are not asserted to be finished riffs or complete phrases.
- STRUMMING, ARTICULATIONS and ENDING remain explicit manual-review queues until source evidence supports their musical identity. ARPEGGIO receives generated voicing hypotheses from chord pitch classes, but tuning, fingering and string attacks remain unverified. Generic onset/RMS analysis is not used to invent stroke direction, articulation or ending role.
- Long RMS-active regions are retained as unassigned review assets; they are not automatically labeled Pattern, Riff or Phrase.

The catalog's WAV paths are relative to the catalog file and resolve into `LibraryManager/staging`. It is a bridge contract for the future VST3 loader, not a compiled plugin or a packaged factory sound bank. A staged asset becomes runtime-playable only after its derived/source hashes and sample boundaries validate and its manifest contains explicit `REVIEWED` + `LICENSE_APPROVED` evidence. No automatic FACTORY promotion occurs.

The GUI adds **Сформировать каталог VST3** and **Sample Browser / режимы VST3**. A full cycle also generates the catalog and a versioned `performance_manifest.json` automatically; the Performance Manifest contains asset bindings and a strict event contract, while its event timeline stays empty until reviewed musical timing data exists. See `docs/PPGU_PLUGIN_ASSET_CATALOG_RU.md` for the contract and mode mapping.


## Единая карта всех 12 нот и Auto Chords

Manager 2.5.0 формирует единую хроматическую карту для будущего VST3:
- все 12 pitch classes представлены отдельно и доступны в объявленном MIDI-диапазоне;
- Sharp/Flat — два способа подписать одну высоту, а не разные ноты;
- C# = Db, D# = Eb, F# = Gb, G# = Ab, A# = Bb;
- E и F остаются двумя разными нотами;
- Auto Chords использует ту же карту pitch class и объединяет только энгармонические дубликаты;
- хроматические ноты не удаляются из клавиатурного диапазона из-за выбранной тональности или текущего аккорда.

При сборке каталога Manager экспортирует chromatic_pitch_map JSON и включает эту же карту в Performance Manifest для VST3. Точные sample mappings требуют подтверждённых MIDI-нот, лицензии и integrity status. Fallback для отсутствующего WAV записывается как предложение QA, а не как готовый runtime asset.

**Граница реализации:** текущий репозиторий содержит Manager и manifests, но отдельного C++/JUCE VST3 playback source tree здесь пока нет. Поэтому карта и контракт подготовлены для плагина; реальное звучание каждой клавиши требует реализации VST3 playback/fallback engine и аудио-QA.


## 3.0 development: reviewed multi-mode assignment index

The unified run now emits `reviewed_mode_assignment_index.json` beside the analysis-only `mode_sorting_report.json`. These are intentionally separate:
- analysis report = evidence-backed hypotheses requiring listening review;
- reviewed assignment index = explicit `mode_assignments` saved by the human review workflow, with WAV hash validation and per-mode runtime blockers.

All ten approved modes are always represented. One staged WAV can be logically assigned to several modes without physical duplication. An assignment is not automatically runtime-ready: the index checks musical review, license approval, derived WAV integrity, and mode-specific mapping gates. Unknown or missing evidence remains a blocker, never a fabricated note or articulation.

Version 3.0 remains a development build until the complete Windows regression suite, portable package smoke test, real-library validation, and user-side workflow checks are successful.

## Manager 3.0 — plugin library structure and coverage

The **Сформировать каталог VST3** action now produces four coordinated artifacts beside the catalog:
- `plugin_asset_catalog_*.json` — validated asset and ten-mode queues;
- `plugin_library_structure_*.json` — logical library layout for SAMPLE, PATTERN and MELODY engines, with all ten Manager mode sections and provenance-linked asset references;
- `plugin_library_coverage_*.json` — explicit coverage/gap report for 12 pitch classes, LOW/MEDIUM/HIGH velocity layers, confirmed techniques, Pattern event structure and Melody note/event timing;
- `chromatic_pitch_map_*.json` and `performance_manifest_*.json` — shared chromatic mapping and runtime contract.

The structure builder does not copy WAV files. One physical staged asset may be referenced from several modes by stable asset ID. Techniques count as covered only when explicitly confirmed in reviewed metadata. Unknown velocity zones, note pitches, articulation labels, Pattern loop/grid fields and Melody event timing remain visible gaps. A runtime-ready row must pass musical review, license approval, integrity validation and the existing mode-specific playback gate. A structurally complete JSON does not mean the underlying mode is already playable in the VST3.


### 3.0-dev3 — review metadata for real library structure

The manual review dialog now records explicit technique tags (Downstroke, Upstroke, Palm Mute, Open, Slide, Legato, Hammer-on, Pull-off, harmonics, tremolo, choke, let-ring and dead-note), a confirmed velocity layer, and optional structured Pattern/Melody event data. Pattern metadata is validated for loop boundaries inside the staged WAV, BPM, meter, attack/beat-grid/technique/harmonic events and cycle/review confirmations. Melody metadata is validated for MIDI pitch, ordered beat positions, durations, velocity and phrase boundaries. Blank/unknown fields are not guessed; they remain coverage gaps. A new review revokes old confirmed tags unless the reviewer confirms them again.


## Manager 3.0-dev6 — ускорение инвентаризации и транзакционное распределение

- Быстрый filesystem scan не вычисляет SHA-256 и не декодирует аудио; строки inventory записываются потоково в CSV, поэтому память не растёт пропорционально числу файлов.
- Для глубокого прохода без DSP используется до двух ограниченных рабочих потоков. При включённом тяжёлом акустическом анализе значение по умолчанию — один поток, чтобы не перегружать старые двухъядерные компьютеры. CLI позволяет явно выбрать --workers 1 или --workers 2.
- SQLite cache readers переиспользуются внутри каждого рабочего потока вместо открытия нового соединения на каждый файл. Кэш хэшей и аудиоанализа остаётся на диске; исходники только читаются.
- Распределение FACTORY в GUI и CLI выполняется через единый транзакционный пакет: сначала пересобирается и проверяется весь план, затем проверяются коллизии путей/хэшей, затем копируются файлы. При ошибке или отмене удаляются только назначения, созданные данной транзакцией; rollback фиксируется в operations.jsonl. Исходники и staging не перемещаются и не удаляются.
- Добавлен regression test для отката частично скопированного пакета и защиты уже существующего файла.

Это development build. Скорость зависит от диска, числа файлов и размера библиотеки; числовые гарантии производительности без измерения на конкретном компьютере не заявляются. Windows Portable smoke test и полный прогон тестов должны быть подтверждены отдельным успешным CI/локальным запуском.
