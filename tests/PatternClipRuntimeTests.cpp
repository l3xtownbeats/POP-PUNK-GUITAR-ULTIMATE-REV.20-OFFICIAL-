#include "PatternClipRuntime.h"

#include <array>
#include <cmath>
#include <iostream>

int main()
{
    using namespace ppgu::performance;
    PatternClipSnapshot snapshot;
    snapshot.clips.resize(2);
    snapshot.clips[0].sampleRate = 48000.0;
    snapshot.clips[0].samples.assign(4096, 0.5f);
    snapshot.clips[1].sampleRate = 48000.0;
    snapshot.clips[1].samples.assign(4096, 0.25f);
    snapshot.mappings.push_back({60, 1, 127, 0, 0, 7, 128, 1.0f, 0.0f});
    snapshot.mappings.push_back({61, 1, 127, 1, 0, 7, 128, 1.0f, 0.0f});

    if (!PatternClipRuntime::validateSnapshot(snapshot))
    {
        std::cerr << "Valid bounded snapshot was rejected.\n";
        return 1;
    }
    auto invalidSnapshot = snapshot;
    invalidSnapshot.mappings.push_back(invalidSnapshot.mappings.front());
    if (PatternClipRuntime::validateSnapshot(invalidSnapshot))
    {
        std::cerr << "Overlapping velocity mapping was accepted.\n";
        return 1;
    }

    PatternClipRuntime rejectedRuntime;
    rejectedRuntime.attachSnapshot(&invalidSnapshot);
    if (rejectedRuntime.noteOn(60, 100, 1))
    {
        std::cerr << "Invalid snapshot was published to the runtime.\n";
        return 1;
    }

    PatternClipRuntime runtime;
    runtime.prepare(48000.0);
    runtime.attachSnapshot(&snapshot);

    if (!runtime.noteOn(60, 100, 1) || runtime.activeVoiceCount() != 1)
    {
        std::cerr << "Mapped trigger did not start exactly one voice.\n";
        return 1;
    }

    std::array<float, 256> left {}, right {};
    runtime.render(left.data(), right.data(), static_cast<int>(left.size()));
    if (!(left[20] > 0.49f && right[20] > 0.49f))
    {
        std::cerr << "Clip PCM was not rendered to stereo output.\n";
        return 1;
    }

    // A note-off on another MIDI channel must not release this voice.
    runtime.noteOff(60, 2);
    if (runtime.activeVoiceCount() != 1)
    {
        std::cerr << "Unmatched channel note-off changed the active voice.\n";
        return 1;
    }

    // A second mapping in the same choke group fades the first voice.
    if (!runtime.noteOn(61, 100, 1) || runtime.activeVoiceCount() != 2)
    {
        std::cerr << "Second mapped clip did not start.\n";
        return 1;
    }
    std::array<float, 128> fadeLeft {}, fadeRight {};
    runtime.render(fadeLeft.data(), fadeRight.data(), static_cast<int>(fadeLeft.size()));
    if (runtime.activeVoiceCount() != 1)
    {
        std::cerr << "Choke fade did not retire the previous voice.\n";
        return 1;
    }

    runtime.noteOff(61, 1);
    std::array<float, 256> releaseLeft {}, releaseRight {};
    runtime.render(releaseLeft.data(), releaseRight.data(), static_cast<int>(releaseLeft.size()));
    if (runtime.activeVoiceCount() != 0)
    {
        std::cerr << "Matching note-off did not complete the release.\n";
        return 1;
    }

    if (runtime.noteOn(62, 100, 1))
    {
        std::cerr << "Unmapped trigger unexpectedly started a clip.\n";
        return 1;
    }

    runtime.detachSnapshot();
    std::cout << "PATTERN clip runtime tests passed.\n";
    return 0;
}
