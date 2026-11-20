# REV.20 — consolidation manifest

## Source selection

- Primary engineering source: `POP-PUNK-GUITAR-ULTIMATE-VST-REV.19-Build.03`, HEAD `7b540ff9cddbc2b0327c83611b49e222bce51d2b`.
- REV.18-only decision commits reconciled into the baseline: `738edc6151a6e75d25ef361fc60c9178fbde4360`, `c20cc6b76d4c66b70bcfcec27d8e79514ada147b`, `bf6465c6d1613a2b04728f9f91ee32c4b6f12983` and `6ac4276c26d84ffb7e60d95cea3909401db00cea`.
- Destination main before migration: `2aeffd1c594232a933e9e5577ffad4efb6877263`.
- REV.20 migration commit: `2bd623a666090d4ef017296f52fdb568808a227b`.

## Preserved in REV.20

- Production VST3 source under `Source/`, CMake project, focused regression tests, SFZ/sample validators, factory catalog and portable preset examples.
- Only the approved 16 skin shells: `Skin_053` and `Skin_103` through `Skin_117`.
- NEON STAGE component assets/manifests and the seven approved interface reference captures.
- Approved MIDI/Melody, sample streaming, bank/preset, auxiliary panel, reference asset and licensing specifications.
- Meta Open Sound license-clearance record and sound asset registry seed.
- All pre-existing REV.20 L3XTOWN inventories, hash manifests, acoustic/electric reports, LibraryManager source and tests remain intact.

## Intentionally excluded from active product

- Legacy/experimental skin directories outside the 16 approved shells, including the old 102-theme registry and generated 50-theme batches.
- Duplicate/repeated prompts, continuation dumps, parallel journals, temporary screenshots and stale copies of specifications.
- Old root-level prototype duplicates where a maintained `Source/` implementation exists.
- The historical `Info.txt` copied as-is: it contained competing REV.17/18/19 branch instructions. A clean REV.20 `Info.txt` is the only active journal.
- Sample audio files not actually present/cleared for redistribution. Existing L3XTOWN originals remain on source storage; metadata manifests are not treated as audio copies.

## Known evidence limitations

- The latest inspected REV.19 workflow run (#2241, SHA `2df2a566b489198bd3ec646bdf6c78deef8c8f06`) failed. That run is not evidence for the selected source HEAD or REV.20.
- A historical REV.18 interim CI package passed at SHA `877a0c8d96dc6ef3bdd620f8af0a75a79fa067ec`; FL Studio 20 manual host acceptance was explicitly not run.
- The REV.20 migration workflow passed, but that workflow copied files and pushed a commit; it did not compile the plugin or execute the VST3 regression suite.
- Therefore imported code is PRESENT; a successful REV.20 build, full CTest, pluginval, package audit and FL Studio 20 host acceptance remain unverified.

## Migration policy

This is a selective consolidation, not a merge of old branches. Old repositories and branches remain available as historical provenance, but all new implementation, changes, validation evidence and releases belong only to this repository's `main` branch.
