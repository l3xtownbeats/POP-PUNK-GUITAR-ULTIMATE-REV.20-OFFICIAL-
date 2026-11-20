"""Canonical 12-tone pitch map shared by Library Manager and future PPGU VST3.

Enharmonic spellings are aliases of one MIDI pitch class, never extra keys.
All twelve chromatic pitch classes remain playable, including chromatic notes
outside the current key or the currently selected Auto Chords voicing.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SCHEMA = "ppgu.chromatic_pitch_map/1.0.0"
SHARP_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
FLAT_NAMES = ("C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B")
ALIASES = {
    "C": 0, "B#": 0,
    "C#": 1, "DB": 1,
    "D": 2,
    "D#": 3, "EB": 3,
    "E": 4, "FB": 4,
    "F": 5, "E#": 5,
    "F#": 6, "GB": 6,
    "G": 7,
    "G#": 8, "AB": 8,
    "A": 9,
    "A#": 10, "BB": 10,
    "B": 11, "CB": 11,
}
ENHARMONIC_NAMES = (
    ("C", "B#"), ("C#", "Db"), ("D",), ("D#", "Eb"),
    ("E", "Fb"), ("F", "E#"), ("F#", "Gb"), ("G",),
    ("G#", "Ab"), ("A",), ("A#", "Bb"), ("B", "Cb"),
)
KEYS_PREFER_FLATS = {
    "F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb",
    "Dm", "Gm", "Cm", "Fm", "Bbm", "Ebm", "Abm",
}


def midi_pitch_class(midi_note: int) -> int:
    if type(midi_note) is not int or not 0 <= midi_note <= 127:
        raise ValueError("MIDI note must be an integer from 0 to 127")
    return midi_note % 12


def normalize_note_name(note_name: str) -> int:
    """Return canonical pitch class; C# and Db resolve to the same integer."""
    value = str(note_name).strip().upper().replace("♯", "#").replace("♭", "B")
    if value not in ALIASES:
        raise ValueError(f"Unsupported note spelling: {note_name!r}")
    return ALIASES[value]


def spelling_for_key(key_name: str | None, spelling: str = "key") -> str:
    mode = str(spelling).strip().casefold()
    if mode in {"sharp", "flat"}:
        return mode
    if mode != "key":
        raise ValueError("spelling must be 'sharp', 'flat' or 'key'")
    key = str(key_name or "C").strip()
    return "flat" if key in KEYS_PREFER_FLATS else "sharp"


def note_name_for_pitch_class(pitch_class: int, *, key_name: str | None = None, spelling: str = "key") -> str:
    if type(pitch_class) is not int or not 0 <= pitch_class <= 11:
        raise ValueError("pitch_class must be an integer from 0 to 11")
    names = FLAT_NAMES if spelling_for_key(key_name, spelling) == "flat" else SHARP_NAMES
    return names[pitch_class]


def canonical_pitch_classes(values: list[int | str]) -> list[int]:
    """Normalize and deduplicate pitch classes; never discard a distinct semitone."""
    result = set()
    for value in values:
        if isinstance(value, str):
            result.add(normalize_note_name(value))
        elif type(value) is int and 0 <= value <= 11:
            result.add(value)
        else:
            raise ValueError(f"Invalid pitch class: {value!r}")
    return sorted(result)


def chromatic_note_table(*, key_name: str | None = None, spelling: str = "key") -> list[dict[str, Any]]:
    mode = spelling_for_key(key_name, spelling)
    names = FLAT_NAMES if mode == "flat" else SHARP_NAMES
    return [
        {
            "pitch_class": pc,
            "canonical_name": names[pc],
            "enharmonic_aliases": list(ENHARMONIC_NAMES[pc]),
            "midi_notes": list(range(pc, 128, 12)),
            "required_for_playback": True,
            "runtime_status": "REQUIRES_APPROVED_SAMPLE_OR_VERIFIED_FALLBACK",
        }
        for pc in range(12)
    ]


