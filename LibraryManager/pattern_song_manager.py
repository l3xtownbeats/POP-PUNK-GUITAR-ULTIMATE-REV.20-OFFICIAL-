#!/usr/bin/env python3
"""PPGU Pattern Song library: reviewed song groups and playable pattern metadata.

This module prepares pattern/song metadata for the future VST3 Pattern Instrument.
It does not time-stretch audio, fabricate chord transcriptions, or approve assets.
"""
from __future__ import annotations

import json
import math
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "ppgu.pattern_song_library/1.0.0"
ROLES = ("VERSE", "PRE_CHORUS", "CHORUS", "BRIDGE", "INTRO", "OUTRO", "FILL", "CUSTOM")
ARTICULATIONS = (
    "DOWNSTROKE", "UPSTROKE", "PALM_MUTE", "OPEN", "HAMMER_ON",
    "PULL_OFF", "SLIDE", "LEGATO", "ACCENT", "STOP", "UNKNOWN",
)
DEFAULT_SONG_PATTERN_TARGET = 8
MAX_SONG_PATTERNS = 32


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_library() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "project": "POP PUNK GUITAR ULTIMATE",
        "updated_at_utc": _utc_now(),
        "time_stretch": False,
        "doubling_supported": True,
        "songs": [],
    }


def load_library(path: Path) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return new_library()
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_library(data)
    return data


def save_library(path: Path, data: dict[str, Any]) -> None:
    validate_library(data)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at_utc"] = _utc_now()
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def create_song(name: str, *, style: str = "", notes: str = "") -> dict[str, Any]:
    name = str(name).strip()
    if not name:
        raise ValueError("Song name cannot be empty")
    return {
        "song_id": uuid.uuid4().hex[:16].upper(),
        "name": name,
        "style": str(style).strip(),
        "notes": str(notes).strip(),
        "patterns": [],
    }


