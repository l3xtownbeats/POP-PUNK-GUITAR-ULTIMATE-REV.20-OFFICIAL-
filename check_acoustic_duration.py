import os, wave, statistics

root = r"F:\POP PUNK GUITAR ULTIMATE\Samples\FACTORY"

for kind in ("Nylon", "Steel"):
    folder = os.path.join(root, "Acoustic", kind)
    durations = []
    total_bytes = 0

    for name in os.listdir(folder):
        if name.lower().endswith(".wav"):
            path = os.path.join(folder, name)

            with wave.open(path, "rb") as w:
                durations.append(w.getnframes() / w.getframerate())

            total_bytes += os.path.getsize(path)

    print("\n==========", kind, "==========")
    print("Файлов:", len(durations))
    print("Минимальная длительность:", round(min(durations), 3), "сек")
    print("Максимальная длительность:", round(max(durations), 3), "сек")
    print("Средняя длительность:", round(statistics.mean(durations), 3), "сек")
    print("Общий размер:", round(total_bytes / 1024**2, 2), "MiB")
