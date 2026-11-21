#include "Performance/AutoChordDisplayState.h"

#include <atomic>
#include <iostream>
#include <thread>

using ppgu::performance::AutoChordDisplayState;
using ppgu::performance::AutoChordDisplayStateStore;

int main()
{
    AutoChordDisplayStateStore store;
    AutoChordDisplayState empty;
    if (!store.read(empty) || empty.noteCount != 0 || empty.active)
    {
        std::cerr << "Initial AutoChord display state was not empty.\n";
        return 1;
    }

    AutoChordDisplayState first;
    first.inputNotes = {{ 60, -1, -1, -1, -1, -1 }};
    first.generatedNotes = {{ 60, 64, 67, -1, -1, -1 }};
    first.inputNoteCount = 1;
    first.noteCount = 3;
    first.scaleRoot = 0;
    first.scaleMode = 1;
    first.playMode = 1;
    first.enabled = true;
    first.active = true;
    first.autoChordApplied = true;
    first.generation = 42;
    if (!store.publish(first))
        return 2;

    AutoChordDisplayState copied;
    if (!store.read(copied)
        || copied.inputNoteCount != 1 || copied.inputNotes[0] != 60
        || copied.noteCount != 3 || copied.generatedNotes[1] != 64
        || copied.generatedNotes[2] != 67 || !copied.enabled
        || !copied.active || !copied.autoChordApplied
        || copied.playMode != 1 || copied.scaleRoot != 0 || copied.scaleMode != 1)
    {
        std::cerr << "Published AutoChord display state was not copied correctly.\n";
        return 3;
    }

    // Concurrent writer/readers stress the two-slot handoff. Each complete
    // snapshot carries correlated values; a torn or mixed copy is rejected.
    std::atomic<bool> finished { false };
    std::atomic<bool> invalidSnapshot { false };
    std::thread writer([&]
    {
        for (int value = 1; value <= 100000; ++value)
        {
            AutoChordDisplayState state;
            state.inputNotes[0] = value % 128;
            state.generatedNotes[0] = value % 128;
            state.generatedNotes[1] = (value + 1) % 128;
            state.generatedNotes[2] = (value + 2) % 128;
            state.inputNoteCount = 1;
            state.noteCount = 3;
            state.generation = static_cast<std::uint32_t>(value);
            while (!store.publish(state))
                std::this_thread::yield();
        }
        finished.store(true, std::memory_order_release);
    });

    std::thread readerA([&]
    {
        AutoChordDisplayState state;
        while (!finished.load(std::memory_order_acquire))
        {
            if (!store.read(state))
                continue;
            if (state.noteCount == 3
                && (state.generatedNotes[1] != (state.generatedNotes[0] + 1) % 128
                    || state.generatedNotes[2] != (state.generatedNotes[0] + 2) % 128))
                invalidSnapshot.store(true, std::memory_order_relaxed);
        }
    });
    std::thread readerB([&]
    {
        AutoChordDisplayState state;
        while (!finished.load(std::memory_order_acquire))
            (void) store.read(state);
    });

    writer.join();
    readerA.join();
    readerB.join();
    if (invalidSnapshot.load(std::memory_order_relaxed))
    {
        std::cerr << "A concurrent reader observed a torn AutoChord snapshot.\n";
        return 4;
    }

    std::cout << "AutoChord display state contracts passed.\n";
    return 0;
}
