#!/usr/bin/env python3
"""Portable Tkinter front end for POP PUNK GUITAR Library Manager.

Uses only Python's standard library plus the existing LibraryManager modules.
All file operations remain review-gated by library_operations.py.
"""
from __future__ import annotations

import json
import queue
import threading
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from pathlib import Path

from app_paths import resolve_runtime_paths, resource_file

from unified_manager import AUDIO_EXT, run_manager, quick_scan, resolve_samples_root
from source_import import import_sources_to_library
from pattern_clip_extractor import extract_pattern_occurrences
from other_audit import audit_other_library, route_approved_to_other
from cleanup_audit import audit_all_import_sources, cleanup_sources_from_audit
from finalization import finalize_library as finalize_library_audit
from manifest_review import review_manifest
from task_journal import TaskJournal
from plugin_asset_catalog import MODE_ORDER, build_plugin_asset_catalog, browser_assets_for_mode
from performance_manifest import build_performance_manifest
from pattern_song_manager import open_pattern_song_manager
from chromatic_pitch_map import build_chromatic_pitch_map, chromatic_note_table
from library_structure import write_library_structure, TECHNIQUES
from library_operations import (
    cleanup_original_sources,
    distribute_assets_transactional,
    distribution_plan,
    auto_distribute_approved,
)
from ppgu_theme import NEON_STAGE_THEME, resource_path, configure_neon_stage_ttk

APP_VERSION = "3.0.0-dev9"
BUNDLE_DIR, MANAGER_DIR, PORTABLE_MODE = resolve_runtime_paths(__file__)
# The application can live anywhere. The input library is selected independently.
DEFAULT_SAMPLES = ""
STAGING_ROOT = MANAGER_DIR / "staging"
MANAGER_DIR.mkdir(parents=True, exist_ok=True)
STAGING_ROOT.mkdir(parents=True, exist_ok=True)


class LibraryManagerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(f"POP PUNK GUITAR LIBRARY MANAGER {APP_VERSION}")
        self.root.geometry("980x680")
        self.root.minsize(760, 520)
        self._settings_path = MANAGER_DIR / "manager_settings.json"
        self.samples_root = tk.StringVar(value=self._load_saved_samples_root())
        self.analyze_audio = tk.BooleanVar(value=True)
        self.guitar_confirmed = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Готов. Выберите Samples или непосредственно Import Sample Guitar.")
        # Worker threads must never call Tkinter methods. They only enqueue events;
        # the Tk main thread drains this queue in _poll_worker_events().
        self._worker_events = queue.Queue()
        self._job_running = False
        self._worker_thread = None
        self._cancel_event = threading.Event()
        self._action_buttons = []
        self._cancel_button = None
        self._task_journal = TaskJournal(MANAGER_DIR / 'reports' / 'task_history.jsonl')
        self._active_task_id = None
        self._active_task_title = None
        self._build()
        self.root.after(100, self._poll_worker_events)
        if not self.samples_root.get().strip():
            self.root.after(350, self._prompt_for_library_root)
        if PORTABLE_MODE and MANAGER_DIR != (BUNDLE_DIR / "UserData").resolve():
            self._write(
                "PORTABLE: папка приложения недоступна для записи; "
                f"пользовательские данные вынесены в резервный каталог: {MANAGER_DIR}"
            )
        elif PORTABLE_MODE:
            self._write(
                "PORTABLE: приложение можно хранить в любой доступной папке. "
                f"Пользовательские данные: {MANAGER_DIR}"
            )

    def _build(self) -> None:
        """Build the six-action Manager dashboard using PPGU NEON STAGE DEFAULT."""
        palette = NEON_STAGE_THEME["palette"]
        bg = palette["window_bg"]
        panel = palette["panel"]
        panel_alt = palette["panel_elevated"]
        control_bg = palette["control_bg"]
        control_face = palette["control_face"]
        border = palette["control_border"]
        text = palette["text_primary"]
        muted = palette["text_secondary"]
        disabled = palette["text_disabled"]
        accent = palette["accent"]
        accent_glow = palette["accent_glow"]
        accent_purple = palette["accent_purple"]
        accent_magenta = palette["accent_magenta"]
        green = palette["success"]
        amber = palette["warning"]
        red = palette["danger"]
        lcd_bg = palette["lcd_bg"]
        lcd_text = palette["lcd_text"]
        lowlight = palette["lowlight"]

        self.root.title(f"POP PUNK GUITAR  •  NEON STAGE DEFAULT  •  {APP_VERSION}")
        self.root.geometry("1280x850")
        self.root.minsize(980, 700)
        self.root.configure(bg=bg)

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        configure_neon_stage_ttk(style, palette)

        style.configure(
            "PPGU.Primary.TButton",
            background=accent,
            foreground=bg,
            bordercolor=accent,
            lightcolor=accent,
            darkcolor=accent,
            padding=(14, 10),
            font=("Segoe UI", 9, "bold"),
            relief="flat",
        )
        style.map(
            "PPGU.Primary.TButton",
            background=[("disabled", control_face), ("pressed", accent_glow), ("active", accent_glow)],
            foreground=[("disabled", disabled)],
            bordercolor=[("active", accent_glow)],
        )
        style.configure(
            "PPGU.Danger.TButton",
            background=red,
            foreground=bg,
            bordercolor=red,
            padding=(12, 8),
            font=("Segoe UI", 8, "bold"),
            relief="flat",
        )
        style.map(
            "PPGU.Danger.TButton",
            background=[("disabled", control_face), ("active", "#FF7B83")],
            foreground=[("disabled", disabled)],
        )
        style.configure(
            "PPGU.TCheckbutton",
            background=panel,
            foreground=text,
            font=("Segoe UI", 9),
            padding=(4, 4),
        )
        style.map(
            "PPGU.TCheckbutton",
            background=[("active", panel)],
            foreground=[("disabled", disabled)],
        )

        # Secondary actions remain available, grouped by their matching workflow.
        # They are intentionally menus rather than extra dashboard buttons.
        menu_bar = tk.Menu(
            self.root, tearoff=0, bg=panel, fg=text,
            activebackground=control_face, activeforeground=accent,
            bd=0, relief="flat",
        )
        self.root.configure(menu=menu_bar)

        def add_menu(label: str, commands: list[tuple[str, object]]) -> None:
            submenu = tk.Menu(
                menu_bar, tearoff=0, bg=panel, fg=text,
                activebackground=control_face, activeforeground=accent,
                bd=0, relief="flat",
            )
            for item_label, command in commands:
                if item_label == "---":
                    submenu.add_separator()
                else:
                    submenu.add_command(label=item_label, command=command)
            menu_bar.add_cascade(label=label, menu=submenu)

        add_menu("ПРОЕКТ", [
            ("Выбрать папку Samples…", self.choose_samples),
            ("---", None),
            ("Открыть отчёты", self.open_reports),
            ("Открыть staging", self.open_staging),
            ("Инструкция", self.open_user_guide),
        ])
        add_menu("01  IMPORT GUITAR", [
            ("Импортировать гитарные материалы", self.import_guitar),
            ("Браузер подготовленных ассетов для VST3", self.open_plugin_browser),
        ])
        add_menu("02  SCAN LIBRARY", [
            ("Быстрое сканирование — только файловая инвентаризация", self.quick_scan_only),
            ("Глубокое сканирование — SHA-256 / SFZ / кэш", self.deep_scan_only),
        ])
        add_menu("03  START HUNTING", [
            ("Запустить полный анализ", self.scan),
            ("Аудит OTHER", self.audit_other),
            ("Направить одобренные материалы в OTHER", self.distribute_other),
        ])
        add_menu("04  REVIEW QUEUE", [
            ("Открыть очередь проверки", self.open_review_queue),
            ("Прослушать WAV", self.preview_audio),
            ("Остановить прослушивание", self.stop_preview),
            ("История задач", self.show_task_history),
        ])
        add_menu("05  BUILD LIBRARY", [
            ("Собрать каталог ассетов PPGU", self.build_plugin_catalog),
            ("Pattern Song Manager", self.open_pattern_song_library),
            ("12-нотная карта (для AutoChords в PATTERN)", self.open_chromatic_pitch_map),
            ("Распределить одобренные ассеты", self.distribute),
        ])
        add_menu("06  VERIFY / RECOVERY", [
            ("Проверить staging и FACTORY", self.finalize_library),
            ("Аудит исходников перед очисткой", self.audit_cleanup),
            ("Очистить исходники (двойное подтверждение)", self.cleanup),
        ])
        settings_menu = tk.Menu(
            menu_bar, tearoff=0, bg=panel, fg=text,
            activebackground=control_face, activeforeground=accent,
            selectcolor=accent, bd=0, relief="flat",
        )
        settings_menu.add_checkbutton(
            label="Полный аудиоанализ и извлечение кандидатов (рекомендуется)",
            variable=self.analyze_audio,
        )
        settings_menu.add_checkbutton(
            label="Источник уже отфильтрован как гитарный",
            variable=self.guitar_confirmed,
        )
        menu_bar.add_cascade(label="НАСТРОЙКИ", menu=settings_menu)

        outer = tk.Frame(self.root, bg=bg)
        outer.pack(fill="both", expand=True, padx=20, pady=16)

        # Premium brand header, using the actual PPGU NEON STAGE hero asset.
        header = tk.Frame(outer, bg=bg)
        header.pack(fill="x", pady=(0, 14))
        brand = tk.Frame(header, bg=bg)
        brand.pack(side="left", fill="x", expand=True)
        tk.Label(
            brand, text="POP PUNK GUITAR ULTIMATE   /   LIBRARY MANAGER",
            bg=bg, fg=accent, font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")
        tk.Label(
            brand, text="NEON STAGE DEFAULT",
            bg=bg, fg=text, font=("Segoe UI", 24, "bold"),
        ).pack(anchor="w", pady=(3, 0))
        tk.Label(
            brand,
            text="Профессиональная подготовка и контроль гитарной библиотеки",
            bg=bg, fg=muted, font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(2, 0))
        tk.Label(
            brand,
            text="SKIN-1  •  NEON STAGE  •  BLUE / PURPLE / MAGENTA",
            bg=bg, fg=disabled, font=("Consolas", 8),
        ).pack(anchor="w", pady=(7, 0))

        self._skin_hero = None
        try:
            hero = tk.PhotoImage(file=str(resource_path("assets", "hero.png")))
            factor = max(1, (hero.width() + 179) // 180, (hero.height() + 89) // 90)
            self._skin_hero = hero.subsample(factor, factor)
            tk.Label(
                header, image=self._skin_hero, bg=panel,
                highlightbackground=border, highlightthickness=1,
                padx=8, pady=6,
            ).pack(side="right", padx=(18, 0))
        except (tk.TclError, OSError):
            self._skin_hero = None

        version = tk.Frame(
            header, bg=panel_alt, highlightbackground=border,
            highlightthickness=1, padx=14, pady=10,
        )
        version.pack(side="right", anchor="n")
        tk.Label(
            version, text="MANAGER BUILD", bg=panel_alt, fg=muted,
            font=("Segoe UI", 7, "bold"),
        ).pack(anchor="e")
        tk.Label(
            version, text=APP_VERSION, bg=panel_alt, fg=accent,
            font=("Consolas", 11, "bold"),
        ).pack(anchor="e", pady=(3, 0))
        tk.Label(
            version, text="PPGU  /  SKIN-1", bg=panel_alt, fg=accent_magenta,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="e", pady=(5, 0))

        # The location is visible, but path-changing controls live in the Project menu.
        path_panel = tk.Frame(
            outer, bg=panel, highlightbackground=border,
            highlightthickness=1, padx=14, pady=10,
        )
        path_panel.pack(fill="x", pady=(0, 15))
        tk.Label(
            path_panel, text="АКТИВНАЯ БИБЛИОТЕКА",
            bg=panel, fg=accent, font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")
        self.samples_entry = tk.Entry(
            path_panel, textvariable=self.samples_root,
            bg=control_bg, fg=text, insertbackground=accent,
            relief="flat", highlightthickness=1,
            highlightbackground=border, highlightcolor=accent,
            font=("Consolas", 9), readonlybackground=control_bg,
            state="readonly",
        )
        self.samples_entry.pack(fill="x", ipady=7, pady=(6, 0))

        section_head = tk.Frame(outer, bg=bg)
        section_head.pack(fill="x", pady=(0, 8))
        tk.Label(
            section_head, text="ОСНОВНОЙ РАБОЧИЙ ПОТОК",
            bg=bg, fg=text, font=("Segoe UI", 12, "bold"),
        ).pack(side="left")
        tk.Label(
            section_head, text="6 ОСНОВНЫХ ЭТАПОВ  •  ОРИГИНАЛЫ ЗАЩИЩЕНЫ",
            bg=bg, fg=muted, font=("Segoe UI", 8, "bold"),
        ).pack(side="right")

        cards = tk.Frame(outer, bg=bg)
        cards.pack(fill="x")
        for column in range(3):
            cards.grid_columnconfigure(column, weight=1, uniform="workflow")

        workflow = [
            ("01", "IMPORT GUITAR",
             "Импорт файлов и папок в Import Sample Guitar с SHA-256-проверкой копий. Оригиналы остаются нетронутыми.",
             self.import_guitar, "SOURCE INTAKE"),
            ("02", "SCAN LIBRARY",
             "Быстрая инвентаризация структуры, форматов и SFZ-зависимостей. Хеширование и декодирование — только по необходимости.",
             self.deep_scan_only, "SMART SCAN"),
            ("03", "START HUNTING",
             "Поиск нот, паттернов, риффов и музыкальных кандидатов. Сомнительные результаты не получают выдуманных тегов.",
             self.scan, "AUDIO INTELLIGENCE"),
            ("04", "REVIEW QUEUE",
             "Прослушивание оригиналов и производных, проверка границ, нот, артикуляций, категорий библиотеки VST3 и лицензии.",
             self.open_review_queue, "HUMAN APPROVAL"),
            ("05", "BUILD LIBRARY",
             "Сборка каталога подготовленных ассетов и Performance Manifest для отдельного VST3. Неодобренное остаётся в staging.",
             self.build_plugin_catalog, "LIBRARY CATALOG"),
            ("06", "VERIFY / RECOVERY",
             "Целостность WAV и manifests, SHA-256, provenance, лицензии, отчёты и безопасное восстановление.",
             self.finalize_library, "INTEGRITY / RECOVERY"),
        ]

        self._action_buttons = []
        for index, (number, title, description, command, tag) in enumerate(workflow):
            row, column = divmod(index, 3)
            card = tk.Frame(
                cards, bg=panel, highlightbackground=border,
                highlightthickness=1, padx=14, pady=12,
            )
            card.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
            tk.Frame(card, bg=(accent, accent_purple, accent_magenta)[index % 3], height=3).pack(fill="x", pady=(0, 10))
            top = tk.Frame(card, bg=panel)
            top.pack(fill="x")
            tk.Label(
                top, text=number, bg=panel, fg=accent,
                font=("Consolas", 17, "bold"),
            ).pack(side="left")
            tk.Label(
                top, text=tag, bg=panel, fg=muted,
                font=("Segoe UI", 7, "bold"),
            ).pack(side="right")
            tk.Label(
                card, text=title, bg=panel, fg=text,
                font=("Segoe UI", 10, "bold"), anchor="w",
            ).pack(fill="x", pady=(4, 5))
            tk.Label(
                card, text=description, bg=panel, fg=muted,
                font=("Segoe UI", 8), justify="left", anchor="nw",
                wraplength=330, height=3,
            ).pack(fill="both", expand=True, pady=(0, 10))
            button = ttk.Button(
                card, text="ОТКРЫТЬ ЭТАП",
                command=command, style="PPGU.Primary.TButton",
            )
            button.pack(fill="x")
            self._action_buttons.append(button)

        # Persistent activity console: the only always-visible secondary surface.
        log_panel = tk.Frame(
            outer, bg=lcd_bg, highlightbackground=border,
            highlightthickness=1, padx=12, pady=9,
        )
        log_panel.pack(fill="both", expand=True, pady=(12, 0))
        log_header = tk.Frame(log_panel, bg=lcd_bg)
        log_header.pack(fill="x", pady=(0, 6))
        tk.Label(
            log_header, text="LIVE ACTIVITY  /  ЖУРНАЛ ОПЕРАЦИЙ",
            bg=lcd_bg, fg=accent, font=("Segoe UI", 8, "bold"),
        ).pack(side="left")
        tk.Label(
            log_header, text="ПКМ: копирование  •  CTRL+A / CTRL+C",
            bg=lcd_bg, fg=muted, font=("Segoe UI", 7),
        ).pack(side="right")
        log_frame = tk.Frame(log_panel, bg=lcd_bg)
        log_frame.pack(fill="both", expand=True)
        self.log = tk.Text(
            log_frame, wrap="word", height=7, font=("Consolas", 9),
            bg=lowlight, fg=lcd_text, insertbackground=accent,
            selectbackground=control_face, relief="flat", padx=10, pady=8,
            exportselection=True, undo=False,
        )
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=log_scroll.set)
        self.log.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")
        self.log.bind("<Control-a>", self.select_log_all)
        self.log.bind("<Control-A>", self.select_log_all)
        self.log.bind("<Control-c>", self.copy_log_selection)
        self.log.bind("<Control-C>", self.copy_log_selection)
        self.log.bind("<Button-3>", self.show_log_context_menu)
        self.log.configure(state="disabled")

        status_panel = tk.Frame(
            outer, bg=panel_alt, highlightbackground=border,
            highlightthickness=1, padx=12, pady=8,
        )
        status_panel.pack(fill="x", pady=(9, 0))
        tk.Label(
            status_panel, text="●", bg=panel_alt, fg=green,
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=(0, 8))
        tk.Label(
            status_panel, textvariable=self.status, bg=panel_alt,
            fg=text, font=("Segoe UI", 8), anchor="w",
        ).pack(side="left", fill="x", expand=True)
        self._cancel_button = ttk.Button(
            status_panel, text="ОСТАНОВИТЬ ЗАДАЧУ",
            command=self.cancel_job, style="PPGU.Danger.TButton", state="disabled",
        )
        self._cancel_button.pack(side="right", padx=(8, 0))

        self._write(
            "NEON STAGE DEFAULT / SKIN-1 загружена из темы PPGU.\n"
            "На главном экране — шесть рабочих этапов; вспомогательные инструменты находятся в меню своих разделов.\n"
            "Оригиналы read-only. В FACTORY допускаются только REVIEWED + LICENSE_APPROVED + VERIFIED материалы.\n"
        )

    def _copy_log_text(self, value: str) -> None:
        if not value:
            self.status.set("Нечего копировать.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self.root.update_idletasks()
        self.status.set(f"Скопировано в буфер обмена: {len(value)} символов.")

    def copy_log_selection(self, event=None):
        try:
            value = self.log.get("sel.first", "sel.last")
        except tk.TclError:
            self.status.set("Сначала выделите нужные строки журнала.")
            return "break" if event else None
        self._copy_log_text(value)
        return "break" if event else None

    def copy_log_all(self):
        self._copy_log_text(self.log.get("1.0", "end-1c"))

    def select_log_all(self, event=None):
        self.log.tag_add("sel", "1.0", "end-1c")
        self.log.mark_set("insert", "1.0")
        self.log.see("insert")
        return "break"

    def show_log_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Копировать выделенное", command=self.copy_log_selection)
        menu.add_command(label="Копировать весь журнал", command=self.copy_log_all)
        menu.add_command(label="Выделить всё", command=self.select_log_all)
        menu.tk_popup(event.x_root, event.y_root)
        menu.grab_release()

    def _write(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text.rstrip() + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _load_saved_samples_root(self) -> str:
        """Restore the last selected library from this installation's data folder."""
        try:
            settings = json.loads(self._settings_path.read_text(encoding="utf-8"))
            value = settings.get("samples_root", "")
            if isinstance(value, str) and value.strip() and Path(value).expanduser().exists():
                return value
        except (OSError, ValueError, TypeError, AttributeError):
            pass
        return DEFAULT_SAMPLES

    def _save_settings(self) -> None:
        """Persist the selected library atomically in UserData / LocalAppData."""
        import os
        import tempfile

        self._settings_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "samples_root": self.samples_root.get().strip(),
            "app_version": APP_VERSION,
        }
        fd, temporary = tempfile.mkstemp(
            prefix="manager_settings-", suffix=".tmp",
            dir=self._settings_path.parent,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self._settings_path)
        except Exception:
            try:
                Path(temporary).unlink(missing_ok=True)
            except OSError:
                pass
            raise

    def _prompt_for_library_root(self) -> None:
        selected = filedialog.askdirectory(
            title="Выберите папку Samples или Import Sample Guitar",
        )
        if not selected:
            self.status.set(
                "Выберите папку библиотеки через меню ПРОЕКТ перед запуском сканирования."
            )
            return
        self.samples_root.set(selected)
        try:
            self._save_settings()
            self.status.set("Папка библиотеки сохранена.")
            self._write(f"Путь Samples сохранён: {selected}")
        except OSError as exc:
            messagebox.showwarning(
                "Настройки",
                f"Папка выбрана на этот запуск, но путь не удалось сохранить: {exc}",
            )

    def _samples(self) -> Path:
        """Resolve and log the exact Samples/Import Sample Guitar paths."""
        if not self.samples_root.get().strip():
            self._prompt_for_library_root()
        if not self.samples_root.get().strip():
            raise ValueError("Сначала выберите папку Samples или Import Sample Guitar.")
        selected = Path(self.samples_root.get()).expanduser()
        resolved = resolve_samples_root(selected)
        incoming = next(
            p for p in resolved.iterdir()
            if p.is_dir() and p.name.strip().casefold() == "import sample guitar"
        )
        self._write(f"Путь Samples: {resolved}")
        self._write(f"Путь входной библиотеки: {incoming.resolve()}")
        return resolved

    def choose_samples(self) -> None:
        selected = filedialog.askdirectory(
            title="Выберите Samples ИЛИ непосредственно Import Sample Guitar"
        )
        if selected:
            self.samples_root.set(selected)
            try:
                self._save_settings()
            except OSError as exc:
                messagebox.showwarning(
                    "Настройки",
                    f"Папка выбрана на этот запуск, но путь не удалось сохранить: {exc}",
                )

    def _background(self, title: str, work) -> None:
        """Run work off the UI thread and deliver all UI updates via a queue."""
        if self._job_running:
            self._write(f"[ОТКАЗ] Уже выполняется другая операция: {title}")
            self.status.set("Дождитесь завершения текущей операции.")
            return

        self._job_running = True
        self._cancel_event.clear()
        self._active_task_title = title
        task_id = self._task_journal.start(
            title, details={"samples_root": self.samples_root.get(), "manager_version": APP_VERSION}
        )
        self._active_task_id = task_id
        self._cancel_button.configure(state="normal")
        self.status.set(title + " — запуск…")
        for button in self._action_buttons:
            button.configure(state="disabled")
        self._write(f"[ЗАДАЧА] Запуск фонового потока: {title}")

        def runner():
            try:
                result = work()
                if self._cancel_event.is_set():
                    self._task_journal.cancel(task_id, title)
                    self._worker_events.put(("cancelled", title, result))
                else:
                    self._task_journal.finish(task_id, title, result=result)
                    self._worker_events.put(("finish", title, result))
            except Exception as exc:
                if self._cancel_event.is_set():
                    self._task_journal.cancel(task_id, title, f"{type(exc).__name__}: {exc}")
                    self._worker_events.put(("cancelled", title, {"error": f"{type(exc).__name__}: {exc}"}))
                else:
                    self._task_journal.fail(task_id, title, f"{type(exc).__name__}: {exc}")
                    self._worker_events.put(("error", title, f"{type(exc).__name__}: {exc}", traceback.format_exc()))

        worker = threading.Thread(target=runner, name="LibraryManagerWorker", daemon=True)
        self._worker_thread = worker
        try:
            worker.start()
        except Exception as exc:
            self._task_journal.fail(task_id, title, f"{type(exc).__name__}: {exc}")
            self._job_running = False
            self._worker_thread = None
            for button in self._action_buttons:
                button.configure(state="normal")
            details = traceback.format_exc()
            self._error(title, exc, details)

    def _queue_progress(self, message: str) -> None:
        """Persist worker progress and forward it to the Tk main thread."""
        task_id = self._active_task_id
        task = self._active_task_title
        if task_id and task:
            self._task_journal.progress(task_id, task, message)
        self._worker_events.put(("progress", message))

    def _poll_worker_events(self) -> None:
        """Process worker events only on Tk's main thread."""
        try:
            while True:
                event = self._worker_events.get_nowait()
                kind = event[0]
                if kind == "progress":
                    self._progress(event[1])
                elif kind == "finish":
                    _, title, result = event
                    self._job_running = False
                    self._worker_thread = None
                    self._cancel_button.configure(state="disabled")
                    for button in self._action_buttons:
                        button.configure(state="normal")
                    self._finish(title, result)
                elif kind == "cancelled":
                    _, title, result = event
                    self._job_running = False
                    self._worker_thread = None
                    self._cancel_button.configure(state="disabled")
                    for button in self._action_buttons:
                        button.configure(state="normal")
                    self._write("[ОСТАНОВЛЕНО] " + json.dumps(result, ensure_ascii=False, indent=2, default=str))
                    self.status.set(title + ": остановлено; частичные отчёты сохранены")
                elif kind == "error":
                    _, title, error_text, details = event
                    self._job_running = False
                    self._worker_thread = None
                    self._cancel_button.configure(state="disabled")
                    for button in self._action_buttons:
                        button.configure(state="normal")
                    self._write(f"[ОШИБКА] {error_text}")
                    self._write(details)
                    self.status.set(title + ": ошибка")
                    messagebox.showerror("Ошибка", error_text)
        except queue.Empty:
            pass
        finally:
            try:
                self.root.after(100, self._poll_worker_events)
            except tk.TclError:
                # Window is already closing.
                pass

    def _finish(self, title: str, result) -> None:
        self._write(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        self.status.set(title + ": завершено")

    def _error(self, title: str, exc: Exception, details: str) -> None:
        self._write(details)
        self.status.set(title + ": ошибка")
        messagebox.showerror("Ошибка", f"{type(exc).__name__}: {exc}")

    def cancel_job(self) -> None:
        if self._job_running:
            self._cancel_event.set()
            self._cancel_button.configure(state="disabled")
            self.status.set("Остановка запрошена — завершаю текущий безопасный блок…")
            self._write("[ОТМЕНА] Запрошена остановка. Исходные файлы не затрагиваются.")

    def _prepare_import_target(self) -> Path | None:
        """Create/resolve the active Samples folder and its incoming destination."""
        chosen = self.samples_root.get().strip()
        if not chosen:
            chosen = filedialog.askdirectory(
                title="Выберите или создайте папку Samples для библиотеки Manager",
            )
            if not chosen:
                return None

        selected = Path(chosen).expanduser().resolve()
        if not selected.is_dir():
            raise NotADirectoryError(f"Выбранный каталог Samples не существует: {selected}")

        if selected.name.strip().casefold() == "import sample guitar":
            samples = selected.parent
            incoming = selected
        else:
            samples = selected
            children = [
                item for item in samples.iterdir()
                if item.is_dir() and item.name.strip().casefold() == "import sample guitar"
            ]
            if len(children) > 1:
                raise RuntimeError(
                    "В выбранной папке найдено несколько Import Sample Guitar. "
                    "Выберите нужную входную папку напрямую."
                )
            incoming = children[0] if children else samples / "Import Sample Guitar"

        incoming.mkdir(parents=True, exist_ok=True)
        (samples / "FACTORY").mkdir(parents=True, exist_ok=True)
        (samples / "OTHER").mkdir(parents=True, exist_ok=True)
        self.samples_root.set(str(samples))
        self._save_settings()
        self._write(f"Целевая папка импорта: {incoming}")
        return incoming

    def import_guitar(self) -> None:
        """Copy selected source libraries into Import Sample Guitar, preserving originals."""
        try:
            incoming = self._prepare_import_target()
        except Exception as exc:
            messagebox.showerror("IMPORT GUITAR — папка библиотеки", str(exc), parent=self.root)
            return
        if incoming is None:
            self.status.set("IMPORT GUITAR: папка Samples не выбрана.")
            return

        selected = list(filedialog.askopenfilenames(
            title="IMPORT GUITAR — выберите аудио, SFZ или архивы",
            filetypes=[
                ("Поддерживаемые материалы", "*.wav *.wave *.aif *.aiff *.flac *.ogg *.oga *.mp3 *.m4a *.aac *.wma *.opus *.sfz *.zip *.7z *.rar"),
                ("Все файлы", "*.*"),
            ],
        ))
        while messagebox.askyesno(
            "IMPORT GUITAR",
            "Добавить целую папку библиотеки? Можно добавить несколько папок подряд.",
            parent=self.root,
        ):
            folder = filedialog.askdirectory(title="Выберите папку исходной гитарной библиотеки")
            if not folder:
                break
            selected.append(folder)
        if not selected:
            self.status.set("IMPORT GUITAR: источники не выбраны.")
            return

        if not messagebox.askyesno(
            "Подтверждение импорта",
            f"Менеджер создаст проверенные копии выбранных файлов в:\n{incoming}\n\n"
            "Оригиналы останутся на прежнем месте и не будут изменены, перемещены или удалены. "
            "Для копирования требуется дополнительное место на диске. "
            "После импорта копии будут доступны этапам SCAN LIBRARY и START HUNTING. Продолжить?",
            parent=self.root,
        ):
            self.status.set("IMPORT GUITAR: копирование отменено.")
            return

        registry = MANAGER_DIR / "reports" / "import_registry.json"

        def work():
            return import_sources_to_library(
                selected,
                incoming,
                registry,
                progress=self._queue_progress,
                cancel_event=self._cancel_event,
            )

        self._write("=== IMPORT GUITAR ===")
        self._write(f"Выбрано источников: {len(selected)}. Будут созданы SHA-256-проверенные копии; оригиналы останутся нетронутыми.")
        self._background("IMPORT GUITAR — копирование и регистрация источников", work)

    def quick_scan_only(self) -> None:
        """Run only the fast filesystem inventory; never start deep analysis."""
        try:
            samples = self._samples()
        except Exception as exc:
            messagebox.showerror("Папка Samples", str(exc))
            return

        def work():
            def report_progress(message: str) -> None:
                self._queue_progress(message)
            return quick_scan(
                samples, progress=report_progress, cancel_event=self._cancel_event,
            )

        self._write("=== БЫСТРОЕ СКАНИРОВАНИЕ ===")
        self._write("Только обход Import Sample Guitar и чтение файловой метаинформации. SHA-256, декодирование и анализ не запускаются.")
        self._background("Быстрое сканирование", work)

    def deep_scan_only(self) -> None:
        """Run full file inventory/hash cache without acoustic decoding or extraction."""
        try:
            samples = self._samples()
        except Exception as exc:
            messagebox.showerror("Папка Samples", str(exc))
            return

        def work():
            def report_progress(message: str) -> None:
                self._queue_progress(message)

            report_progress("ЭТАП 1/2: быстрый filesystem scan без SHA-256 и декодирования.")
            quick_result = quick_scan(
                samples, progress=report_progress, cancel_event=self._cancel_event,
            )
            if self._cancel_event.is_set():
                raise RuntimeError("Глубокий анализ остановлен после быстрого сканирования.")
            report_progress("ЭТАП 2/2: глубокая инвентаризация, SHA-256 cache, форматы и SFZ. Аудио не декодируется.")
            deep_result = run_manager(
                samples,
                analyze_audio=False,
                guitar_source_confirmed=False,
                write_virtual=False,
                progress=report_progress,
                cancel_event=self._cancel_event,
                workers=1,
            )
            return {
                "quick_scan": quick_result,
                "deep_inventory": deep_result,
                "acoustic_analysis_performed": False,
                "physical_extraction_performed": False,
                "workers": 1,
                "source_files_modified": False,
            }

        self._write("=== БЫСТРЫЙ ГЛУБОКИЙ АНАЛИЗ ===")
        self._write("Проверка форматов, размеров, SHA-256/кэша, точных дубликатов и SFZ. Без pitch/YIN, акустического декодирования и извлечения WAV.")
        self._write("На первом проходе SHA-256 читает аудиофайлы; последующие проходы используют кэш неизменённых файлов.")
        self._background("Быстрый глубокий анализ", work)

    def scan(self) -> None:
        """Run the complete preparation pipeline after the fast scan."""
        try:
            samples = self._samples()
        except Exception as exc:
            messagebox.showerror("Папка Samples", str(exc))
            return
        analyze_audio = self.analyze_audio.get()
        guitar_confirmed = self.guitar_confirmed.get()
        if analyze_audio and not guitar_confirmed:
            guitar_confirmed = messagebox.askyesno(
                "Подтверждение гитарного источника",
                "Подтверждаете, что выбранная библиотека предназначена для гитарного плагина "
                "и уже очищена от Piano / Bell / Drum материалов?\n\n"
                "При ответе «Нет» Manager всё равно завершит инвентаризацию и акустический анализ, "
                "но не будет запускать гитарное извлечение Pattern / Chord / Sample / Melody.",
            )
            if guitar_confirmed:
                self.guitar_confirmed.set(True)

        def work():
            def report_progress(message: str) -> None:
                self._queue_progress(message)

            report_progress("ЭТАП 1/8: быстрое сканирование структуры — только файловая метаинформация.")
            quick_result = quick_scan(
                samples, progress=report_progress, cancel_event=self._cancel_event,
            )
            if self._cancel_event.is_set():
                raise RuntimeError("Полный цикл остановлен после быстрого сканирования.")
            report_progress("ЭТАП 2/8: глубокая инвентаризация, SHA-256 cache, форматы, дубликаты и SFZ.")
            analysis_result = run_manager(
                samples,
                analyze_audio=analyze_audio,
                guitar_source_confirmed=guitar_confirmed,
                write_virtual=bool(analyze_audio and guitar_confirmed),
                progress=report_progress,
                cancel_event=self._cancel_event,
                workers=1,
            )

            mode_counts = analysis_result.get("mode_candidate_counts", {})
            mode_report_path = Path(analysis_result["report_directory"]) / "mode_sorting_report.json"
            report_progress(
                "КЛАССИФИКАЦИЯ ПО 10 КАТЕГОРИЯМ ПОДГОТОВКИ БИБЛИОТЕКИ ДЛЯ VST3: "
                + "; ".join(f"{name}: {count}" for name, count in mode_counts.items())
                + f". Отчёт: {mode_report_path}"
            )

            extracted_region = 0
            extracted_pattern = 0
            extracted_chord = 0
            extracted_sample = 0
            extracted_melody_notes = 0
            extracted_melody = 0
            extraction_failures = []
            report_file = Path(analysis_result["report_directory"]) / "unified_audio_analysis.json"
            if analyze_audio and guitar_confirmed and report_file.is_file():
                records = json.loads(report_file.read_text(encoding="utf-8"))
                from pattern_clip_extractor import extract_pattern_occurrences
                from sample_melody_pipeline import prepare_sample_and_melody
                from virtual_sample_extractor import extract_virtual_ranges

                report_progress("ЭТАП 3/8: извлечение реальных WAV-отрывков из длинных гитарных записей.")
                for record in records:
                    if self._cancel_event.is_set():
                        raise RuntimeError("Извлечение остановлено; уже созданные staging-кандидаты сохранены.")
                    virtual = record.get("virtual_extraction")
                    if not isinstance(virtual, dict) or not virtual.get("candidates"):
                        continue
                    try:
                        candidates = virtual.get("candidates") or []
                        for offset in range(0, len(candidates), 1000):
                            if self._cancel_event.is_set():
                                raise RuntimeError("Извлечение длинных отрывков остановлено.")
                            chunk_report = {
                                **virtual,
                                "candidates": candidates[offset:offset + 1000],
                            }
                            clips = extract_virtual_ranges(
                                chunk_report, STAGING_ROOT,
                                max_clips=1000,
                                cancel_event=self._cancel_event,
                                progress=report_progress,
                            )
                            extracted_region += len(clips)
                    except Exception as exc:
                        if self._cancel_event.is_set():
                            raise
                        extraction_failures.append({
                            "source_path": record.get("source_path"),
                            "stage": "LONG_RECORDING_RANGE_EXTRACTION",
                            "error": f"{type(exc).__name__}: {exc}",
                        })

                report_progress("ЭТАП 4/8: извлечение WAV повторяющихся ритм-паттернов.")
                for record in records:
                    if self._cancel_event.is_set():
                        raise RuntimeError("Извлечение остановлено; созданные staging-кандидаты сохранены.")
                    pattern_data = (record.get("pattern_analysis") or {}).get("pattern_analysis", {})
                    if not pattern_data.get("patterns"):
                        continue
                    try:
                        source_report = {
                            "source": record["source_path"],
                            "source_sha256": record["source_sha256"],
                        }
                        patterns = pattern_data.get("patterns") or []
                        # Split large candidate sets into bounded chunks. This
                        # removes the old global 500-asset ceiling without
                        # building one enormous in-memory extraction batch.
                        for pattern in patterns:
                            occurrences = pattern.get("occurrences") or []
                            for offset in range(0, len(occurrences), 10000):
                                if self._cancel_event.is_set():
                                    raise RuntimeError("Извлечение Pattern остановлено.")
                                chunk_pattern = {
                                    **pattern,
                                    "occurrences": occurrences[offset:offset + 10000],
                                }
                                chunk_analysis = {"patterns": [chunk_pattern]}
                                clips = extract_pattern_occurrences({
                                    **source_report,
                                    "pattern_analysis": chunk_analysis,
                                }, STAGING_ROOT, max_clips=10000,
                                    cancel_event=self._cancel_event)
                                extracted_pattern += len(clips)
                    except Exception as exc:
                        if self._cancel_event.is_set():
                            raise
                        extraction_failures.append({
                            "source_path": record.get("source_path"),
                            "stage": "PATTERN_EXTRACTION",
                            "error": f"{type(exc).__name__}: {exc}",
                        })

                report_progress("ЭТАП 5/8: извлечение аккордовых и Power Chord WAV-кандидатов для категории SAMPLE MODE библиотеки VST3 и AutoChords внутри PATTERN.")
                from chord_clip_extractor import extract_chord_samples
                for record in records:
                    if self._cancel_event.is_set():
                        raise RuntimeError("Извлечение аккордов остановлено; созданные staging-кандидаты сохранены.")
                    chord_data = record.get("chord_analysis") or {}
                    if not chord_data.get("chord_candidates"):
                        continue
                    try:
                        candidates = chord_data.get("chord_candidates") or []
                        for offset in range(0, len(candidates), 5000):
                            if self._cancel_event.is_set():
                                raise RuntimeError("Извлечение Chord остановлено.")
                            chunk_report = {
                                **chord_data,
                                "chord_candidates": candidates[offset:offset + 5000],
                            }
                            clips = extract_chord_samples(
                                chunk_report, STAGING_ROOT, max_clips=5000,
                                cancel_event=self._cancel_event,
                            )
                            extracted_chord += len(clips)
                    except Exception as exc:
                        if self._cancel_event.is_set():
                            raise
                        extraction_failures.append({
                            "source_path": record.get("source_path"),
                            "stage": "CHORD_SAMPLE_EXTRACTION",
                            "error": f"{type(exc).__name__}: {exc}",
                        })

                report_progress("ЭТАП 6/8: извлечение одиночных нот для категорий SAMPLE MODE и MELODY MODE библиотеки VST3; дополнительные фразы для категории MELODY MODE.")
                for record in records:
                    if self._cancel_event.is_set():
                        raise RuntimeError("Извлечение остановлено; созданные staging-кандидаты сохранены.")
                    source = Path(record.get("source_path", ""))
                    if source.suffix.lower() not in AUDIO_EXT:
                        continue
                    try:
                        pitch_events = record.get("pitch_candidates") or []
                        # This engine processes the full per-source event list;
                        # note WAVs are shared by Sample and Melody assignments.
                        source_asset_budget = max(1, len(pitch_events) * 2)
                        result = prepare_sample_and_melody(
                            source, STAGING_ROOT,
                            max_note_events=max(1, len(pitch_events) or 500),
                            max_assets=source_asset_budget,
                            pitch_candidates=record.get("pitch_candidates"),
                            expected_source_sha256=record.get("source_sha256"),
                            source_metadata=record.get("filename_metadata"),
                            cancel_event=self._cancel_event,
                        )
                        extracted_sample += result["sample_mode_count"]
                        extracted_melody_notes += result.get("melody_note_mode_count", 0)
                        extracted_melody += result["melody_mode_count"]
                        if result["sample_mode_count"] + result["melody_mode_count"] == 0:
                            extraction_failures.append({
                                "source_path": str(source),
                                "stage": "SAMPLE_MELODY_EXTRACTION",
                                "error": "Не обнаружены надёжные кандидаты pitch-events; WAV не создан.",
                            })
                    except Exception as exc:
                        if self._cancel_event.is_set():
                            raise
                        extraction_failures.append({
                            "source_path": str(source),
                            "stage": "SAMPLE_MELODY_EXTRACTION",
                            "error": f"{type(exc).__name__}: {exc}",
                        })
            elif analyze_audio and not guitar_confirmed:
                extraction_failures.append({
                    "stage": "EXTRACTION_GATE",
                    "error": "Физическое извлечение пропущено: оператор не подтвердил гитарный источник.",
                })

            if self._cancel_event.is_set():
                raise RuntimeError("Полный цикл остановлен до финализации; исходные файлы не изменены.")

            report_progress("ЭТАП 7/8: финальная проверка SHA-256, границ, PCM WAV, музыкального статуса и лицензии.")
            finalization_result = finalize_library_audit(
                samples, STAGING_ROOT,
                progress=report_progress,
                cancel_event=self._cancel_event,
            )
            if self._cancel_event.is_set():
                raise RuntimeError("Полный цикл остановлен до сборки каталога; исходные файлы не изменены.")

            report_progress("ЭТАП 8/8: проверка и сборка каталога по 10 категориям подготовленной библиотеки для VST3.")
            catalog_path = Path(analysis_result["report_directory"]) / "plugin_asset_catalog.json"
            catalog_result = build_plugin_asset_catalog(
                STAGING_ROOT,
                catalog_path,
                mode_report_path=mode_report_path if mode_report_path.is_file() else None,
                pattern_engine_manifest_path=(
                    Path(analysis_result["report_directory"]) / "pattern_engine_manifest.json"
                ),
            )
            performance_path = Path(analysis_result["report_directory"]) / "performance_manifest.json"
            performance_result = build_performance_manifest(catalog_path, performance_path)
            report_progress(
                f"Каталог VST3: {catalog_result['asset_count']} staged assets, "
                f"{catalog_result['playable_asset_count']} runtime-ready, "
                f"{catalog_result['candidate_count']} analysis candidates. "
                f"Performance Manifest: {performance_result['asset_binding_count']} bindings, "
                f"{performance_result['event_count']} reviewed events. "
                f"Файлы: {catalog_path}; {performance_path}"
            )
            return {
                "quick_scan": quick_result,
                "deep_analysis": analysis_result,
                "physical_extraction": {
                    "long_recording_region_wav_count": extracted_region,
                    "pattern_instrument_wav_count": extracted_pattern,
                    "chord_and_power_chord_wav_count": extracted_chord,
                    "sample_mode_wav_count": extracted_sample,
                    "melody_mode_single_note_bindings": extracted_melody_notes,
                    "melody_mode_phrase_wav_count": extracted_melody,
                    "total_new_wav_candidates": extracted_region + extracted_pattern + extracted_chord + extracted_sample + extracted_melody,
                    "extraction_batching": "CHUNKED_PER_ENGINE_NO_GLOBAL_500_ASSET_CAP",
                    "manifest_count_in_staging": finalization_result["staging"]["manifests_checked"],
                    "failures": extraction_failures,
                    "review_status": "NEEDS_MUSICAL_REVIEW",
                    "license_status": "UNREVIEWED",
                },
                "finalization": finalization_result,
                "plugin_asset_catalog": catalog_result,
                "performance_manifest": performance_result,
                "source_files_modified": False,
                "source_files_moved_or_deleted": False,
            }

        self._write("=== ПОЛНЫЙ ЦИКЛ ПОДГОТОВКИ БИБЛИОТЕКИ ===")
        self._write("Быстрый scan → глубокая инвентаризация → акустика/ритм → извлечение длинных отрывков + Pattern/Sample/Melody WAV → аудит staging.")
        self._write("Извлечение запускается только после ручного подтверждения гитарного источника. FACTORY остаётся защищённой review/license gate.")
        self._write(f"Акустический анализ: {'ВКЛЮЧЁН' if analyze_audio else 'ВЫКЛЮЧЕН'}")
        self._write(f"Гитарный источник подтверждён: {'ДА' if guitar_confirmed else 'НЕТ'}")
        self._background("Полный цикл подготовки библиотеки", work)

    def _progress(self, message: str) -> None:
        self._write("[ВЫПОЛНЯЕТСЯ] " + message)
        if self._active_task_id:
            try:
                self._task_journal.progress(self._active_task_id, self._active_task_title or "Background task", message)
            except OSError as exc:
                self._write(f"[ПРЕДУПРЕЖДЕНИЕ] Не удалось записать историю: {exc}")
        self.status.set(message)

    def show_task_history(self) -> None:
        """Display last known task states from the durable journal."""
        try:
            states = self._task_journal.latest_states()
            if not states:
                self._write("История задач пока пуста.")
                return
            self._write("=== ИСТОРИЯ ЗАДАЧ ===")
            for task_id, state in list(states.items())[-100:]:
                self._write(
                    f"{state.get('last_timestamp_utc')} | {state.get('task')} | "
                    f"{state.get('last_event')} | id={task_id}"
                )
            self._write(f"Полный журнал: {self._task_journal.path}")
        except OSError as exc:
            messagebox.showerror("История задач", str(exc))

    def preview_audio(self) -> None:
        selected = filedialog.askopenfilename(
            title="Выберите WAV для предпрослушивания",
            filetypes=[("WAV audio", "*.wav *.wave")],
        )
        if not selected:
            return
        try:
            import winsound
            winsound.PlaySound(selected, winsound.SND_FILENAME | winsound.SND_ASYNC)
            self._write("Предпрослушивание: " + selected)
            self.status.set("Воспроизведение WAV")
        except Exception as exc:
            messagebox.showerror("Предпрослушивание", f"Не удалось воспроизвести WAV: {exc}")

    def stop_preview(self) -> None:
        try:
            import winsound
            winsound.PlaySound(None, 0)
            self.status.set("Воспроизведение остановлено")
        except Exception as exc:
            messagebox.showerror("Предпрослушивание", str(exc))

    def build_plugin_catalog(self) -> None:
        """Build a validated plugin catalog from existing staged WAV manifests."""
        reports_root = MANAGER_DIR / "reports"
        mode_reports = sorted(
            reports_root.glob("run_*/mode_sorting_report.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        pattern_manifests = sorted(
            reports_root.glob("run_*/pattern_engine_manifest.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        stamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output = reports_root / f"plugin_asset_catalog_{stamp}.json"

        def work():
            catalog_result = build_plugin_asset_catalog(
                STAGING_ROOT,
                output,
                mode_report_path=mode_reports[0] if mode_reports else None,
                pattern_engine_manifest_path=pattern_manifests[0] if pattern_manifests else None,
            )
            chromatic_output = output.with_name(output.stem.replace(
                "plugin_asset_catalog", "chromatic_pitch_map"
            ) + ".json")
            chromatic_map = build_chromatic_pitch_map(json.loads(output.read_text(encoding="utf-8")))
            performance_output = output.with_name(output.stem.replace(
                "plugin_asset_catalog", "performance_manifest"
            ) + ".json")
            performance_result = build_performance_manifest(
                output, performance_output, chromatic_pitch_map=chromatic_map
            )
            structure_output = output.with_name(output.stem.replace(
                "plugin_asset_catalog", "plugin_library_structure"
            ) + ".json")
            coverage_output = output.with_name(output.stem.replace(
                "plugin_asset_catalog", "plugin_library_coverage"
            ) + ".json")
            structure_result = write_library_structure(output, structure_output, coverage_output)
            chromatic_output.write_text(json.dumps(chromatic_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return {
                "plugin_asset_catalog": catalog_result,
                "performance_manifest": performance_result,
                "library_structure": structure_result,
                "chromatic_pitch_map": {
                    "path": str(chromatic_output),
                    "pitch_class_count": len(chromatic_map["pitch_classes"]),
                    "midi_key_count": chromatic_map["coverage"]["midi_key_count"],
                    "exact_sample_count": chromatic_map["coverage"]["exact_approved_sample_count"],
                    "fallback_proposal_count": chromatic_map["coverage"]["fallback_proposal_count"],
                    "missing_source_count": chromatic_map["coverage"]["missing_source_count"],
                    "runtime_status": chromatic_map["runtime_status"],
                },
            }

        self._write("=== СБОРКА КАТАЛОГА ДЛЯ VST3 ===")
        self._write("Проверяются SHA-256 источников и WAV-кандидатов, source offsets, статусы review/license и 10 категорий назначения ассетов для VST3. Непроверенные WAV не становятся playable.")
        self._background("Сборка каталога VST3", work)

    def open_chromatic_pitch_map(self) -> None:
        """Show the 12-tone data map used by AutoChords inside the VST3 PATTERN mode."""
        sharp = "  ".join(item["canonical_name"] for item in chromatic_note_table(spelling="sharp"))
        flat = "  ".join(item["canonical_name"] for item in chromatic_note_table(spelling="flat"))
        messagebox.showinfo(
            "PPGU — 12-нотная карта для AutoChords внутри PATTERN",
            "Все 12 хроматических высот сохраняются и доступны для исполнения.\n\n"
            f"Диезы: {sharp}\n\nБемоли: {flat}\n\n"
            "Энгармонические названия объединяются в один pitch class: C# = Db, D# = Eb, F# = Gb и т. д.\n"
            "E и F — разные ноты.\n\n"
             "В VST3 AutoChords открывается внутри PATTERN и использует ту же карту высот. Названия-дубликаты объединяются, "
            "но хроматические ноты не удаляются. Непроверенные WAV и fallback не допускаются автоматически."
        )

    def open_pattern_song_library(self) -> None:
        """Edit song-grouped Pattern Instrument metadata; WAV sources remain untouched."""
        path = MANAGER_DIR / "reports" / "pattern_song_library.json"
        open_pattern_song_manager(self.root, path)

    def open_plugin_browser(self) -> None:
        """Browse the latest plugin catalog and audition staged WAV candidates."""
        reports_root = MANAGER_DIR / "reports"
        catalogs = sorted(
            reports_root.rglob("plugin_asset_catalog*.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        if not catalogs:
            messagebox.showinfo(
                "Sample Browser",
                "Каталог ассетов для VST3 ещё не создан. Сначала выполните START HUNTING "
                "или выберите «Собрать каталог ассетов PPGU» в меню BUILD LIBRARY.",
            )
            return
        catalog_path = catalogs[0]
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("Sample Browser", f"Не удалось прочитать каталог: {exc}")
            return

        window = tk.Toplevel(self.root)
        window.title("POP PUNK GUITAR ULTIMATE — Sample Browser / подготовленные категории библиотеки")
        window.geometry("1120x650")
        window.configure(bg=NEON_STAGE_THEME["palette"]["window_bg"])
        window.transient(self.root)
        frame = ttk.Frame(window, padding=10)
        frame.pack(fill="both", expand=True)

        top = ttk.Frame(frame)
        top.pack(fill="x")
        ttk.Label(top, text="Категория назначения для VST3:").pack(side="left")
        mode_var = tk.StringVar(value=MODE_ORDER[0])
        mode_box = ttk.Combobox(
            top, textvariable=mode_var, values=list(MODE_ORDER),
            state="readonly", width=24,
        )
        mode_box.pack(side="left", padx=8)
        ttk.Label(
            top,
            text=f"Каталог: {catalog_path.name} • статус: {catalog.get('status', 'UNKNOWN')}",
        ).pack(side="left", padx=8)

        columns = ("kind", "review", "license", "duration", "asset")
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for column, label, width in (
            ("kind", "Тип / кандидат", 220),
            ("review", "Музыкальная проверка", 180),
            ("license", "Лицензия", 150),
            ("duration", "Длительность, сек", 120),
            ("asset", "WAV / ID", 360),
        ):
            tree.heading(column, text=label)
            tree.column(column, width=width, anchor="w")
        tree.pack(fill="both", expand=True, pady=(8, 6))
        tree.tag_configure("candidate", foreground=NEON_STAGE_THEME["palette"]["warning"])
        tree.tag_configure("staged", foreground=NEON_STAGE_THEME["palette"]["accent"])
        tree.tag_configure("playable", foreground=NEON_STAGE_THEME["palette"]["success"])
        tree.tag_configure("pattern_instrument", foreground=NEON_STAGE_THEME["palette"]["accent_purple"])

        details = tk.Text(
            frame, height=7, wrap="word", font=("Consolas", 9),
            bg=NEON_STAGE_THEME["palette"]["lowlight"],
            fg=NEON_STAGE_THEME["palette"]["lcd_text"],
            insertbackground=NEON_STAGE_THEME["palette"]["accent_glow"],
            selectbackground=NEON_STAGE_THEME["palette"]["control_face"],
            relief="flat", highlightthickness=1,
            highlightbackground=NEON_STAGE_THEME["palette"]["control_border"],
        )
        details.pack(fill="x")
        item_records = {}

        def refresh_mode(*_args):
            tree.delete(*tree.get_children())
            item_records.clear()
            selected_mode = next(
                (item for item in catalog.get("modes", []) if item.get("mode") == mode_var.get()),
                {},
            )
            for candidate in selected_mode.get("candidates", []):
                values = (
                    candidate.get("candidate_type", "ANALYSIS_CANDIDATE"),
                    candidate.get("review_status", "NEEDS_MUSICAL_REVIEW"),
                    candidate.get("license_status", "UNREVIEWED"),
                    "",
                    str(candidate.get("candidate_id") or candidate.get("source_path") or "analysis only"),
                )
                row_id = tree.insert("", "end", values=values, tags=("candidate",))
                item_records[row_id] = candidate
            for asset in browser_assets_for_mode(catalog, mode_var.get()):
                is_pattern_instrument = asset.get("playable_in_pattern_instrument") is not None
                asset_kind = "PATTERN INSTRUMENT" if is_pattern_instrument else asset.get("kind", "STAGED_WAV")
                values = (
                    asset_kind,
                    asset.get("review_status", "NEEDS_MUSICAL_REVIEW"),
                    asset.get("license_status", "UNREVIEWED"),
                    asset.get("duration_seconds", ""),
                    asset.get("asset_id", ""),
                )
                if is_pattern_instrument:
                    row_tag = "pattern_instrument"
                else:
                    row_tag = "playable" if asset.get("playable") else "staged"
                row_id = tree.insert("", "end", values=values, tags=(row_tag,))
                item_records[row_id] = asset
            details.delete("1.0", "end")
            details.insert("end", json.dumps({
                "plugin_target_category": selected_mode.get("mode"),
                "status": selected_mode.get("status"),
                "assets": selected_mode.get("asset_count", 0),
                "playable_assets": selected_mode.get("playable_asset_count", 0),
                "analysis_candidates": selected_mode.get("candidate_count", 0),
                "pattern_instrument_assets": (
                    len(catalog.get("pattern_instrument_assets", []))
                    if mode_var.get() == "PATTERN MODE" else 0
                ),
                "description": selected_mode.get("description", ""),
            }, ensure_ascii=False, indent=2))

        def show_selected(_event=None):
            selection = tree.selection()
            if not selection:
                return
            details.delete("1.0", "end")
            details.insert("end", json.dumps(item_records[selection[0]], ensure_ascii=False, indent=2))

        def preview_selected():
            selection = tree.selection()
            if not selection:
                messagebox.showinfo("Предпрослушивание", "Выберите WAV-кандидат.", parent=window)
                return
            record = item_records[selection[0]]
            relative = record.get("asset_file")
            if not relative:
                messagebox.showinfo(
                    "Предпрослушивание",
                    "Это аналитический кандидат без извлечённого WAV. Сначала выполните извлечение.",
                    parent=window,
                )
                return
            audio = (catalog_path.parent / relative).resolve()
            try:
                audio.relative_to(STAGING_ROOT.resolve())
            except ValueError:
                messagebox.showerror("Предпрослушивание", "Путь WAV выходит за пределы staging.", parent=window)
                return
            if not audio.is_file() or audio.suffix.lower() not in {".wav", ".wave"}:
                messagebox.showerror("Предпрослушивание", f"WAV не найден: {audio}", parent=window)
                return
            try:
                import winsound
                winsound.PlaySound(None, 0)
                winsound.PlaySound(str(audio), winsound.SND_FILENAME | winsound.SND_ASYNC)
                self.status.set("Предпрослушивание staging WAV-кандидата")
                self._write(f"[SAMPLE BROWSER] Предпрослушивание: {audio}")
            except Exception as exc:
                messagebox.showerror("Предпрослушивание", str(exc), parent=window)

        mode_box.bind("<<ComboboxSelected>>", refresh_mode)
        tree.bind("<<TreeviewSelect>>", show_selected)
        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(6, 0))
        ttk.Button(buttons, text="Прослушать выбранный WAV", command=preview_selected).pack(side="left")
        ttk.Button(buttons, text="Остановить", command=self.stop_preview).pack(side="left", padx=6)
        ttk.Button(buttons, text="Обновить", command=refresh_mode).pack(side="left", padx=6)
        ttk.Label(
            frame,
            text="Playable допускается только при REVIEWED + LICENSE_APPROVED и подтверждённой целостности. "
                 "Все остальные записи остаются кандидатами.",
        ).pack(anchor="w", pady=(6, 0))
        refresh_mode()

    def audit_other(self) -> None:
        try:
            samples = self._samples()
        except Exception as exc:
            messagebox.showerror("Папка Samples", str(exc))
            return
        report_dir = MANAGER_DIR / "reports" / ("other_audit_" + __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S"))
        self._background("Аудит OTHER", lambda: audit_other_library(samples, report_dir))

    def distribute_other(self) -> None:
        try:
            samples = self._samples()
        except Exception as exc:
            messagebox.showerror("Папка Samples", str(exc))
            return
        decision_file = filedialog.askopenfilename(
            title="Выберите вручную проверенный other_decisions.json",
            initialdir=str(samples / "OTHER"),
            filetypes=[("OTHER decisions", "*.json")],
        )
        if not decision_file:
            return
        try:
            plan = route_approved_to_other(samples, Path(decision_file), approve=False)
        except Exception as exc:
            messagebox.showerror("План OTHER", str(exc))
            return
        preview = "\n".join(f'{item["source_path"]} → {item["destination_path"]} ({item["reason"]})' for item in plan["entries"])
        self._write("ПЛАН OTHER (без изменений):\n" + (preview or "Нет явно одобренных записей."))
        if not plan["entries"]:
            return
        if not messagebox.askyesno("Подтверждение копирования в OTHER",
                                   f"Будет скопировано файлов: {len(plan['entries'])}.\nSHA-256 проверяется; оригиналы останутся на месте. Продолжить?"):
            return
        self._background("Копирование в OTHER", lambda: route_approved_to_other(
            samples, Path(decision_file), approve=True))

    def extract_patterns(self) -> None:
        report_path = filedialog.askopenfilename(
            title="Выберите unified_audio_analysis.json из отчёта анализа",
            initialdir=str(MANAGER_DIR / "reports"),
            filetypes=[("Audio analysis report", "unified_audio_analysis.json"), ("JSON", "*.json")],
        )
        if not report_path:
            return
        try:
            records = json.loads(Path(report_path).read_text(encoding="utf-8"))
            if not isinstance(records, list):
                raise ValueError("Ожидается список аудио-отчётов.")
            eligible = [
                item for item in records
                if (item.get("pattern_analysis") or {}).get("pattern_analysis", {}).get("patterns")
            ]
            if not eligible:
                messagebox.showinfo("Паттерны не найдены",
                                    "В отчёте нет повторяющихся ритмических кандидатов для извлечения.")
                return
            total = sum(
                len(item["pattern_analysis"]["pattern_analysis"]["patterns"])
                for item in eligible
            )
            if not messagebox.askyesno(
                "Физическое извлечение WAV",
                f"Найдено исходных файлов с кандидатами: {len(eligible)}.\n"
                f"Кандидатов паттернов: {total}.\n"
                "Будут созданы отдельные WAV-фрагменты в LibraryManager/staging/clips "
                "и JSON-манифесты в staging/manifests.\n"
                "Все фрагменты останутся NEEDS_MUSICAL_REVIEW и UNREVIEWED.\n"
                "Продолжить?"
            ):
                return
        except Exception as exc:
            messagebox.showerror("Отчёт анализа", str(exc))
            return

        def work():
            extracted = []
            failures = []
            for item in eligible:
                pattern_report = {
                    "source": item["source_path"],
                    "source_sha256": item["source_sha256"],
                    "pattern_analysis": (item.get("pattern_analysis") or {}).get("pattern_analysis", {}),
                }
                try:
                    extracted.extend(extract_pattern_occurrences(pattern_report, STAGING_ROOT))
                except Exception as exc:
                    failures.append({
                        "source_path": item.get("source_path"),
                        "error": f"{type(exc).__name__}: {exc}",
                    })
            return {
                "extracted_count": len(extracted),
                "assets": extracted,
                "failures": failures,
                "review_required": True,
                "license_review_required": True,
            }
        self._background("Извлечение ритм-паттернов", work)

    def open_review_queue(self) -> None:
        """List staged WAV manifests awaiting independent musical/license review."""
        manifests = sorted((STAGING_ROOT / "manifests").glob("*.json"))
        rows = []
        for path in manifests:
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
                rows.append((
                    path, str(record.get("kind", "UNKNOWN")),
                    str(record.get("review_status", "NEEDS_MUSICAL_REVIEW")),
                    str(record.get("license_status", "UNREVIEWED")),
                    str(record.get("duration_seconds", "")),
                ))
            except (OSError, json.JSONDecodeError):
                rows.append((path, "INVALID_MANIFEST", "ERROR", "ERROR", ""))

        window = tk.Toplevel(self.root)
        window.title("Очередь ручной проверки — Staging")
        window.geometry("960x460")
        window.configure(bg=NEON_STAGE_THEME["palette"]["window_bg"])
        window.transient(self.root)
        frame = ttk.Frame(window, padding=10)
        frame.pack(fill="both", expand=True)
        columns = ("kind", "review", "license", "duration", "manifest")
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for column, label, width in (
            ("kind", "Тип", 150), ("review", "Музыкальный статус", 190),
            ("license", "Лицензия", 150), ("duration", "Длительность, сек", 120),
            ("manifest", "Манифест", 340),
        ):
            tree.heading(column, text=label)
            tree.column(column, width=width, anchor="w")
        tree.pack(fill="both", expand=True)
        paths = {}
        for path, kind, review, license_status, duration in rows:
            tree_id = tree.insert("", "end", values=(kind, review, license_status, duration, path.name))
            paths[tree_id] = path

        ttk.Label(frame, text=f"Манифестов: {len(rows)}. Музыкальная проверка и лицензия подтверждаются отдельно.").pack(anchor="w", pady=6)

        def selected_manifest() -> Path | None:
            selection = tree.selection()
            if not selection:
                messagebox.showinfo("Очередь проверки", "Сначала выберите WAV-манифест.", parent=window)
                return None
            return paths[selection[0]]

        def audio_path_for(manifest: Path, field: str, *, require_staging: bool) -> Path:
            record = json.loads(manifest.read_text(encoding="utf-8"))
            raw = Path(str(record.get(field, ""))).expanduser()
            audio = raw if raw.is_absolute() else (manifest.parent / raw)
            audio = audio.resolve()
            if not audio.is_file() or audio.suffix.lower() not in {".wav", ".wave"}:
                raise ValueError(f"Файл {field} отсутствует или не является WAV: {audio}")
            if require_staging:
                try:
                    audio.relative_to(STAGING_ROOT.resolve())
                except ValueError as exc:
                    raise ValueError("Производный WAV должен находиться внутри LibraryManager/staging.") from exc
            return audio

        def play_selected(field: str) -> None:
            manifest = selected_manifest()
            if manifest is None:
                return
            try:
                audio = audio_path_for(manifest, field, require_staging=(field == "derived_path"))
                import winsound
                winsound.PlaySound(None, 0)
                winsound.PlaySound(str(audio), winsound.SND_FILENAME | winsound.SND_ASYNC)
                self._write(f"Предпрослушивание {field}: {audio}")
                self.status.set("Воспроизведение WAV-кандидата" if field == "derived_path" else "Воспроизведение оригинала")
            except Exception as exc:
                messagebox.showerror("Предпрослушивание", str(exc), parent=window)

        def stop_selected_preview() -> None:
            try:
                import winsound
                winsound.PlaySound(None, 0)
                self.status.set("Воспроизведение остановлено")
            except Exception as exc:
                messagebox.showerror("Предпрослушивание", str(exc), parent=window)

        def review_selected() -> None:
            selected_path = selected_manifest()
            if selected_path is None:
                return
            window.destroy()
            self.review_candidate(str(selected_path))

        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(4, 0))
        ttk.Button(controls, text="▶ Прослушать фрагмент", command=lambda: play_selected("derived_path")).pack(side="left", padx=3)
        ttk.Button(controls, text="▶ Прослушать оригинал", command=lambda: play_selected("source_path")).pack(side="left", padx=3)
        ttk.Button(controls, text="■ Стоп", command=stop_selected_preview).pack(side="left", padx=3)
        ttk.Button(controls, text="Проверить выбранный WAV", command=review_selected).pack(side="right", padx=3)
        tree.bind("<Double-1>", lambda _event: play_selected("derived_path"))
        if not rows:
            self._write("Очередь ручной проверки пуста: staging/manifests не содержит JSON-манифестов.")

    def review_candidate(self, selected_path: str | None = None) -> None:
        """Collect explicit musical and license decisions for one staged WAV."""
        selected = selected_path or filedialog.askopenfilename(
            title="Выберите WAV-манифест для музыкальной и лицензионной проверки",
            initialdir=str(STAGING_ROOT / "manifests"),
            filetypes=[("Staging manifests", "*.json")],
        )
        if not selected:
            return
        from factory_curator import INSTRUMENTS, ROLES, STYLES, TONES

        def ask_value(title: str, prompt: str, values: set[str]) -> str | None:
            return simpledialog.askstring(
                title, prompt + "\n\nДопустимые значения:\n" + ", ".join(sorted(values)),
                parent=self.root,
            )

        style = ask_value("Стиль", "Укажите подтверждённый стиль:", STYLES)
        if style is None:
            return
        instrument = ask_value("Инструмент", "Укажите подтверждённое семейство инструмента:", INSTRUMENTS)
        if instrument is None:
            return
        role = ask_value("Тип материала", "Укажите подтверждённую роль материала:", ROLES)
        if role is None:
            return
        tone = ask_value("Характер звучания", "Укажите подтверждённый тип звучания:", TONES)
        if tone is None:
            return
        notes = simpledialog.askstring(
            "Музыкальная проверка",
            "Что прослушано и проверено? Укажите границы, характер партии и возможные ограничения:",
            parent=self.root,
        )
        if notes is None:
            return
        evidence = simpledialog.askstring(
            "Лицензионное основание",
            "Укажите лицензию/источник и основание, разрешающее включение производного WAV в распространяемую FACTORY-библиотеку:",
            parent=self.root,
        )
        if evidence is None:
            return
        mode_text = simpledialog.askstring(
            "Категории назначения библиотеки для VST3",
            "Укажите только подтверждённые категории подготовленной библиотеки через запятую. "
            "Это не режимы Manager; музыкальные режимы плагина — MELODY и PATTERN. "
            "Можно оставить пустым, если назначение пока неизвестно.\n\n"
            + ", ".join(MODE_ORDER),
            parent=self.root,
        )
        if mode_text is None:
            return
        selected_modes = [item.strip().upper() for item in mode_text.split(",") if item.strip()]
        invalid_modes = [item for item in selected_modes if item not in MODE_ORDER]
        if invalid_modes:
            messagebox.showerror(
                "Категории библиотеки VST3",
                "Неизвестные разделы: " + ", ".join(invalid_modes)
                + "\nДопустимые значения: " + ", ".join(MODE_ORDER),
                parent=self.root,
            )
            return
        if not messagebox.askyesno(
            "Подтверждение REVIEWED",
            "Подтверждаете, что лично прослушали WAV, проверили музыкальное содержимое и границы, "
            "а также корректность выбранных категорий назначения для библиотеки VST3?",
            parent=self.root,
        ):
            return
        mapping_text = simpledialog.askstring(
            "Подтверждённая музыкальная привязка",
            "Введите только подтверждённые данные из прослушивания: "
            "MIDI:60, CHORD:C или NOTES:60,62,64. "
            "Оставьте пустым, если нота/аккорд/последовательность не подтверждены.",
            parent=self.root,
        )
        if mapping_text is None:
            return
        confirmed_midi_note = None
        confirmed_chord_name = None
        confirmed_note_sequence = []
        token = mapping_text.strip()
        try:
            if token.upper().startswith("MIDI:"):
                confirmed_midi_note = int(token.split(":", 1)[1].strip())
                if not 0 <= confirmed_midi_note <= 127:
                    raise ValueError
            elif token.upper().startswith("CHORD:"):
                confirmed_chord_name = token.split(":", 1)[1].strip()
                if not confirmed_chord_name or len(confirmed_chord_name) > 24:
                    raise ValueError
            elif token.upper().startswith("NOTES:"):
                confirmed_note_sequence = [
                    int(item.strip()) for item in token.split(":", 1)[1].split(",") if item.strip()
                ]
                if len(confirmed_note_sequence) < 2 or any(
                    note < 0 or note > 127 for note in confirmed_note_sequence
                ):
                    raise ValueError
            elif token:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Музыкальная привязка",
                "Формат: MIDI:60, CHORD:C или NOTES:60,62,64. "
                "MIDI-ноты должны быть в диапазоне 0–127.",
                parent=self.root,
            )
            return
        technique_text = simpledialog.askstring(
            "Подтверждённые техники",
            "Введите только прослушанные и подтверждённые техники через запятую.\n"
            + ", ".join(TECHNIQUES) + "\nОставьте пустым, если техника не подтверждена.",
            parent=self.root,
        )
        if technique_text is None:
            return
        confirmed_techniques = [
            item.strip().upper().replace(" ", "_").replace("-", "_")
            for item in technique_text.split(",") if item.strip()
        ]
        velocity_layer = simpledialog.askstring(
            "Velocity layer",
            "Подтверждённый слой: LOW, MEDIUM, HIGH или UNKNOWN.",
            initialvalue="UNKNOWN", parent=self.root,
        )
        if velocity_layer is None:
            return
        velocity_layer = velocity_layer.strip().upper()
        advanced_text = simpledialog.askstring(
            "Структура Pattern / Melody",
            "Необязательно: вставьте JSON с подтверждёнными событиями Pattern/Melody. "
            "Если данных нет — оставьте {}.\n"
            "Pattern: pattern_performance_review {loop_start_sample, loop_end_sample, tempo_bpm, "
            "time_signature, attack_events, beat_grid, technique_events, harmonic_events, "
            "cycle_integrity_verified:true, musical_review_verified:true}.\n"
            "Melody: confirmed_melody_events [{midi_note,start_beats,duration_beats,velocity}, ...], "
            "melody_phrase_boundaries [0,4], melody_mapping_verified:true.\n"
            "Также допустимы velocity_min и velocity_max.",
            initialvalue="{}", parent=self.root,
        )
        if advanced_text is None:
            return
        try:
            advanced_metadata = json.loads(advanced_text or "{}")
            if not isinstance(advanced_metadata, dict):
                raise ValueError("Нужен JSON-объект.")
        except (json.JSONDecodeError, ValueError) as exc:
            messagebox.showerror("Структура Pattern / Melody", f"Некорректный JSON: {exc}", parent=self.root)
            return

        if not messagebox.askyesno(
            "Подтверждение LICENSE_APPROVED",
            "Подтверждаете, что указанное лицензионное основание действительно разрешает распространение этого материала?",
            parent=self.root,
        ):
            return

        def work():
            return review_manifest(
                Path(selected), STAGING_ROOT,
                style_family=style.strip().upper(),
                instrument_family=instrument.strip().upper(),
                asset_role=role.strip().upper(),
                tone_family=tone.strip().upper(),
                musical_review_notes=notes,
                license_evidence=evidence,
                approve_musical_review=True,
                approve_license=True,
                mode_assignments=selected_modes,
                confirmed_midi_note=confirmed_midi_note,
                confirmed_chord_name=confirmed_chord_name,
                confirmed_note_sequence=confirmed_note_sequence,
                confirmed_techniques=confirmed_techniques,
                confirmed_velocity_layer=velocity_layer,
                advanced_metadata=advanced_metadata,
            )
        self._background("Музыкальная и лицензионная проверка WAV", work)

    def finalize_library(self) -> None:
        """Audit staging and distributed Factory without moving or copying assets."""
        try:
            samples = self._samples()
        except Exception as exc:
            messagebox.showerror("Папка Samples", str(exc))
            return
        def progress(message: str) -> None:
            self._queue_progress(message)
        self._background(
            "Финализация библиотеки",
            lambda: finalize_library_audit(
                samples, STAGING_ROOT,
                progress=progress,
                cancel_event=self._cancel_event,
            ),
        )

    def distribute(self) -> None:
        """Automatically distribute all independently verified approved assets."""
        try:
            samples = self._samples()
        except Exception as exc:
            messagebox.showerror("Папка Samples", str(exc))
            return
        manifests_dir = STAGING_ROOT / "manifests"
        manifest_count = len(list(manifests_dir.glob("*.json"))) if manifests_dir.is_dir() else 0
        if manifest_count == 0:
            messagebox.showinfo("FACTORY", "В staging пока нет манифестов для распределения.")
            return
        if not messagebox.askyesno(
            "Автоматическое распределение FACTORY",
            f"Менеджер автоматически проверит все {manifest_count} манифестов.\n"
            "Будут скопированы только кандидаты с подтверждённой музыкальной проверкой, "
            "разрешённой лицензией, целыми SHA-256 и корректными PCM WAV/границами.\n"
            "Повреждённые, недоступные и неподтверждённые записи будут внесены в отчёт, "
            "а обработка продолжится со следующими. Каждый WAV копируется отдельной транзакцией.\n"
            "Оригиналы не перемещаются и не удаляются. Продолжить?",
        ):
            self.status.set("Автоматическое распределение отменено")
            return

        def work():
            return auto_distribute_approved(
                samples, STAGING_ROOT, approve=True,
                journal_path=samples / "FACTORY" / "LibraryManagerReports" / "operations.jsonl",
                cancel_event=self._cancel_event,
                progress=self._queue_progress,
            )

        self._background("Автоматическое распределение FACTORY", work)

    def audit_cleanup(self) -> None:
        try:
            samples = self._samples()
        except Exception as exc:
            messagebox.showerror("Папка Samples", str(exc))
            return
        report_path = MANAGER_DIR / "reports" / ("cleanup_audit_" + __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S") + ".json")
        self._background("Полный аудит Import", lambda: audit_all_import_sources(
            samples, STAGING_ROOT, report_path))

    def cleanup(self) -> None:
        try:
            samples = self._samples()
        except Exception as exc:
            messagebox.showerror("Папка Samples", str(exc))
            return
        audit_path = filedialog.askopenfilename(
            title="Выберите полный cleanup_audit_*.json",
            initialdir=str(MANAGER_DIR / "reports"),
            filetypes=[("Cleanup audit", "cleanup_audit_*.json"), ("JSON", "*.json")],
        )
        if not audit_path:
            return
        try:
            audit = json.loads(Path(audit_path).read_text(encoding="utf-8"))
            summary = audit["summary"]
            if summary.get("blocked_sources") or summary.get("errors") or summary.get("eligible_for_cleanup") != summary.get("source_files_scanned"):
                messagebox.showwarning(
                    "Очистка заблокирована",
                    "Не все исходники имеют полностью проверенные производные копии. "
                    "Сначала устраните блокировки в отчёте. Ни один файл не удалён."
                )
                return
        except Exception as exc:
            messagebox.showerror("Отчёт очистки", str(exc))
            return
        if not messagebox.askyesno(
            "Удаление оригиналов — подтверждение 1/2",
            f"Аудит охватил все {summary['source_files_scanned']} исходных файлов. "
            "Все зависимости имеют проверенные копии. Удалить оригиналы из Import?"
        ):
            return
        if not messagebox.askyesno(
            "Удаление оригиналов — подтверждение 2/2",
            "Подтверждаете окончательное удаление всех исходников? "
            "Перед удалением аудит и SHA-256 будут проверены повторно."
        ):
            return
        self._background("Очистка исходников", lambda: cleanup_sources_from_audit(
            samples, STAGING_ROOT, Path(audit_path), approve=True,
            confirm_all_dependents_accounted_for=True,
            journal_path=samples / "LibraryManagerReports" / "cleanup.jsonl"))

    def open_user_guide(self) -> None:
        """Open the numbered Russian quick-start guide in the default browser."""
        guide = resource_file(
            "PORTABLE_USER_GUIDE_RU.md", module_file=__file__, bundle_dir=BUNDLE_DIR
        )
        if not guide.is_file():
            messagebox.showinfo("Инструкция", "Файл PORTABLE_USER_GUIDE_RU.md не найден рядом с приложением.")
            return
        try:
            import os
            os.startfile(str(guide))
        except Exception as exc:
            messagebox.showerror("Инструкция", str(exc))

    def open_reports(self) -> None:
        path = MANAGER_DIR / "reports"
        path.mkdir(parents=True, exist_ok=True)
        self._open_path(path)

    def open_staging(self) -> None:
        STAGING_ROOT.mkdir(parents=True, exist_ok=True)
        self._open_path(STAGING_ROOT)

    @staticmethod
    def _open_path(path: Path) -> None:
        import os
        import subprocess
        if os.name == "nt":
            os.startfile(str(path))
        else:
            subprocess.Popen(["xdg-open", str(path)])


def main() -> int:
    root = tk.Tk()
    LibraryManagerApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
