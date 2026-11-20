import tempfile
import unittest
from pathlib import Path

import numpy as np
import soundfile as sf

from audio_range_io import audio_source_info, write_pcm_wav_range


class AudioRangeIOTests(unittest.TestCase):
    def test_streams_large_range_to_verified_pcm24_wav(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "long_source.wav"
            destination = root / "range.wav"
            rate = 8000
            frames = 150_000
            data = np.column_stack((
                0.25 * np.sin(2 * np.pi * 220 * np.arange(frames) / rate),
                0.20 * np.sin(2 * np.pi * 330 * np.arange(frames) / rate),
            )).astype("float32")
            sf.write(str(source), data, rate, subtype="PCM_16")
            start, end = 17_123, 143_777

            result = write_pcm_wav_range(source, start, end, destination,
                                         expected_rate=rate)

            info = audio_source_info(destination)
            self.assertEqual(info.frames, end - start)
            self.assertEqual(info.framerate, rate)
            self.assertEqual(info.nchannels, 2)
            self.assertEqual(info.source_format, "WAV")
            self.assertEqual(info.source_subtype, "PCM_24")
            self.assertEqual(result["frame_count"], end - start)
            self.assertEqual(result["sample_width_bytes"], 3)
            actual, actual_rate = sf.read(str(destination), dtype="float32",
                                          always_2d=True)
            self.assertEqual(actual_rate, rate)
            np.testing.assert_allclose(actual, data[start:end], atol=2 / 32768)

    def test_refuses_overwrite_and_invalid_ranges(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.wav"
            destination = root / "existing.wav"
            sf.write(str(source), np.zeros(1000, dtype="float32"), 8000,
                     subtype="PCM_16")
            destination.write_bytes(b"keep")
            with self.assertRaises(FileExistsError):
                write_pcm_wav_range(source, 0, 100, destination)
            self.assertEqual(destination.read_bytes(), b"keep")
            with self.assertRaises(ValueError):
                write_pcm_wav_range(source, -1, 100, root / "invalid.wav")


if __name__ == "__main__":
    unittest.main()
