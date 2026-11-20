# Shazam-inspired audio intelligence architecture

## Product principle

The Library Manager uses the core idea behind audio fingerprinting systems such as Shazam: transform audio into compact, comparable representations, find meaningful correspondences, and use those correspondences to help identify and organize material.

However, this product is not only a song-identification service. It must analyze, relate, segment, classify and prepare guitar assets for a playable sample library. Therefore fingerprint matching is one shared foundation, not a substitute for musical analysis.

## End-to-end pipeline

1. **Ingest and preserve** — inventory source files, calculate SHA-256, record format and provenance. Originals remain read-only.
2. **Fingerprint generation** — build versioned, deterministic audio fingerprints from time-frequency landmarks and other robust features. Keep the source hash and analysis settings with every fingerprint.
3. **Candidate matching** — compare fingerprints to find exact identity or possible shared source/performance evidence. Matching returns ranked relationships and evidence, not destructive actions.
4. **Independent feature analysis** — calculate separate evidence for timbre, rhythm, pitch/interval sequence, polyphonic note activity, chord candidates, phrase contour and performance/articulation. Never collapse these dimensions into one generic similarity score.
5. **Musical event analysis** — identify candidate note events, simultaneous note groups, chord events, attacks, pauses, sustained regions and phrase boundaries. Preserve uncertainty and overlapping events; do not force polyphonic audio into a monophonic answer.
6. **Phrase and riff analysis** — group events into coherent musical phrases; compare ordered pitch and timing patterns to find repeated or related riffs, including repetitions within one recording and across recordings.
7. **Asset classification** — determine the useful role of each source and derived candidate: one-shot, individual note, chord event, melody phrase, rhythmic melody, stable rhythm pattern, riff, multi-hit, sustain, loop candidate, full take, etc. Classification is multi-label where appropriate and retains the original parent asset.
8. **Staging and review** — create derived clips and manifests only in LibraryManager/staging. Keep exact source offsets, parent-child links, hashes, confidence, evidence, analyzer versions and license/review states.
9. **Library routing proposal** — recommend a destination and tags for reviewed assets under the approved SAMPLES structure. Do not move or promote source or derived assets automatically; FACTORY admission requires review and license approval.

## Fingerprinting is not musical understanding

A Shazam-like landmark fingerprint is useful for recognizing matching audio passages even when the recording has some noise or playback changes. It can help answer: Have we heard this same recorded passage before? It does not, by itself, answer which notes or chords are played, whether a passage is a melody or rhythm guitar, where musical phrases begin and end, whether similar passages are different performances, or which articulation, string, fret, velocity layer or guitar tone is present.

Those answers require dedicated analyzers and, where necessary, human audition/review.

## Separate relationship dimensions

Store relationships independently, for example:
- EXACT_BYTE_DUPLICATE — identical SHA-256 bytes;
- POSSIBLE_AUDIO_DERIVATIVE — possible same performance after processing, trimming, encoding or gain changes;
- SAME_RECORDED_PASSAGE — fingerprint landmarks align over a time span;
- SIMILAR_TIMBRE — similar tone/spectral character;
- SIMILAR_RHYTHM — similar onset and duration pattern;
- SIMILAR_MELODY — similar ordered pitch/interval contour;
- SIMILAR_CHORD_SEQUENCE — similar chord-event sequence;
- SIMILAR_RIFF — related musical phrase/riff structure;
- RELATED_PERFORMANCE — similar articulation or playing behavior.

Each relationship stores its own confidence, evidence, analyzer version, source offsets and review state. A relationship can have multiple independent dimensions.

## Critical non-destructive rule

**No fingerprint or similarity result may delete, merge, overwrite, suppress or automatically discard an asset.**

Two files can contain the same riff but be valuable different recordings. A riff played with clean, crunch and distortion tones, different palm muting, picking, voicing, octave, dynamics, timing or reverb remains separately addressable. Similarity supports grouping, search, comparison, audition and tagging only.

Only byte-identical SHA-256 files qualify as confirmed exact duplicates in the current policy, and even those are reported rather than automatically deleted. Possible derivatives remain review-only.

## Output model

Every analysis result must retain stable asset ID and parent asset ID; source path and source SHA-256; exact time/sample offsets when applicable; fingerprint and feature schema versions; separate similarity scores (nullable, never treated as duplicate certainty); note/chord/phrase candidates with confidence and evidence; classification labels and review status; license status; proposed destination/tags; and automatic_destructive_action = NONE.

## Approved storage boundaries

Keep the single approved library root and folders unchanged:
- SAMPLES/FACTORY — approved, checked and organized library;
- SAMPLES/Import Sample Guitar — incoming material;
- SAMPLES/OTHER — unsuitable, damaged or unidentified material.

All derived files and analysis artifacts are staged first in LibraryManager/staging. Never modify, rename, move or delete originals. Never promote staging output to FACTORY automatically.

## Implementation status

This document defines the target architecture. Existing modules provide partial foundations for acoustic analysis, monophonic pitch candidates, experimental polyphonic pitch candidates, coarse asset classification and conservative note-event extraction. They do not yet constitute a complete Shazam-style robust fingerprint matcher, reliable polyphonic guitar transcription, chord recognition, phrase/riff recognition or automatic library router. Each capability must be implemented and regression-tested independently before it is described as available.