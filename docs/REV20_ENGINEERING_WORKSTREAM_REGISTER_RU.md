# REV.20 — РЕЕСТР ИНЖЕНЕРНЫХ НАПРАВЛЕНИЙ M1–M13 И ОТКРЫТЫХ PR

**Каноническая цель:** REV.20 main  
**Сверка исходника:** POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-, PR #2–15 и журнал M1–M5.  
**Принцип:** source-branch CI pass, наличие кода и рабочая функция в REV.20 — разные статусы. Ни один Draft PR не считается автоматически принятой реализацией.

## 1. Статусы

- **SOURCE PRESENT** — исходник/тест/описание присутствует в исходной ветке.
- **SOURCE CI PASS** — на конкретном source SHA прошла названная автоматизация; это не PASS текущего target.
- **PORTED TO REV.20** — конкретные файлы изолированно перенесены в target.
- **REV.20 CI PASS** — тесты выполнены на точно указанном SHA целевого main.
- **HOST VERIFIED** — вручную подтверждено в FL Studio 20 на Windows 10 x64.
- **RELEASE ACCEPTED** — все engineering, pluginval, legal, package и host gates закрыты.

## 2. Общая основа M1–M3

Исходная интеграционная линия: fix/m1-m2-m3-release-gates (source branch; не target branch и не нынешняя REV.20 main).

Согласно source docs/WORK_LOG_M1_M5_INTEGRATION_RU.md:
- M1: APVTS state XML, async SFZ bank load, generation token, SafePointer, worker lifecycle и state restore присутствуют в исходниках. Ранее проходили Windows build/CTest/pluginval/package runs, включая 42871881934 на SHA 2e9356b729e3daba6a5c62c31fed7257072c6f12.
- M1 host gaps: FL Studio save/reopen, missing library recovery, automation, editor close during load, repeated bank changes, device change, long playback и clean Windows 10 execution.
- M2: streaming sample pool, bounded page cache, worker-backed page decode, pinned leases, SFZ RR parsing/selection присутствуют и имели CI regression coverage.
- M2 open: реальный DSP velocity-layer crossfade, palm-mute zones/velocity threshold on licensed guitar banks, rendered midpoint gain, xfin/xfout semantics, click/pop + repeated-hit/cache/voice stress, доказательство zero allocation/lock/I/O on audio callback и host playback.
- M3: transport-aware pattern scheduler и sample-offset NoteOn/NoteOff присутствуют; unit tests покрывают host/internal clock, PPQ/sample conversion, long NoteOff, wrap и discontinuities.
- M3 open: полная scheduler→sampler end-to-end цепочка, ownership/NoteOff/chord transitions, stop/seek/loop/tempo changes/slot switch/simultaneous input и FL Studio 20.

Исторический source workflow success не переносится как доказательство на текущую REV.20 сборку. REV.20 на точном SHA 8cfd11ecce3c8039360c1c194be5251e716c9015 уже имеет собственный green Windows VST3 + full CTest + 16-theme runtime/asset/package workflow (run 44717722638). Это подтверждает именно актуальный импортированный target-снимок, но не заменяет host acceptance.

## 3. Изолированные модули и PR

### PR #2 — PageCache publish rollback
- Source branch: fix/page-cache-publish-rollback; source head a2ec7a3b9c5496c8bf6b2f01be1f1e79b19d43e2; открыт, не Draft.
- Root cause: publish() отвергал неправильную геометрию страницы, но оставлял reservation в состоянии loading, теряя слот cache.
- PORTED TO REV.20: Source/Sampler/PageCacheSlots.cpp теперь сначала подтверждает текущий exact PageKey; при некорректных channels/frames делает CAS loading→empty только для этой же reservation. Старая/устаревшая задача с другим key не может отменить чужую загрузку.
- Добавлены regression cases invalid geometry rollback и stale worker key protection в tests/PageCacheSlotsTests.cpp.
- REV.20 exact-SHA CTest: требуется после включения этого patch в следующий commit; до результата не ставить PASS.

### PR #3 — M5 Style Engine
- Source branch/head: work/m5-style-engine-tests / c18353df0a68e68ff9790e9c68bc009527aaf811; Draft, base main.
- Foundation: deterministic, bounded, allocation-free velocity/accent transforms; downbeat/backbeat/offbeat; chug/palm mute candidates; hammer-on/pull-off probabilities; strum spread; FX taste; NaN/Inf sanitization.
- Catalog targets include Mest — PHOTOGRAPHS Lead/Rhythm.
- Earlier source workflow 42840410645 succeeded on source commit 0cc36c7455edb3adcc5bde1f5bd690c831acf3cb.
- Runtime binding to PatternScheduler/Processor, preset StyleDNA/parameter binding, articulation sample routing, UI controls and refreshed exact-head CI remain open. NOT PORTED / NOT COMPLETE in REV.20.

