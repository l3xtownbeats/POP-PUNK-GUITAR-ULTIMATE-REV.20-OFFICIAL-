#!/usr/bin/env python3
"""Explicit human-review annotation for staged guitar assets.

This tool adds the three primary FACTORY folder tags only when a reviewer
supplies them deliberately. It never infers tags, approves a license, edits
audio, or copies an asset into FACTORY.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from factory_curator import INSTRUMENTS, ROLES, TONES, sha256_file


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def annotate_manifest(manifest_path: Path, staging_root: Path, *,
                      instrument_family: str, asset_role: str,
                      tone_family: str, reviewed_by: str,
                      confirm_musical_review: bool = False) -> dict[str, Any]:
    """Write explicit primary tags and mark musical review complete.

    License state is intentionally preserved and must be reviewed separately.
    """
    manifest_path = manifest_path.resolve()
    staging_root = staging_root.resolve()
    if not _inside(manifest_path, staging_root) or not manifest_path.is_file():
        raise ValueError("Manifest must be an existing file inside LibraryManager/staging")
    if not confirm_musical_review:
        raise ValueError("Pass the explicit musical-review confirmation flag")
    if not reviewed_by.strip():
        raise ValueError("reviewed_by must identify the human reviewer")
    if instrument_family not in INSTRUMENTS:
        raise ValueError(f"Unsupported instrument_family: {instrument_family}")
    if asset_role not in ROLES:
        raise ValueError(f"Unsupported asset_role: {asset_role}")
    if tone_family not in TONES:
        raise ValueError(f"Unsupported tone_family: {tone_family}")

    record = json.loads(manifest_path.read_text(encoding="utf-8"))
    if record.get("review_status") == "REJECTED":
        raise ValueError("Rejected asset cannot be marked reviewed")
    source = Path(record.get("derived_path", ""))
    if not source.is_absolute():
        source = (manifest_path.parent / source).resolve()
    if not _inside(source, staging_root) or not source.is_file():
        raise ValueError("Derived WAV must exist inside LibraryManager/staging")
    if source.suffix.lower() not in {".wav", ".wave"}:
        raise ValueError("Only staged WAV assets can be annotated")
    expected = str(record.get("derived_sha256", "")).upper()
    if not expected or sha256_file(source) != expected:
        raise ValueError("Derived WAV SHA-256 does not match its manifest")

    tags = record.get("musical_metadata") or {}
    if not isinstance(tags, dict):
        raise ValueError("musical_metadata must be an object")
    tags = dict(tags)
    tags.update({
        "instrument_family": instrument_family,
        "asset_role": asset_role,
        "tone_family": tone_family,
    })
    record["musical_metadata"] = tags
    record["review_status"] = "REVIEWED"
    record["musical_tag_review"] = {
        "status": "HUMAN_CONFIRMED",
        "reviewed_by": reviewed_by.strip(),
        "reviewed_at_utc": datetime.now(timezone.utc).isoformat(),
        "fields": ["instrument_family", "asset_role", "tone_family"],
        "automatic_inference_used": False,
    }
    # Deliberately do not change license_status.
    payload = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
    fd, temporary_name = tempfile.mkstemp(prefix=manifest_path.name + ".",
                                          suffix=".tmp", dir=manifest_path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, manifest_path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
    return {
        "manifest_path": str(manifest_path),
        "review_status": record["review_status"],
        "license_status": record.get("license_status", "UNREVIEWED"),
        "musical_metadata": tags,
        "promotion_ready": record.get("license_status") == "LICENSE_APPROVED",
        "automatic_destructive_action": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply explicitly human-confirmed primary musical tags to a staged asset manifest."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--staging", type=Path,
                        default=Path(__file__).resolve().parent / "staging")
    parser.add_argument("--instrument", choices=sorted(INSTRUMENTS), required=True)
    parser.add_argument("--role", choices=sorted(ROLES), required=True)
    parser.add_argument("--tone", choices=sorted(TONES), required=True)
    parser.add_argument("--reviewed-by", required=True)
    parser.add_argument("--confirm-musical-review", action="store_true",
                        help="Confirm that the staged audio and these tags were actually listened to/reviewed")
    args = parser.parse_args()
    result = annotate_manifest(
        args.manifest, args.staging,
        instrument_family=args.instrument, asset_role=args.role,
        tone_family=args.tone, reviewed_by=args.reviewed_by,
        confirm_musical_review=args.confirm_musical_review,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
