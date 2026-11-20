from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import wave
from pathlib import Path

from finalization import audit_factory_library, finalize_staging


def write_wav(path: Path, frames: int) -> None:
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(8000)
        out.writeframes(b"\x01\x00" * frames)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class FinalizationTests(unittest.TestCase):
    def test_factory_audit_verifies_distributed_wav_and_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            factory = root / "Samples" / "FACTORY"
            category = factory / "POP_PUNK" / "WAV" / "ELECTRIC_GUITAR" / "RHYTHM_PATTERN" / "CRUNCH"
            category.mkdir(parents=True)
            wav_path = category / "riff.wav"
            write_wav(wav_path, 400)
            digest = sha(wav_path)
            record = {
                "asset_id": "FACTORY-001",
                "distributed_path": str(wav_path),
                "distributed_sha256": digest,
                "derived_sha256": digest,
                "distribution_status": "VERIFIED_COPIED",
                "distribution_category": "POP_PUNK/WAV/ELECTRIC_GUITAR/RHYTHM_PATTERN/CRUNCH",
                "review_status": "REVIEWED",
                "license_status": "LICENSE_APPROVED",
                "source_sha256": "A" * 64,
                "review_validation": {
                    "source_sha256_verified": True,
                    "derived_sha256_verified": True,
                    "sample_boundaries_verified": True,
                    "explicit_musical_approval": True,
                    "explicit_license_approval": True,
                },
                "musical_metadata": {
                    "style_family": "POP_PUNK",
                    "instrument_family": "ELECTRIC_GUITAR",
                    "asset_role": "RHYTHM_PATTERN",
                    "tone_family": "CRUNCH",
                    "musical_review_notes": "Reviewed.",
                    "license_evidence": "Redistribution allowed.",
                },
            }
            wav_path.with_suffix(".wav.json").write_text(json.dumps(record), encoding="utf-8")
            result = audit_factory_library(root / "Samples", reports_root=root / "reports")
            self.assertEqual(result["factory_wav_checked"], 1)
            self.assertEqual(result["factory_valid_count"], 1)
            self.assertTrue(result["factory_finalized"])

    def test_reports_factory_ready_and_review_pending_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staging = root / "staging"
            (staging / "clips").mkdir(parents=True)
            manifests = staging / "manifests"
            manifests.mkdir()
            source = root / "source.wav"
            write_wav(source, 1000)
            for name, review, license_status in (
                ("ready", "REVIEWED", "LICENSE_APPROVED"),
                ("pending", "NEEDS_MUSICAL_REVIEW", "UNREVIEWED"),
            ):
                clip = staging / "clips" / f"{name}.wav"
                write_wav(clip, 400)
                record = {
                    "asset_id": name,
                    "source_path": str(source),
                    "source_sha256": sha(source),
                    "source_start_sample": 100,
                    "source_end_sample": 500,
                    "derived_path": str(clip),
                    "derived_sha256": sha(clip),
                    "review_status": review,
                    "license_status": license_status,
                    "musical_metadata": {
                        "style_family": "POP_PUNK",
                        "instrument_family": "ELECTRIC_GUITAR",
                        "asset_role": "RHYTHM_PATTERN",
                        "tone_family": "CRUNCH",
                    },
                }
                if review == "REVIEWED":
                    record["review_validation"] = {
                        "source_sha256_verified": True,
                        "derived_sha256_verified": True,
                        "sample_boundaries_verified": True,
                        "explicit_musical_approval": True,
                        "explicit_license_approval": True,
                    }
                    record["musical_metadata"].update({
                        "musical_review_notes": "Reviewed by listening.",
                        "license_evidence": "License permits redistribution.",
                    })
                (manifests / f"{name}.json").write_text(json.dumps(record), encoding="utf-8")
            before_source = sha(source)
            result = finalize_staging(staging, reports_root=root / "reports")
            self.assertEqual(result["manifests_checked"], 2)
            report = Path(result["report_directory"]) / "finalization_inventory.csv"
            self.assertTrue(report.is_file())
            report_text = report.read_text(encoding="utf-8-sig")
            self.assertEqual(result["factory_ready_count"], 1, report_text)
            self.assertEqual(result["musical_review_required_count"], 1, report_text)
            self.assertFalse(result["distribution_executed"])
            self.assertEqual(sha(source), before_source)
            summary = json.loads((Path(result["report_directory"]) / "finalization_summary.json").read_text(encoding="utf-8"))
            self.assertTrue(summary["factory_distribution_allowed"])


if __name__ == "__main__":
    unittest.main()
