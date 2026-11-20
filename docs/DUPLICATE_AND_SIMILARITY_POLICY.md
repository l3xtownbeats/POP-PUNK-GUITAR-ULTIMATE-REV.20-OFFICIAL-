# Duplicate detection versus musical similarity policy

## Non-negotiable rule

**Similarity is not duplication.** The Library Manager must never delete, merge, overwrite, suppress, or discard an audio asset merely because it has a similar timbre, tone, pitch, chord, riff, rhythm, note sequence, tempo, envelope, or musical role to another asset.

Duplicate detection and musical analysis are separate systems with separate outputs and separate decision rules.

## Classification dimensions

Every comparison must keep these dimensions separate:

1. **Exact file duplicate** — identical SHA-256 bytes. This is the only automatic, definitive duplicate identity currently accepted.
2. **Technical derivative / near-duplicate candidate** — potentially the same performance rendered, encoded, trimmed, normalized, resampled, or processed differently. This is only a review candidate, never an automatic deletion decision.
3. **Timbre similarity** — similar guitar tone or spectral character (for example same amp/pickup/effect family). This is descriptive metadata, not duplication.
4. **Musical-content similarity** — similar notes, intervals, chord progression, rhythm, riff contour, or phrase. This is a musical relationship, not duplication.
5. **Performance similarity** — similar playing pattern or articulation. Different takes, timing, dynamics, velocity, pick attack, muting, string/fret choices and human feel remain distinct performances.
6. **Unique asset** — no supported relationship has been established.

A file can be similar in several dimensions and still be a valuable independent library asset.

## Examples that must remain separate

- Same riff played with clean, crunch, overdrive and distortion tones.
- Same chord progression played with different voicings, inversions, strings or frets.
- Same notes played as palm-muted downstrokes versus open alternate picking.
- Same phrase performed with different timing, dynamics, velocity, attack, decay or reverb tail.
- Same rhythm recorded as separate takes.
- Same melody played in a different octave or on a different string.
- Two unrelated performances that happen to have similar spectral/timbre fingerprints.

These may be linked by tags or similarity relationships, but their audio files and asset records must remain independently addressable.

## Allowed automated behavior

- Group byte-identical files by SHA-256 and report their paths.
- Compute audio fingerprints and similarity scores as evidence only.
- Store separate scores for timbre, rhythmic pattern, pitch/interval sequence, chord progression, phrase contour and performance/articulation when those analyzers become reliable.
- Create relationship edges such as `EXACT_BYTE_DUPLICATE`, `POSSIBLE_DERIVATIVE`, `SIMILAR_TIMBRE`, `SIMILAR_RHYTHM`, `SIMILAR_MELODY`, `SIMILAR_CHORD_SEQUENCE`, `RELATED_PERFORMANCE`.
- Preserve confidence, evidence, analyzer version, source hashes and review status for every relationship.
- Let the user filter, compare, audition and manually decide what to keep.

## Forbidden behavior

- No automatic deletion based on perceptual/audio similarity.
- No merging two assets because they share a timbre or note sequence.
- No treating a repeated riff as a duplicate of another recording.
- No removing alternate takes, velocity layers, round robins, articulations, tone variants or different performances.
- No replacing a source asset with a supposedly “better” similar asset.
- No destructive deduplication during scanning, classification, segmentation or factory preparation.

## Required data model separation

Duplicate identity belongs to a file-integrity layer. Musical and timbral similarity belongs to an analysis/relationship layer. Asset classification and segmentation belong to their own layers.

A recommended comparison record contains:
- `relationship_type`
- `source_asset_id` and `target_asset_id`
- `source_sha256` and `target_sha256`
- `similarity_score` (nullable; never reinterpret as duplicate certainty)
- independent optional scores: `timbre_score`, `rhythm_score`, `pitch_sequence_score`, `chord_sequence_score`, `phrase_score`, `performance_score`
- `evidence`, `analyzer_version`, `review_status`
- `action_allowed = NONE_AUTOMATIC`

The current scanner's exact SHA-256 report is a report only. Any future near-duplicate or similarity analysis must preserve this policy and remain non-destructive.
