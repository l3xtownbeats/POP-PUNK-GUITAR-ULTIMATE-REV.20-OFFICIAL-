#!/usr/bin/env python3
"""Fail-closed validator for approved PATTERN_MODE note-event clip manifests.

This is an offline Library Manager gate, not an audio-thread component. It
publishes only immutable, provenance-complete mappings. An empty registry is
valid but never reports READY.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import wave
from typing import Any

_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
_ALLOWED_KIND = "note_event"
_ALLOWED_ENGINE = "PATTERN_MODE"


@dataclass(frozen=True)
class PatternClipMapping:
    asset_id: str
    clip_path: Path
    clip_sha256: str
    source_sha256: str
    source_start_sample: int
    source_end_sample: int
    sample_rate: int
    trigger_midi_note: int
    source_midi_note: int
    articulation_id: str
    velocity_min: int
    velocity_max: int
    round_robin_group: str


@dataclass(frozen=True)
class PatternClipRegistry:
    mappings: tuple[PatternClipMapping, ...]
    ready: bool
    status: str


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _required_int(value: Any, field: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{field} must be an integer >= {minimum}")
    return value


def _sha(value: Any, field: str) -> str:
    result = _required_text(value, field)
    if not _SHA256.fullmatch(result):
        raise ValueError(f"{field} must be a 64-character SHA-256")
    return result.upper()


def _resolve_packaged_file(root: Path, raw: Any, field: str) -> Path:
    text = _required_text(raw, field)
    relative = PurePosixPath(text.replace("\\", "/"))
    if relative.is_absolute() or not relative.parts or any(p in ("", ".", "..") for p in relative.parts):
        raise ValueError(f"{field} must be a safe relative path inside the library package")
    path = root.joinpath(*relative.parts).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"{field} resolves outside the library package") from exc
    if not path.is_file():
        raise ValueError(f"{field} does not exist: {text}")
    return path


def _verify_license(record: dict[str, Any], root: Path, asset_id: str) -> None:
    if record.get("license_status") != "LICENSE_APPROVED":
        raise ValueError(f"{asset_id}: license_status must be LICENSE_APPROVED")
    license_record = record.get("license")
    if not isinstance(license_record, dict):
        raise ValueError(f"{asset_id}: license evidence object is required")
    _required_text(license_record.get("spdx_id"), f"{asset_id}.license.spdx_id")
    source_url = _required_text(license_record.get("source_url"), f"{asset_id}.license.source_url")
    if not source_url.startswith("https://"):
        raise ValueError(f"{asset_id}: license source_url must use HTTPS")
    _required_text(license_record.get("reviewed_by"), f"{asset_id}.license.reviewed_by")
    _required_text(license_record.get("reviewed_at_utc"), f"{asset_id}.license.reviewed_at_utc")
    evidence = _resolve_packaged_file(
        root, license_record.get("evidence_path"), f"{asset_id}.license.evidence_path"
    )
    if evidence.stat().st_size == 0:
        raise ValueError(f"{asset_id}: license evidence file is empty")


def _verify_musical_review(record: dict[str, Any], asset_id: str) -> None:
    review = record.get("musical_review")
    if not isinstance(review, dict) or review.get("status") != "APPROVED":
        raise ValueError(f"{asset_id}: explicit musical_review APPROVED is required")
    _required_text(review.get("reviewed_by"), f"{asset_id}.musical_review.reviewed_by")
    _required_text(review.get("reviewed_at_utc"), f"{asset_id}.musical_review.reviewed_at_utc")
    _required_text(review.get("boundary_basis"), f"{asset_id}.musical_review.boundary_basis")


def _build_mapping(record: dict[str, Any], root: Path) -> PatternClipMapping:
    asset_id = _required_text(record.get("asset_id"), "asset_id")
    if record.get("kind") != _ALLOWED_KIND:
        raise ValueError(f"{asset_id}: kind must be {_ALLOWED_KIND}")
    targets = record.get("engine_targets")
    if not isinstance(targets, list) or _ALLOWED_ENGINE not in targets:
        raise ValueError(f"{asset_id}: engine_targets must include {_ALLOWED_ENGINE}")

    _verify_license(record, root, asset_id)
    _verify_musical_review(record, asset_id)

    source_hash = _sha(record.get("source_sha256"), f"{asset_id}.source_sha256")
    source_path = _resolve_packaged_file(
        root, record.get("source_path"), f"{asset_id}.source_path"
    )
    actual_source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest().upper()
    if actual_source_hash != source_hash:
        raise ValueError(f"{asset_id}: source WAV SHA-256 mismatch")

    clip_hash = _sha(record.get("derived_sha256"), f"{asset_id}.derived_sha256")
    start = _required_int(record.get("source_start_sample"), f"{asset_id}.source_start_sample")
    end = _required_int(record.get("source_end_sample"), f"{asset_id}.source_end_sample", 1)
    if end <= start:
        raise ValueError(f"{asset_id}: source sample range must be non-empty")
    sample_rate = _required_int(record.get("sample_rate"), f"{asset_id}.sample_rate", 1)
    frame_count = _required_int(record.get("frame_count"), f"{asset_id}.frame_count", 1)
    if frame_count != end - start:
        raise ValueError(f"{asset_id}: frame_count must equal source_end_sample - source_start_sample")
    try:
        with wave.open(str(source_path), "rb") as source_wav:
            if source_wav.getcomptype() != "NONE":
                raise ValueError(f"{asset_id}: source must be uncompressed PCM WAV")
            if source_wav.getframerate() != sample_rate:
                raise ValueError(f"{asset_id}: source WAV sample rate does not match manifest")
            if end > source_wav.getnframes():
                raise ValueError(f"{asset_id}: source sample range exceeds source WAV frame count")
    except wave.Error as exc:
        raise ValueError(f"{asset_id}: invalid source PCM WAV: {exc}") from exc

    clip_path = _resolve_packaged_file(root, record.get("clip_path"), f"{asset_id}.clip_path")
    digest = hashlib.sha256(clip_path.read_bytes()).hexdigest().upper()
    if digest != clip_hash:
        raise ValueError(f"{asset_id}: derived clip SHA-256 mismatch")
    try:
        with wave.open(str(clip_path), "rb") as wav:
            if wav.getcomptype() != "NONE":
                raise ValueError(f"{asset_id}: clip must be uncompressed PCM WAV")
            if wav.getframerate() != sample_rate:
                raise ValueError(f"{asset_id}: WAV sample rate does not match manifest")
            if wav.getnframes() != frame_count:
                raise ValueError(f"{asset_id}: WAV frame count does not match manifest")
    except wave.Error as exc:
        raise ValueError(f"{asset_id}: invalid PCM WAV clip: {exc}") from exc

    mapping = record.get("mapping")
    if not isinstance(mapping, dict):
        raise ValueError(f"{asset_id}: mapping object is required")
    trigger = _required_int(mapping.get("trigger_midi_note"), f"{asset_id}.trigger_midi_note")
    source_note = _required_int(mapping.get("source_midi_note"), f"{asset_id}.source_midi_note")
    if trigger > 127 or source_note > 127:
        raise ValueError(f"{asset_id}: MIDI notes must be in range 0..127")
    articulation = _required_text(mapping.get("articulation_id"), f"{asset_id}.articulation_id")
    velocity_min = _required_int(mapping.get("velocity_min"), f"{asset_id}.velocity_min", 1)
    velocity_max = _required_int(mapping.get("velocity_max"), f"{asset_id}.velocity_max", 1)
    if velocity_max > 127 or velocity_min > velocity_max:
        raise ValueError(f"{asset_id}: invalid velocity range")
    rr = _required_text(mapping.get("round_robin_group", "RR-1"), f"{asset_id}.round_robin_group")

    return PatternClipMapping(
        asset_id=asset_id, clip_path=clip_path, clip_sha256=clip_hash,
        source_sha256=source_hash, source_start_sample=start, source_end_sample=end,
        sample_rate=sample_rate, trigger_midi_note=trigger, source_midi_note=source_note,
        articulation_id=articulation, velocity_min=velocity_min,
        velocity_max=velocity_max, round_robin_group=rr,
    )


def load_pattern_clip_registry(manifest_path: Path) -> PatternClipRegistry:
    """Validate the entire manifest and return immutable mappings or fail closed."""
    manifest_path = Path(manifest_path).resolve()
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    root = manifest_path.parent.resolve()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("Unsupported PATTERN clip registry schema_version")
    clips = payload.get("clips")
    if not isinstance(clips, list):
        raise ValueError("Registry clips must be an array")
    if not clips:
        return PatternClipRegistry((), False, "EMPTY_NO_APPROVED_CLIPS")

    mappings = tuple(_build_mapping(item, root) for item in clips
                     if isinstance(item, dict))
    if len(mappings) != len(clips):
        raise ValueError("Every registry clip entry must be an object")
    ids = [item.asset_id for item in mappings]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate asset_id in PATTERN clip registry")

    # Velocity layers may not overlap for the same trigger, articulation and
    # round-robin lane. Different round-robin lanes may intentionally coexist.
    lanes: dict[tuple[int, str, str], list[tuple[int, int, str]]] = {}
    for item in mappings:
        key = (item.trigger_midi_note, item.articulation_id, item.round_robin_group)
        zones = lanes.setdefault(key, [])
        for low, high, other_id in zones:
            if max(low, item.velocity_min) <= min(high, item.velocity_max):
                raise ValueError(
                    f"Overlapping velocity zones for {item.asset_id} and {other_id}"
                )
        zones.append((item.velocity_min, item.velocity_max, item.asset_id))

    return PatternClipRegistry(mappings, True, "READY_VALIDATED")
