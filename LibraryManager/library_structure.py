#!/usr/bin/env python3
"""Create the approved on-disk/logical library contract consumed by PPGU.

The builder never copies audio. It produces deterministic engine/mode indexes,
pitch/velocity/articulation coverage, explicit gaps and runtime readiness gates.
All musical facts must already be present as reviewed metadata in the catalog.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "ppgu.library_structure/1.0.0"
MODES = (
    "SAMPLE MODE", "STRUMMING", "ARPEGGIO", "PATTERN MODE", "RIFF MODE",
    "MELODY MODE", "PHRASE MODE", "ONE PITCH", "ARTICULATIONS", "ENDING",
)
MODE_ENGINES = {
    "SAMPLE MODE": ("SAMPLE_INSTRUMENT",),
    "STRUMMING": ("PATTERN_INSTRUMENT",),
    "ARPEGGIO": ("PATTERN_INSTRUMENT",),
    "PATTERN MODE": ("PATTERN_INSTRUMENT", "NOTE_PLAYABLE_PATTERN_ZONES"),
    "RIFF MODE": ("PATTERN_INSTRUMENT",),
    "MELODY MODE": ("MELODY_INSTRUMENT",),
    "PHRASE MODE": ("PATTERN_INSTRUMENT",),
    "ONE PITCH": ("PATTERN_INSTRUMENT",),
    "ARTICULATIONS": ("PATTERN_INSTRUMENT", "MELODY_INSTRUMENT"),
    "ENDING": ("PATTERN_INSTRUMENT",),
}
TECHNIQUES = (
    "DOWNSTROKE", "UPSTROKE", "PALM_MUTE", "OPEN", "MUTED",
    "SLIDE", "LEGATO", "HAMMER_ON", "PULL_OFF", "NATURAL_HARMONIC",
    "PINCH_HARMONIC", "TREMOLO", "CHOKE", "LET_RING", "DEAD_NOTE",
)
VELOCITY_LAYERS = ("LOW", "MEDIUM", "HIGH")


def _as_int(value: Any, low: int = 0, high: int = 127) -> int | None:
    return value if type(value) is int and low <= value <= high else None


def _reviewed_techniques(asset: dict[str, Any], metadata: dict[str, Any]) -> list[str]:
    raw = metadata.get("confirmed_techniques") or metadata.get("confirmed_articulations") or []
    if not isinstance(raw, list):
        return []
    allowed = set(TECHNIQUES)
    values = {str(item).strip().upper().replace(" ", "_").replace("-", "_") for item in raw}
    return [item for item in TECHNIQUES if item in values and asset.get("review_status") == "REVIEWED"]


def _pitch_records(asset: dict[str, Any], metadata: dict[str, Any]) -> list[dict[str, Any]]:
    values: list[int] = []
    single = _as_int(asset.get("confirmed_midi_note"))
    if single is not None:
        values.append(single)
    sequence = asset.get("confirmed_note_sequence") or metadata.get("confirmed_note_sequence") or []
    if isinstance(sequence, list):
        values.extend(note for note in sequence if _as_int(note) is not None)
    result = []
    for note in dict.fromkeys(values):
        result.append({"midi_note": note, "pitch_class": note % 12, "octave": note // 12 - 1})
    return result


def _velocity_record(asset: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    lo = _as_int(metadata.get("velocity_min"), 1, 127)
    hi = _as_int(metadata.get("velocity_max"), 1, 127)
    layer = str(metadata.get("confirmed_velocity_layer") or "").upper()
    if lo is not None and hi is not None and lo <= hi:
        return {"status": "CONFIRMED_RANGE", "min": lo, "max": hi,
                "layer": layer if layer in VELOCITY_LAYERS else "UNASSIGNED"}
    if layer in VELOCITY_LAYERS and asset.get("review_status") == "REVIEWED":
        return {"status": "CONFIRMED_LAYER", "min": None, "max": None, "layer": layer}
    return {"status": "UNKNOWN", "min": None, "max": None, "layer": "UNKNOWN"}


def _pattern_readiness(metadata: dict[str, Any], frame_count: int | None = None) -> tuple[str, list[str]]:
    pattern = metadata.get("pattern_performance_review") or metadata.get("pattern") or {}
    if not isinstance(pattern, dict):
        pattern = {}
    missing: list[str] = []
    start, end = pattern.get("loop_start_sample"), pattern.get("loop_end_sample")
    if (type(start) is not int or type(end) is not int or start < 0 or end <= start
            or (type(frame_count) is int and end > frame_count)):
        missing.append("valid_loop_start_end_sample_within_clip")
    tempo = pattern.get("tempo_bpm")
    if not isinstance(tempo, (int, float)) or not 20 <= tempo <= 400:
        missing.append("tempo_bpm")
    signature = pattern.get("time_signature")
    if not isinstance(signature, str) or not re.fullmatch(r"[1-9][0-9]*/[1-9][0-9]*", signature):
        missing.append("time_signature")
    for field in ("attack_events", "technique_events", "harmonic_events"):
        values = pattern.get(field)
        if not isinstance(values, list) or not values or any(not isinstance(x, dict) for x in values):
            missing.append(field)
    beat_grid = pattern.get("beat_grid")
    if not isinstance(beat_grid, list) or not beat_grid or any(
        not isinstance(x, (int, float)) or x < 0 for x in beat_grid
    ) or beat_grid != sorted(beat_grid):
        missing.append("beat_grid")
    if pattern.get("cycle_integrity_verified") is not True:
        missing.append("cycle_integrity_verified")
    if pattern.get("musical_review_verified") is not True:
        missing.append("musical_review_verified")
    return ("STRUCTURE_VERIFIED" if not missing else "INCOMPLETE"), missing


def _melody_readiness(asset: dict[str, Any], metadata: dict[str, Any]) -> tuple[str, list[str]]:
    notes = asset.get("confirmed_note_sequence") or metadata.get("confirmed_note_sequence") or []
    events = metadata.get("confirmed_melody_events") or metadata.get("melody_events") or []
    missing: list[str] = []
    if not isinstance(notes, list) or len(notes) < 2 or any(_as_int(x) is None for x in notes):
        missing.append("confirmed_note_sequence")
    if not isinstance(events, list) or len(events) < 2:
        missing.append("confirmed_melody_events_with_timing")
    else:
        previous_start = -1.0
        for item in events:
            if not isinstance(item, dict):
                missing.append("melody_event_objects")
                break
            note, velocity = _as_int(item.get("midi_note")), _as_int(item.get("velocity"), 1, 127)
            start, duration = item.get("start_beats"), item.get("duration_beats")
            if (note is None or velocity is None
                    or not isinstance(start, (int, float)) or start < 0 or start < previous_start
                    or not isinstance(duration, (int, float)) or duration <= 0):
                missing.append("melody_event_pitch_timing_duration_or_velocity")
                break
            previous_start = float(start)
    boundaries = metadata.get("melody_phrase_boundaries")
    if isinstance(events, list) and len(events) >= 2 and isinstance(notes, list):
        event_notes = [item.get("midi_note") for item in events if isinstance(item, dict)]
        if event_notes != notes:
            missing.append("melody_note_sequence_mismatch")
    if not isinstance(boundaries, list) or len(boundaries) < 2 or any(
        not isinstance(value, (int, float)) or value < 0 for value in boundaries
    ) or boundaries != sorted(boundaries):
        missing.append("melody_phrase_boundaries")
    if metadata.get("melody_mapping_verified") is not True:
        missing.append("melody_mapping_verified")
    return ("STRUCTURE_VERIFIED" if not missing else "INCOMPLETE"), missing


def build_library_structure(catalog: dict[str, Any], *, catalog_path: str | Path | None = None) -> dict[str, Any]:
    if catalog.get("schema") != "ppgu.plugin_asset_catalog/1.0.0":
        raise ValueError("Unsupported or missing plugin asset catalog schema")
    sections = {item.get("mode"): item for item in catalog.get("modes", []) if isinstance(item, dict)}
    if list(sections) != list(MODES):
        raise ValueError("Catalog must contain all ten modes in the approved order")

    mode_rows = []
    global_assets: dict[str, dict[str, Any]] = {}
    technique_coverage = {technique: [] for technique in TECHNIQUES}
    pitch_coverage = {str(pc): [] for pc in range(12)}
    velocity_coverage = {layer: [] for layer in VELOCITY_LAYERS}
    pattern_records = []
    melody_records = []

    for mode in MODES:
        section = sections[mode]
        rows = []
        for asset in section.get("assets", []):
            asset_id = str(asset.get("asset_id") or "")
            if not asset_id:
                continue
            metadata = asset.get("musical_metadata") or {}
            if not isinstance(metadata, dict):
                metadata = {}
            approved_evidence = (
                asset.get("review_status") == "REVIEWED"
                and asset.get("license_status") == "LICENSE_APPROVED"
                and asset.get("integrity_status") == "VERIFIED"
            )
            techniques = _reviewed_techniques(asset, metadata) if approved_evidence else []
            pitches = _pitch_records(asset, metadata) if approved_evidence else []
            velocity = _velocity_record(asset, metadata) if approved_evidence else {
                "status": "UNKNOWN", "min": None, "max": None, "layer": "UNKNOWN"
            }
            review_ok = (
                asset.get("review_status") == "REVIEWED"
                and asset.get("license_status") == "LICENSE_APPROVED"
            )
            integrity_ok = asset.get("integrity_status") == "VERIFIED" and bool(asset.get("asset_file"))
            mode_mapping_ok = mode in (asset.get("playable_modes") or [])
            playable = bool(
                asset.get("playable") and asset.get("playable_in_mode")
                and review_ok and integrity_ok and mode_mapping_ok
            )
            status = (
                "RUNTIME_READY" if playable else
                "REVIEW_REQUIRED" if not review_ok else
                "INTEGRITY_BLOCKED" if not integrity_ok else
                "MODE_MAPPING_BLOCKED"
            )
            row = {
                "asset_id": asset_id,
                "asset_file": asset.get("asset_file"),
                "manifest_file": asset.get("manifest_file"),
                "kind": asset.get("kind", "UNKNOWN"),
                "status": status,
                "runtime_ready": playable,
                "review_status": asset.get("review_status", "NEEDS_MUSICAL_REVIEW"),
                "license_status": asset.get("license_status", "UNREVIEWED"),
                "integrity_status": asset.get("integrity_status", "UNKNOWN"),
                "confirmed_pitches": pitches,
                "confirmed_techniques": techniques,
                "velocity_zone": velocity,
                "blocking_reasons": asset.get("blocking_reasons", []),
                "source_start_sample": asset.get("source_start_sample"),
                "source_end_sample": asset.get("source_end_sample"),
                "source_sha256": asset.get("source_sha256"),
                "derived_sha256": asset.get("derived_sha256"),
            }
            rows.append(row)
            global_assets.setdefault(asset_id, row)
            for pitch in pitches:
                pitch_coverage[str(pitch["pitch_class"])].append(asset_id)
            if velocity["layer"] in velocity_coverage:
                velocity_coverage[velocity["layer"]].append(asset_id)
            for technique in techniques:
                technique_coverage[technique].append(asset_id)
            if mode == "PATTERN MODE":
                asset_kind = str(asset.get("kind") or "").casefold()
                is_note_zone = asset_kind in {
                    "note_event", "sample_note_candidate", "sample_note", "one_shot_sample"
                }
                if is_note_zone:
                    state = "NOTE_ZONE_READY" if pitches and asset.get("asset_file") else "NOTE_ZONE_INCOMPLETE"
                    missing = [] if pitches and asset.get("asset_file") else [
                        field for field, ok in (("confirmed_pitch_zone", bool(pitches)),
                                                ("derived_wav_reference", bool(asset.get("asset_file"))))
                        if not ok
                    ]
                    pattern_records.append({
                        "asset_id": asset_id, "asset_kind": asset_kind,
                        "pattern_structure_status": state, "missing_fields": missing,
                        "confirmed_pitches": pitches, "reviewed_techniques": techniques,
                        "metadata": {},
                    })
                else:
                    state, missing = _pattern_readiness(metadata, asset.get("frame_count"))
                    pattern_records.append({
                        "asset_id": asset_id, "asset_kind": asset_kind or "UNKNOWN",
                        "pattern_structure_status": state, "missing_fields": missing,
                        "reviewed_techniques": techniques,
                        "metadata": metadata.get("pattern_performance_review") or metadata.get("pattern") or {},
                    })
            if mode == "MELODY MODE":
                state, missing = _melody_readiness(asset, metadata)
                melody_records.append({"asset_id": asset_id, "melody_structure_status": state,
                                       "missing_fields": missing,
                                       "confirmed_note_sequence": asset.get("confirmed_note_sequence") or [],
                                       "confirmed_melody_events": metadata.get("confirmed_melody_events") or []})

        mode_rows.append({
            "mode": mode,
            "engine_targets": list(MODE_ENGINES[mode]),
            "asset_count": len(rows),
            "runtime_ready_count": sum(1 for item in rows if item["runtime_ready"]),
            "review_required_count": sum(1 for item in rows if item["status"] == "REVIEW_REQUIRED"),
            "mode_mapping_blocked_count": sum(1 for item in rows if item["status"] == "MODE_MAPPING_BLOCKED"),
            "integrity_blocked_count": sum(1 for item in rows if item["status"] == "INTEGRITY_BLOCKED"),
            "assets": rows,
        })

    for bucket in (pitch_coverage, velocity_coverage, technique_coverage):
        for key, asset_ids in bucket.items():
            bucket[key] = sorted(set(asset_ids))

    return {
        "schema": SCHEMA,
        "project": "POP PUNK GUITAR ULTIMATE",
        "manager_version": "3.0.0-dev6",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "catalog_path": str(Path(catalog_path).resolve()) if catalog_path else None,
        "library_policy": {
            "single_physical_samples_library": True,
            "logical_multi_mode_assignments": True,
            "wav_copies_created_by_structure_builder": False,
            "source_files_modified": False,
            "unreviewed_or_unlicensed_assets_playable": False,
            "unknown_music_data_fabricated": False,
            "engine_layout": "TWO_ENGINES_PATTERN_AND_MELODY_WITH_SAMPLE_NOTE_ZONES",
        },
        "engines": [
            {"engine": "SAMPLE_INSTRUMENT", "modes": ["SAMPLE MODE"]},
            {"engine": "PATTERN_INSTRUMENT", "modes": [m for m in MODES if "PATTERN_INSTRUMENT" in MODE_ENGINES[m]]},
            {"engine": "MELODY_INSTRUMENT", "modes": ["MELODY MODE", "ARTICULATIONS"]},
        ],
        "modes": mode_rows,
        "coverage": {
            "pitch_classes": [{"pitch_class": int(pc), "asset_ids": ids, "status": "COVERED" if ids else "GAP"}
                              for pc, ids in pitch_coverage.items()],
            "velocity_layers": [{"layer": layer, "asset_ids": ids, "status": "COVERED" if ids else "GAP"}
                                for layer, ids in velocity_coverage.items()],
            "techniques": [{"technique": technique, "asset_ids": ids,
                            "status": "COVERED" if ids else "GAP"} for technique, ids in technique_coverage.items()],
        },
        "pattern_mode": {
            "asset_count": len(pattern_records),
            "structure_verified_count": sum(x["pattern_structure_status"] == "STRUCTURE_VERIFIED" for x in pattern_records),
            "note_zone_ready_count": sum(x["pattern_structure_status"] == "NOTE_ZONE_READY" for x in pattern_records),
            "note_zone_incomplete_count": sum(x["pattern_structure_status"] == "NOTE_ZONE_INCOMPLETE" for x in pattern_records),
            "assets": pattern_records,
        },
        "melody_mode": {
            "asset_count": len(melody_records),
            "structure_verified_count": sum(x["melody_structure_status"] == "STRUCTURE_VERIFIED" for x in melody_records),
            "assets": melody_records,
        },
        "summary": {
            "unique_asset_count": len(global_assets),
            "mode_assignment_count": sum(item["asset_count"] for item in mode_rows),
            "multi_mode_asset_count": sum(1 for asset_id in global_assets
                                          if sum(asset_id in {x["asset_id"] for x in row["assets"]} for row in mode_rows) > 1),
            "runtime_ready_assignment_count": sum(item["runtime_ready_count"] for item in mode_rows),
            "pattern_structure_verified_count": sum(x["pattern_structure_status"] == "STRUCTURE_VERIFIED" for x in pattern_records),
            "melody_structure_verified_count": sum(x["melody_structure_status"] == "STRUCTURE_VERIFIED" for x in melody_records),
        },
    }


def validate_library_structure(structure: dict[str, Any]) -> list[str]:
    errors = []
    if structure.get("schema") != SCHEMA:
        errors.append("Unsupported library structure schema")
    modes = structure.get("modes")
    if not isinstance(modes, list) or [item.get("mode") for item in modes] != list(MODES):
        errors.append("All ten modes must be present in approved order")
        return errors
    seen = set()
    for mode in modes:
        for asset in mode.get("assets", []):
            key = (mode["mode"], asset.get("asset_id"))
            if not asset.get("asset_id") or key in seen:
                errors.append(f"Missing or duplicate asset assignment: {key}")
            seen.add(key)
            if asset.get("runtime_ready") and (
                asset.get("review_status") != "REVIEWED"
                or asset.get("license_status") != "LICENSE_APPROVED"
                or asset.get("integrity_status") != "VERIFIED"
                or not asset.get("asset_file")
                or mode["mode"] not in (asset.get("playable_modes") or [])
            ):
                errors.append(f"Runtime-ready assignment violates approval/integrity gate: {key}")
    return errors


def write_library_structure(catalog_path: Path, structure_path: Path, coverage_path: Path) -> dict[str, Any]:
    catalog_path, structure_path, coverage_path = map(lambda p: Path(p).resolve(),
                                                       (catalog_path, structure_path, coverage_path))
    if structure_path.exists() or coverage_path.exists():
        raise FileExistsError("Refusing to overwrite existing library structure or coverage report")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    structure = build_library_structure(catalog, catalog_path=catalog_path)
    errors = validate_library_structure(structure)
    if errors:
        raise ValueError("Invalid library structure: " + "; ".join(errors))
    coverage = {"schema": SCHEMA, "created_at_utc": structure["created_at_utc"],
                "summary": structure["summary"], "coverage": structure["coverage"],
                "pattern_mode": structure["pattern_mode"], "melody_mode": structure["melody_mode"]}
    for path, payload in ((structure_path, structure), (coverage_path, coverage)):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    return {"structure_path": str(structure_path), "coverage_path": str(coverage_path),
            "schema": SCHEMA, "summary": structure["summary"],
            "mode_count": len(structure["modes"]), "validation_errors": errors}
