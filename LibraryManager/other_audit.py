#!/usr/bin/env python3
"""Conservative audit and approval-gated routing for Samples/OTHER.

The audio classifier does not prove guitar identity. Unknown WAVs remain manual
review candidates; only unsupported/corrupt assets or explicitly approved
decisions may be routed to OTHER. Originals are never deleted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from asset_classifier import classify_wav
from library_manager import AUDIO_EXT, sha256_file, wav_info

VERSION = "1.0.0"
DECISIONS_NAME = "other_decisions.json"


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing report: {path}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing report: {path}")
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("x", newline="", encoding="utf-8-sig") as stream:
        if fields:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)


def audit_other_library(samples_root: Path, report_dir: Path) -> dict[str, Any]:
    """Audit existing OTHER and find Import assets needing separate review."""
    samples_root = Path(samples_root).expanduser().resolve()
    incoming = samples_root / "Import Sample Guitar"
    other = samples_root / "OTHER"
    if not incoming.is_dir():
        raise FileNotFoundError(f"Import folder not found: {incoming}")
    other.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for origin, base in (("OTHER", other), ("IMPORT", incoming)):
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            try:
                digest = _hash(path)
                ext = path.suffix.lower()
                row: dict[str, Any] = {
                    "origin": origin,
                    "path": str(path.resolve()),
                    "relative_path": str(path.relative_to(base)),
                    "extension": ext,
                    "bytes": path.stat().st_size,
                    "sha256": digest,
                    "audit_status": "EXISTING_OTHER_AUDITED" if origin == "OTHER" else "REVIEW_REQUIRED",
                    "other_reason": "",
                    "asset_kind_candidate": "",
                    "sample_subtype_candidate": "",
                    "classification_confidence": "",
                    "routing_decision": "NONE",
                    "source_preserved": True,
                }
                if origin == "OTHER" and ext in AUDIO_EXT:
                    try:
                        metadata = wav_info(path)
                        row["wav_status"] = metadata.get("wav_status", "UNKNOWN")
                        if metadata.get("wav_status") in {"OK", "NON_PCM_OR_EXTENSIBLE"}:
                            classification = classify_wav(path, analyze_pitch=False)
                            row.update({
                                "asset_kind_candidate": classification.get("asset_kind_candidate", "UNKNOWN"),
                                "sample_subtype_candidate": classification.get("sample_subtype_candidate", "UNKNOWN"),
                                "classification_confidence": classification.get("classification_confidence", ""),
                                "classification_evidence": " | ".join(classification.get("evidence", [])),
                                "content_audit": "AUDIO_CANDIDATE_ONLY_REQUIRES_REVIEW",
                            })
                        else:
                            row["content_audit"] = "INVALID_OR_UNSUPPORTED_AUDIO"
                    except Exception as exc:
                        row["content_audit"] = f"AUDIO_AUDIT_ERROR: {type(exc).__name__}: {exc}"
                if origin == "IMPORT":
                    if ext not in AUDIO_EXT and ext not in {".sfz", ".zip", ".7z", ".rar"}:
                        row.update(audit_status="OTHER_REVIEW_REQUIRED",
                                   other_reason="Unsupported file extension; separate inspection required.",
                                   routing_decision="MANUAL_OTHER_REVIEW")
                    elif ext in AUDIO_EXT:
                        try:
                            metadata = wav_info(path)
                            row["wav_status"] = metadata.get("wav_status", "UNKNOWN")
                            if ext in {".wav", ".wave"} and metadata.get("wav_status") in {"OK", "NON_PCM_OR_EXTENSIBLE"}:
                                classification = classify_wav(path, analyze_pitch=False)
                                row.update({
                                    "asset_kind_candidate": classification.get("asset_kind_candidate", "UNKNOWN"),
                                    "sample_subtype_candidate": classification.get("sample_subtype_candidate", "UNKNOWN"),
                                    "classification_confidence": classification.get("classification_confidence", ""),
                                    "classification_evidence": " | ".join(classification.get("evidence", [])),
                                    "audit_status": "UNKNOWN_MANUAL_REVIEW" if classification.get("asset_kind_candidate") == "UNKNOWN" else "SUITABLE_CANDIDATE_REQUIRES_REVIEW",
                                    "other_reason": "Audio evidence does not establish guitar identity; human listening required.",
                                    "routing_decision": "DO_NOT_AUTO_ROUTE",
                                })
                            elif metadata.get("wav_status") not in {"OK", "NON_PCM_OR_EXTENSIBLE"}:
                                row.update(audit_status="OTHER_REVIEW_REQUIRED",
                                           other_reason="WAV container is invalid, unreadable or unsupported.",
                                           routing_decision="MANUAL_OTHER_REVIEW")
                            else:
                                row.update(audit_status="UNKNOWN_MANUAL_REVIEW",
                                           other_reason="Non-WAV audio format requires supported decoder and review.",
                                           routing_decision="MANUAL_REVIEW")
                        except Exception as exc:
                            row.update(audit_status="OTHER_REVIEW_REQUIRED",
                                       other_reason=f"Audio metadata/classification failed: {type(exc).__name__}: {exc}",
                                       routing_decision="MANUAL_OTHER_REVIEW")
                    elif ext in {".sfz", ".zip", ".7z", ".rar"}:
                        row.update(audit_status="MANUAL_REVIEW",
                                   other_reason="Instrument definition/archive requires dependency and content audit.",
                                   routing_decision="MANUAL_REVIEW")
                rows.append(row)
            except Exception as exc:
                errors.append({"path": str(path), "error": f"{type(exc).__name__}: {exc}"})

    report_dir = Path(report_dir).expanduser().resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "schema_version": 1,
        "audit_version": VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "samples_root": str(samples_root),
        "other_folder": str(other),
        "files_audited": len(rows),
        "existing_other_files": sum(r["origin"] == "OTHER" for r in rows),
        "existing_other_wav_files": sum(r["origin"] == "OTHER" and r["extension"] in AUDIO_EXT for r in rows),
        "import_files_needing_other_or_manual_review": sum(
            r["origin"] == "IMPORT" and r["audit_status"] in {"OTHER_REVIEW_REQUIRED", "UNKNOWN_MANUAL_REVIEW", "MANUAL_REVIEW"}
            for r in rows
        ),
        "unknown_manual_review": sum(r["audit_status"] == "UNKNOWN_MANUAL_REVIEW" for r in rows),
        "errors": len(errors),
        "automatic_routing": False,
        "source_files_moved_or_deleted": False,
        "policy": "No audio-only inference can establish non-guitar identity; unknown assets remain manual review.",
    }
    _write_json(report_dir / "other_audit.json", {"summary": summary, "assets": rows, "errors": errors})
    _write_csv(report_dir / "other_audit.csv", rows)
    return summary


def load_other_decisions(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    decisions = payload.get("decisions", payload)
    if not isinstance(decisions, dict):
        raise ValueError("Decision file must contain a decisions object keyed by absolute source path")
    return decisions


def route_approved_to_other(samples_root: Path, decision_file: Path, *, approve: bool = False,
                            journal_path: Path | None = None) -> dict[str, Any]:
    """Copy only explicitly approved Import files into OTHER; dry-run by default."""
    samples_root = Path(samples_root).expanduser().resolve()
    incoming, other = samples_root / "Import Sample Guitar", samples_root / "OTHER"
    if not incoming.is_dir():
        raise FileNotFoundError(incoming)
    other.mkdir(parents=True, exist_ok=True)
    decisions = load_other_decisions(decision_file)
    entries = []
    for source_text, decision in decisions.items():
        if not isinstance(decision, dict) or decision.get("route_to_other") is not True:
            continue
        source = Path(source_text).expanduser().resolve()
        if not _inside(source, incoming) or not source.is_file():
            raise ValueError(f"Approved source must be an existing file inside Import Sample Guitar: {source}")
        digest = _hash(source)
        expected = str(decision.get("sha256", "")).upper()
        if not expected or digest != expected:
            raise RuntimeError(f"Decision SHA-256 missing or stale for {source}")
        reason = str(decision.get("reason", "")).strip()
        if not reason:
            raise ValueError(f"An explicit reason is required for OTHER routing: {source}")
        destination = (other / source.relative_to(incoming)).resolve()
        if not _inside(destination, other):
            raise ValueError(f"OTHER destination escaped its approved root: {destination}")
        entries.append({"source_path": str(source), "destination_path": str(destination),
                        "sha256": digest, "reason": reason, "status": "READY_FOR_APPROVAL"})
    plan = {"schema_version": 1, "samples_root": str(samples_root), "entries": entries,
            "executed": False, "source_files_deleted": False}
    if not approve:
        return {**plan, "status": "DRY_RUN"}
    journal = Path(journal_path or (other / "LibraryManagerReports" / "other_operations.jsonl"))
    results = []
    for entry in entries:
        source, destination = Path(entry["source_path"]), Path(entry["destination_path"])
        if _hash(source) != entry["sha256"]:
            raise RuntimeError(f"Source changed before OTHER copy: {source}")
        if destination.exists() or destination.with_suffix(destination.suffix + ".json").exists():
            raise FileExistsError(f"Refusing to overwrite OTHER destination: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        copied = False
        sidecar = destination.with_suffix(destination.suffix + ".json")
        try:
            with source.open("rb") as src, destination.open("xb") as dst:
                copied = True
                shutil.copyfileobj(src, dst, 1024 * 1024)
            if _hash(destination) != entry["sha256"]:
                raise IOError("OTHER destination SHA-256 mismatch")
            record = {**entry, "asset_id": entry["sha256"][:24], "source_sha256": entry["sha256"],
                      "destination_sha256": _hash(destination),
                      "distribution_status": "VERIFIED_COPIED_TO_OTHER",
                      "distributed_at_utc": datetime.now(timezone.utc).isoformat(),
                      "source_preserved": True, "license_status": "UNREVIEWED"}
            with sidecar.open("x", encoding="utf-8") as stream:
                json.dump(record, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            journal.parent.mkdir(parents=True, exist_ok=True)
            with journal.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"event": "COPIED_TO_OTHER", **record}, ensure_ascii=False) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            results.append(record)
        except Exception:
            sidecar.unlink(missing_ok=True)
            if copied:
                destination.unlink(missing_ok=True)
            raise
    return {**plan, "executed": True, "status": "COPIED_VERIFIED", "results": results,
            "source_files_deleted": False}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit OTHER and prepare safe, approval-gated routing.")
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--reports", type=Path, default=Path(__file__).resolve().parent / "reports")
    parser.add_argument("--decisions", type=Path)
    parser.add_argument("--approve-other-copy", action="store_true")
    args = parser.parse_args()
    if args.decisions:
        result = route_approved_to_other(args.samples, args.decisions, approve=args.approve_other_copy)
    else:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        result = audit_other_library(args.samples, args.reports / f"other_{run_id}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
