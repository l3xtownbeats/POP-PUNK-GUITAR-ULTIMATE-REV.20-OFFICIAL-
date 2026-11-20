import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from pitch_events import analyze_pitch_events


def write_tone(path: Path, sections, rate=16000):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        samples = []
        for frequency, seconds in sections:
            count = int(rate * seconds)
            for i in range(count):
                value = 0 if frequency is None else int(
                    12000 * math.sin(2 * math.pi * frequency * i / rate))
                samples.append(struct.pack("<h", value))
        wav.writeframes(b"".join(samples))


class PitchEventTests(unittest.TestCase):
    def test_detects_stable_monophonic_tone(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tone.wav"
            write_tone(path, [(440.0, 0.8)])
            result = analyze_pitch_events(path)
            self.assertGreaterEqual(result["pitch_event_candidate_count"], 1)
            self.assertTrue(any(abs(e["midi_note_candidate"] - 69) <= 1
                                for e in result["pitch_events"]))
            self.assertTrue(all(e["review_status"] == "NEEDS_MUSICAL_REVIEW"
                                for e in result["pitch_events"]))

    def test_tracks_pitch_change_as_separate_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "two_notes.wav"
            write_tone(path, [(440.0, 0.5), (523.25, 0.5)])
            result = analyze_pitch_events(path)
            pitches = {e["midi_note_candidate"] for e in result["pitch_events"]}
            self.assertIn(69, pitches)
            self.assertIn(72, pitches)

    def test_silence_does_not_invent_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "silence.wav"
            write_tone(path, [(None, 0.6)])
            result = analyze_pitch_events(path)
            self.assertEqual(result["pitch_events"], [])

    def test_rejects_invalid_parameters(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tone.wav"
            write_tone(path, [(440.0, 0.3)])
            with self.assertRaises(ValueError):
                analyze_pitch_events(path, frame_ms=10)


if __name__ == "__main__":
    unittest.main()
