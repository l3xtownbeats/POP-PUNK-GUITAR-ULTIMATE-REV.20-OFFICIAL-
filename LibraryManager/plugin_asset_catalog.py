#!/usr/bin/env python3
"""Build a validated, vendor-neutral asset catalog for the POP PUNK GUITAR VST3.

The catalog is a bridge between Library Manager staging and the future plugin.
It contains all approved mode queues, exact provenance and relative WAV paths.
Unreviewed assets remain preview/review candidates and are never runtime-playable.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audio_range_io import audio_source_info

CATALOG_SCHEMA = "ppgu.plugin_asset_catalog/1.0.0"
STAGING_BASE = (Path(__file__).resolve().parent / "staging").resolve()
MODE_ORDER = (
    "SAMPLE MODE", "STRUMMING", "ARPEGGIO", "PATTERN MODE", "RIFF MODE",
    "MELODY MODE", "PHRASE MODE", "ONE PITCH", "ARTICULATIONS", "ENDING",
)
MODE_DESCRIPTIONS = {
    "SAMPLE MODE": "Pitch-specific note attacks, reviewed chord samples and Power Chords.",
    "STRUMMING": "Reviewed Downstroke, Upstroke and chord-strumming performances.",
    "ARPEGGIO": "Chord voicing hypotheses plus reviewed string-by-string arpeggio events.",
    "PATTERN MODE": "Repeated rhythmic patterns plus pitch-specific note zones.",
    "RIFF MODE": "Musically reviewed guitar riffs and characteristic fragments.",
    "MELODY MODE": "Pitch-specific notes and reviewed melodic sequences.",
    "PHRASE MODE": "Complete musical phrases with preserved source timing.",
    "ONE PITCH": "Rhythmic note sequences constrained to one verified pitch.",
    "ARTICULATIONS": "Reviewed Palm Mute, Open, Slide, Legato and related layers.",
    "ENDING": "Reviewed musical endings and outro performances.",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _resolve_record_path(value: Any, base: Path) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value).expanduser()
    return (path if path.is_absolute() else base / path).resolve()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _candidate_mode_assignments(record: dict[str, Any]) -> list[str]:
    kind = str(record.get("kind") or "").casefold()
    targets = {str(item).upper() for item in (record.get("engine_targets") or [])}
    modes: list[str] = [mode for mode in record.get("mode_assignments", []) if mode in MODE_ORDER]
    if kind in {"sample_note_candidate", "melody_single_note_candidate", "one_shot_sample", "note_event", "chord_sample_candidate", "power_chord_sample_candidate"} or "SAMPLE_MODE" in targets:
        modes.append("SAMPLE MODE")
    if kind in {"melody_phrase_candidate", "melody_single_note_candidate"} or "MELODY_MODE" in targets:
        modes.append("MELODY MODE")
    if kind == "rhythm_pattern" or "PATTERN_MODE" in targets:
        modes.append("PATTERN MODE")
    # A note-event clip is also the pitch-specific key payload for the approved
    # note-playable Pattern Mode; it is not a whole-loop chord-performance WAV.
    if kind == "note_event" and "PATTERN MODE" not in modes:
        modes.append("PATTERN MODE")
    return list(dict.fromkeys(modes))


def _read_mode_candidates(mode_report_path: Path | None) -> dict[str, list[dict[str, Any]]]:
    result = {mode: [] for mode in MODE_ORDER}
    if mode_report_path is None:
        return result
    report = json.loads(mode_report_path.read_text(encoding="utf-8"))
    for section in report.get("modes", []):
        mode = section.get("mode")
        if mode not in result:
            continue
        for candidate in section.get("candidates", []):
            result[mode].append({
                "candidate_id": candidate.get("candidate_id"),
                "candidate_type": candidate.get("candidate_type", "UNCLASSIFIED_CANDIDATE"),
                "source_path": candidate.get("source_path"),
                "source_sha256": candidate.get("source_sha256"),
                "source_start_sample": candidate.get("source_start_sample"),
                "source_end_sample": candidate.get("source_end_sample"),
                "evidence": candidate.get("evidence", []),
                "assignment_status": candidate.get("mode_assignment_status", "REQUIRES_REVIEW"),
                "review_status": candidate.get("review_status", "NEEDS_MUSICAL_REVIEW"),
                "license_status": candidate.get("license_status", "UNREVIEWED"),
                "chord_name_candidate": candidate.get("chord_name_candidate"),
                "root_pitch_class_candidate": candidate.get("root_pitch_class_candidate"),
                "quality_candidate": candidate.get("quality_candidate"),
                "pitch_classes_candidate": candidate.get("pitch_classes_candidate", []),
                "voicing_candidates": candidate.get("voicing_candidates", []),
                "voicing_candidate_count": candidate.get("voicing_candidate_count", 0),
                "tuning_name_candidate": candidate.get("tuning_name_candidate"),
                "tuning_status": candidate.get("tuning_status"),
                "tuning_open_midi": candidate.get("tuning_open_midi"),
                "max_fret": candidate.get("max_fret"),
                "max_fret_span": candidate.get("max_fret_span"),
                "physical_fingering_review_required": candidate.get("physical_fingering_review_required", False),
                "playable": False,
                "candidate_only": True,
                "blocking_reason": "Analysis candidate only; no approved staged playback asset is bound.",
            })
    return result


def _manifest_to_asset(
    manifest_path: Path,
    staging_root: Path,
    catalog_parent: Path,
    source_hash_cache: dict[str, bool],
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    try:
        record = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"Invalid manifest {manifest_path.name}: {exc}"]
    if not isinstance(record, dict):
        return None, [f"Manifest root must be an object: {manifest_path.name}"]

    asset_id = str(record.get("asset_id") or manifest_path.stem)
    derived = _resolve_record_path(record.get("derived_path"), manifest_path.parent)
    source = _resolve_record_path(record.get("source_path"), manifest_path.parent)
    source_digest = str(record.get("source_sha256") or "").upper()
    derived_digest = str(record.get("derived_sha256") or "").upper()
    start = record.get("source_start_sample")
    end = record.get("source_end_sample")
    frame_count = record.get("frame_count")
    review_status = str(record.get("review_status") or "NEEDS_MUSICAL_REVIEW")
    license_status = str(record.get("license_status") or "UNREVIEWED")
    review_validation = record.get("review_validation") or {}
    metadata = record.get("musical_metadata") or {}

    if not re.fullmatch(r"[0-9A-F]{64}", source_digest):
        errors.append("source_sha256 is missing or invalid")
    if not re.fullmatch(r"[0-9A-F]{64}", derived_digest):
        errors.append("derived_sha256 is missing or invalid")
    if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end <= start:
        errors.append("source sample offsets are invalid")
    if not isinstance(frame_count, int) or frame_count <= 0:
        errors.append("frame_count is missing or invalid")
    elif isinstance(start, int) and isinstance(end, int) and frame_count != end - start:
        errors.append("frame_count does not match source offsets")
    if derived is None or not derived.is_file():
        errors.append("derived WAV is missing")
    elif not _inside(derived, staging_root):
        errors.append("derived WAV resolves outside staging")
    elif derived.suffix.lower() not in {".wav", ".wave"}:
        errors.append("plugin sample asset must be WAV")
    if source is None or not source.is_file():
        errors.append("original source file is missing")

    derived_ok = False
    if derived is not None and derived.is_file() and re.fullmatch(r"[0-9A-F]{64}", derived_digest):
        try:
            derived_ok = _sha256(derived) == derived_digest
        except OSError as exc:
            errors.append(f"cannot hash derived WAV: {exc}")
        if not derived_ok:
            errors.append("derived WAV SHA-256 mismatch")

    source_ok = False
    if source is not None and source.is_file() and re.fullmatch(r"[0-9A-F]{64}", source_digest):
        cache_key = str(source)
        if cache_key not in source_hash_cache:
            try:
                source_hash_cache[cache_key] = _sha256(source) == source_digest
            except OSError:
                source_hash_cache[cache_key] = False
        source_ok = source_hash_cache[cache_key]
        if not source_ok:
            errors.append("original source SHA-256 mismatch")

    # Independently validate the exact frame mapping and PCM container before
    # any asset can be advertised as loadable by the future plugin.
    if source is not None and source.is_file() and derived is not None and derived.is_file() and _inside(derived, staging_root):
        if isinstance(start, int) and isinstance(end, int) and end > start:
            try:
                source_info = audio_source_info(source)
                derived_info = audio_source_info(derived)
                if end > source_info.frames:
                    errors.append("source sample offsets exceed original audio length")
                if derived_info.frames != end - start:
                    errors.append("derived WAV frame count does not match source offsets")
                if derived_info.framerate != source_info.framerate:
                    errors.append("derived WAV sample rate differs from original source")
                if derived_info.source_format.upper() != "WAV" or derived_info.source_subtype not in {
                    "PCM_16", "PCM_24", "PCM_32", "PCM_U8", "PCM"
                }:
                    errors.append("derived asset is not uncompressed PCM WAV")
            except Exception as exc:
                errors.append(f"audio range validation failed: {type(exc).__name__}: {exc}")

    confirmed_mapping = (
        type(metadata.get("confirmed_midi_note")) is int
        and 0 <= metadata.get("confirmed_midi_note") <= 127
    ) or bool(str(metadata.get("confirmed_chord_name") or "").strip()) or (
        isinstance(metadata.get("confirmed_note_sequence"), list)
        and len(metadata.get("confirmed_note_sequence")) >= 2
        and all(type(note) is int and 0 <= note <= 127
                for note in metadata.get("confirmed_note_sequence"))
    )
    approval_reasons = []
    if review_status != "REVIEWED":
        approval_reasons.append("requires REVIEWED musical approval")
    if license_status != "LICENSE_APPROVED" or not str(metadata.get("license_evidence") or "").strip():
        approval_reasons.append("requires LICENSE_APPROVED status and evidence")
    for field in (
        "source_sha256_verified", "derived_sha256_verified", "sample_boundaries_verified",
        "explicit_musical_approval", "explicit_license_approval", "musical_mapping_verified",
    ):
        if review_validation.get(field) is not True:
            approval_reasons.append(f"review_validation.{field} is not confirmed")
    if not confirmed_mapping:
        approval_reasons.append("confirmed MIDI note, chord label or note sequence is missing")
    approvals_ok = not approval_reasons

    valid_integrity = not errors and source_ok and derived_ok
    target_modes = _candidate_mode_assignments(record)
    confirmed_note = type(metadata.get("confirmed_midi_note")) is int and 0 <= metadata.get("confirmed_midi_note") <= 127
    confirmed_chord = bool(str(metadata.get("confirmed_chord_name") or "").strip())
    confirmed_sequence = (
        isinstance(metadata.get("confirmed_note_sequence"), list)
        and len(metadata.get("confirmed_note_sequence")) >= 2
        and all(type(note) is int and 0 <= note <= 127 for note in metadata.get("confirmed_note_sequence"))
    )
    playable_modes = []
    for mode in target_modes:
        # The current Manager can supply pitch-mapped Sample/Melody zones.
        # Other performance engines need reviewed event timelines that are not
        # fabricated by this asset-only extraction pipeline.
        if mode == "SAMPLE MODE" and (confirmed_note or confirmed_chord or confirmed_sequence):
            playable_modes.append(mode)
        elif mode == "MELODY MODE" and (confirmed_note or confirmed_sequence):
            playable_modes.append(mode)
    playable = valid_integrity and approvals_ok and bool(playable_modes)
    blocking = list(errors) + approval_reasons
    if valid_integrity and approvals_ok and not playable_modes:
        blocking.append("mode-specific reviewed event mapping is not yet available for this performance mode")
    relative_audio = None
    if derived is not None and derived.is_file() and _inside(derived, staging_root):
        relative_audio = Path(os.path.relpath(derived, catalog_parent)).as_posix()

    return {
        "asset_id": asset_id,
        "kind": record.get("kind", "UNKNOWN"),
        "target_modes": target_modes,
        "playable_modes": playable_modes,
        "mode_assignments": [mode for mode in record.get("mode_assignments", []) if mode in MODE_ORDER],
        "asset_file": relative_audio,
        "manifest_file": Path(os.path.relpath(manifest_path.resolve(), catalog_parent)).as_posix(),
        "source_path": str(source) if source else str(record.get("source_path") or ""),
        "source_sha256": source_digest or None,
        "source_start_sample": start,
        "source_end_sample": end,
        "sample_rate": record.get("sample_rate"),
        "channels": record.get("channels"),
        "frame_count": frame_count,
        "duration_seconds": record.get("duration_seconds"),
        "derived_sha256": derived_digest or None,
        "midi_note_candidate": metadata.get("midi_note_candidate"),
        "note_name_candidate": metadata.get("note_name_candidate"),
        "note_candidates": metadata.get("note_candidates", []),
        "confirmed_midi_note": metadata.get("confirmed_midi_note"),
        "confirmed_chord_name": metadata.get("confirmed_chord_name"),
        "confirmed_note_sequence": metadata.get("confirmed_note_sequence", []),
        "chord_name_candidate": metadata.get("chord_name_candidate"),
        "root_pitch_class_candidate": metadata.get("root_pitch_class_candidate"),
        "quality_candidate": metadata.get("quality_candidate"),
        "pitch_classes_candidate": metadata.get("pitch_classes_candidate", []),
        "voicing_candidate": metadata.get("voicing_candidate", "UNKNOWN"),
        "string_fret_positions": metadata.get("string_fret_positions"),
        "articulation_candidates": metadata.get("articulation_candidates", ["UNKNOWN"]),
        "velocity_candidate": metadata.get("velocity_candidate"),
        "musical_metadata": metadata,
        "review_status": review_status,
        "license_status": license_status,
        "license_evidence": metadata.get("license_evidence"),
        "integrity_status": "VERIFIED" if valid_integrity else "BLOCKED",
        "playable": playable,
        "blocking_reasons": blocking,
        "automatic_factory_promotion": False,
        "source_modified": False,
    }, errors


def validate_plugin_asset_catalog(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if catalog.get("schema") != CATALOG_SCHEMA:
        errors.append("Unsupported plugin catalog schema")
    modes = catalog.get("modes")
    if not isinstance(modes, list):
        errors.append("modes must be a list")
        return errors
    names = [item.get("mode") for item in modes if isinstance(item, dict)]
    if names != list(MODE_ORDER):
        errors.append("Catalog must contain all ten modes in the approved order")
    seen: set[tuple[str, str]] = set()
    for mode in modes:
        if not isinstance(mode, dict):
            errors.append("Mode entry must be an object")
            continue
        for asset in mode.get("assets", []):
            asset_id = str(asset.get("asset_id") or "")
            if not asset_id:
                errors.append(f"{mode.get('mode')}: asset without asset_id")
            mode_asset_key = (str(mode.get("mode")), asset_id)
            if mode_asset_key in seen:
                errors.append(f"Duplicate asset_id within mode {mode.get('mode')}: {asset_id}")
            seen.add(mode_asset_key)
            if asset.get("playable") and (
                mode.get("mode") not in asset.get("playable_modes", [])
                or not asset.get("playable_in_mode")
                or asset.get("review_status") != "REVIEWED"
                or asset.get("license_status") != "LICENSE_APPROVED"
                or asset.get("integrity_status") != "VERIFIED"
                or not asset.get("asset_file")
                or not (
                    type(asset.get("confirmed_midi_note")) is int
                    or bool(asset.get("confirmed_chord_name"))
                    or len(asset.get("confirmed_note_sequence") or []) >= 2
                )
            ):
                errors.append(f"Playable asset does not satisfy review/integrity gates: {asset_id}")
    return errors


def build_plugin_asset_catalog(
    staging_root: Path,
    output_path: Path,
    *,
    mode_report_path: Path | None = None,
    pattern_engine_manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Build a plugin-consumable catalog; unreviewed items are never playable."""
    staging_root = Path(staging_root).expanduser().resolve()
    output_path = Path(output_path).expanduser().resolve()
    try:
        staging_root.relative_to(STAGING_BASE)
    except ValueError as exc:
        raise ValueError("Catalog input must be inside LibraryManager/staging") from exc
    output_path.parent.mkdir(parents=True, exist_ok=True)

    mode_candidates = _read_mode_candidates(Path(mode_report_path).resolve() if mode_report_path else None)
    mode_assets = {mode: [] for mode in MODE_ORDER}
    review_queue: list[dict[str, Any]] = []
    source_hash_cache: dict[str, bool] = {}
    manifests_dir = staging_root / "manifests"
    manifest_paths = sorted(manifests_dir.glob("*.json")) if manifests_dir.is_dir() else []
    integrity_errors: list[dict[str, str]] = []

    for manifest_path in manifest_paths:
        asset, errors = _manifest_to_asset(
            manifest_path, staging_root, output_path.parent, source_hash_cache,
        )
        if asset is None:
            integrity_errors.extend({"manifest": str(manifest_path), "error": error} for error in errors)
            continue
        if errors:
            integrity_errors.extend({"manifest": str(manifest_path), "error": error} for error in errors)
        if not asset["target_modes"]:
            review_queue.append(asset)
            continue
        for mode in asset["target_modes"]:
            if mode in mode_assets:
                mode_assets[mode].append(asset)

    modes = []
    for mode in MODE_ORDER:
        source_assets = sorted(mode_assets[mode], key=lambda item: (item["kind"], item["asset_id"]))
        assets = []
        for source_asset in source_assets:
            mode_asset = dict(source_asset)
            mode_asset["playable_in_mode"] = mode in source_asset.get("playable_modes", [])
            mode_asset["playable"] = mode_asset["playable_in_mode"]
            if not mode_asset["playable_in_mode"]:
                mode_asset["mode_blocking_reason"] = (
                    "This mode requires a reviewed event timeline or mode-specific mapping; "
                    "a WAV file and generic note/chord label are not enough."
                )
            assets.append(mode_asset)
        candidates = mode_candidates[mode]
        playable_count = sum(1 for item in assets if item["playable_in_mode"])
        modes.append({
            "mode": mode,
            "description": MODE_DESCRIPTIONS[mode],
            "candidate_count": len(candidates),
            "asset_count": len(assets),
            "playable_asset_count": playable_count,
            "status": "READY_FOR_PLUGIN_IMPORT" if playable_count else (
                "REVIEW_REQUIRED" if assets or candidates else "NO_VERIFIED_ASSETS"
            ),
            "candidates": candidates,
            "assets": assets,
        })

    playable_assets = []
    for mode in modes:
        for asset in mode["assets"]:
            if asset["playable"] and asset["asset_id"] not in {item["asset_id"] for item in playable_assets}:
                playable_assets.append(asset)

    pattern_manifest = None
    if pattern_engine_manifest_path:
        try:
            pattern_manifest = json.loads(Path(pattern_engine_manifest_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            integrity_errors.append({"manifest": str(pattern_engine_manifest_path), "error": str(exc)})

    catalog = {
        "schema": CATALOG_SCHEMA,
        "project": "POP PUNK GUITAR ULTIMATE",
        "catalog_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "READY_FOR_PLUGIN_IMPORT" if playable_assets else "CANDIDATES_ONLY_NO_APPROVED_RUNTIME_ASSETS",
        "plugin_runtime_contract": {
            "asset_paths_are_relative_to_catalog": True,
            "selector_keys_are_control_only": True,
            "pattern_selector_note_numbers": None,
            "host_calibration_required": "FL_STUDIO_20",
            "note_playback": "MIDI_NOTE_TO_PITCH_SPECIFIC_WAV_ZONE",
            "pattern_playback": "CHORD_INPUT_TO_EVENT_PATTERN_WITH_PITCH_SPECIFIC_NOTE_ZONES",
            "chord_adaptation": "REVIEWED_NOTE_ZONES_AND_VOICINGS_ONLY",
            "whole_wav_chromatic_transposition_as_chord_engine": False,
            "unknown_musical_metadata_must_remain_unknown": True,
            "audio_callback_file_io_allowed": False,
        },
        "modes": modes,
        "playable_assets": playable_assets,
        "unassigned_review_assets": review_queue,
        "integrity_errors": integrity_errors,
        "safety": {
            "source_files_modified": False,
            "source_files_moved_or_deleted": False,
            "automatic_factory_promotion": False,
            "unreviewed_assets_playable": False,
            "required_review_status": "REVIEWED",
            "required_license_status": "LICENSE_APPROVED",
        },
        "pattern_engine_manifest": pattern_manifest,
    }
    validation_errors = validate_plugin_asset_catalog(catalog)
    if validation_errors:
        raise ValueError("Invalid plugin asset catalog: " + "; ".join(validation_errors))

    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing plugin catalog: {output_path}")
    temporary.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output_path)
    return {
        "catalog_path": str(output_path),
        "schema": CATALOG_SCHEMA,
        "status": catalog["status"],
        "mode_count": len(modes),
        "asset_count": sum(item["asset_count"] for item in modes),
        "candidate_count": sum(item["candidate_count"] for item in modes),
        "playable_asset_count": len(playable_assets),
        "unassigned_review_asset_count": len(review_queue),
        "integrity_error_count": len(integrity_errors),
        "source_files_modified": False,
        "automatic_factory_promotion": False,
    }
