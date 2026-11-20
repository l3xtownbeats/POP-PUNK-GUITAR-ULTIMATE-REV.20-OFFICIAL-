import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from asset_classifier import classify_wav

def write_signal(path, seconds, signal_fn, rate=11025):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        data = []
        for i in range(int(seconds*rate)):
            value = max(-1.0, min(1.0, signal_fn(i/rate)))
            data.append(struct.pack("<h", int(value*15000)))
        wav.writeframes(b"".join(data))

def pulse_train(t, period=0.4, width=0.10):
    phase = t % period
    if phase >= width:
        return 0.0
    return math.sin(2*math.pi*220*t) * (1.0-phase/width)

class AssetClassifierTests(unittest.TestCase):
    def test_short_decaying_tone_is_one_shot_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"hit.wav"
            write_signal(p, 0.65, lambda t: math.sin(2*math.pi*220*t)*math.exp(-t*9))
            result=classify_wav(p)
            self.assertEqual(result["asset_kind_candidate"], "ONE_SHOT")
            self.assertEqual(result["sample_subtype_candidate"], "NOTE_ONE_SHOT")
            self.assertEqual(result["review_status"], "NEEDS_MUSICAL_REVIEW")

    def test_long_regular_pulses_are_rhythmic_sample_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"rhythm.wav"
            write_signal(p, 4.0, pulse_train)
            result=classify_wav(p)
            self.assertEqual(result["asset_kind_candidate"], "SAMPLE")
            self.assertEqual(result["sample_subtype_candidate"], "RHYTHM_PATTERN")
            self.assertEqual(result["content_type_candidate"], "REPEATING_GUITAR_RHYTHM")
            self.assertGreaterEqual(result["features"]["onset_count"], 4)


    def test_long_guitar_melody_is_sample_and_proposes_note_fragments(self):
        pitches = [220.0, 277.18, 329.63, 392.0]
        def melody(t):
            slot = int(t / 0.8)
            if slot >= len(pitches):
                return 0.0
            local = t - slot * 0.8
            if local >= 0.62:
                return 0.0
            return 0.55 * math.sin(2 * math.pi * pitches[slot] * local)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"guitar_melody.wav"
            write_signal(p, 3.4, melody)
            result=classify_wav(p)
            self.assertEqual(result["asset_kind_candidate"], "SAMPLE")
            self.assertIn(result["sample_subtype_candidate"], ("RHYTHMIC_MELODY", "MELODIC"))
            self.assertEqual(result["content_type_candidate"], "GUITAR_MELODY_WITH_RHYTHMIC_PULSE" if result["sample_subtype_candidate"] == "RHYTHMIC_MELODY" else "GUITAR_MELODY")
            self.assertGreater(result["fragment_count"], 0)
            self.assertEqual(result["fragment_policy"], "METADATA_CUT_PROPOSALS_ONLY")

    def test_long_sustain_is_sample_but_not_loop(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"sustain.wav"
            write_signal(p, 3.0, lambda t: 0.45*math.sin(2*math.pi*196*t))
            result=classify_wav(p)
            self.assertEqual(result["asset_kind_candidate"], "SAMPLE")
            self.assertFalse(result["loop_candidate"])

    def test_silence_is_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"silence.wav"
            write_signal(p, 2.0, lambda t: 0.0)
            self.assertEqual(classify_wav(p)["asset_kind_candidate"], "UNKNOWN")

    def test_source_is_not_changed_and_license_not_assumed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"source.wav"
            write_signal(p, 0.5, lambda t: math.sin(2*math.pi*330*t)*math.exp(-t*8))
            before=p.read_bytes()
            result=classify_wav(p)
            self.assertEqual(p.read_bytes(), before)
            self.assertEqual(result["license_status"], "UNREVIEWED")
            self.assertFalse(result["source_modified"])

if __name__ == "__main__":
    unittest.main()
