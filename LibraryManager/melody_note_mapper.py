"""Conservative metadata mapping for single-note guitar assets.

No pitch, velocity layer, or articulation is promoted to a confirmed value
without explicit evidence. Candidate values remain review-gated.
"""
from __future__ import annotations

PITCH_CLASS_NAMES = ("C", "C#", "D", "D#", "E", "F",
                     "F#", "G", "G#", "A", "A#", "B")


def map_single_note_candidate(candidate: dict) -> dict:
    """Return a normalized, review-safe map for one detected note event."""
    midi = candidate.get("midi_note_candidate")
    confidence = candidate.get("confidence")
    valid_midi = type(midi) is int and 0 <= midi <= 127
    valid_confidence = (
        isinstance(confidence, (int, float))
        and not isinstance(confidence, bool)
        and 0.0 <= float(confidence) <= 1.0
    )
    confidence_value = float(confidence) if valid_confidence else None
    pitch_class = midi % 12 if valid_midi else None
    octave = midi // 12 - 1 if valid_midi else None

    velocity = candidate.get("velocity")
    velocity_layer = "UNKNOWN"
    if type(velocity) is int and 1 <= velocity <= 127:
        velocity_layer = (
            "LOW" if velocity <= 42 else
            "MEDIUM" if velocity <= 84 else "HIGH"
        )

    articulation = candidate.get("articulation")
    allowed_articulations = {
        "PALM_MUTE", "OPEN", "SLIDE", "LEGATO", "HAMMER_ON",
        "PULL_OFF", "HARMONIC", "UNKNOWN",
    }
    articulation = (
        str(articulation).upper()
        if str(articulation).upper() in allowed_articulations else "UNKNOWN"
    )
    confident = valid_midi and confidence_value is not None and confidence_value >= 0.85
    return {
        "asset_role": "SINGLE_GUITAR_NOTE",
        "one_sound_one_note": True,
        "midi_note_candidate": midi if valid_midi else None,
        "note_name_candidate": candidate.get("note_name_candidate"),
        "pitch_class_index_candidate": pitch_class,
        "pitch_class_name_candidate": PITCH_CLASS_NAMES[pitch_class] if pitch_class is not None else None,
        "octave_candidate": octave,
        "pitch_confidence": confidence_value,
        "pitch_mapping_status": "HIGH_CONFIDENCE_CANDIDATE" if confident else "REQUIRES_REVIEW",
        "velocity_value_candidate": velocity if type(velocity) is int and 1 <= velocity <= 127 else None,
        "velocity_layer_candidate": velocity_layer,
        "articulation_candidate": articulation,
        "review_required": not confident or velocity_layer == "UNKNOWN" or articulation == "UNKNOWN",
    }
