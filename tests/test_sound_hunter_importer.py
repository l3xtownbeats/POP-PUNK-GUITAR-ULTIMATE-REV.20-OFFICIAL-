#!/usr/bin/env python3
"""Focused regression tests for Sound Hunter import safety and unlimited Samples growth."""
from pathlib import Path
import importlib.util
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "SoundHunter" / "sound_hunter_real_guitars.py"
SPEC = importlib.util.spec_from_file_location("ppgu_sound_hunter", MODULE_PATH)
sound_hunter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sound_hunter)


class SoundHunterRegressionTests(unittest.TestCase):
    def test_importer_has_no_artificial_samples_size_cap(self):
        result = subprocess.run([sys.executable, str(MODULE_PATH), "--help"], capture_output=True, text=True, check=True)
        self.assertNotIn("--max-library-gb", result.stdout)

    def test_release_assets_use_separate_directory(self):
        source = Path("/tmp/run/meta-open-sound-steel")
        target = sound_hunter.release_asset_target(
            source, "meta-open-sound-steel/release/steel/sample.wav"
        )
        self.assertEqual(
            target,
            source / "release_assets" / "release" / "steel" / "sample.wav",
        )
        self.assertNotEqual(target, source / "release" / "steel" / "sample.wav")

    def test_release_asset_path_rejects_traversal(self):
        with self.assertRaises(ValueError):
            sound_hunter.release_asset_target(
                Path("/tmp/run/source"), "../outside/sample.wav"
            )

    def test_safe_member_rejects_windows_path_traversal(self):
        self.assertFalse(sound_hunter.safe_member("folder\\\\..\\\\outside.wav"))
        self.assertFalse(sound_hunter.safe_member("C:\\\\outside.wav"))
        self.assertFalse(sound_hunter.safe_member("/absolute/outside.wav"))

    def test_safe_member_accepts_normal_repo_paths(self):
        self.assertTrue(sound_hunter.safe_member("root/Samples/guitar.wav"))

    def test_release_checksum_manifest_verifies_all_members(self):
        import hashlib, io, zipfile
        payload=b"real guitar sample"
        digest=hashlib.sha256(payload).hexdigest()
        buffer=io.BytesIO()
        with zipfile.ZipFile(buffer,"w") as z:
            z.writestr("bank/sample.wav",payload)
            z.writestr("bank/SHA256SUMS",f"{digest}  sample.wav\n")
        with zipfile.ZipFile(io.BytesIO(buffer.getvalue())) as z:
            count,members=sound_hunter.verify_zip_sha256_manifest(z)
        self.assertEqual(count,1)
        self.assertEqual(members,["bank/sample.wav"])

    def test_release_checksum_manifest_rejects_modified_member(self):
        import hashlib, io, zipfile
        buffer=io.BytesIO()
        with zipfile.ZipFile(buffer,"w") as z:
            z.writestr("sample.wav",b"changed")
            z.writestr("SHA256SUMS",f"{hashlib.sha256(b'original').hexdigest()}  sample.wav\n")
        with zipfile.ZipFile(io.BytesIO(buffer.getvalue())) as z:
            with self.assertRaises(RuntimeError):
                sound_hunter.verify_zip_sha256_manifest(z)

    def test_github_headers_uses_actions_token_when_available(self):
        from unittest import mock
        with mock.patch.dict("os.environ", {"GITHUB_TOKEN": "unit-test-token"}, clear=True):
            headers = sound_hunter.github_headers()
        self.assertEqual(headers["Authorization"], "Bearer unit-test-token")
        self.assertEqual(headers["Accept"], "application/vnd.github+json")

    def test_github_headers_works_without_token_for_public_sources(self):
        from unittest import mock
        with mock.patch.dict("os.environ", {}, clear=True):
            headers = sound_hunter.github_headers()
        self.assertNotIn("Authorization", headers)

    def test_fetch_repo_archive_pins_immutable_commit_and_hashes_payload(self):
        import hashlib
        import tempfile
        from unittest import mock
        commit_sha = "a" * 40
        payload = b"immutable source archive bytes"
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "snapshot.zip"
            with mock.patch.object(
                sound_hunter, "json_url",
                side_effect=[{"default_branch": "main"}, {"sha": commit_sha}]
            ) as api, mock.patch.object(
                sound_hunter, "request", return_value=payload
            ) as download:
                metadata = sound_hunter.fetch_repo_archive("owner/repo", destination)
            self.assertEqual(destination.read_bytes(), payload)
            self.assertEqual(metadata["resolved_commit_sha"], commit_sha)
            self.assertEqual(metadata["archive_sha256"], hashlib.sha256(payload).hexdigest())
            self.assertEqual(metadata["archive_bytes"], len(payload))
            download.assert_called_once_with(
                f"https://api.github.com/repos/owner/repo/zipball/{commit_sha}",
                timeout=180
            )

    def test_existing_hashes_fails_closed_when_audio_is_unreadable(self):
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "bank.wav"
            audio.write_bytes(b"audio")
            with mock.patch.object(sound_hunter, "sha256", side_effect=OSError("denied")):
                with self.assertRaises(RuntimeError):
                    sound_hunter.existing_hashes(Path(tmp))

    def test_existing_audio_bytes_counts_audio_only(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "guitar.wav").write_bytes(b"x" * 123)
            (root / "notes.txt").write_text("not audio")
            nested = root / "nested"
            nested.mkdir()
            (nested / "bank.sfz").write_bytes(b"x" * 17)
            self.assertEqual(sound_hunter.existing_audio_bytes(root), 123)


if __name__ == "__main__":
    unittest.main()
