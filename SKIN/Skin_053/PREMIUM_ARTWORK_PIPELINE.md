# SKIN-1 / NEON STAGE PREMIUM — Production Artwork Pipeline

**Approval:** BASE APPROVED  
**Theme ID:** `skin-053` (stable)  
**Scope:** Skin-1 only. Other themes remain untouched.  
**Visual source of truth:** seven official repository-root PNG references, 01–07, as one unified interface system.

## Non-negotiable production rules
- Reproduce the seven approved references faithfully. No alternative skin, redesign, simplified substitute or placeholder.
- PNG is mandatory for production interface artwork. Preserve alpha where compositing is required.
- Deliver authored high-resolution masters and lossless 2×/4× variants. An upscaled low-resolution placeholder is not a master.
- Five control states: `default`, `hover`, `pressed`, `disabled`, `active`, where applicable. Record `not_applicable` explicitly for controls that do not support a state.
- Materials and lighting must be consistent across the seven reference screens.
- Dynamic text, parameter values, meters and status remain native JUCE controls.
- Palette: graphite, cyan and electric blue only. No violet, purple or magenta.
- JPEG is allowed only for genuine photographic content. WEBP is optional. SVG is excluded from the final premium production/runtime pipeline.
- Do not change APVTS IDs/ranges, DSP, sampler/audio callback, MIDI behaviour, plugin geometry or stable theme identity as part of visual work.

## Existing runtime artwork inventory
The existing Skin-1 runtime composite currently uses:
1. `assets/background/main.png` — 2560×1440.
2. `assets/textures/material.png` — 1024×1024.
3. `assets/fx_layers/shadow.png` — 800×450.
4. `assets/fx_layers/stage_glow.png` — 800×450.
5. `assets/fx_layers/specular.png` — 800×450.
6. `svg/texture.svg`, `svg/bezel.svg`, `svg/crest.svg` — legacy layers, pending PNG replacement.
7. `assets/fx_layers/edge_highlight.png` — 800×450.

Existing PNG control artwork and four sprite atlases are retained as legacy/runtime assets pending visual comparison against the seven approved references. Their presence does not establish that they match the approved design.

## Known legacy items — not accepted as final
- `assets/hero.png` (800×450) and `assets/preview.png` (360×240) are legacy artwork; not approved as final premium hero/preview.
- Existing master hero/preview files were upscaled from legacy runtime images; they are not valid authored high-resolution masters.
- Existing control states include `dragged` rather than the approved `active` terminology. Do not blindly rename: verify each component's runtime semantics and provide the required active state.
- Three material SVG layers are still referenced by `theme.json` and loaded by the current ThemeManager. They must remain until verified PNG replacements are integrated and all references/build paths are migrated.
- SVG icon master sources may exist alongside PNG runtime icons. Audit all SVG files and code paths before declaring the entire theme SVG-free.

## Required asset structure
```
NEON_STAGE_PREMIUM/
  references/                 immutable reference copies + checksums
  master/screens/              high-resolution screen compositions
  master/panels/               header, left, centre, right, lower strip, footer
  master/controls/<control>/   five state masters where applicable
  master/materials/            graphite, metal, glass, display surfaces
  master/lighting/              glow, shadow, specular, edge passes
  runtime/2x/                   lossless PNG runtime assets
  runtime/4x/                   lossless PNG runtime assets
  atlases/                      PNG atlases and exact coordinate maps
  manifests/                    inventory, state matrix, provenance, hashes
```

## Reference-to-asset workflow
1. Inspect all seven source images at native resolution. Preserve the originals.
2. Record SHA-256, dimensions, alpha presence and source provenance.
3. Map the exact screen composition and component geometry from references 01–07.
4. Author independent transparent PNG masters; do not extract arbitrary fragments from flattened mockups and call them production-ready without cleanup.
5. Generate 2×/4× variants from masters. Verify edge quality and alpha fringes.
6. Build atlases and coordinate maps; validate every rectangle is in bounds and every required state is accounted for.
7. Replace the three SVG material layers with inspected PNG equivalents. Update theme metadata, manifest, packager and loader together.
8. Search the full Skin-1 runtime/package for SVG references. Remove SVG loading and SVG assets only when no required references remain.
9. Validate image decode, dimensions, checksums, alpha, package contents and runtime drawing.
10. Run Windows x64 VST3 build, CTest, plugin validation and FL Studio 20 host acceptance.

## Current execution status
- Approved specification, asset schema, reference inventory, control-state matrix and atlas schema: committed.
- Theme identity: changed to NEON STAGE PREMIUM while preserving `skin-053`.
- Seven binary reference files: known to exist in repository root; their pixel content has not yet been inspected by the repository text connector.
- New premium master PNG artwork and PNG replacements for the three SVG material layers: not yet authored.
- SVG loader removal and SVG deletion: intentionally not performed because verified PNG replacements do not yet exist.
- Build/test status for this branch: not claimed by this artwork-specification commit.

**Completion rule:** NEON STAGE PREMIUM is not complete until the actual reference-matched PNG artwork is authored, integrated, visually reviewed, runtime-validated and the Windows x64 VST3/CTest/FL Studio 20 acceptance gates pass.