def add_pattern(
    song: dict[str, Any],
    *,
    name: str,
    wav_path: str,
    role: str = "CUSTOM",
    selector_note: int | None = None,
    tempo_min_bpm: float | None = None,
    tempo_max_bpm: float | None = None,
    numerator: int | None = None,
    denominator: int | None = None,
    shift_beats: float = 0.0,
    end_beats: float | None = None,
    chord_qualities: list[str] | None = None,
    articulations: list[str] | None = None,
    events: list[dict[str, Any]] | None = None,
    license_status: str = "UNREVIEWED",
    review_status: str = "NEEDS_MUSICAL_REVIEW",
    doubling_enabled: bool = False,
    doubling_gain_db: float = -6.0,
    doubling_timing_ms: float = 12.0,
) -> dict[str, Any]:
    if len(song.get("patterns", [])) >= MAX_SONG_PATTERNS:
        raise ValueError(f"A song may contain at most {MAX_SONG_PATTERNS} patterns")
    name, wav_path = str(name).strip(), str(wav_path).strip()
    if not name or not wav_path:
        raise ValueError("Pattern name and WAV path are required")
    role = str(role).upper()
    if role not in ROLES:
        raise ValueError(f"Unsupported song role: {role}")
    if selector_note is not None and (type(selector_note) is not int or not 0 <= selector_note <= 127):
        raise ValueError("Selector note must be a MIDI note from 0 to 127")
    for label, value in (("tempo_min_bpm", tempo_min_bpm), ("tempo_max_bpm", tempo_max_bpm)):
        if value is not None and (not isinstance(value, (int, float)) or not 30 <= value <= 300):
            raise ValueError(f"{label} must be between 30 and 300 BPM")
    if tempo_min_bpm is not None and tempo_max_bpm is not None and tempo_min_bpm > tempo_max_bpm:
        raise ValueError("Minimum tempo cannot exceed maximum tempo")
    if numerator is not None and (type(numerator) is not int or not 1 <= numerator <= 32):
        raise ValueError("Time-signature numerator must be 1..32")
    if denominator is not None and (type(denominator) is not int or denominator not in {1, 2, 4, 8, 16, 32}):
        raise ValueError("Time-signature denominator must be 1, 2, 4, 8, 16 or 32")
    if not isinstance(shift_beats, (int, float)) or not math.isfinite(shift_beats):
        raise ValueError("Shift must be a finite beat offset")
    if end_beats is not None and (not isinstance(end_beats, (int, float)) or not math.isfinite(end_beats) or end_beats <= 0):
        raise ValueError("End must be a positive beat length")
    if not isinstance(doubling_gain_db, (int, float)) or not -24 <= doubling_gain_db <= 0:
        raise ValueError("Doubling gain must be between -24 and 0 dB")
    if not isinstance(doubling_timing_ms, (int, float)) or not 0 <= doubling_timing_ms <= 40:
        raise ValueError("Doubling timing offset must be between 0 and 40 ms")
    arts = [str(x).upper() for x in (articulations or ["UNKNOWN"])]
    if any(x not in ARTICULATIONS for x in arts):
        raise ValueError("Unknown articulation in pattern metadata")
    pattern = {
        "pattern_id": uuid.uuid4().hex[:16].upper(),
        "name": name,
        "role": role,
        "wav_path": wav_path,
        "selector_midi_note": selector_note,
        "tempo_range_bpm": {"min": tempo_min_bpm, "max": tempo_max_bpm},
        "time_signature": {"numerator": numerator, "denominator": denominator},
        "shift_beats": float(shift_beats),
        "end_beats": float(end_beats) if end_beats is not None else None,
        "time_stretch": False,
        "tempo_policy": "NATIVE_AUDIO_RATE_NO_TIME_STRETCH",
        "natural_tempo_guidance_bpm": [60, 160],
        "chord_compatibility": {
            "qualities": sorted({str(x).upper() for x in (chord_qualities or [])}),
            "mapping_status": "REQUIRES_REVIEW",
            "adaptation_method": "REVIEWED_PITCH_EVENT_AND_VOICING_MAP_ONLY",
            "whole_chord_wav_transposition_allowed": False,
        },
        "articulations": arts,
        "articulation_events": list(events or []),
        "transition_noise_policy": "PRESERVE_REVIEWED_FRET_AND_HAND_NOISE",
        "rhythm_search_signature": [],
        "doubling": {
            "enabled": bool(doubling_enabled),
            "mode": "NATURAL_SECOND_TAKE",
            "gain_db": float(doubling_gain_db),
            "timing_offset_ms": float(doubling_timing_ms),
            "independent_voice": True,
        },
        "review_status": str(review_status),
        "license_status": str(license_status),
        "runtime_ready": False,
        "runtime_blockers": [
            "Pattern performance event timeline requires musical review.",
            "Chord adaptation map requires confirmed note/voicing data.",
            "VST3 playback engine and transition handling are not yet implemented.",
        ],
    }
    song.setdefault("patterns", []).append(pattern)
    return pattern


