from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from mode_assignment_index import MODE_ORDER, build_mode_assignment_index


class ModeAssignmentIndexTests(unittest.TestCase):
    def _asset(self, root: Path, *, modes, review="REVIEWED", license_status="LICENSE_APPROVED",
               metadata=None, validation=None):
        wav = root / "clips" / "asset.wav"
        wav.parent.mkdir(parents=True, exist_ok=True)
        wav.write_bytes(b"RIFF-test-pcm")
        digest = hashlib.sha256(wav.read_bytes()).hexdigest().upper()
        manifest = root / "manifests" / "asset.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({
            "asset_id": "ASSET-1", "derived_path": str(wav),
            "derived_sha256": digest, "source_path": "source.wav",
            "source_sha256": "A" * 64, "source_start_sample": 0,
            "source_end_sample": 100, "asset_kind": "TEST",
            "mode_assignments": modes, "review_status": review,
            "license_status": license_status, "musical_metadata": metadata or {},
            "review_validation": validation or {},
        }), encoding="utf-8")
        return manifest

    def test_all_modes_always_exist_and_assignments_are_indexed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._asset(root, modes=["PATTERN MODE", "MELODY MODE"],
                        metadata={"confirmed_note_sequence": [60, 62, 64]},
                        validation={"musical_mapping_verified": True})
            report = build_mode_assignment_index(root)
            self.assertEqual([item["mode"] for item in report["modes"]], list(MODE_ORDER))
            self.assertEqual(report["assignment_count"], 2)
            modes = {item["mode"]: item for item in report["modes"]}
            self.assertEqual(modes["PATTERN MODE"]["assignment_count"], 1)
            self.assertEqual(modes["MELODY MODE"]["assignment_count"], 1)
            self.assertFalse(modes["MELODY MODE"]["assets"][0]["source_modified"])

    def test_unapproved_license_blocks_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._asset(root, modes=["SAMPLE MODE"], license_status="UNREVIEWED",
                        metadata={"confirmed_midi_note": 60})
            report = build_mode_assignment_index(root)
            asset = next(x for x in report["modes"] if x["mode"] == "SAMPLE MODE")["assets"][0]
            self.assertEqual(asset["runtime_status"], "NOT_RUNTIME_READY")
            self.assertIn("LICENSE_NOT_APPROVED", asset["runtime_blockers"])

    def test_melody_requires_note_mapping_even_when_reviewed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._asset(root, modes=["MELODY MODE"])
            report = build_mode_assignment_index(root)
            asset = next(x for x in report["modes"] if x["mode"] == "MELODY MODE")["assets"][0]
            self.assertIn("MELODY_NOTE_MAPPING_NOT_CONFIRMED", asset["runtime_blockers"])

    def test_outside_or_tampered_wav_is_not_runtime_ready(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = self._asset(root, modes=["SAMPLE MODE"],
                                   metadata={"confirmed_midi_note": 60})
            wav = root / "clips" / "asset.wav"
            wav.write_bytes(b"tampered")
            report = build_mode_assignment_index(root)
            asset = next(x for x in report["modes"] if x["mode"] == "SAMPLE MODE")["assets"][0]
            self.assertIn("DERIVED_WAV_MISSING_OR_HASH_MISMATCH", asset["runtime_blockers"])

    def test_invalid_mode_assignment_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self._asset(root, modes=["NOT A MODE"])
            report = build_mode_assignment_index(root)
            self.assertEqual(len(report["rejected_manifests"]), 1)
            self.assertEqual(report["assignment_count"], 0)


if __name__ == "__main__":
    unittest.main()
