#!/usr/bin/env python3
"""POP PUNK GUITAR LIBRARY MANAGER ULTIMATE — safe inventory engine 0.2.0.
Scan-only: never moves, renames, deletes, or overwrites source files.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, re, sqlite3, struct, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from sfz_parser import parse_sfz_file

AUDIO_EXT = {".wav", ".wave", ".aif", ".aiff", ".flac", ".ogg", ".oga", ".mp3"}
SFZ_EXT = {".sfz"}
ARCHIVE_EXT = {".zip", ".7z", ".rar"}
SUPPORTED = AUDIO_EXT | SFZ_EXT | ARCHIVE_EXT
NOTE_RE = re.compile(r"(?i)(?:^|[\s_\-\[\(])([A-G](?:#|b)?)(-?\d{1,2})(?:$|[\s_\-\]\)])")
VELOCITY_RE = re.compile(r"(?i)(?:vel|velocity|v)(?:ocity)?[_\-\s]*(\d{1,3})")
STRING_RE = re.compile(r"(?i)(?:string|str|s)[_\-\s]*([1-6])")
ARTICULATION_WORDS = ("palm", "mute", "pm", "harmonic", "slide", "pick", "finger",
                      "sustain", "release", "staccato", "legato", "choke", "up", "down")
# Exclude clearly non-guitar instrument labels from the guitar-library scan.
EXCLUDED_LABELS = {"piano", "bell", "drum"}
EXCLUDED_LABEL_RE = re.compile(r"(?i)(?<![a-z0-9])(piano|bell|drum)(?![a-z0-9])")

def is_excluded_label(path: Path) -> bool:
    """Return True when any path component contains a standalone excluded label."""
    return any(EXCLUDED_LABEL_RE.search(part) for part in path.parts)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()

def wav_info(path: Path) -> dict:
    """Return audio metadata for WAV and libsndfile-supported formats.

    The legacy field names are retained for compatibility with existing reports
    and callers. Non-WAV formats are decoded only through python-soundfile;
    unsupported codecs are reported instead of silently ignored.
    """
    path = Path(path)
    result = {"wav_status": "UNKNOWN", "sample_rate": "", "channels": "",
              "bit_depth": "", "frames": "", "duration_seconds": "",
              "audio_format": path.suffix.lower().lstrip(".").upper(),
              "audio_subtype": ""}
    if path.suffix.lower() not in {".wav", ".wave"}:
        try:
            import soundfile as sf
            info = sf.info(str(path))
            if info.frames <= 0 or info.samplerate <= 0 or info.channels <= 0:
                result["wav_status"] = "INVALID_OR_EMPTY_AUDIO"
                return result
            result.update(
                wav_status="OK",
                sample_rate=int(info.samplerate),
                channels=int(info.channels),
                bit_depth=info.subtype or "UNKNOWN",
                frames=int(info.frames),
                duration_seconds=round(info.frames / info.samplerate, 6),
                audio_format=info.format or result["audio_format"],
                audio_subtype=info.subtype or "UNKNOWN",
                decoder_backend="libsndfile",
            )
            return result
        except ImportError:
            result["wav_status"] = "DECODER_NOT_BUNDLED"
            result["unsupported_reason"] = "This format requires the bundled soundfile/libsndfile decoder."
            return result
        except Exception as exc:
            result["wav_status"] = "DECODE_ERROR:" + type(exc).__name__
            result["unsupported_reason"] = str(exc)[:240]
            return result

    try:
        with path.open("rb") as f:
            head = f.read(12)
            if len(head) < 12 or head[:4] not in (b"RIFF", b"RIFX") or head[8:12] != b"WAVE":
                result["wav_status"] = "INVALID_RIFF_WAVE"
                return result
            endian = ">" if head[:4] == b"RIFX" else "<"
            fmt = None
            data_size = None
            while True:
                chunk = f.read(8)
                if len(chunk) < 8: break
                cid, size = chunk[:4], struct.unpack(endian + "I", chunk[4:])[0]
                if cid == b"fmt ":
                    raw = f.read(min(size, 64))
                    if len(raw) >= 16:
                        audio_fmt, channels, rate, byte_rate, align, bits = struct.unpack(endian + "HHIIHH", raw[:16])
                        fmt = (audio_fmt, channels, rate, align, bits)
                    if size > len(raw): f.seek(size - len(raw), 1)
                elif cid == b"data":
                    data_size = size
                    f.seek(size, 1)
                else: f.seek(size, 1)
                if size & 1: f.seek(1, 1)
            if not fmt:
                result["wav_status"] = "MISSING_FMT_CHUNK"
                return result
            audio_fmt, channels, rate, align, bits = fmt
            frames = int(data_size / align) if data_size is not None and align else 0
            result.update(sample_rate=rate, channels=channels, bit_depth=bits, frames=frames,
                          duration_seconds=round(frames / rate, 6) if rate else "",
                          wav_status="OK" if data_size is not None else "MISSING_DATA_CHUNK",
                          audio_format="WAV", audio_subtype=f"{bits}-bit")
            if audio_fmt not in (1, 3, 0xFFFE): result["wav_status"] = "NON_PCM_OR_EXTENSIBLE"
    except Exception as e:
        result["wav_status"] = "READ_ERROR:" + type(e).__name__
    return result

def infer_labels(path: Path) -> dict:
    text = (path.stem + " " + str(path.parent)).lower()
    m = NOTE_RE.search(path.stem)
    note = (m.group(1).upper() + m.group(2)) if m else ""
    vm, sm = VELOCITY_RE.search(text), STRING_RE.search(text)
    arts = [w for w in ARTICULATION_WORDS if re.search(
        r"(?i)(?:^|[\s_\-])" + re.escape(w) + r"(?:$|[\s_\-])", text)]
    return {"note_candidate": note, "velocity_candidate": vm.group(1) if vm else "",
            "string_candidate": sm.group(1) if sm else "", "articulation_candidates": ";".join(arts)}

def parse_sfz(path: Path, root: Path) -> list[dict]:
    """Compatibility wrapper around the structured SFZ parser."""
    return parse_sfz_file(path, root)


def load_cache(db: Path):
    con = sqlite3.connect(db)
    con.execute("""CREATE TABLE IF NOT EXISTS file_cache(
        path TEXT PRIMARY KEY, size INTEGER NOT NULL, mtime_ns INTEGER NOT NULL,
        sha256 TEXT NOT NULL, updated REAL NOT NULL)""")
    con.commit()
    return con

def cached_hash(con, path: Path, st):
    row = con.execute("SELECT sha256 FROM file_cache WHERE path=? AND size=? AND mtime_ns=?",
                      (str(path), st.st_size, st.st_mtime_ns)).fetchone()
    return row[0] if row else None

def update_cache(con, path: Path, st, digest):
    con.execute("INSERT OR REPLACE INTO file_cache VALUES(?,?,?,?,?)",
                (str(path), st.st_size, st.st_mtime_ns, digest, time.time()))

def main():
    ap = argparse.ArgumentParser(description="Safe WAV/SFZ inventory and integrity scanner.")
    ap.add_argument("--samples", type=Path, default=None)
    ap.add_argument("--workers", type=int, default=max(1, min(8, os.cpu_count() or 2)))
    ap.add_argument("--no-cache", action="store_true")
    args = ap.parse_args()
    script_dir = Path(__file__).resolve().parent
    samples = (args.samples or (script_dir.parent / "Samples")).expanduser().resolve()
    incoming = samples / "Import Sample Guitar"
    reports = script_dir / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    if not incoming.is_dir():
        print("ERROR: incoming folder not found:", incoming)
        print("Expected: Samples/Import Sample Guitar")
        return 2
    all_files = sorted(p for p in incoming.rglob("*") if p.is_file())
    excluded_files = [p for p in all_files if is_excluded_label(p.relative_to(incoming))]
    files = [p for p in all_files if not is_excluded_label(p.relative_to(incoming))]
    con = None if args.no_cache else load_cache(reports / "scan_cache.sqlite3")
    jobs = []
    for p in files:
        if p.suffix.lower() not in SUPPORTED: continue
        st = p.stat()
        jobs.append((p, st, cached_hash(con, p, st) if con else None))
    def work(item):
        p, st, digest = item
        if digest is None: digest = sha256_file(p)
        meta = wav_info(p) if p.suffix.lower() in AUDIO_EXT else {}
        return p, st, digest, meta
    print(f"Scanning {len(jobs)} supported files with {max(1,args.workers)} worker(s)...")
    rows = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(work, item) for item in jobs]
        for i, future in enumerate(as_completed(futures), 1):
            p, st, digest, meta = future.result()
            ext = p.suffix.lower()
            category = "SFZ_INSTRUMENT" if ext in SFZ_EXT else ("AUDIO_SAMPLE" if ext in AUDIO_EXT else "ARCHIVE_REVIEW_REQUIRED")
            if ext in AUDIO_EXT and meta.get("wav_status") not in ("OK", "NON_PCM_OR_EXTENSIBLE"):
                category = "OTHER_REVIEW_REQUIRED"
            rows.append({"relative_path": str(p.relative_to(incoming)), "filename": p.name,
                         "extension": ext, "bytes": st.st_size, "sha256": digest,
                         "category_suggestion": category, **meta, **infer_labels(p)})
            if con: update_cache(con, p, st, digest)
            if i % 100 == 0: print(f"  {i}/{len(jobs)}")
    if con: con.commit(); con.close()
    sfz_rows = []
    for p in (x for x in files if x.suffix.lower() in SFZ_EXT):
        sfz_rows.extend(parse_sfz(p, incoming))
    by_hash = {}
    for row in rows: by_hash.setdefault(row["sha256"], []).append(row["relative_path"])
    duplicates = [{"sha256": h, "count": len(paths), "paths": paths}
                  for h, paths in by_hash.items() if len(paths) > 1]
    def write_csv(path, data):
        if not data: path.write_text("", encoding="utf-8-sig"); return
        fieldnames = list(dict.fromkeys(key for row in data for key in row.keys()))
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            w.writerows(data)
    write_csv(reports / "inventory.csv", sorted(rows, key=lambda x: x["relative_path"].lower()))
    write_csv(reports / "sfz_sample_references.csv", sfz_rows)
    (reports / "exact_duplicates.json").write_text(json.dumps(duplicates, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {"version":"0.2.0", "samples_root":str(samples), "incoming_folder":str(incoming),
               "files_scanned":len(rows), "files_excluded_by_label":len(excluded_files),
               "excluded_labels":sorted(EXCLUDED_LABELS), "wav_files":sum(r["extension"] in AUDIO_EXT for r in rows),
               "sfz_files":sum(r["extension"] in SFZ_EXT for r in rows),
               "archives_for_manual_review":sum(r["extension"] in ARCHIVE_EXT for r in rows),
               "exact_duplicate_groups":len(duplicates), "sfz_sample_references":len(sfz_rows),
               "sfz_missing_references":sum(r["status"]=="MISSING" for r in sfz_rows),
               "sfz_outside_library_references":sum(r["status"]=="OUTSIDE_LIBRARY" for r in sfz_rows),
               "sfz_missing_includes":sum(r["status"]=="INCLUDE_MISSING" for r in sfz_rows),
               "sfz_include_cycles":sum(r["status"]=="INCLUDE_CYCLE" for r in sfz_rows),
               "sfz_read_errors":sum(str(r["status"]).startswith("SFZ_READ_ERROR") for r in sfz_rows),
               "note":"Scan-only. Piano/Bell/Drum-labeled paths are excluded; no source files were moved, renamed, deleted, or overwritten."}
    (reports / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("Reports:", reports)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
