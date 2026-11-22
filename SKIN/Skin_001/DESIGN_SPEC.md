# SIGNALS — SKIN-001

**Status:** design foundation only; not yet selectable or runtime-ready.

## Source reference

The reference image is already present in this repository as `01 INTERFACE  NEON STAGE DEFAULT .png` (PNG, 2,359,486 bytes, Git blob `747207e183c77e8b913a543b2dc40b29829e77da`). The same source was located in the ChatGPT Library and visually inspected. It is the user's supplied design reference, not a finished SIGNALS asset.

## Approved visual direction

- Dark chassis with brushed-metal grain and machined bevels.
- Restrained cyan and electric-blue neon lighting.
- Top navigation; preset browser anchored on the left.
- Wide central electric-guitar / graffiti hero banner.
- Nine illuminated metal rotary controls.
- Dedicated AMP & TONE module on the right.
- Seven-item FX Chain.
- Full-width MIDI keyboard.
- Bottom status strip: MIDI, CPU, tempo and Sync.

## Identity and compatibility

- Display name: **SIGNALS**.
- Logical slot: **SKIN-001**.
- Stable ID: `skin-001`; folder: `Skin_001`.
- This is a new 17th theme. Preserve all existing 16 entries and all stable IDs, especially `skin-053` / NEON STAGE DEFAULT.
- Reuse the canonical 27 control IDs plus `sync_selector` metadata and the existing runtime binding schema. No APVTS, DSP, sampler, MIDI, preset, parameter-ID or audio callback changes.

## Remaining implementation gates

1. Produce original SIGNALS artwork: preview, hero, SVG texture/bezel/crest and optimized transparent control/icon atlases with a machine-readable atlas manifest.
2. Add a unique 17th registry entry without changing the default stable ID.
3. Extend ThemeManager discovery, gallery selection, persistence/hot-swap and package staging to 17 themes.
4. Replace 16-only assumptions in validators, tests, documentation and CI; add regression assertions that the previous 16 identities and assets remain unchanged.
5. Run the exact-revision Windows x64 VST3 build and CTest; verify PNG/SVG assets and package contents. Only then mark SIGNALS runtime-ready.

**Important:** the directory and theme manifest are a foundation, not proof of runtime integration. Do not advertise this skin as selectable until all gates above pass.
