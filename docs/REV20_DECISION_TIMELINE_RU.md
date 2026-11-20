# REV.20 — ХРОНОЛОГИЯ УТВЕРЖДЁННОЙ БАЗЫ И ПЕРЕНОСОВ

**Канонический проект:** `l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-REV.20-OFFICIAL-`  
**Каноническая ветка:** `main`  
**Период сверки:** 2026-11-13 — 2026-11-20  
**Правило:** каждый следующий подтверждённый пункт уточняет предыдущие; самая свежая пользовательская фиксация — действующая база.

## 2026-11-15 — NEON STAGE / SKIN-1

Исходный PR #43 в репозитории `POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-` был merged 2026-11-15.

- Каноническая оболочка: **NEON STAGE DEFAULT**.
- Логический номер: **SKIN-1**.
- Стабильная идентичность: `skin-053` / `Skin_053` / index 53.
- NEON STAGE определяет общий визуальный язык интерфейса, типографику и палитру существующих реальных контролов.
- Скоуп визуальный: не изменять Audio Engine, DSP, MIDI, APVTS, parameter IDs, sampler, preset content, audio callbacks и существующие control bindings.
- PR #43 был интеграционным visual checkpoint. Его описание прямо оставляло Windows build, полный CTest, pluginval, runtime package и FL Studio 20 host acceptance открытыми.

## 2026-11-15 — 2026-11-16 — утверждение полного набора из 16 имён

В ветках REV.18/REV.19 и последующем 16-skin registry work зафиксирована полная логическая последовательность. Это **ровно 16 оболочек всего**, а не 16 дополнительных поверх главной:

| Logical ordinal | Утверждённое имя | Stable ID | Stable index |
|---:|---|---|---:|
| SKIN-1 | NEON STAGE DEFAULT | `skin-053` | 53 |
| SKIN-2 | OBSIDIAN GOLD | `skin-103` | 103 |
| SKIN-3 | CARBON FORGE | `skin-104` | 104 |
| SKIN-4 | MIDNIGHT CRIMSON | `skin-105` | 105 |
| SKIN-5 | ARCTIC PLATINUM | `skin-106` | 106 |
| SKIN-6 | VIOLET NOIR | `skin-107` | 107 |
| SKIN-7 | TITANIUM STORM | `skin-108` | 108 |
| SKIN-8 | EMERALD CIRCUIT | `skin-109` | 109 |
| SKIN-9 | SOLAR FLARE | `skin-110` | 110 |
| SKIN-10 | DEEP OCEAN | `skin-111` | 111 |
| SKIN-11 | ROSE CHROME | `skin-112` | 112 |
| SKIN-12 | DESERT AMBER | `skin-113` | 113 |
| SKIN-13 | GLACIER TEAL | `skin-114` | 114 |
| SKIN-14 | PHANTOM GRAPHITE | `skin-115` | 115 |
| SKIN-15 | ULTRAVIOLET DRIVE | `skin-116` | 116 |
| SKIN-16 | VOLCANIC STEEL | `skin-117` | 117 |

Stable IDs and indices are immutable source identities. They are **not** logical gallery ordinals. The gallery order must always use ordinal 1…16. No other themes or legacy batches may be active or selectable.

## 2026-11-16 — premium artwork / draft PR #58

Source branch: `work/approved-16-skins-completion`  
Source SHA: `10e590c8a3fdfed90cc7ae05e0ff74d8875ac88a`  
PR #58 remains a draft/open source PR; REV.20 imports the approved assets selectively, not the branch wholesale.

The source branch completed the named premium visual pack:

- 15 distinct additional material/art-direction briefs for SKIN-2…SKIN-16.
- 45 SVG foundations: per theme `texture.svg`, `bezel.svg`, `crest.svg`.
- 30 PNG assets: 15 `preview.png` at 360×240 and 15 `hero.png` at 800×450.
- All 15 additional preview images were visually reviewed; ARCTIC PLATINUM vs GLACIER TEAL and VIOLET NOIR vs ULTRAVIOLET DRIVE were specifically differentiated.
- Strict source asset and 16-entry registry audit: 0 errors / 0 warnings, according to the PR and workflow result.

Source evidence on the exact SHA:

- Artwork generation + strict audit [workflow 43835887953](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-/actions/runs/43835887953) — SUCCESS.
- Windows x64 configure/build + full CTest + strict 16-skin asset/registry checks + 16-only VST3/Skins packaging [workflow 43835886032](https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-/actions/runs/43835886032) — SUCCESS.
- Artifact: `PPGU-Windows-x64-VST3-REV19-16-SKINS`.

These results prove the source-branch pack/build gates on that SHA, not an exact-SHA REV.20 build or FL Studio 20 host acceptance.

## 2026-11-16 — Library size decision, newer than the earlier 10–12 GB planning estimate

Draft PR #59 records the newer library-tier baseline:

- BASIC LIBRARY: **15 GB**, included in the standard product.
- EXPANDED ADD-ON: **+15 GB**, optional.
- Initial combined tier: **30 GB total** (15 + 15), not 30 GB added on top of BASIC.
- EXPANDED may grow beyond the initial 30 GB without a product-imposed cap.
- The 500 core presets must be usable from BASIC alone.
- PR #59 explicitly states this is a requirements/contract change, not proof that payloads or 500 playable presets have already been delivered.

## 2026-11-20 — final user-approved REV.20 product baseline

The user reconfirmed and locked the following as the canonical basis:

### Visual shell system

- Exactly **16 graphical shells total**.
- Main/default shell: **NEON STAGE DEFAULT / SKIN-1**.
- Exactly 15 additional shells: **SKIN-2…SKIN-16**, using the fixed names in the table above.
- No 17th theme, no extra packs, no 50-theme batch and no 102-theme gallery.
- All future skin work must preserve the named 16-item sequence and stable-ID mapping.

### Main product modes and preset bank

- Exactly **two main modes**: **MELODY** and **PATTERN**.
- AUTOCHORDS, FX EDIT, Import Guitar, Settings, library tools and other panels are auxiliary windows/functions, not separate top-level modes.
- Core factory bank: **500 presets total** — **250 MELODY + 250 PATTERN**.
- All 500 core presets must operate from the 15 GB BASIC LIBRARY alone.
- The 250 PATTERN presets must be distributed across relevant PATTERN windows, sections and functions. They must not be placed in a single flat list/screen of 250 items.
- The 500 presets define the primary included bank; the catalog can expand beyond 500.
- The existing 300-entry authored catalog (150 + 150) is partial work, not proof of 500 complete/playable presets.

## Current evidence interpretation

- **APPROVED / LOCKED:** user has approved the product decision and identity.
- **ARTWORK PRESENT:** manifests, SVG and PNG files are present.
- **SOURCE-CI VERIFIED:** named source SHA passed the source branch audit/build/tests indicated above.
- **REV.20 VERIFIED:** only after a successful check against the exact current REV.20 commit SHA.
- **HOST-VERIFIED:** only after actual FL Studio 20 validation and evidence.
- **RELEASE-READY:** only after build, full tests, pluginval, package, licensing and host gates pass.

A source-branch pass must never be reported as a REV.20 pass. A design preview must never be described as a running VST3 screenshot.
