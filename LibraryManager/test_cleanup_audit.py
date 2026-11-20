from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from cleanup_audit import audit_all_import_sources, cleanup_sources_from_audit
from other_audit import route_approved_to_other


class CleanupAuditTests(unittest.TestCase):
    def test_unaccounted_import_source_blocks_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Samples"
            incoming = root / "Import Sample Guitar"
            incoming.mkdir(parents=True)
            (incoming / "orphan.wav").write_bytes(b"source")
            report_path = Path(tmp) / "cleanup.json"
            report = audit_all_import_sources(root, Path(tmp) / "staging", report_path)
            self.assertEqual(report["summary"]["source_files_scanned"], 1)
            self.assertEqual(report["summary"]["eligible_for_cleanup"], 0)
            self.assertIn("NO_DEPENDENCY_MANIFESTS", report["sources"][0]["blockers"])
            self.assertTrue((incoming / "orphan.wav").exists())

    def test_verified_other_copy_can_be_cleaned_only_after_explicit_double_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Samples"
            incoming = root / "Import Sample Guitar"
            incoming.mkdir(parents=True)
            source = incoming / "unrelated.xyz"
            source.write_bytes(b"unrelated")
            digest = hashlib.sha256(source.read_bytes()).hexdigest().upper()
            decisions = Path(tmp) / "decisions.json"
            decisions.write_text(json.dumps({"decisions": {
                str(source.resolve()): {"route_to_other": True, "sha256": digest,
                                        "reason": "Human-reviewed non-guitar asset"}
            }}), encoding="utf-8")
            route_approved_to_other(root, decisions, approve=True)
            audit_path = Path(tmp) / "cleanup.json"
            report = audit_all_import_sources(root, Path(tmp) / "staging", audit_path)
            self.assertEqual(report["summary"]["eligible_for_cleanup"], 1)
            with self.assertRaises(PermissionError):
                cleanup_sources_from_audit(root, Path(tmp) / "staging", audit_path)
            result = cleanup_sources_from_audit(
                root, Path(tmp) / "staging", audit_path, approve=True,
                confirm_all_dependents_accounted_for=True,
                journal_path=Path(tmp) / "cleanup.jsonl")
            self.assertEqual(result["status"], "CLEANUP_COMPLETED")
            self.assertFalse(source.exists())
            self.assertTrue((root / "OTHER" / "unrelated.xyz").exists())


if __name__ == "__main__":
    unittest.main()
