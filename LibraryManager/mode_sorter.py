"""Conservative mapping of analyzed guitar assets to approved PPGU VST3 modes.

The sorter emits review candidates only. It never claims uncertain musical roles,
never promotes assets to FACTORY, and never edits or relocates source audio.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from voicing_generator import generate_voicing_candidates

SORTER_VERSION = "1.1.0"
MAX_CHORD_HYPOTHESES_PER_FILE = 25

MODE_ORDER = (
    "SAMPLE MODE", "STRUMMING", "ARPEGGIO", "PATTERN MODE", "RIFF MODE",
    "MELODY MODE", "PHRASE MODE", "ONE PITCH", "ARTICULATIONS", "ENDING",
)

MODE_PURPOSES = {
    "SAMPLE MODE": "Individual notes, one-shots and reviewed chord/power-chord samples.",
    "STRUMMING": "Reviewed downstroke, upstroke and chord-strumming patterns.",
    "ARPEGGIO": "Generated chord voicing hypotheses and reviewed individual-string attack events.",
    "PATTERN MODE": "Verified repeating rhythmic patterns with preserved timing.",
    "RIFF MODE": "Musically reviewed guitar riffs and characteristic fragments.",
    "MELODY MODE": "Melodic note sequences supported by pitch-event evidence.",
    "PHRASE MODE": "Irregular or complete phrase candidates requiring listening review.",
    "ONE PITCH": "Rhythmic sequences verified to remain on one pitch.",
    "ARTICULATIONS": "Reviewed Palm Mute, Open, Slide, Legato and related articulations.",
    "ENDING": "Reviewed musical endings and outro phrases.",
}

_MANUAL_ONLY = {
    "STRUMMING": "Requires human confirmation of strum direction and chord performance.",
    "ARPEGGIO": "Generated voicings require tuning/fingering review; envelope analysis alone is insufficient.",
    "ARTICULATIONS": "Requires listening review; Palm Mute/Open/Slide/Legato are not inferred from filename or RMS.",
    "ENDING": "Requires musical-context review; an isolated fragment is not automatically an ending.",
}


def _frames(record: dict[str, Any]) -> tuple[int | None, int | None, int | None]:
    acoustic = record.get("acoustic_analysis") or {}
    rate = acoustic.get("sample_rate")
    total = acoustic.get("total_frames")
    if not isinstance(total, int) or total <= 0:
        duration = acoustic.get("duration_seconds")
        if isinstance(duration, (int, float)) and isinstance(rate, int) and rate > 0:
            total = int(round(float(duration) * rate))
    if not isinstance(rate, int) or rate <= 0:
        rate = None
    if not isinstance(total, int) or total <= 0:
        total = None
    return rate, total, acoustic.get("duration_seconds")


def _candidate(record: dict[str, Any], mode: str, candidate_type: str,
               start: int | None, end: int | None, *, status: str,
               evidence: list[str], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    result = {
        "source_path": record.get("source_path", ""),
        "source_sha256": record.get("source_sha256", ""),
        "candidate_type": candidate_type,
        "target_mode": mode,
        "source_start_sample": start,
        "source_end_sample": end,
        "review_status": "NEEDS_MUSICAL_REVIEW",
        "license_status": "UNREVIEWED",
        "mode_assignment_status": status,
        "evidence": evidence,
        "automatic_factory_promotion": False,
        "source_modified": False,
    }
    if extra:
        result.update(extra)
    return result


def build_mode_sorting_report(audio_reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Build all ten mode queues from available evidence; unresolved modes stay explicit."""
    queues: dict[str, list[dict[str, Any]]] = {mode: [] for mode in MODE_ORDER}

    for record in audio_reports:
        classification = record.get("classification") or {}
        if not classification:
            # unified_manager may attach pitch candidates directly to the record.
            classification = {}
        acoustic_rate, total_frames, duration = _frames(record)
        subtype = str(classification.get("sample_subtype_candidate") or "UNKNOWN")
        asset_kind = str(classification.get("asset_kind_candidate") or "UNKNOWN")
        features = classification.get("features") or {}
        distinct_pitches = features.get("distinct_pitch_count")
        pitch_events = classification.get("fragment_candidates") or record.get("pitch_candidates") or []

        if asset_kind == "ONE_SHOT" and total_frames:
            queues["SAMPLE MODE"].append(_candidate(
                record, "SAMPLE MODE", "ONE_SHOT_SAMPLE", 0, total_frames,
                status="CANDIDATE_REQUIRES_LISTENING",
                evidence=["Existing classifier proposed a short one-shot; musical identity and boundaries require review."],
                extra={"duration_seconds": duration},
            ))

        if acoustic_rate:
            for event in pitch_events:
                start_s, end_s = event.get("start_seconds"), event.get("end_seconds")
                if not isinstance(start_s, (int, float)) or not isinstance(end_s, (int, float)) or end_s <= start_s:
                    continue
                start = max(0, int(round(start_s * acoustic_rate)))
                end = int(round(end_s * acoustic_rate))
                if total_frames:
                    end = min(end, total_frames)
                if end <= start:
                    continue
                queues["SAMPLE MODE"].append(_candidate(
                    record, "SAMPLE MODE", "PITCH_EVENT_NOTE", start, end,
                    status="PITCH_HYPOTHESIS_REQUIRES_REVIEW",
                    evidence=["Monophonic pitch tracker event; guitar note identity and polyphonic context are unverified."],
                    extra={"midi_note_candidate": event.get("midi_note_candidate"),
                           "note_name_candidate": event.get("note_name_candidate"),
                           "pitch_confidence": event.get("confidence")},
                ))

        # Experimental chord regions are SAMPLE MODE chord/power-chord
        # candidates. They are not verified voicings or string/fret positions.
        chord_report = record.get("chord_analysis") or {}
        for chord in (chord_report.get("chord_candidates", []) or [])[:MAX_CHORD_HYPOTHESES_PER_FILE]:
            start_s, end_s = chord.get("start_seconds"), chord.get("end_seconds")
            if not acoustic_rate or not isinstance(start_s, (int, float)) or not isinstance(end_s, (int, float)) or end_s <= start_s:
                continue
            start = max(0, int(round(start_s * acoustic_rate)))
            end = int(round(end_s * acoustic_rate))
            if total_frames:
                end = min(end, total_frames)
            if end <= start:
                continue
            quality = str(chord.get("quality") or "UNKNOWN").upper()
            candidate_type = "POWER_CHORD_SAMPLE" if quality == "POWER5" else "CHORD_SAMPLE"
            queues["SAMPLE MODE"].append(_candidate(
                record, "SAMPLE MODE", candidate_type, start, end,
                status="CHORD_HYPOTHESIS_REQUIRES_LISTENING",
                evidence=["Experimental spectral/chroma chord hypothesis; not verified transcription or guitar fingering."],
                extra={
                    "chord_name_candidate": chord.get("chord_name_candidate"),
                    "root_pitch_class_candidate": chord.get("root_pitch_class"),
                    "quality_candidate": quality,
                    "pitch_classes_candidate": chord.get("pitch_classes_candidate", []),
                    "pitch_confidence": chord.get("mean_confidence", chord.get("confidence")),
                    "voicing_candidate": "UNKNOWN",
                    "string_fret_positions": None,
                },
            ))
            # Build review-only fretboard shapes from the chord pitch-class
            # hypothesis. Standard EADGBE is an assumption, never confirmed tuning.
            voicing_report = generate_voicing_candidates(chord, max_candidates=8)
            if voicing_report.get("voicing_candidates"):
                queues["ARPEGGIO"].append(_candidate(
                    record, "ARPEGGIO", "ARPEGGIO_VOICING_HYPOTHESIS", start, end,
                    status="GENERATED_VOICING_REQUIRES_GUITAR_REVIEW",
                    evidence=[
                        "Voicing candidates generated from an experimental chord pitch-class hypothesis.",
                        "Standard EADGBE tuning is assumed and must be confirmed; fingerings are not solved.",
                    ],
                    extra={
                        "chord_name_candidate": chord.get("chord_name_candidate"),
                        "root_pitch_class_candidate": chord.get("root_pitch_class"),
                        "quality_candidate": quality,
                        "pitch_classes_candidate": chord.get("pitch_classes_candidate", []),
                        "voicing_candidates": voicing_report["voicing_candidates"],
                        "voicing_candidate_count": voicing_report["candidate_count"],
                        "tuning_name_candidate": voicing_report.get("tuning_name_candidate"),
                        "tuning_status": voicing_report.get("tuning_status"),
                        "tuning_open_midi": voicing_report.get("tuning_open_midi"),
                        "max_fret": voicing_report.get("max_fret"),
                        "max_fret_span": voicing_report.get("max_fret_span"),
                        "physical_fingering_review_required": True,
                    },
                ))

        # Only the repeated-motif extractor can populate Pattern Mode.
        virtual = record.get("virtual_extraction") or {}
        for item in virtual.get("candidates", []) or []:
            start, end = item.get("source_start_sample"), item.get("source_end_sample")
            if not isinstance(start, int) or not isinstance(end, int) or end <= start:
                continue
            queues["PATTERN MODE"].append(_candidate(
                record, "PATTERN MODE", "REPEATED_RHYTHM_PATTERN", start, end,
                status="REPEATED_MOTIF_CANDIDATE_REQUIRES_REVIEW",
                evidence=["Candidate came from repeated-motif analysis; groove, bar boundaries and seamless looping are not confirmed."],
                extra={"candidate_id": item.get("candidate_id"),
                       "start_seconds": item.get("start_seconds"),
                       "end_seconds": item.get("end_seconds")},
            ))

        # Irregular onset groups are phrase candidates, never automatically Pattern.
        irregular = record.get("irregular_phrase_extraction") or {}
        for item in irregular.get("candidates", []) or []:
            start, end = item.get("source_start_sample"), item.get("source_end_sample")
            if not isinstance(start, int) or not isinstance(end, int) or end <= start:
                continue
            phrase = _candidate(
                record, "PHRASE MODE", "IRREGULAR_PHRASE_CANDIDATE", start, end,
                status="PHRASE_IDENTITY_REQUIRES_LISTENING",
                evidence=["Irregular onset-group segmentation; this is not proof of a complete phrase or riff."],
                extra={"candidate_id": item.get("candidate_id"),
                       "onset_count_candidate": item.get("onset_count_candidate"),
                       "tempo_candidate_bpm": None},
            )
            queues["PHRASE MODE"].append(phrase)
            riff_alternative = dict(phrase)
            riff_alternative["target_mode"] = "RIFF MODE"
            riff_alternative["candidate_type"] = "RIFF_OR_PHRASE_REVIEW"
            riff_alternative["mode_assignment_status"] = "AMBIGUOUS_RIFF_OR_PHRASE"
            riff_alternative["evidence"] = ["Same source range is offered for human choice only; the sorter does not assert that it is a riff."]
            queues["RIFF MODE"].append(riff_alternative)

        # Melody is proposed only when multiple distinct pitch hypotheses exist.
        if isinstance(distinct_pitches, int) and distinct_pitches >= 3 and pitch_events and acoustic_rate:
            valid = [event for event in pitch_events
                     if isinstance(event.get("start_seconds"), (int, float))
                     and isinstance(event.get("end_seconds"), (int, float))]
            if valid:
                start = max(0, int(round(min(e["start_seconds"] for e in valid) * acoustic_rate)))
                end = int(round(max(e["end_seconds"] for e in valid) * acoustic_rate))
                if total_frames:
                    end = min(end, total_frames)
                if end > start:
                    queues["MELODY MODE"].append(_candidate(
                        record, "MELODY MODE", "MONOPHONIC_MELODY_HYPOTHESIS", start, end,
                        status="MELODY_REQUIRES_LISTENING",
                        evidence=["Three or more distinct monophonic pitch hypotheses; chords, distortion and tracker errors remain possible."],
                        extra={"pitch_sequence_candidate": features.get("pitch_sequence", [])},
                    ))

        # A single distinct pitch is not enough to claim a rhythmic ONE PITCH part;
        # require repeated attack evidence and retain it as a review-only candidate.
        onset_count = features.get("onset_count")
        if (isinstance(distinct_pitches, int) and distinct_pitches == 1
                and isinstance(onset_count, int) and onset_count >= 3
                and total_frames):
            queues["ONE PITCH"].append(_candidate(
                record, "ONE PITCH", "SINGLE_PITCH_RHYTHM_HYPOTHESIS", 0, total_frames,
                status="ONE_PITCH_REQUIRES_PITCH_AND_RHYTHM_REVIEW",
                evidence=["One distinct monophonic pitch hypothesis and multiple envelope attacks; pitch tracking may be incomplete."],
            ))

        # Strumming and arpeggio are deliberately not inferred from generic onset data.
        # Other unproven modes remain visible in the report with an explicit reason.

    modes = []
    for mode in MODE_ORDER:
        modes.append({
            "mode": mode,
            "purpose": MODE_PURPOSES[mode],
            "candidate_count": len(queues[mode]),
            "candidates": queues[mode],
            "status": "CANDIDATES_REQUIRE_REVIEW" if queues[mode] else "NO_SUPPORTED_CANDIDATES",
            "limitation": _MANUAL_ONLY.get(mode, (
                "Only evidence-backed candidates are listed; absence of candidates does not mean the library contains no such material."
            )),
        })

    return {
        "schema_version": "1.0.0",
        "sorter_version": SORTER_VERSION,
        "project": "POP PUNK GUITAR ULTIMATE",
        "policy": "CONSERVATIVE_CANDIDATES_ONLY",
        "mode_count": len(MODE_ORDER),
        "total_candidates": sum(len(items) for items in queues.values()),
        "modes": modes,
        "safety": {
            "source_files_modified": False,
            "source_files_moved_or_deleted": False,
            "automatic_factory_promotion": False,
            "default_review_status": "NEEDS_MUSICAL_REVIEW",
            "default_license_status": "UNREVIEWED",
            "exact_source_offsets": "SAMPLES/FRAMES_WHEN_EVIDENCE_AVAILABLE",
            "unknown_musical_facts_remain_unknown": True,
        },
    }
