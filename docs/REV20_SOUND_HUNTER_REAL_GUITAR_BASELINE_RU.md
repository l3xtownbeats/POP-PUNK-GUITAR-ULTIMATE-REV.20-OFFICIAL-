# REV.20 — SOUND HUNTER / REAL-RECORDED GUITAR BASELINE

**Status:** PORTED AS ENGINEERING/ACQUISITION PIPELINE · AUDIO PAYLOAD NOT ACQUIRED · 500 PRESETS NOT READY

## 1. Approved source class

Only explicitly catalogued REAL_RECORDED guitar sources may enter the product sample pipeline.

- Meta Open Sound — Steel Guitar
- Meta Open Sound — Nylon Guitar
- FreePats electric guitar clean / direct / distorted / jazz
- FreePats Spanish Classical Guitar
- Karoryfer Black and Green Guitars
- Karoryfer Emilyguitar
- Karoryfer Shinyguitar

The catalog records expected CC0-1.0 licensing and the exact license file to verify. Importer code still verifies the actual downloaded license text and release SHA256SUMS before admitting audio.

## 2. Safety contract

The Sound Hunter importer is additive only. It creates a unique Samples/SoundHunterImports/<run-id> destination and never overwrites, moves, renames or deletes existing user/sample-library files.

It verifies safe archive paths and traversal rejection, license evidence, release license evidence, SHA-256 of LFS/audio payloads, SHA256SUMS inside release bundles, exact file sizes, duplicate-content suppression by SHA-256 and bounded transport splitting.

## 3. Library-size reconciliation

The source Sound Hunter code uses an unlimited/no-hard-cap policy. In REV.20 this means **no artificial maximum**:

- BASIC LIBRARY: minimum 15 GB, included in the standard product.
- EXPANDED: optional +15 GB initial tier; 30 GB combined at the initial tier.
- The library may grow beyond those initial values when additional unique, legal, high-quality content is justified.
- Never pad the library with duplicate or lower-quality content to hit a number.

The transport splitter part size is a GitHub artifact-transfer setting, not a product library limit.

## 4. Preset binding baseline

The inherited 300-definition candidate binding plan is stored as presets/rev20_sound_hunter_binding_plan.json.

It is planning only: 150 MELODY + 150 PATTERN, READY=0. No entry becomes a playable/approved factory preset until preset-specific source mapping, root-key/velocity/round-robin evidence, license evidence, target runtime playback and listening QA exist.

## 5. Execution status on REV.20

Source review found no completed Sound Hunter GitHub Actions run that can be used as evidence of a successful acquisition. Therefore:

- Pipeline present: YES
- Importer tests: pending new target CTest run after this port
- Real-guitar audio payload acquired: NO EVIDENCE / NOT CLAIMED
- Preset mappings READY: 0 in the copied planning baseline
- 500 playable presets: NOT COMPLETE

## 6. Manual workflow

.github/workflows/rev20-sound-hunter-real-guitar.yml is workflow_dispatch only.
- acquire_samples=false runs discovery and regression contracts without downloading audio.
- acquire_samples=true explicitly performs acquisition, audit, SHA-verified packaging and artifact upload.

This prevents an ordinary code push from silently starting a large external sample download.

## 7. Legal boundary

Only libraries whose actual licensing permits bundle/redistribution into the plugin may be shipped. Proprietary sound libraries remain tonal/playability references, not copy sources.


## 2026-11-20 — acquisition workflow diagnostic

Target run 44722586113 proved the discovery and three regression test suites pass, but the first real source download stopped on the Meta Open Sound zipball containing multiple LICENSE files. The importer has now been corrected to use the repository-root-most LICENSE and a regression test covers the nested-license case. A fresh manual acquisition run is still required; no audio payload is considered acquired until that run uploads a verified artifact and registry.


## Automated engineering baseline now green

The imported Sound Hunter regression contracts are part of the 19/19 target CTest pass on SHA `10b05a0117366cf33afeb194b3c28456f30fef80`. This validates the importer/policy/splitter contracts, not the existence of a 15 GB BASIC payload. A separate real acquisition artifact (run 44728326148, 2.97 GB) is already preserved as provenance.
