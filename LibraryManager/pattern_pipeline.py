#!/usr/bin/env python3
"""End-to-end first-pass WAV -> rhythm evidence -> PATTERN MODE candidates.

This is an intermediate, review-only preparation tool. It does not extract or
modify audio, recognize chords/notes, or claim musical section labels.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from audio_analysis import analyse_wav
from rhythm_analysis import analyze_rhythm
from pattern_candidate_analyzer import find_repeating_patterns

VERSION = "0.1.0"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def build_pattern_report(acoustic_report: dict[str, Any]) -> dict[str, Any]:
    """Compose the existing acoustic/rhythm analyzers into one pattern report."""
    rhythm = analyze_rhythm(acoustic_report)
    patterns = find_repeating_patterns(rhythm)
    return {
        "pipeline_version": VERSION,
        "engine_target": "PATTERN_MODE_PREPARATION",
        "source": acoustic_report.get("source"),
        "source_sha256": acoustic_report.get("source_sha256"),
        "duration_seconds": acoustic_report.get("duration_seconds"),
        "acoustic_evidence": {
            "onset_count": rhythm["onset_count"],
            "onset_evidence_seconds": rhythm["onset_evidence_seconds"],
            "tempo_candidates": rhythm["tempo_candidates"],
            "rhythmic_regularity_candidate": rhythm["rhythmic_regularity_candidate"],
            "rhythm_descriptor": rhythm["rhythm_descriptor"],
        },
        "rhythm_analysis": rhythm,
        "pattern_analysis": patterns,
        "review_status": "NEEDS_MUSICAL_REVIEW",
        "license_status": "UNREVIEWED",
        "source_audio_modified": False,
        "source_audio_copied": False,
        "limitations": [
            "This pipeline starts from acoustic onset candidates; it does not verify that the input contains guitar only.",
            "The required CLI confirmation is an operator assertion, not an automatic Piano/Bell/Drum classifier.",
            "Repeated onset intervals are timing motifs, not confirmed riffs, bars, loops or musical sections.",
            "No chord, note, key, meter, downbeat, articulation, playing technique or Intro/Verse/Chorus/Bridge/Ending label is inferred.",
            "No audio is sliced, copied, moved or modified; all candidates refer to original source offsets.",
            "Chord-adaptive Pattern Instrument playback and note-playable mappings require later reviewed event extraction and VST engine work."
        ],
    }


def analyze_pattern_wav(source: Path, *, guitar_source_confirmed: bool = False) -> dict[str, Any]:
    source = Path(source).resolve()
    if not guitar_source_confirmed:
        raise ValueError(
            "Confirm that the source has passed the approved guitar-only filter before analysis"
        )
    acoustic = analyse_wav(source)
    acoustic["source_sha256"] = sha256_file(source)
    result = build_pattern_report(acoustic)
    result["operator_guitar_source_confirmation"] = True
    result["confirmation_scope"] = "MANUAL_ASSERTION_NOT_AUTOMATIC_CLASSIFICATION"
    # Detect accidental source mutation during analysis.
    if sha256_file(source) != acoustic["source_sha256"]:
        raise RuntimeError("Source WAV changed during analysis")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare review-only repeated rhythm candidates for PATTERN MODE."
    )
    parser.add_argument("wav", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--guitar-source-confirmed", action="store_true",
        help="Operator confirms upstream filtering excluded Piano, Bell and Drum."
    )
    args = parser.parse_args()
    report = analyze_pattern_wav(
        args.wav, guitar_source_confirmed=args.guitar_source_confirmed
    )
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