def build_chromatic_pitch_map(
    catalog: dict[str, Any] | None = None,
    *,
    midi_min: int = 0,
    midi_max: int = 127,
    key_name: str | None = None,
    spelling: str = "key",
    max_fallback_semitones: int = 5,
) -> dict[str, Any]:
    """Build a manifest for every key; source coverage remains approval-gated.

    A missing exact sample gets a fallback proposal only. It is never marked
    playable until the VST3 fallback renderer and audio QA are implemented.
    """
    if type(midi_min) is not int or type(midi_max) is not int or not 0 <= midi_min <= midi_max <= 127:
        raise ValueError("MIDI range must satisfy 0 <= minimum <= maximum <= 127")
    if type(max_fallback_semitones) is not int or not 0 <= max_fallback_semitones <= 12:
        raise ValueError("max_fallback_semitones must be from 0 to 12")
    mode = spelling_for_key(key_name, spelling)
    assets = []
    for section in (catalog or {}).get("modes", []):
        if section.get("mode") not in {"SAMPLE MODE", "MELODY MODE"}:
            continue
        for asset in section.get("assets", []):
            note = asset.get("confirmed_midi_note")
            if (
                type(note) is int and 0 <= note <= 127
                and asset.get("playable") is True
                and asset.get("review_status") == "REVIEWED"
                and asset.get("license_status") == "LICENSE_APPROVED"
                and asset.get("integrity_status") == "VERIFIED"
                and asset.get("asset_file")
            ):
                assets.append(asset)

    rows = []
    for midi_note in range(midi_min, midi_max + 1):
        exact = [asset for asset in assets if asset["confirmed_midi_note"] == midi_note]
        pc = midi_pitch_class(midi_note)
        name = note_name_for_pitch_class(pc, key_name=key_name, spelling=mode)
        if exact:
            rows.append({
                "midi_note": midi_note, "pitch_class": pc, "note_name": name,
                "status": "EXACT_APPROVED_SAMPLE", "runtime_ready_in_catalog": True,
                "asset_ids": sorted({asset["asset_id"] for asset in exact}),
                "source_midi_note": midi_note, "pitch_shift_semitones": 0,
            })
            continue
        nearest = min(assets, key=lambda asset: (abs(asset["confirmed_midi_note"] - midi_note), asset["asset_id"]), default=None)
        distance = abs(nearest["confirmed_midi_note"] - midi_note) if nearest else None
        if nearest is not None and distance is not None and 0 < distance <= max_fallback_semitones:
            rows.append({
                "midi_note": midi_note, "pitch_class": pc, "note_name": name,
                "status": "FALLBACK_PROPOSAL_REQUIRES_QA", "runtime_ready_in_catalog": False,
                "asset_ids": [nearest["asset_id"]], "source_midi_note": nearest["confirmed_midi_note"],
                "pitch_shift_semitones": midi_note - nearest["confirmed_midi_note"],
            })
        else:
            rows.append({
                "midi_note": midi_note, "pitch_class": pc, "note_name": name,
                "status": "SOURCE_MISSING", "runtime_ready_in_catalog": False,
                "asset_ids": [], "source_midi_note": None, "pitch_shift_semitones": None,
            })

    return {
        "schema": SCHEMA,
        "project": "POP PUNK GUITAR ULTIMATE",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "key_context": {"key_name": key_name, "display_spelling": mode},
        "midi_range": {"min": midi_min, "max": midi_max},
        "all_12_chromatic_pitch_classes_required": True,
        "enharmonic_aliases_are_merged": True,
        "autochords_uses_same_pitch_class_map": True,
        "autochords_policy": "NORMALIZE_ENHARMONIC_NAMES_KEEP_ALL_12_CHROMATIC_CLASSES",
        "pitch_classes": chromatic_note_table(key_name=key_name, spelling=mode),
        "midi_note_map": rows,
        "coverage": {
            "midi_key_count": len(rows),
            "exact_approved_sample_count": sum(row["status"] == "EXACT_APPROVED_SAMPLE" for row in rows),
            "fallback_proposal_count": sum(row["status"] == "FALLBACK_PROPOSAL_REQUIRES_QA" for row in rows),
            "missing_source_count": sum(row["status"] == "SOURCE_MISSING" for row in rows),
            "silent_key_policy": "NO_SILENT_KEYS_AFTER_VST3_RUNTIME_FALLBACK_QA",
        },
        "runtime_status": "MANIFEST_ONLY_VST3_PLAYBACK_ENGINE_REQUIRED",
        "safety": {
            "unreviewed_assets_promoted": False,
            "license_gate_preserved": True,
            "whole_chord_wav_transposition_allowed": False,
            "source_assets_modified": False,
        },
    }
