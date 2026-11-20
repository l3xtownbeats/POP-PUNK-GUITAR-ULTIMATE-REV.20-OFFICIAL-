#!/usr/bin/env python3
"""Virtual riff extraction: index useful WAV ranges without slicing audio.

The source WAV is read-only. The engine writes JSON sidecars under the
user-approved Samples/Import Sample Guitar area; playback resolves each range
against the original file and verifies its SHA-256 before use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import wave
from pathlib import Path
from typing import Any

from audio_range_io import audio_source_info, write_pcm_wav_range

from app_paths import runtime_staging_root

STAGING_BASE = runtime_staging_root(__file__)

VERSION = "0.2.0"
DEFAULT_WINDOW_MS = 20
DEFAULT_HOP_MS = 10


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _frame_levels(source: Path, window_ms: int, hop_ms: int) -> tuple[list[dict[str, float]], dict[str, int]]:
    with wave.open(str(source), "rb") as reader:
        if reader.getcomptype() != "NONE":
            raise ValueError("Only uncompressed PCM WAV is supported")
        channels, width, rate, total = (reader.getnchannels(), reader.getsampwidth(),
                                        reader.getframerate(), reader.getnframes())
        if width not in (1, 2, 3, 4) or channels < 1 or rate <= 0:
            raise ValueError("Unsupported WAV format")
        window = max(1, round(rate * window_ms / 1000))
        hop = max(1, round(rate * hop_ms / 1000))
        if total < window:
            raise ValueError("WAV is shorter than one analysis window")
        # Sequential bounded-memory reader: read the first window once, then
        # advance by hop frames while retaining only the overlap. This avoids
        # one seek and one overlapping disk read for every 10 ms window.
        frame_bytes = channels * width
        levels = []
        raw = bytearray(reader.readframes(window))
        if len(raw) != window * frame_bytes:
            raise IOError("Incomplete PCM analysis window")
        start = 0
        scale = float(1 << (8 * width - 1))
        while len(raw) == window * frame_bytes:
            square_sum = 0.0
            crossings = 0
            previous = None
            frame_count = 0
            for offset in range(0, len(raw), frame_bytes):
                mono = 0.0
                for channel in range(channels):
                    sample_start = offset + channel * width
                    if width == 1:
                        value = (raw[sample_start] - 128) / 128.0
                    elif width == 3:
                        b0, b1, b2 = raw[sample_start:sample_start + 3]
                        integer = b0 | (b1 << 8) | (b2 << 16)
                        if integer & 0x800000:
                            integer -= 0x1000000
                        value = integer / scale
                    else:
                        sample = raw[sample_start:sample_start + width]
                        value = int.from_bytes(sample, "little", signed=True) / scale
                    mono += value
                mono /= channels
                square_sum += mono * mono
                if previous is not None and ((previous < 0) != (mono < 0)):
                    crossings += 1
                previous = mono
                frame_count += 1
            levels.append({
                "start_sample": start,
                "end_sample": start + window,
                "rms": math.sqrt(square_sum / max(1, frame_count)),
                "zcr": crossings / max(1, frame_count - 1),
            })
            if start + hop + window > total:
                break
            advance = hop * frame_bytes
            del raw[:advance]
            raw.extend(reader.readframes(hop))
            if len(raw) < window * frame_bytes:
                break
            start += hop
    return levels, {"sample_rate": rate, "channels": channels,
                    "sample_width_bytes": width, "total_frames": total}


def detect_active_ranges(levels: list[dict[str, float]], *, sample_rate: int,
                         total_frames: int, min_duration_ms: int = 250,
                         silence_bridge_ms: int = 180,
                         threshold_floor: float = 0.003) -> list[tuple[int, int]]:
    """Find broad sound-active regions; these are review candidates, not riffs."""
    if not levels:
        return []
    if min_duration_ms < 50 or silence_bridge_ms < 0 or threshold_floor < 0:
        raise ValueError("Invalid segmentation parameters")
    values = [item["rms"] for item in levels]
    noise_floor = statistics.median(sorted(values)[:max(1, len(values) // 5)])
    peak = max(values)
    threshold = max(threshold_floor, noise_floor * 2.8, peak * 0.035)
    active = [item["rms"] >= threshold for item in levels]
    bridge = max(0, round(silence_bridge_ms / DEFAULT_HOP_MS))
    if bridge:
        index = 0
        while index < len(active):
            if active[index]:
                index += 1
                continue
            start = index
            while index < len(active) and not active[index]:
                index += 1
            if start > 0 and index < len(active) and index - start <= bridge:
                active[start:index] = [True] * (index - start)

    ranges = []
    start_index = None
    for index, is_active in enumerate(active + [False]):
        if is_active and start_index is None:
            start_index = index
        elif not is_active and start_index is not None:
            start = levels[start_index]["start_sample"]
            end = min(total_frames, levels[index - 1]["end_sample"])
            if (end - start) * 1000 / sample_rate >= min_duration_ms:
                ranges.append((max(0, start), end))
            start_index = None
    return ranges


def _range_fingerprint(levels: list[dict[str, float]], start: int, end: int) -> str:
    selected = [item for item in levels
                if item["start_sample"] < end and item["end_sample"] > start]
    if not selected:
        return hashlib.sha256(b"empty-range").hexdigest()
    # Quantized RMS + zero-crossing envelope is a repeatable search fingerprint,
    # not an audio reconstruction and not a cryptographic identity of the clip.
    payload = "|".join(
        f'{round(item["rms"] * 10000)}:{round(item["zcr"] * 1000)}'
        for item in selected
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest().upper()


def analyze_pattern_ranges(source: Path, pattern_report: dict[str, Any], *,
                          guitar_source_confirmed: bool = False,
                          source_sha256: str = "") -> dict[str, Any]:
    """Create Pattern Mode ranges only from repeated rhythmic motifs.

    A candidate must be a repeated onset-interval motif with at least two
    non-overlapping occurrences, >=5 source onsets, >=0.65 rhythmic regularity,
    and >=4 attacks per occurrence. Broad RMS-active regions are never promoted.
    """
    source = Path(source).resolve()
    if not guitar_source_confirmed:
        raise ValueError("Confirm guitar-only source before Pattern Mode analysis")
    patterns = pattern_report.get("pattern_analysis", {}).get("patterns", [])
    if not isinstance(patterns, list):
        raise ValueError("Pattern report does not contain a valid pattern list")
    regularity = pattern_report.get("pattern_analysis", {}).get("rhythmic_regularity_candidate")
    onset_count = int(pattern_report.get("pattern_analysis", {}).get("onset_count") or 0)
    if not isinstance(regularity, (int, float)) or regularity < 0.65 or onset_count < 5:
        patterns = []
    info = audio_source_info(source)
    rate, total = info.framerate, info.frames
    candidates = []
    for pattern in patterns:
        if pattern.get("candidate_type") != "REPEATED_RHYTHM_MOTIF":
            continue
        if int(pattern.get("occurrence_count") or 0) < 2:
            continue
        for occurrence in pattern.get("occurrences", []):
            start_s = float(occurrence.get("start_seconds") or 0.0)
            end_s = float(occurrence.get("end_seconds") or 0.0)
            hits = int(occurrence.get("end_onset_index_exclusive") or 0) - int(
                occurrence.get("start_onset_index") or 0
            )
            duration = end_s - start_s
            if hits < 4 or duration < 0.35 or duration > 20.0:
                continue
            start = max(0, int(round((start_s - 0.02) * rate)))
            end = min(total, int(round((end_s + 0.03) * rate)))
            if end <= start:
                continue
            identity = hashlib.sha256(
                f"{source_sha256}:{start}:{end}:{pattern.get('pattern_candidate_id')}:{VERSION}".encode("utf-8")
            ).hexdigest().upper()[:24]
            candidates.append({
                "candidate_id": identity,
                "candidate_type": "REPEATED_GUITAR_RHYTHM_PATTERN",
                "pattern_candidate_id": pattern.get("pattern_candidate_id", ""),
                "pattern_signature_units": pattern.get("pattern_signature_units", []),
                "source_start_sample": start, "source_end_sample": end,
                "start_seconds": round(start / rate, 6),
                "end_seconds": round(end / rate, 6),
                "duration_seconds": round((end - start) / rate, 6),
                "onset_count_candidate": hits,
                "pattern_occurrence_count": int(pattern.get("occurrence_count") or 0),
                "rhythmic_regularity_candidate": round(float(regularity), 4),
                "review_status": "NEEDS_MUSICAL_REVIEW",
                "license_status": "UNREVIEWED",
                "proposed_group": "PATTERN_MODE_CANDIDATES",
            })
            if len(candidates) >= 500:
                break
        if len(candidates) >= 500:
            break
    return {
        "schema_version": 1, "engine": "PATTERN_MODE_VIRTUAL_EXTRACTION",
        "engine_version": VERSION, "source_path": str(source),
        "source_sha256": source_sha256.upper(), "sample_rate": rate,
        "channels": info.nchannels, "sample_width_bytes": info.sampwidth,
        "total_frames": total, "candidate_count": len(candidates),
        "audio_copied": False, "audio_modified": False,
        "extraction_policy": "REPEATED_RHYTHM_ONLY_NO_BROAD_RMS_ACTIVE_REGIONS",
        "candidates": candidates,
        "limitations": [
            "Candidates are repeated onset-timing motifs, not guaranteed complete bars or seamless loops.",
            "Only repeated patterns with multiple attacks and stable rhythmic evidence are proposed.",
            "Melodic note candidates remain a separate Melody Mode path.",
            "Every candidate requires listening and manual review; no automatic FACTORY promotion occurs.",
        ],
    }


def analyze_long_wav(source: Path, *, guitar_source_confirmed: bool = False,
                     window_ms: int = DEFAULT_WINDOW_MS,
                     hop_ms: int = DEFAULT_HOP_MS,
                     min_duration_ms: int = 250,
                     silence_bridge_ms: int = 180) -> dict[str, Any]:
    source = Path(source).resolve()
    if not guitar_source_confirmed:
        raise ValueError("Confirm that the source has passed guitar-only filtering before analysis")
    if window_ms < 10 or hop_ms < 5 or hop_ms > window_ms:
        raise ValueError("Require window_ms >= 10 and 5 <= hop_ms <= window_ms")
    # Segmentation currently uses a fixed 10 ms hop for gap bridging.
    if hop_ms != DEFAULT_HOP_MS:
        raise ValueError("This version currently requires hop_ms=10")
    levels, fmt = _frame_levels(source, window_ms, hop_ms)
    ranges = detect_active_ranges(levels, sample_rate=fmt["sample_rate"],
                                  total_frames=fmt["total_frames"],
                                  min_duration_ms=min_duration_ms,
                                  silence_bridge_ms=silence_bridge_ms)
    source_hash = sha256_file(source)
    candidates = []
    for start, end in ranges:
        identity = hashlib.sha256(
            f"{source_hash}:{start}:{end}:{VERSION}".encode("ascii")
        ).hexdigest().upper()[:24]
        candidates.append({
            "candidate_id": identity,
            "candidate_type": "SOUND_ACTIVE_REGION",
            "source_start_sample": start,
            "source_end_sample": end,
            "start_seconds": round(start / fmt["sample_rate"], 6),
            "end_seconds": round(end / fmt["sample_rate"], 6),
            "duration_seconds": round((end - start) / fmt["sample_rate"], 6),
            "acoustic_fingerprint": _range_fingerprint(levels, start, end),
            "fingerprint_algorithm": "RMS_ZCR_ENVELOPE_SHA256",
            "fingerprint_version": VERSION,
            "review_status": "NEEDS_MUSICAL_REVIEW",
            "license_status": "UNREVIEWED",
            "proposed_group": "RIFF_CANDIDATES",
        })
    return {
        "schema_version": 1,
        "engine": "VIRTUAL_SAMPLE_EXTRACTION",
        "engine_version": VERSION,
        "source_path": str(source),
        "source_sha256": source_hash,
        **fmt,
        "candidate_count": len(candidates),
        "audio_copied": False,
        "audio_modified": False,
        "candidates": candidates,
        "limitations": [
            "This pass finds broad sound-active regions, not verified riffs, notes, chords, bars or loops.",
            "A guitar-only source must be confirmed by the upstream instrument filter; Piano, Bell and Drum must not enter this stage.",
            "The fingerprint is a compact envelope search key, not a playable sound or proof of identical audio.",
            "Playback requires the original WAV to remain available and its SHA-256 to match.",
            "Candidates remain in Import Sample Guitar for listening and review; nothing is promoted to FACTORY automatically."
        ],
    }


def write_virtual_index(report: dict[str, Any], import_root: Path) -> list[Path]:
    """Write or safely reuse JSON sidecars under Samples/Import Sample Guitar."""
    root = Path(import_root).resolve()
    if root.name.casefold() != "import sample guitar":
        raise ValueError("Index destination must be the approved 'Import Sample Guitar' folder")
    source = Path(report["source_path"]).resolve()
    expected_hash = str(report["source_sha256"]).upper()
    if sha256_file(source) != expected_hash:
        raise RuntimeError("Source SHA-256 changed after analysis; refusing to index")
    target_name = ("PATTERN_MODE_CANDIDATES"
                   if report.get("engine") == "PATTERN_MODE_VIRTUAL_EXTRACTION"
                   else "RIFF_CANDIDATES")
    target = root / "VIRTUAL_CANDIDATES" / target_name
    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    created: list[Path] = []
    try:
        for candidate in report["candidates"]:
            path = target / f'{candidate["candidate_id"]}.json'
            record = {
                "schema_version": report["schema_version"],
                "asset_kind": "VIRTUAL_AUDIO_RANGE",
                "source_path": str(source),
                "source_sha256": expected_hash,
                "sample_rate": report["sample_rate"],
                "channels": report["channels"],
                "sample_width_bytes": report["sample_width_bytes"],
                "frame_count": candidate["source_end_sample"] - candidate["source_start_sample"],
                **candidate,
                "playback": "Read source_path from source_start_sample for frame_count frames",
                "automatic_destructive_action": "NONE",
            }
            if path.exists():
                if not path.is_file():
                    raise FileExistsError(f"Virtual sidecar path is not a regular file: {path}")
                existing = json.loads(path.read_text(encoding="utf-8"))
                matches = (
                    str(existing.get("source_sha256", "")).upper() == expected_hash
                    and Path(str(existing.get("source_path", ""))).resolve() == source
                    and existing.get("candidate_id") == candidate.get("candidate_id")
                    and int(existing.get("source_start_sample", -1)) == int(candidate["source_start_sample"])
                    and int(existing.get("source_end_sample", -1)) == int(candidate["source_end_sample"])
                    and existing.get("acoustic_fingerprint") == candidate.get("acoustic_fingerprint")
                )
                if not matches:
                    raise RuntimeError(
                        f"Existing virtual sidecar failed source/range/fingerprint validation: {path.name}"
                    )
                written.append(path)
                continue
            # Exclusive creation prevents overwriting user or concurrent data.
            with path.open("x", encoding="utf-8") as stream:
                json.dump(record, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            created.append(path)
            written.append(path)

        if sha256_file(source) != expected_hash:
            raise RuntimeError("Source SHA-256 changed while writing virtual index")
        return written
    except Exception:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        raise



def _safe_staging_root(path: Path) -> Path:
    root = Path(path).expanduser().resolve()
    try:
        root.relative_to(STAGING_BASE)
    except ValueError as exc:
        raise ValueError("Extracted long-recording WAVs must remain inside LibraryManager/staging") from exc
    return root


def extract_virtual_ranges(
    report: dict[str, Any],
    staging_root: Path = STAGING_BASE,
    *,
    max_clips: int = 100,
    min_duration_ms: int = 250,
    cancel_event: Any = None,
    progress: Any = None,
) -> list[dict[str, Any]]:
    """Physically extract reviewed-range candidates from a long WAV to staging.

    The detector only supplies broad sound-active regions. Extracted WAVs remain
    NEEDS_MUSICAL_REVIEW/UNREVIEWED and are never presented as verified riffs.
    Source offsets are exact frames; audio is decoded/written in bounded blocks.
    """
    if max_clips < 0 or max_clips > 1000 or min_duration_ms < 1:
        raise ValueError("Invalid virtual-range extraction limits")
    if max_clips == 0:
        return []
    root = _safe_staging_root(staging_root)
    source = Path(str(report.get("source_path") or "")).expanduser().resolve()
    expected_hash = str(report.get("source_sha256") or "").upper()
    candidates = report.get("candidates")
    if not source.is_file() or len(expected_hash) != 64:
        raise ValueError("Virtual-range report must identify an existing source and SHA-256")
    if not isinstance(candidates, list):
        raise ValueError("Virtual-range report does not contain a candidate list")
    if sha256_file(source) != expected_hash:
        raise RuntimeError("Source SHA-256 changed since long-recording analysis")

    info = audio_source_info(source)
    if (int(report.get("sample_rate") or 0) != info.framerate
            or int(report.get("total_frames") or -1) != info.frames):
        raise RuntimeError("Long-recording report no longer matches source audio metadata")
    clips_dir, manifests_dir = root / "clips", root / "manifests"
    for folder in (clips_dir, manifests_dir):
        folder.mkdir(parents=True, exist_ok=True)
        try:
            folder.resolve().relative_to(root)
            folder.resolve().relative_to(STAGING_BASE)
        except ValueError as exc:
            raise ValueError("Staging subdirectories must not resolve outside staging") from exc

    results: list[dict[str, Any]] = []
    created: list[Path] = []
    seen_ranges: set[tuple[int, int]] = set()
    try:
        for candidate in candidates:
            if cancel_event is not None and cancel_event.is_set():
                raise RuntimeError("Long-recording extraction stopped by user")
            if len(results) >= max_clips:
                break
            start = int(candidate.get("source_start_sample", -1))
            end = int(candidate.get("source_end_sample", -1))
            if start < 0 or end <= start or end > info.frames:
                raise ValueError("Virtual candidate contains an invalid source-frame range")
            if (end - start) * 1000 < min_duration_ms * info.framerate:
                continue
            key = (start, end)
            if key in seen_ranges:
                continue
            seen_ranges.add(key)
            identity = hashlib.sha256(
                f"{expected_hash}:LONG_REGION:{start}:{end}:{VERSION}".encode("utf-8")
            ).hexdigest()[:24].upper()
            clip = clips_dir / f"REGION-{identity}.wav"
            manifest = manifests_dir / f"REGION-{identity}.json"
            if clip.exists() or manifest.exists():
                if not (clip.is_file() and manifest.is_file()):
                    raise FileExistsError(f"Incomplete existing long-recording candidate {identity}")
                existing = json.loads(manifest.read_text(encoding="utf-8"))
                matches = (
                    existing.get("source_sha256") == expected_hash
                    and int(existing.get("source_start_sample", -1)) == start
                    and int(existing.get("source_end_sample", -1)) == end
                    and Path(str(existing.get("derived_path", ""))).resolve() == clip.resolve()
                    and str(existing.get("derived_sha256", "")).upper() == sha256_file(clip)
                )
                if not matches:
                    raise RuntimeError(f"Existing staged long-recording candidate failed provenance/hash validation: {identity}")
                existing["reused_existing"] = True
                results.append(existing)
                if progress and (len(results) == 1 or len(results) % 10 == 0):
                    progress(f"Проверено WAV-отрывков длинной записи: {len(results)}")
                continue

            clip_info = write_pcm_wav_range(
                source, start, end, clip, expected_rate=info.framerate,
            )
            created.append(clip)
            record = {
                "schema_version": 1,
                "asset_id": identity,
                "parent_asset_id": expected_hash,
                "source_path": str(source),
                "source_sha256": expected_hash,
                "source_start_sample": start,
                "source_end_sample": end,
                "source_start_seconds": round(start / info.framerate, 6),
                "source_end_seconds": round(end / info.framerate, 6),
                "frame_count": end - start,
                "duration_seconds": round((end - start) / info.framerate, 6),
                "sample_rate": clip_info["sample_rate"],
                "channels": clip_info["channels"],
                "sample_width_bytes": clip_info["sample_width_bytes"],
                "source_format": info.source_format,
                "source_subtype": info.source_subtype,
                "derived_format": clip_info["derived_format"],
                "derived_subtype": clip_info["derived_subtype"],
                "derived_path": str(clip),
                "derived_sha256": sha256_file(clip),
                "kind": "long_recording_region_candidate",
                "engine_targets": ["PATTERN_INSTRUMENT", "MELODY_INSTRUMENT"],
                "extractor": "virtual_sample_extractor",
                "extractor_version": VERSION,
                "musical_metadata": {
                    "candidate_type": candidate.get("candidate_type", "SOUND_ACTIVE_REGION"),
                    "candidate_id": candidate.get("candidate_id", identity),
                    "acoustic_fingerprint": candidate.get("acoustic_fingerprint", ""),
                    "fingerprint_algorithm": candidate.get("fingerprint_algorithm", ""),
                    "boundary_basis": "RMS_ZCR_SOUND_ACTIVE_REGION",
                    "boundary_confidence": None,
                    "musical_identity": "NOT_ESTABLISHED",
                },
                "confidence": None,
                "review_status": "NEEDS_MUSICAL_REVIEW",
                "license_status": "UNREVIEWED",
                "automatic_factory_promotion": False,
                "automatic_destructive_action": "NONE",
            }
            try:
                with manifest.open("x", encoding="utf-8") as stream:
                    json.dump(record, stream, ensure_ascii=False, indent=2)
                    stream.write("\n")
                created.append(manifest)
            except Exception:
                clip.unlink(missing_ok=True)
                created.remove(clip)
                raise
            record["reused_existing"] = False
            results.append(record)
            if progress and (len(results) == 1 or len(results) % 10 == 0):
                progress(f"Извлечено WAV-отрывков длинной записи: {len(results)}")

        if sha256_file(source) != expected_hash:
            raise RuntimeError("Source SHA-256 changed during long-recording extraction")
        return results
    except Exception:
        for path in reversed(created):
            path.unlink(missing_ok=True)
        raise



def main() -> int:
    parser = argparse.ArgumentParser(description="Index useful ranges in a guitar WAV without slicing the audio.")
    parser.add_argument("wav", type=Path)
    parser.add_argument("--import-root", type=Path,
                        help="Samples/Import Sample Guitar; writes JSON virtual candidates")
    parser.add_argument("--guitar-source-confirmed", action="store_true",
                        help="Confirm upstream filtering has excluded Piano, Bell and Drum")
    args = parser.parse_args()
    report = analyze_long_wav(args.wav, guitar_source_confirmed=args.guitar_source_confirmed)
    if args.import_root:
        report["index_files"] = [str(path) for path in write_virtual_index(report, args.import_root)]
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
