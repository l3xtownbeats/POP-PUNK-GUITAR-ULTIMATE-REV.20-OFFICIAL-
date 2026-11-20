import json
import tempfile
import unittest
from pathlib import Path

from task_journal import TaskJournal


class TaskJournalTests(unittest.TestCase):
    def test_lifecycle_is_durable_and_ordered(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = TaskJournal(Path(directory) / "reports" / "tasks.jsonl")
            task_id = journal.start("Quick Scan", details={"samples": "Samples"})
            journal.progress(task_id, "Quick Scan", "12 files")
            journal.finish(task_id, "Quick Scan", result={"files": 12})

            records = journal.history()
            self.assertEqual([r["event"] for r in records],
                             ["STARTED", "PROGRESS", "SUCCEEDED"])
            self.assertTrue(all(r["task_id"] == task_id for r in records))
            self.assertEqual(journal.latest_states()[task_id]["last_event"], "SUCCEEDED")

    def test_failed_task_is_visible_as_incomplete_state(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = TaskJournal(Path(directory) / "tasks.jsonl")
            task_id = journal.start("Deep Analysis")
            journal.fail(task_id, "Deep Analysis", "decoder failed")
            state = journal.latest_states()[task_id]
            self.assertEqual(state["last_event"], "FAILED")
            self.assertIn("decoder failed", state["details"]["error"])

    def test_cancelled_task_is_not_recorded_as_success(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = TaskJournal(Path(directory) / "tasks.jsonl")
            task_id = journal.start("Deep Analysis")
            journal.cancel(task_id, "Deep Analysis", "user requested stop")
            state = journal.latest_states()[task_id]
            self.assertEqual(state["last_event"], "CANCELLED")
            self.assertEqual(state["details"]["reason"], "user requested stop")

    def test_malformed_trailing_record_does_not_hide_previous_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.jsonl"
            journal = TaskJournal(path)
            task_id = journal.start("Scan")
            with path.open("a", encoding="utf-8") as stream:
                stream.write('{"schema_version":')
            self.assertEqual(len(journal.history()), 1)
            self.assertEqual(journal.latest_states()[task_id]["last_event"], "STARTED")

    def test_progress_is_flushed_without_forcing_a_disk_sync(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            journal = TaskJournal(Path(directory) / "tasks.jsonl")
            task_id = journal.start("Scan")
            with patch("task_journal.os.fsync") as sync:
                journal.progress(task_id, "Scan", "100 files")
                sync.assert_not_called()
            self.assertEqual(journal.history()[-1]["details"]["message"], "100 files")

    def test_history_limit_returns_newest_records(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = TaskJournal(Path(directory) / "tasks.jsonl")
            task_id = journal.start("Scan")
            journal.progress(task_id, "Scan", "one")
            journal.finish(task_id, "Scan")
            self.assertEqual([r["event"] for r in journal.history(limit=2)],
                             ["PROGRESS", "SUCCEEDED"])


if __name__ == "__main__":
    unittest.main()
