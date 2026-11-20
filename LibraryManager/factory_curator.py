#!/usr/bin/env python3
"""Review-gated, copy-only promotion from LibraryManager staging to SAMPLES/FACTORY.

A single canonical folder path is selected from approved primary tags. Other
verified tags stay in the sidecar manifest for search; files are never moved,
overwritten, deduplicated by similarity, or silently promoted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any


INSTRUMENTS = {
    "ELECTRIC_GUITAR", "ACOUSTIC_GUITAR", "NYLON_GUITAR",
    "STEEL_STRING_GUITAR", "BASS_GUITAR"
}
ROLES = {
    "ONE_SHOT", "INDIVIDUAL_NOTE", "CHORD", "NOTE_SEQUENCE",
    "MELODIC_PHRASE", "RHYTHMIC_MELODY", "RHYTHM_PATTERN", "RIFF",
    "CONFIRMED_LOOP", "GUITAR_LOOP", "MELODY_PART", "POWER_CHORD",
    "PALM_MUTE", "ARPEGGIO", "LEAD_GUITAR", "RHYTHM_GUITAR",
    "MULTI_HIT", "SUSTAIN", "AMBIENCE_OR_FX"
}
STYLES = {
    "POP_PUNK", "PUNK_ROCK", "ALTERNATIVE_ROCK", "MELODIC_PUNK",
    "SKATE_PUNK", "EMO_POP_ROCK"
}
TONES = {
    "CLEAN", "EDGE_OF_BREAKUP", "CRUNCH", "OVERDRIVE", "DISTORTION",
    "FUZZ", "ACOUSTIC_NATURAL", "PROCESSED", "DI"
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _primary_value(metadata: dict[str, Any], field: str, allowed: set[str]) -> str:
    value = metadata.get(field)
    if isinstance(value, dict):
        value = value.get("value")
    if value not in allowed:
        raise ValueError(f"Approved primary {field} must be one of: {', '.join(sorted(allowed))}")
    return value


def promotion_plan(manifest_path: Path, factory_root: Path,
                   staging_root: Path) -> dict[str, Any]:
    manifest_path = manifest_path.resolve()
    staging_root = staging_root.resolve()
    factory_root = factory_root.resolve()
    if not _inside(manifest_path, staging_root):
        raise ValueError("Manifest must be inside LibraryManager/staging")
    record = json.loads(manifest_path.read_text(encoding="utf-8"))
    if record.get("review_status") not in {
        "REVIEWED", "BOUNDARIES_USER_OR_REVIEWER_APPROVED"
    }:
        raise ValueError("Musical boundaries/content must be reviewed before FACTORY promotion")
    if record.get("license_status") != "LICENSE_APPROVED":
        raise ValueError("License must explicitly be LICENSE_APPROVED")
    tags = record.get("musical_metadata") or {}
    if not isinstance(tags, dict) or not str(tags.get("license_evidence", "")).strip():
        raise ValueError("Explicit license evidence is required")
    if not str(tags.get("musical_review_notes", "")).strip():
        raise ValueError("Musical review notes are required")
    validation = record.get("review_validation") or {}
    if not all(validation.get(key) is True for key in (
        "source_sha256_verified", "derived_sha256_verified",
        "sample_boundaries_verified", "explicit_musical_approval",
        "explicit_license_approval",
    )):
        raise ValueError("Explicit review/license validation evidence is missing")
    source = Path(record.get("derived_path", ""))
    if not source.is_absolute():
        source = (manifest_path.parent / source).resolve()
    if not _inside(source, staging_root) or not source.is_file():
        raise ValueError("Derived WAV must exist inside LibraryManager/staging")
    if source.suffix.lower() not in {".wav", ".wave"}:
        raise ValueError("Only staged WAV assets can be promoted")
    expected_hash = str(record.get("derived_sha256", "")).upper()
    if not expected_hash or sha256_file(source) != expected_hash:
        raise ValueError("Staged asset SHA-256 does not match its manifest")

    tags = record.get("musical_metadata", {})
    if not isinstance(tags, dict):
        raise ValueError("musical_metadata must be an object")
    style = _primary_value(tags, "style_family", STYLES)
    instrument = _primary_value(tags, "instrument_family", INSTRUMENTS)
    role = _primary_value(tags, "asset_role", ROLES)
    tone = _primary_value(tags, "tone_family", TONES)
    format_family = "WAV"
    destination_dir = factory_root / style / format_family / instrument / role / tone
    destination = destination_dir / source.name
    return {
        "source_path": str(source),
        "source_sha256": expected_hash,
        "factory_root": str(factory_root),
        "destination_path": str(destination),
        "group_path": f"{style}/{format_family}/{instrument}/{role}/{tone}",
        "all_tags": tags,
        "promotion_status": "READY_FOR_EXPLICIT_APPROVAL",
        "operation": "COPY_ONLY",
        "automatic_destructive_action": "NONE"
    }


def promote_asset(manifest_path: Path, factory_root: Path, staging_root: Path,
                  *, approve: bool = False) -> dict[str, Any]:
    plan = promotion_plan(manifest_path, factory_root, staging_root)
    if not approve:
        return plan
    source = Path(plan["source_path"])
    destination = Path(plan["destination_path"])
    destination_dir = destination.parent
    destination_dir.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing FACTORY asset: {destination}")
    sidecar = destination.with_suffix(destination.suffix + ".json")
    if sidecar.exists():
        raise FileExistsError(f"Refusing to overwrite existing FACTORY manifest: {sidecar}")
    created_destination = False
    # Exclusive creation prevents accidental replacement of an existing file.
    try:
        with source.open("rb") as src, destination.open("xb") as dst:
            created_destination = True
            shutil.copyfileobj(src, dst, length=1024 * 1024)
        copied_hash = sha256_file(destination)
        if copied_hash != plan["source_sha256"]:
            destination.unlink()
            raise IOError("Copied asset hash mismatch; incomplete copy was removed")
        sidecar_record = {
            "factory_asset_path": str(destination),
            "factory_sha256": copied_hash,
            "staging_manifest": str(Path(manifest_path).resolve()),
            "source_sha256": plan["source_sha256"],
            "group_path": plan["group_path"],
            "musical_metadata": plan["all_tags"],
            "promotion_operation": "COPY_ONLY",
            "review_status": "REVIEWED",
            "license_status": "LICENSE_APPROVED",
            "automatic_destructive_action": "NONE"
        }
        with sidecar.open("x", encoding="utf-8") as stream:
            json.dump(sidecar_record, stream, ensure_ascii=False, indent=2)
        return {**plan, "promotion_status": "COPIED_TO_FACTORY",
                "factory_sha256": copied_hash, "sidecar_path": str(sidecar)}
    except Exception:
        # Remove only a partial file created by this invocation, never the source.
        if created_destination and destination.exists():
            destination.unlink()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Review-gated copy of approved staged WAV assets into SAMPLES/FACTORY.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--staging", type=Path,
                        default=Path(__file__).resolve().parent / "staging")
    parser.add_argument("--factory", type=Path, required=True,
                        help="Path to SAMPLES/FACTORY")
    parser.add_argument("--approve", action="store_true",
                        help="Explicitly perform the copy after all review/license gates pass")
    args = parser.parse_args()
    result = promote_asset(args.manifest, args.factory, args.staging, approve=args.approve)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
