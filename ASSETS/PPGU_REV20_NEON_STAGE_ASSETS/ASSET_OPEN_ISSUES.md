# NEON STAGE DEFAULT — ASSET OPEN ISSUES

## Reference image — not visually reviewed
The exact repository reference `01 INTERFACE  NEON STAGE DEFAULT .png` has not been decoded/visually inspected in this session. Therefore exact geometry, proportions, spacing and pixel parity are not certified. The master prompt explicitly forbids inventing the mockup. Closure requires a directly viewable upload of the reference image and comparison with the 1024×700 editor.

## Existing asset inventory vs requested production deliverables
The canonical Skin-053 manifest contains 307 records. These include hero/preview, 2560×1440 background, material texture, four FX overlay layers, 135 master and 135 runtime control-state records, six topbar icon families/atlases, and three SVG shell layers. This is not the complete separate export inventory requested by the master prompt.

Completed in this increment:
- 16 separate scalable SVG panel frames: header, preset browser, playing core, amp/FX rack, performance strip, MIDI keyboard bay, status footer, guitar import, FX edit, pattern routing, AUTOCHORDS, workspace settings, skin gallery, and three dialog frames.

Outstanding deliverables:
- PPGU_SKIN053_BG_MAIN_1024x700.png
- PPGU_SKIN053_BG_GRAPHITE_TEXTURE.png
- PPGU_SKIN053_BG_ANODIZED_METAL.png
- PPGU_SKIN053_BG_BRUSHED_METAL.png
- PPGU_SKIN053_BG_LCD_DARK.png
- PPGU_SKIN053_BG_CONTROL_RECESSED.png
- PPGU_SKIN053_PANEL_HEADER.png
- PPGU_SKIN053_PANEL_PRESET_BROWSER.png
- PPGU_SKIN053_PANEL_PLAYING_CORE.png
- PPGU_SKIN053_PANEL_AMP_FX_RACK.png
- PPGU_SKIN053_PANEL_PERFORMANCE_STRIP.png
- PPGU_SKIN053_PANEL_MIDI_KEYBOARD_BAY.png
- PPGU_SKIN053_PANEL_STATUS_FOOTER.png
- PPGU_SKIN053_PANEL_IMPORT_GUITAR.png
- PPGU_SKIN053_PANEL_FX_EDIT.png
- PPGU_SKIN053_PANEL_PATTERN_ROUTING.png
- PPGU_SKIN053_PANEL_AUTOCHORDS.png
- PPGU_SKIN053_PANEL_WORKSPACE_SETTINGS.png
- PPGU_SKIN053_PANEL_SKIN_GALLERY.png
- PPGU_SKIN053_PANEL_DIALOG_BASE.png
- PPGU_SKIN053_PANEL_DIALOG_WARNING.png
- PPGU_SKIN053_PANEL_DIALOG_ERROR.png
- separate main rotary component layers for all 9 controls (BASE/RIM/FACE/POINTER/SCALE/GLOW)
- FX EDIT rotary component layers and parameter-specific scale overlays
- standalone per-state export for all required buttons and seven FX switches
- standalone LED state assets (OFF/ON/GLOW/WARNING/ERROR/SUCCESS/DISABLED)
- separate display frame assets (LCD empty/active/warning/error, numeric, harmony, notes-held, scale/key)
- individual white/black keyboard key states, separator, active-note overlay, and 49-key preview
- individual SVG icon family (41 icons × 16/24/32/48 sizes)
- hardware details as separate PNG/SVG assets
- button, FX toggle, LED, keyboard, meter and icon sprite atlases with extracted frames
- main interface previews 1024x700 and 1600x1100 and five contact sheets
- ZIP archive of the complete export package

## Sprite sheet manifest conflict
`SKIN/Skin_053/assets/spritesheets/neon_stage_spritesheet_manifest.json` identifies its project as `NEON_STAGE_MANAGER_3_0` and specifies base colors `#05070E`, `#00D2FF`, `#00E5FF`, `#6B8CFF`, `#FFB454`. PPGU REV.20 master prompt and `theme.json` define a different authoritative palette and PPGU product identity. Treat this manifest as unapproved for PPGU until reconciled; do not silently overwrite either source.

## Palette conflict
The master prompt specifies `danger #FF557A` and `warning #FFBE55`; `theme.json` currently specifies `danger #FF665E` and `warning #FFB454`. The theme manifest is currently consumed by runtime; product owner must decide whether to update the theme tokens or amend the prompt. Until resolved, preserve runtime tokens and do not create new semantic-color assets from the conflicting values.

## Export state
No binary assets were copied into this export directory in this step. Existing source assets remain under `SKIN/Skin_053/`. No ZIP, contact sheets, or 1024×700/1600×1100 final previews are claimed. Do not mark the pack COMPLETE.
