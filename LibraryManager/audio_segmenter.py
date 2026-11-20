#!/usr/bin/env python3
"""Conservative note-event WAV segmenter.

Dry-run is the default. Extraction is opt-in and restricted to
LibraryManager/staging. Candidate boundaries are estimates, never approvals.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import uuid
import wave
from pathlib import Path
from typing import Any

from pitch_events import analyze_pitch_events

from app_paths import runtime_staging_root

STAGING_BASE = runtime_staging_root(__file__)
SEGMENTER_VERSION = "0.1.0"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _safe_staging_root(root: Path) -> Path:
    resolved = Path(root).resolve()
    try:
        resolved.relative_to(STAGING_BASE)
    except ValueError as exc:
        raise ValueError("Output must be inside LibraryManager/staging") from exc
    if resolved == STAGING_BASE:
        return resolved
    return resolved


def propose_segments(source: Path, *, pre_roll_ms: int = 35,
                     post_roll_ms: int = 220, min_duration_ms: int = 70,
                     max_segments: int = 500) -> dict[str, Any]:
    source = Path(source).resolve()
    if pre_roll_ms < 0 or post_roll_ms < 0 or min_duration_ms < 1:
        raise ValueError("Invalid segment padding or minimum duration")
    if max_segments < 1 or max_segments > 10000:
        raise ValueError("max_segments must be between 1 and 10000")
    analysis = analyze_pitch_events(source)
    rate = analysis["sample_rate"]
    total_frames = round(analysis["duration_seconds"] * rate)
    pad_before = round(rate * pre_roll_ms / 1000)
    pad_after = round(rate * post_roll_ms / 1000)
    min_frames = round(rate * min_duration_ms / 1000)
    proposals = []
    for event in analysis["pitch_events"][:max_segments]:
        raw_start = round(event["start_seconds"] * rate)
        raw_end = round(event["end_seconds"] * rate)
        start = max(0, raw_start - pad_before)
        end = min(total_frames, raw_end + pad_after)
        if end - start < min_frames:
            continue
        proposals.append({
            "segment_id": f"NOTE-{len(proposals)+1:04d}",
            "segment_type_candidate": "NOTE_EVENT",
            "source_start_sample": start,
            "source_end_sample": end,
            "source_start_seconds": round(start / rate, 6),
            "source_end_seconds": round(end / rate, 6),
            "duration_seconds": round((end - start) / rate, 6),
            "detected_note_start_seconds": event["start_seconds"],
            "detected_note_end_seconds": event["end_seconds"],
            "midi_note_candidate": event["midi_note_candidate"],
            "note_name_candidate": event["note_name_candidate"],
            "confidence": event["mean_confidence"],
            "pre_roll_ms": round((raw_start - start) * 1000 / rate, 2),
            "post_roll_ms": round((end - raw_end) * 1000 / rate, 2),
            "review_status": "NEEDS_MUSICAL_REVIEW",
            "license_status": "UNREVIEWED"
        })
    return {
        "schema_version": 1,
        "segmenter_version": SEGMENTER_VERSION,
        "source_path": str(source),
        "source_sha256": sha256_file(source),
        "sample_rate": rate,
        "channels": analysis["channels"],
        "sample_width_bytes": analysis["sample_width_bytes"],
        "candidate_count": len(proposals),
        "extraction_performed": False,
        "segments": proposals,
        "limitations": [
            "Monophonic pitch-event candidates only; this is not chord or polyphonic guitar segmentation.",
            "Frame-derived boundaries and note labels require listening and human approval.",
            "Pre-roll and post-roll preserve likely pick attack and decay, but reverb tails may extend beyond the configured post-roll.",
            "No rhythmic phrase, bar, loop, articulation or chord identity is inferred.",
            "Source audio is read-only; candidates remain review-pending and license-unreviewed."
        ]
    }


def extract_segments(report: dict[str, Any], staging_root: Path) -> list[dict[str, Any]]:
    """Write proposed PCM ranges to staging; never overwrite and verify source."""
    root = _safe_staging_root(staging_root)
    source = Path(report["source_path"]).resolve()
    if sha256_file(source) != report["source_sha256"]:
        raise RuntimeError("Source hash changed since analysis; refusing extraction")
    clips_dir = root / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir = root / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    # A pre-existing symlink inside staging must not redirect writes outside it.
    for directory in (clips_dir, manifest_dir):
        resolved_directory = directory.resolve()
        try:
            resolved_directory.relative_to(root)
            resolved_directory.relative_to(STAGING_BASE)
        except ValueError as exc:
            raise ValueError("Staging subdirectories must not resolve outside staging") from exc
    results = []
    with wave.open(str(source), "rb") as reader:
        params = reader.getparams()
        if params.comptype != "NONE":
            raise ValueError("Compressed WAV is not supported")
        total = reader.getnframes()
        for item in report["segments"]:
            start, end = item["source_start_sample"], item["source_end_sample"]
            if start < 0 or end <= start or end > total:
                raise ValueError("Segment range is outside source WAV")
            identity = hashlib.sha256(
                f'{report["source_sha256"]}:{start}:{end}:{SEGMENTER_VERSION}'.encode()
            ).hexdigest()[:24]
            clip = clips_dir / f"{identity}.wav"
            manifest = manifest_dir / f"{identity}.json"
            if clip.exists() or manifest.exists():
                raise FileExistsError(f"Refusing to overwrite existing staged asset: {identity}")
            reader.setpos(start)
            frames = reader.readframes(end - start)
            expected = (end - start) * params.nchannels * params.sampwidth
            if len(frames) != expected:
                raise IOError("Incomplete PCM frame range read from source")
            # Exclusive creation protects against collisions/races.
            with clip.open("xb") as raw_clip:
                with wave.open(raw_clip, "wb") as writer:
                    writer.setparams(params)
                    writer.writeframes(frames)
            record = {
                "schema_version": 1,
                "asset_id": identity,
                "parent_asset_id": report["source_sha256"],
                "source_path": str(source),
                "source_sha256": report["source_sha256"],
                "source_start_sample": start,
                "source_end_sample": end,
                "source_start_seconds": item["source_start_seconds"],
                "source_end_seconds": item["source_end_seconds"],
                "sample_rate": params.framerate,
                "channels": params.nchannels,
                "sample_width_bytes": params.sampwidth,
                "frame_count": end - start,
                "duration_seconds": item["duration_seconds"],
                "kind": "note_event",
                "engine_targets": ["MELODY_INSTRUMENT", "PATTERN_MODE"],
                "derived_path": str(clip),
                "derived_sha256": sha256_file(clip),
                "extractor": "audio_segmenter",
                "extractor_version": SEGMENTER_VERSION,
                "musical_metadata": {
                    "midi_note_candidate": item["midi_note_candidate"],
                    "note_name_candidate": item["note_name_candidate"],
                    "detected_note_start_seconds": item["detected_note_start_seconds"],
                    "detected_note_end_seconds": item["detected_note_end_seconds"],
                    "pre_roll_ms": item["pre_roll_ms"],
                    "post_roll_ms": item["post_roll_ms"]
                },
                "confidence": item["confidence"],
                "review_status": "NEEDS_MUSICAL_REVIEW",
                "license_status": "UNREVIEWED"
            }
            # Create sidecar exclusively; remove this clip if metadata creation fails.
            try:
                with manifest.open("x", encoding="utf-8") as stream:
                    json.dump(record, stream, ensure_ascii=False, indent=2)
            except Exception:
                clip.unlink(missing_ok=True)
                raise
            results.append(record)
    if sha256_file(source) != report["source_sha256"]:
        raise RuntimeError("Source hash changed during extraction")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Propose guitar note segments; extraction requires --extract.")
    parser.add_argument("wav", type=Path)
    parser.add_argument("--staging", type=Path, default=STAGING_BASE)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pre-roll-ms", type=int, default=35)
    parser.add_argument("--post-roll-ms", type=int, default=220)
    parser.add_argument("--extract", action="store_true", help="Write candidates to LibraryManager/staging.")
    args = parser.parse_args()
    report = propose_segments(args.wav, pre_roll_ms=args.pre_roll_ms,
                              post_roll_ms=args.post_roll_ms)
    if args.extract:
        records = extract_segments(report, args.staging)
        report["extraction_performed"] = True
        report["extracted_count"] = len(records)
        report["extracted_assets"] = records
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
