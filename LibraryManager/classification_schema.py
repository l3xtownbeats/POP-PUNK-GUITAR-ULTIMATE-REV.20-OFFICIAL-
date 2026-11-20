#!/usr/bin/env python3
"""Controlled, multi-axis metadata vocabulary for guitar-library organization.

This module defines labels and validates proposed metadata. It does not guess
unknown musical facts, move files, or make destructive duplicate decisions.
"""
from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "1.0.0"

ASSET_ROLES = {
    "ONE_SHOT", "INDIVIDUAL_NOTE", "CHORD", "NOTE_SEQUENCE",
    "MELODIC_PHRASE", "RHYTHMIC_MELODY", "RHYTHM_PATTERN", "RIFF",
    "LOOP_CANDIDATE", "CONFIRMED_LOOP", "MULTI_HIT", "SUSTAIN",
    "FULL_TAKE", "AMBIENCE_OR_FX", "UNKNOWN"
}
INSTRUMENT_FAMILIES = {"ELECTRIC_GUITAR", "ACOUSTIC_GUITAR", "BASS_GUITAR",
                       "NYLON_GUITAR", "STEEL_STRING_GUITAR", "OTHER_STRING",
                       "UNKNOWN"}
TONE_FAMILIES = {"CLEAN", "EDGE_OF_BREAKUP", "CRUNCH", "OVERDRIVE",
                 "DISTORTION", "FUZZ", "ACOUSTIC_NATURAL", "PROCESSED",
                 "DI", "UNKNOWN"}
ARTICULATIONS = {"OPEN", "PALM_MUTE", "MUTED", "DOWNSTROKE", "UPSTROKE",
                 "ALTERNATE_PICKING", "TREMOLO_PICKING", "CHUGGING",
                 "ARPEGGIO", "STRUM", "FINGER_PICKED", "SLIDE", "BEND",
                 "HARMONIC", "LEGATO", "STACCATO", "SUSTAIN", "UNKNOWN"}
MUSICAL_ROLES = {"RHYTHM_GUITAR", "LEAD_GUITAR", "MELODY", "CHORDS",
                 "ARPEGGIO", "BASS_LINE", "TEXTURE", "UNKNOWN"}
STYLES = {"POP_PUNK", "PUNK_ROCK", "SKATE_PUNK", "ALTERNATIVE_ROCK",
          "POWER_POP", "POP_ROCK", "EMO", "POST_HARDCORE",
          "HARD_ROCK", "INDIE_ROCK", "ACOUSTIC_POP", "OTHER", "UNKNOWN"}
STRUCTURE_SECTIONS = {"INTRO", "VERSE", "PRE_CHORUS", "CHORUS", "POST_CHORUS",
                      "BRIDGE", "BREAKDOWN", "SOLO", "INTERLUDE", "OUTRO",
                      "FILL", "TURNAROUND", "UNKNOWN"}
TONALITY_FIELDS = {"key_candidate", "mode_candidate", "tuning_candidate",
                   "root_note_candidate", "chord_quality_candidate"}
TEMPO_FIELDS = {"bpm_candidate", "tempo_min_candidate", "tempo_max_candidate",
                "meter_candidate", "beat_unit_candidate", "groove_candidate"}
REVIEW_STATES = {"NEEDS_MUSICAL_REVIEW", "REVIEWED", "REJECTED"}
LICENSE_STATES = {"UNREVIEWED", "LICENSE_APPROVED", "LICENSE_RESTRICTED",
                  "LICENSE_UNKNOWN"}


def empty_profile(asset_id: str, source_path: str, source_sha256: str) -> dict[str, Any]:
    """Create a complete profile with unknowns explicit rather than fabricated."""
    return {
        "schema_version": SCHEMA_VERSION,
        "asset_id": asset_id,
        "source": {"path": source_path, "sha256": source_sha256},
        "asset_roles": [{"value": "UNKNOWN", "confidence": None, "evidence": []}],
        "instrument_family": {"value": "UNKNOWN", "confidence": None, "evidence": []},
        "tone_families": [{"value": "UNKNOWN", "confidence": None, "evidence": []}],
        "articulations": [{"value": "UNKNOWN", "confidence": None, "evidence": []}],
        "musical_roles": [{"value": "UNKNOWN", "confidence": None, "evidence": []}],
        "styles": [{"value": "UNKNOWN", "confidence": None, "evidence": []}],
        "tonality": {field: None for field in TONALITY_FIELDS},
        "timing": {field: None for field in TEMPO_FIELDS},
        "structure": [],
        "relationships": [],
        "review_status": "NEEDS_MUSICAL_REVIEW",
        "license_status": "UNREVIEWED",
        "proposed_destination": None,
        "automatic_destructive_action": "NONE"
    }


def validate_profile(profile: dict[str, Any]) -> list[str]:
    """Return validation errors; no values are silently normalized or invented."""
    errors: list[str] = []
    if profile.get("schema_version") != SCHEMA_VERSION:
        errors.append("Unsupported or missing schema_version")
    if profile.get("review_status") not in REVIEW_STATES:
        errors.append("Invalid review_status")
    if profile.get("license_status") not in LICENSE_STATES:
        errors.append("Invalid license_status")
    if profile.get("automatic_destructive_action") != "NONE":
        errors.append("Destructive actions are forbidden")
    if not isinstance(profile.get("source"), dict) or not profile["source"].get("sha256"):
        errors.append("Source SHA-256 is required")

    dimensions = {
        "asset_roles": ASSET_ROLES,
        "tone_families": TONE_FAMILIES,
        "articulations": ARTICULATIONS,
        "musical_roles": MUSICAL_ROLES,
        "styles": STYLES,
    }
    for field, allowed in dimensions.items():
        values = profile.get(field)
        if not isinstance(values, list) or not values:
            errors.append(f"{field} must be a non-empty list")
            continue
        for item in values:
            if not isinstance(item, dict) or item.get("value") not in allowed:
                errors.append(f"Invalid {field} value")
                continue
            confidence = item.get("confidence")
            if confidence is not None and (not isinstance(confidence, (int, float))
                                           or not 0.0 <= confidence <= 1.0):
                errors.append(f"Invalid confidence in {field}")
    family = profile.get("instrument_family", {})
    if not isinstance(family, dict) or family.get("value") not in INSTRUMENT_FAMILIES:
        errors.append("Invalid instrument_family")
    for section in profile.get("structure", []):
        if section.get("section") not in STRUCTURE_SECTIONS:
            errors.append("Invalid structure section")
        start, end = section.get("start_seconds"), section.get("end_seconds")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)) or start < 0 or end <= start:
            errors.append("Structure section requires valid increasing time bounds")
    for relation in profile.get("relationships", []):
        if relation.get("type") not in {
            "EXACT_BYTE_DUPLICATE", "POSSIBLE_AUDIO_DERIVATIVE", "SAME_RECORDED_PASSAGE",
            "SIMILAR_TIMBRE", "SIMILAR_RHYTHM", "SIMILAR_MELODY",
            "SIMILAR_CHORD_SEQUENCE", "SIMILAR_RIFF", "RELATED_PERFORMANCE"
        }:
            errors.append("Invalid relationship type")
    return errors
