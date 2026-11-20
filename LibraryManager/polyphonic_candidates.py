#!/usr/bin/env python3
"""Experimental polyphonic spectral pitch candidates for WAV review.

This module estimates simultaneous pitch candidates from harmonic spectral
energy. It is not a chord recognizer or a production guitar transcription
system. Every result remains a human-review candidate.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from audio_analysis import read_mono_pcm

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def _goertzel_magnitude(frame: list[float], sample_rate: float,
                        frequency: float) -> float:
    """Return a Hann-windowed Goertzel magnitude at one frequency."""
    if frequency <= 0 or frequency >= sample_rate / 2:
        return 0.0
    n = len(frame)
    omega = 2.0 * math.pi * frequency / sample_rate
    coefficient = 2.0 * math.cos(omega)
    s1 = s2 = 0.0
    mean = sum(frame) / n
    for index, value in enumerate(frame):
        window = 0.5 - 0.5 * math.cos(2.0 * math.pi * index / max(1, n - 1))
        sample = (value - mean) * window
        current = sample + coefficient * s1 - s2
        s2, s1 = s1, current
    power = max(0.0, s1 * s1 + s2 * s2 - coefficient * s1 * s2)
    return math.sqrt(power) * 2.0 / max(1, n)


def _frame_pitch_candidates(frame: list[float], rate: float,
                            min_midi: int, max_midi: int,
                            max_candidates: int, relative_threshold: float
                            ) -> list[dict[str, Any]]:
    if not frame:
        return []
    rms = math.sqrt(sum(value * value for value in frame) / len(frame))
    if rms < 1e-5:
        return []
    scored = []
    for midi in range(min_midi, max_midi + 1):
        fundamental = 440.0 * (2.0 ** ((midi - 69) / 12.0))
        # Harmonic support helps weak fundamentals, but the fundamental has
        # the greatest weight to reduce octave/harmonic-only false positives.
        score = 0.0
        for harmonic, weight in ((1, 1.0), (2, 0.45), (3, 0.25)):
            hz = fundamental * harmonic
            if hz < rate * 0.48:
                score += weight * _goertzel_magnitude(frame, rate, hz)
        scored.append((score, midi, fundamental))
    scored.sort(reverse=True)
    if not scored or scored[0][0] <= 1e-8:
        return []
    peak = scored[0][0]
    selected = []
    used_pitch_classes = set()
    for score, midi, hz in scored:
        if score < peak * relative_threshold:
            continue
        # Keep distinct semitone candidates; nearby MIDI notes can be
        # spectral leakage from the same source note.
        if any(abs(midi - item["midi_note_candidate"]) <= 1 for item in selected):
            continue
        selected.append({
            "midi_note_candidate": midi,
            "note_name_candidate": NOTE_NAMES[midi % 12] + str(midi // 12 - 1),
            "frequency_hz": round(hz, 2),
            "salience": round(score / peak, 4),
            "confidence": round(min(1.0, score / peak), 3),
        })
        if len(selected) >= max_candidates:
            break
    return selected


def analyze_polyphonic_candidates(
    path: Path, *, frame_ms: int = 100, hop_ms: int = 50,
    min_midi: int = 36, max_midi: int = 84,
    max_candidates: int = 6, relative_threshold: float = 0.28,
    min_event_seconds: float = 0.10,
) -> dict[str, Any]:
    """Create simultaneous pitch-event candidates; never asserts chord names."""
    if frame_ms < 40 or hop_ms < 10 or hop_ms > frame_ms:
        raise ValueError("Use frame_ms >= 40 and 10 <= hop_ms <= frame_ms")
    if min_midi < 0 or max_midi > 127 or max_midi <= min_midi:
        raise ValueError("MIDI range must satisfy 0 <= min_midi < max_midi <= 127")
    if not 1 <= max_candidates <= 12:
        raise ValueError("max_candidates must be between 1 and 12")
    if not 0.05 <= relative_threshold <= 1.0 or min_event_seconds <= 0:
        raise ValueError("Invalid threshold or minimum event duration")

    samples, rate, total_frames, channels, width, decimation = read_mono_pcm(path)
    if not samples or rate <= 0:
        raise ValueError("Empty or invalid WAV")
    effective_rate = rate / decimation
    # Bound the expensive pure-Python spectral scoring workload.
    extra = max(1, math.ceil(effective_rate / 11025.0))
    samples = samples[::extra]
    effective_rate /= extra
    frame_size = max(256, round(effective_rate * frame_ms / 1000.0))
    hop_size = max(1, round(effective_rate * hop_ms / 1000.0))

    frames = []
    for start in range(0, len(samples) - frame_size + 1, hop_size):
        candidates = _frame_pitch_candidates(
            samples[start:start + frame_size], effective_rate,
            min_midi, max_midi, max_candidates, relative_threshold)
        frames.append({
            "time_seconds": round(start / effective_rate, 4),
            "pitch_candidates": candidates,
        })

    # Track each MIDI candidate independently across adjacent frames.
    active: dict[int, list[dict[str, Any]]] = {}
    completed: list[dict[str, Any]] = []
    for frame in frames:
        present = {item["midi_note_candidate"]: item
                   for item in frame["pitch_candidates"]}
        for midi in list(active):
            if midi not in present:
                group = active.pop(midi)
                start = group[0]["time_seconds"]
                end = min(total_frames / rate,
                          group[-1]["time_seconds"] + frame_ms / 1000.0)
                if end - start >= min_event_seconds:
                    completed.append(_make_event(midi, group, start, end))
        for midi, item in present.items():
            active.setdefault(midi, []).append({
                **item, "time_seconds": frame["time_seconds"]})
    for midi, group in active.items():
        start = group[0]["time_seconds"]
        end = min(total_frames / rate,
                  group[-1]["time_seconds"] + frame_ms / 1000.0)
        if end - start >= min_event_seconds:
            completed.append(_make_event(midi, group, start, end))
    completed.sort(key=lambda event: (event["start_seconds"],
                                      event["midi_note_candidate"]))
    for index, event in enumerate(completed, 1):
        event["event_id"] = f"MULTIPITCH-{index:04d}"

    return {
        "analysis_version": "0.1.0-experimental",
        "source": str(path.resolve()),
        "duration_seconds": round(total_frames / rate, 6),
        "sample_rate": rate, "channels": channels,
        "sample_width_bytes": width,
        "analysis_rate_hz": round(effective_rate, 2),
        "frame_count": len(frames),
        "pitch_event_candidate_count": len(completed),
        "pitch_events": completed,
        "frames": frames,
        "review_status": "NEEDS_MUSICAL_REVIEW",
        "license_status": "UNREVIEWED",
        "limitations": [
            "Spectral salience candidates are not verified notes or chord labels.",
            "Harmonics, distortion, tuning, phase cancellation and overlapping guitar parts can create or hide candidates.",
            "The frame tracker may split sustained notes or miss short attacks.",
            "No chord quality, inversion, string, fret, articulation, velocity layer or instrument role is inferred.",
            "All candidates require listening and human review; source audio is never modified."
        ],
    }


def _make_event(midi: int, group: list[dict[str, Any]],
                start: float, end: float) -> dict[str, Any]:
    return {
        "event_id": "",
        "start_seconds": round(start, 4),
        "end_seconds": round(end, 4),
        "duration_seconds": round(max(0.0, end - start), 4),
        "midi_note_candidate": midi,
        "note_name_candidate": NOTE_NAMES[midi % 12] + str(midi // 12 - 1),
        "mean_confidence": round(sum(x["confidence"] for x in group) / len(group), 3),
        "mean_salience": round(sum(x["salience"] for x in group) / len(group), 4),
        "frame_count": len(group),
        "review_status": "NEEDS_MUSICAL_REVIEW",
        "license_status": "UNREVIEWED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate experimental polyphonic pitch candidates for WAV review.")
    parser.add_argument("wav", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-midi", type=int, default=36)
    parser.add_argument("--max-midi", type=int, default=84)
    parser.add_argument("--max-candidates", type=int, default=6)
    args = parser.parse_args()
    result = analyze_polyphonic_candidates(
        args.wav, min_midi=args.min_midi, max_midi=args.max_midi,
        max_candidates=args.max_candidates)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
