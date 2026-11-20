"""Conservative segmentation of useful phrases in irregular guitar-loop recordings.

This detector is deliberately separate from repeated-motif detection. It uses
coarse onset evidence and long gaps to propose review ranges; it does not claim
note/chord transcription, bar boundaries, or a verified musical phrase.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

VERSION = "0.1.0"


def analyze_irregular_guitar_phrases(
    source: Path, acoustic_report: dict[str, Any], *,
    guitar_source_confirmed: bool = False, source_sha256: str = "",
    min_attacks: int = 3, min_duration: float = 0.25,
    max_duration: float = 12.0, gap_floor: float = 0.65,
    max_candidates: int = 300,
) -> dict[str, Any]:
    """Return non-repeating phrase candidates with exact source frame offsets."""
    if not guitar_source_confirmed:
        raise ValueError("Confirm guitar-only source before irregular phrase analysis")
    if min_attacks < 2 or min_duration <= 0 or max_duration <= min_duration or gap_floor <= 0:
        raise ValueError("Invalid irregular phrase segmentation settings")
    source = Path(source).resolve()
    rate = int(acoustic_report.get("sample_rate") or 0)
    total_frames = int(round(float(acoustic_report.get("duration_seconds") or 0) * rate))
    if rate <= 0 or total_frames <= 0:
        raise ValueError("Acoustic report lacks valid source duration/sample rate")
    raw = acoustic_report.get("onset_evidence_seconds") or []
    onsets = sorted({float(value) for value in raw
                     if isinstance(value, (int, float)) and 0 <= float(value) < total_frames / rate})
    groups: list[list[float]] = []
    current: list[float] = []
    for onset in onsets:
        if current and onset - current[-1] > gap_floor:
            if len(current) >= min_attacks:
                groups.append(current)
            current = []
        current.append(onset)
    if len(current) >= min_attacks:
        groups.append(current)

    candidates = []
    for group in groups:
        start_s = max(0.0, group[0] - 0.035)
        end_s = min(total_frames / rate, group[-1] + 0.18)
        duration = end_s - start_s
        if duration < min_duration or duration > max_duration:
            continue
        start = max(0, int(round(start_s * rate)))
        end = min(total_frames, int(round(end_s * rate)))
        if end <= start:
            continue
        ident = hashlib.sha256(
            f"{source_sha256}:{start}:{end}:{VERSION}:IRREGULAR".encode("utf-8")
        ).hexdigest().upper()[:24]
        candidates.append({
            "candidate_id": ident,
            "candidate_type": "IRREGULAR_GUITAR_LOOP_PHRASE",
            "segmentation_algorithm": "IRREGULAR_GUITAR_LOOP_SEGMENTATION",
            "source_start_sample": start, "source_end_sample": end,
            "start_seconds": round(start / rate, 6),
            "end_seconds": round(end / rate, 6),
            "duration_seconds": round((end - start) / rate, 6),
            "onset_count_candidate": len(group),
            "onset_times_seconds_candidate": [round(x, 6) for x in group],
            "tempo_candidate_bpm": None,
            "review_status": "NEEDS_MUSICAL_REVIEW",
            "license_status": "UNREVIEWED",
            "proposed_group": "IRREGULAR_GUITAR_PHRASE_CANDIDATES",
            "automatic_factory_promotion": False,
        })
        if len(candidates) >= max_candidates:
            break
    return {
        "schema_version": 1,
        "engine": "IRREGULAR_GUITAR_LOOP_SEGMENTATION",
        "engine_version": VERSION,
        "source_path": str(source),
        "source_sha256": source_sha256.upper(),
        "sample_rate": rate, "total_frames": total_frames,
        "candidate_count": len(candidates), "candidates": candidates,
        "automatic_factory_promotion": False,
        "audio_copied": False, "audio_modified": False,
        "limitations": [
            "Onset groups are phrase-boundary candidates, not verified notes, chords, riffs, bars or loop seams.",
            "Irregular timing is preserved; no quantization, tempo normalization or BPM is imposed.",
            "Review/listening is mandatory; silence, noise, clipped notes and musical usefulness require human confirmation.",
            "Original audio remains untouched and all ranges refer to exact source sample offsets."
        ],
    }
