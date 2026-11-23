# ASSET OPEN ISSUES — REV.20

This file records only items that cannot be honestly marked complete from the current repository evidence.

## ASSET-001 — Pixel-level comparison to approved main reference

- **Reference:** `01 INTERFACE  NEON STAGE DEFAULT .png` (repository filename includes the exact spacing).
- **Current limitation:** the GitHub integration available in this session can read UTF-8 source files but cannot decode the referenced binary PNG. The image has therefore not been visually inspected in this session.
- **What is already established:** the NEON STAGE visual specification, palette, material language, component IDs and composition constraints are recorded in the approved master prompt, `SKIN/Skin_053/theme.json`, `Info.txt` and REV.20 approval documents.
- **Required closure:** compare a directly viewable copy of the main reference against a 1024×700 runtime screenshot and record geometry, proportions, spacing, typography, material and control-state differences. Do not claim pixel-perfect parity before this review.

## ASSET-002 — Auxiliary-window references 02–07

- **References:** repository images 02–07 for AutoChords, FX EDIT and multi-window layouts.
- **Required closure:** inspect each reference and compare against the actual auxiliary windows. Keep the main editor, FX EDIT, PATTERN routing and AutoChords as separate UI surfaces where specified. Do not invent controls or claim unavailable backend functionality.

## ASSET-003 — Export handoff versus runtime paths

- **Status:** the production assets already exist in the canonical `SKIN/Skin_053/assets/` and `SKIN/Skin_053/svg/` trees; the manifests define the runtime/master assets.
- **Required closure:** if a flattened external handoff is needed, generate it from the manifests and verify every copied file by SHA-256. Do not manually duplicate or rename files and then treat those copies as runtime-integrated.

## ASSET-004 — Host acceptance

- **Status:** repository journal records exact-SHA Windows x64 VST3 build, CTest, 16-theme resource validation and package staging as passed on documented revisions. FL Studio 20 host acceptance and pluginval are separate release gates and must not be inferred from artwork presence.
