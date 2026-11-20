#!/usr/bin/env python3
"""Versioned PPGU Performance Manifest contract for the future VST3 runtime.

The manager exports verified asset bindings and a strict event schema. It does
not fabricate performance ticks, strum directions, string/fret positions,
microtiming or articulation events that have not been reviewed.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from plugin_asset_catalog import CATALOG_SCHEMA, MODE_ORDER
from chromatic_pitch_map import SCHEMA as CHROMATIC_PITCH_MAP_SCHEMA, build_chromatic_pitch_map

PERFORMANCE_SCHEMA = "ppgu.performance_manifest/1.0.0"

MODE_EXECUTION_MODELS = {
    "SAMPLE MODE": "PITCH_SPECIFIC_SAMPLE_ZONES",
    "STRUMMING": "STRUMMING_EVENT_SEQUENCE",
    "ARPEGGIO": "ARPEGGIO_STRING_EVENT_SEQUENCE",
    "PATTERN MODE": "PATTERN_EVENT_SEQUENCE_WITH_PITCH_ZONES",
    "RIFF MODE": "RIFF_EVENT_SEQUENCE",
    "MELODY MODE": "MELODY_NOTE_SEQUENCE",
    "PHRASE MODE": "PHRASE_EVENT_SEQUENCE",
    "ONE PITCH": "ONE_PITCH_RHYTHM_SEQUENCE",
    "ARTICULATIONS": "ARTICULATION_LAYER_EVENTS",
    "ENDING": "ENDING_EVENT_SEQUENCE",
}

REQUIRED_EVENT_FIELDS = (
    "event_id", "position_ticks", "duration_ticks", "event_kind",
    "review_status", "source_sha256", "source_start_sample", "source_end_sample",
)
OPTIONAL_REVIEWED_EVENT_FIELDS = (
    "midi_pitch", "chord_interval", "string_number", "fret_number",
    "stroke_direction", "articulation", "velocity_layer",
    "round_robin_group", "sample_zone_id", "transition_role",
    "noise_event_kind", "microtiming_ticks",
)


def build_performance_manifest(
    catalog_path: Path,
    output_path: Path,
    chromatic_pitch_map: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a performance manifest beside its catalog, preserving relative paths."""
    catalog_path = Path(catalog_path).expanduser().resolve()
    output_path = Path(output_path).expanduser().resolve()
    if catalog_path.parent != output_path.parent:
        raise ValueError("Performance Manifest must be written beside its asset catalog")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if catalog.get("schema") != CATALOG_SCHEMA:
        raise ValueError("Unsupported or invalid plugin asset catalog")

    mode_bindings = {mode: [] for mode in MODE_ORDER}
    mode_candidate_bindings = {mode: [] for mode in MODE_ORDER}
    bindings_by_id: dict[str, dict[str, Any]] = {}
    for section in catalog.get("modes", []):
        mode = section.get("mode")
        if mode not in mode_bindings:
            continue
        mode_candidate_bindings[mode] = section.get("candidates", [])
        for asset in section.get("assets", []):
            asset_id = str(asset.get("asset_id") or "")
            if not asset_id:
                continue
            mode_bindings[mode].append(asset_id)
            binding = bindings_by_id.get(asset_id)
            if binding is None:
                binding = {
                    "asset_id": asset_id,
                    "kind": asset.get("kind", "UNKNOWN"),
                    "asset_file": asset.get("asset_file"),
                    "target_modes": [],
                    "playable_modes": asset.get("playable_modes", []),
                    "mode_assignments": asset.get("mode_assignments", []),
                    "source_path": asset.get("source_path"),
                    "source_sha256": asset.get("source_sha256"),
                    "source_start_sample": asset.get("source_start_sample"),
                    "source_end_sample": asset.get("source_end_sample"),
                    "sample_rate": asset.get("sample_rate"),
                    "channels": asset.get("channels"),
                    "frame_count": asset.get("frame_count"),
                    "derived_sha256": asset.get("derived_sha256"),
                    "midi_note_candidate": asset.get("midi_note_candidate"),
                    "confirmed_midi_note": asset.get("confirmed_midi_note"),
                    "confirmed_chord_name": asset.get("confirmed_chord_name"),
                    "confirmed_note_sequence": asset.get("confirmed_note_sequence", []),
                    "note_name_candidate": asset.get("note_name_candidate"),
                    "chord_name_candidate": asset.get("chord_name_candidate"),
                    "quality_candidate": asset.get("quality_candidate"),
                    "pitch_classes_candidate": asset.get("pitch_classes_candidate", []),
                    "voicing_candidate": asset.get("voicing_candidate", "UNKNOWN"),
                    "string_fret_positions": asset.get("string_fret_positions"),
                    "articulation_candidates": asset.get("articulation_candidates", ["UNKNOWN"]),
                    "velocity_candidate": asset.get("velocity_candidate"),
                    "review_status": asset.get("review_status", "NEEDS_MUSICAL_REVIEW"),
                    "license_status": asset.get("license_status", "UNREVIEWED"),
                    "integrity_status": asset.get("integrity_status", "BLOCKED"),
                    "playable": bool(asset.get("playable")),
                    "blocking_reasons": asset.get("blocking_reasons", []),
                }
                bindings_by_id[asset_id] = binding
            if mode not in binding["target_modes"]:
                binding["target_modes"].append(mode)

    bindings = sorted(bindings_by_id.values(), key=lambda item: item["asset_id"])
    manifest = {
        "schema": PERFORMANCE_SCHEMA,
        "project": "POP PUNK GUITAR ULTIMATE",
        "status": ("ASSET_BINDINGS_AVAILABLE_EVENT_TIMELINE_PENDING" if any(item["playable"] for item in bindings) else "REVIEW_ONLY_ASSET_BINDINGS_EVENT_TIMELINE_PENDING") if bindings else "TEMPLATE_ONLY_NO_STAGED_ASSETS",
        "catalog_schema": catalog.get("schema"),
        "catalog_file": catalog_path.name,
        "mode_execution_models": [
            {"mode": mode, "execution_model": MODE_EXECUTION_MODELS[mode]}
            for mode in MODE_ORDER
        ],
        "mode_asset_bindings": mode_bindings,
        "mode_candidate_bindings": mode_candidate_bindings,
        "asset_bindings": bindings,
        "events": [],
        "event_count": 0,
        "event_contract": {
            "required_fields": list(REQUIRED_EVENT_FIELDS),
            "optional_reviewed_fields": list(OPTIONAL_REVIEWED_EVENT_FIELDS),
            "position_unit": "DAW_PPQ_TICKS",
            "tempo_bpm": None,
            "time_signature": None,
            "host_position_ticks": None,
            "unknown_timing_must_remain_unknown": True,
        },
        "chromatic_pitch_map": chromatic_pitch_map or build_chromatic_pitch_map(catalog),
        "midi_contract": {
            "chromatic_pitch_map_schema": CHROMATIC_PITCH_MAP_SCHEMA,
            "all_12_chromatic_pitch_classes_playable_requirement": True,
            "enharmonic_aliases_share_one_pitch_class": True,
            "autochords_uses_same_canonical_pitch_classes": True,
            "autochords_must_not_drop_chromatic_pitch_classes": True,
            "pattern_selector_keys_are_control_only": True,
            "selector_note_numbers": None,
            "playable_note_range": None,
            "host_octave_calibration": "REQUIRED_IN_FL_STUDIO_20",
            "selector_and_playable_ranges_must_not_overlap": True,
            "midi_key_switch_support": True,
        },
        "realtime_contract": {
            "audio_callback_file_io_allowed": False,
            "audio_callback_hashing_or_decoding_allowed": False,
            "bounded_voice_pool_required": True,
            "voice_count_control_required": True,
            "chord_change_preserves_pattern_phase": True,
            "articulation_switch_preserves_rhythm_phase": True,
            "pattern_change_applies_at_musical_boundary": True,
            "active_voices_must_release_without_clicks_or_stuck_notes": True,
            "whole_wav_chromatic_transposition_as_chord_engine": False,
            "host_transport_tempo_position_sync_required": True,
        },
        "review_policy": {
            "runtime_playable_requires": [
                "REVIEWED", "LICENSE_APPROVED", "INTEGRITY_VERIFIED",
            ],
            "unreviewed_assets_playable": False,
            "automatic_factory_promotion": False,
            "unknown_musical_facts_must_remain_unknown": True,
        },
        "safety": {
            "source_files_modified": False,
            "source_files_moved_or_deleted": False,
            "events_invented": False,
        },
    }
    errors = validate_performance_manifest(manifest)
    if errors:
        raise ValueError("Invalid Performance Manifest: " + "; ".join(errors))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite Performance Manifest: {output_path}")
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
            stream.flush()
        temporary.replace(output_path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return {
        "manifest_path": str(output_path),
        "schema": PERFORMANCE_SCHEMA,
        "status": manifest["status"],
        "mode_count": len(mode_bindings),
        "asset_binding_count": len(bindings),
        "playable_binding_count": sum(1 for item in bindings if item["playable"]),
        "event_count": 0,
        "source_files_modified": False,
    }


def validate_performance_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != PERFORMANCE_SCHEMA:
        errors.append("Unsupported Performance Manifest schema")
    pitch_map = manifest.get("chromatic_pitch_map")
    if not isinstance(pitch_map, dict) or pitch_map.get("schema") != CHROMATIC_PITCH_MAP_SCHEMA:
        errors.append("A valid shared chromatic pitch map is required")
    else:
        classes = pitch_map.get("pitch_classes", [])
        if [item.get("pitch_class") for item in classes] != list(range(12)):
            errors.append("The shared pitch map must contain all 12 chromatic pitch classes")
        if pitch_map.get("enharmonic_aliases_are_merged") is not True:
            errors.append("Enharmonic spellings must resolve to one pitch class")
        if pitch_map.get("autochords_uses_same_pitch_class_map") is not True:
            errors.append("Auto Chords must use the shared chromatic pitch map")
    models = manifest.get("mode_execution_models")
    if not isinstance(models, list) or [item.get("mode") for item in models] != list(MODE_ORDER):
        errors.append("All ten mode execution models must be present in approved order")
    mode_bindings = manifest.get("mode_asset_bindings")
    if not isinstance(mode_bindings, dict) or list(mode_bindings) != list(MODE_ORDER):
        errors.append("mode_asset_bindings must contain all ten modes in approved order")
    candidate_bindings = manifest.get("mode_candidate_bindings")
    if not isinstance(candidate_bindings, dict) or list(candidate_bindings) != list(MODE_ORDER):
        errors.append("mode_candidate_bindings must contain all ten modes in approved order")
    events = manifest.get("events")
    if not isinstance(events, list) or manifest.get("event_count") != len(events):
        errors.append("events/event_count are inconsistent")
    for event in events if isinstance(events, list) else []:
        if not isinstance(event, dict):
            errors.append("Every performance event must be an object")
            continue
        missing = [field for field in REQUIRED_EVENT_FIELDS if field not in event]
        if missing:
            errors.append("Performance event missing: " + ", ".join(missing))
        start, end = event.get("source_start_sample"), event.get("source_end_sample")
        if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end <= start:
            errors.append("Performance event source sample offsets are invalid")
        position, duration = event.get("position_ticks"), event.get("duration_ticks")
        if not isinstance(position, int) or position < 0 or not isinstance(duration, int) or duration <= 0:
            errors.append("Performance event DAW tick position/duration are invalid")
        digest = str(event.get("source_sha256") or "").upper()
        if not re.fullmatch(r"[0-9A-F]{64}", digest):
            errors.append("Performance event source SHA-256 is invalid")
        if event.get("review_status") != "REVIEWED":
            errors.append("Unreviewed performance events cannot enter a runtime timeline")
    for binding in manifest.get("asset_bindings", []):
        if not isinstance(binding, dict) or not binding.get("asset_id"):
            errors.append("Every asset binding requires asset_id")
            continue
        if binding.get("playable") and (
            binding.get("review_status") != "REVIEWED"
            or binding.get("license_status") != "LICENSE_APPROVED"
            or binding.get("integrity_status") != "VERIFIED"
            or not binding.get("asset_file")
            or not binding.get("playable_modes")
            or not (
                type(binding.get("confirmed_midi_note")) is int
                or bool(binding.get("confirmed_chord_name"))
                or len(binding.get("confirmed_note_sequence") or []) >= 2
            )
        ):
            errors.append("Playable asset binding does not satisfy mode/mapping/approval/integrity gates")
    if manifest.get("safety", {}).get("events_invented") is not False:
        errors.append("Performance event invention must remain disabled")
    return errors
