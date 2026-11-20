#!/usr/bin/env python3
"""Conservative audio-region candidate builder.

Groups acoustic onset evidence into previewable time regions. These are NOT
claimed to be musical phrases, loops, notes, chords, bars, or articulation IDs.
Every candidate is marked for human musical review before extraction/approval.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any


def build_candidates(report: dict[str, Any], *, max_gap_seconds: float = 1.25,
                     pre_roll_seconds: float = 0.04, tail_seconds: float = 0.30,
                     min_duration_seconds: float = 0.20,
                     max_duration_seconds: float = 16.0) -> dict[str, Any]:
    duration = float(report.get("duration_seconds", 0.0))
    if duration <= 0:
        raise ValueError("Analysis report must contain a positive duration_seconds")
    if max_gap_seconds <= 0 or min_duration_seconds <= 0 or max_duration_seconds < min_duration_seconds:
        raise ValueError("Invalid candidate timing limits")
    events = sorted({max(0.0, min(duration, float(t)))
                     for t in report.get("onset_evidence_seconds", [])
                     if isinstance(t, (int, float))})
    groups: list[list[float]] = []
    for event in events:
        if not groups or event - groups[-1][-1] > max_gap_seconds:
            groups.append([event])
        else:
            groups[-1].append(event)
    candidates = []
    for group in groups:
        start = max(0.0, group[0] - pre_roll_seconds)
        end = min(duration, group[-1] + tail_seconds)
        if end - start < min_duration_seconds:
            end = min(duration, start + min_duration_seconds)
        if end - start < min_duration_seconds:
            continue
        # Split long evidence groups into bounded preview regions; split points
        # are mechanical limits, not inferred musical boundaries.
        cursor = start
        while end - cursor > max_duration_seconds:
            part_end = cursor + max_duration_seconds
            candidates.append(_candidate(len(candidates) + 1, cursor, part_end, group))
            cursor = part_end
        if end - cursor >= min_duration_seconds:
            candidates.append(_candidate(len(candidates) + 1, cursor, end, group))
    return {
        "candidate_builder_version": "0.1.0",
        "source": report.get("source"),
        "duration_seconds": duration,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "limitations": [
            "Regions are grouped from acoustic onset evidence only; they are not verified musical phrases, loops, notes, chords or bars.",
            "Quiet, sustained or legato passages may have no onset evidence and therefore may not produce a candidate.",
            "Long groups are split only to bound preview length; split points are not musical boundaries.",
            "Review candidate audio and source licensing before extraction or FACTORY promotion."
        ]
    }


def _candidate(index: int, start: float, end: float, evidence: list[float]) -> dict[str, Any]:
    return {
        "candidate_id": f"REGION-{index:04d}",
        "start_seconds": round(start, 6),
        "end_seconds": round(end, 6),
        "duration_seconds": round(end - start, 6),
        "kind": "audio_region_candidate",
        "boundary_basis": "grouped_onset_evidence_with_fixed_preroll_tail",
        "review_status": "NEEDS_MUSICAL_REVIEW",
        "license_status": "UNREVIEWED",
        "confidence": None,
        "onset_evidence_seconds": [round(t, 4) for t in evidence if start <= t <= end]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build conservative preview-region candidates from an audio analysis JSON report.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-gap", type=float, default=1.25)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    result = build_candidates(report, max_gap_seconds=args.max_gap)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
