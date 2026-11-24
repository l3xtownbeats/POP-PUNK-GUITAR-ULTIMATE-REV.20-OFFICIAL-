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

    // Hot publication must leave active voices attached to the old,
    // still-owned immutable snapshot while new triggers use the replacement.
    PatternClipSnapshot replacement;
    replacement.clips.resize(1);
    replacement.clips[0].sampleRate = 48000.0;
    replacement.clips[0].samples.assign(512, 0.1f);
    replacement.mappings.push_back({62, 1, 127, 0, 0, 0, 64, 1.0f, 0.0f});

    PatternClipRuntime hotSwapRuntime;
    hotSwapRuntime.prepare(48000.0);
    hotSwapRuntime.attachSnapshot(&snapshot);
    if (!hotSwapRuntime.noteOn(60, 100, 1)
        || !hotSwapRuntime.publishSnapshot(&replacement)
        || !hotSwapRuntime.noteOn(62, 100, 1)
        || hotSwapRuntime.activeVoiceCount() != 2)
    {
        std::cerr << "Live snapshot publication did not preserve old voices and route new triggers.\\n";
        return 1;
    }
    std::array<float, 8> hotSwapLeft {}, hotSwapRight {};
    hotSwapRuntime.render(hotSwapLeft.data(), hotSwapRight.data(),
                          static_cast<int>(hotSwapLeft.size()));
    if (!(hotSwapLeft[0] > 0.59f && hotSwapLeft[0] < 0.61f))
    {
        std::cerr << "Voices did not retain their respective immutable snapshot PCM.\\n";
        return 1;
    }
    if (hotSwapRuntime.publishSnapshot(&invalidSnapshot))
    {
        std::cerr << "Invalid snapshot replaced the active publication.\\n";
        return 1;
    }
    hotSwapRuntime.clearPublishedSnapshot();
    if (hotSwapRuntime.noteOn(62, 100, 1) || hotSwapRuntime.activeVoiceCount() != 2)
    {
        std::cerr << "Clearing publication affected active voices or accepted new triggers.\\n";
        return 1;
    }
    hotSwapRuntime.detachSnapshot();

    // Distinct RR lanes may overlap in velocity and must alternate deterministically.
    PatternClipSnapshot roundRobin;
    roundRobin.clips.resize(2);
    roundRobin.clips[0].sampleRate = 48000.0;
    roundRobin.clips[0].samples.assign(128, 0.5f);
    roundRobin.clips[1].sampleRate = 48000.0;
    roundRobin.clips[1].samples.assign(128, 0.25f);
    roundRobin.mappings.push_back({64, 1, 127, 0, 0, 0, 64, 1.0f, 0.0f, 1});
    roundRobin.mappings.push_back({64, 1, 127, 1, 0, 0, 64, 1.0f, 0.0f, 2});
    if (!PatternClipRuntime::validateSnapshot(roundRobin))
    {
        std::cerr << "Distinct round-robin lanes with overlapping velocity zones were rejected.\\n";
        return 1;
    }
    PatternClipRuntime rrRuntime;
    rrRuntime.prepare(48000.0);
    rrRuntime.attachSnapshot(&roundRobin);
    std::array<float, 64> rrLeft {}, rrRight {};
    if (!rrRuntime.noteOn(64, 100, 1))
        return 1;
    rrRuntime.render(rrLeft.data(), rrRight.data(), 1);
    if (!(rrLeft[0] > 0.49f && rrLeft[0] < 0.51f))
    {
        std::cerr << "First round-robin lane was not selected.\\n";
        return 1;
    }
    rrRuntime.noteOff(64, 1);
    rrLeft.fill(0.0f);
    rrRight.fill(0.0f);
    rrRuntime.render(rrLeft.data(), rrRight.data(), static_cast<int>(rrLeft.size()));
    rrLeft.fill(0.0f);
    rrRight.fill(0.0f);
    if (!rrRuntime.noteOn(64, 100, 1))
        return 1;
    rrRuntime.render(rrLeft.data(), rrRight.data(), 1);
    if (!(rrLeft[0] > 0.24f && rrLeft[0] < 0.26f))
    {
        std::cerr << "Second round-robin lane did not alternate.\\n";
        return 1;
    }
    rrRuntime.detachSnapshot();

    // Pitch ratio must change playback speed, and invalid ratios must fail closed.
    PatternClipSnapshot pitched;
    pitched.clips.resize(1);
    pitched.clips[0].sampleRate = 48000.0;
    pitched.clips[0].samples.assign(256, 0.2f);
    PatternClipMapping pitchedMapping;
    pitchedMapping.triggerNote = 67;
    pitchedMapping.velocityLow = 1;
    pitchedMapping.velocityHigh = 127;
    pitchedMapping.clipIndex = 0;
    pitchedMapping.releaseSamples = 32;
    pitchedMapping.pitchRatio = 2.0f;
    pitched.mappings.push_back(pitchedMapping);
    if (!PatternClipRuntime::validateSnapshot(pitched))
    {
        std::cerr << "Valid pitch-ratio mapping was rejected.\\n";
        return 1;
    }
    PatternClipRuntime pitchRuntime;
    pitchRuntime.prepare(48000.0);
    pitchRuntime.attachSnapshot(&pitched);
    std::array<float, 128> pitchLeft {}, pitchRight {};
    if (!pitchRuntime.noteOn(67, 100, 1))
        return 1;
    pitchRuntime.render(pitchLeft.data(), pitchRight.data(), 128);
    if (pitchRuntime.activeVoiceCount() != 0)
    {
        std::cerr << "Pitch ratio did not advance the clip at the expected rate.\\n";
        return 1;
    }
    pitched.mappings[0].pitchRatio = 4.01f;
    if (PatternClipRuntime::validateSnapshot(pitched))
    {
        std::cerr << "Out-of-range pitch ratio was accepted.\\n";
        return 1;
    }
    pitchRuntime.detachSnapshot();

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

    for (int i = 0; i < 40; ++i)
        if (!runtime.noteOn(60, 100, 1))
        {
            std::cerr << "Repeated mapped trigger failed during voice-capacity test.\\n";
            return 1;
        }
    if (runtime.activeVoiceCount() != static_cast<int>(PatternClipRuntime::maximumVoices))
    {
        std::cerr << "Voice pool exceeded its fixed capacity or failed to steal.\\n";
        return 1;
    }
    runtime.reset();

    if (runtime.noteOn(62, 100, 1))
    {
        std::cerr << "Unmapped trigger unexpectedly started a clip.\n";
        return 1;
    }

    runtime.detachSnapshot();
    std::cout << "PATTERN clip runtime tests passed.\n";
    return 0;
}
