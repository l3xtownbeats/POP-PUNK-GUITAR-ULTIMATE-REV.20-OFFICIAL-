"""Conservative phrase segmentation for long guitar-loop recordings.

Uses onset evidence already computed by the bounded acoustic pass. It proposes
review ranges only; it does not claim note/chord transcription or loop quality.
"""
from __future__ import annotations

import hashlib
import statistics
from typing import Any

SEGMENTER_VERSION = "0.1.0"


def segment_guitar_loop_phrases(
    source_path: str,
    source_sha256: str,
    sample_rate: int,
    total_frames: int,
    onset_times: list[float],
    *,
    excluded_ranges: list[tuple[int, int]] | None = None,
    min_attacks: int = 3,
    max_gap_seconds: float = 0.72,
    max_phrase_seconds: float = 8.0,
    pre_roll_seconds: float = 0.035,
    tail_seconds: float = 0.22,
) -> dict[str, Any]:
    """Return review-only phrase ranges with exact source-frame offsets."""
    if sample_rate <= 0 or total_frames <= 0:
        raise ValueError("Valid source sample rate and frame count are required")
    if min_attacks < 3 or max_gap_seconds <= 0 or max_phrase_seconds <= 0:
        raise ValueError("Invalid phrase segmentation limits")
    times = sorted({float(t) for t in onset_times if 0 <= float(t) < total_frames / sample_rate})
    groups: list[list[float]] = []
    current: list[float] = []
    for onset in times:
        if current and (onset - current[-1] > max_gap_seconds or
                        onset - current[0] > max_phrase_seconds):
            if len(current) >= min_attacks:
                groups.append(current)
            current = []
        current.append(onset)
    if len(current) >= min_attacks:
        groups.append(current)

    excluded = excluded_ranges or []
    candidates = []
    for group in groups:
        intervals = [b - a for a, b in zip(group, group[1:])]
        if not intervals:
            continue
        mean_interval = statistics.fmean(intervals)
        cv = (statistics.pstdev(intervals) / mean_interval) if mean_interval > 0 else 1.0
        start = max(0, int(round((group[0] - pre_roll_seconds) * sample_rate)))
        end = min(total_frames, int(round((group[-1] + tail_seconds) * sample_rate)))
        if end <= start or any(start < old_end and end > old_start for old_start, old_end in excluded):
            continue
        duration = (end - start) / sample_rate
        if duration < 0.25 or duration > max_phrase_seconds + tail_seconds:
            continue
        kind = ("IRREGULAR_GUITAR_LOOP_PHRASE" if cv >= 0.22
                else "NON_REPEATING_STEADY_RHYTHM_PHRASE")
        token = f"{source_sha256}:{start}:{end}:{SEGMENTER_VERSION}:{kind}"
        candidates.append({
            "candidate_id": hashlib.sha256(token.encode("utf-8")).hexdigest().upper()[:24],
            "candidate_type": kind,
            "source_start_sample": start,
            "source_end_sample": end,
            "start_seconds": round(start / sample_rate, 6),
            "end_seconds": round(end / sample_rate, 6),
            "duration_seconds": round(duration, 6),
            "onset_count_candidate": len(group),
            "inter_onset_cv_candidate": round(cv, 4),
            "timing_classification": "IRREGULAR_CANDIDATE" if cv >= 0.22 else "STEADY_NON_REPEATING_CANDIDATE",
            "review_status": "NEEDS_MUSICAL_REVIEW",
            "license_status": "UNREVIEWED",
            "musical_identity": "NOT_ESTABLISHED",
            "proposed_group": "PATTERN_MODE_CANDIDATES",
            "boundary_basis": "ONSET_EVIDENCE_WITH_FIXED_PREROLL_AND_TAIL",
        })
    return {
        "algorithm": "IRREGULAR_GUITAR_LOOP_SEGMENTATION",
        "algorithm_version": SEGMENTER_VERSION,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "source_audio_modified": False,
        "automatic_factory_promotion": False,
        "limitations": [
            "Onsets are acoustic candidates, not verified notes or strums.",
            "Phrase boundaries are conservative estimates and require listening review.",
            "No tempo, chord, bar, meter, articulation or instrument identity is inferred.",
            "Overlapping ranges already selected as repeated patterns are excluded.",
        ],
    }
