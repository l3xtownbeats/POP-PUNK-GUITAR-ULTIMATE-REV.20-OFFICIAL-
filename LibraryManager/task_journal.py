"""Durable, append-only task journal for the portable Library Manager.

The journal records task lifecycle and progress only. It never performs file
operations and is safe to replay for diagnostics after an interrupted run.
"""
from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class TaskJournal:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: str, *, task_id: str, task: str,
               details: dict[str, Any] | None = None,
               durable: bool = True) -> dict[str, Any]:
        if not event or not task_id or not task:
            raise ValueError("event, task_id and task are required")
        record = {
            "schema_version": SCHEMA_VERSION,
            "timestamp_utc": _utc_now(),
            "event": event,
            "task_id": task_id,
            "task": task,
            "details": details or {},
        }
        payload = json.dumps(record, ensure_ascii=False, sort_keys=True, default=str)
        with self._lock:
            with self.path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(payload + "\n")
                stream.flush()
                if durable:
                    os.fsync(stream.fileno())
        return record

    def start(self, task: str, *, details: dict[str, Any] | None = None) -> str:
        task_id = uuid.uuid4().hex
        self.append("STARTED", task_id=task_id, task=task, details=details)
        return task_id

    def progress(self, task_id: str, task: str, message: str) -> None:
        # Progress is frequent on large libraries. Flush the stream but avoid
        # a disk fsync for every line; lifecycle boundaries remain durable.
        self.append("PROGRESS", task_id=task_id, task=task,
                    details={"message": str(message)}, durable=False)

    def finish(self, task_id: str, task: str, *, result: Any = None) -> None:
        if isinstance(result, dict):
            summary = {"keys": sorted(str(key) for key in result.keys())}
            for key, value in result.items():
                if isinstance(value, (str, int, float, bool, type(None))):
                    summary[str(key)] = value
                elif isinstance(value, (list, tuple, dict)):
                    summary[str(key) + "_count"] = len(value)
        elif isinstance(result, (str, int, float, bool, type(None))):
            summary = result
        else:
            summary = str(result)
        self.append("SUCCEEDED", task_id=task_id, task=task,
                    details={"result_summary": summary})

    def fail(self, task_id: str, task: str, error: str) -> None:
        self.append("FAILED", task_id=task_id, task=task,
                    details={"error": str(error)})

    def cancel(self, task_id: str, task: str, reason: str = "Операция остановлена пользователем.") -> None:
        self.append("CANCELLED", task_id=task_id, task=task,
                    details={"reason": str(reason)})

    def history(self, *, limit: int | None = None) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records = []
        with self.path.open("r", encoding="utf-8") as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                    if item.get("schema_version") == SCHEMA_VERSION:
                        records.append(item)
                except (json.JSONDecodeError, AttributeError):
                    # Ignore a malformed/torn record; never rewrite the journal.
                    continue
        return records[-limit:] if limit is not None else records

    def latest_states(self) -> dict[str, dict[str, Any]]:
        states: dict[str, dict[str, Any]] = {}
        for item in self.history():
            state = states.setdefault(item["task_id"], {"task": item["task"]})
            state["last_event"] = item["event"]
            state["last_timestamp_utc"] = item["timestamp_utc"]
            state["details"] = item.get("details", {})
        return states
