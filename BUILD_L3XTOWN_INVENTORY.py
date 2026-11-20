#!/usr/bin/env python3
"""
Build a full-path WAV inventory for the user-owned L3XTOWN GUITAR library.

Read-only: source WAV files are never modified.
Python standard library only.

Example (Windows):
  py tools\build_l3xtown_full_inventory.py ^
    --root "F:\POP PUNK GUITAR ULTIMATE\Samples\SourceLibraries\L3XTOWN GUITAR" ^
    --sample-map "L3XTOWN_SAMPLE_MAP.csv" ^
    --out "L3XTOWN_FULL_INVENTORY.csv" ^
    --report "L3XTOWN_INVENTORY_RECONCILIATION.csv"
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
import wave
from pathlib import Path


def read_csv(path: Path):
    # utf-8-sig accepts both UTF-8 and Excel-style UTF-8 BOM files.
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def safe_wav_metadata(path: Path):
    try:
        with wave.open(str(path), "rb") as wav:
            channels = wav.getnchannels()
            sample_rate = wav.getframerate()
            frames = wav.getnframes()
            sample_width_bytes = wav.getsampwidth()
            duration = frames / sample_rate if sample_rate else 0.0
            return {
                "sample_rate_hz": sample_rate,
                "channels": channels,
                "sample_width_bytes": sample_width_bytes,
                "bit_depth": sample_width_bytes * 8,
                "frames": frames,
                "duration_seconds": f"{duration:.6f}",
                "wav_header_status": "OK",
            }
    except (wave.Error, EOFError, OSError) as exc:
        return {
            "sample_rate_hz": "",
            "channels": "",
            "sample_width_bytes": "",
            "bit_depth": "",
            "frames": "",
            "duration_seconds": "",
            "wav_header_status": "UNREADABLE_OR_UNSUPPORTED: " + str(exc),
        }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, help="L3XTOWN GUITAR root folder")
    ap.add_argument("--sample-map", required=True, help="L3XTOWN_SAMPLE_MAP.csv")
    ap.add_argument("--out", default="L3XTOWN_FULL_INVENTORY.csv")
    ap.add_argument("--report", default="L3XTOWN_INVENTORY_RECONCILIATION.csv")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    map_path = Path(args.sample_map).expanduser().resolve()
    if not root.is_dir():
        ap.error(f"Library root does not exist: {root}")
    if not map_path.is_file():
        ap.error(f"Sample map does not exist: {map_path}")

    source_rows = read_csv(map_path)
    full_rows = []
    report_rows = []
    totals = {
        "rows": 0, "found": 0, "missing": 0,
        "size_match": 0, "size_mismatch": 0,
        "sha_match": 0, "sha_mismatch": 0,
        "wav_ok": 0, "wav_header_problem": 0,
    }

    for source in source_rows:
        category = (source.get("Category") or "").strip()
        filename = (source.get("Filename") or "").strip()
        expected_bytes = (source.get("SizeBytes") or "").strip()
        expected_sha = (source.get("SHA256") or "").strip().upper()

        relative_parts = [p for p in category.split("\\") if p]
        relative_parts.append(filename)
        relative_path = Path(*relative_parts)
        wav_path = root / relative_path
        totals["rows"] += 1

        status = []
        exists = wav_path.is_file()
        actual_bytes = ""
        actual_sha = ""
        meta = {
            "sample_rate_hz": "", "channels": "", "sample_width_bytes": "",
            "bit_depth": "", "frames": "", "duration_seconds": "",
            "wav_header_status": "FILE_NOT_FOUND",
        }

        if not exists:
            totals["missing"] += 1
            status.append("FILE_NOT_FOUND")
        else:
            totals["found"] += 1
            actual_bytes = wav_path.stat().st_size
            actual_sha = sha256_file(wav_path)
            if expected_bytes and actual_bytes == int(expected_bytes):
                totals["size_match"] += 1
                status.append("SIZE_MATCH")
            else:
                totals["size_mismatch"] += 1
                status.append("SIZE_MISMATCH")

            if expected_sha and actual_sha == expected_sha:
                totals["sha_match"] += 1
                status.append("SHA256_MATCH")
            else:
                totals["sha_mismatch"] += 1
                status.append("SHA256_MISMATCH")

            meta = safe_wav_metadata(wav_path)
            if meta["wav_header_status"] == "OK":
                totals["wav_ok"] += 1
            else:
                totals["wav_header_problem"] += 1
                status.append("WAV_HEADER_PROBLEM")

        full_rows.append({
            "source_category": category,
            "source_group": relative_parts[0] if relative_parts else "",
            "source_relative_folder": "/".join(relative_parts[:-1]),
            "original_filename": filename,
            "relative_path_from_library_root": relative_path.as_posix(),
            "expected_source_bytes": expected_bytes,
            "actual_source_bytes": actual_bytes,
            "expected_sha256": expected_sha,
            "actual_sha256": actual_sha,
            **meta,
            "file_status": ";".join(status) if status else "UNKNOWN",
        })

        report_rows.append({
            "source_category": category,
            "filename": filename,
            "relative_path_from_library_root": relative_path.as_posix(),
            "expected_source_bytes": expected_bytes,
            "actual_source_bytes": actual_bytes,
            "expected_sha256": expected_sha,
            "actual_sha256": actual_sha,
            "file_exists": "YES" if exists else "NO",
            "wav_header_status": meta["wav_header_status"],
            "reconciliation_status": ";".join(status) if status else "UNKNOWN",
        })

    full_fields = [
        "source_category", "source_group", "source_relative_folder",
        "original_filename", "relative_path_from_library_root",
        "expected_source_bytes", "actual_source_bytes",
        "expected_sha256", "actual_sha256", "sample_rate_hz", "channels",
        "sample_width_bytes", "bit_depth", "frames", "duration_seconds",
        "wav_header_status", "file_status",
    ]
    report_fields = [
        "source_category", "filename", "relative_path_from_library_root",
        "expected_source_bytes", "actual_source_bytes",
        "expected_sha256", "actual_sha256", "file_exists",
        "wav_header_status", "reconciliation_status",
    ]

    for output, fields, rows in [
        (Path(args.out), full_fields, full_rows),
        (Path(args.report), report_fields, report_rows),
    ]:
        output = output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    print("L3XTOWN inventory scan complete (read-only).")
    print(f"Rows: {totals['rows']}")
    print(f"Files found: {totals['found']}; missing: {totals['missing']}")
    print(f"Size matches: {totals['size_match']}; mismatches: {totals['size_mismatch']}")
    print(f"SHA-256 matches: {totals['sha_match']}; mismatches: {totals['sha_mismatch']}")
    print(f"WAV headers readable: {totals['wav_ok']}; unsupported/unreadable: {totals['wav_header_problem']}")
    print(f"Full inventory: {Path(args.out).resolve()}")
    print(f"Reconciliation report: {Path(args.report).resolve()}")
    print("Do not distribute the library until any missing files or hash mismatches are reviewed.")
    return 0 if totals["missing"] == 0 and totals["sha_mismatch"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
