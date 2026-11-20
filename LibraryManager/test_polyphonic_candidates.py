import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from polyphonic_candidates import analyze_polyphonic_candidates


def write_chord(path: Path, frequencies, seconds=0.7, rate=11025):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        frames = []
        for index in range(int(rate * seconds)):
            value = sum(math.sin(2 * math.pi * hz * index / rate)
                        for hz in frequencies)
            value /= max(1, len(frequencies))
            frames.append(struct.pack("<h", int(10000 * value)))
        wav.writeframes(b"".join(frames))


class PolyphonicCandidateTests(unittest.TestCase):
    def test_detects_two_simultaneous_notes_without_naming_a_chord(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dyad.wav"
            write_chord(path, [440.0, 523.25])
            result = analyze_polyphonic_candidates(path)
            pitches = {event["midi_note_candidate"] for event in result["pitch_events"]}
            self.assertIn(69, pitches)
            self.assertIn(72, pitches)
            self.assertTrue(all(event["review_status"] == "NEEDS_MUSICAL_REVIEW"
                                for event in result["pitch_events"]))
            self.assertIn("limitations", result)

    def test_detects_multiple_notes_in_a_synthetic_triad(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "triad.wav"
            write_chord(path, [261.63, 329.63, 392.00])
            result = analyze_polyphonic_candidates(path)
            pitches = {event["midi_note_candidate"] for event in result["pitch_events"]}
            self.assertTrue({60, 64, 67}.issubset(pitches), pitches)

    def test_silence_produces_no_pitch_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "silence.wav"
            write_chord(path, [])
            result = analyze_polyphonic_candidates(path)
            self.assertEqual(result["pitch_events"], [])

    def test_rejects_invalid_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tone.wav"
            write_chord(path, [440.0])
            with self.assertRaises(ValueError):
                analyze_polyphonic_candidates(path, hop_ms=120, frame_ms=100)


if __name__ == "__main__":
    unittest.main()
