# NEON STAGE — Meshy AI asset owner attestation

**Recorded:** 2026-11-21  
**Project:** POP PUNK GUITAR ULTIMATE REV.20 / NEON STAGE  
**Branch:** `feat/rev20-neon-stage-graphite-magenta-integration`  
**Scope:** Meshy AI-generated visual source files already present in this repository.

## Owner statement

The project owner explicitly confirmed in the project conversation on 2026-11-21: **the owner created the listed Meshy AI images and asserts having the rights needed to use, modify, create derivative vector artwork from, and commercially distribute the resulting artwork as part of the NEON STAGE product, including the VST3 plugin.** This is recorded as an owner-provided rights attestation, not as an independent legal opinion or a verification of Meshy account records.

The attestation authorizes the project team to proceed with visual review, SVG/vector reconstruction and derivatives based on these source images. It does not authorize copying unrelated third-party material contained in prompts/references, nor does it supersede applicable Meshy terms or third-party rights. Preserve generation receipts, plan-at-generation evidence and input/reference provenance with the release records where available.

## Source inventory

The following unique Meshy image files are present in the REV.20 repository. Git blob SHAs identify the exact source versions covered by this record:

| Source image | Git blob SHA |
|---|---|
| `Assets/3D/References/Meshy_AI_4020f9f8e4a2cd28e8723fdbeff39c9690391b32fc5d18e338279bafe12b147b.png` | `dd8c0e1c73d1f9dc661e94b72fc72a110ca09ac2` |
| `Assets/3D/References/Meshy_AI_6cefecb7af424cd587c2e509734561226ebfeafdf5e54f4fa310c94014f41acb.png` | `7e99d10870930d6d2a2cc20fd5069505569d27b4` |
| `Assets/3D/References/Meshy_AI_9795f5366a84b9bd03fa351947c013cec5e8d9472d90fd20205247e8af0ebaa9.png` | `8c1c30da4793224706d7243a37f3fab068d8d549` |
| `Assets/3D/References/Meshy_AI_d3c0df0c42b7717e88b1c4a68c0866b67e7b6cbc06b78eb1a5cb26ea910725f3.png` | `4618dc013e6c279972423a4d2b1cc3e47c63a709` |
| `Assets/3D/References/Meshy_AI_neon_stage_buttons_and_switches.png` | `4b7c6b2611aedb7e00f3a7d746805be0af3a3be5` |
| `Assets/3D/References/Meshy_AI_neon_stage_buttons_sheet.png` | `73d75392dd48dc1cc8db3f7096e43140143fc296` |
| `Assets/3D/References/Meshy_AI_neon_stage_frames_and_panels.png` | `d7499e74cab2cefa68e6e52fbb7007e0f8230b62` |
| `Assets/3D/References/Meshy_AI_neon_stage_knobs_and_meters.png` | `fd639e613f23d96ede299fbe02011e95b54f00c7` |
| `Assets/3D/References/Meshy_AI_neon_stage_knobs_sheet.png` | `ba9aafa398a2d65bcb8ee6ad2a223309e11bd138` |
| `Assets/3D/References/Meshy_AI_neon_stage_meters_sheet.png` | `4363e8e2fb901db0a882cf8c7e9beb2e78600e82` |
| `Assets/3D/References/Meshy_AI_neon_stage_ui_icons_set.png` | `3494a4f2c7be8b5225175d726e933e0f86dde334` |

Four hash-named PNGs also exist at repository root as duplicate blobs of the first four entries above; they are not separate source artworks.

## Integration decision

- **Approved:** use these exact source images as visual source material for NEON STAGE review, tracing/reconstruction and derived SVG artwork.
- **Approved by owner attestation:** commercial distribution of the resulting owner-created/owner-controlled artwork in the VST3 product, subject to applicable platform/service terms and third-party input rights.
- **Not approved as a shortcut:** blindly embedding large reference sheets as runtime controls. Create clean, optimized, transparent SVG components and rasterize only where JUCE/runtime compatibility or measured performance requires it.
- Keep the immutable master banner `assets/POP_PUNK_GUITAR_ULTIMATE_BANNER.svg` unchanged. Preserve its 5:2 composition and the sole DEFAULT palette in `SKIN/Skin_053/theme.json`.
- Before SVG assets are marked production-ready, perform a visual audit against the approved master, validate SVG/XML, inspect alpha/edges, verify component dimensions and ensure all interactive elements remain native JUCE controls with their existing APVTS attachments.

## Evidence status

This file records the owner's explicit statement. It does not contain Meshy invoices, account-plan receipts, generation timestamps or input-image provenance records. Attach those records to the project's release evidence when available; do not represent them as inspected unless they have actually been supplied and reviewed.
