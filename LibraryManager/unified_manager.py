#!/usr/bin/env python3
"""Unified, non-destructive POP PUNK GUITAR Library Manager entry point.

Combines inventory/SHA-256/WAV metadata/SFZ audit with the existing acoustic,
rhythm, repeated-pattern and optional virtual-range analyzers. Original assets
are read-only. Derived reports live under the resolved persistent runtime data directory; virtual
sidecars are opt-in and live under Import Sample Guitar.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from audio_analysis import analyse_wav
from asset_classifier import classify_wav
from library_manager import AUDIO_EXT, ARCHIVE_EXT, EXCLUDED_LABEL_RE, infer_labels, sha256_file, wav_info
from pattern_pipeline import build_pattern_report
from sfz_parser import parse_sfz_file
from virtual_sample_extractor import analyze_pattern_ranges, write_virtual_index
from irregular_phrase_segmenter import analyze_irregular_guitar_phrases
from other_audit import audit_other_library
from pattern_engine_schema import build_pattern_engine_manifest, validate_pattern_engine_manifest
from mode_sorter import build_mode_sorting_report
from mode_assignment_index import build_mode_assignment_index
from app_paths import resolve_runtime_paths, runtime_staging_root

VERSION = "3.0.0-dev9"
SUPPORTED = AUDIO_EXT | {".sfz"} | ARCHIVE_EXT
# Non-audio production assets are excluded immediately from all scan/analyze queues.
# Source files are never deleted or moved; this is an analysis-only filter.
EXCLUDED_NON_AUDIO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".mid", ".midi", ".xml"}


def resolve_samples_root(selected_path: Path) -> Path:
    """Resolve either Samples or Import Sample Guitar to the Samples root.

    Matching is case-insensitive and tolerates trailing whitespace in the
    directory name. The returned path always contains the incoming directory.
    """
    selected = Path(selected_path).expanduser()
    if not selected.exists():
        raise FileNotFoundError(f"Выбранный путь не существует: {selected}")
    if not selected.is_dir():
        raise NotADirectoryError(f"Выбранный путь не является папкой: {selected}")
    selected = selected.resolve()

    def is_incoming(path: Path) -> bool:
        return path.name.strip().casefold() == "import sample guitar"

    if is_incoming(selected):
        samples_root = selected.parent
        incoming = selected
    else:
        samples_root = selected
        try:
            children = [p for p in samples_root.iterdir()
                        if p.is_dir() and is_incoming(p)]
        except OSError as exc:
            raise OSError(f"Не удалось прочитать выбранную папку: {samples_root}: {exc}") from exc
        if not children:
            # Also tolerate a case-insensitive spelling on filesystems where
            # directory lookup itself is case-sensitive.
            raise FileNotFoundError(
                "В выбранной папке не найдена подпапка 'Import Sample Guitar'. "
                f"Выбранный путь: {samples_root}. Выберите Samples либо саму Import Sample Guitar."
            )
        if len(children) > 1:
            raise RuntimeError(
                "Найдено несколько папок Import Sample Guitar. "
                "Выберите непосредственно нужную папку, чтобы избежать анализа не той библиотеки."
            )
        incoming = children[0]

    if not incoming.is_dir():
        raise FileNotFoundError(f"Папка импорта не найдена или недоступна: {incoming}")
    return samples_root


def _is_excluded(path: Path) -> bool:
    return any(EXCLUDED_LABEL_RE.search(part) for part in path.parts)

def _absolute_path_key(path: Path | str) -> str:
    """Create a stable lexical path key without touching a possibly offline file."""
    try:
        return os.path.normcase(os.path.abspath(os.fspath(path)))
    except (OSError, TypeError, ValueError):
        return str(path).casefold()


def _is_manager_virtual_metadata(path: Path) -> bool:
    """Recognize sidecars created by the manager, not importable audio assets."""
    return any(part.strip().casefold() == "virtual_candidates" for part in path.parts)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite report: {path}")
    temporary.replace(path)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite report: {path}")
    if not rows:
        path.write_text("", encoding="utf-8-sig")
        return
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("x", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)



def quick_scan(samples_root: Path, *, reports_root: Path | None = None,
               progress: Callable[[str], None] | None = None,
               cancel_event: Any = None) -> dict[str, Any]:
    """Fast filesystem-only scan with bounded memory.

    This stage only enumerates directories and reads stat metadata. It never
    hashes, decodes, previews, classifies, copies, moves or deletes source data.
    Inventory rows are streamed directly to CSV; memory use is independent of
    the number of files (apart from the small extension counter and directory
    traversal stack).
    """
    import time

    started = time.perf_counter()
    samples_root = resolve_samples_root(samples_root)
    incoming = next(
        (p for p in samples_root.iterdir()
         if p.is_dir() and p.name.strip().casefold() == "import sample guitar"),
        None,
    )
    if incoming is None:
        raise FileNotFoundError(f"Не найдена папка Import Sample Guitar внутри {samples_root}")
    report_data_root = resolve_runtime_paths(__file__)[1]
    report_base = (reports_root or (report_data_root / "reports")).expanduser().resolve()
    report_base.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    report_dir = report_base / f"quick_scan_{run_id}"
    report_dir.mkdir(parents=True, exist_ok=False)

    def emit(message: str) -> None:
        if progress:
            progress(message)

    emit("БЫСТРОЕ СКАНИРОВАНИЕ: обход папок и файловая метаинформация; без SHA-256, декодирования и аудиоанализа.")
    fields = [
        "relative_path", "filename", "extension", "bytes", "modified_ns",
        "source_path", "scan_status", "source_modified_by_manager",
    ]
    counts: dict[str, int] = defaultdict(int)
    excluded_counts: dict[str, int] = defaultdict(int)
    total_bytes = 0
    files_found = 0
    stat_errors = 0
    directory_errors = 0
    directory_error_details: list[dict[str, str]] = []
    directories_scanned = 0
    stack = [incoming]
    csv_path = report_dir / "quick_inventory.csv"
    with csv_path.open("x", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        while stack:
            if cancel_event is not None and cancel_event.is_set():
                raise RuntimeError("Быстрое сканирование остановлено пользователем.")
            folder = stack.pop()
            try:
                with os.scandir(folder) as entries:
                    for entry in entries:
                        if cancel_event is not None and cancel_event.is_set():
                            raise RuntimeError("Быстрое сканирование остановлено пользователем.")
                        try:
                            if entry.is_dir(follow_symlinks=False):
                                if entry.name.startswith(".manager-import-tmp-"):
                                    continue
                                stack.append(Path(entry.path))
                                continue
                            if not entry.is_file(follow_symlinks=False):
                                continue
                            path = Path(entry.path)
                            relative_path = path.relative_to(incoming)
                            if _is_excluded(relative_path):
                                continue
                            ext = path.suffix.lower() or "[без расширения]"
                            if ext in EXCLUDED_NON_AUDIO_EXTENSIONS:
                                excluded_counts[ext] += 1
                                continue
                            stat = entry.stat(follow_symlinks=False)
                            counts[ext] += 1
                            total_bytes += stat.st_size
                            files_found += 1
                            writer.writerow({
                                "relative_path": str(relative_path),
                                "filename": path.name,
                                "extension": ext,
                                "bytes": stat.st_size,
                                "modified_ns": stat.st_mtime_ns,
                                "source_path": str(path.absolute()),
                                "scan_status": "OK",
                                "source_modified_by_manager": False,
                            })
                        except OSError as exc:
                            stat_errors += 1
                            files_found += 1
                            try:
                                relative = str(Path(entry.path).relative_to(incoming))
                            except (ValueError, OSError):
                                relative = entry.name
                            writer.writerow({
                                "relative_path": relative,
                                "filename": entry.name,
                                "extension": Path(entry.name).suffix.lower(),
                                "bytes": "",
                                "modified_ns": "",
                                "source_path": entry.path,
                                "scan_status": f"ERROR: {type(exc).__name__}: {exc}",
                                "source_modified_by_manager": False,
                            })
                        if files_found and files_found % 100 == 0:
                            emit(f"Быстрый обход: найдено {files_found:,} файлов…")
                directories_scanned += 1
                if directories_scanned == 1 or directories_scanned % 10 == 0:
                    emit(f"Быстрый обход: проверено папок {directories_scanned:,}; файлов {files_found:,}…")
            except OSError as exc:
                directory_errors += 1
                directories_scanned += 1
                directory_error_details.append({
                    "path": str(folder),
                    "stage": "QUICK_DIRECTORY_SCAN",
                    "error": f"{type(exc).__name__}: {exc}",
                })
                emit(f"[ОШИБКА ПАПКИ] Не удалось прочитать {folder}: {type(exc).__name__}: {exc}")
                if folder.resolve() == incoming.resolve():
                    raise OSError(
                        f"Не удаётся прочитать входную папку Import Sample Guitar: {incoming}: {exc}"
                    ) from exc

    elapsed = time.perf_counter() - started
    summary = {
        "manager_version": VERSION,
        "scan_type": "FAST_FILESYSTEM_ONLY",
        "report_directory": str(report_dir),
        "incoming_folder": str(incoming),
        "files_found": files_found,
        "directories_scanned": directories_scanned,
        "stat_errors": stat_errors,
        "directory_errors": directory_errors,
        "directory_error_details": directory_error_details,
        "total_bytes": total_bytes,
        "formats": dict(sorted(counts.items())),
        "excluded_non_audio_files": sum(excluded_counts.values()),
        "excluded_non_audio_formats": dict(sorted(excluded_counts.items())),
        "excluded_extensions": sorted(EXCLUDED_NON_AUDIO_EXTENSIONS),
        "elapsed_seconds": round(elapsed, 3),
        "memory_strategy": "STREAMING_CSV_BOUNDED_MEMORY",
        "sha256_performed": False,
        "audio_decoding_performed": False,
        "acoustic_analysis_performed": False,
        "source_files_modified": False,
        "next_stage": "DEEP_INVENTORY_AND_ANALYSIS",
    }
    _write_json(report_dir / "quick_summary.json", summary)
    _write_json(report_dir / "quick_errors.json", {
        "directory_errors": directory_error_details,
        "stat_error_count": stat_errors,
    })
    emit(
        f"БЫСТРОЕ СКАНИРОВАНИЕ ЗАВЕРШЕНО: {files_found:,} файлов за {elapsed:.2f} сек.; "
        f"ошибок метаданных: {stat_errors}. Отчёт: {report_dir}"
    )
    return summary


def run_manager(samples_root: Path, *, analyze_audio: bool = False,
                guitar_source_confirmed: bool = False,
                write_virtual: bool = False,
                reports_root: Path | None = None,
                progress: Callable[[str], None] | None = None,
                cancel_event: Any = None,
                workers: int | None = None) -> dict[str, Any]:
    """Run a resumable, low-memory read-only inventory and analysis pass.

    Defaults to one worker for older dual-core/8GB systems to keep the PC responsive.
    Callers may explicitly request two workers on faster systems; the hard cap is two.

    SHA-256 values are cached by absolute path + size + mtime_ns. Unchanged
    files are not re-read on subsequent runs. All source files are read-only.
    """
    import hashlib
    import sqlite3
    import threading
    from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

    samples_root = resolve_samples_root(samples_root)
    incoming = next(p for p in samples_root.iterdir()
                    if p.is_dir() and p.name.strip().casefold() == "import sample guitar")
    if write_virtual and not (analyze_audio and guitar_source_confirmed):
        raise ValueError("--write-virtual-index requires --analyze-audio and --guitar-source-confirmed")

    report_data_root = resolve_runtime_paths(__file__)[1]
    report_base = (reports_root or (report_data_root / "reports")).expanduser().resolve()
    report_base.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    reports = report_base / f"run_{run_id}"
    reports.mkdir(parents=True, exist_ok=False)

    def emit(message: str) -> None:
        if progress:
            progress(message)

    if cancel_event is not None and cancel_event.is_set():
        raise RuntimeError("Анализ отменён пользователем до начала.")

    emit(f"Папка импорта найдена: {incoming}. Начинаю глубокий обход папок…")
    all_files: list[Path] = []
    walk_errors: list[dict[str, str]] = []
    directory_stack = [incoming]
    directories_seen = 0
    while directory_stack:
        if cancel_event is not None and cancel_event.is_set():
            raise RuntimeError("Глубокая инвентаризация остановлена пользователем при обходе папок.")
        folder = directory_stack.pop()
        try:
            with os.scandir(folder) as entries:
                for entry in entries:
                    if cancel_event is not None and cancel_event.is_set():
                        raise RuntimeError("Глубокая инвентаризация остановлена пользователем при обходе папок.")
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            if entry.name.startswith(".manager-import-tmp-"):
                                continue
                            directory_stack.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            candidate = Path(entry.path)
                            if candidate.suffix.lower() in EXCLUDED_NON_AUDIO_EXTENSIONS:
                                continue
                            all_files.append(candidate)
                    except OSError as exc:
                        walk_errors.append({
                            "path": entry.path, "stage": "DIRECTORY_ENUMERATION",
                            "error": f"{type(exc).__name__}: {exc}",
                        })
        except OSError as exc:
            walk_errors.append({
                "path": str(folder), "stage": "DIRECTORY_ENUMERATION",
                "error": f"{type(exc).__name__}: {exc}",
            })
        directories_seen += 1
        if directories_seen == 1 or directories_seen % 10 == 0 or len(all_files) % 500 == 0:
            emit(f"Глубокий обход: папок {directories_seen:,}; файлов {len(all_files):,}…")

    excluded = [path for path in all_files if _is_excluded(path.relative_to(incoming))]
    included = [path for path in all_files if not _is_excluded(path.relative_to(incoming))]
    total_files = len(included)
    emit(f"Обход завершён: папок {directories_seen}; найдено файлов: {len(all_files)}; к обработке: {total_files}; исключено по меткам: {len(excluded)}; ошибок доступа: {len(walk_errors)}.")
    emit("ЭТАП 1/4: быстрый обход дерева и подсчёт файлов завершён.")
    emit("ЭТАП 2/4: параллельная инвентаризация, SHA-256 и метаданные. Кэш SHA-256 включён; исходники только читаются.")

    cache_db = report_base / "scan_cache.sqlite3"
    con = sqlite3.connect(str(cache_db), timeout=30)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("""CREATE TABLE IF NOT EXISTS file_hash_cache (
        path TEXT PRIMARY KEY, size INTEGER NOT NULL, mtime_ns INTEGER NOT NULL,
        sha256 TEXT NOT NULL, updated_utc TEXT NOT NULL)""")
    con.execute("""CREATE TABLE IF NOT EXISTS audio_analysis_cache (
        cache_key TEXT PRIMARY KEY, path TEXT NOT NULL, size INTEGER NOT NULL,
        mtime_ns INTEGER NOT NULL, source_sha256 TEXT NOT NULL,
        acoustic_json TEXT NOT NULL, classification_json TEXT NOT NULL,
        updated_utc TEXT NOT NULL)""")
    con.commit()

    # Reuse one read-only SQLite connection per worker. Opening/closing a
    # database connection twice for every file adds avoidable overhead on
    # Windows, especially when scanning thousands of short samples.
    # Worker connections are never shared between worker threads.
    cache_thread_state = threading.local()
    cache_reader_connections: list[sqlite3.Connection] = []
    cache_reader_guard = threading.Lock()

    def get_cache_reader() -> sqlite3.Connection:
        reader = getattr(cache_thread_state, "connection", None)
        if reader is None:
            reader = sqlite3.connect(str(cache_db), timeout=15, check_same_thread=False)
            reader.execute("PRAGMA query_only=ON")
            reader.execute("PRAGMA busy_timeout=15000")
            cache_thread_state.connection = reader
            with cache_reader_guard:
                cache_reader_connections.append(reader)
        return reader

    # The inventory itself is processed with a bounded number of futures;
    # no full path->digest or audio-analysis cache is loaded into RAM.

    def hash_with_cancel(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as stream:
            while True:
                if cancel_event is not None and cancel_event.is_set():
                    raise RuntimeError("Анализ остановлен пользователем.")
                block = stream.read(1024 * 1024)
                if not block:
                    break
                h.update(block)
        return h.hexdigest().upper()

    def process_one(path: Path) -> dict[str, Any]:
        if cancel_event is not None and cancel_event.is_set():
            raise RuntimeError("Анализ остановлен пользователем.")
        stat = path.stat()
        ext = path.suffix.lower()
        relative = str(path.relative_to(incoming))
        # Hash only audio and SFZ assets. Archives and unrelated files are
        # inventoried by metadata; hashing multi-GB archives adds no value to
        # guitar classification and needlessly stalls the scan.
        hash_required = ext in AUDIO_EXT or ext == ".sfz"
        key = str(path.resolve()) if hash_required else ""
        cached = None
        if key:
            cached = get_cache_reader().execute(
                "SELECT size,mtime_ns,sha256 FROM file_hash_cache WHERE path=?",
                (key,),
            ).fetchone()
        if not hash_required:
            digest, hash_source = "", "SKIPPED_NON_AUDIO"
        elif cached and cached[0] == stat.st_size and cached[1] == stat.st_mtime_ns:
            digest, hash_source = cached[2], "CACHE"
        else:
            digest, hash_source = hash_with_cancel(path), "COMPUTED"
        row: dict[str, Any] = {
            "relative_path": relative, "filename": path.name, "extension": ext,
            "bytes": stat.st_size, "sha256": digest, "source_path": str(path.resolve()),
            "source_modified_by_manager": False, "hash_source": hash_source,
        }
        row.update(infer_labels(path))
        audio_record = None
        classification = None
        analysis_cache_record = None
        local_errors = []
        if _is_manager_virtual_metadata(path.relative_to(incoming)):
            row.update(
                category_suggestion="MANAGER_GENERATED_METADATA",
                audio_analysis_status="MANAGER_METADATA",
                classification_status="NOT_AN_AUDIO_ASSET",
                unsupported_reason="Manager-generated virtual range sidecar; source audio is referenced separately.",
            )
        elif ext not in SUPPORTED:
            row.update(category_suggestion="OTHER_REVIEW_REQUIRED",
                       audio_analysis_status="UNSUPPORTED_FORMAT",
                       classification_status="MANUAL_REVIEW_REQUIRED",
                       unsupported_reason="File extension is not currently supported by the analysis pipeline.")
        elif ext in AUDIO_EXT:
            meta = wav_info(path)
            row.update(meta)
            row["category_suggestion"] = (
                "AUDIO_SAMPLE" if meta.get("wav_status") in {"OK", "NON_PCM_OR_EXTENSIBLE"}
                else "OTHER_REVIEW_REQUIRED"
            )
            if analyze_audio and row.get("wav_status") in {"OK", "NON_PCM_OR_EXTENSIBLE"}:
                try:
                    if cancel_event is not None and cancel_event.is_set():
                        raise RuntimeError("Анализ остановлен пользователем.")
                    # Bounded discovery view for acoustics; the optional deep/full
                    # cycle also runs the monophonic tracker on eligible clips so the
                    # Sample/Melody extraction stage receives actual note candidates.
                    # YIN is internally skipped for sources longer than 45 seconds.
                    analysis_key = hashlib.sha256(
                        ("|".join((str(path.resolve()).casefold(), str(stat.st_size),
                                   str(stat.st_mtime_ns), digest, "acoustic-0.4.0",
                                   "classifier-0.3.0", "pitch-events-current", "chord-analysis-0.1.0",
                                   "max_samples=90000"))).encode("utf-8")
                    ).hexdigest()
                    cached_pair = get_cache_reader().execute(
                        "SELECT acoustic_json,classification_json FROM audio_analysis_cache WHERE cache_key=?",
                        (analysis_key,),
                    ).fetchone()
                    cache_status = "MISS"
                    if cached_pair:
                        try:
                            acoustic = json.loads(cached_pair[0])
                            classification = json.loads(cached_pair[1])
                            cache_status = "HIT"
                        except (TypeError, ValueError, json.JSONDecodeError):
                            acoustic = analyse_wav(path, max_samples=90_000)
                            classification = classify_wav(path, analyze_pitch=True, max_samples=90_000)
                            cache_status = "REBUILT_CORRUPT_ENTRY"
                    else:
                        acoustic = analyse_wav(path, max_samples=90_000)
                        classification = classify_wav(path, analyze_pitch=True, max_samples=90_000)
                    chord_analysis = None
                    if guitar_source_confirmed:
                        chord_analysis = acoustic.get("chord_analysis")
                        if not isinstance(chord_analysis, dict):
                            try:
                                from chord_analysis import analyze_chords
                                chord_analysis = analyze_chords(path, source_sha256=digest)
                                acoustic["chord_analysis"] = chord_analysis
                            except Exception as chord_exc:
                                local_errors.append({
                                    "path": relative,
                                    "stage": "CHORD_ANALYSIS",
                                    "error": f"{type(chord_exc).__name__}: {chord_exc}",
                                })
                                chord_analysis = None
                    acoustic["source_sha256"] = digest
                    acoustic["analysis_cache_status"] = cache_status
                    classification["source_sha256"] = digest
                    classification["analysis_cache_status"] = cache_status
                    analysis_cache_record = (
                        analysis_key, str(path.resolve()), stat.st_size, stat.st_mtime_ns,
                        digest, json.dumps(acoustic, ensure_ascii=False, separators=(",", ":")),
                        json.dumps(classification, ensure_ascii=False, separators=(",", ":"))
                    )
                    classification["source_sha256"] = digest
                    classification["classification_status"] = "CANDIDATE_REQUIRES_REVIEW"
                    classification["automatic_factory_promotion"] = False
                    pattern = build_pattern_report(acoustic)
                    audio_record = {
                        "source_path": str(path.resolve()), "source_sha256": digest,
                        "acoustic_analysis": acoustic, "pattern_analysis": pattern,
                        "pitch_candidates": classification.get("fragment_candidates", []),
                        "chord_analysis": chord_analysis,
                        "classification": classification,
                        "filename_metadata": {
                            "note_candidate": row.get("note_candidate", ""),
                            "velocity_candidate": row.get("velocity_candidate", ""),
                            "string_candidate": row.get("string_candidate", ""),
                            "articulation_candidates": row.get("articulation_candidates", ""),
                        },
                        "virtual_extraction": None,
                        "analysis_cache_status": cache_status,
                    }
                    if guitar_source_confirmed and ext in {".wav", ".wave"}:
                        # Pattern Mode uses repeated rhythmic motifs only; broad RMS
                        # active regions are not treated as loops or riffs.
                        virtual = analyze_pattern_ranges(
                            path, pattern, guitar_source_confirmed=True,
                            source_sha256=digest,
                        )
                        audio_record["virtual_extraction"] = virtual
                        # Separate path for expressive/non-repeating loops. This is
                        # onset-group segmentation only: candidates are not asserted
                        # to be notes, chords, complete riffs or musical sections.
                        irregular = analyze_irregular_guitar_phrases(
                            path, acoustic, guitar_source_confirmed=True,
                            source_sha256=digest,
                        )
                        audio_record["irregular_phrase_extraction"] = irregular
                        audio_record["pattern_candidate_total"] = (
                            virtual.get("candidate_count", 0) +
                            irregular.get("candidate_count", 0)
                        )
                        if write_virtual and virtual.get("candidate_count", 0):
                            audio_record["virtual_index_files"] = [
                                str(p) for p in write_virtual_index(virtual, incoming)
                            ]
                        if write_virtual and irregular.get("candidate_count", 0):
                            audio_record["irregular_phrase_index_files"] = [
                                str(p) for p in write_virtual_index(irregular, incoming,
                                    group_name="IRREGULAR_GUITAR_PHRASE_CANDIDATES")
                            ]
                    elif guitar_source_confirmed:
                        audio_record["virtual_extraction_status"] = "SKIPPED_NON_WAV"
                    row["audio_analysis_status"] = "ANALYZED"
                    row["classification_status"] = "CANDIDATE_REQUIRES_REVIEW"
                    row["asset_kind_candidate"] = classification.get("asset_kind_candidate", "UNKNOWN")
                    row["sample_subtype_candidate"] = classification.get("sample_subtype_candidate", "UNKNOWN")
                    row["classification_confidence"] = classification.get("classification_confidence")
                    row["pattern_candidate_count"] = pattern["pattern_analysis"]["candidate_count"]
                    row["chord_candidate_count"] = (
                        chord_analysis.get("chord_candidate_count", 0) if chord_analysis else 0
                    )
                    row["virtual_region_count"] = (
                        audio_record["virtual_extraction"]["candidate_count"]
                        if audio_record["virtual_extraction"] else ""
                    )
                except Exception as exc:
                    if isinstance(exc, RuntimeError) and cancel_event is not None and cancel_event.is_set():
                        raise
                    row["audio_analysis_status"] = "ERROR"
                    local_errors.append({"path": relative, "stage": "AUDIO_ANALYSIS",
                                         "error": f"{type(exc).__name__}: {exc}"})
            elif analyze_audio:
                row["audio_analysis_status"] = "SKIPPED_INVALID_AUDIO"
        elif ext == ".sfz":
            row["category_suggestion"] = "SFZ_INSTRUMENT"
        else:
            row["category_suggestion"] = "ARCHIVE_REVIEW_REQUIRED"
        return {
            "row": row, "audio_record": audio_record, "classification": classification,
            "errors": local_errors,
            "cache": (key, stat.st_size, stat.st_mtime_ns, digest) if hash_required and digest else None,
            "analysis_cache": analysis_cache_record if ext in AUDIO_EXT and analyze_audio else None,
        }

    def safe_process_one(path: Path) -> dict[str, Any]:
        """Convert an unreadable/locked source into a per-file error, not a fatal scan error."""
        try:
            return process_one(path)
        except Exception as exc:
            if cancel_event is not None and cancel_event.is_set():
                raise
            try:
                stat = path.stat()
                size = stat.st_size
            except OSError:
                size = ""
            # Avoid resolving/stat'ing the failed path again while building
            # its error row: network drives and ACL failures can make even a
            # second metadata lookup fail. The lexical absolute path is enough
            # for an auditable per-file failure record.
            try:
                relative = str(path.relative_to(incoming))
            except (ValueError, OSError):
                relative = path.name
            try:
                source_path = str(path.absolute())
            except OSError:
                source_path = str(path)
            return {
                "row": {
                    "relative_path": relative, "filename": path.name,
                    "extension": path.suffix.lower(), "bytes": size, "sha256": "",
                    "source_path": source_path, "source_modified_by_manager": False,
                    "hash_source": "ERROR", "category_suggestion": "MANUAL_REVIEW_REQUIRED",
                    "audio_analysis_status": "FILE_READ_ERROR",
                    "classification_status": "MANUAL_REVIEW_REQUIRED",
                },
                "audio_record": None, "classification": None,
                "errors": [{"path": relative, "stage": "INVENTORY",
                            "error": f"{type(exc).__name__}: {exc}"}],
                "cache": None, "analysis_cache": None,
            }

    inventory: list[dict[str, Any]] = []
    audio_reports: list[dict[str, Any]] = []
    classification_reports: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = list(walk_errors)
    duplicate_groups: dict[str, list[str]] = defaultdict(list)
    # SFZ maps are parsed first so their referenced WAVs can be prioritized.
    sfz_rows: list[dict[str, Any]] = []
    sfz_files = sorted((p for p in included if p.suffix.lower() == ".sfz"),
                       key=lambda p: str(p).casefold())
    for index, sfz in enumerate(sfz_files, 1):
        if cancel_event is not None and cancel_event.is_set():
            raise RuntimeError("Анализ остановлен пользователем на этапе приоритетного SFZ.")
        try:
            sfz_rows.extend(parse_sfz_file(sfz, incoming))
        except Exception as exc:
            errors.append({"path": str(sfz.relative_to(incoming)), "stage": "SFZ_PARSE",
                           "error": f"{type(exc).__name__}: {exc}"})
        if index % 25 == 0:
            emit(f"Приоритетный разбор SFZ: {index}/{len(sfz_files)}…")
    sfz_referenced = {
        _absolute_path_key(str(row.get("resolved_sample") or ""))
        for row in sfz_rows if row.get("status") == "FOUND" and row.get("resolved_sample")
    }
    supported_files = sorted(
        included,
        key=lambda p: (
            0 if p.suffix.lower() == ".sfz" else
            1 if _absolute_path_key(p) in sfz_referenced else
            2 if p.suffix.lower() in AUDIO_EXT else 3,
            str(p).casefold(),
        ),
    )  # SFZ, mapped WAV, other audio, then non-audio metadata.

    # Two I/O workers speed up hashing/inventory on most drives. During
    # acoustic analysis, default to one worker on older dual-core PCs to keep
    # the UI responsive; users can explicitly select two after benchmarking.
    default_workers = 1 if analyze_audio else 2
    worker_count = max(1, min(int(workers if workers is not None else default_workers), 2))
    completed = 0
    pending = set()
    iterator = iter(supported_files)
    try:
        with ThreadPoolExecutor(max_workers=worker_count, thread_name_prefix="LibraryScan") as pool:
            for _ in range(min(len(supported_files), worker_count)):
                try:
                    pending.add(pool.submit(safe_process_one, next(iterator)))
                except StopIteration:
                    break
            while pending:
                if cancel_event is not None and cancel_event.is_set():
                    for future in pending:
                        future.cancel()
                    raise RuntimeError("Анализ остановлен пользователем. Уже обработанные файлы и кэш сохранены.")
                done, pending = wait(pending, timeout=0.5, return_when=FIRST_COMPLETED)
                if not done:
                    continue
                for future in done:
                    result = future.result()
                    row = result["row"]
                    inventory.append(row)
                    if row.get("sha256"):
                        duplicate_groups[row["sha256"]].append(row["relative_path"])
                    if result["audio_record"] is not None:
                        audio_reports.append(result["audio_record"])
                    if result["classification"] is not None:
                        classification_reports.append(result["classification"])
                    errors.extend(result["errors"])
                    if result["cache"] is not None:
                        con.execute(
                            "INSERT OR REPLACE INTO file_hash_cache VALUES(?,?,?,?,?)",
                            (*result["cache"], datetime.now(timezone.utc).isoformat())
                        )
                    if result.get("analysis_cache") is not None:
                        cache_item = result["analysis_cache"]
                        con.execute(
                            "INSERT OR REPLACE INTO audio_analysis_cache VALUES(?,?,?,?,?,?,?,?)",
                            (*cache_item, datetime.now(timezone.utc).isoformat())
                        )
                    completed += 1
                    # Keep the Tk event queue bounded: report progress in
                    # batches, not once per file (12k events can freeze the UI).
                    if completed == 1 or completed % 50 == 0 or completed == len(supported_files):
                        emit(
                            f"Обработка: {completed}/{len(supported_files)} "
                            f"({completed / max(1, len(supported_files)):.0%}); "
                            f"последний файл: {row['filename']}"
                        )
                    try:
                        pending.add(pool.submit(safe_process_one, next(iterator)))
                    except StopIteration:
                        pass
                    if completed % 25 == 0:
                        con.commit()
                con.commit()
        analysis_cache_entries = con.execute(
            "SELECT COUNT(*) FROM audio_analysis_cache"
        ).fetchone()[0]
    except Exception:
        con.commit()
        raise
    finally:
        # Executor shutdown has completed before this block, so each cached
        # reader is idle and can be closed safely from the coordinating thread.
        for cache_reader in cache_reader_connections:
            try:
                cache_reader.close()
            except sqlite3.Error:
                pass
        con.close()

    # Unsupported files remain visible in the inventory; they are never silently dropped.
    supported_rel = {str(p.relative_to(incoming)) for p in supported_files}
    for path in included:
        if str(path.relative_to(incoming)) in supported_rel:
            continue
        try:
            st = path.stat()
            inventory.append({
                "relative_path": str(path.relative_to(incoming)), "filename": path.name,
                "extension": path.suffix.lower(), "bytes": st.st_size, "sha256": "",
                "source_path": str(path.resolve()), "source_modified_by_manager": False,
                "category_suggestion": "OTHER_REVIEW_REQUIRED",
                "audio_analysis_status": "UNSUPPORTED_FORMAT",
                "classification_status": "MANUAL_REVIEW_REQUIRED",
                "unsupported_reason": "Unsupported file type; listed without reading its contents.",
            })
        except Exception as exc:
            errors.append({"path": str(path.relative_to(incoming)), "stage": "STAT",
                           "error": f"{type(exc).__name__}: {exc}"})

    emit(f"ЭТАП 2/4 ЗАВЕРШЁН: {len(inventory)} файлов, ошибок: {len(errors)}. ЭТАП 3/4: SFZ уже разобран первым; проверяю ссылки…")

    duplicates = [
        {"sha256": digest, "count": len(paths), "paths": paths}
        for digest, paths in sorted(duplicate_groups.items()) if len(paths) > 1
    ]
    emit("ЭТАП 3/4 ЗАВЕРШЁН: SFZ-проверка. ЭТАП 4/4: аудит OTHER и подготовка отчётов…")
    try:
        other_audit_summary = audit_other_library(samples_root, reports / "other_audit")
    except Exception as exc:
        other_audit_summary = {"errors": 1, "error": f"{type(exc).__name__}: {exc}"}
        errors.append({"path": str(samples_root / "OTHER"), "stage": "OTHER_AUDIT",
                       "error": f"{type(exc).__name__}: {exc}"})
    pattern_manifest = build_pattern_engine_manifest()
    manifest_errors = validate_pattern_engine_manifest(pattern_manifest)
    if manifest_errors:
        raise RuntimeError("Invalid Pattern Mode manifest template: " + "; ".join(manifest_errors))

    mode_sorting = build_mode_sorting_report(audio_reports)
    # Separate index of explicitly human-reviewed staged assets. This connects
    # manual mode assignments to the same ten queues without trusting hypotheses.
    mode_assignment_index = build_mode_assignment_index(runtime_staging_root(__file__))
    mode_candidate_counts = {
        item["mode"]: item["candidate_count"] for item in mode_sorting["modes"]
    }
    mode_candidate_rows = [
        {"mode": item["mode"], **candidate}
        for item in mode_sorting["modes"] for candidate in item["candidates"]
    ]

    summary = {
        "manager_version": VERSION, "run_id": run_id,
        "report_directory": str(reports), "samples_root": str(samples_root),
        "incoming_folder": str(incoming), "files_scanned": len(inventory),
        "files_excluded_by_piano_bell_drum_path_label": len(excluded),
        "wav_files": sum(row.get("extension") in AUDIO_EXT for row in inventory),
        "sfz_files": sum(row.get("extension") == ".sfz" for row in inventory),
        "archives_for_manual_review": sum(row.get("extension") in ARCHIVE_EXT for row in inventory),
        "exact_duplicate_groups": len(duplicates), "sfz_sample_references": len(sfz_rows),
        "sfz_missing_references": sum(row.get("status") == "MISSING" for row in sfz_rows),
        "sfz_outside_library_references": sum(row.get("status") == "OUTSIDE_LIBRARY" for row in sfz_rows),
        "audio_analysis_enabled": analyze_audio,
        "guitar_source_manually_confirmed": guitar_source_confirmed,
        "audio_files_analyzed": len(audio_reports),
        "asset_classifications_created": len(classification_reports),
        "mode_sorting_report": "mode_sorting_report.json",
        "mode_candidate_counts": mode_candidate_counts,
        "mode_candidates_total": mode_sorting["total_candidates"],
        "reviewed_mode_assignment_index": "reviewed_mode_assignment_index.json",
        "reviewed_mode_assignment_count": mode_assignment_index["assignment_count"],
        "reviewed_mode_assignment_status": mode_assignment_index["status"],
        "chord_sample_candidates": sum(
            (item.get("chord_analysis") or {}).get("chord_candidate_count", 0)
            for item in audio_reports
        ),
        "classification_policy": "CANDIDATE_ONLY_REQUIRES_HUMAN_REVIEW",
"pattern_engine_manifest": "pattern_engine_manifest.json",
        "pattern_engine_manifest_status": pattern_manifest["status"],
        "repeated_rhythm_pattern_candidates": sum(
            item["pattern_analysis"]["pattern_analysis"]["candidate_count"] for item in audio_reports
        ),
        "pattern_mode_candidates": sum(
            item["virtual_extraction"]["candidate_count"]
            for item in audio_reports if item["virtual_extraction"] is not None
        ),
        # Backward-compatible field name; candidates now represent repeated
        # rhythmic motifs, not broad RMS-active regions.
        "virtual_active_region_candidates": sum(
            item["virtual_extraction"]["candidate_count"]
            for item in audio_reports if item["virtual_extraction"] is not None
        ),
        "errors": len(errors),
        "other_audit": other_audit_summary,
        "unsupported_import_files": sum(row.get("audio_analysis_status") == "UNSUPPORTED_FORMAT" for row in inventory),
        "manager_generated_metadata_files": sum(row.get("audio_analysis_status") == "MANAGER_METADATA" for row in inventory),
        "source_files_modified": False, "source_files_moved_or_deleted": False,
        "automatic_factory_promotion": False,
        "hash_cache": str(cache_db),
        "audio_analysis_cache": str(cache_db),
        "audio_analysis_cache_entries": analysis_cache_entries,
        "workers": worker_count,
        "note": "All source files are read-only. Candidates require musical review and independent license approval.",
    }

    _write_csv(reports / "unified_inventory.csv", sorted(inventory, key=lambda x: x["relative_path"].lower()))
    _write_csv(reports / "unified_sfz_references.csv", sfz_rows)
    _write_json(reports / "unified_exact_duplicates.json", duplicates)
    _write_json(reports / "unified_audio_analysis.json", audio_reports)
    _write_json(reports / "unified_asset_classification.json", classification_reports)
    _write_json(reports / "mode_sorting_report.json", mode_sorting)
    _write_json(reports / "reviewed_mode_assignment_index.json", mode_assignment_index)
    _write_csv(reports / "mode_candidates.csv", mode_candidate_rows)
    _write_json(reports / "pattern_engine_manifest.json", pattern_manifest)
    _write_json(reports / "unified_errors.json", errors)
    _write_json(reports / "unified_summary.json", summary)
    emit(f"ВСЕ 4 ЭТАПА ЗАВЕРШЕНЫ. Обработано: {len(inventory)}; ошибок: {len(errors)}. Отчёт: {reports}")
    return summary

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified safe Library Manager: inventory, SFZ audit and optional audio analysis."
    )
    parser.add_argument("--samples", type=Path,
                        default=Path(__file__).resolve().parent.parent / "Samples")
    parser.add_argument("--analyze-audio", action="store_true",
                        help="Run acoustic/rhythm/repeated-pattern analysis on valid WAV files.")
    parser.add_argument("--guitar-source-confirmed", action="store_true",
                        help="Operator confirms that input has already excluded Piano, Bell and Drum.")
    parser.add_argument("--write-virtual-index", action="store_true",
                        help="Write non-audio JSON range sidecars under Import Sample Guitar (never slices WAV).")
    parser.add_argument("--workers", type=int, choices=(1, 2), default=None,
                        help="Parallel workers: default 2 for inventory-only, 1 during heavy audio analysis.")
    args = parser.parse_args()
    try:
        summary = run_manager(
            args.samples,
            analyze_audio=args.analyze_audio,
            guitar_source_confirmed=args.guitar_source_confirmed,
            write_virtual=args.write_virtual_index,
            workers=args.workers,
        )
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Reports: {summary['report_directory']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
