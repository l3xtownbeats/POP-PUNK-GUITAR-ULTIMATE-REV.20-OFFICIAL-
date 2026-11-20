import math, tempfile, unittest, wave
from pathlib import Path
from audio_analysis import analyse_wav, read_mono_pcm

class AudioAnalysisTests(unittest.TestCase):
    def make_tone(self, path, hz=440, seconds=1.0, rate=8000):
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
            data=bytearray()
            for i in range(int(seconds*rate)):
                value=int(12000*math.sin(2*math.pi*hz*i/rate))
                data.extend(value.to_bytes(2,"little",signed=True))
            w.writeframes(data)

    def test_detects_tone_pitch_candidate_and_duration(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"a440.wav"; self.make_tone(p); r=analyse_wav(p)
            self.assertEqual(r["duration_seconds"],1.0)
            self.assertEqual(r["analysis_sample_cap"],90_000)  # Low-load discovery default for 2-core / 8 GB PCs
            self.assertEqual(r["decoder_block_frames"],65_536)
            self.assertIsNotNone(r["dominant_pitch_candidate"])
            self.assertEqual(r["dominant_pitch_candidate"]["midi_note"],69)

    def test_silence_has_no_pitch(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"silence.wav"
            with wave.open(str(p),"wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000); w.writeframes(bytes(16000))
            r=analyse_wav(p); self.assertIsNone(r["dominant_pitch_candidate"])
            self.assertEqual(r["level"]["peak"],0.0)

    def test_non_audio_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.txt"; p.write_text("not audio")
            with self.assertRaises(Exception): analyse_wav(p)

    def test_soundfile_formats_roundtrip_when_backend_available(self):
        try:
            import soundfile as sf
            import numpy as np
        except ImportError:
            self.skipTest("optional soundfile backend is not installed")
        with tempfile.TemporaryDirectory() as td:
            samples=np.sin(2*np.pi*440*np.arange(8000)/8000).astype("float32")*.4
            for ext,fmt,subtype in [(".aiff","AIFF","PCM_16"),(".flac","FLAC","PCM_16"),(".ogg","OGG","VORBIS")]:
                path=Path(td)/("tone"+ext); sf.write(str(path),samples,8000,format=fmt,subtype=subtype)
                result=analyse_wav(path)
                self.assertAlmostEqual(result["duration_seconds"],1.0,places=3)
                self.assertEqual(result["decoder_backend"],"libsndfile")
                self.assertIsNotNone(result["dominant_pitch_candidate"])

if __name__=="__main__": unittest.main()
