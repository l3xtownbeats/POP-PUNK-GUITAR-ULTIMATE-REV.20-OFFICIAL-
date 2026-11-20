import math, tempfile, unittest, wave
from pathlib import Path
from audio_analysis import analyse_wav, read_mono_pcm

class AudioAnalysisTests(unittest.TestCase):
    def make_tone(self, path, hz=440, seconds=1.0, rate=8000):
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
            data = bytearray()
            for i in range(int(seconds*rate)):
                value = int(12000*math.sin(2*math.pi*hz*i/rate))
                data.extend(value.to_bytes(2, "little", signed=True))
            w.writeframes(data)

    def test_detects_tone_pitch_candidate_and_duration(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"a440.wav"; self.make_tone(p)
            r=analyse_wav(p)
            self.assertEqual(r["duration_seconds"], 1.0)
            self.assertIsNotNone(r["dominant_pitch_candidate"])
            self.assertEqual(r["dominant_pitch_candidate"]["midi_note"], 69)

    def test_silence_has_no_pitch(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"silence.wav"
            with wave.open(str(p),"wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
                w.writeframes(bytes(8000*2))
            r=analyse_wav(p)
            self.assertIsNone(r["dominant_pitch_candidate"])
            self.assertEqual(r["level"]["peak"], 0.0)

    def test_rejects_compressed_or_non_wav_input(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.txt"; p.write_text("not audio")
            with self.assertRaises(Exception):
                analyse_wav(p)

if __name__ == "__main__":
    unittest.main()
