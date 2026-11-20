"""Session Guitarist-inspired, vendor-neutral Pattern Mode manifest contract.

This describes our own engine data model. It does not contain NI code or assets.
"""
from __future__ import annotations

from typing import Any

SCHEMA_VERSION = 1
ENGINE_MODEL = "POP_PUNK_PATTERN_PERFORMANCE"

DEFAULT_PATTERN_SLOTS = (
    {"key_label": "C1", "pattern_id": "POP_PUNK_DOWNSTROKE", "display_name": "Pop Punk Downstroke",
     "candidate_models": ["STRUMMING_PERFORMANCE"]},
    {"key_label": "C#1", "pattern_id": "PALM_MUTE_8TH_NOTES", "display_name": "Palm Mute 8th Notes",
     "candidate_models": ["STRUMMING_PERFORMANCE"]},
    {"key_label": "D1", "pattern_id": "POWER_CHORD_RHYTHM", "display_name": "Power Chord Rhythm",
     "candidate_models": ["STRUMMING_PERFORMANCE", "CHORD_AWARE_RIFF"]},
    {"key_label": "D#1", "pattern_id": "PUNK_ROCK_RHYTHM", "display_name": "Punk Rock Rhythm",
     "candidate_models": ["STRUMMING_PERFORMANCE", "CHORD_AWARE_RIFF"]},
    {"key_label": "E1", "pattern_id": "FAST_DOWNSTROKE", "display_name": "Fast Downstroke",
     "candidate_models": ["STRUMMING_PERFORMANCE"]},
    {"key_label": "F1", "pattern_id": "ALTERNATIVE_PUNK_RHYTHM", "display_name": "Alternative Punk Rhythm",
     "candidate_models": ["STRUMMING_PERFORMANCE", "ARPEGGIO_EVENT_PATTERN"]},
)

SUPPORTED_PERFORMANCE_MODELS = (
    "STRUMMING_PERFORMANCE", "ARPEGGIO_EVENT_PATTERN", "CHORD_AWARE_RIFF",
    "MELODY_PHRASE", "SAMPLE_NOTE_ZONE",
)

def build_pattern_engine_manifest() -> dict[str, Any]:
    """Return an unbound, review-safe template for the future VST3 engine."""
    return {
        "schema_version": SCHEMA_VERSION,
        "engine_model": ENGINE_MODEL,
        "status": "TEMPLATE_ONLY_NOT_FACTORY_READY",
        "midi_mapping": {
            "selector_label_convention": "HOST_CALIBRATION_REQUIRED",
            "selector_note_numbers": None,
            "selector_keys_are_control_only": True,
            "playable_chord_range": None,
            "range_overlap_allowed": False,
            "host_calibration_target": "FL_STUDIO_20",
        },
        "pattern_slots": [dict(slot) for slot in DEFAULT_PATTERN_SLOTS],
        "performance_models": list(SUPPORTED_PERFORMANCE_MODELS),
        "chord_adaptation_modes": [
            "AS_PLAYED", "REVIEWED_VOICING_PRESET", "CHORD_AWARE_INTERVAL_ADAPTATION",
        ],
        "event_contract": {
            "required_fields": [
                "event_id", "position_ticks", "duration_ticks", "event_kind",
                "review_status", "source_sha256", "source_start_sample", "source_end_sample",
            ],
            "optional_reviewed_fields": [
                "midi_pitch", "chord_interval", "string_number", "fret_number",
                "stroke_direction", "articulation", "velocity_layer", "round_robin_group",
                "sample_zone_id", "transition_role", "noise_event_kind",
            ],
            "tempo_bpm": None, "tempo_confidence": None, "time_signature": None,
            "unknown_timing_must_remain_unknown": True,
        },
        "runtime_requirements": [
            "HOST_TRANSPORT_SYNC_AND_START_ON_KEY", "LEGATO_CHORD_AND_PATTERN_TRANSITIONS",
            "LATCH_AND_EXPLICIT_ENDINGS", "VELOCITY_AND_PERFORMANCE_DYNAMICS",
            "RECORDED_MICROTIMING_HUMANIZE", "REALTIME_SAFE_SAMPLE_SCHEDULING",
            "NO_WHOLE_LOOP_CHROMATIC_TRANSPOSITION_AS_CHORD_ENGINE",
        ],
        "review_policy": {
            "automatic_factory_promotion": False,
            "required_review_status": "REVIEWED",
            "required_license_status": "LICENSE_APPROVED",
            "source_assets_read_only": True,
        },
        "limitations": [
            "Key labels are not converted to MIDI note numbers until FL Studio 20 host calibration.",
            "This template does not claim that any source asset has been musically reviewed.",
            "Acoustic onset and pitch candidates are not proof of strum events, chords, strings or articulations.",
            "Only reviewed event/sample mappings may be consumed as playable factory content.",
        ],
    }


def validate_pattern_engine_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("Unsupported schema_version")
    mapping = manifest.get("midi_mapping", {})
    if mapping.get("selector_keys_are_control_only") is not True:
        errors.append("Selector keys must be control-only")
    if mapping.get("range_overlap_allowed") is not False:
        errors.append("Selector and playable ranges must never overlap")
    if mapping.get("selector_note_numbers") is not None and not isinstance(
        mapping.get("selector_note_numbers"), dict
    ):
        errors.append("selector_note_numbers must be a mapping or null")
    slots = manifest.get("pattern_slots", [])
    labels = [slot.get("key_label") for slot in slots]
    ids = [slot.get("pattern_id") for slot in slots]
    if len(labels) != len(set(labels)):
        errors.append("Duplicate selector key labels")
    if len(ids) != len(set(ids)):
        errors.append("Duplicate pattern IDs")
    for slot in slots:
        if not slot.get("key_label") or not slot.get("pattern_id"):
            errors.append("Every slot requires key_label and pattern_id")
    return errors