def validate_library(data: dict[str, Any]) -> None:
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("Unsupported Pattern Song library schema")
    songs = data.get("songs")
    if not isinstance(songs, list):
        raise ValueError("songs must be a list")
    song_ids = set()
    pattern_ids = set()
    selector_keys = set()
    for song in songs:
        if not isinstance(song, dict) or not str(song.get("name") or "").strip():
            raise ValueError("Every song must have a name")
        song_id = song.get("song_id")
        if not song_id or song_id in song_ids:
            raise ValueError("Song IDs must be unique and non-empty")
        song_ids.add(song_id)
        patterns = song.get("patterns")
        if not isinstance(patterns, list) or len(patterns) > MAX_SONG_PATTERNS:
            raise ValueError("Song patterns must be a list within the configured limit")
        for pattern in patterns:
            if not isinstance(pattern, dict) or not pattern.get("pattern_id") or not pattern.get("wav_path"):
                raise ValueError("Pattern is missing its ID or WAV path")
            if pattern["pattern_id"] in pattern_ids:
                raise ValueError("Pattern IDs must be unique")
            pattern_ids.add(pattern["pattern_id"])
            selector = pattern.get("selector_midi_note")
            if selector is not None:
                if type(selector) is not int or not 0 <= selector <= 127:
                    raise ValueError("Invalid pattern selector MIDI note")
                if selector in selector_keys:
                    raise ValueError("Pattern selector MIDI notes must be unique across this library")
                selector_keys.add(selector)
            if pattern.get("time_stretch") is not False:
                raise ValueError("Time-stretch is prohibited for recorded patterns")
            if pattern.get("tempo_policy") != "NATIVE_AUDIO_RATE_NO_TIME_STRETCH":
                raise ValueError("Pattern tempo policy must preserve the original recording rate")
            chord = pattern.get("chord_compatibility") or {}
            if chord.get("whole_chord_wav_transposition_allowed") is not False:
                raise ValueError("Whole chord WAV transposition is prohibited")
            doubling = pattern.get("doubling") or {}
            if doubling.get("mode") != "NATURAL_SECOND_TAKE" or doubling.get("independent_voice") is not True:
                raise ValueError("Doubling must be represented as an independent second voice")


def rhythm_distance(reference: list[float], candidate: list[float]) -> float:
    """Compare onset intervals with normalized scale; supports shifted starts."""
    if not reference or not candidate:
        return float("inf")
    a = [float(x) for x in reference]
    b = [float(x) for x in candidate]
    if any(x <= 0 or not math.isfinite(x) for x in a + b):
        raise ValueError("Rhythm intervals must be finite positive durations")
    def normalize(values: list[float]) -> list[float]:
        mean = sum(values) / len(values)
        return [x / mean for x in values]
    na, nb = normalize(a), normalize(b)
    n = max(len(na), len(nb))
    # Circular alignment handles a tap beginning on a different beat.
    best = float("inf")
    for shift in range(len(nb)):
        rotated = nb[shift:] + nb[:shift]
        m = min(len(na), len(rotated))
        cost = sum(abs(na[i] - rotated[i]) for i in range(m)) / m
        cost += abs(len(na) - len(rotated)) * 0.35
        best = min(best, cost)
    return best


def search_similar_patterns(library: dict[str, Any], tapped_intervals: list[float], limit: int = 20) -> list[dict[str, Any]]:
    validate_library(library)
    if type(limit) is not int or not 1 <= limit <= 200:
        raise ValueError("limit must be between 1 and 200")
    matches = []
    for song in library["songs"]:
        for pattern in song["patterns"]:
            signature = pattern.get("rhythm_search_signature") or []
            if not signature:
                continue
            distance = rhythm_distance(tapped_intervals, signature)
            matches.append({
                "song_id": song["song_id"], "song_name": song["name"],
                "pattern_id": pattern["pattern_id"], "pattern_name": pattern["name"],
                "role": pattern["role"], "distance": round(distance, 6),
                "selector_midi_note": pattern.get("selector_midi_note"),
            })
    return sorted(matches, key=lambda item: (item["distance"], item["song_name"], item["pattern_name"]))[:limit]


def tap_intervals(tap_times_seconds: list[float]) -> list[float]:
    if len(tap_times_seconds) < 3:
        raise ValueError("At least three taps are required to estimate a rhythm")
    times = [float(x) for x in tap_times_seconds]
    if any(not math.isfinite(x) for x in times) or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("Tap timestamps must be finite and strictly increasing")
    return [b - a for a, b in zip(times, times[1:])]