### PR #4 — M4 AutoChords / FingeringGenerator
- Source branch/head: work/m4-autochords-fingering / 9308bf83c5dcc9859451c9dbe4f48df454259e35; Draft, base M1–M3 integration.
- Foundation: chord qualities (major/minor/diminished/augmented/sus2/sus4/dom7/maj7/min7/power), inversions, bounded voicings and E-A-D-G-B-E string/fret fingering; scale-aware mapping in newer work.
- Source work log records a Windows success on an earlier commit/run 42844161921; current PR head remains a Draft, so do not promote that old pass to current-head acceptance.
- Live Pattern MIDI scheduler/UI/state integration and FL Studio 20 remain open. NOT PORTED / NOT COMPLETE in REV.20.
- Architecture constraint: AutoChords is an auxiliary window/function inside PATTERN, not a third top-level mode.

### PR #5 — M2 SFZ velocity crossfade
- Source branch/head: work/m2-velocity-crossfade / 6a97e24188fe0dd25e2a27e5bcb3fa5a0de33252; Draft, base M1–M3.
- Up to eight overlapping SFZ velocity regions, per-layer fade, gain/power velocity curves, fixed-capacity selection and round-robin.
- Earlier source run 42843931173 passed on earlier commit ef1ee5b04c3dc6653f749d7602b92a683253d059.
- Open: rendered audio midpoint response, real-bank xfin/xfout semantics, palm-mute articulation zones, repeated-hit/click/cache/voice stress, no audio-thread allocation/lock/I/O and FL Studio playback. NOT PORTED as this PR's implementation into REV.20.

### PR #8 — advanced M2 crossfade / palm-mute / voice safety integration
- Source branch/head: feature/m2-velocity-crossfade-gain / 52f92ae03f81a912c5656a2b46d3e5493bdb5098; Draft, base M1–M3.
- Ports velocity layer rendering, velocity-triggered palm mute/damped voice, RR selection, bounded click-reduced voice-steal tails and fail-closed pattern clock.
- Earlier source CI pass on prior SHA 324d33a95da4dda5d6eecd32f89f4866b41416f0, run 42828453471.
- Unified target SHA, real-bank audio response, full stress and FL20 are pending. NOT PORTED / NOT COMPLETE in REV.20.

### PR #9 — rendered velocity-crossfade midpoint test
- Branch/head: test/m2-crossfade-rendered-signal / 17c7f20b5cb2eccd36b0eee4104e3fc2fbc8bcf7; Draft.
- Adds SamplerEngine rendered-signal assertion for equal-power crossfade midpoint. Source exact-head Windows/CTest/pluginval is not recorded as pass. NOT PORTED.

### PR #10 — page-cache lease pinning
- Branch/head: test/m2-page-cache-lease-pinning / 1bc97f14ae93b67c22a8262ca1087de062b05a7f; Draft.
- Tests multiple concurrent readers pinning same page, foreign-cache lease rejection, no eviction under a live lease, and safe slot reuse after release. Does not replace long-running concurrent stress. NOT PORTED.

### PR #11 — Hermite page-acquire fastpath
- Branch/head: perf/m2-hermite-page-acquire-fastpath / 618dc3055558080d3d01a22e0680fc14067c4b1d; Draft.
- Reduces contiguous four-tap Hermite reads to acquire first page and second only when crossing page boundary; fixed storage/lease semantics maintained.
- CPU gain is structural expectation only; numeric benchmark is not recorded. NOT PORTED.

### PR #12 — CI / packaging acceleration
- Branch/head: ci/speed-up-validation-and-packaging / 584a6ddb488a58a7ddeca8a1dd604f633c429ec1; Draft.
- Parallelizes independent CTest targets (4 workers) and uses fast ZIP compression without removing tests.
- Needs fixture isolation review in REV.20 before adoption. NOT PORTED.

### PR #13 — power profiles / DOUBLE
- Branch/head: feat/power-profiles-double-multicore / e2f9c61765f36dc6a921c163bd50f05e8d44e4f4; Draft.
- Implements GOOD/NORMAL/NIGHT profile proposal with 64/32/12 voice caps and a preallocated short-delay stereo thickener for DOUBLE parameter.
- It does not prove true two-recording Double Track, worker-count multicore DSP or measured battery/CPU savings.
- Exact-head build/CTest/pluginval and FL20 acceptance are not confirmed. NOT PORTED.

### PR #14 — functional audit engine/UI/presets/import
- Branch/head: audit/engine-ui-presets-import-sounds / 630545d935f652bd758206387d45b9c360789276; Draft, documentation/audit only.
- Findings: factory catalog applies only a limited parameter subset; user preset save/load/browser actions absent; Import Sounds currently single-SFZ async path; approved Cover UI only partially represented.
- It does not implement the audited gaps. These remain REV.20 work items until code and tests prove completion.

