"""Runtime paths for relocatable Portable and per-user installed Manager builds."""
from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Callable


APP_FOLDER_NAME = "POP PUNK GUITAR Library Manager"


def _probe_writable(directory: Path) -> bool:
    """Create the directory and prove that a temporary file can be written there."""
    try:
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            prefix=".ppgu-write-check-", suffix=".tmp",
            dir=directory, delete=True,
        ):
            pass
        return True
    except OSError:
        return False


def _portable_profile_id(bundle: Path) -> str:
    """Read a build-stable profile token so a read-only portable folder can move."""
    marker = bundle / "portable.mode"
    try:
        value = marker.read_text(encoding="utf-8").strip()
    except OSError:
        value = ""
    if not value:
        value = bundle.name or "default"
    value = re.sub(r"[^A-Za-z0-9_-]", "_", value)[:80]
    return value or "default"


def resolve_runtime_paths(
    module_file: str | Path,
    *,
    executable: str | Path | None = None,
    frozen: bool | None = None,
    environ: dict[str, str] | None = None,
    writable_probe: Callable[[Path], bool] | None = None,
) -> tuple[Path, Path, bool]:
    """Return (bundle_dir, writable_data_dir, portable_mode).

    Portable builds can be extracted to any directory or drive. They keep mutable
    state in ./UserData when writable and fall back to a profile-specific
    LocalAppData folder when the application directory is protected/read-only.
    Installed builds keep mutable state in LocalAppData, never Program Files.
    Source checkouts retain their historic in-tree reports/staging layout.
    """
    env = os.environ if environ is None else environ
    probe = writable_probe or _probe_writable
    is_frozen = bool(getattr(sys, "frozen", False)) if frozen is None else bool(frozen)
    if is_frozen:
        exe = Path(executable or sys.executable).expanduser().resolve()
        bundle = exe.parent
        portable = (bundle / "portable.mode").is_file()
        local = env.get("LOCALAPPDATA")
        local_root = (
            Path(local).expanduser()
            if local else Path.home() / "AppData" / "Local"
        )
        if portable:
            adjacent_data = bundle / "UserData"
            if probe(adjacent_data):
                return bundle, adjacent_data.resolve(), True
            fallback = (
                local_root / APP_FOLDER_NAME / "PortableFallback"
                / _portable_profile_id(bundle)
            )
            if probe(fallback):
                return bundle, fallback.resolve(), True
            raise PermissionError(
                "Не удалось создать UserData рядом с Portable-программой "
                "и резервную папку данных в LocalAppData. Переместите Manager "
                "в доступную для записи папку или проверьте права Windows."
            )

        installed_data = local_root / APP_FOLDER_NAME
        if not probe(installed_data):
            raise PermissionError(
                f"Не удалось записывать пользовательские данные Manager: {installed_data}"
            )
        return bundle, installed_data.resolve(), False

    module_dir = Path(module_file).expanduser().resolve().parent
    return module_dir, module_dir, False


def resource_file(name: str, *, module_file: str | Path,
                  bundle_dir: str | Path | None = None) -> Path:
    """Resolve read-only packaged resources without writing into the bundle."""
    module_dir = Path(module_file).resolve().parent
    roots = []
    if getattr(sys, "_MEIPASS", None):
        roots.append(Path(sys._MEIPASS))
    if bundle_dir is not None:
        roots.append(Path(bundle_dir))
    roots.append(module_dir)
    for root in roots:
        candidate = root / name
        if candidate.is_file():
            return candidate
    return roots[0] / name if roots else module_dir / name


def runtime_staging_root(module_file: str | Path) -> Path:
    """Return the same writable staging root used by the GUI in every build mode."""
    _bundle, data_dir, _portable = resolve_runtime_paths(module_file)
    return (data_dir / "staging").resolve()
