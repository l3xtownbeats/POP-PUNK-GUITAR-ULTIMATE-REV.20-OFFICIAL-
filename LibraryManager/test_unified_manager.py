from __future__ import annotations

import hashlib
import json
import math
import shutil
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from unittest.mock import patch

from unified_manager import quick_scan, run_manager


def make_test_wav(path: Path, seconds: float = 2.0, rate: int = 8000) -> None:
    frames = []
    for index in range(int(seconds * rate)):
        # A short, repeated amplitude envelope gives the analyzer non-silent audio.
        phase = index / rate
        envelope = 1.0 if (phase % 0.5) < 0.18 else 0.0
        value = int(11000 * envelope * math.sin(2.0 * math.pi * 220.0 * phase))
        frames.append(struct.pack("<h", value))
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(b"".join(frames))


class UnifiedManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.samples = self.root / "Samples"
        self.incoming = self.samples / "Import Sample Guitar"
        self.incoming.mkdir(parents=True)
        self.reports = self.root / "reports"
        self.wav = self.incoming / "guitar.wav"
        make_test_wav(self.wav)
        self.original_hash = hashlib.sha256(self.wav.read_bytes()).hexdigest().upper()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_quick_scan_never_hashes_or_decodes_audio(self) -> None:
        with patch("unified_manager.sha256_file", side_effect=AssertionError("hash called")), \
             patch("unified_manager.wav_info", side_effect=AssertionError("decoder called")), \
             patch("unified_manager.analyse_wav", side_effect=AssertionError("acoustic analyzer called")):
            summary = quick_scan(self.samples, reports_root=self.reports)
        self.assertEqual(summary["scan_type"], "FAST_FILESYSTEM_ONLY")
        self.assertEqual(summary["files_found"], 1)
        self.assertFalse(summary["sha256_performed"])
        self.assertFalse(summary["audio_decoding_performed"])
        self.assertFalse(summary["source_files_modified"])
        self.assertEqual(summary["memory_strategy"], "STREAMING_CSV_BOUNDED_MEMORY")
        self.assertGreaterEqual(summary["elapsed_seconds"], 0)
        self.assertTrue((Path(summary["report_directory"]) / "quick_inventory.csv").is_file())
        self.assertEqual(hashlib.sha256(self.wav.read_bytes()).hexdigest().upper(),
                         self.original_hash)


    def test_quick_and_deep_scan_ignore_interrupted_import_temp_directories(self) -> None:
        temp_dir = self.incoming / ".manager-import-tmp-interrupted"
        temp_dir.mkdir()
        partial = temp_dir / "partial.wav"
        make_test_wav(partial)

        quick = quick_scan(self.samples, reports_root=self.reports)
        quick_csv = (
            Path(quick["report_directory"]) / "quick_inventory.csv"
        ).read_text(encoding="utf-8-sig")
        self.assertEqual(quick["files_found"], 1)
        self.assertIn("guitar.wav", quick_csv)
        self.assertNotIn("partial.wav", quick_csv)
        self.assertTrue(partial.is_file())

        deep = run_manager(
            self.samples, reports_root=self.reports,
            analyze_audio=False, guitar_source_confirmed=False,
            write_virtual=False, workers=1,
        )
        deep_csv = (
            Path(deep["report_directory"]) / "unified_inventory.csv"
        ).read_text(encoding="utf-8-sig")
        self.assertIn("guitar.wav", deep_csv)
        self.assertNotIn("partial.wav", deep_csv)
        self.assertTrue(partial.is_file())

    def test_quick_scan_default_reports_to_runtime_data_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_root = Path(tmp) / "UserData"
            module_root = Path(tmp) / "bundle"
            with patch(
                "unified_manager.resolve_runtime_paths",
                return_value=(module_root, data_root, True),
            ):
                result = quick_scan(self.samples)
            report_dir = Path(result["report_directory"])
            self.assertEqual(report_dir.parent, data_root / "reports")
            self.assertTrue((data_root / "reports").is_dir())

    def test_deep_scan_uses_runtime_reports_cache_and_staging_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_root = Path(tmp) / "UserData"
            module_root = Path(tmp) / "bundle"
            expected_staging = data_root / "staging"
            expected_staging.mkdir(parents=True)
            index_result = {"assignment_count": 0, "status": "NO_REVIEWED_ASSETS", "assignments": []}
            with patch(
                "unified_manager.resolve_runtime_paths",
                return_value=(module_root, data_root, True),
            ), patch(
                "unified_manager.runtime_staging_root",
                return_value=expected_staging,
            ) as staging_root, patch(
                "unified_manager.build_mode_assignment_index",
                return_value=index_result,
            ) as build_index:
                result = run_manager(self.samples)
            report_dir = Path(result["report_directory"])
            self.assertEqual(report_dir.parent, data_root / "reports")
            self.assertTrue((data_root / "reports" / "scan_cache.sqlite3").is_file())
            staging_root.assert_called_once()
            build_index.assert_called_once_with(expected_staging)

    def test_quick_scan_reports_empty_import_folder_as_completed(self) -> None:
        self.wav.unlink()
        messages = []
        summary = quick_scan(
            self.samples, reports_root=self.reports, progress=messages.append,
        )
        self.assertEqual(summary["files_found"], 0)
        self.assertEqual(summary["directory_errors"], 0)
        self.assertEqual(summary["directories_scanned"], 1)
        self.assertTrue(any("БЫСТРОЕ СКАНИРОВАНИЕ ЗАВЕРШЕНО" in item for item in messages))

    def test_quick_scan_skips_unreadable_nested_folder_and_finishes(self) -> None:
        locked = self.incoming / "locked"
        locked.mkdir()
        make_test_wav(locked / "hidden.wav")
        healthy = self.incoming / "healthy.wav"
        make_test_wav(healthy)
        import os
        real_scandir = os.scandir

        def guarded_scandir(path):
            if Path(path) == locked:
                raise PermissionError("simulated nested folder access denied")
            return real_scandir(path)

        with patch("unified_manager.os.scandir", side_effect=guarded_scandir):
            summary = quick_scan(
                self.samples, reports_root=self.reports,
            )

        self.assertEqual(summary["files_found"], 1)
        self.assertEqual(summary["directory_errors"], 1)
        self.assertEqual(summary["directory_error_details"][0]["path"], str(locked))
        report_dir = Path(summary["report_directory"])
        errors = json.loads((report_dir / "quick_errors.json").read_text(encoding="utf-8"))
        self.assertEqual(errors["directory_errors"][0]["stage"], "QUICK_DIRECTORY_SCAN")
        inventory = (report_dir / "quick_inventory.csv").read_text(encoding="utf-8-sig")
        self.assertIn("healthy.wav", inventory)
        self.assertNotIn("hidden.wav", inventory)

    def test_quick_scan_fails_clearly_when_import_root_is_unreadable(self) -> None:
        import os

        real_scandir = os.scandir

        def guarded_scandir(path):
            if Path(path).resolve() == self.incoming.resolve():
                raise PermissionError("access denied by regression test")
            return real_scandir(path)

        with patch("unified_manager.os.scandir", side_effect=guarded_scandir):
            with self.assertRaisesRegex(OSError, "Не удаётся прочитать входную папку"):
                quick_scan(self.samples, reports_root=self.reports)

    def test_unreadable_file_is_recorded_and_scan_continues_to_next_file(self) -> None:
        broken = self.incoming / "locked.wav"
        shutil.copyfile(self.wav, broken)
        healthy = self.incoming / "healthy.wav"
        shutil.copyfile(self.wav, healthy)
        real_open = Path.open

        def guarded_open(path, *args, **kwargs):
            if path.name == "locked.wav" and args and args[0] == "rb":
                raise PermissionError("simulated locked source")
            return real_open(path, *args, **kwargs)

        with patch.object(Path, "open", guarded_open):
            summary = run_manager(self.samples, reports_root=self.reports)

        report_dir = Path(summary["report_directory"])
        inventory = (report_dir / "unified_inventory.csv").read_text(encoding="utf-8-sig")
        errors = json.loads((report_dir / "unified_errors.json").read_text(encoding="utf-8"))
        self.assertIn("locked.wav", inventory)
        self.assertIn("FILE_READ_ERROR", inventory)
        self.assertIn("healthy.wav", inventory)
        self.assertTrue(any(item.get("path") == "locked.wav" for item in errors))
        self.assertEqual(summary["files_scanned"], 3)
        self.assertTrue(broken.exists())
        self.assertTrue(healthy.exists())

    def test_deep_scan_path_key_does_not_resolve_offline_files(self) -> None:
        locked = self.incoming / "offline.wav"
        shutil.copyfile(self.wav, locked)
        healthy = self.incoming / "healthy.wav"
        shutil.copyfile(self.wav, healthy)
        real_resolve = Path.resolve

        def guarded_resolve(path, *args, **kwargs):
            if path.name == "offline.wav":
                raise OSError("simulated offline path resolution failure")
            return real_resolve(path, *args, **kwargs)

        with patch.object(Path, "resolve", guarded_resolve):
            summary = run_manager(self.samples, reports_root=self.reports)

        inventory = (
            Path(summary["report_directory"]) / "unified_inventory.csv"
        ).read_text(encoding="utf-8-sig")
        self.assertIn("offline.wav", inventory)
        self.assertIn("FILE_READ_ERROR", inventory)
        self.assertIn("healthy.wav", inventory)
        self.assertEqual(summary["files_scanned"], 3)

    def test_inventory_sfz_and_exact_duplicates(self) -> None:
        duplicate = self.incoming / "copy.wav"
        shutil.copyfile(self.wav, duplicate)
        (self.incoming / "instrument.sfz").write_text(
            '<region> sample="guitar.wav" lokey=60 hikey=72 lovel=1 hivel=127\n',
            encoding="utf-8",
        )

        summary = run_manager(self.samples, reports_root=self.reports)
        report_dir = Path(summary["report_directory"])
        self.assertEqual(summary["wav_files"], 2)
        self.assertEqual(summary["sfz_files"], 1)
        self.assertEqual(summary["exact_duplicate_groups"], 1)
        self.assertEqual(summary["sfz_sample_references"], 1)
        self.assertEqual(summary["sfz_missing_references"], 0)
        self.assertTrue((report_dir / "unified_inventory.csv").is_file())
        self.assertTrue((report_dir / "unified_sfz_references.csv").is_file())
        self.assertEqual(hashlib.sha256(self.wav.read_bytes()).hexdigest().upper(),
                         self.original_hash)
        self.assertFalse(summary["source_files_modified"])
        self.assertFalse(summary["automatic_factory_promotion"])

    def test_audio_analysis_is_optional_and_read_only(self) -> None:
        summary = run_manager(
            self.samples, analyze_audio=True, guitar_source_confirmed=False,
            reports_root=self.reports,
        )
        self.assertEqual(summary["audio_files_analyzed"], 1)
        self.assertGreaterEqual(summary["repeated_rhythm_pattern_candidates"], 0)
        self.assertEqual(summary["virtual_active_region_candidates"], 0)
        self.assertEqual(summary["asset_classifications_created"], 1)
        self.assertEqual(summary["classification_policy"], "CANDIDATE_ONLY_REQUIRES_HUMAN_REVIEW")
        classifications = json.loads((Path(summary["report_directory"]) / "unified_asset_classification.json").read_text(encoding="utf-8"))
        self.assertEqual(len(classifications), 1)
        self.assertEqual(classifications[0]["classification_status"], "CANDIDATE_REQUIRES_REVIEW")
        self.assertFalse(classifications[0]["automatic_factory_promotion"])
        self.assertEqual(hashlib.sha256(self.wav.read_bytes()).hexdigest().upper(),
                         self.original_hash)
        self.assertFalse(summary["source_files_moved_or_deleted"])

    def test_confirmed_guitar_analysis_adds_chord_candidates_to_sample_mode(self) -> None:
        chord_report = {
            "source_path": str(self.wav.resolve()),
            "source_sha256": self.original_hash,
            "chord_candidate_count": 1,
            "chord_candidates": [{
                "start_seconds": 0.2,
                "end_seconds": 0.7,
                "chord_name_candidate": "A5",
                "root_pitch_class": "A",
                "quality": "POWER5",
                "pitch_classes_candidate": ["A", "E"],
                "confidence": 0.91,
            }],
        }
        with patch("chord_analysis.analyze_chords", return_value=chord_report):
            summary = run_manager(
                self.samples, analyze_audio=True, guitar_source_confirmed=True,
                reports_root=self.reports,
            )
        report_dir = Path(summary["report_directory"])
        audio = json.loads((report_dir / "unified_audio_analysis.json").read_text(encoding="utf-8"))
        self.assertEqual(audio[0]["chord_analysis"]["chord_candidate_count"], 1)
        self.assertEqual(summary["chord_sample_candidates"], 1)
        modes = json.loads((report_dir / "mode_sorting_report.json").read_text(encoding="utf-8"))
        sample_mode = next(item for item in modes["modes"] if item["mode"] == "SAMPLE MODE")
        self.assertTrue(any(item["candidate_type"] == "POWER_CHORD_SAMPLE"
                            for item in sample_mode["candidates"]))
        self.assertEqual(hashlib.sha256(self.wav.read_bytes()).hexdigest().upper(),
                         self.original_hash)
        self.assertFalse(summary["source_files_modified"])

    def test_aiff_flac_ogg_are_inventoried_when_bundled_decoder_supports_them(self) -> None:
        try:
            import numpy as np
            import soundfile as sf
        except ImportError:
            self.skipTest("bundled soundfile decoder is unavailable in this test environment")
        samples = (0.25 * np.sin(2 * np.pi * 330 * np.arange(8000) / 8000)).astype("float32")
        written = []
        for ext, fmt, subtype in ((".aiff", "AIFF", "PCM_16"),
                                  (".flac", "FLAC", "PCM_16"),
                                  (".ogg", "OGG", "VORBIS")):
            path = self.incoming / ("tone" + ext)
            try:
                sf.write(str(path), samples, 8000, format=fmt, subtype=subtype)
            except Exception:
                self.skipTest(f"libsndfile cannot encode {fmt} in this environment")
            written.append(path)
        summary = run_manager(self.samples, reports_root=self.reports)
        self.assertEqual(summary["wav_files"], 4)  # includes WAV + 3 decoded audio formats
        inventory = (Path(summary["report_directory"]) / "unified_inventory.csv").read_text(encoding="utf-8-sig")
        for path in written:
            self.assertIn(path.name, inventory)
            self.assertIn("OK", inventory)

    def test_unsupported_files_are_visible_and_other_audit_is_generated(self) -> None:
        unsupported = self.incoming / "unhandled.bin"
        unsupported.write_bytes(b"not a supported library format")
        summary = run_manager(self.samples, reports_root=self.reports)
        report_dir = Path(summary["report_directory"])
        self.assertEqual(summary["unsupported_import_files"], 1)
        self.assertTrue((report_dir / "other_audit" / "other_audit.json").is_file())
        inventory = (report_dir / "unified_inventory.csv").read_text(encoding="utf-8-sig")
        self.assertIn("unhandled.bin", inventory)
        self.assertIn("OTHER_REVIEW_REQUIRED", inventory)
        self.assertTrue(unsupported.exists())

    def test_manager_virtual_sidecars_are_not_marked_as_unsupported_audio(self) -> None:
        virtual_dir = self.incoming / "VIRTUAL_CANDIDATES" / "RIFF_CANDIDATES"
        virtual_dir.mkdir(parents=True)
        sidecar = virtual_dir / "candidate.json"
        sidecar.write_text(
            '{"asset_kind":"VIRTUAL_AUDIO_RANGE","source_sha256":"test"}',
            encoding="utf-8",
        )
        summary = run_manager(self.samples, reports_root=self.reports)
        self.assertEqual(summary["manager_generated_metadata_files"], 1)
        self.assertEqual(summary["unsupported_import_files"], 0)
        inventory = (
            Path(summary["report_directory"]) / "unified_inventory.csv"
        ).read_text(encoding="utf-8-sig")
        self.assertIn("MANAGER_GENERATED_METADATA", inventory)
        self.assertNotIn("OTHER_REVIEW_REQUIRED", inventory)

    def test_virtual_index_requires_explicit_analysis_and_confirmation(self) -> None:
        with self.assertRaises(ValueError):
            run_manager(self.samples, write_virtual=True, reports_root=self.reports)


    def test_inventory_only_defaults_to_two_bounded_workers(self) -> None:
        summary = run_manager(self.samples, reports_root=self.reports)
        self.assertEqual(summary["workers"], 2)

    def test_heavy_audio_analysis_defaults_to_one_worker(self) -> None:
        summary = run_manager(
            self.samples, analyze_audio=True, reports_root=self.reports,
        )
        self.assertEqual(summary["workers"], 1)
    def test_second_scan_reuses_hash_cache_without_modifying_sources(self) -> None:
        first = run_manager(self.samples, reports_root=self.reports)
        second = run_manager(self.samples, reports_root=self.reports)
        report = Path(second["report_directory"]) / "unified_inventory.csv"
        inventory = report.read_text(encoding="utf-8-sig")
        self.assertIn("CACHE", inventory)
        self.assertEqual(second["files_scanned"], first["files_scanned"])
        self.assertTrue(self.wav.exists())
        self.assertEqual(hashlib.sha256(self.wav.read_bytes()).hexdigest().upper(),
                         self.original_hash)
        self.assertTrue(Path(second["hash_cache"]).is_file())


if __name__ == "__main__":
    unittest.main()
