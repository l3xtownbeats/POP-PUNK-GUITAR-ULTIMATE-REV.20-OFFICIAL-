#!/usr/bin/env python3
"""Build a non-destructive index of explicitly reviewed staged assets by PPGU mode.

This index is distinct from audio-analysis hypotheses: only a human-reviewed
manifest with an explicit mode assignment enters an approved assignment queue.
Unknown mappings remain visible and are never promoted to runtime-ready.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

MODE_ORDER = (
    "SAMPLE MODE", "STRUMMING", "ARPEGGIO", "PATTERN MODE", "RIFF MODE",
    "MELODY MODE", "PHRASE MODE", "ONE PITCH", "ARTICULATIONS", "ENDING",
)
VERSION = "1.0.0"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _runtime_gate(mode: str, manifest: dict[str, Any], wav_valid: bool) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if not wav_valid:
        reasons.append("DERIVED_WAV_MISSING_OR_HASH_MISMATCH")
    if manifest.get("review_status") != "REVIEWED":
        reasons.append("MUSICAL_REVIEW_NOT_APPROVED")
    if manifest.get("license_status") != "LICENSE_APPROVED":
        reasons.append("LICENSE_NOT_APPROVED")

    metadata = manifest.get("musical_metadata") or {}
    validation = manifest.get("review_validation") or {}

    # A review label alone is not sufficient for runtime readiness. Require
    # persisted provenance, integrity, and explicit approval confirmations.
    required_review_checks = (
        "source_sha256_verified",
        "derived_sha256_verified",
        "sample_boundaries_verified",
        "explicit_musical_approval",
        "explicit_license_approval",
    )
    for field in required_review_checks:
        if validation.get(field) is not True:
            reasons.append(f"REVIEW_VALIDATION_{field.upper()}_NOT_CONFIRMED")

    midi_note = metadata.get("confirmed_midi_note")
    confirmed_midi = type(midi_note) is int and 0 <= midi_note <= 127
    note_sequence = metadata.get("confirmed_note_sequence")
    confirmed_sequence = (
        isinstance(note_sequence, list)
        and len(note_sequence) >= 2
        and all(type(note) is int and 0 <= note <= 127 for note in note_sequence)
    )
    chord_name = metadata.get("confirmed_chord_name")
    confirmed_chord = isinstance(chord_name, str) and bool(chord_name.strip())

    if mode == "MELODY MODE":
        if not (confirmed_sequence or confirmed_midi):
            reasons.append("MELODY_NOTE_MAPPING_NOT_CONFIRMED")
        if validation.get("musical_mapping_verified") is not True:
            reasons.append("MELODY_MAPPING_VALIDATION_MISSING")
    elif mode == "SAMPLE MODE":
        if not (confirmed_midi or confirmed_chord or confirmed_sequence):
            reasons.append("SAMPLE_NOTE_OR_CHORD_MAPPING_NOT_CONFIRMED")
        if validation.get("musical_mapping_verified") is not True:
            reasons.append("SAMPLE_MAPPING_VALIDATION_MISSING")
    elif mode == "PATTERN MODE":
        pattern_review = metadata.get("pattern_performance_review")
        valid_pattern_review = (
            isinstance(pattern_review, dict)
            and pattern_review.get("cycle_integrity_verified") is True
            and pattern_review.get("musical_review_verified") is True
            and type(pattern_review.get("loop_start_sample")) is int
            and type(pattern_review.get("loop_end_sample")) is int
            and pattern_review["loop_start_sample"] >= 0
            and pattern_review["loop_end_sample"] > pattern_review["loop_start_sample"]
        )
        if not (confirmed_sequence or confirmed_chord or valid_pattern_review):
            reasons.append("PATTERN_PERFORMANCE_MAPPING_NOT_CONFIRMED")
        if validation.get("musical_mapping_verified") is not True:
            reasons.append("PATTERN_MAPPING_VALIDATION_MISSING")
    else:
        reasons.append("MODE_SPECIFIC_RUNTIME_VALIDATION_REQUIRED")

    return ("RUNTIME_READY" if not reasons else "NOT_RUNTIME_READY"), reasons

def build_mode_assignment_index(staging_root: Path) -> dict[str, Any]:
    """Index reviewed manifest assignments without moving, copying or editing assets."""
    root = Path(staging_root).expanduser().resolve()
    queues: dict[str, list[dict[str, Any]]] = {mode: [] for mode in MODE_ORDER}
    rejected: list[dict[str, Any]] = []
    if not root.exists():
        return {
            "schema_version": "1.0.0", "index_version": VERSION,
            "staging_root": str(root), "mode_count": len(MODE_ORDER),
            "assignment_count": 0, "modes": [
                {"mode": mode, "assignment_count": 0, "assets": []} for mode in MODE_ORDER
            ], "rejected_manifests": [], "status": "STAGING_NOT_FOUND",
        }

    for manifest_path in sorted(root.rglob("*.json")):
        if manifest_path.name.endswith(".tmp"):
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            rejected.append({"manifest_path": str(manifest_path),
                             "reason": f"MANIFEST_READ_ERROR:{type(exc).__name__}"})
            continue
        assignments = manifest.get("mode_assignments") or []
        if not assignments:
            continue
        if not isinstance(assignments, list) or any(mode not in MODE_ORDER for mode in assignments):
            rejected.append({"manifest_path": str(manifest_path), "reason": "INVALID_MODE_ASSIGNMENTS"})
            continue
        derived = Path(str(manifest.get("derived_path") or ""))
        if not derived.is_absolute():
            derived = (manifest_path.parent / derived).resolve()
        # A file can disappear or become unreadable between is_file() and
        # hashing (for example, removable/network drives or concurrent changes).
        # Treat that asset as invalid and continue indexing the remaining queue.
        try:
            wav_valid = (
                _inside(derived, root) and derived.is_file()
                and derived.suffix.lower() in {".wav", ".wave"}
                and bool(manifest.get("derived_sha256"))
                and _sha256(derived) == str(manifest.get("derived_sha256")).upper()
            )
        except OSError:
            wav_valid = False
        for mode in dict.fromkeys(assignments):
            runtime_status, reasons = _runtime_gate(mode, manifest, wav_valid)
            queues[mode].append({
                "asset_id": manifest.get("asset_id"),
                "manifest_path": str(manifest_path),
                "derived_path": str(derived),
                "derived_sha256": manifest.get("derived_sha256"),
                "source_path": manifest.get("source_path"),
                "source_sha256": manifest.get("source_sha256"),
                "source_start_sample": manifest.get("source_start_sample"),
                "source_end_sample": manifest.get("source_end_sample"),
                "asset_kind": manifest.get("asset_kind"),
                "musical_metadata": manifest.get("musical_metadata") or {},
                "review_status": manifest.get("review_status", "NEEDS_MUSICAL_REVIEW"),
                "license_status": manifest.get("license_status", "UNREVIEWED"),
                "runtime_status": runtime_status,
                "runtime_blockers": reasons,
                "source_modified": False,
            })

    modes = [{"mode": mode, "assignment_count": len(queues[mode]), "assets": queues[mode]}
             for mode in MODE_ORDER]
    return {
        "schema_version": "1.0.0", "index_version": VERSION,
        "staging_root": str(root), "mode_count": len(MODE_ORDER),
        "assignment_count": sum(len(items) for items in queues.values()),
        "modes": modes, "rejected_manifests": rejected,
        "status": "INDEXED" if any(queues.values()) else "NO_REVIEWED_MODE_ASSIGNMENTS",
        "policy": "EXPLICIT_MANIFEST_ASSIGNMENTS_ONLY",
        "source_files_modified": False, "source_files_moved_or_deleted": False,
        "automatic_factory_promotion": False,
    }


def write_mode_assignment_index(staging_root: Path, output_path: Path) -> dict[str, Any]:
    report = build_mode_assignment_index(staging_root)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite mode assignment index: {output}")
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output)
    return report
