#!/usr/bin/env python3
"""Extract review-only chord and power-chord sample zones for SAMPLE MODE.

Chord labels are hypotheses from the experimental spectral analyzer. This
module preserves exact source offsets and never claims a verified fingering,
voicing, string/fret position or automatic chord adaptation.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from audio_segmenter import STAGING_BASE, _safe_staging_root, sha256_file
from audio_range_io import audio_source_info, write_pcm_wav_range

VERSION = "0.1.0"


def extract_chord_samples(
    report: dict[str, Any],
    staging_root: Path = STAGING_BASE,
    *,
    pre_roll_ms: int = 35,
    post_roll_ms: int = 220,
    max_clips: int = 300,
) -> list[dict[str, Any]]:
    if pre_roll_ms < 0 or post_roll_ms < 0 or not 1 <= max_clips <= 5000:
        raise ValueError("Invalid chord extraction limits")
    root = _safe_staging_root(staging_root)
    source = Path(str(report.get("source_path") or "")).expanduser().resolve()
    expected_hash = str(report.get("source_sha256") or "").upper()
    candidates = report.get("chord_candidates")
    if not source.is_file() or len(expected_hash) != 64:
        raise ValueError("Chord report must identify an existing source and SHA-256")
    if not isinstance(candidates, list):
        raise ValueError("Chord report does not contain chord_candidates")
    if sha256_file(source) != expected_hash:
        raise RuntimeError("Source SHA-256 changed since chord analysis")

    info = audio_source_info(source)
    rate, total_frames = info.framerate, info.frames
    before = round(rate * pre_roll_ms / 1000)
    after = round(rate * post_roll_ms / 1000)
    clips_dir, manifests_dir = root / "clips", root / "manifests"
    for folder in (clips_dir, manifests_dir):
        folder.mkdir(parents=True, exist_ok=True)
        folder.resolve().relative_to(root)
        folder.resolve().relative_to(STAGING_BASE)

    results: list[dict[str, Any]] = []
    created: list[Path] = []
    seen_ranges: set[tuple[int, int]] = set()
    try:
        for candidate in candidates:
            if len(results) >= max_clips:
                break
            start_seconds = candidate.get("start_seconds")
            end_seconds = candidate.get("end_seconds")
            if not isinstance(start_seconds, (int, float)) or not isinstance(end_seconds, (int, float)):
                continue
            if start_seconds < 0 or end_seconds <= start_seconds:
                continue
            raw_start = round(float(start_seconds) * rate)
            raw_end = round(float(end_seconds) * rate)
            start = max(0, raw_start - before)
            end = min(total_frames, raw_end + after)
            if end <= start or (start, end) in seen_ranges:
                continue
            seen_ranges.add((start, end))
            quality = str(candidate.get("quality") or "UNKNOWN").upper()
            kind = "power_chord_sample_candidate" if quality == "POWER5" else "chord_sample_candidate"
            prefix = "POWER5" if quality == "POWER5" else "CHORD"
            identity = hashlib.sha256(
                f"{expected_hash}:{kind}:{start}:{end}:{VERSION}".encode("utf-8")
            ).hexdigest().upper()[:24]
            clip = clips_dir / f"{prefix}-{identity}.wav"
            manifest = manifests_dir / f"{prefix}-{identity}.json"
            if clip.exists() or manifest.exists():
                if not (clip.is_file() and manifest.is_file()):
                    raise FileExistsError(f"Incomplete existing staged chord asset: {identity}")
                existing = json.loads(manifest.read_text(encoding="utf-8"))
                if (
                    existing.get("source_sha256") != expected_hash
                    or existing.get("source_start_sample") != start
                    or existing.get("source_end_sample") != end
                    or existing.get("derived_sha256") != sha256_file(clip)
                ):
                    raise RuntimeError(f"Existing staged chord asset failed integrity validation: {identity}")
                existing["reused_existing"] = True
                results.append(existing)
                continue

            clip_info = write_pcm_wav_range(source, start, end, clip, expected_rate=rate)
            created.append(clip)
            record = {
                "schema_version": 1,
                "asset_id": identity,
                "parent_asset_id": expected_hash,
                "source_path": str(source),
                "source_sha256": expected_hash,
                "source_start_sample": start,
                "source_end_sample": end,
                "source_start_seconds": round(start / rate, 6),
                "source_end_seconds": round(end / rate, 6),
                "sample_rate": rate,
                "channels": clip_info["channels"],
                "sample_width_bytes": clip_info["sample_width_bytes"],
                "frame_count": end - start,
                "duration_seconds": round((end - start) / rate, 6),
                "derived_format": clip_info["derived_format"],
                "derived_subtype": clip_info["derived_subtype"],
                "derived_path": str(clip),
                "derived_sha256": sha256_file(clip),
                "kind": kind,
                "engine_targets": ["SAMPLE_MODE", "CHORD_MODE", "AUTO_CHORDS"],
                "extractor": "chord_clip_extractor",
                "extractor_version": VERSION,
                "musical_metadata": {
                    "chord_name_candidate": candidate.get("chord_name_candidate"),
                    "root_pitch_class_candidate": candidate.get("root_pitch_class"),
                    "quality_candidate": quality,
                    "pitch_classes_candidate": candidate.get("pitch_classes_candidate", []),
                    "confidence_candidate": candidate.get("mean_confidence", candidate.get("confidence")),
                    "voicing_candidate": "UNKNOWN",
                    "string_fret_positions": None,
                    "tuning_candidate": "UNKNOWN",
                    "pre_roll_ms": round((raw_start - start) * 1000 / rate, 2),
                    "post_roll_ms": round((end - raw_end) * 1000 / rate, 2),
                },
                "review_status": "NEEDS_MUSICAL_REVIEW",
                "license_status": "UNREVIEWED",
                "automatic_factory_promotion": False,
                "source_modified": False,
            }
            with manifest.open("x", encoding="utf-8") as stream:
                created.append(manifest)
                json.dump(record, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            record["reused_existing"] = False
            results.append(record)

        if sha256_file(source) != expected_hash:
            raise RuntimeError("Source SHA-256 changed during chord extraction")
        return results
    except Exception:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        raise
