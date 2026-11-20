#!/usr/bin/env python3
"""Explicit human review and license approval for staged WAV candidates."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from factory_curator import INSTRUMENTS, ROLES, STYLES, TONES
from audio_range_io import audio_source_info
from plugin_asset_catalog import MODE_ORDER


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def review_manifest(
    manifest_path: Path,
    staging_root: Path,
    *,
    style_family: str,
    instrument_family: str,
    asset_role: str,
    tone_family: str,
    musical_review_notes: str,
    license_evidence: str,
    approve_musical_review: bool = False,
    approve_license: bool = False,
    mode_assignments: list[str] | None = None,
    confirmed_midi_note: int | None = None,
    confirmed_chord_name: str | None = None,
    confirmed_note_sequence: list[int] | None = None,
    confirmed_techniques: list[str] | None = None,
    confirmed_velocity_layer: str | None = None,
    advanced_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate provenance and atomically record explicit human approvals."""
    manifest_path = Path(manifest_path).resolve()
    staging_root = Path(staging_root).resolve()
    if not _inside(manifest_path, staging_root) or not manifest_path.is_file():
        raise ValueError("Manifest must be an existing file inside LibraryManager/staging")
    if not approve_musical_review:
        raise ValueError("Musical review approval must be explicitly confirmed")
    if not approve_license:
        raise ValueError("License approval must be explicitly confirmed")
    if style_family not in STYLES:
        raise ValueError(f"style_family must be one of: {', '.join(sorted(STYLES))}")
    if instrument_family not in INSTRUMENTS:
        raise ValueError(f"instrument_family must be one of: {', '.join(sorted(INSTRUMENTS))}")
    if asset_role not in ROLES:
        raise ValueError(f"asset_role must be one of: {', '.join(sorted(ROLES))}")
    if tone_family not in TONES:
        raise ValueError(f"tone_family must be one of: {', '.join(sorted(TONES))}")
    if not musical_review_notes.strip():
        raise ValueError("Enter a short note describing what was musically checked")
    if not license_evidence.strip():
        raise ValueError("License approval requires a source, license name or evidence note")
    selected_modes = list(mode_assignments or [])
    if len(selected_modes) != len(set(selected_modes)) or any(mode not in MODE_ORDER for mode in selected_modes):
        raise ValueError("mode_assignments must contain unique approved VST3 library target categories")
    if confirmed_midi_note is not None and (
        type(confirmed_midi_note) is not int or not 0 <= confirmed_midi_note <= 127
    ):
        raise ValueError("confirmed_midi_note must be a MIDI note number from 0 to 127")
    if confirmed_chord_name is not None and (
        not isinstance(confirmed_chord_name, str) or not confirmed_chord_name.strip()
        or len(confirmed_chord_name.strip()) > 24
    ):
        raise ValueError("confirmed_chord_name must be a non-empty chord label up to 24 characters")
    selected_note_sequence = list(confirmed_note_sequence or [])
    if selected_note_sequence and (
        len(selected_note_sequence) < 2
        or any(type(note) is not int or not 0 <= note <= 127 for note in selected_note_sequence)
    ):
        raise ValueError("confirmed_note_sequence must contain at least two MIDI note numbers from 0 to 127")

    allowed_techniques = {
        "DOWNSTROKE", "UPSTROKE", "PALM_MUTE", "OPEN", "MUTED", "SLIDE",
        "LEGATO", "HAMMER_ON", "PULL_OFF", "NATURAL_HARMONIC",
        "PINCH_HARMONIC", "TREMOLO", "CHOKE", "LET_RING", "DEAD_NOTE",
    }
    selected_techniques = list(confirmed_techniques or [])
    if len(selected_techniques) != len(set(selected_techniques)) or any(
        item not in allowed_techniques for item in selected_techniques
    ):
        raise ValueError("confirmed_techniques contains an unsupported or duplicate technique")
    if confirmed_velocity_layer not in (None, "", "UNKNOWN", "LOW", "MEDIUM", "HIGH"):
        raise ValueError("confirmed_velocity_layer must be LOW, MEDIUM, HIGH or UNKNOWN")
    extra = dict(advanced_metadata or {})
    allowed_extra = {
        "pattern_performance_review", "confirmed_melody_events",
        "melody_phrase_boundaries", "melody_mapping_verified",
        "velocity_min", "velocity_max",
    }
    if set(extra) - allowed_extra:
        raise ValueError("advanced_metadata contains unsupported fields")
    pattern = extra.get("pattern_performance_review")
    if pattern is not None:
        if not isinstance(pattern, dict):
            raise ValueError("pattern_performance_review must be an object")
        start, end = pattern.get("loop_start_sample"), pattern.get("loop_end_sample")
        if type(start) is not int or type(end) is not int or start < 0 or end <= start:
            raise ValueError("Pattern loop sample boundaries must be valid integers")
        tempo = pattern.get("tempo_bpm")
        if not isinstance(tempo, (int, float)) or not 20 <= tempo <= 400:
            raise ValueError("Pattern tempo_bpm must be between 20 and 400")
        signature = pattern.get("time_signature")
        if not isinstance(signature, str) or not re.fullmatch(r"[1-9][0-9]*/[1-9][0-9]*", signature):
            raise ValueError("Pattern time_signature must be a valid ratio like 4/4")
        for field in ("attack_events", "technique_events", "harmonic_events"):
            if not isinstance(pattern.get(field), list) or not pattern[field] or any(
                not isinstance(event, dict) for event in pattern[field]
            ):
                raise ValueError(f"Pattern {field} must be a non-empty list of event objects")
        beat_grid = pattern.get("beat_grid")
        if not isinstance(beat_grid, list) or not beat_grid or any(
            not isinstance(value, (int, float)) or value < 0 for value in beat_grid
        ) or beat_grid != sorted(beat_grid):
            raise ValueError("Pattern beat_grid must be a non-empty ordered list of non-negative beat positions")
        if pattern.get("cycle_integrity_verified") is not True or pattern.get("musical_review_verified") is not True:
            raise ValueError("Pattern cycle integrity and musical review must be explicitly verified")
    melody_events = extra.get("confirmed_melody_events")
    if melody_events is not None:
        if not isinstance(melody_events, list) or len(melody_events) < 2:
            raise ValueError("confirmed_melody_events must contain at least two events")
        previous_start = -1.0
        for event in melody_events:
            if not isinstance(event, dict):
                raise ValueError("Each confirmed melody event must be an object")
            note, velocity = event.get("midi_note"), event.get("velocity")
            start, duration = event.get("start_beats"), event.get("duration_beats")
            if type(note) is not int or not 0 <= note <= 127:
                raise ValueError("Melody event midi_note must be in 0..127")
            if type(velocity) is not int or not 1 <= velocity <= 127:
                raise ValueError("Melody event velocity must be in 1..127")
            if not isinstance(start, (int, float)) or start < previous_start:
                raise ValueError("Melody event start_beats must be non-negative and ordered")
            if not isinstance(duration, (int, float)) or duration <= 0:
                raise ValueError("Melody event duration_beats must be positive")
            previous_start = float(start)
    boundaries = extra.get("melody_phrase_boundaries")
    if boundaries is not None and (
        not isinstance(boundaries, list) or len(boundaries) < 2
        or any(not isinstance(value, (int, float)) or value < 0 for value in boundaries)
        or boundaries != sorted(boundaries)
    ):
        raise ValueError("melody_phrase_boundaries must be an ordered list of at least two beat positions")
    if "melody_mapping_verified" in extra and type(extra["melody_mapping_verified"]) is not bool:
        raise ValueError("melody_mapping_verified must be true or false")
    for field in ("velocity_min", "velocity_max"):
        value = extra.get(field)
        if value is not None and (type(value) is not int or not 1 <= value <= 127):
            raise ValueError(f"{field} must be an integer in 1..127")
    if extra.get("velocity_min") is not None and extra.get("velocity_max") is not None:
        if extra["velocity_min"] > extra["velocity_max"]:
            raise ValueError("velocity_min cannot exceed velocity_max")

    record = json.loads(manifest_path.read_text(encoding="utf-8"))
    derived = Path(record.get("derived_path", ""))
    if not derived.is_absolute():
        derived = (manifest_path.parent / derived).resolve()
    if not _inside(derived, staging_root) or not derived.is_file():
        raise ValueError("Derived WAV must exist inside LibraryManager/staging")
    if derived.suffix.lower() not in {".wav", ".wave"}:
        raise ValueError("Only WAV candidates can be reviewed for FACTORY")
    expected_derived = str(record.get("derived_sha256", "")).upper()
    if not expected_derived or _sha256(derived) != expected_derived:
        raise ValueError("Derived WAV hash does not match manifest")

    source = Path(record.get("source_path", ""))
    expected_source = str(record.get("source_sha256", "")).upper()
    if not source.is_file() or not expected_source or _sha256(source) != expected_source:
        raise ValueError("Original source is missing or its SHA-256 changed")
    start = int(record.get("source_start_sample", -1))
    end = int(record.get("source_end_sample", -1))
    if start < 0 or end <= start:
        raise ValueError("Invalid source sample boundaries")
    original_info = audio_source_info(source)
    derived_info = audio_source_info(derived)
    if end > original_info.frames:
        raise ValueError("Source sample boundaries exceed the original audio")
    if derived_info.frames != end - start:
        raise ValueError("Derived WAV frame count does not match source boundaries")
    if derived_info.source_format.upper() != "WAV" or derived_info.source_subtype not in {"PCM_16", "PCM_24", "PCM_32", "PCM_U8", "PCM"}:
        raise ValueError("Derived asset must be uncompressed PCM WAV")
    if derived_info.framerate != original_info.framerate:
        raise ValueError("Derived WAV sample rate differs from original source")
    pattern_review = (advanced_metadata or {}).get("pattern_performance_review")
    if pattern_review is not None and pattern_review["loop_end_sample"] > derived_info.frames:
        raise ValueError("Pattern loop_end_sample exceeds the derived WAV frame count")

    metadata = record.setdefault("musical_metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("musical_metadata must be a JSON object")
    # A fresh review must re-confirm mappings; blank input revokes stale
    # confirmations instead of silently carrying them forward.
    for field in (
        "confirmed_midi_note", "confirmed_chord_name", "confirmed_note_sequence",
        "confirmed_techniques", "confirmed_velocity_layer", "velocity_min", "velocity_max",
        "pattern_performance_review", "confirmed_melody_events",
        "melody_phrase_boundaries", "melody_mapping_verified",
    ):
        metadata.pop(field, None)
    metadata.update({
        "style_family": style_family,
        "instrument_family": instrument_family,
        "asset_role": asset_role,
        "tone_family": tone_family,
        "format_family": "WAV",
        "musical_review_notes": musical_review_notes.strip(),
        "license_evidence": license_evidence.strip(),
    })
    if confirmed_midi_note is not None:
        metadata["confirmed_midi_note"] = confirmed_midi_note
    if confirmed_chord_name is not None:
        metadata["confirmed_chord_name"] = confirmed_chord_name.strip()
    if selected_note_sequence:
        metadata["confirmed_note_sequence"] = selected_note_sequence
    if selected_techniques:
        metadata["confirmed_techniques"] = selected_techniques
    if confirmed_velocity_layer and confirmed_velocity_layer != "UNKNOWN":
        metadata["confirmed_velocity_layer"] = confirmed_velocity_layer
    metadata.update(extra)
    record["review_status"] = "REVIEWED"
    record["license_status"] = "LICENSE_APPROVED"
    record["reviewed_at_utc"] = datetime.now(timezone.utc).isoformat()
    record["license_approved_at_utc"] = record["reviewed_at_utc"]
    record["mode_assignments"] = [mode for mode in MODE_ORDER if mode in selected_modes]
    record["review_validation"] = {
        "source_sha256_verified": True,
        "derived_sha256_verified": True,
        "sample_boundaries_verified": True,
        "explicit_musical_approval": True,
        "explicit_license_approval": True,
        "musical_mapping_verified": bool(
            confirmed_midi_note is not None or confirmed_chord_name is not None
            or selected_note_sequence or bool(melody_events)
        ),
    }

    fd, temp_name = tempfile.mkstemp(prefix=manifest_path.name + ".", suffix=".tmp",
                                     dir=str(manifest_path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, manifest_path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
    return {
        "manifest_path": str(manifest_path),
        "asset_id": record.get("asset_id"),
        "review_status": record["review_status"],
        "license_status": record["license_status"],
        "style_family": style_family,
        "derived_sha256": expected_derived,
        "source_sha256": expected_source,
        "factory_eligible": True,
        "mode_assignments": record["mode_assignments"],
        "musical_mapping_verified": record["review_validation"]["musical_mapping_verified"],
    }
