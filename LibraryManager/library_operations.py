#!/usr/bin/env python3
"""Review-gated physical distribution and separately confirmed source cleanup.

The module never guesses classifications. It uses only reviewed manifest tags,
verifies SHA-256 after every copy, refuses overwrites, and journals operations.
Original import files are deleted only by a separate explicit cleanup call after
all listed child assets have verified destinations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from factory_curator import INSTRUMENTS, ROLES, STYLES, TONES
from audio_range_io import audio_source_info

VERSION = "0.2.0"
APPROVED_REVIEW_STATES = {"REVIEWED", "BOUNDARIES_USER_OR_REVIEWER_APPROVED"}


def sha256_file(path: Path) -> str:
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


def _tag(metadata: dict[str, Any], field: str, allowed: set[str]) -> str:
    value = metadata.get(field)
    if isinstance(value, dict):
        value = value.get("value")
    if value not in allowed:
        raise ValueError(f"Missing/invalid reviewed {field}: {value!r}")
    return value


def _load_approved_manifest(manifest_path: Path, staging_root: Path,
                            source_hash_cache: dict[str, str] | None = None) -> tuple[dict, Path, str]:
    manifest_path = manifest_path.resolve()
    staging_root = staging_root.resolve()
    if not _inside(manifest_path, staging_root) or not manifest_path.is_file():
        raise ValueError("Manifest must be an existing file inside LibraryManager/staging")
    record = json.loads(manifest_path.read_text(encoding="utf-8"))
    if record.get("review_status") not in APPROVED_REVIEW_STATES:
        raise ValueError("Musical content/boundaries must be reviewed before distribution")
    if record.get("license_status") != "LICENSE_APPROVED":
        raise ValueError("Only LICENSE_APPROVED material can enter FACTORY")
    tags = record.get("musical_metadata") or {}
    if not isinstance(tags, dict) or not str(tags.get("license_evidence", "")).strip():
        raise ValueError("Explicit license evidence is required before FACTORY distribution")
    if not str(tags.get("musical_review_notes", "")).strip():
        raise ValueError("Musical review notes are required before FACTORY distribution")
    validation = record.get("review_validation") or {}
    if not all(validation.get(key) is True for key in (
        "source_sha256_verified", "derived_sha256_verified",
        "sample_boundaries_verified", "explicit_musical_approval",
        "explicit_license_approval",
    )):
        raise ValueError("Manifest is missing explicit review/license validation evidence")
    source = Path(record.get("derived_path", ""))
    if not source.is_absolute():
        source = (manifest_path.parent / source).resolve()
    if not _inside(source, staging_root) or not source.is_file():
        raise ValueError("Derived WAV must exist inside LibraryManager/staging")
    if source.suffix.lower() not in {".wav", ".wave"}:
        raise ValueError("Only WAV assets can be distributed by this stage")
    expected = str(record.get("derived_sha256", "")).upper()
    actual = sha256_file(source)
    if not expected or actual != expected:
        raise ValueError("Staged WAV SHA-256 does not match its manifest")
    original = Path(record.get("source_path", ""))
    expected_original = str(record.get("source_sha256", "")).upper()
    if not original.is_file() or not expected_original:
        raise ValueError("Original source is missing or source SHA-256 is absent")
    cache = source_hash_cache if source_hash_cache is not None else {}
    original_key = str(original.resolve())
    actual_original = cache.get(original_key)
    if actual_original is None:
        actual_original = sha256_file(original)
        cache[original_key] = actual_original
    if actual_original != expected_original:
        raise ValueError("Original source SHA-256 changed after extraction/review")
    start = int(record.get("source_start_sample", -1))
    end = int(record.get("source_end_sample", -1))
    if start < 0 or end <= start:
        raise ValueError("Invalid source sample boundaries")
    original_info = audio_source_info(original)
    derived_info = audio_source_info(source)
    if end > original_info.frames or derived_info.frames != end - start:
        raise ValueError("WAV frame ranges do not match original sample boundaries")
    if derived_info.source_format.upper() != "WAV" or derived_info.source_subtype not in {"PCM_16", "PCM_24", "PCM_32", "PCM_U8", "PCM"}:
        raise ValueError("Only uncompressed PCM WAV can enter FACTORY")
    if original_info.framerate != derived_info.framerate:
        raise ValueError("Derived WAV sample rate differs from original source")
    return record, source, actual


def distribution_plan(manifest_paths: list[Path], samples_root: Path,
                      staging_root: Path) -> dict[str, Any]:
    samples_root = samples_root.resolve()
    factory_root = samples_root / "FACTORY"
    entries = []
    seen = set()
    source_hash_cache: dict[str, str] = {}
    for manifest_path in manifest_paths:
        record, source, digest = _load_approved_manifest(manifest_path, staging_root, source_hash_cache)
        if digest in seen:
            raise ValueError(f"Duplicate staged content in one distribution batch: {digest}")
        seen.add(digest)
        tags = record.get("musical_metadata") or {}
        if not isinstance(tags, dict):
            raise ValueError("musical_metadata must be an object")
        style = _tag(tags, "style_family", STYLES)
        instrument = _tag(tags, "instrument_family", INSTRUMENTS)
        role = _tag(tags, "asset_role", ROLES)
        tone = _tag(tags, "tone_family", TONES)
        # All promoted derivatives are PCM WAV; source formats remain recorded in provenance.
        format_family = "WAV"
        destination_dir = factory_root / style / format_family / instrument / role / tone
        destination = destination_dir / source.name
        entries.append({
            "manifest_path": str(Path(manifest_path).resolve()),
            "source_path": str(source),
            "source_sha256": digest,
            "destination_path": str(destination),
            "category_path": f"{style}/{format_family}/{instrument}/{role}/{tone}",
            "asset_id": record.get("asset_id"),
            "engine_targets": record.get("engine_targets", []),
            "operation": "COPY_TO_FACTORY",
            "status": "READY_FOR_EXPLICIT_APPROVAL",
        })
    return {
        "schema_version": 1,
        "manager_version": VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "samples_root": str(samples_root),
        "staging_root": str(Path(staging_root).resolve()),
        "entries": entries,
        "automatic_factory_promotion": False,
        "source_originals_deleted": False,
    }


def _append_journal(journal: Path, event: dict[str, Any]) -> None:
    journal.parent.mkdir(parents=True, exist_ok=True)
    with journal.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def distribute_assets(plan: dict[str, Any], *, approve: bool = False,
                      journal_path: Path | None = None) -> dict[str, Any]:
    """Copy verified assets into FACTORY; dry-run unless approve=True."""
    if not approve:
        return {**plan, "executed": False, "status": "DRY_RUN"}
    journal = (journal_path or (Path(plan["samples_root"]) / "FACTORY" /
                                "LibraryManagerReports" / "operations.jsonl")).resolve()
    results = []
    verified_originals: dict[str, str] = {}
    for entry in plan["entries"]:
        source = Path(entry["source_path"]).resolve()
        destination = Path(entry["destination_path"]).resolve()
        if not source.is_file() or sha256_file(source) != entry["source_sha256"]:
            raise RuntimeError(f"Staged source changed before distribution: {source}")
        manifest_record = json.loads(Path(entry["manifest_path"]).read_text(encoding="utf-8"))
        if manifest_record.get("review_status") not in APPROVED_REVIEW_STATES or manifest_record.get("license_status") != "LICENSE_APPROVED":
            raise RuntimeError("Review/license approval changed after the distribution plan was created")
        tags = manifest_record.get("musical_metadata") or {}
        manifest_derived = Path(manifest_record.get("derived_path", ""))
        if not manifest_derived.is_absolute():
            manifest_derived = (Path(entry["manifest_path"]).parent / manifest_derived).resolve()
        if manifest_derived.resolve() != source or str(manifest_record.get("derived_sha256", "")).upper() != entry["source_sha256"]:
            raise RuntimeError("Staged asset path/hash changed after the distribution plan was created")
        if not str(tags.get("license_evidence", "")).strip() or not str(tags.get("musical_review_notes", "")).strip():
            raise RuntimeError("Review or license evidence is missing at distribution time")
        style = _tag(tags, "style_family", STYLES)
        instrument = _tag(tags, "instrument_family", INSTRUMENTS)
        role = _tag(tags, "asset_role", ROLES)
        tone = _tag(tags, "tone_family", TONES)
        expected_destination = (Path(plan["samples_root"]).resolve() / "FACTORY" /
                                style / "WAV" / instrument / role / tone / source.name).resolve()
        if expected_destination != destination:
            raise RuntimeError("Factory destination tags changed after the distribution plan was created")
        validation = manifest_record.get("review_validation") or {}
        if not all(validation.get(key) is True for key in (
            "source_sha256_verified", "derived_sha256_verified",
            "sample_boundaries_verified", "explicit_musical_approval",
            "explicit_license_approval",
        )):
            raise RuntimeError("Explicit review/license validation evidence changed")
        original = Path(manifest_record.get("source_path", ""))
        expected_original = str(manifest_record.get("source_sha256", "")).upper()
        original_key = str(original.resolve())
        actual_original = verified_originals.get(original_key)
        if actual_original is None:
            if not original.is_file() or not expected_original:
                raise RuntimeError("Original source is missing at distribution time")
            actual_original = sha256_file(original)
            verified_originals[original_key] = actual_original
        if actual_original != expected_original:
            raise RuntimeError("Original source changed after review; refusing Factory copy")
        factory_root = (Path(plan["samples_root"]).resolve() / "FACTORY").resolve()
        if not _inside(destination, factory_root):
            raise ValueError("Destination escaped FACTORY")
        sidecar = destination.with_suffix(destination.suffix + ".json")
        if destination.exists() or sidecar.exists():
            raise FileExistsError(f"Refusing to overwrite existing destination: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        created_audio = False
        try:
            with source.open("rb") as src, destination.open("xb") as dst:
                created_audio = True
                shutil.copyfileobj(src, dst, length=1024 * 1024)
            copied_hash = sha256_file(destination)
            if copied_hash != entry["source_sha256"]:
                raise IOError("Destination SHA-256 mismatch")
            original_manifest = json.loads(Path(entry["manifest_path"]).read_text(encoding="utf-8"))
            distributed_record = dict(original_manifest)
            distributed_record.update({
                "distributed_path": str(destination),
                "distributed_sha256": copied_hash,
                "distribution_status": "VERIFIED_COPIED",
                "distribution_operation": "COPY_TO_FACTORY",
                "distribution_category": entry["category_path"],
                "distribution_verified_at_utc": datetime.now(timezone.utc).isoformat(),
            })
            with sidecar.open("x", encoding="utf-8") as stream:
                json.dump(distributed_record, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            event = {
                "event": "ASSET_DISTRIBUTED",
                "at_utc": datetime.now(timezone.utc).isoformat(),
                "source": str(source),
                "destination": str(destination),
                "sha256": copied_hash,
                "category": entry["category_path"],
                "status": "VERIFIED_COPIED",
            }
            _append_journal(journal, event)
            results.append(event)
        except Exception:
            sidecar.unlink(missing_ok=True)
            if created_audio:
                destination.unlink(missing_ok=True)
            raise
    return {
        **plan,
        "executed": True,
        "status": "DISTRIBUTION_COMPLETE",
        "results": results,
        "journal_path": str(journal),
        "source_originals_deleted": False,
    }



def auto_distribute_approved(
    samples_root: Path,
    staging_root: Path,
    *,
    approve: bool = False,
    journal_path: Path | None = None,
    cancel_event: Any = None,
    progress=None,
) -> dict[str, Any]:
    """Process every staging manifest independently; bad assets never block later ones.

    Only manifests that pass the existing musical-review, license, provenance,
    PCM, bounds and SHA-256 gates are copied. Each asset is its own transaction:
    a failed item is recorded and the next approved candidate is attempted.
    Completed transactions are retained if a later item fails or cancellation
    is requested. Original source files are never modified.
    """
    samples = Path(samples_root).resolve()
    staging = Path(staging_root).resolve()
    manifests_dir = staging / "manifests"
    manifests = sorted(manifests_dir.glob("*.json")) if manifests_dir.is_dir() else []
    journal = journal_path or (
        samples / "FACTORY" / "LibraryManagerReports" / "operations.jsonl"
    )
    ready: list[tuple[Path, dict[str, Any]]] = []
    rejected: list[dict[str, str]] = []
    for index, manifest in enumerate(manifests, 1):
        if cancel_event is not None and cancel_event.is_set():
            return {
                "status": "CANCELLED_DURING_PREFLIGHT",
                "manifests_seen": index - 1,
                "ready_count": len(ready),
                "copied_count": 0,
                "rejected": rejected,
                "results": [],
                "source_originals_deleted": False,
            }
        try:
            plan = distribution_plan([manifest], samples, staging)
            if len(plan.get("entries", [])) != 1:
                raise ValueError("Manifest did not produce exactly one eligible FACTORY asset")
            ready.append((manifest, plan))
        except Exception as exc:
            rejected.append({
                "manifest_path": str(manifest),
                "error": f"{type(exc).__name__}: {exc}",
            })
        if progress and (index == 1 or index % 25 == 0 or index == len(manifests)):
            progress(f"Автораспределение: проверено манифестов {index}/{len(manifests)}; готово {len(ready)}; пропущено {len(rejected)}.")

    if not approve:
        return {
            "status": "DRY_RUN",
            "manifests_seen": len(manifests),
            "ready_count": len(ready),
            "copied_count": 0,
            "rejected": rejected,
            "ready_manifest_paths": [str(path) for path, _ in ready],
            "results": [],
            "source_originals_deleted": False,
        }

    results: list[dict[str, Any]] = []
    failed: list[dict[str, str]] = []
    cancelled = False
    for index, (manifest, plan) in enumerate(ready, 1):
        if cancel_event is not None and cancel_event.is_set():
            cancelled = True
            break
        try:
            result = distribute_assets_transactional(
                plan,
                staging_root=staging,
                approve=True,
                journal_path=journal,
                cancel_event=cancel_event,
            )
            results.extend(result.get("results", []))
        except Exception as exc:
            if cancel_event is not None and cancel_event.is_set():
                cancelled = True
                break
            failed.append({
                "manifest_path": str(manifest),
                "error": f"{type(exc).__name__}: {exc}",
            })
        if progress and (index == 1 or index % 10 == 0 or index == len(ready)):
            progress(f"Автораспределение: обработано {index}/{len(ready)} одобренных кандидатов; скопировано {len(results)}; ошибок {len(failed)}.")

    finalization = None
    finalization_error = None
    if not cancelled:
        try:
            from finalization import finalize_library
            finalization = finalize_library(
                samples, staging, progress=progress, cancel_event=cancel_event,
            )
        except Exception as exc:
            # Copies already verified in their own transactions are retained;
            # report-generation failure must not erase successful distribution.
            finalization_error = f"{type(exc).__name__}: {exc}"
            if progress:
                progress(f"ПРЕДУПРЕЖДЕНИЕ: распределение сохранено, но финальный аудит не завершился: {finalization_error}")

    status = "CANCELLED_PARTIAL" if cancelled else (
        "DISTRIBUTION_COMPLETE_WITH_ERRORS"
        if failed or rejected or finalization_error else "DISTRIBUTION_COMPLETE"
    )
    return {
        "status": status,
        "manifests_seen": len(manifests),
        "ready_count": len(ready),
        "copied_count": len(results),
        "rejected": rejected,
        "failed": failed,
        "results": results,
        "journal_path": str(journal),
        "transaction_per_asset": True,
        "finalization": finalization,
        "finalization_error": finalization_error,
        "source_originals_deleted": False,
    }


def cleanup_original_sources(distributed_manifest_paths: list[Path], *,
                             samples_root: Path, confirm_delete: bool = False,
                             confirm_all_dependents_accounted_for: bool = False,
                             journal_path: Path | None = None) -> dict[str, Any]:
    """Delete source originals only after every supplied dependent is verified.

    The second confirmation explicitly asserts that the supplied manifest list
    contains every derived asset depending on each source recording.
    """
    if not confirm_delete or not confirm_all_dependents_accounted_for:
        raise ValueError(
            "Cleanup requires BOTH --confirm-delete-originals and "
            "--confirm-all-dependents-accounted-for"
        )
    samples_root = samples_root.resolve()
    incoming_root = (samples_root / "Import Sample Guitar").resolve()
    by_source: dict[str, dict[str, Any]] = {}
    for manifest_path in distributed_manifest_paths:
        path = Path(manifest_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("distribution_status") != "VERIFIED_COPIED":
            raise ValueError(f"Dependent asset is not successfully distributed: {path}")
        factory_root = (samples_root / "FACTORY").resolve()
        destination = Path(record.get("distributed_path", "")).resolve()
        expected_derived = str(record.get("distributed_sha256", "")).upper()
        if not _inside(destination, factory_root) or not destination.is_file() or not expected_derived:
            raise ValueError(
                f"Verified dependent must be an existing file inside FACTORY: {destination}"
            )
        if sha256_file(destination) != expected_derived:
            raise ValueError(f"Distributed asset integrity check failed: {destination}")
        # Never trust the staging manifest alone: the installed FACTORY sidecar
        # must independently attest to the exact source and copied destination.
        sidecar = destination.with_suffix(destination.suffix + ".json")
        if not sidecar.is_file():
            raise ValueError(f"Verified FACTORY sidecar is missing: {sidecar}")
        distributed_record = json.loads(sidecar.read_text(encoding="utf-8"))
        if (
            distributed_record.get("distribution_status") != "VERIFIED_COPIED"
            or Path(distributed_record.get("distributed_path", "")).resolve() != destination
            or str(distributed_record.get("distributed_sha256", "")).upper() != expected_derived
        ):
            raise ValueError(f"FACTORY sidecar does not verify this distributed asset: {sidecar}")
        source = Path(record.get("source_path", "")).resolve()
        source_hash = str(record.get("source_sha256", "")).upper()
        if (
            Path(distributed_record.get("source_path", "")).resolve() != source
            or str(distributed_record.get("source_sha256", "")).upper() != source_hash
        ):
            raise ValueError(f"FACTORY sidecar source provenance mismatch: {sidecar}")
        if not _inside(source, incoming_root) or not source.is_file():
            raise ValueError(f"Original must be an existing file inside Import Sample Guitar: {source}")
        if not source_hash or sha256_file(source) != source_hash:
            raise ValueError(f"Original source hash mismatch; refusing cleanup: {source}")
        key = str(source)
        entry = by_source.setdefault(key, {
            "source_path": key,
            "source_sha256": source_hash,
            "verified_dependents": [],
        })
        if entry["source_sha256"] != source_hash:
            raise ValueError(f"Conflicting source hashes for {source}")
        entry["verified_dependents"].append(str(destination))

    plan = {
        "operation": "DELETE_ORIGINALS_AFTER_VERIFIED_DISTRIBUTION",
        "sources": list(by_source.values()),
        "confirm_all_dependents_accounted_for": True,
        "confirm_delete": True,
    }
    if not by_source:
        return {**plan, "deleted": [], "status": "NOTHING_TO_DELETE"}
    journal = (journal_path or (samples_root / "FACTORY" /
                                "LibraryManagerReports" / "operations.jsonl")).resolve()
    # Validate every source and every dependent before deleting any source.
    for item in plan["sources"]:
        source = Path(item["source_path"])
        if sha256_file(source) != item["source_sha256"]:
            raise RuntimeError(f"Source changed during cleanup preflight: {source}")
        for dependent in item["verified_dependents"]:
            if not Path(dependent).is_file():
                raise RuntimeError(f"Dependent asset disappeared: {dependent}")
    deleted = []
    for item in plan["sources"]:
        source = Path(item["source_path"])
        event = {
            "event": "ORIGINAL_SOURCE_DELETED_AFTER_CONFIRMATION",
            "at_utc": datetime.now(timezone.utc).isoformat(),
            "source": str(source),
            "source_sha256": item["source_sha256"],
            "verified_dependents": item["verified_dependents"],
        }
        _append_journal(journal, event)
        source.unlink()
        deleted.append(event)
    return {**plan, "deleted": deleted, "status": "ORIGINAL_CLEANUP_COMPLETE",
            "journal_path": str(journal)}


def distribute_assets_transactional(
    plan: dict[str, Any],
    *,
    staging_root: Path,
    approve: bool = False,
    journal_path: Path | None = None,
    cancel_event: Any = None,
) -> dict[str, Any]:
    """Preflight and copy a complete approved batch, rolling back this batch on error.

    Originals and staged assets are never moved or deleted. Only destinations
    opened by this invocation are eligible for rollback. Existing files are
    never overwritten, including when a destination appears after preflight.
    """
    if not approve:
        return {**plan, "executed": False, "status": "DRY_RUN"}

    samples_root = Path(plan.get("samples_root", "")).resolve()
    staging_root = Path(staging_root).resolve()
    factory_root = (samples_root / "FACTORY").resolve()
    entries = plan.get("entries")
    if not samples_root.is_dir() or not isinstance(entries, list):
        raise ValueError("Distribution plan is missing a valid Samples root or entries list")
    if not entries:
        return {**plan, "executed": True, "status": "NOTHING_TO_DISTRIBUTE", "results": []}

    manifests = []
    for entry in entries:
        manifest_value = entry.get("manifest_path")
        if not isinstance(manifest_value, str) or not manifest_value:
            raise ValueError("Every distribution entry must reference its staging manifest")
        manifest = Path(manifest_value).resolve()
        if not _inside(manifest, staging_root) or not manifest.is_file():
            raise ValueError(f"Manifest is missing or outside staging: {manifest}")
        manifests.append(manifest)

    # Rebuild the plan immediately before writing. This rechecks musical and
    # license approvals, source/derived hashes, PCM format and sample bounds,
    # and prevents a stale or edited plan from changing a destination.
    canonical = distribution_plan(manifests, samples_root, staging_root)
    def signature(items: list[dict[str, Any]]) -> list[tuple[str, str, str, str, str]]:
        return sorted(
            (
                str(Path(item["manifest_path"]).resolve()),
                str(Path(item["source_path"]).resolve()),
                str(item["source_sha256"]).upper(),
                str(Path(item["destination_path"]).resolve()),
                str(item["category_path"]),
            )
            for item in items
        )
    if signature(entries) != signature(canonical["entries"]):
        raise RuntimeError("Distribution plan is stale or was modified; regenerate the plan before copying")

    destinations: set[str] = set()
    hashes: set[str] = set()
    # Complete preflight before creating any output directory or file.
    for entry in canonical["entries"]:
        if cancel_event is not None and cancel_event.is_set():
            raise RuntimeError("Distribution cancelled during preflight; no files were copied")
        destination = Path(entry["destination_path"]).resolve()
        source = Path(entry["source_path"]).resolve()
        digest = str(entry["source_sha256"]).upper()
        destination_key = str(destination).casefold()
        if not _inside(destination, factory_root):
            raise ValueError(f"Destination escaped FACTORY: {destination}")
        if destination_key in destinations:
            raise ValueError(f"Two assets target the same destination: {destination}")
        if digest in hashes:
            raise ValueError(f"Duplicate staged content in the distribution batch: {digest}")
        destinations.add(destination_key)
        hashes.add(digest)
        if not source.is_file() or sha256_file(source) != digest:
            raise RuntimeError(f"Staged source changed during preflight: {source}")
        sidecar = destination.with_suffix(destination.suffix + ".json")
        if destination.exists() or sidecar.exists():
            raise FileExistsError(f"Refusing to overwrite existing destination or manifest: {destination}")

    journal = (journal_path or (factory_root / "LibraryManagerReports" / "operations.jsonl")).resolve()
    results: list[dict[str, Any]] = []
    created: list[dict[str, Any]] = []

    try:
        for index, entry in enumerate(canonical["entries"], 1):
            if cancel_event is not None and cancel_event.is_set():
                raise RuntimeError("Distribution cancelled; rolling back the current batch")
            manifest_path = Path(entry["manifest_path"]).resolve()
            source = Path(entry["source_path"]).resolve()
            destination = Path(entry["destination_path"]).resolve()
            sidecar = destination.with_suffix(destination.suffix + ".json")
            digest = str(entry["source_sha256"]).upper()

            # Revalidate each source immediately before opening its destination.
            record = json.loads(manifest_path.read_text(encoding="utf-8"))
            if record.get("review_status") not in APPROVED_REVIEW_STATES or record.get("license_status") != "LICENSE_APPROVED":
                raise RuntimeError(f"Review/license approval changed before copy: {manifest_path}")
            if not source.is_file() or sha256_file(source) != digest:
                raise RuntimeError(f"Staged source changed before copy: {source}")

            destination.parent.mkdir(parents=True, exist_ok=True)
            created_item = {
                "destination": destination,
                "sidecar": sidecar,
                "sha256": digest,
                "audio_created": False,
                "sidecar_created": False,
            }
            # Exclusive create protects against races and never overwrites.
            with source.open("rb") as src, destination.open("xb") as dst:
                created_item["audio_created"] = True
                created.append(created_item)
                shutil.copyfileobj(src, dst, length=1024 * 1024)
                dst.flush()
                os.fsync(dst.fileno())

            copied_hash = sha256_file(destination)
            if copied_hash != digest:
                raise IOError(f"Destination SHA-256 mismatch: {destination}")

            distributed_record = dict(record)
            distributed_record.update({
                "distributed_path": str(destination),
                "distributed_sha256": copied_hash,
                "distribution_status": "VERIFIED_COPIED",
                "distribution_operation": "COPY_TO_FACTORY_TRANSACTION",
                "distribution_category": entry["category_path"],
                "distribution_verified_at_utc": datetime.now(timezone.utc).isoformat(),
            })
            with sidecar.open("x", encoding="utf-8") as stream:
                created_item["sidecar_created"] = True
                json.dump(distributed_record, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())

            event = {
                "event": "ASSET_DISTRIBUTED",
                "transaction": "BATCH",
                "batch_index": index,
                "batch_count": len(canonical["entries"]),
                "at_utc": datetime.now(timezone.utc).isoformat(),
                "source": str(source),
                "destination": str(destination),
                "sha256": copied_hash,
                "category": entry["category_path"],
                "status": "VERIFIED_COPIED",
            }
            _append_journal(journal, event)
            results.append(event)

    except Exception as failure:
        rollback_errors: list[str] = []
        for item in reversed(created):
            destination = item["destination"]
            sidecar = item["sidecar"]
            try:
                if item["sidecar_created"] and sidecar.exists():
                    sidecar_record = json.loads(sidecar.read_text(encoding="utf-8"))
                    if (sidecar_record.get("distributed_path") == str(destination)
                            and str(sidecar_record.get("distributed_sha256", "")).upper() == item["sha256"]):
                        sidecar.unlink()
                if item["audio_created"] and destination.exists():
                    # This file was opened with exclusive creation by this run.
                    destination.unlink()
                _append_journal(journal, {
                    "event": "BATCH_ROLLBACK",
                    "transaction": "BATCH",
                    "at_utc": datetime.now(timezone.utc).isoformat(),
                    "destination": str(destination),
                    "sha256": item["sha256"],
                    "status": "ROLLED_BACK",
                })
            except Exception as rollback_exc:
                rollback_errors.append(
                    f"{destination}: {type(rollback_exc).__name__}: {rollback_exc}"
                )
        if rollback_errors:
            raise RuntimeError(
                f"Batch distribution failed ({type(failure).__name__}: {failure}); "
                "rollback was incomplete: " + "; ".join(rollback_errors)
            ) from failure
        raise RuntimeError(
            f"Batch distribution failed and all files created by this batch were rolled back: "
            f"{type(failure).__name__}: {failure}"
        ) from failure

    return {
        **canonical,
        "executed": True,
        "status": "DISTRIBUTION_COMPLETE",
        "transactional": True,
        "results": results,
        "journal_path": str(journal),
        "source_originals_deleted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Review-gated asset distribution and source cleanup.")
    sub = parser.add_subparsers(dest="command", required=True)
    plan_parser = sub.add_parser("plan")
    plan_parser.add_argument("samples_root", type=Path)
    plan_parser.add_argument("staging_root", type=Path)
    plan_parser.add_argument("manifests", nargs="+", type=Path)
    copy_parser = sub.add_parser("distribute")
    copy_parser.add_argument("plan", type=Path)
    copy_parser.add_argument("--approve", action="store_true")
    copy_parser.add_argument("--journal", type=Path)
    copy_parser.add_argument("--staging", type=Path,
                             default=Path(__file__).resolve().parent / "staging")
    cleanup_parser = sub.add_parser("cleanup-originals")
    cleanup_parser.add_argument("samples_root", type=Path)
    cleanup_parser.add_argument("distributed_manifests", nargs="+", type=Path)
    cleanup_parser.add_argument("--confirm-delete-originals", action="store_true")
    cleanup_parser.add_argument("--confirm-all-dependents-accounted-for", action="store_true")
    cleanup_parser.add_argument("--journal", type=Path)
    args = parser.parse_args()
    if args.command == "plan":
        result = distribution_plan(args.manifests, args.samples_root, args.staging_root)
    elif args.command == "distribute":
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        result = distribute_assets_transactional(
            plan, staging_root=args.staging, approve=args.approve,
            journal_path=args.journal,
        )
    else:
        result = cleanup_original_sources(
            args.distributed_manifests, samples_root=args.samples_root,
            confirm_delete=args.confirm_delete_originals,
            confirm_all_dependents_accounted_for=args.confirm_all_dependents_accounted_for,
            journal_path=args.journal,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
