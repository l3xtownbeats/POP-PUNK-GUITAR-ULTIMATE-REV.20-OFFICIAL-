#!/usr/bin/env python3
"""Non-destructive finalization audit for the POP PUNK GUITAR staging library."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from factory_curator import INSTRUMENTS, ROLES, STYLES, TONES
from audio_range_io import audio_source_info


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def finalize_staging(
    staging_root: Path,
    *,
    reports_root: Path | None = None,
    progress=None,
    cancel_event=None,
) -> dict[str, Any]:
    """Verify every staged manifest and report readiness without moving/copying files."""
    staging = Path(staging_root).resolve()
    if not staging.is_dir():
        raise FileNotFoundError(f"Staging directory not found: {staging}")
    manifests_dir = staging / "manifests"
    manifests = sorted(manifests_dir.glob("*.json")) if manifests_dir.is_dir() else []
    report_base = Path(reports_root or (staging.parent / "reports")).resolve()
    report_base.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    report_dir = report_base / f"finalization_{run_id}"
    report_dir.mkdir(parents=True, exist_ok=False)

    rows: list[dict[str, Any]] = []
    source_hash_cache: dict[str, str] = {}
    status_counts: Counter[str] = Counter()
    style_counts: Counter[str] = Counter()
    for index, manifest_path in enumerate(manifests, 1):
        if cancel_event is not None and cancel_event.is_set():
            raise RuntimeError("Finalization audit cancelled; no staged assets were changed.")
        if progress and (index == 1 or index % 25 == 0 or index == len(manifests)):
            progress(f"Финализация: проверено манифестов {index}/{len(manifests)}")
        row: dict[str, Any] = {
            "manifest_path": str(manifest_path),
            "asset_id": "",
            "derived_path": "",
            "status": "INVALID",
            "review_status": "",
            "license_status": "",
            "style_family": "",
            "instrument_family": "",
            "asset_role": "",
            "tone_family": "",
            "format_family": "",
            "error": "",
        }
        try:
            record = json.loads(manifest_path.read_text(encoding="utf-8"))
            row["asset_id"] = record.get("asset_id", "")
            row["review_status"] = record.get("review_status", "")
            row["license_status"] = record.get("license_status", "")
            derived = Path(record.get("derived_path", ""))
            if not derived.is_absolute():
                derived = (manifest_path.parent / derived).resolve()
            row["derived_path"] = str(derived)
            if not _inside(derived, staging) or not derived.is_file():
                raise ValueError("Derived WAV missing or outside staging")
            if derived.suffix.lower() not in {".wav", ".wave"}:
                raise ValueError("Only WAV assets can be finalized")
            expected_derived = str(record.get("derived_sha256", "")).upper()
            if not expected_derived or _sha256(derived) != expected_derived:
                raise ValueError("Derived WAV SHA-256 mismatch")
            source = Path(record.get("source_path", ""))
            expected_source = str(record.get("source_sha256", "")).upper()
            source_key = str(source.resolve())
            if not source.is_file() or not expected_source:
                raise ValueError("Original source missing or SHA-256 mismatch")
            actual_source_hash = source_hash_cache.get(source_key)
            if actual_source_hash is None:
                actual_source_hash = _sha256(source)
                source_hash_cache[source_key] = actual_source_hash
            if actual_source_hash != expected_source:
                raise ValueError("Original source SHA-256 mismatch")
            start = int(record.get("source_start_sample", -1))
            end = int(record.get("source_end_sample", -1))
            if start < 0 or end <= start:
                raise ValueError("Invalid source sample boundaries")
            original_info = audio_source_info(source)
            derived_info = audio_source_info(derived)
            if end > original_info.frames or derived_info.frames != end - start:
                raise ValueError("WAV frame ranges do not match original sample boundaries")
            if derived_info.source_format.upper() != "WAV" or derived_info.source_subtype not in {"PCM_16", "PCM_24", "PCM_32", "PCM_U8", "PCM"}:
                raise ValueError("Derived asset must be uncompressed PCM WAV")
            if derived_info.framerate != original_info.framerate:
                raise ValueError("Derived WAV sample rate differs from original")
            tags = record.get("musical_metadata") or {}
            if not isinstance(tags, dict):
                raise ValueError("musical_metadata must be an object")
            for field in ("style_family", "instrument_family", "asset_role", "tone_family"):
                if tags.get(field) in (STYLES if field == "style_family" else
                                       INSTRUMENTS if field == "instrument_family" else
                                       ROLES if field == "asset_role" else TONES):
                    row[field] = tags[field]
            row["format_family"] = "WAV"
            validation = record.get("review_validation") or {}
            if row["review_status"] != "REVIEWED":
                row["status"] = "MUSICAL_REVIEW_REQUIRED"
            elif row["license_status"] != "LICENSE_APPROVED":
                row["status"] = "LICENSE_REVIEW_REQUIRED"
            else:
                for field, allowed in (
                    ("style_family", STYLES),
                    ("instrument_family", INSTRUMENTS),
                    ("asset_role", ROLES),
                    ("tone_family", TONES),
                ):
                    if tags.get(field) not in allowed:
                        raise ValueError(f"Missing or invalid reviewed tag: {field}")
                if not str(tags.get("license_evidence", "")).strip() or not str(tags.get("musical_review_notes", "")).strip():
                    raise ValueError("Missing explicit license evidence or musical review notes")
                if not all(validation.get(key) is True for key in (
                    "source_sha256_verified", "derived_sha256_verified",
                    "sample_boundaries_verified", "explicit_musical_approval",
                    "explicit_license_approval",
                )):
                    raise ValueError("Missing explicit review/license validation evidence")
                row["status"] = "FACTORY_READY"
                style_counts[row["style_family"]] += 1
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
            if row["status"] == "INVALID" and row["review_status"] == "REVIEWED" and row["license_status"] != "LICENSE_APPROVED":
                row["status"] = "LICENSE_REVIEW_REQUIRED"
        status_counts[row["status"]] += 1
        rows.append(row)

    csv_path = report_dir / "finalization_inventory.csv"
    fields = [
        "manifest_path", "asset_id", "derived_path", "status", "review_status",
        "license_status", "style_family", "instrument_family", "asset_role",
        "tone_family", "format_family", "error",
    ]
    with csv_path.open("x", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    ready = status_counts["FACTORY_READY"]
    summary = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "staging_root": str(staging),
        "report_directory": str(report_dir),
        "manifests_checked": len(manifests),
        "factory_ready_count": ready,
        "musical_review_required_count": status_counts["MUSICAL_REVIEW_REQUIRED"],
        "license_review_required_count": status_counts["LICENSE_REVIEW_REQUIRED"],
        "invalid_count": status_counts["INVALID"],
        "status_counts": dict(status_counts),
        "style_counts_factory_ready": dict(style_counts),
        "factory_distribution_allowed": ready > 0,
        "distribution_executed": False,
        "source_files_modified": False,
        "staged_files_modified": False,
    }
    (report_dir / "finalization_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def audit_factory_library(
    samples_root: Path,
    *,
    reports_root: Path | None = None,
    progress=None,
    cancel_event=None,
) -> dict[str, Any]:
    """Verify distributed FACTORY WAVs and their sidecar provenance records."""
    samples = Path(samples_root).resolve()
    factory = samples / "FACTORY"
    report_base = Path(reports_root or (Path(__file__).resolve().parent / "reports")).resolve()
    report_base.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    report_dir = report_base / f"factory_finalization_{run_id}"
    report_dir.mkdir(parents=True, exist_ok=False)
    fields = [
        "factory_wav", "sidecar", "asset_id", "status", "style_family",
        "instrument_family", "asset_role", "tone_family", "sha256", "error",
    ]
    counts: Counter[str] = Counter()
    rows_written = 0
    csv_path = report_dir / "factory_inventory.csv"
    with csv_path.open("x", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        def record_walk_error(exc: OSError) -> None:
            nonlocal rows_written
            counts["WALK_ERROR"] += 1
            writer.writerow({
                "factory_wav": str(getattr(exc, "filename", "") or factory),
                "sidecar": "",
                "asset_id": "",
                "status": "WALK_ERROR",
                "style_family": "",
                "instrument_family": "",
                "asset_role": "",
                "tone_family": "",
                "sha256": "",
                "error": f"{type(exc).__name__}: {exc}",
            })
            rows_written += 1

        if factory.is_dir():
            for current, dirs, files in os.walk(factory, onerror=record_walk_error):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for filename in files:
                    if not filename.lower().endswith((".wav", ".wave")):
                        continue
                    if cancel_event is not None and cancel_event.is_set():
                        raise RuntimeError("FACTORY finalization cancelled; no assets were changed.")
                    wav_path = Path(current) / filename
                    sidecar = wav_path.with_suffix(wav_path.suffix + ".json")
                    row = {
                        "factory_wav": str(wav_path),
                        "sidecar": str(sidecar),
                        "asset_id": "",
                        "status": "INVALID",
                        "style_family": "",
                        "instrument_family": "",
                        "asset_role": "",
                        "tone_family": "",
                        "sha256": "",
                        "error": "",
                    }
                    try:
                        if not _inside(wav_path, factory) or not sidecar.is_file():
                            raise ValueError("Factory WAV has no valid provenance sidecar")
                        record = json.loads(sidecar.read_text(encoding="utf-8"))
                        row["asset_id"] = record.get("asset_id", "")
                        if record.get("distribution_status") != "VERIFIED_COPIED":
                            raise ValueError("Sidecar does not record VERIFIED_COPIED")
                        if Path(record.get("distributed_path", "")).resolve() != wav_path.resolve():
                            raise ValueError("Sidecar distributed_path does not match WAV path")
                        expected = str(record.get("distributed_sha256", "")).upper()
                        actual = _sha256(wav_path)
                        row["sha256"] = actual
                        if not expected or actual != expected:
                            raise ValueError("Factory WAV SHA-256 mismatch")
                        info = audio_source_info(wav_path)
                        if info.source_format.upper() != "WAV" or info.source_subtype not in {
                            "PCM_16", "PCM_24", "PCM_32", "PCM_U8", "PCM"
                        }:
                            raise ValueError("Factory file is not uncompressed PCM WAV")
                        if record.get("review_status") != "REVIEWED" or record.get("license_status") != "LICENSE_APPROVED":
                            raise ValueError("Factory sidecar lacks explicit musical/license approvals")
                        tags = record.get("musical_metadata") or {}
                        for field, allowed in (
                            ("style_family", STYLES),
                            ("instrument_family", INSTRUMENTS),
                            ("asset_role", ROLES),
                            ("tone_family", TONES),
                        ):
                            value = tags.get(field)
                            if value not in allowed:
                                raise ValueError(f"Missing/invalid reviewed tag: {field}")
                            row[field] = value
                        expected_category = wav_path.parent.relative_to(factory).as_posix()
                        tag_category = "/".join([
                            row["style_family"], "WAV", row["instrument_family"],
                            row["asset_role"], row["tone_family"],
                        ])
                        if expected_category != tag_category or record.get("distribution_category") != expected_category:
                            raise ValueError("Factory folder path does not match reviewed category tags")
                        if str(record.get("derived_sha256", "")).upper() != expected:
                            raise ValueError("Distributed WAV hash differs from reviewed source derivative")
                        if not str(tags.get("license_evidence", "")).strip() or not str(tags.get("musical_review_notes", "")).strip():
                            raise ValueError("Missing review or license evidence")
                        validation = record.get("review_validation") or {}
                        if not all(validation.get(key) is True for key in (
                            "source_sha256_verified", "derived_sha256_verified",
                            "sample_boundaries_verified", "explicit_musical_approval",
                            "explicit_license_approval",
                        )):
                            raise ValueError("Missing explicit review/license validation evidence")
                        row["status"] = "FACTORY_VALID"
                    except Exception as exc:
                        row["error"] = f"{type(exc).__name__}: {exc}"
                    counts[row["status"]] += 1
                    writer.writerow(row)
                    rows_written += 1
                    if progress and rows_written % 50 == 0:
                        progress(f"Финализация FACTORY: проверено WAV {rows_written}")
    valid = counts["FACTORY_VALID"]
    summary = {
        "factory_root": str(factory),
        "report_directory": str(report_dir),
        "factory_wav_checked": rows_written,
        "factory_valid_count": valid,
        "factory_invalid_count": counts["INVALID"],
        "status_counts": dict(counts),
        "factory_finalized": rows_written > 0 and valid == rows_written,
        "source_files_modified": False,
        "factory_files_modified": False,
    }
    (report_dir / "factory_finalization_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def finalize_library(
    samples_root: Path,
    staging_root: Path,
    *,
    reports_root: Path | None = None,
    progress=None,
    cancel_event=None,
) -> dict[str, Any]:
    """Finalize both staging candidates and already distributed FACTORY assets."""
    staging_result = finalize_staging(
        staging_root, reports_root=reports_root,
        progress=progress, cancel_event=cancel_event,
    )
    factory_result = audit_factory_library(
        samples_root, reports_root=reports_root,
        progress=progress, cancel_event=cancel_event,
    )
    return {
        "staging": staging_result,
        "factory": factory_result,
        "factory_distribution_allowed": staging_result["factory_distribution_allowed"],
        "factory_finalized": factory_result["factory_finalized"],
        "source_files_modified": False,
        "factory_files_modified": False,
    }

