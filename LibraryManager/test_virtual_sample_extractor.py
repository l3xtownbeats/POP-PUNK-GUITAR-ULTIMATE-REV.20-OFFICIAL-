import hashlib
import json
import math
import struct
import tempfile
import shutil
import unittest
import wave
from pathlib import Path

from virtual_sample_extractor import (analyze_long_wav, analyze_pattern_ranges,
                                      write_virtual_index, extract_virtual_ranges, STAGING_BASE)


def write_test_wav(path: Path, rate: int = 11025) -> None:
    samples = []
    # Silence, a sustained guitar-like tone, short gap, second tone, silence.
    for index in range(rate * 3):
        seconds = index / rate
        if 0.30 <= seconds < 1.00:
            value = 0.35 * math.sin(2 * math.pi * 110 * seconds)
        elif 1.35 <= seconds < 2.00:
            value = 0.30 * math.sin(2 * math.pi * 146.83 * seconds)
        else:
            value = 0.0
        samples.append(struct.pack("<h", int(value * 32767)))
    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(rate)
        writer.writeframes(b"".join(samples))


class VirtualSampleExtractorTests(unittest.TestCase):
    def test_requires_guitar_filter_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "riff.wav"
            write_test_wav(source)
            with self.assertRaises(ValueError):
                analyze_long_wav(source)

    def test_finds_virtual_regions_without_modifying_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "riff.wav"
            write_test_wav(source)
            before = hashlib.sha256(source.read_bytes()).hexdigest().upper()
            report = analyze_long_wav(source, guitar_source_confirmed=True)
            after = hashlib.sha256(source.read_bytes()).hexdigest().upper()
            self.assertEqual(before, after)
            self.assertFalse(report["audio_copied"])
            self.assertFalse(report["audio_modified"])
            self.assertGreaterEqual(report["candidate_count"], 2)
            for item in report["candidates"]:
                self.assertLess(item["source_start_sample"], item["source_end_sample"])
                self.assertEqual(len(item["acoustic_fingerprint"]), 64)
                self.assertEqual(item["review_status"], "NEEDS_MUSICAL_REVIEW")

    def test_pattern_mode_keeps_only_repeated_rhythm_occurrences(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "take.wav"
            write_test_wav(source)
            report = {
                "pattern_analysis": {
                    "onset_count": 8,
                    "rhythmic_regularity_candidate": 0.91,
                    "patterns": [{
                        "candidate_type": "REPEATED_RHYTHM_MOTIF",
                        "pattern_candidate_id": "PATTERN-TEST",
                        "pattern_signature_units": [8, 8, 8],
                        "occurrence_count": 2,
                        "occurrences": [
                            {"start_seconds": 0.50, "end_seconds": 1.20,
                             "start_onset_index": 0, "end_onset_index_exclusive": 4},
                            {"start_seconds": 1.50, "end_seconds": 2.20,
                             "start_onset_index": 4, "end_onset_index_exclusive": 8},
                        ],
                    }],
                },
            }
            result = analyze_pattern_ranges(
                source, report, guitar_source_confirmed=True,
                source_sha256=hashlib.sha256(source.read_bytes()).hexdigest().upper(),
            )
            self.assertEqual(result["candidate_count"], 2)
            self.assertEqual(result["extraction_policy"],
                             "REPEATED_RHYTHM_ONLY_NO_BROAD_RMS_ACTIVE_REGIONS")
            for candidate in result["candidates"]:
                self.assertEqual(candidate["candidate_type"],
                                 "REPEATED_GUITAR_RHYTHM_PATTERN")
                self.assertEqual(candidate["review_status"], "NEEDS_MUSICAL_REVIEW")
                self.assertGreaterEqual(candidate["onset_count_candidate"], 4)
                self.assertLess(candidate["duration_seconds"], 1.0)

    def test_pattern_mode_rejects_irregular_or_unrepeated_material(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "take.wav"
            write_test_wav(source)
            report = {"pattern_analysis": {
                "onset_count": 8, "rhythmic_regularity_candidate": 0.40,
                "patterns": [{
                    "candidate_type": "REPEATED_RHYTHM_MOTIF",
                    "occurrence_count": 2,
                    "occurrences": [{"start_seconds": 0.2, "end_seconds": 1.2,
                                     "start_onset_index": 0,
                                     "end_onset_index_exclusive": 5}],
                }],
            }}
            result = analyze_pattern_ranges(source, report,
                                             guitar_source_confirmed=True,
                                             source_sha256="A" * 64)
            self.assertEqual(result["candidate_count"], 0)

    def test_writes_sidecars_only_to_import_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "riff.wav"
            write_test_wav(source)
            import_root = root / "Import Sample Guitar"
            import_root.mkdir()
            report = analyze_long_wav(source, guitar_source_confirmed=True)
            files = write_virtual_index(report, import_root)
            self.assertGreaterEqual(len(files), 2)
            self.assertTrue(all(path.parent.name == "RIFF_CANDIDATES" for path in files))
            record = json.loads(files[0].read_text(encoding="utf-8"))
            self.assertEqual(record["asset_kind"], "VIRTUAL_AUDIO_RANGE")
            self.assertEqual(record["source_sha256"], report["source_sha256"])
            # Re-running the same scan reuses only sidecars with matching
            # source hash, exact offsets and acoustic fingerprint.
            reused = write_virtual_index(report, import_root)
            self.assertEqual(reused, files)


    def test_extracts_long_recording_regions_to_staging_wav_with_exact_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "long_riff.wav"
            write_test_wav(source)
            before = hashlib.sha256(source.read_bytes()).hexdigest().upper()
            report = analyze_long_wav(source, guitar_source_confirmed=True)
            stage = STAGING_BASE / ("test-long-regions-" + next(tempfile._get_candidate_names()))
            try:
                records = extract_virtual_ranges(report, stage, max_clips=10)
                self.assertGreaterEqual(len(records), 2)
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest().upper(), before)
                for record in records:
                    clip = Path(record["derived_path"])
                    manifest = stage / "manifests" / (clip.stem + ".json")
                    self.assertTrue(clip.is_file())
                    self.assertTrue(manifest.is_file())
                    self.assertEqual(record["source_sha256"], before)
                    self.assertEqual(record["review_status"], "NEEDS_MUSICAL_REVIEW")
                    self.assertEqual(record["license_status"], "UNREVIEWED")
                    self.assertEqual(record["kind"], "long_recording_region_candidate")
                    with wave.open(str(clip), "rb") as audio:
                        self.assertEqual(audio.getnframes(), record["frame_count"])
                        self.assertEqual(audio.getframerate(), 11025)
                        self.assertEqual(audio.getnchannels(), 1)
                        self.assertEqual(audio.getsampwidth(), 3)
                self.assertTrue(all(record.get("reused_existing") is False for record in records))
                reused = extract_virtual_ranges(report, stage, max_clips=10)
                self.assertEqual(len(reused), len(records))
                self.assertTrue(all(record.get("reused_existing") is True for record in reused))
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest().upper(), before)
            finally:
                shutil.rmtree(stage, ignore_errors=True)

    def test_long_region_extraction_refuses_output_outside_staging(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "long_riff.wav"
            write_test_wav(source)
            report = analyze_long_wav(source, guitar_source_confirmed=True)
            with self.assertRaises(ValueError):
                extract_virtual_ranges(report, Path(tmp) / "outside")

    def test_refuses_wrong_destination_and_changed_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "riff.wav"
            write_test_wav(source)
            report = analyze_long_wav(source, guitar_source_confirmed=True)
            with self.assertRaises(ValueError):
                write_virtual_index(report, root / "FACTORY")
            with source.open("ab") as stream:
                stream.write(b"changed")
            import_root = root / "Import Sample Guitar"
            import_root.mkdir()
            with self.assertRaises(RuntimeError):
                write_virtual_index(report, import_root)


if __name__ == "__main__":
    unittest.main()
