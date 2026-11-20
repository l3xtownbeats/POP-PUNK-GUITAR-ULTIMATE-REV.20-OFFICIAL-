#!/usr/bin/env python3
"""Read-only batch fingerprint index for incoming guitar WAV files."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from audio_fingerprint import FINGERPRINT_VERSION, compare_fingerprints, fingerprint_wav

AUDIO_EXTENSIONS = {".wav", ".wave"}
MIN_SHARED_HASHES = 8
MAX_CANDIDATE_PAIRS = 100_000
EXCLUDED_LABELS = {"piano", "bell", "drum"}
EXCLUDED_LABEL_RE = re.compile(r"(?i)(?<![a-z0-9])(piano|bell|drum)(?![a-z0-9])")

def is_excluded_label(path: Path) -> bool:
    """Exclude non-guitar labels in any path component, case-insensitively."""
    return any(EXCLUDED_LABEL_RE.search(part) for part in path.parts)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def build_fingerprint_index(root: Path, workers: int | None = None) -> dict:
    """Fingerprint WAV files under root without changing any source file."""
    root = root.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Input root must be a directory")
    all_paths = sorted((p for p in root.rglob("*")
                        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS),
                       key=lambda p: str(p).casefold())
    excluded_count = sum(1 for p in all_paths if is_excluded_label(p.relative_to(root)))
    paths = [p for p in all_paths if not is_excluded_label(p.relative_to(root))]
    paths.sort(key=lambda p: str(p).casefold())
    # Piano, Bell and Drum labels are intentionally outside the guitar scan.
    worker_count = max(1, workers or min(8, os.cpu_count() or 2))
    records = []
    errors = []
    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        futures = {pool.submit(fingerprint_wav, path): path for path in paths}
        for future in as_completed(futures):
            path = futures[future]
            try:
                fp = future.result()
                records.append({
                    "relative_path": str(path.relative_to(root)),
                    "sha256": sha256_file(path),
                    "fingerprint": fp
                })
            except Exception as exc:
                errors.append({"relative_path": str(path.relative_to(root)),
                               "error": type(exc).__name__ + ": " + str(exc)})
    records.sort(key=lambda r: r["relative_path"].casefold())

    exact_groups = defaultdict(list)
    inverted = defaultdict(set)
    for index, record in enumerate(records):
        exact_groups[record["sha256"]].append(record["relative_path"])
        # A set prevents repeated landmarks in one file inflating candidate counts.
        for landmark in {item["hash"] for item in record["fingerprint"]["landmarks"]}:
            inverted[landmark].add(index)

    pair_evidence = Counter()
    for indices in inverted.values():
        ordered = sorted(indices)
        for pos, left in enumerate(ordered):
            for right in ordered[pos + 1:]:
                pair_evidence[(left, right)] += 1

    candidate_pairs = sorted(
        ((pair, count) for pair, count in pair_evidence.items()
         if count >= MIN_SHARED_HASHES),
        key=lambda item: (-item[1], item[0])
    )[:MAX_CANDIDATE_PAIRS]

    relationships = []
    for (left_index, right_index), shared in candidate_pairs:
        left, right = records[left_index], records[right_index]
        comparison = compare_fingerprints(left["fingerprint"], right["fingerprint"])
        relationships.append({
            "left_path": left["relative_path"],
            "right_path": right["relative_path"],
            "shared_unique_landmark_hashes": shared,
            **comparison
        })

    exact_duplicates = [
        {"sha256": digest, "paths": group, "count": len(group)}
        for digest, group in exact_groups.items() if len(group) > 1
    ]
    return {
        "index_version": "0.1.0",
        "fingerprint_version": FINGERPRINT_VERSION,
        "root": str(root),
        "files_discovered": len(paths),
        "files_excluded_by_label": excluded_count,
        "excluded_labels": sorted(EXCLUDED_LABELS),
        "files_fingerprinted": len(records),
        "files_with_errors": len(errors),
        "exact_duplicate_groups": exact_duplicates,
        "relationship_candidates": relationships,
        "errors": errors,
        "safety": {
            "source_files_modified": False,
            "automatic_delete_merge_or_move": False,
            "similarity_is_not_duplicate_identity": True,
            "review_status": "NEEDS_MUSICAL_REVIEW",
            "candidate_pair_cap": MAX_CANDIDATE_PAIRS
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a read-only incoming WAV fingerprint index.")
    parser.add_argument("root", type=Path, help="Folder to scan recursively")
    parser.add_argument("--output", type=Path,
                        default=Path("reports/fingerprint_relationships.json"))
    parser.add_argument("--workers", type=int, default=None)
    args = parser.parse_args()
    report = build_fingerprint_index(args.root, args.workers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "files_discovered", "files_fingerprinted", "files_with_errors",
        "exact_duplicate_groups")}, ensure_ascii=False, indent=2))
    print("Relationship candidates:", len(report["relationship_candidates"]))
    print("Report:", args.output)


if __name__ == "__main__":
    main()
