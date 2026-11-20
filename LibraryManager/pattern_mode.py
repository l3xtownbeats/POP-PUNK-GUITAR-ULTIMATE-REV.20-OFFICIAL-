"""PPGU Pattern Mode metadata and non-time-stretched playback planning.

This is a manager-side preparation/validation layer, not an audio renderer.
Patterns are recorded performances: tempo mismatch is reported, never repaired
by stretching the source audio. Articulations must be explicitly reviewed.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

PATTERN_SCHEMA = "ppgu.pattern_mode_asset/1.0.0"
DEFAULT_DOUBLING = {
    "enabled": False,
    "voice_count": 1,
    "timing_offset_ms": 0.0,
    "velocity_delta": 0,
    "humanization_seed": None,
}
ARTICULATIONS = {
    "HAMMER_ON", "PULL_OFF", "SLIDE", "LEGATO", "PALM_MUTE",
    "OPEN", "DOWNSTROKE", "UPSTROKE", "ACCENT",
}


def build_pattern_asset(
    *,
    asset_id: str,
    source_sha256: str,
    source_start_sample: int,
    source_end_sample: int,
    sample_rate: int,
    recorded_tempo_bpm: float | None,
    meter_numerator: int | None = None,
    meter_denominator: int | None = None,
    loop_start_sample: int | None = None,
    loop_end_sample: int | None = None,
    events: list[dict[str, Any]] | None = None,
    articulations_reviewed: bool = False,
    review_status: str = "NEEDS_MUSICAL_REVIEW",
    license_status: str = "UNREVIEWED",
) -> dict[str, Any]:
    """Create a review-only Pattern Mode descriptor with exact source bounds."""
    if not asset_id or len(source_sha256) != 64:
        raise ValueError("asset_id and a 64-character source SHA-256 are required")
    if any(c not in "0123456789abcdefABCDEF" for c in source_sha256):
        raise ValueError("source_sha256 must be hexadecimal")
    if type(source_start_sample) is not int or type(source_end_sample) is not int:
        raise ValueError("source bounds must be integer sample offsets")
    if source_start_sample < 0 or source_end_sample <= source_start_sample:
        raise ValueError("source sample range is invalid")
    if type(sample_rate) is not int or sample_rate <= 0:
        raise ValueError("sample_rate must be a positive integer")
    if recorded_tempo_bpm is not None and not 20 <= float(recorded_tempo_bpm) <= 400:
        raise ValueError("recorded_tempo_bpm must be between 20 and 400")
    if (meter_numerator is None) != (meter_denominator is None):
        raise ValueError("time signature numerator and denominator must be supplied together")
    if meter_numerator is not None and (meter_numerator <= 0 or meter_denominator <= 0):
        raise ValueError("time signature values must be positive")
    if (loop_start_sample is None) != (loop_end_sample is None):
        raise ValueError("loop start and end must be supplied together")
    if loop_start_sample is not None and not (
        source_start_sample <= loop_start_sample < loop_end_sample <= source_end_sample
    ):
        raise ValueError("loop bounds must be inside the reviewed source range")

    reviewed_events = []
    for event in events or []:
        item = deepcopy(event)
        articulation = item.get("articulation")
        if articulation is not None and articulation not in ARTICULATIONS:
            raise ValueError(f"unsupported articulation: {articulation}")
        if type(item.get("position_ticks")) is not int or item["position_ticks"] < 0:
            raise ValueError("each reviewed event needs a non-negative position_ticks")
        if type(item.get("duration_ticks")) is not int or item["duration_ticks"] <= 0:
            raise ValueError("each reviewed event needs a positive duration_ticks")
        reviewed_events.append(item)

    return {
        "schema": PATTERN_SCHEMA,
        "asset_id": asset_id,
        "source_sha256": source_sha256.lower(),
        "source_start_sample": source_start_sample,
        "source_end_sample": source_end_sample,
        "sample_rate": sample_rate,
        "recorded_tempo_bpm": float(recorded_tempo_bpm) if recorded_tempo_bpm is not None else None,
        "time_signature": (
            {"numerator": meter_numerator, "denominator": meter_denominator}
            if meter_numerator is not None else None
        ),
        "loop_start_sample": loop_start_sample,
        "loop_end_sample": loop_end_sample,
        "time_stretch": {"enabled": False, "policy": "NEVER_STRETCH_RECORDED_PATTERN"},
        "articulations": {
            "reviewed": bool(articulations_reviewed),
            "allowed": sorted(ARTICULATIONS),
            "events": reviewed_events,
            "automatic_inference": False,
        },
        "doubling": deepcopy(DEFAULT_DOUBLING),
        "review_status": review_status,
        "license_status": license_status,
        "runtime_ready": False,
        "blocking_reasons": [
            "Pattern events, bar/loop boundaries and chord adaptation require musical review.",
            "VST3 playback renderer and audio-quality validation are not implemented by this manager descriptor.",
        ],
    }


def set_doubling(
    pattern: dict[str, Any],
    *,
    enabled: bool,
    timing_offset_ms: float = 8.0,
    velocity_delta: int = -4,
    humanization_seed: int = 1,
) -> dict[str, Any]:
    """Set bounded natural-double parameters; does not synthesize or render audio."""
    if not isinstance(enabled, bool):
        raise ValueError("enabled must be boolean")
    if not 0 <= float(timing_offset_ms) <= 30:
        raise ValueError("timing_offset_ms must be between 0 and 30")
    if type(velocity_delta) is not int or not -20 <= velocity_delta <= 20:
        raise ValueError("velocity_delta must be an integer from -20 to 20")
    if type(humanization_seed) is not int:
        raise ValueError("humanization_seed must be an integer")
    result = deepcopy(pattern)
    result["doubling"] = {
        "enabled": enabled,
        "voice_count": 2 if enabled else 1,
        "timing_offset_ms": float(timing_offset_ms) if enabled else 0.0,
        "velocity_delta": velocity_delta if enabled else 0,
        "humanization_seed": humanization_seed if enabled else None,
    }
    return result


def build_playback_plan(
    pattern: dict[str, Any],
    *,
    project_tempo_bpm: float,
    incoming_chords: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Prepare a transparent plan; audio timing is unchanged and no WAV is stretched."""
    recorded = pattern.get("recorded_tempo_bpm")
    if project_tempo_bpm <= 0:
        raise ValueError("project_tempo_bpm must be positive")
    ratio = float(project_tempo_bpm) / float(recorded) if recorded else None
    events = deepcopy(pattern.get("articulations", {}).get("events", []))
    chord_changes = sorted(
        (deepcopy(chord) for chord in (incoming_chords or [])),
        key=lambda chord: chord.get("position_ticks", 0),
    )
    return {
        "pattern_asset_id": pattern.get("asset_id"),
        "recorded_tempo_bpm": recorded,
        "project_tempo_bpm": float(project_tempo_bpm),
        "tempo_ratio": ratio,
        "tempo_mismatch_warning": bool(ratio is not None and abs(ratio - 1.0) > 0.08),
        "time_stretch_applied": False,
        "source_audio_timing_preserved": True,
        "events": events,
        "articulations_applied_only_from_reviewed_events": bool(
            pattern.get("articulations", {}).get("reviewed")
        ),
        "incoming_chords": chord_changes,
        "chord_adaptation_status": "REQUIRES_VERIFIED_NOTE_VOICINGS",
        "doubling": deepcopy(pattern.get("doubling", DEFAULT_DOUBLING)),
        "runtime_ready": False,
    }
