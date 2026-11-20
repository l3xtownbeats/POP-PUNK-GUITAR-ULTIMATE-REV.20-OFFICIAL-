#!/usr/bin/env python3
"""Frame-based monophonic pitch-event candidates for guitar WAV review.

Uses a bounded YIN-style difference function. Results are pitch hypotheses,
not polyphonic transcription, chord recognition, or verified note boundaries.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from typing import Any

from audio_analysis import read_mono_pcm

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def _yin_pitch(frame: list[float], sample_rate: float,
               min_hz: float, max_hz: float) -> tuple[int, float, float] | None:
    if len(frame) < 96:
        return None
    mean = sum(frame) / len(frame)
    x = [v - mean for v in frame]
    energy = sum(v * v for v in x) / len(x)
    if energy < 1e-7:
        return None
    min_lag = max(2, int(sample_rate / max_hz))
    max_lag = min(len(x) // 2, int(sample_rate / min_hz))
    if max_lag <= min_lag:
        return None

    diff = [0.0] * (max_lag + 1)
    for lag in range(1, max_lag + 1):
        diff[lag] = sum((x[i] - x[i + lag]) ** 2
                        for i in range(len(x) - lag))
    running = 0.0
    cmnd = [1.0] * (max_lag + 1)
    for lag in range(1, max_lag + 1):
        running += diff[lag]
        cmnd[lag] = diff[lag] * lag / running if running > 0 else 1.0

    # Prefer the first convincing period to reduce octave errors.
    threshold = 0.18
    chosen = None
    for lag in range(min_lag, max_lag):
        if cmnd[lag] < threshold:
            while lag + 1 <= max_lag and cmnd[lag + 1] < cmnd[lag]:
                lag += 1
            chosen = lag
            break
    if chosen is None:
        chosen = min(range(min_lag, max_lag + 1), key=lambda n: cmnd[n])
    confidence = max(0.0, min(1.0, 1.0 - cmnd[chosen]))
    if confidence < 0.65:
        return None
    # Parabolic interpolation around the selected lag.
    if 1 < chosen < max_lag:
        left, center, right = cmnd[chosen - 1:chosen + 2]
        denom = left - 2 * center + right
        if abs(denom) > 1e-12:
            chosen += 0.5 * (left - right) / denom
    hz = sample_rate / chosen
    midi = round(69 + 12 * math.log2(hz / 440.0))
    return midi, hz, confidence


def analyze_pitch_events(path: Path, *, frame_ms: int = 30,
                         hop_ms: int = 10, min_hz: float = 65.0,
                         max_hz: float = 1200.0,
                         min_event_seconds: float = 0.07) -> dict[str, Any]:
    if frame_ms < 20 or hop_ms < 5 or hop_ms > frame_ms:
        raise ValueError("Use frame_ms >= 20 and 5 <= hop_ms <= frame_ms")
    if min_hz <= 0 or max_hz <= min_hz or min_event_seconds <= 0:
        raise ValueError("Invalid pitch or event limits")

    samples, rate, total_frames, channels, width, decimation = read_mono_pcm(path, max_samples=100_000)
    if not samples or rate <= 0:
        raise ValueError("Empty or invalid WAV")
    effective_rate = rate / decimation
    # Keep the analysis rate bounded while retaining enough bandwidth for guitar.
    extra = max(1, math.ceil(effective_rate / 4000.0))
    samples = samples[::extra]
    effective_rate /= extra
    frame_size = max(96, round(effective_rate * frame_ms / 1000))
    hop_size = max(1, round(effective_rate * hop_ms / 1000))
    frames: list[dict[str, Any]] = []
    for start in range(0, len(samples) - frame_size + 1, hop_size):
        result = _yin_pitch(samples[start:start + frame_size], effective_rate,
                            min_hz, max_hz)
        timestamp = start / effective_rate
        if result is None:
            frames.append({"time_seconds": round(timestamp, 4), "midi_note": None,
                           "confidence": 0.0})
        else:
            midi, hz, confidence = result
            frames.append({"time_seconds": round(timestamp, 4),
                           "midi_note": midi, "frequency_hz": round(hz, 2),
                           "note_name": NOTE_NAMES[midi % 12] + str(midi // 12 - 1),
                           "confidence": round(confidence, 3)})

    # Group adjacent frames only when the estimated pitch is stable.
    groups: list[list[dict[str, Any]]] = []
    for item in frames:
        midi = item["midi_note"]
        if midi is None:
            if groups and groups[-1] and groups[-1][-1]["midi_note"] is not None:
                groups.append([])
            continue
        if not groups or not groups[-1] or groups[-1][-1]["midi_note"] != midi:
            groups.append([item])
        else:
            groups[-1].append(item)

    events = []
    for group in groups:
        if not group:
            continue
        start = group[0]["time_seconds"]
        end = min(total_frames / rate, group[-1]["time_seconds"] + frame_ms / 1000)
        duration = max(0.0, end - start)
        if duration < min_event_seconds:
            continue
        midi = group[0]["midi_note"]
        events.append({
            "event_id": f"PITCH-{len(events) + 1:04d}",
            "start_seconds": start, "end_seconds": round(end, 4),
            "duration_seconds": round(duration, 4),
            "midi_note_candidate": midi,
            "note_name_candidate": NOTE_NAMES[midi % 12] + str(midi // 12 - 1),
            "mean_confidence": round(sum(x["confidence"] for x in group) / len(group), 3),
            "frame_count": len(group),
            "review_status": "NEEDS_MUSICAL_REVIEW",
            "license_status": "UNREVIEWED"
        })

    return {
        "pitch_tracker_version": "0.1.0",
        "source": str(path.resolve()),
        "duration_seconds": round(total_frames / rate, 6),
        "sample_rate": rate, "channels": channels, "sample_width_bytes": width,
        "analysis_rate_hz": round(effective_rate, 2),
        "frame_count": len(frames), "pitch_event_candidate_count": len(events),
        "pitch_events": events,
        "frames": frames,
        "limitations": [
            "This is a monophonic pitch hypothesis tracker, not polyphonic transcription.",
            "Chords, distorted tones, harmonics, detuning and overlapping notes can cause octave or pitch errors.",
            "Event boundaries are frame estimates and require listening/review before extraction.",
            "No palm-mute, picking, string, chord-quality or musical-role identity is inferred.",
            "No source audio is modified; derived clips remain a separate reviewed staging operation."
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate monophonic pitch-event review candidates.")
    parser.add_argument("wav", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-hz", type=float, default=65.0)
    parser.add_argument("--max-hz", type=float, default=1200.0)
    args = parser.parse_args()
    result = analyze_pitch_events(args.wav, min_hz=args.min_hz, max_hz=args.max_hz)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
