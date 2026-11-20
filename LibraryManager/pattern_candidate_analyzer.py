#!/usr/bin/env python3
"""Conservative repeated-rhythm pattern candidate analysis.

Consumes onset timestamps from the existing rhythm-analysis report. It proposes
repeated timing motifs and source ranges for PATTERN MODE preparation; it does
not infer chords, notes, downbeats, meter, section names, or articulations.
All results remain review-pending and refer to the original source timeline.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

VERSION = "0.1.0"


def _valid_onsets(report: dict[str, Any]) -> tuple[list[float], float]:
    duration = report.get("duration_seconds")
    if not isinstance(duration, (int, float)) or not math.isfinite(float(duration)) or duration <= 0:
        raise ValueError("report requires a positive finite duration_seconds")
    raw = report.get("onset_evidence_seconds")
    if not isinstance(raw, list):
        raise ValueError("report requires onset_evidence_seconds list")
    onsets = sorted({
        float(value) for value in raw
        if isinstance(value, (int, float)) and math.isfinite(float(value))
        and 0 <= float(value) <= float(duration)
    })
    return onsets, float(duration)


def _duration_beat_candidates(duration_seconds: float, tempo_candidates: list[Any]) -> list[dict[str, Any]]:
    """Estimate integer beat counts from upstream tempo hypotheses, never meter."""
    results = []
    for item in tempo_candidates[:5]:
        if not isinstance(item, dict):
            continue
        bpm = item.get("bpm")
        if not isinstance(bpm, (int, float)) or not math.isfinite(float(bpm)) or bpm <= 0:
            continue
        exact_beats = duration_seconds * float(bpm) / 60.0
        beat_count = round(exact_beats)
        deviation = abs(exact_beats - beat_count)
        if beat_count >= 1 and deviation <= 0.15:
            results.append({
                "bpm": round(float(bpm), 3),
                "estimated_beat_count": int(beat_count),
                "beat_count_deviation": round(deviation, 4),
                "evidence": "DURATION_NEAR_INTEGER_BEATS_ONLY",
            })
    return results


def find_repeating_patterns(
    report: dict[str, Any], *, min_intervals: int = 3,
    max_intervals: int = 16, quantization_steps: int = 8,
    min_occurrences: int = 2, max_candidates: int = 200,
) -> dict[str, Any]:
    """Find repeated onset-interval motifs; ranges are candidate source offsets.

    Interval values are normalized to the file's median inter-onset interval,
    then quantized. This supports modest timing variation while deliberately
    avoiding claims that a motif is a complete bar or musical section.
    """
    if min_intervals < 2 or max_intervals < min_intervals or max_intervals > 64:
        raise ValueError("Require 2 <= min_intervals <= max_intervals <= 64")
    if quantization_steps < 2 or quantization_steps > 32:
        raise ValueError("quantization_steps must be between 2 and 32")
    if min_occurrences < 2 or max_candidates < 1:
        raise ValueError("min_occurrences must be >= 2 and max_candidates >= 1")

    onsets, duration = _valid_onsets(report)
    intervals = [b - a for a, b in zip(onsets, onsets[1:]) if b > a]
    if len(intervals) < min_intervals:
        return {
            "pattern_analysis_version": VERSION,
            "source": report.get("source"),
            "duration_seconds": duration,
            "candidate_count": 0,
            "patterns": [],
            "review_status": "NEEDS_MUSICAL_REVIEW",
            "license_status": "UNREVIEWED",
            "automatic_destructive_action": "NONE",
            "limitations": ["Not enough onset intervals to search for repeated motifs."]
        }

    base = statistics.median(intervals)
    # Quantized relative timing signature; it is a search key, not a fingerprint
    # of the audio or proof that two performances are musically identical.
    units = [max(1, min(128, round((value / base) * quantization_steps)))
             for value in intervals]

    grouped: dict[tuple[int, ...], list[tuple[int, int]]] = defaultdict(list)
    upper = min(max_intervals, len(units))
    for length in range(min_intervals, upper + 1):
        for start in range(0, len(units) - length + 1):
            signature = tuple(units[start:start + length])
            grouped[signature].append((start, start + length))

    # Sliding windows overlap heavily. Treating every matching window as an
    # occurrence would inflate counts and report one long passage as many
    # repetitions. Keep only temporally non-overlapping instances per signature.
    repeated = []
    for signature, occurrences in grouped.items():
        accepted = []
        last_end = -1
        for start, end in sorted(occurrences):
            if start >= last_end:
                accepted.append((start, end))
                last_end = end
        if len(accepted) >= min_occurrences:
            repeated.append((signature, accepted))
    # Prefer longer motifs and collapse candidates whose every occurrence is
    # already covered by a longer repeated motif with the same occurrence starts.
    repeated.sort(key=lambda item: (-len(item[0]), -len(item[1]), item[0]))
    selected: list[tuple[tuple[int, ...], list[tuple[int, int]]]] = []
    for signature, occurrences in repeated:
        starts = {start for start, _ in occurrences}
        covered = False
        for longer_sig, longer_occurrences in selected:
            if len(longer_sig) <= len(signature):
                continue
            longer_by_start = {start: end for start, end in longer_occurrences}
            if starts.issubset(longer_by_start) and all(
                longer_by_start[start] >= end for start, end in occurrences
            ):
                covered = True
                break
        if not covered:
            selected.append((signature, occurrences))
        if len(selected) >= max_candidates:
            break

    patterns = []
    for signature, occurrences in selected:
        occurrence_records = []
        tempo_candidates = report.get("tempo_candidates", [])
        if not isinstance(tempo_candidates, list):
            tempo_candidates = []
        for first_interval, after_last_interval in occurrences:
            start_seconds = onsets[first_interval]
            end_seconds = onsets[after_last_interval]
            duration_seconds = end_seconds - start_seconds
            occurrence_records.append({
                "start_seconds": round(start_seconds, 6),
                "end_seconds": round(end_seconds, 6),
                "duration_seconds": round(duration_seconds, 6),
                "start_onset_index": first_interval,
                "end_onset_index_exclusive": after_last_interval + 1,
                "duration_beat_count_candidates": _duration_beat_candidates(
                    duration_seconds, tempo_candidates
                ),
            })
        signature_text = ",".join(map(str, signature))
        identity = hashlib.sha256(signature_text.encode("ascii")).hexdigest().upper()[:24]
        patterns.append({
            "pattern_candidate_id": identity,
            "candidate_type": "REPEATED_RHYTHM_MOTIF",
            "pattern_signature_units": list(signature),
            "signature_quantization_steps": quantization_steps,
            "signature_base_interval_seconds": round(base, 6),
            "interval_count": len(signature),
            "occurrence_count": len(occurrence_records),
            "occurrences": occurrence_records,
            "pattern_role_candidate": "RHYTHM_PATTERN",
            "musical_section_candidate": "UNKNOWN",
            "articulation_candidates": ["UNKNOWN"],
            "harmonic_content": "NOT_ANALYZED",
            "review_status": "NEEDS_MUSICAL_REVIEW",
            "license_status": "UNREVIEWED",
        })

    patterns.sort(key=lambda item: (
        -item["interval_count"], -item["occurrence_count"],
        item["occurrences"][0]["start_seconds"]
    ))
    return {
        "pattern_analysis_version": VERSION,
        "engine_target": "PATTERN_MODE",
        "source": report.get("source"),
        "source_sha256": report.get("source_sha256"),
        "duration_seconds": duration,
        "onset_count": len(onsets),
        "tempo_candidates": report.get("tempo_candidates", []),
        "rhythmic_regularity_candidate": report.get("rhythmic_regularity_candidate"),
        "candidate_count": len(patterns),
        "patterns": patterns,
        "review_status": "NEEDS_MUSICAL_REVIEW",
        "license_status": "UNREVIEWED",
        "automatic_destructive_action": "NONE",
        "limitations": [
            "Repeated onset timing is only a rhythmic motif candidate, not verified musical pattern identity.",
            "No meter, downbeat, bar boundary, tempo lock, chord, note, key, or articulation is inferred.",
            "Intro, Verse, Chorus, Bridge and Ending labels require separate musical review and are not guessed.",
            "The signature is a timing search key, not an audio fingerprint or duplicate-deletion key.",
            "All time ranges refer to the original recording; no audio is sliced, copied, moved, or modified.",
            "MIDI chord adaptation and tempo-synchronous playback belong to the later VST pattern engine."
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Find repeated rhythmic motif candidates for PATTERN MODE.")
    parser.add_argument("rhythm_report", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-intervals", type=int, default=3)
    parser.add_argument("--max-intervals", type=int, default=16)
    args = parser.parse_args()
    result = find_repeating_patterns(
        json.loads(args.rhythm_report.read_text(encoding="utf-8")),
        min_intervals=args.min_intervals, max_intervals=args.max_intervals,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
