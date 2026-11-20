#!/usr/bin/env python3
"""Whole-import dependency audit and explicitly confirmed source cleanup."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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
    except (OSError, ValueError):
        return False


def audit_all_import_sources(samples_root: Path, staging_root: Path,
                             report_path: Path) -> dict[str, Any]:
    """Audit every Import file against staged, FACTORY and OTHER provenance records."""
    samples_root = Path(samples_root).expanduser().resolve()
    incoming = samples_root / "Import Sample Guitar"
    if not incoming.is_dir():
        raise FileNotFoundError(incoming)
    roots = [Path(staging_root).expanduser().resolve(),
             samples_root / "FACTORY", samples_root / "OTHER"]
    source_records: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, str]] = []
    manifests_scanned = 0
    verified_distributed_assets: set[tuple[str, str]] = set()
    for distributed_root in roots[1:]:
        if not distributed_root.is_dir():
            continue
        for sidecar in distributed_root.rglob("*.json"):
            try:
                item = json.loads(sidecar.read_text(encoding="utf-8"))
                if item.get("distribution_status") in {"VERIFIED_COPIED", "VERIFIED_COPIED_TO_OTHER"}:
                    if item.get("source_path") and item.get("asset_id"):
                        verified_distributed_assets.add((str(Path(item["source_path"]).resolve()), str(item["asset_id"])))
            except Exception:
                continue

    for source in sorted(p for p in incoming.rglob("*") if p.is_file()):
        try:
            if source.suffix.lower() == ".json":
                try:
                    sidecar_data = json.loads(source.read_text(encoding="utf-8"))
                    if isinstance(sidecar_data, dict) and sidecar_data.get("source_path") and sidecar_data.get("source_sha256"):
                        continue
                except (ValueError, OSError, UnicodeDecodeError):
                    pass
            source_records[str(source.resolve())] = {
                "source_path": str(source.resolve()),
                "source_sha256": sha256_file(source),
                "bytes": source.stat().st_size,
                "dependents": [],
                "can_cleanup": False,
                "cleanup_status": "BLOCKED_NO_VERIFIED_DESTINATION",
                "blockers": [],
            }
        except Exception as exc:
            errors.append({"path": str(source), "stage": "SOURCE_HASH",
                           "error": f"{type(exc).__name__}: {exc}"})

    for base in roots:
        if not base.is_dir():
            continue
        for manifest in sorted(base.rglob("*.json")):
            try:
                record = json.loads(manifest.read_text(encoding="utf-8"))
                source_text = record.get("source_path")
                source_hash = record.get("source_sha256") or record.get("sha256")
                if not source_text or not source_hash:
                    continue
                source = Path(source_text).expanduser().resolve()
                if not _inside(source, incoming):
                    continue
                manifests_scanned += 1
                tracked = source_records.get(str(source))
                if tracked is None:
                    errors.append({"path": str(manifest), "stage": "DEPENDENCY",
                                   "error": "Manifest references a source outside the current Import inventory."})
                    continue
                dependent: dict[str, Any] = {
                    "manifest_path": str(manifest.resolve()),
                    "manifest_sha256": sha256_file(manifest),
                    "source_sha256_in_manifest": str(source_hash).upper(),
                    "destination_path": None,
                    "destination_verified": False,
                    "license_status": record.get("license_status", "UNREVIEWED"),
                    "review_status": record.get("review_status", "UNKNOWN"),
                    "kind": record.get("kind", "UNKNOWN"),
                    "blockers": [],
                }
                if str(source_hash).upper() != tracked["source_sha256"]:
                    dependent["blockers"].append("SOURCE_HASH_MISMATCH")
                destination_text = (record.get("distributed_path") or record.get("destination_path"))
                if base == roots[0] and not destination_text:
                    asset_key = (str(source), str(record.get("asset_id", "")))
                    if asset_key in verified_distributed_assets:
                        continue
                destination_hash = (record.get("distributed_sha256") or
                                    record.get("destination_sha256") or
                                    record.get("derived_sha256"))
                if destination_text:
                    destination = Path(destination_text).expanduser().resolve()
                    dependent["destination_path"] = str(destination)
                    if not (_inside(destination, samples_root / "FACTORY") or _inside(destination, samples_root / "OTHER")):
                        dependent["blockers"].append("DESTINATION_OUTSIDE_APPROVED_ROOT")
                    elif destination.is_file() and destination_hash:
                        actual = sha256_file(destination)
                        if actual == str(destination_hash).upper():
                            dependent["destination_verified"] = True
                        else:
                            dependent["blockers"].append("DESTINATION_HASH_MISMATCH")
                    else:
                        dependent["blockers"].append("DESTINATION_MISSING_OR_HASH_UNAVAILABLE")
                else:
                    dependent["blockers"].append("NOT_DISTRIBUTED")
                if manifest.is_relative_to(roots[0]) if hasattr(manifest, "is_relative_to") else _inside(manifest, roots[0]):
                    if record.get("review_status") not in {"REVIEWED", "BOUNDARIES_USER_OR_REVIEWER_APPROVED"}:
                        dependent["blockers"].append("MUSICAL_REVIEW_INCOMPLETE")
                    if record.get("license_status") != "LICENSE_APPROVED":
                        dependent["blockers"].append("LICENSE_NOT_APPROVED")
                if record.get("distribution_status") == "VERIFIED_COPIED":
                    if record.get("license_status") != "LICENSE_APPROVED":
                        dependent["blockers"].append("FACTORY_LICENSE_NOT_APPROVED")
                elif record.get("distribution_status") == "VERIFIED_COPIED_TO_OTHER":
                    if not record.get("reason"):
                        dependent["blockers"].append("OTHER_REASON_MISSING")
                if dependent["blockers"]:
                    dependent["destination_verified"] = False
                tracked["dependents"].append(dependent)
            except Exception as exc:
                errors.append({"path": str(manifest), "stage": "MANIFEST_READ",
                               "error": f"{type(exc).__name__}: {exc}"})

    rows = []
    for record in source_records.values():
        deps = record["dependents"]
        blockers = []
        if not deps:
            blockers.append("NO_DEPENDENCY_MANIFESTS")
        for dep in deps:
            blockers.extend(f'{dep["manifest_path"]}: {reason}' for reason in dep["blockers"])
        if deps and all(dep["destination_verified"] for dep in deps) and not blockers:
            record["can_cleanup"] = True
            record["cleanup_status"] = "ELIGIBLE_AFTER_EXPLICIT_CONFIRMATION"
        else:
            record["blockers"] = sorted(set(blockers))
        rows.append(record)

    referenced_staged = set()
    for row in rows:
        for dep in row["dependents"]:
            if dep.get("manifest_path"):
                try:
                    manifest_record = json.loads(Path(dep["manifest_path"]).read_text(encoding="utf-8"))
                    if manifest_record.get("derived_path"):
                        referenced_staged.add(str(Path(manifest_record["derived_path"]).resolve()))
                except Exception:
                    pass
    staging_clips = Path(staging_root).expanduser().resolve() / "clips"
    if staging_clips.is_dir():
        for staged_audio in staging_clips.rglob("*"):
            if staged_audio.is_file() and staged_audio.suffix.lower() in {".wav", ".wave"} and str(staged_audio.resolve()) not in referenced_staged:
                errors.append({"path": str(staged_audio), "stage": "DEPENDENCY",
                               "error": "Unmanifested staged audio clip; source dependency cannot be proven complete."})

    eligible = sum(row["can_cleanup"] for row in rows)
    if errors:
        for row in rows:
            row["can_cleanup"] = False
            if "GLOBAL_AUDIT_ERRORS" not in row["blockers"]:
                row["blockers"].append("GLOBAL_AUDIT_ERRORS")
        eligible = 0
    summary = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "samples_root": str(samples_root),
        "incoming_folder": str(incoming),
        "source_files_scanned": len(rows),
        "dependency_manifests_scanned": manifests_scanned,
        "eligible_for_cleanup": eligible,
        "blocked_sources": len(rows) - eligible,
        "errors": len(errors),
        "deletion_performed": False,
        "policy": "Every Import source and every known dependent must have a verified destination; no inferred completeness.",
    }
    report = {"summary": summary, "sources": rows, "errors": errors}
    report_path = Path(report_path).expanduser().resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if report_path.exists():
        raise FileExistsError(f"Refusing to overwrite cleanup audit: {report_path}")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def cleanup_sources_from_audit(samples_root: Path, staging_root: Path, audit_path: Path, *,
                               approve: bool = False,
                               confirm_all_dependents_accounted_for: bool = False,
                               journal_path: Path | None = None) -> dict[str, Any]:
    """Delete only sources passing a fresh whole-import audit and explicit approvals."""
    if not approve or not confirm_all_dependents_accounted_for:
        raise PermissionError("Cleanup requires both explicit approval confirmations.")
    samples_root = Path(samples_root).expanduser().resolve()
    audit_path = Path(audit_path).expanduser().resolve()
    previous = json.loads(audit_path.read_text(encoding="utf-8"))
    if Path(previous["summary"]["samples_root"]).resolve() != samples_root:
        raise ValueError("Audit belongs to a different Samples root.")
    fresh_path = audit_path.with_name(audit_path.stem + "_fresh.json")
    fresh = audit_all_import_sources(samples_root, staging_root, fresh_path)
    if fresh["summary"]["blocked_sources"] or fresh["errors"]:
        return {"deleted": 0, "status": "BLOCKED", "audit": fresh["summary"],
                "fresh_audit_path": str(fresh_path)}
    eligible = fresh["sources"]
    if not eligible or not all(item["can_cleanup"] for item in eligible):
        return {"deleted": 0, "status": "BLOCKED", "reason": "Not every Import source is eligible."}
    journal = Path(journal_path or (samples_root / "LibraryManagerReports" / "cleanup.jsonl"))
    deleted = []
    for item in eligible:
        source = Path(item["source_path"])
        if not _inside(source, samples_root / "Import Sample Guitar") or not source.is_file():
            raise RuntimeError(f"Source path changed or escaped Import: {source}")
        if sha256_file(source) != item["source_sha256"]:
            raise RuntimeError(f"Source changed after fresh audit: {source}")
        source.unlink()
        event = {"event": "SOURCE_CLEANED_UP", "at_utc": datetime.now(timezone.utc).isoformat(),
                 "source_path": str(source), "source_sha256": item["source_sha256"],
                 "verified_dependents": len(item["dependents"])}
        journal.parent.mkdir(parents=True, exist_ok=True)
        with journal.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        deleted.append(event)
    return {"deleted": len(deleted), "status": "CLEANUP_COMPLETED",
            "events": deleted, "fresh_audit_path": str(fresh_path)}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Audit every Import dependency; optional confirmed cleanup.")
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--staging", type=Path, default=Path(__file__).resolve().parent / "staging")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "reports" / "cleanup_audit.json")
    args = parser.parse_args()
    result = audit_all_import_sources(args.samples, args.staging, args.output)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