### PR #15 — key-aware AutoChords scale mapper
- Branch/head: feat/pattern-auto-chords-scale-mode / 9fe1c522f90164bce928ba50d69e76c13ca6dfc6; Draft.
- Scale snapping to selected root + Major/Minor scale; note-off mapping tracked across held notes/key changes. This is scale mapping, not single-note chord-voicing generation.
- The proposed branch applies the feature to both MELODY and PATTERN. That conflicts with the current approved product architecture (AutoChords auxiliary window/function inside PATTERN only). Explicitly excluded from blind import; redesign for PATTERN-only before considering.

## 4. Performance and QA gaps that must not be hidden

- True multicore task processing / worker count and measured power profiles remain not proven.
- Double Track as two independently recorded takes is not proven by a stereo delay thickener.
- Factory 500 parameter completeness/playability, user preset browser/save/load/import/export, full Cover UI, FX parameter QA and Import Guitar multi-bank ingest all need feature-level verification.
- Velocity crossfade/palm mute have promising WIP implementations, but not target-integrated and fully stress/host-verified.
- AutoChords algorithmic foundations are not equivalent to live Pattern MIDI voicing/preview/state UI.
- M1 lifecycle/async state, M2 streaming/cache, M3 transport/scheduler each require host-specific acceptance even where source CI passed.

## 5. Target integration policy and next order

1. Keep this matrix as canonical gap/source evidence, not as code-import authorization.
2. Port safe correctness fixes such as PR #2 into REV.20 with target regression tests.
3. Run target exact-SHA Windows build/CTest after each integration chunk; never inherit a source branch pass as target pass.
4. Then selectively port M2 crossfade/palm-mute after reviewing the actual current REV.20 sampler API and APVTS IDs; preserve callback allocation/lock/I/O prohibition.
5. Complete M3 end-to-end transport/scheduler acceptance.
6. Integrate M4 AutoChords only as PATTERN auxiliary window and test state/persistence.
7. Integrate M5 StyleEngine with explicit preset-to-style bindings and deterministic regression coverage.
8. M6–M13 features remain sequenced after core M1–M5 gates; do not advertise runtime features from a documentation/validator PR.
9. pluginval strictness 5, FL Studio 20 Windows 10 host acceptance, performance/DPI and package gates remain separate from CTest.

## 6. Do-not-import conflicts and obsolete material

- PR #15 MELODY scale-snap behavior conflicts with AutoChords-in-PATTERN-only rule.
- Old 10/20/50/102 theme galleries, skin-001 remaps and NEON FORGE rename conflict with the 16-theme immutable identity contract.
- PR #54 whole merge conflicts with NEON STAGE DEFAULT and legacy theme count; only safely separable UI behaviour may be reviewed separately.


## 7. Additional source-main DSP work ported selectively

### Live AMP TONE / EQ frequency / compressor amount wiring

Source main commits 7ec945b73f0cb94de1e2d77ea10595ec88f93a12 and 8e51fa5d2acd0dbd7f2cdb115c85da337df49e43 added live DSP use of the existing parameters:

- eqLowFreq / eqHighFreq now control the low/high one-pole crossover frequencies instead of fixed 250 Hz / 2500 Hz cutoffs.
- The AMP TONE parameter controls an independent high-band tilt and remains active when the 3-band EQ is bypassed.
- EQ bypass uses unity band gains rather than bypassing the independent AMP TONE stage.
- Compressor Amount is snapshotted once per audio block, outside the sample loop, and controls dry/processed gain blend rather than always applying 100% compression.
- Source test tests/test_fx_dsp_parameter_wiring.py guards declarations, DSP consumption and the no-per-sample APVTS atomic read.

These existing APVTS IDs are already present in REV.20. The DSP block and its wiring test were selectively ported into REV.20 and registered as a CTest target. This code requires a new exact-SHA Windows build/CTest result; until then status is PORTED, TARGET TEST PENDING. No new APVTS IDs are introduced.

### NEON STAGE approved mockup source of truth

Source commit 8f097e00b426b1dee8d74c9be4394575ea655cd0 records the approved NEON STAGE main screenshot (01) as the binding visual source. References 02–07 specify AutoChords, FX EDIT and floating/multi-window states. The SVG banner is branding only and must never replace the actual interface reference. REV.20 README header uses the PNG reference, and the six supporting image references exist in the target repo.


### REV.20 target verification update — 2026-11-20

- PR #2 PageCache rollback fix is now **REV.20 CI PASS** on exact SHA `974c5877d1a0375100539d2513329a38feb84871`, workflow 44719521911; full CTest 15/15 passed including the new exact-key rollback tests.
- The next staged task is the live AMP TONE / EQ crossover / compressor Amount DSP slice. It has been ported in code and guarded by a Python test registered in CTest, but awaits the next target exact-SHA build/CTest.


### Live DSP parameter wiring — ported into REV.20

The source-main DSP block implementing live EQ crossover frequencies, independent AMP TONE high-band tilt and Compressor Amount dry/processed blend is now present in REV.20. A Python CTest guard is registered as `ppgu_fx_dsp_parameter_wiring`. Existing APVTS IDs are unchanged. Target verification remains pending; expected CTest total is 16 after this new target.
