#!/usr/bin/env python3
"""
Read-only local preflight for L3XTOWN acoustic WAV sources.

Checks inventory paths, file sizes, SHA-256 and WAV headers. It never edits,
moves, renames, deletes, or copies source audio.

Windows example:
  py tools\\preflight_l3xtown_acoustic_sources.py ^
    --library-root "F:\\POP PUNK GUITAR ULTIMATE\\Samples\\SourceLibraries\\L3XTOWN GUITAR" ^
    --inventory "L3XTOWN_FULL_INVENTORY.csv" ^
    --output-dir "F:\\POP PUNK GUITAR ULTIMATE\\Reports\\AcousticPreflight" ^
    --family acoustic

Use --family all to check every inventory row (default: acoustic).
Python 3.10+, standard library only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import wave
from datetime import datetime, timezone
from pathlib import Path

CHUNK_SIZE = 1024 * 1024
REQUIRED_COLUMNS = {
    "relative_path_from_library_root",
    "expected_source_bytes",
    "expected_sha256",
    "source_relative_folder",
    "source_category",
    "original_filename",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def wav_metadata(path: Path) -> dict:
    try:
        with wave.open(str(path), "rb") as wav:
            channels = wav.getnchannels()
            rate = wav.getframerate()
            frames = wav.getnframes()
            width = wav.getsampwidth()
            return {
                "wav_header_status": "OK",
                "sample_rate_hz": rate,
                "channels": channels,
                "sample_width_bytes": width,
                "bit_depth": width * 8,
                "frames": frames,
                "duration_seconds": round(frames / rate, 6) if rate else 0,
                "compression_type": wav.getcomptype(),
                "compression_name": wav.getcompname(),
            }
    except (wave.Error, EOFError, OSError, ValueError) as exc:
        return {
            "wav_header_status": "UNREADABLE_OR_UNSUPPORTED: " + str(exc),
            "sample_rate_hz": "",
            "channels": "",
            "sample_width_bytes": "",
            "bit_depth": "",
            "frames": "",
            "duration_seconds": "",
            "compression_type": "",
            "compression_name": "",
        }


def within_root(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library-root", required=True, help="Root of extracted L3XTOWN GUITAR library")
    parser.add_argument("--inventory", required=True, help="L3XTOWN_FULL_INVENTORY.csv")
    parser.add_argument("--output-dir", required=True, help="Separate folder for reports; must not be inside source library")
    parser.add_argument("--family", choices=("acoustic", "all"), default="acoustic",
                        help="acoustic checks ALL MARTIN and ALL TAYLOR; all checks every inventory row")
    args = parser.parse_args()

    root = Path(args.library_root).expanduser().resolve()
    inventory_path = Path(args.inventory).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not root.is_dir():
        parser.error(f"Library root does not exist: {root}")
    if not inventory_path.is_file():
        parser.error(f"Inventory file does not exist: {inventory_path}")
    if within_root(root, output_dir):
        parser.error("Output directory must be outside the source library (read-only safety rule).")

    with inventory_path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = set(reader.fieldnames or [])
        missing_columns = sorted(REQUIRED_COLUMNS - columns)
        if missing_columns:
            parser.error("Inventory is missing required columns: " + ", ".join(missing_columns))
        source_rows = list(reader)

    if args.family == "acoustic":
        source_rows = [
            row for row in source_rows
            if "ALL MARTIN" in (row.get("source_relative_folder") or "").upper()
            or "ALL TAYLOR" in (row.get("source_relative_folder") or "").upper()
        ]

    results = []
    counts = {
        "inventory_rows_selected": len(source_rows),
        "files_found": 0,
        "files_missing": 0,
        "size_match": 0,
        "size_mismatch": 0,
        "sha256_match": 0,
        "sha256_mismatch": 0,
        "wav_header_ok": 0,
        "wav_header_problem": 0,
        "path_rejected": 0,
    }

    for index, row in enumerate(source_rows, start=1):
        relative = (row.get("relative_path_from_library_root") or "").strip().replace("\\", "/")
        expected_size_text = (row.get("expected_source_bytes") or "").strip()
        expected_hash = (row.get("expected_sha256") or "").strip().upper()
        result = {
            "row_number": index,
            "source_category": row.get("source_category", ""),
            "source_relative_folder": row.get("source_relative_folder", ""),
            "original_filename": row.get("original_filename", ""),
            "relative_path_from_library_root": relative,
            "expected_source_bytes": expected_size_text,
            "actual_source_bytes": "",
            "expected_sha256": expected_hash,
            "actual_sha256": "",
            "file_exists": "NO",
            "size_status": "NOT_CHECKED",
            "sha256_status": "NOT_CHECKED",
            "wav_header_status": "NOT_CHECKED",
            "sample_rate_hz": "",
            "channels": "",
            "sample_width_bytes": "",
            "bit_depth": "",
            "frames": "",
            "duration_seconds": "",
            "compression_type": "",
            "compression_name": "",
            "overall_status": "",
            "error": "",
        }

        candidate = (root / Path(relative)).resolve()
        if not relative or Path(relative).is_absolute() or not within_root(root, candidate):
            result["overall_status"] = "PATH_REJECTED"
            result["error"] = "Empty, absolute, or outside-root path"
            counts["path_rejected"] += 1
            results.append(result)
            continue

        if not candidate.is_file():
            result["overall_status"] = "FILE_NOT_FOUND"
            counts["files_missing"] += 1
            results.append(result)
            continue

        counts["files_found"] += 1
        result["file_exists"] = "YES"
        try:
            actual_size = candidate.stat().st_size
            actual_hash = sha256_file(candidate)
            result["actual_source_bytes"] = actual_size
            result["actual_sha256"] = actual_hash

            try:
                size_matches = bool(expected_size_text) and actual_size == int(expected_size_text)
            except ValueError:
                size_matches = False
            result["size_status"] = "MATCH" if size_matches else "MISMATCH_OR_NO_EXPECTED_VALUE"
            counts["size_match" if size_matches else "size_mismatch"] += 1

            hash_matches = bool(expected_hash) and actual_hash == expected_hash
            result["sha256_status"] = "MATCH" if hash_matches else "MISMATCH_OR_NO_EXPECTED_VALUE"
            counts["sha256_match" if hash_matches else "sha256_mismatch"] += 1

            metadata = wav_metadata(candidate)
            result.update(metadata)
            if metadata["wav_header_status"] == "OK":
                counts["wav_header_ok"] += 1
            else:
                counts["wav_header_problem"] += 1

            checks_ok = size_matches and hash_matches and metadata["wav_header_status"] == "OK"
            result["overall_status"] = "PASS" if checks_ok else "REVIEW"
        except OSError as exc:
            result["overall_status"] = "READ_ERROR"
            result["error"] = str(exc)

        results.append(result)

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "ACOUSTIC_LOCAL_PREFLIGHT.csv"
    json_path = output_dir / "ACOUSTIC_LOCAL_PREFLIGHT_SUMMARY.json"

    fieldnames = list(results[0].keys()) if results else [
        "row_number", "relative_path_from_library_root", "overall_status", "error"
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "tool": "L3XTOWN Acoustic Local Preflight",
        "version": "1.0.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "library_root": str(root),
        "inventory": str(inventory_path),
        "family_filter": args.family,
        "read_only_source_policy": True,
        "source_files_modified": False,
        "counts": counts,
        "pass": sum(1 for item in results if item["overall_status"] == "PASS"),
        "review": sum(1 for item in results if item["overall_status"] not in ("PASS",)),
        "csv_report": str(csv_path),
        "notes": [
            "The script reads source WAV files only; it never changes or copies them.",
            "PASS means path exists, byte size matches, SHA-256 matches, and Python wave can read the header.",
            "A readable WAV header is not a listening test or musical note/chord recognition.",
            "Unsupported WAV encodings are reported for review rather than converted."
        ],
    }
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("L3XTOWN LOCAL PREFLIGHT COMPLETE")
    print(f"Rows checked: {counts['inventory_rows_selected']}")
    print(f"PASS: {summary['pass']} | REVIEW: {summary['review']}")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    print("Source library was not modified.")
    return 0 if summary["review"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
