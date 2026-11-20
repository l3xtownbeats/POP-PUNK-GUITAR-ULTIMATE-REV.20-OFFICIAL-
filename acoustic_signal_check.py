import wave
import math
from pathlib import Path

ROOTS = {
    "NYLON": Path(r"F:\POP PUNK GUITAR ULTIMATE\Samples\FACTORY\Acoustic\Nylon"),
    "STEEL": Path(r"F:\POP PUNK GUITAR ULTIMATE\Samples\FACTORY\Acoustic\Steel")
}

def analyze(path):
    with wave.open(str(path), "rb") as w:
        channels = w.getnchannels()
        width = w.getsampwidth()
        rate = w.getframerate()
        frames_total = w.getnframes()

        if width != 3 or channels != 2:
            raise ValueError(
                f"Expected 24-bit stereo; got {width*8}-bit, {channels} channels"
            )

        peak = 0
        total_sq = 0
        total_sum = 0
        count = 0
        first_active = None
        last_active = None
        threshold = int(8388607 * 0.001)

        position = 0

        while True:
            data = w.readframes(8192)
            if not data:
                break

            view = memoryview(data)
            active_in_chunk = []

            for i in range(0, len(view), 3):
                value = view[i] | (view[i+1] << 8) | (view[i+2] << 16)
                if value & 0x800000:
                    value -= 0x1000000

                absolute = abs(value)
                if absolute > peak:
                    peak = absolute

                total_sq += value * value
                total_sum += value
                count += 1

                frame = (i // 6) + position
                if absolute > threshold:
                    active_in_chunk.append(frame)

            if active_in_chunk:
                if first_active is None:
                    first_active = active_in_chunk[0]
                last_active = active_in_chunk[-1]

            position += len(data) // 6

        duration = frames_total / rate
        rms = math.sqrt(total_sq / count) if count else 0
        peak_db = 20 * math.log10(peak / 8388607) if peak else float("-inf")
        rms_db = 20 * math.log10(rms / 8388607) if rms else float("-inf")
        dc = total_sum / count / 8388607 if count else 0

        leading = first_active / rate if first_active is not None else duration
        trailing = (
            (frames_total - 1 - last_active) / rate
            if last_active is not None else duration
        )

        return {
            "file": path.name,
            "duration_sec": round(duration, 3),
            "sample_rate": rate,
            "channels": channels,
            "bit_depth": width * 8,
            "peak_dbfs": round(peak_db, 2),
            "rms_dbfs": round(rms_db, 2),
            "dc_offset": round(dc, 7),
            "leading_silence_sec": round(leading, 3),
            "trailing_silence_sec": round(trailing, 3)
        }

for name, folder in ROOTS.items():
    files = sorted(folder.glob("*.wav"))
    print(f"\n--- {name} ---")

    if not files:
        print("ERROR: WAV files not found")
        continue

    try:
        result = analyze(files[0])
        for key, value in result.items():
            print(f"{key}: {value}")
        print("RESULT: READ OK")
    except Exception as e:
        print(f"ERROR: {type(e).name}: {e}")
