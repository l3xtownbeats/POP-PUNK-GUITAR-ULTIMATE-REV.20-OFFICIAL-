#!/usr/bin/env python3
"""Non-destructive source registration for the Manager 3.0 IMPORT GUITAR stage.

Import records point to original files; this module never copies, moves, renames,
rewrites, or deletes user assets. Expensive hashing/decoding belongs to later stages.
"""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

AUDIO_EXTENSIONS = {
    ".wav", ".wave", ".aif", ".aiff", ".flac", ".ogg", ".oga",
    ".mp3", ".m4a", ".aac", ".wma", ".opus",
}
SUPPORTED_EXTENSIONS = AUDIO_EXTENSIONS | {".sfz", ".zip", ".7z", ".rar"}
REGISTRY_VERSION = 2


def _identity(path: Path) -> str:
    return os.path.normcase(str(path.resolve()))


def _walk(path: Path):
    """Yield files recursively without following directory symlinks."""
    if path.is_file():
        yield path
        return
    stack = [path]
    while stack:
        folder = stack.pop()
        try:
            with os.scandir(folder) as entries:
                for entry in entries:
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            yield Path(entry.path)
                    except OSError:
                        continue
        except OSError:
            continue


def register_sources(
    selected_paths: Iterable[str | Path],
    registry_path: str | Path,
) -> dict:
    """Register multiple files/folders, retaining exact original paths and hierarchy."""
    selections = [Path(item).expanduser().resolve() for item in selected_paths]
    if not selections:
        raise ValueError("Не выбраны файлы или папки для импорта.")
    for item in selections:
        if not item.exists():
            raise FileNotFoundError(f"Источник не найден: {item}")
        if not (item.is_file() or item.is_dir()):
            raise ValueError(f"Неподдерживаемый тип источника: {item}")

    target = Path(registry_path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        data = json.loads(target.read_text(encoding="utf-8"))
        if data.get("registry_version") not in {1, REGISTRY_VERSION}:
            raise ValueError("Неизвестная версия реестра импорта; исходный реестр не изменён.")
        records = data.get("sources", [])
    else:
        records = []

    known = {record["identity"] for record in records if "identity" in record}
    added, duplicates, errors = [], [], []
    sfz_roots: dict[str, Path] = {}
    for selected in selections:
        root = selected if selected.is_dir() else selected.parent
        for file_path in _walk(selected):
            try:
                resolved = file_path.resolve()
                stat = resolved.stat()
                identity = _identity(resolved)
                if identity in known:
                    duplicates.append(str(resolved))
                    continue
                suffix = resolved.suffix.lower()
                relative = os.path.relpath(resolved, root)
                record = {
                    "identity": identity,
                    "source_path": str(resolved),
                    "selected_root": str(root),
                    "relative_path": relative,
                    "filename": resolved.name,
                    "extension": suffix,
                    "size_bytes": stat.st_size,
                    "modified_ns": stat.st_mtime_ns,
                    "format_group": (
                        "AUDIO" if suffix in AUDIO_EXTENSIONS else
                        "SFZ" if suffix == ".sfz" else
                        "ARCHIVE" if suffix in {".zip", ".7z", ".rar"} else
                        "OTHER_REVIEW_REQUIRED"
                    ),
                    "registration_status": "REGISTERED",
                    "registered_at": datetime.now(timezone.utc).isoformat(),
                    "source_modified_by_manager": False,
                }
                records.append(record)
                known.add(identity)
                added.append(record)
                if suffix == ".sfz":
                    sfz_roots[identity] = root
            except OSError as exc:
                errors.append({"path": str(file_path), "error": f"{type(exc).__name__}: {exc}"})

    # Re-audit every registered SFZ on each import pass, including duplicate
    # selections, so dependency status never silently goes stale.
    sfz_roots = {
        item["identity"]: Path(item.get("selected_root") or Path(item["source_path"]).parent)
        for item in records
        if str(item.get("extension", "")).lower() == ".sfz"
        and item.get("identity") and item.get("source_path")
    }

    # Resolve SFZ sample= and #include dependencies before the import is
    # considered scan-ready. The parser is read-only and confines samples to
    # the selected library root; unresolved references remain explicit.
    sfz_audit = []
    if sfz_roots:
        try:
            from sfz_parser import parse_sfz_file
        except ImportError:
            from .sfz_parser import parse_sfz_file
        for sfz_identity, library_root in sfz_roots.items():
            sfz_record = next(item for item in records if item.get("identity") == sfz_identity)
            try:
                rows = parse_sfz_file(Path(sfz_record["source_path"]), library_root)
                for row in rows:
                    sfz_audit.append({
                        "sfz_identity": sfz_identity,
                        "sfz_path": sfz_record["source_path"],
                        "library_root": str(library_root),
                        **row,
                    })
            except Exception as exc:
                sfz_audit.append({
                    "sfz_identity": sfz_identity,
                    "sfz_path": sfz_record["source_path"],
                    "library_root": str(library_root),
                    "status": "SFZ_AUDIT_ERROR",
                    "error": f"{type(exc).__name__}: {exc}",
                })

    payload = {
        "registry_version": REGISTRY_VERSION,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "source_count": len(records),
        "sources": records,
        "sfz_dependency_audit": sfz_audit,
    }
    fd, temporary_name = tempfile.mkstemp(
        prefix=target.name + ".", suffix=".tmp", dir=str(target.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, target)
    except Exception:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise

    return {
        "registry_path": str(target),
        "selected_sources": len(selections),
        "registered_files": len(added),
        "already_registered": len(duplicates),
        "errors": errors,
        "registered_by_format": {
            key: sum(1 for item in added if item["format_group"] == key)
            for key in sorted({item["format_group"] for item in added})
        },
        "sfz_dependency_rows": len(sfz_audit),
        "sfz_dependencies_found": sum(1 for row in sfz_audit if row.get("status") == "FOUND"),
        "sfz_dependencies_blocked": sum(1 for row in sfz_audit if row.get("status") != "FOUND"),
        "source_files_modified": False,
        "source_files_moved": False,
        "source_files_deleted": False,
        "next_stage": "SCAN_LIBRARY",
    }
