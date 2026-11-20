from __future__ import annotations

import hashlib
import json
import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from other_audit import audit_other_library, route_approved_to_other


def make_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(8000)
        frames = [struct.pack("<h", int(9000 * math.sin(2 * math.pi * 220 * i / 8000)))
                  for i in range(16000)]
        out.writeframes(b"".join(frames))


class OtherAuditTests(unittest.TestCase):
    def test_audit_reports_other_and_unsupported_without_mutating_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Samples"
            incoming = root / "Import Sample Guitar"
            other = root / "OTHER"
            incoming.mkdir(parents=True)
            other.mkdir()
            unsupported = incoming / "readme.xyz"
            unsupported.write_text("not an audio asset", encoding="utf-8")
            wav = incoming / "guitar.wav"
            make_wav(wav)
            existing = other / "old.bin"
            existing.write_bytes(b"other")
            before = hashlib.sha256(wav.read_bytes()).hexdigest().upper()
            report_dir = Path(tmp) / "reports"
            summary = audit_other_library(root, report_dir)
            report = json.loads((report_dir / "other_audit.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["existing_other_files"], 1)
            self.assertEqual(summary["files_audited"], 3)
            by_path = {row["path"]: row for row in report["assets"]}
            self.assertEqual(by_path[str(unsupported.resolve())]["audit_status"], "OTHER_REVIEW_REQUIRED")
            self.assertEqual(by_path[str(wav.resolve())]["routing_decision"], "DO_NOT_AUTO_ROUTE")
            self.assertEqual(hashlib.sha256(wav.read_bytes()).hexdigest().upper(), before)
            self.assertTrue(unsupported.exists())
            self.assertTrue(existing.exists())

    def test_other_copy_requires_explicit_decision_and_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Samples"
            incoming = root / "Import Sample Guitar"
            incoming.mkdir(parents=True)
            source = incoming / "bad-format.xyz"
            source.write_bytes(b"opaque")
            digest = hashlib.sha256(source.read_bytes()).hexdigest().upper()
            decisions = Path(tmp) / "other_decisions.json"
            decisions.write_text(json.dumps({"decisions": {
                str(source.resolve()): {"route_to_other": True, "sha256": digest,
                                        "reason": "Manually confirmed unrelated source asset"}
            }}), encoding="utf-8")
            dry = route_approved_to_other(root, decisions, approve=False)
            self.assertEqual(dry["status"], "DRY_RUN")
            destination = root / "OTHER" / "bad-format.xyz"
            self.assertFalse(destination.exists())
            result = route_approved_to_other(root, decisions, approve=True)
            self.assertEqual(result["status"], "COPIED_VERIFIED")
            self.assertEqual(destination.read_bytes(), source.read_bytes())
            self.assertTrue(destination.with_suffix(".xyz.json").is_file())
            self.assertTrue(source.exists())


if __name__ == "__main__":
    unittest.main()