def open_pattern_song_manager(parent, library_path: Path) -> None:
    """Open a small Tk editor for Songs/Patterns metadata; never edits source WAVs."""
    import tkinter as tk
    import time
    from tkinter import filedialog, messagebox, simpledialog, ttk

    path = Path(library_path)
    try:
        library = load_library(path)
    except Exception as exc:
        messagebox.showerror("Pattern Song Manager", str(exc), parent=parent)
        return

    window = tk.Toplevel(parent)
    window.title("PPGU — Pattern Song Manager")
    window.geometry("980x620")
    window.transient(parent)

    top = ttk.Frame(window, padding=10)
    top.pack(fill="both", expand=True)
    ttk.Label(top, text="PATTERN SONGS — группы паттернов по песням", font=("Segoe UI", 14, "bold")).pack(anchor="w")
    ttk.Label(top, text="Без time-stretch • Shift / End • Key Switch • Rhythm Search • Chord adaptation • Natural Doubling").pack(anchor="w", pady=(0, 8))

    body = ttk.Frame(top)
    body.pack(fill="both", expand=True)
    left = ttk.LabelFrame(body, text="Songs / Patterns", padding=6)
    left.pack(side="left", fill="both", expand=True)
    tree = ttk.Treeview(left, columns=("role", "key", "status"), show="tree headings", height=18)
    tree.heading("#0", text="Название")
    for col, title in (("role", "Роль"), ("key", "Key Switch"), ("status", "Проверка")):
        tree.heading(col, text=title)
        tree.column(col, width=105, anchor="w")
    tree.pack(fill="both", expand=True)

    right = ttk.LabelFrame(body, text="Параметры выбранного паттерна", padding=8)
    right.pack(side="right", fill="y", padx=(8, 0))
    fields = {}
    field_specs = [
        ("role", "Роль", "CUSTOM"), ("selector", "Key Switch MIDI", ""),
        ("tempo_min", "Tempo min BPM", ""), ("tempo_max", "Tempo max BPM", ""),
        ("meter_num", "Размер: числитель", ""), ("meter_den", "Размер: знаменатель", ""),
        ("shift", "Shift (beats)", "0"), ("end", "End (beats)", ""),
        ("chords", "Аккорды (через запятую)", ""),
        ("articulations", "Артикуляции", "UNKNOWN"),
        ("rhythm", "Rhythm intervals (ms)", ""),
    ]
    for row, (key, label, default) in enumerate(field_specs):
        ttk.Label(right, text=label).grid(row=row, column=0, sticky="w", pady=2)
        var = tk.StringVar(value=default)
        fields[key] = var
        if key == "role":
            widget = ttk.Combobox(right, textvariable=var, values=ROLES, state="readonly", width=24)
        else:
            widget = ttk.Entry(right, textvariable=var, width=27)
        widget.grid(row=row, column=1, sticky="ew", pady=2)
    doubling = tk.BooleanVar(value=False)
    ttk.Checkbutton(right, text="Natural Doubling (второй дубль)", variable=doubling).grid(row=len(field_specs), column=0, columnspan=2, sticky="w", pady=6)
    ttk.Label(right, text="Дубль: отдельный голос, небольшой сдвиг тайминга/динамики.").grid(row=len(field_specs)+1, column=0, columnspan=2, sticky="w")
    ttk.Label(right, text="Time-stretch выключен: темп вне диапазона звучит менее естественно.", wraplength=320).grid(row=len(field_specs)+2, column=0, columnspan=2, sticky="w", pady=4)

    selected = {"song": None, "pattern": None}

    def refresh():
        tree.delete(*tree.get_children())
        for song in library["songs"]:
            sid = tree.insert("", "end", iid=song["song_id"], text=song["name"], values=("SONG", "", ""), open=True)
            for pattern in song["patterns"]:
                tree.insert(sid, "end", iid=pattern["pattern_id"], text=pattern["name"],
                            values=(pattern["role"], pattern.get("selector_midi_note") or "", pattern.get("review_status", "")))

    def select_item(_event=None):
        item = tree.focus()
        parent_id = tree.parent(item)
        if not parent_id:
            selected.update(song=next((s for s in library["songs"] if s["song_id"] == item), None), pattern=None)
            return
        song = next((s for s in library["songs"] if s["song_id"] == parent_id), None)
        pattern = next((p for p in song["patterns"] if p["pattern_id"] == item), None) if song else None
        selected.update(song=song, pattern=pattern)
        if not pattern:
            return
        fields["role"].set(pattern["role"])
        fields["selector"].set("" if pattern.get("selector_midi_note") is None else str(pattern["selector_midi_note"]))
        fields["tempo_min"].set("" if pattern["tempo_range_bpm"]["min"] is None else str(pattern["tempo_range_bpm"]["min"]))
        fields["tempo_max"].set("" if pattern["tempo_range_bpm"]["max"] is None else str(pattern["tempo_range_bpm"]["max"]))
        fields["meter_num"].set("" if pattern["time_signature"]["numerator"] is None else str(pattern["time_signature"]["numerator"]))
        fields["meter_den"].set("" if pattern["time_signature"]["denominator"] is None else str(pattern["time_signature"]["denominator"]))
        fields["shift"].set(str(pattern["shift_beats"]))
        fields["end"].set("" if pattern["end_beats"] is None else str(pattern["end_beats"]))
        fields["chords"].set(", ".join(pattern["chord_compatibility"]["qualities"]))
        fields["articulations"].set(", ".join(pattern["articulations"]))
        fields["rhythm"].set(", ".join(str(round(x * 1000, 1)) for x in pattern["rhythm_search_signature"]))
        doubling.set(pattern["doubling"]["enabled"])

    tree.bind("<<TreeviewSelect>>", select_item)

    def add_song():
        name = simpledialog.askstring("Новая Song", "Название группы паттернов:", parent=window)
        if not name:
            return
        style = simpledialog.askstring("Стиль", "Стиль/направление (необязательно):", parent=window) or ""
        library["songs"].append(create_song(name, style=style))
        refresh()

    def add_pattern_ui():
        song = selected.get("song")
        if song is None:
            messagebox.showinfo("Выбор Song", "Сначала выберите Song в дереве.", parent=window)
            return
        wav = filedialog.askopenfilename(parent=window, title="Выберите извлечённый Pattern WAV", filetypes=[("WAV", "*.wav")])
        if not wav:
            return
        name = simpledialog.askstring("Название Pattern", "Например: Verse 8ths / Chorus Accents:", parent=window)
        if not name:
            return
        try:
            pattern = add_pattern(song, name=name, wav_path=wav)
            refresh()
            tree.selection_set(pattern["pattern_id"])
            tree.focus(pattern["pattern_id"])
            select_item()
        except Exception as exc:
            messagebox.showerror("Pattern", str(exc), parent=window)

    def save_selected():
        pattern, song = selected.get("pattern"), selected.get("song")
        if pattern is None or song is None:
            messagebox.showinfo("Выбор Pattern", "Выберите паттерн, чтобы сохранить его параметры.", parent=window)
            return
        try:
            role = fields["role"].get().strip().upper()
            selector = int(fields["selector"].get()) if fields["selector"].get().strip() else None
            def opt_num(key, cast=float):
                return cast(fields[key].get()) if fields[key].get().strip() else None
            tempo_min, tempo_max = opt_num("tempo_min"), opt_num("tempo_max")
            meter_num, meter_den = opt_num("meter_num", int), opt_num("meter_den", int)
            shift, end = opt_num("shift") or 0.0, opt_num("end")
            chords = [x.strip().upper() for x in fields["chords"].get().split(",") if x.strip()]
            arts = [x.strip().upper() for x in fields["articulations"].get().split(",") if x.strip()]
            rhythm_ms = [float(x.strip()) for x in fields["rhythm"].get().split(",") if x.strip()]
            pattern.update({
                "role": role, "selector_midi_note": selector,
                "tempo_range_bpm": {"min": tempo_min, "max": tempo_max},
                "time_signature": {"numerator": meter_num, "denominator": meter_den},
                "shift_beats": shift, "end_beats": end,
                "chord_compatibility": {
                    **pattern["chord_compatibility"], "qualities": chords,
                    "mapping_status": "REQUIRES_REVIEW",
                },
                "articulations": arts or ["UNKNOWN"],
                "rhythm_search_signature": [x / 1000.0 for x in rhythm_ms],
                "doubling": {**pattern["doubling"], "enabled": bool(doubling.get())},
            })
            validate_library(library)
            save_library(path, library)
            refresh()
            messagebox.showinfo("Pattern", "Параметры сохранены. Runtime-ready остаётся закрыт до проверки событий и лицензии.", parent=window)
        except Exception as exc:
            messagebox.showerror("Ошибка проверки", str(exc), parent=window)

    tap_state = {"times": []}
    tap_button = {"widget": None}

    def tap_rhythm():
        now = time.monotonic()
        tap_state["times"].append(now)
        if len(tap_state["times"]) > 17:
            tap_state["times"] = tap_state["times"][-17:]
        if len(tap_state["times"]) >= 3:
            intervals = tap_intervals(tap_state["times"])
            fields["rhythm"].set(", ".join(str(round(x * 1000, 1)) for x in intervals))
        if tap_button["widget"] is not None:
            tap_button["widget"].configure(text=f"Tap ритм ({len(tap_state['times'])})")

    def reset_taps():
        tap_state["times"] = []
        if tap_button["widget"] is not None:
            tap_button["widget"].configure(text="Tap ритм")

    def rhythm_search():
        try:
            values = [float(x.strip()) / 1000.0 for x in fields["rhythm"].get().split(",") if x.strip()]
            results = search_similar_patterns(library, values)
            if not results:
                messagebox.showinfo("Rhythm Search", "Совпадений нет. Добавьте rhythm signature проверенным паттернам.", parent=window)
                return
            lines = [f'{item["song_name"]} — {item["pattern_name"]} [{item["role"]}] | distance={item["distance"]:.3f}' for item in results]
            messagebox.showinfo("Rhythm Search", "\\n".join(lines), parent=window)
        except Exception as exc:
            messagebox.showerror("Rhythm Search", str(exc), parent=window)

    def delete_selected():
        pattern, song = selected.get("pattern"), selected.get("song")
        if pattern is None or song is None:
            return
        if not messagebox.askyesno("Удалить запись", "Удалить только запись паттерна из Song? WAV-файл не удаляется.", parent=window):
            return
        song["patterns"] = [p for p in song["patterns"] if p["pattern_id"] != pattern["pattern_id"]]
        selected.update(pattern=None)
        save_library(path, library)
        refresh()

    controls = ttk.Frame(top)
    controls.pack(fill="x", pady=(8, 0))
    ttk.Button(controls, text="Новая Song", command=add_song).pack(side="left", padx=3)
    ttk.Button(controls, text="Добавить Pattern WAV", command=add_pattern_ui).pack(side="left", padx=3)
    ttk.Button(controls, text="Сохранить параметры", command=save_selected).pack(side="left", padx=3)
    ttk.Button(controls, text="Удалить запись (не WAV)", command=delete_selected).pack(side="left", padx=3)
    tap_button["widget"] = ttk.Button(controls, text="Tap ритм", command=tap_rhythm)
    tap_button["widget"].pack(side="left", padx=3)
    ttk.Button(controls, text="Сброс Tap", command=reset_taps).pack(side="left", padx=3)
    ttk.Button(controls, text="Rhythm Search", command=rhythm_search).pack(side="left", padx=3)
    ttk.Button(controls, text="Закрыть", command=window.destroy).pack(side="right", padx=3)
    refresh()
