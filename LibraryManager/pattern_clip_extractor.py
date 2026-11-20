#!/usr/bin/env python3
"""Physically extract repeated-rhythm occurrences to review-only WAV clips.

Input is a pattern_pipeline report. Every occurrence is sliced at its original
sample offsets, with configurable pre/post padding. Results remain unapproved
in LibraryManager/staging and retain full source provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from audio_segmenter import STAGING_BASE, sha256_file, _safe_staging_root
from audio_range_io import audio_source_info, write_pcm_wav_range

VERSION = "0.2.0"


def extract_pattern_occurrences(
    report: dict[str, Any],
    staging_root: Path = STAGING_BASE,
    *,
    pre_roll_ms: int = 35,
    post_roll_ms: int = 250,
    min_duration_ms: int = 100,
    max_clips: int = 500,
    cancel_event: Any = None,
) -> list[dict[str, Any]]:
    if pre_roll_ms < 0 or post_roll_ms < 0 or min_duration_ms < 1:
        raise ValueError("Invalid padding or minimum duration")
    if max_clips < 1 or max_clips > 10000:
        raise ValueError("max_clips must be between 1 and 10000")
    root = _safe_staging_root(staging_root)
    source = Path(report.get("source") or "").resolve()
    expected_hash = str(report.get("source_sha256") or "").upper()
    if not source.is_file() or not expected_hash:
        raise ValueError("Pattern report must identify an existing source and SHA-256")
    if sha256_file(source) != expected_hash:
        raise RuntimeError("Source SHA-256 changed since pattern analysis")
    patterns = (report.get("pattern_analysis") or {}).get("patterns")
    if not isinstance(patterns, list):
        raise ValueError("Report does not contain pattern_analysis.patterns")

    source_info = audio_source_info(source)
    rate, total_frames = source_info.framerate, source_info.frames
    pad_before = round(rate * pre_roll_ms / 1000)
    pad_after = round(rate * post_roll_ms / 1000)
    min_frames = round(rate * min_duration_ms / 1000)

    clips_dir = root / "clips"
    manifests_dir = root / "manifests"
    for directory in (clips_dir, manifests_dir):
        directory.mkdir(parents=True, exist_ok=True)
        try:
            directory.resolve().relative_to(root)
            directory.resolve().relative_to(STAGING_BASE)
        except ValueError as exc:
            raise ValueError("Staging subdirectory escaped staging root") from exc

    results: list[dict[str, Any]] = []
    created_paths: list[Path] = []
    created_identities: set[str] = set()
    try:
        for pattern in patterns:
            pattern_id = str(pattern.get("pattern_candidate_id") or "UNKNOWN")
            occurrences = pattern.get("occurrences") or []
            for occurrence_index, occurrence in enumerate(occurrences, 1):
                if cancel_event is not None and cancel_event.is_set():
                    raise RuntimeError("Pattern extraction cancelled; this batch is rolled back safely")
                if len(results) >= max_clips:
                    break
                start_sec = float(occurrence["start_seconds"])
                end_sec = float(occurrence["end_seconds"])
                if end_sec <= start_sec or start_sec < 0:
                    continue
                raw_start, raw_end = round(start_sec * rate), round(end_sec * rate)
                raw_end = min(raw_end, total_frames)
                start = max(0, raw_start - pad_before)
                end = min(total_frames, raw_end + pad_after)
                if end <= start or end - start < min_frames:
                    continue
                identity = hashlib.sha256(
                    f"{expected_hash}:{pattern_id}:{start}:{end}:{VERSION}".encode("utf-8")
                ).hexdigest()[:24].upper()
                clip_path = clips_dir / f"PATTERN-{identity}.wav"
                manifest_path = manifests_dir / f"PATTERN-{identity}.json"
                if clip_path.exists() or manifest_path.exists():
                    if identity in created_identities:
                        raise FileExistsError(f"Duplicate pattern occurrence in this extraction batch: {identity}")
                    if not (clip_path.is_file() and manifest_path.is_file()):
                        raise FileExistsError(f"Incomplete existing staged pattern clip {identity}")
                    existing = json.loads(manifest_path.read_text(encoding="utf-8"))
                    matches = (
                        existing.get("source_sha256") == expected_hash
                        and int(existing.get("source_start_sample", -1)) == start
                        and int(existing.get("source_end_sample", -1)) == end
                        and Path(str(existing.get("derived_path", ""))).resolve() == clip_path.resolve()
                        and str(existing.get("derived_sha256", "")).upper() == sha256_file(clip_path)
                    )
                    if not matches:
                        raise RuntimeError(f"Existing staged pattern clip failed provenance/hash validation: {identity}")
                    existing["reused_existing"] = True
                    results.append(existing)
                    continue
                created_paths.extend([clip_path, manifest_path])
                clip_info = write_pcm_wav_range(
                    source, start, end, clip_path, expected_rate=rate,
                )
                if cancel_event is not None and cancel_event.is_set():
                    raise RuntimeError("Pattern extraction cancelled; this batch is rolled back safely")
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
                    "source_sample_width_bytes": source_info.sampwidth,
                    "source_format": source_info.source_format,
                    "source_subtype": source_info.source_subtype,
                    "derived_format": clip_info["derived_format"],
                    "derived_subtype": clip_info["derived_subtype"],
                    "frame_count": end - start,
                    "duration_seconds": round((end - start) / rate, 6),
                    "kind": "rhythm_pattern",
                    "engine_targets": ["PATTERN_INSTRUMENT"],
                    "derived_path": str(clip_path),
                    "derived_sha256": sha256_file(clip_path),
                    "extractor": "pattern_clip_extractor",
                    "extractor_version": VERSION,
                    "musical_metadata": {
                        "pattern_candidate_id": pattern_id,
                        "pattern_signature_units": pattern.get("pattern_signature_units", []),
                        "pattern_role_candidate": pattern.get("pattern_role_candidate", "RHYTHM_PATTERN"),
                        "occurrence_index": occurrence_index,
                        "detected_start_seconds": start_sec,
                        "detected_end_seconds": end_sec,
                        "pre_roll_ms": round((raw_start - start) * 1000 / rate, 2),
                        "post_roll_ms": round((end - raw_end) * 1000 / rate, 2),
                        "musical_section_candidate": pattern.get("musical_section_candidate", "UNKNOWN"),
                        "articulation_candidates": pattern.get("articulation_candidates", ["UNKNOWN"]),
                    },
                    "confidence": None,
                    "review_status": "NEEDS_MUSICAL_REVIEW",
                    "license_status": "UNREVIEWED",
                }
                with manifest_path.open("x", encoding="utf-8") as stream:
                    json.dump(record, stream, ensure_ascii=False, indent=2)
                    stream.write("\n")
                record["reused_existing"] = False
                created_identities.add(identity)
                results.append(record)
            if len(results) >= max_clips:
                break
        if sha256_file(source) != expected_hash:
            raise RuntimeError("Source changed during pattern extraction")
        return results
    except Exception:
        for created in reversed(created_paths):
            created.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract repeated rhythm occurrences to staging WAV clips.")
    parser.add_argument("pattern_report", type=Path)
    parser.add_argument("--staging", type=Path, default=STAGING_BASE)
    parser.add_argument("--pre-roll-ms", type=int, default=35)
    parser.add_argument("--post-roll-ms", type=int, default=250)
    parser.add_argument("--max-clips", type=int, default=500)
    args = parser.parse_args()
    report = json.loads(args.pattern_report.read_text(encoding="utf-8"))
    records = extract_pattern_occurrences(
        report, args.staging, pre_roll_ms=args.pre_roll_ms,
        post_roll_ms=args.post_roll_ms, max_clips=args.max_clips,
    )
    print(json.dumps({"extracted_count": len(records), "assets": records},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
