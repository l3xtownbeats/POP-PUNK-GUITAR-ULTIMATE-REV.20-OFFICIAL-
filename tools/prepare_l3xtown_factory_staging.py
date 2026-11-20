#!/usr/bin/env python3
"""Prepare a non-destructive FACTORY staging copy from L3XTOWN_SAMPLE_MAP.csv.

This script routes files by their existing source folder/filename labels only.
It does NOT analyse audio content or claim verified tone/articulation.
Original WAV files are never moved, renamed, or modified.
Run without --copy for a read-only preflight. Add --copy to create verified copies.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_ROOT = Path(r"F:\POP PUNK GUITAR ULTIMATE\Samples\SourceLibraries\L3XTOWN GUITAR")
DEFAULT_MAP = Path.home() / "Desktop" / "L3XTOWN_SAMPLE_MAP.csv"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def category_parts(value: str) -> list[str]:
    return [part.strip() for part in value.replace("/", "\\").split("\\") if part.strip()]


def route_for(category: str) -> tuple[str, str, str]:
    parts = category_parts(category)
    if len(parts) < 2:
        raise ValueError(f"Unrecognised source category: {category!r}")

    top = parts[0].casefold()
    if "акустика" in top:
        family = parts[1].upper().replace(" ", "_")
        if family not in {"ALL_MARTIN", "ALL_TAYLOR"}:
            raise ValueError(f"Unknown acoustic family in category: {category!r}")
        label = parts[2].casefold() if len(parts) >= 3 else "root"
        role_map = {
            "root": "ROOT_CHORD_LABELS",
            "7": "SEVENTH_CHORD_LABELS",
            "вверх": "UPSTROKE_LABELS",
            "кода": "CODA_LABELS",
            "сус": "SUS_LABELS",
        }
        role = role_map.get(label)
        if role is None:
            raise ValueError(f"Unknown acoustic subfolder label: {category!r}")
        return ("ACOUSTIC", family, role)

    if "квинты" in top:
        family = parts[1].upper().replace(" ", "_")
        if family.startswith("01_"):
            family = "ENGL"
        elif family.startswith("02_"):
            family = "MESA"
        elif family.startswith("03_"):
            family = "EVH"
        elif family.startswith("04_"):
            family = "MARSHALL_GIBSON"
        elif family.startswith("05_"):
            family = "FX"
        else:
            raise ValueError(f"Unknown electric source family: {category!r}")

        label = parts[2].casefold() if len(parts) >= 3 else "fx"
        role_map = {
            "квинты": "POWER_CHORD_LABELS",
            "кода": "CODA_LABELS",
            "ноты": "NOTE_LABELS",
            "слайды": "SLIDE_LABELS",
            "переборы 75 bpm": "ARPEGGIO_75BPM_LABEL",
            "fx": "FX_SOURCE_LABELS",
        }
        role = role_map.get(label)
        if role is None:
            raise ValueError(f"Unknown electric subfolder label: {category!r}")
        return ("ELECTRIC", family, role)

    raise ValueError(f"Unknown top-level source family: {category!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--map", dest="sample_map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--out", type=Path, default=None,
                        help="Destination FACTORY directory (default: <Samples>\\FACTORY)")
    parser.add_argument("--copy", action="store_true",
                        help="Actually copy files after validating source size and SHA-256")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    sample_map = args.sample_map.expanduser().resolve()
    out = (args.out.expanduser().resolve() if args.out else root.parent.parent / "FACTORY")

    if not root.is_dir():
        print(f"ERROR: source library folder not found: {root}", file=sys.stderr)
        return 2
    if not sample_map.is_file():
        print(f"ERROR: SAMPLE_MAP not found: {sample_map}", file=sys.stderr)
        return 2
    if out == root or root in out.parents:
        print("ERROR: destination must not be inside the source library.", file=sys.stderr)
        return 2

    with sample_map.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"Category", "Filename", "SizeBytes", "SHA256"}
        if not required.issubset(reader.fieldnames or []):
            print(f"ERROR: SAMPLE_MAP must contain columns: {sorted(required)}", file=sys.stderr)
            return 2
        rows = list(reader)

    if not rows:
        print("ERROR: SAMPLE_MAP contains no rows.", file=sys.stderr)
        return 2

    hash_paths: dict[str, list[str]] = defaultdict(list)
    plan: list[dict[str, str]] = []
    errors: list[str] = []

    for index, row in enumerate(rows, start=2):
        category = (row.get("Category") or "").strip()
        filename = (row.get("Filename") or "").strip()
        expected_hash = (row.get("SHA256") or "").strip().upper()
        try:
            expected_size = int(row.get("SizeBytes") or "")
            route = route_for(category)
            source = root.joinpath(*category_parts(category), filename).resolve()
            if root not in source.parents:
                raise ValueError("resolved source path escapes source root")
            if not source.is_file():
                raise FileNotFoundError(f"missing source file: {source}")
            actual_size = source.stat().st_size
            if actual_size != expected_size:
                raise ValueError(f"size mismatch ({actual_size} != {expected_size})")
            actual_hash = sha256_file(source)
            if actual_hash != expected_hash:
                raise ValueError(f"SHA256 mismatch ({actual_hash} != {expected_hash})")
            relative_source = source.relative_to(root).as_posix()
            destination_relative = Path(*route, filename).as_posix()
            hash_paths[expected_hash].append(relative_source)
            plan.append({
                "source_relative_path": relative_source,
                "destination_relative_path": destination_relative,
                "source_bytes": str(actual_size),
                "sha256": expected_hash,
                "sample_id": expected_hash[:16].lower(),
                "factory_group": "/".join(route),
                "classification_basis": "SOURCE_FOLDER_AND_FILENAME_LABEL_ONLY",
                "audio_review_status": "UNREVIEWED",
            })
        except Exception as exc:
            errors.append(f"CSV row {index}: {exc}")

    duplicate_counts = {key: len(paths) for key, paths in hash_paths.items()}
    for item in plan:
        item["duplicate_content_count"] = str(duplicate_counts[item["sha256"]])
        item["duplicate_content_status"] = (
            "EXACT_BYTE_DUPLICATE_REVIEW" if duplicate_counts[item["sha256"]] > 1
            else "UNIQUE_CONTENT"
        )

    print(f"Source rows: {len(rows)}")
    print(f"Validated files: {len(plan)}")
    print(f"Unique SHA-256 contents: {len(hash_paths)}")
    print(f"Exact duplicate groups: {sum(1 for count in duplicate_counts.values() if count > 1)}")
    print(f"Destination: {out}")
    print("Mode:", "COPY" if args.copy else "PREFLIGHT ONLY")
    for group, count in sorted(Counter(item["factory_group"] for item in plan).items()):
        print(f"  {group}: {count}")
    if errors:
        print("\nERRORS:")
        for error in errors:
            print(" -", error)
        print("No files were copied.")
        return 2

    if not args.copy:
        print("\nPreflight passed. No folders or files were created.")
        print("Run again with --copy to create FACTORY copies and its routing manifest.")
        return 0

    # Do not overwrite a destination file. Existing identical files are treated as already staged.
    copied = 0
    skipped = 0
    for item in plan:
        source = root / Path(item["source_relative_path"])
        destination = out / Path(item["destination_relative_path"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if not destination.is_file() or destination.stat().st_size != int(item["source_bytes"]):
                raise RuntimeError(f"Destination conflict; refusing to overwrite: {destination}")
            if sha256_file(destination) != item["sha256"]:
                raise RuntimeError(f"Destination hash conflict; refusing to overwrite: {destination}")
            skipped += 1
            continue
        shutil.copy2(source, destination)
        if destination.stat().st_size != int(item["source_bytes"]) or sha256_file(destination) != item["sha256"]:
            raise RuntimeError(f"Post-copy verification failed: {destination}")
        copied += 1

    manifest_path = out / "FACTORY_SOURCE_ROUTING.csv"
    with manifest_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(plan[0].keys()))
        writer.writeheader()
        writer.writerows(plan)

    print(f"\nCopy complete. New copies: {copied}; already present and verified: {skipped}")
    print(f"Routing manifest: {manifest_path}")
    print("Original source WAV files were not moved, renamed, or modified.")
    print("Tone, pitch, chord voicing, articulation and tempo remain UNREVIEWED until audio analysis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
