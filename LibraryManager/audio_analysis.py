#!/usr/bin/env python3
"""Dependency-free first-pass WAV analysis.

Produces evidence/features and review candidates; it does not claim definitive
music transcription, chord recognition, or automatic musical segmentation.
"""
from __future__ import annotations
import argparse, json, math, statistics, wave
from pathlib import Path

def _decode_sample(raw: bytes, width: int) -> int:
    if width == 1:
        return (raw[0] - 128) << 8
    if width == 2:
        return int.from_bytes(raw, "little", signed=True)
    if width == 3:
        value = int.from_bytes(raw + (b"\xff" if raw[2] & 0x80 else b"\x00"), "little", signed=True)
        return value >> 8
    if width == 4:
        return int.from_bytes(raw, "little", signed=True) >> 16
    raise ValueError("Unsupported PCM sample width")

def read_mono_pcm(path: Path, max_samples: int = 2_000_000):
    with wave.open(str(path), "rb") as w:
        if w.getcomptype() != "NONE":
            raise ValueError("Only uncompressed PCM WAV is supported")
        channels, width, rate, frames = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        if width not in (1, 2, 3, 4):
            raise ValueError("Unsupported PCM sample width")
        stride = channels * width
        hop = max(1, math.ceil(frames / max_samples))
        values = []
        index = 0
        while True:
            block = w.readframes(min(8192, frames - index))
            if not block:
                break
            usable = len(block) - (len(block) % stride)
            for off in range(0, usable, stride * hop):
                total = 0
                for ch in range(channels):
                    start = off + ch * width
                    total += _decode_sample(block[start:start + width], width)
                values.append(total / channels / 32768.0)
            index += usable // stride
        return values, rate, frames, channels, width, hop

def _autocorrelation_pitch(samples, rate):
    if len(samples) < 128:
        return None
    # Use a bounded, decimated window to keep the pure-Python calculation practical.
    step = max(1, len(samples) // 4096)
    x = samples[::step][:4096]
    sr = rate / step
    mean = sum(x) / len(x)
    x = [v - mean for v in x]
    min_lag = max(2, int(sr / 1200))
    max_lag = min(len(x) // 2, int(sr / 65))
    if max_lag <= min_lag:
        return None
    best_lag, best = None, 0.0
    energy = sum(v*v for v in x)
    if energy < 1e-10:
        return None
    for lag in range(min_lag, max_lag + 1):
        corr = sum(x[i] * x[i + lag] for i in range(len(x) - lag)) / energy
        if corr > best:
            best, best_lag = corr, lag
    if best_lag is None or best < 0.35:
        return None
    hz = sr / best_lag
    midi = round(69 + 12 * math.log2(hz / 440.0))
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return {"frequency_hz": round(hz, 2), "midi_note": midi,
            "note_name": names[midi % 12] + str(midi // 12 - 1),
            "confidence": round(min(1.0, best), 3)}

def analyse_wav(path: Path, frame_ms: int = 20, hop_ms: int = 10) -> dict:
    samples, rate, frames, channels, width, decimation = read_mono_pcm(path)
    if rate <= 0 or not samples:
        raise ValueError("Empty or invalid WAV")
    frame = max(32, round(rate * frame_ms / 1000 / decimation))
    hop = max(1, round(rate * hop_ms / 1000 / decimation))
    rms, zcr, times = [], [], []
    for start in range(0, max(1, len(samples) - frame + 1), hop):
        chunk = samples[start:start + frame]
        if len(chunk) < frame:
            break
        rms.append(math.sqrt(sum(v*v for v in chunk) / frame))
        zcr.append(sum(1 for a,b in zip(chunk, chunk[1:]) if (a < 0) != (b < 0)) / max(1, frame-1))
        times.append(start * decimation / rate)
    if not rms:
        rms, zcr, times = [0.0], [0.0], [0.0]
    peak = max((abs(v) for v in samples), default=0.0)
    mean_rms = statistics.fmean(rms)
    # Positive frame-to-frame energy changes are onset evidence, not musical boundaries.
    onset = [max(0.0, rms[i] - rms[i-1]) for i in range(1, len(rms))]
    onset_mean = statistics.fmean(onset) if onset else 0.0
    onset_std = statistics.pstdev(onset) if len(onset) > 1 else 0.0
    threshold = onset_mean + 2.0 * onset_std
    onset_candidates = [round(times[i+1], 4) for i,v in enumerate(onset) if v > threshold and v > 0.015]
    # Tempo candidates from onset-envelope autocorrelation, explicitly approximate.
    tempo = None
    if len(onset) >= 20 and onset_mean > 1e-6:
        env = [v - onset_mean for v in onset]
        env_rate = 1000.0 / hop_ms
        min_lag, max_lag = int(env_rate * 60 / 200), int(env_rate * 60 / 60)
        best_lag, best_corr = None, 0.0
        for lag in range(max(1,min_lag), min(max_lag, len(env)//2) + 1):
            corr = sum(env[i]*env[i+lag] for i in range(len(env)-lag))
            if corr > best_corr:
                best_lag, best_corr = lag, corr
        if best_lag and best_corr > 0:
            tempo = round(60 * env_rate / best_lag, 1)
    pitch = _autocorrelation_pitch(samples, rate)
    return {
        "analysis_version": "0.1.0",
        "source": str(path.resolve()),
        "duration_seconds": round(frames / rate, 6),
        "sample_rate": rate, "channels": channels, "sample_width_bytes": width,
        "analysis_decimation": decimation,
        "level": {"peak": round(peak, 6), "mean_frame_rms": round(mean_rms, 6),
                  "rms_min": round(min(rms), 6), "rms_max": round(max(rms), 6)},
        "zero_crossing_rate_mean": round(statistics.fmean(zcr), 6),
        "tempo_candidate_bpm": tempo,
        "dominant_pitch_candidate": pitch,
        "onset_evidence_seconds": onset_candidates,
        "onset_evidence_count": len(onset_candidates),
        "limitations": [
            "Tempo and pitch are approximate analysis candidates, not verified transcription.",
            "Onset evidence is not a phrase or loop boundary decision.",
            "No chord, key, articulation, guitar-style or instrument-role identity is asserted.",
            "Polyphonic and distorted guitar audio may produce unreliable pitch estimates."
        ]
    }

def main():
    ap = argparse.ArgumentParser(description="Generate first-pass acoustic evidence for a WAV file.")
    ap.add_argument("wav", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = analyse_wav(args.wav)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)

if __name__ == "__main__":
    main()
