#!/usr/bin/env python3
"""Safe, provenance-preserving WAV clip staging primitives.

This first extraction layer deliberately requires reviewed sample boundaries.
It never guesses musical boundaries and never edits source files.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import uuid
import wave
from pathlib import Path

ENGINES = {"PATTERN_MODE", "MELODY_INSTRUMENT", "PATTERN_INSTRUMENT"}
KINDS = {"whole_take", "musical_phrase", "rhythm_pattern", "chord_event", "note_event", "micro_event"}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()

def extract_reviewed_wav(source: Path, staging_root: Path, start_sample: int,
                          end_sample: int, *, kind: str, engines: list[str],
                          metadata: dict | None = None) -> dict:
    """Extract an explicitly reviewed PCM WAV range into staging with provenance."""
    source = source.resolve()
    staging_root = staging_root.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() not in {".wav", ".wave"}:
        raise ValueError("Only WAV sources are supported by this extraction stage")
    if kind not in KINDS:
        raise ValueError(f"Unsupported asset kind: {kind}")
    if not engines or not set(engines).issubset(ENGINES):
        raise ValueError("engines must contain supported engine IDs")
    source_hash = sha256_file(source)
    with wave.open(str(source), "rb") as reader:
        params = reader.getparams()
        if params.comptype != "NONE":
            raise ValueError("Compressed WAV is not supported")
        total = reader.getnframes()
        if start_sample < 0 or end_sample <= start_sample or end_sample > total:
            raise ValueError("Invalid sample boundaries")
        reader.setpos(start_sample)
        frames = reader.readframes(end_sample - start_sample)
        if len(frames) != (end_sample - start_sample) * params.nchannels * params.sampwidth:
            raise ValueError("Source WAV returned an incomplete frame range")
    asset_id = uuid.uuid4().hex
    output_dir = staging_root / "clips"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{asset_id}.wav"
    with wave.open(str(output), "wb") as writer:
        writer.setparams(params)
        writer.writeframes(frames)
    derived_hash = sha256_file(output)
    extra = metadata or {}
    record = {
        "schema_version": 1,
        "asset_id": asset_id,
        "parent_asset_id": extra.get("parent_asset_id"),
        "source_path": str(source),
        "source_sha256": source_hash,
        "source_start_sample": start_sample,
        "source_end_sample": end_sample,
        "source_start_seconds": round(start_sample / params.framerate, 9),
        "source_end_seconds": round(end_sample / params.framerate, 9),
        "sample_rate": params.framerate,
        "channels": params.nchannels,
        "sample_width_bytes": params.sampwidth,
        "frame_count": end_sample - start_sample,
        "duration_seconds": round((end_sample - start_sample) / params.framerate, 9),
        "kind": kind,
        "engine_targets": sorted(set(engines)),
        "derived_path": str(output),
        "derived_sha256": derived_hash,
        "extractor": "reviewed_wav_range",
        "extractor_version": "0.1.0",
        "review_status": "BOUNDARIES_USER_OR_REVIEWER_APPROVED",
        "license_status": extra.get("license_status", "UNREVIEWED"),
        "musical_metadata": extra.get("musical_metadata", {}),
        "confidence": extra.get("confidence"),
    }
    manifest = output.with_suffix(".json")
    manifest.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record

def main() -> int:
    ap = argparse.ArgumentParser(description="Extract a reviewed WAV range into LibraryManager staging.")
    ap.add_argument("source", type=Path)
    ap.add_argument("--staging", type=Path, default=Path(__file__).resolve().parent / "staging")
    ap.add_argument("--start-sample", type=int, required=True)
    ap.add_argument("--end-sample", type=int, required=True)
    ap.add_argument("--kind", choices=sorted(KINDS), required=True)
    ap.add_argument("--engine", action="append", choices=sorted(ENGINES), required=True)
    ap.add_argument("--license-status", default="UNREVIEWED")
    args = ap.parse_args()
    record = extract_reviewed_wav(args.source, args.staging, args.start_sample,
                                  args.end_sample, kind=args.kind, engines=args.engine,
                                  metadata={"license_status": args.license_status})
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
