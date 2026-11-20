#!/usr/bin/env python3
"""Conservative guitar voicing hypotheses for the PPGU Manager.

Voicings are generated from pitch-class hypotheses and an explicitly declared
tuning. The default is standard EADGBE only as an assumption; every result
requires tuning and physical fingering review before it can be used as truth.
"""
from __future__ import annotations

from itertools import product
from typing import Any

NOTE_TO_PC = {
    "C": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3,
    "E": 4, "F": 5, "F#": 6, "GB": 6, "G": 7, "G#": 8,
    "AB": 8, "A": 9, "A#": 10, "BB": 10, "B": 11,
}
STANDARD_EADGBE_OPEN_MIDI = (40, 45, 50, 55, 59, 64)  # strings 6 -> 1
NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def _pitch_class(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    token = value.strip().upper().replace("♯", "#").replace("♭", "B")
    # Strip octave digits if the analyzer supplied a note name with octave.
    while token and token[-1].isdigit():
        token = token[:-1]
    return NOTE_TO_PC.get(token)


def generate_voicing_candidates(
    chord_candidate: dict[str, Any],
    *,
    tuning_open_midi: tuple[int, ...] = STANDARD_EADGBE_OPEN_MIDI,
    max_fret: int = 12,
    max_fret_span: int = 4,
    min_strings: int | None = None,
    max_candidates: int = 24,
) -> dict[str, Any]:
    """Enumerate playable fretboard note combinations for a chord hypothesis."""
    if len(tuning_open_midi) != 6 or any(not isinstance(note, int) or not 0 <= note <= 127 for note in tuning_open_midi):
        raise ValueError("tuning_open_midi must contain six valid MIDI open-string notes")
    if not 0 <= max_fret <= 24 or not 0 <= max_fret_span <= 12:
        raise ValueError("Invalid fretboard limits")
    if not 1 <= max_candidates <= 128:
        raise ValueError("max_candidates must be between 1 and 128")

    pitch_classes = sorted({
        pc for pc in (_pitch_class(value) for value in chord_candidate.get("pitch_classes_candidate", []))
        if pc is not None
    })
    quality = str(chord_candidate.get("quality") or "UNKNOWN").upper()
    root_pc = _pitch_class(chord_candidate.get("root_pitch_class"))
    if not pitch_classes or root_pc is None or root_pc not in pitch_classes:
        return {
            "generator_version": "0.1.0",
            "candidate_count": 0,
            "voicing_candidates": [],
            "reason": "Chord root or pitch-class hypothesis is incomplete.",
            "tuning_open_midi": list(tuning_open_midi),
            "tuning_status": "NEEDS_CONFIRMATION",
        }

    required_strings = min_strings or (2 if quality == "POWER5" else 3)
    required_unique_tones = 2 if quality == "POWER5" else min(3, len(pitch_classes))
    choices = []
    for open_note in tuning_open_midi:
        string_choices = [None]
        for fret in range(max_fret + 1):
            if (open_note + fret) % 12 in pitch_classes:
                string_choices.append(fret)
        choices.append(string_choices)

    scored = []
    for frets in product(*choices):
        sounding = [
            (string_index, fret, tuning_open_midi[string_index] + fret)
            for string_index, fret in enumerate(frets) if fret is not None
        ]
        if len(sounding) < required_strings:
            continue
        tones = {midi % 12 for _, _, midi in sounding}
        if len(tones) < required_unique_tones:
            continue
        fret_values = [fret for _, fret, _ in sounding if fret > 0]
        span = max(fret_values) - min(fret_values) if fret_values else 0
        if span > max_fret_span:
            continue
        midi_notes = [midi for _, _, midi in sounding]
        bass_pc = min(midi_notes) % 12
        root_bass_penalty = 0 if bass_pc == root_pc else 1
        max_used_fret = max((fret for _, fret, _ in sounding), default=0)
        fret_sum = sum(fret for _, fret, _ in sounding)
        # Favor root-position bass, compact hand span and fewer high frets.
        score = (root_bass_penalty, span, max_used_fret, fret_sum, -len(sounding))
        scored.append((score, frets, sounding, span, tones))

    scored.sort(key=lambda item: (item[0], tuple(-1 if fret is None else fret for fret in item[1])))
    candidates = []
    for index, (_score, frets, sounding, span, tones) in enumerate(scored[:max_candidates], 1):
        string_positions = []
        for string_index, fret in enumerate(frets):
            string_positions.append({
                "string_number": 6 - string_index,
                "fret_number": fret,
                "midi_note_candidate": (
                    tuning_open_midi[string_index] + fret if fret is not None else None
                ),
            })
        candidates.append({
            "voicing_candidate_id": f"VOICING-{index:03d}",
            "string_positions_6_to_1": string_positions,
            "midi_notes_candidate": [midi for _, _, midi in sounding],
            "pitch_classes_candidate": [NOTE_NAMES[pc] for pc in sorted(tones)],
            "sounding_string_count": len(sounding),
            "fret_span_candidate": span,
            "root_position_bass_candidate": min(midi for _, _, midi in sounding) % 12 == root_pc,
            "fingering_candidate": "UNKNOWN",
            "barre_candidate": "UNKNOWN",
            "physical_playability_status": "NEEDS_HUMAN_REVIEW",
            "review_status": "NEEDS_MUSICAL_REVIEW",
            "license_status": "UNREVIEWED",
        })

    return {
        "generator_version": "0.1.0",
        "candidate_count": len(candidates),
        "voicing_candidates": candidates,
        "chord_name_candidate": chord_candidate.get("chord_name_candidate"),
        "root_pitch_class_candidate": chord_candidate.get("root_pitch_class"),
        "quality_candidate": quality,
        "pitch_classes_candidate": [NOTE_NAMES[pc] for pc in pitch_classes],
        "tuning_open_midi": list(tuning_open_midi),
        "tuning_name_candidate": "STANDARD_EADGBE",
        "tuning_status": "NEEDS_CONFIRMATION",
        "max_fret": max_fret,
        "max_fret_span": max_fret_span,
        "physical_fingering_review_required": True,
        "limitations": [
            "Input chord is an experimental pitch-class hypothesis, not verified transcription.",
            "Standard EADGBE is an explicit default assumption, not a confirmed instrument tuning.",
            "Finger assignments, barre feasibility, hand stretch, string muting and ergonomics are not solved.",
            "Every generated shape is a candidate and requires listening plus guitarist review.",
        ],
    }
