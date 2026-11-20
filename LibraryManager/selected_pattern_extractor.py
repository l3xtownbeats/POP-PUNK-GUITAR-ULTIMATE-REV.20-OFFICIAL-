#!/usr/bin/env python3
"""Selective, user-approved Pattern fragment extraction with full provenance.

The tool is intentionally opt-in. It does not split every loop or automatically
promote a musical hypothesis to a finished Pattern. A human selects the range
and records why the parent recording needs selective extraction.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from audio_segmenter import STAGING_BASE, _safe_staging_root, sha256_file
from audio_range_io import audio_source_info, write_pcm_wav_range

VERSION = "0.1.0"
SELECTION_REASONS = {
    "LONG_RECORDING",
    "IRREGULAR_STRUCTURE",
    "POSSIBLE_MID_PHRASE_START",
    "MULTIPLE_SECTIONS_OR_STYLES",
}


def extract_selected_pattern_fragment(
    source: Path,
    staging_root: Path = STAGING_BASE,
    *,
    start_seconds: float,
    end_seconds: float,
    selection_reasons: list[str],
    pre_roll_ms: int = 35,
    post_roll_ms: int = 350,
    reviewer_note: str = "",
) -> dict[str, Any]:
    """Copy one explicitly selected source range to a new review-only Pattern WAV."""
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if not isinstance(start_seconds, (int, float)) or not isinstance(end_seconds, (int, float)):
        raise ValueError("Selection start/end must be numeric seconds")
    if start_seconds < 0 or end_seconds <= start_seconds:
        raise ValueError("Selection boundaries must satisfy 0 <= start < end")
    if pre_roll_ms < 0 or post_roll_ms < 0:
        raise ValueError("Pre-roll and post-roll must not be negative")

    reasons = list(selection_reasons or [])
    if not reasons or len(reasons) != len(set(reasons)) or any(
        reason not in SELECTION_REASONS for reason in reasons
    ):
        raise ValueError(
            "At least one selection reason is required: long recording, irregular structure, "
            "possible mid-phrase start or multiple sections/styles"
        )
    root = _safe_staging_root(staging_root)
    info = audio_source_info(source)
    start_frame = round(float(start_seconds) * info.framerate)
    end_frame = round(float(end_seconds) * info.framerate)
    if start_frame < 0 or end_frame <= start_frame or end_frame > info.frames:
        raise ValueError(
            f"Selected range exceeds source duration ({info.frames / info.framerate:.3f} seconds)"
        )
    if end_frame - start_frame < max(1, round(info.framerate * 0.1)):
        raise ValueError("A Pattern fragment must be at least 100 ms long")

    pre_roll_frames = round(info.framerate * pre_roll_ms / 1000)
    post_roll_frames = round(info.framerate * post_roll_ms / 1000)
    extract_start = max(0, start_frame - pre_roll_frames)
    extract_end = min(info.frames, end_frame + post_roll_frames)

    # Hashing is deliberately limited to this explicitly selected operation.
    # Scan-only inventory never calculates it; extraction stores full provenance.
    source_hash = sha256_file(source)
    identity = hashlib.sha256(
        f"{source_hash}:{extract_start}:{extract_end}:PATTERN-SELECTED:{VERSION}".encode("utf-8")
    ).hexdigest()[:24].upper()

    clips_dir = root / "clips"
    manifests_dir = root / "manifests"
    for directory in (clips_dir, manifests_dir):
        directory.mkdir(parents=True, exist_ok=True)
        try:
            directory.resolve().relative_to(root)
            directory.resolve().relative_to(STAGING_BASE)
        except ValueError as exc:
            raise ValueError("Staging output directory resolves outside LibraryManager/staging") from exc

    clip_path = clips_dir / f"PATTERN-SELECTED-{identity}.wav"
    manifest_path = manifests_dir / f"PATTERN-SELECTED-{identity}.json"
    if clip_path.exists() or manifest_path.exists():
        if not (clip_path.is_file() and manifest_path.is_file()):
            raise FileExistsError("An incomplete asset with this selected-fragment ID already exists")
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        valid = (
            existing.get("source_sha256") == source_hash
            and existing.get("source_start_sample") == extract_start
            and existing.get("source_end_sample") == extract_end
            and str(existing.get("derived_sha256", "")).upper() == sha256_file(clip_path)
            and Path(str(existing.get("derived_path", ""))).resolve() == clip_path.resolve()
        )
        if not valid:
            raise RuntimeError("Existing selected Pattern fragment failed provenance/integrity verification")
        return {**existing, "reused_existing": True}

    created_clip = False
    try:
        clip_info = write_pcm_wav_range(
            source, extract_start, extract_end, clip_path, expected_rate=info.framerate,
        )
        created_clip = True
        derived_hash = sha256_file(clip_path)
        if sha256_file(source) != source_hash:
            raise RuntimeError("Source file changed during selected-fragment extraction")

        record: dict[str, Any] = {
            "schema_version": 1,
            "asset_id": identity,
            "parent_asset_id": source_hash,
            "source_path": str(source),
            "source_sha256": source_hash,
            "source_start_sample": extract_start,
            "source_end_sample": extract_end,
            "source_start_seconds": round(extract_start / info.framerate, 9),
            "source_end_seconds": round(extract_end / info.framerate, 9),
            "user_selection_start_sample": start_frame,
            "user_selection_end_sample": end_frame,
            "user_selection_start_seconds": round(start_frame / info.framerate, 9),
            "user_selection_end_seconds": round(end_frame / info.framerate, 9),
            "pre_roll_frames": start_frame - extract_start,
            "post_roll_frames": extract_end - end_frame,
            "pre_roll_ms": round((start_frame - extract_start) * 1000 / info.framerate, 3),
            "post_roll_ms": round((extract_end - end_frame) * 1000 / info.framerate, 3),
            "sample_rate": info.framerate,
            "channels": clip_info["channels"],
            "sample_width_bytes": clip_info["sample_width_bytes"],
            "source_sample_width_bytes": info.sampwidth,
            "source_format": info.source_format,
            "source_subtype": info.source_subtype,
            "derived_format": clip_info["derived_format"],
            "derived_subtype": clip_info["derived_subtype"],
            "frame_count": extract_end - extract_start,
            "duration_seconds": round((extract_end - extract_start) / info.framerate, 9),
            "kind": "rhythm_pattern",
            "engine_targets": ["PATTERN_MODE", "PATTERN_INSTRUMENT"],
            "derived_path": str(clip_path),
            "derived_sha256": derived_hash,
            "extractor": "selected_pattern_fragment_extractor",
            "extractor_version": VERSION,
            "musical_metadata": {
                "selection_source": "EXPLICIT_USER_RANGE",
                "selection_reasons": reasons,
                "reviewer_note": reviewer_note.strip(),
                "possible_mid_phrase_start": "POSSIBLE_MID_PHRASE_START" in reasons,
                "loop_review_required": True,
                "cycle_integrity_verified": False,
                "pattern_structure_status": "NEEDS_MUSICAL_REVIEW",
                "tempo_bpm": None,
                "time_signature": None,
                "beat_grid": [],
                "attack_events": [],
                "technique_events": [],
                "harmonic_events": [],
            },
            "confidence": None,
            "review_status": "NEEDS_MUSICAL_REVIEW",
            "license_status": "UNREVIEWED",
            "integrity_status": "VERIFIED",
            "automatic_factory_promotion": False,
        }
        with manifest_path.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        return {**record, "reused_existing": False}
    except Exception:
        if created_clip:
            clip_path.unlink(missing_ok=True)
        manifest_path.unlink(missing_ok=True)
        raise


__all__ = ["SELECTION_REASONS", "extract_selected_pattern_fragment"]
