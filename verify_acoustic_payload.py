import os, wave

root = r"F:\POP PUNK GUITAR ULTIMATE\Samples\FACTORY"

for kind in ("Nylon", "Steel"):
    folder = os.path.join(root, "Acoustic", kind)

    checked = 0
    errors = []

    for name in os.listdir(folder):
        if not name.lower().endswith(".wav"):
            continue

        path = os.path.join(folder, name)

        try:
            with wave.open(path, "rb") as w:
                expected = w.getnframes()
                actual = 0

                while True:
                    chunk = w.readframes(4096)
                    if not chunk:
                        break

                    actual += len(chunk) // (
                        w.getnchannels() * w.getsampwidth()
                    )

                if actual != expected:
                    errors.append((name, expected, actual))

            checked += 1

        except Exception as e:
            errors.append((name, str(e)))

    print("\n==========", kind, "==========")
    print("Полностью прочитано:", checked)
    print("Ошибок:", len(errors))

    for item in errors[:20]:
        print(item)
