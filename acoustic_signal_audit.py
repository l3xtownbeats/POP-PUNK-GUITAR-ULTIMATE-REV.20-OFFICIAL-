import wave
import math
import csv
import time
from pathlib import Path

ROOTS = {
    "NYLON": Path(r"F:\POP PUNK GUITAR ULTIMATE\Samples\FACTORY\Acoustic\Nylon"),
    "STEEL": Path(r"F:\POP PUNK GUITAR ULTIMATE\Samples\FACTORY\Acoustic\Steel")
}

DESKTOP = Path.home() / "Desktop"
CSV_PATH = DESKTOP / "ACOUSTIC_SIGNAL_AUDIT.csv"
SUMMARY_PATH = DESKTOP / "ACOUSTIC_SIGNAL_AUDIT_SUMMARY.txt"
ERROR_PATH = DESKTOP / "ACOUSTIC_SIGNAL_AUDIT_ERRORS.txt"

FULL_SCALE = 8388607
SILENCE_THRESHOLD = int(FULL_SCALE * 0.001)
CLIP_THRESHOLD = int(FULL_SCALE * 0.999)

FIELDS = [
    "library", "file", "duration_sec", "sample_rate",
    "channels", "bit_depth", "peak_dbfs", "rms_dbfs",
    "dc_offset", "near_clip_samples",
    "leading_below_threshold_sec", "trailing_below_threshold_sec"
]

def analyze(path, library):
    with wave.open(str(path), "rb") as w:
        channels = w.getnchannels()
        width = w.getsampwidth()
        rate = w.getframerate()
        frames_total = w.getnframes()

        if width != 3 or channels != 2 or rate != 48000:
            raise ValueError(
                f"Unexpected format: {width*8}-bit, "
                f"{channels} channels, {rate} Hz"
            )

        peak = 0
        total_sq = 0
        total_sum = 0
        count = 0
        near_clip = 0
        first_active = None
        last_active = None
        position = 0

        while True:
            data = w.readframes(8192)
            if not data:
                break

            view = memoryview(data)
            active_first = None
            active_last = None

            for i in range(0, len(view), 3):
                value = view[i] | (view[i+1] << 8) | (view[i+2] << 16)

                if value & 0x800000:
                    value -= 0x1000000

                absolute = abs(value)

                if absolute > peak:
                    peak = absolute

                if absolute >= CLIP_THRESHOLD:
                    near_clip += 1

                total_sq += value * value
                total_sum += value
                count += 1

                if absolute > SILENCE_THRESHOLD:
                    frame = position + i // 6

                    if active_first is None:
                        active_first = frame

                    active_last = frame

            if active_first is not None:
                if first_active is None:
                    first_active = active_first

                last_active = active_last

            position += len(data) // 6

        duration = frames_total / rate
        rms = math.sqrt(total_sq / count) if count else 0

        peak_db = (
            20 * math.log10(peak / FULL_SCALE)
            if peak else float("-inf")
        )

        rms_db = (
            20 * math.log10(rms / FULL_SCALE)
            if rms else float("-inf")
        )

        dc = total_sum / count / FULL_SCALE if count else 0

        leading = (
            first_active / rate
            if first_active is not None else duration
        )

        trailing = (
            (frames_total - 1 - last_active) / rate
            if last_active is not None else duration
        )

        return {
            "library": library,
            "file": path.name,
            "duration_sec": round(duration, 4),
            "sample_rate": rate,
            "channels": channels,
            "bit_depth": width * 8,
            "peak_dbfs": round(peak_db, 3),
            "rms_dbfs": round(rms_db, 3),
            "dc_offset": round(dc, 9),
            "near_clip_samples": near_clip,
            "leading_below_threshold_sec": round(leading, 4),
            "trailing_below_threshold_sec": round(trailing, 4)
        }

results = []
errors = []
start = time.time()

all_files = []

for library, folder in ROOTS.items():
    if not folder.is_dir():
        errors.append(f"FOLDER NOT FOUND: {folder}")
        continue

    for path in sorted(folder.glob("*.wav")):
        all_files.append((library, path))

total = len(all_files)
print("Starting local PCM analysis...")

for index, (library, path) in enumerate(all_files, 1):
    try:
        result = analyze(path, library)
        results.append(result)
    except Exception as exc:
        errors.append(f"{library} | {path.name} | {type(exc).name}: {exc}")

    if index % 25 == 0 or index == total:
        print(f"PROGRESS: {index}/{total} | errors: {len(errors)}")

with CSV_PATH.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(results)

summary = []
summary.append("ACOUSTIC SIGNAL AUDIT")
summary.append("=====================")
summary.append(f"Files found: {total}")
summary.append(f"Successfully analyzed: {len(results)}")
summary.append(f"Errors: {len(errors)}")
summary.append(f"Elapsed seconds: {round(time.time()-start, 2)}")

for library in ROOTS:
    subset = [r for r in results if r["library"] == library]

    summary.append("")
    summary.append(f"[{library}]")
    summary.append(f"Files analyzed: {len(subset)}")

    if subset:
        durations = [r["duration_sec"] for r in subset]
        rms_values = [r["rms_dbfs"] for r in subset]
        peak_values = [r["peak_dbfs"] for r in subset]

        summary.append(f"Duration min: {min(durations):.4f} sec")
        summary.append(f"Duration max: {max(durations):.4f} sec")
        summary.append(f"Duration average: {sum(durations)/len(durations):.4f} sec")
        summary.append(f"RMS average: {sum(rms_values)/len(rms_values):.3f} dBFS")
        summary.append(f"Peak average: {sum(peak_values)/len(peak_values):.3f} dBFS")
        summary.append(
            "Files with near-full-scale samples: "
            + str(sum(1 for r in subset if r["near_clip_samples"] > 0))
        )

SUMMARY_PATH.write_text("\n".join(summary), encoding="utf-8")

ERROR_PATH.write_text(
    "\n".join(errors) if errors else "No errors.",
    encoding="utf-8"
)

print("\n".join(summary))
print(f"\nCSV: {CSV_PATH}")
print(f"SUMMARY: {SUMMARY_PATH}")
print(f"ERRORS: {ERROR_PATH}")
