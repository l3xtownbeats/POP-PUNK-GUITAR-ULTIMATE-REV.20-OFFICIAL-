#!/usr/bin/env python3
"""Evidence-based rhythm and pulse analysis for audio-analysis reports.

This module proposes rhythmic descriptors from onset timestamps. It does not
claim verified meter, groove, bar boundaries, loop seams, or musical identity.
No audio files are changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any


VERSION = "0.1.0"


def _median(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def _quantize(value: float, quantum: float) -> int:
    return int(round(value / quantum))


def analyze_rhythm(report: dict[str, Any], *, tolerance: float = 0.12) -> dict[str, Any]:
    """Return tempo/grid and repeating-interval candidates from onset evidence."""
    if not 0.01 <= tolerance <= 0.5:
        raise ValueError("tolerance must be between 0.01 and 0.5")
    duration = float(report.get("duration_seconds", 0.0))
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("report requires positive finite duration_seconds")

    raw = report.get("onset_evidence_seconds", [])
    if not isinstance(raw, list):
        raise ValueError("onset_evidence_seconds must be a list")
    events = sorted({float(t) for t in raw
                     if isinstance(t, (int, float)) and math.isfinite(float(t))
                     and 0 <= float(t) <= duration})
    intervals = [b - a for a, b in zip(events, events[1:]) if b > a]
    median_interval = _median(intervals)
    mean_interval = statistics.fmean(intervals) if intervals else 0.0
    cv = (statistics.pstdev(intervals) / mean_interval
          if len(intervals) > 1 and mean_interval else None)

    # Evaluate plausible beat periods using common subdivisions/multipliers
    # of observed inter-onset intervals. These are hypotheses, not a meter.
    candidates: dict[int, float] = {}
    for interval in intervals:
        for factor in (1, 2, 3, 4):
            bpm = round(60.0 / (interval * factor))
            if 50 <= bpm <= 220:
                candidates[bpm] = candidates.get(bpm, 0.0) + 1.0 / factor
    ranked = []
    for bpm, support in candidates.items():
        beat = 60.0 / bpm
        phases = [abs((t / beat) - round(t / beat)) for t in events]
        fit = sum(1 for p in phases if p <= tolerance) / len(phases) if phases else 0.0
        ranked.append((support * (0.5 + fit), bpm, fit))
    ranked.sort(reverse=True)
    tempo_candidates = [
        {"bpm": bpm, "grid_fit": round(fit, 4), "support": round(score, 4)}
        for score, bpm, fit in ranked[:5]
    ]

    # Quantized interval contour is a searchable rhythm descriptor, not a
    # duplicate key. Keep timing scale separately so half/double-time variants
    # remain distinguishable and no deletion decision can use this value.
    rhythm_descriptor = None
    if intervals:
        base = _median(intervals)
        quantum = max(0.015, base * 0.125)
        contour = [_quantize(value, quantum) for value in intervals]
        payload = ",".join(map(str, contour)).encode("ascii")
        rhythm_descriptor = {
            "interval_units": contour,
            "unit_seconds": round(quantum, 6),
            "descriptor_sha256": hashlib.sha256(payload).hexdigest(),
            "purpose": "SEARCH_AND_GROUPING_ONLY_NOT_DUPLICATE_ID"
        }

    regularity = None
    if len(intervals) >= 2 and mean_interval:
        regularity = max(0.0, min(1.0, 1.0 - (statistics.pstdev(intervals) / mean_interval)))
    repeated_pulse_candidate = bool(len(events) >= 5 and regularity is not None
                                    and regularity >= 0.65)
    return {
        "rhythm_analysis_version": VERSION,
        "source": report.get("source"),
        "source_sha256": report.get("source_sha256"),
        "duration_seconds": duration,
        "onset_count": len(events),
        "onset_evidence_seconds": [round(t, 6) for t in events],
        "inter_onset_interval_seconds": [round(v, 6) for v in intervals],
        "median_inter_onset_interval_seconds": round(median_interval, 6) if intervals else None,
        "interval_coefficient_of_variation": round(cv, 4) if cv is not None else None,
        "rhythmic_regularity_candidate": round(regularity, 4) if regularity is not None else None,
        "tempo_candidates": tempo_candidates,
        "rhythm_descriptor": rhythm_descriptor,
        "repeating_pulse_candidate": repeated_pulse_candidate,
        "review_status": "NEEDS_MUSICAL_REVIEW",
        "license_status": "UNREVIEWED",
        "automatic_destructive_action": "NONE",
        "limitations": [
            "Onset timestamps are acoustic evidence and may include false or missed attacks.",
            "Tempo candidates may be half-time, double-time or subdivision interpretations.",
            "Meter, downbeat, bar boundaries, groove and loop seam are not confirmed.",
            "The rhythm descriptor is for search/grouping only, never duplicate deletion or merging.",
            "A repeated rhythm does not imply the same melody, riff, performance or recording."
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze rhythm evidence from an audio-analysis JSON report.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--tolerance", type=float, default=0.12)
    args = parser.parse_args()
    result = analyze_rhythm(json.loads(args.report.read_text(encoding="utf-8")),
                            tolerance=args.tolerance)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
