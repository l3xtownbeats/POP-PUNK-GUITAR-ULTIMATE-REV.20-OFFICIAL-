#!/usr/bin/env python3
"""Experimental, non-destructive time-frequency landmark fingerprints.

This is a first fingerprint foundation, not a Shazam clone and not a musical
similarity classifier. A match is only a review candidate for the same
recorded passage/derivative. It must never trigger deletion, merging or routing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from audio_analysis import read_mono_pcm

FINGERPRINT_VERSION = "0.1.0"
FFT_SIZE = 2048
HOP_SIZE = 512
MAX_PEAKS_PER_FRAME = 6
MAX_LANDMARKS = 250_000


def _fft_real(values: list[float]) -> list[complex]:
    """In-place iterative radix-2 FFT; input length must be a power of two."""
    n = len(values)
    data = [complex(v, 0.0) for v in values]
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            data[i], data[j] = data[j], data[i]
    length = 2
    while length <= n:
        angle = -2.0 * math.pi / length
        root = complex(math.cos(angle), math.sin(angle))
        half = length >> 1
        for start in range(0, n, length):
            factor = 1 + 0j
            for k in range(start, start + half):
                u, v = data[k], data[k + half] * factor
                data[k], data[k + half] = u + v, u - v
                factor *= root
        length <<= 1
    return data


def _frame_peaks(frame: list[float], rate: float) -> list[int]:
    windowed = [frame[i] * (0.5 - 0.5 * math.cos(2 * math.pi * i / (len(frame)-1)))
                for i in range(len(frame))]
    spectrum = _fft_real(windowed)
    mags = [abs(spectrum[i]) for i in range(2, len(frame)//2 - 1)]
    if not mags or max(mags) < 1e-5:
        return []
    floor = max(mags) * 0.12
    peaks = []
    for offset in range(1, len(mags)-1):
        mag = mags[offset]
        if mag >= floor and mag > mags[offset-1] and mag >= mags[offset+1]:
            peaks.append((mag, offset + 2))
    peaks.sort(reverse=True)
    # Frequency bins are kept as integer bins; sample-rate is part of the report.
    return [bin_index for _, bin_index in peaks[:MAX_PEAKS_PER_FRAME]]


def fingerprint_wav(path: Path) -> dict:
    samples, rate, frames, channels, width, decimation = read_mono_pcm(path, max_samples=1_000_000)
    if rate <= 0 or not samples:
        raise ValueError("Empty or invalid WAV")
    effective_rate = rate / decimation
    if len(samples) < FFT_SIZE:
        raise ValueError(f"WAV is shorter than {FFT_SIZE} analysis samples")
    landmarks = []
    frame_peaks = []
    for start in range(0, len(samples) - FFT_SIZE + 1, HOP_SIZE):
        frame = samples[start:start + FFT_SIZE]
        frame_peaks.append(_frame_peaks(frame, effective_rate))
    # Pair peaks across nearby frames. This gives limited timing/frequency
    # invariance while retaining a deterministic, versioned representation.
    for anchor, peaks in enumerate(frame_peaks):
        for target in range(anchor + 1, min(len(frame_peaks), anchor + 6)):
            delta = target - anchor
            for f1 in peaks[:4]:
                for f2 in frame_peaks[target][:4]:
                    token = f"{f1}:{f2}:{delta}:{round(effective_rate)}"
                    digest = hashlib.sha1(token.encode("ascii")).hexdigest()[:16]
                    landmarks.append({"hash": digest,
                                      "time_seconds": round(anchor * HOP_SIZE / effective_rate, 5)})
                    if len(landmarks) >= MAX_LANDMARKS:
                        break
                if len(landmarks) >= MAX_LANDMARKS:
                    break
            if len(landmarks) >= MAX_LANDMARKS:
                break
        if len(landmarks) >= MAX_LANDMARKS:
            break
    return {
        "fingerprint_version": FINGERPRINT_VERSION,
        "source": str(path.resolve()),
        "duration_seconds": round(frames / rate, 6),
        "sample_rate": rate,
        "analysis_sample_rate": round(effective_rate, 3),
        "analysis_decimation": decimation,
        "fft_size": FFT_SIZE,
        "hop_size": HOP_SIZE,
        "landmark_count": len(landmarks),
        "landmarks": landmarks,
        "review_status": "NEEDS_MUSICAL_REVIEW",
        "limitations": [
            "Experimental spectral landmark fingerprint; not a production-grade Shazam implementation.",
            "A match suggests a possible shared recording passage or derivative, not musical equivalence.",
            "Different performances of the same riff are not expected to match reliably.",
            "No timbre, rhythm, melody, chord, riff or articulation similarity is inferred.",
            "No file is changed, moved, deleted, merged or automatically routed."
        ]
    }


def compare_fingerprints(left: dict, right: dict) -> dict:
    if left.get("fingerprint_version") != right.get("fingerprint_version"):
        raise ValueError("Fingerprint versions must match")
    a, b = left.get("landmarks", []), right.get("landmarks", [])
    if not a or not b:
        return {"relationship_candidate": "NO_FINGERPRINT_EVIDENCE",
                "matched_landmarks": 0, "confidence": 0.0,
                "review_status": "NEEDS_MUSICAL_REVIEW"}
    index = {}
    for item in b:
        index.setdefault(item["hash"], []).append(item["time_seconds"])
    offsets = Counter()
    matched = 0
    for item in a:
        hits = index.get(item["hash"], ())
        if hits:
            matched += 1
            # Quantized offset histogram absorbs small frame/rounding jitter.
            for hit in hits:
                offsets[round(hit - item["time_seconds"], 1)] += 1
    best_offset, best_count = offsets.most_common(1)[0] if offsets else (0.0, 0)
    denominator = max(1, min(len(a), len(b)))
    score = min(1.0, best_count / denominator)
    return {
        "relationship_candidate": "POSSIBLE_SAME_RECORDED_PASSAGE" if best_count >= 8 else "INSUFFICIENT_MATCH_EVIDENCE",
        "matched_landmarks": matched,
        "aligned_landmarks": best_count,
        "alignment_offset_seconds": best_offset,
        "confidence": round(score, 4),
        "left_landmark_count": len(a),
        "right_landmark_count": len(b),
        "review_status": "NEEDS_MUSICAL_REVIEW",
        "action": "REPORT_ONLY_NO_DESTRUCTIVE_ACTION"
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create experimental WAV landmark fingerprints.")
    parser.add_argument("wav", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compare", type=Path, help="Compare against another fingerprint JSON report.")
    args = parser.parse_args()
    result = fingerprint_wav(args.wav)
    if args.compare:
        other = json.loads(args.compare.read_text(encoding="utf-8"))
        result["comparison"] = compare_fingerprints(result, other)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
