import os, wave, collections

root = r"F:\POP PUNK GUITAR ULTIMATE\Samples\FACTORY"

for kind in ("Nylon", "Steel"):
    folder = os.path.join(root, "Acoustic", kind)
    stats = collections.Counter()
    errors = []

    for name in os.listdir(folder):
        if not name.lower().endswith(".wav"):
            continue

        path = os.path.join(folder, name)

        try:
            with wave.open(path, "rb") as w:
                rate = w.getframerate()
                channels = w.getnchannels()
                bits = w.getsampwidth() * 8
                duration = w.getnframes() / rate

                stats[(rate, bits, channels)] += 1

        except Exception as e:
            errors.append((name, str(e)))

    print("\n==========", kind, "==========")
    print("Технические форматы:")

    for fmt, count in sorted(stats.items()):
        print(fmt, ":", count, "файлов")

    print("Ошибок чтения:", len(errors))

    for name, error in errors[:10]:
        print(name, ":", error)
