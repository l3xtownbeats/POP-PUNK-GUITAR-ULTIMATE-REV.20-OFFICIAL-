# NEON STAGE PREMIUM — Production Asset Base

**Approval:** BASE APPROVED  
**Visual authority:** the seven official repository-root PNG references, `01–07 INTERFACE NEON STAGE`.  
**Scope:** one unified premium visual system for Skin-1 / `skin-053`; not seven skins.

## Immutable design requirements
- Reproduce the approved reference system; do not reinterpret it or replace it with simplified mockups.
- PNG is the required production format for all interface artwork: screens, panels, buttons, knobs, switches, indicators, displays, frames, textures, atlases and lighting.
- Preserve alpha transparency for composited assets.
- Keep high-resolution authored masters and generate lossless 2× and 4× variants from the authored source. Upscaling is not a substitute for high-resolution master artwork.
- JPEG is permitted only for actual photographic material. WEBP is optional and is not part of the required pipeline.
- SVG is excluded from the NEON STAGE PREMIUM production/runtime pipeline.
- Palette is graphite, cyan and electric blue. No violet, purple or magenta.
- Keep materials, typography, lighting, edge treatment and proportions consistent across all seven references.
- Dynamic labels, values, meters and status text remain native JUCE UI elements, never baked into static images.
- Preserve APVTS IDs, DSP/audio behaviour, MIDI behaviour, plugin geometry and the stable theme identity unless separately authorized.

## Reference mapping
| Reference | Approved role | Status |
|---|---|---|
| 01 | Main/default interface visual authority | Binary reference exists; pixel inspection pending |
| 02 | AUTOCHORDS interface/state reference | Binary reference exists; pixel inspection pending |
| 03 | Supporting screen/state in the same system | Role to be mapped from image |
| 04 | Supporting screen/state in the same system | Role to be mapped from image |
| 05 | Supporting screen/state in the same system | Role to be mapped from image |
| 06 | Supporting screen/state in the same system | Role to be mapped from image |
| 07 | Supporting screen/state in the same system | Role to be mapped from image |

The source PNGs are references, not production assets to overwrite. Their binary payloads must be preserved and checksummed when accessible.

## Directory contract
- `references/` — immutable source references and checksums.
- `master/screens/` — high-resolution screen compositions.
- `master/panels/` — header, preset browser, central playing area, AMP & TONE/FX, lower performance strip and footer.
- `master/controls/` — knobs, buttons, switches, LEDs, displays and control-state artwork.
- `master/materials/` — graphite, anodized metal, glass and screen surfaces.
- `master/lighting/` — glow, shadow, specular and edge-highlight passes.
- `runtime/2x/`, `runtime/4x/` — lossless PNG runtime variants.
- `atlases/` — PNG atlases plus machine-readable coordinate maps.
- `manifests/` — asset inventory, state matrix, reference mapping and checksums.

## Control-state contract
Where meaningful, each image control has five explicit states: `default`, `hover`, `pressed`, `disabled`, `active`. A state that does not apply to a component must be explicitly recorded as `not_applicable`; it must not be silently omitted or represented by an accidental blank image.

## Production gates
1. Inspect all seven reference images and map their screen regions.
2. Record source dimensions, alpha-channel presence, SHA-256 and provenance.
3. Author individual production assets from the approved visual references.
4. Review masters at 100% and 200%; check edges, transparency and artifacts.
5. Validate atlas coordinates, bounds, overlap and state completeness.
6. Confirm there are no SVG references or SVG decoders in the premium pipeline.
7. Validate PNG decoding, scaling, packaging and runtime rendering.
8. Run Windows x64 VST3 build, CTest and FL Studio 20 host acceptance.

## Current truth
This commit establishes the approved production specification, folder contract, asset schema and control-state inventory. It does **not** claim that the seven binary references have been visually inspected or that final premium artwork has already been authored. Existing placeholder/legacy artwork is not promoted to final status by this specification.
