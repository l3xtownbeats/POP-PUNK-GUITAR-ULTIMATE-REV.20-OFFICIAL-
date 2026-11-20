#!/usr/bin/env python3
"""Experimental polyphonic chord candidates from guitar WAV files.

This is a review-only spectral-harmonic analyzer. It does not transcribe
voicings, identify strings/frets, extract clips, or approve library assets.
Input should already have passed the guitar-source filtering stage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from audio_analysis import read_mono_pcm

VERSION = "0.1.0"
NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
QUALITIES = {
    "MAJOR": (0, 4, 7),
    "MINOR": (0, 3, 7),
    "DIMINISHED": (0, 3, 6),
    "SUS2": (0, 2, 7),
    "SUS4": (0, 5, 7),
    "POWER5": (0, 7),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _fft(values: list[complex]) -> None:
    """In-place radix-2 Cooley-Tukey FFT."""
    n = len(values)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            values[i], values[j] = values[j], values[i]
    size = 2
    while size <= n:
        angle = -2.0 * math.pi / size
        root = complex(math.cos(angle), math.sin(angle))
        half = size // 2
        for start in range(0, n, size):
            factor = 1.0 + 0.0j
            for offset in range(half):
                even = values[start + offset]
                odd = factor * values[start + offset + half]
                values[start + offset] = even + odd
                values[start + offset + half] = even - odd
                factor *= root
        size <<= 1


def _frame_chroma(frame: list[float], rate: float) -> list[float]:
    size = len(frame)
    values = []
    mean = sum(frame) / size
    for index, sample in enumerate(frame):
        window = 0.5 - 0.5 * math.cos(2.0 * math.pi * index / (size - 1))
        values.append(complex((sample - mean) * window, 0.0))
    _fft(values)
    chroma = [0.0] * 12
    # Accumulate local spectral maxima into pitch classes. A mild harmonic
    # discount limits (but cannot eliminate) octave/harmonic confusion.
    magnitudes = [abs(value) for value in values[:size // 2]]
    for bin_index in range(2, len(magnitudes) - 1):
        magnitude = magnitudes[bin_index]
        if magnitude < magnitudes[bin_index - 1] or magnitude < magnitudes[bin_index + 1]:
            continue
        frequency = bin_index * rate / size
        if not 65.0 <= frequency <= 1400.0:
            continue
        midi = round(69.0 + 12.0 * math.log2(frequency / 440.0))
        target = 440.0 * (2.0 ** ((midi - 69) / 12.0))
        cents = abs(1200.0 * math.log2(frequency / target))
        if cents > 45.0:
            continue
        chroma[midi % 12] += magnitude / math.sqrt(max(1, midi // 12 - 1))
    peak = max(chroma, default=0.0)
    if peak > 0:
        chroma = [value / peak for value in chroma]
    return chroma


def _cosine(observed: list[float], template: list[float]) -> float:
    dot = sum(a * b for a, b in zip(observed, template))
    norm_a = math.sqrt(sum(a * a for a in observed))
    norm_b = math.sqrt(sum(b * b for b in template))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def _best_chord(chroma: list[float], *, min_confidence: float,
                min_margin: float) -> dict[str, Any] | None:
    active = [index for index, value in enumerate(chroma) if value >= 0.20]
    if len(active) < 2:
        return None
    ranked = []
    for root in range(12):
        for quality, intervals in QUALITIES.items():
            if quality != "POWER5" and len(active) < 3:
                continue
            template = [0.0] * 12
            for interval in intervals:
                template[(root + interval) % 12] = 1.0
            score = _cosine(chroma, template)
            ranked.append((score, root, quality, intervals))
    ranked.sort(reverse=True)
    if not ranked:
        return None
    best = ranked[0]
    second = ranked[1][0] if len(ranked) > 1 else 0.0
    margin = best[0] - second
    if best[0] < min_confidence or margin < min_margin:
        return None
    score, root, quality, intervals = best
    return {
        "root_pitch_class": NOTE_NAMES[root],
        "quality": quality,
        "chord_name_candidate": NOTE_NAMES[root] + {
            "MAJOR": "", "MINOR": "m", "DIMINISHED": "dim",
            "SUS2": "sus2", "SUS4": "sus4", "POWER5": "5"
        }[quality],
        "pitch_classes_candidate": [NOTE_NAMES[(root + step) % 12] for step in intervals],
        "confidence": round(score, 4),
        "margin": round(margin, 4),
        "active_pitch_classes": [NOTE_NAMES[index] for index in active],
    }


def analyze_chords(path: Path, *, frame_ms: int = 180, hop_ms: int = 60,
                   min_confidence: float = 0.78,
                   min_margin: float = 0.035,
                   min_region_seconds: float = 0.24) -> dict[str, Any]:
    path = Path(path).resolve()
    if frame_ms < 80 or hop_ms < 20 or hop_ms > frame_ms:
        raise ValueError("Use frame_ms >= 80 and 20 <= hop_ms <= frame_ms")
    if not 0.0 < min_confidence <= 1.0 or not 0.0 <= min_margin < 1.0:
        raise ValueError("Invalid confidence thresholds")
    if min_region_seconds <= 0:
        raise ValueError("min_region_seconds must be positive")

    samples, original_rate, total_frames, channels, width, decimation = read_mono_pcm(path)
    rate = original_rate / decimation
    # Bound the spectral analysis cost while retaining useful guitar bandwidth.
    extra = max(1, math.ceil(rate / 11025.0))
    samples = samples[::extra]
    rate /= extra
    size = 1
    requested = max(256, round(rate * frame_ms / 1000))
    while size < requested:
        size <<= 1
    hop = max(1, round(rate * hop_ms / 1000))

    frames: list[dict[str, Any]] = []
    for start in range(0, len(samples) - size + 1, hop):
        chroma = _frame_chroma(samples[start:start + size], rate)
        chord = _best_chord(chroma, min_confidence=min_confidence,
                            min_margin=min_margin)
        frames.append({
            "start_seconds": start / rate,
            "end_seconds": min(total_frames / original_rate, (start + size) / rate),
            "chord": chord,
        })

    regions: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []
    current_key = None
    for frame in frames + [{"chord": None, "start_seconds": 0.0, "end_seconds": 0.0}]:
        chord = frame["chord"]
        key = (chord["chord_name_candidate"] if chord else None)
        if key != current_key:
            if current and current_key is not None:
                start = current[0]["start_seconds"]
                end = current[-1]["end_seconds"]
                if end - start >= min_region_seconds:
                    confidences = [item["chord"]["confidence"] for item in current]
                    representative = current[len(current) // 2]["chord"]
                    regions.append({
                        "segment_id": f"CHORD-{len(regions) + 1:04d}",
                        "segment_type_candidate": "CHORD_REGION",
                        "start_seconds": round(start, 6),
                        "end_seconds": round(end, 6),
                        "duration_seconds": round(end - start, 6),
                        **representative,
                        "mean_confidence": round(sum(confidences) / len(confidences), 4),
                        "review_status": "NEEDS_MUSICAL_REVIEW",
                        "license_status": "UNREVIEWED",
                    })
            current = []
            current_key = key
        if chord is not None:
            current.append(frame)

    return {
        "chord_analyzer_version": VERSION,
        "source_path": str(path),
        "source_sha256": sha256_file(path),
        "duration_seconds": round(total_frames / original_rate, 6),
        "sample_rate": original_rate,
        "channels": channels,
        "sample_width_bytes": width,
        "frame_count": len(frames),
        "chord_candidate_count": len(regions),
        "chord_candidates": regions,
        "review_status": "NEEDS_MUSICAL_REVIEW",
        "license_status": "UNREVIEWED",
        "automatic_destructive_action": "NONE",
        "limitations": [
            "Experimental chroma/template candidates; not verified chord transcription.",
            "Distortion, harmonics, inversions, doubled notes, detuning and overlapping instruments can mislead the templates.",
            "A candidate is a pitch-class hypothesis, not a guitar fingering, string/fret map or confirmed voicing.",
            "Only stable regions meeting duration/confidence/margin thresholds are emitted; uncertain regions remain unlabelled.",
            "Input must already have passed guitar-source filtering; this module does not identify Piano, Bell or Drum.",
            "No audio is extracted or modified. All candidates require listening and human review.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate review-only polyphonic chord candidates from a guitar WAV.")
    parser.add_argument("wav", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-confidence", type=float, default=0.78)
    parser.add_argument("--min-margin", type=float, default=0.035)
    args = parser.parse_args()
    result = analyze_chords(args.wav, min_confidence=args.min_confidence,
                            min_margin=args.min_margin)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
