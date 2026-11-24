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

    // Snapshot ownership is counted per voice and becomes reclaimable after
    // the final voice retires; active publication itself is never reclaimable.
    PatternClipSnapshot ownedSnapshot;
    ownedSnapshot.clips.resize(1);
    ownedSnapshot.clips[0].sampleRate = 48000.0;
    ownedSnapshot.clips[0].samples.assign(64, 0.2f);
    ownedSnapshot.mappings.push_back({65, 1, 127, 0, 0, 0, 1, 1.0f, 0.0f});
    PatternClipRuntime ownershipRuntime;
    ownershipRuntime.prepare(48000.0);
    if (!ownershipRuntime.publishSnapshot(&ownedSnapshot)
        || ownershipRuntime.canRetireSnapshot(&ownedSnapshot)
        || !ownershipRuntime.noteOn(65, 100, 1)
        || ownedSnapshot.activeVoiceReferences.load(std::memory_order_seq_cst) != 1)
    {
        std::cerr << "Snapshot voice ownership was not retained correctly.\\n";
        return 1;
    }
    ownershipRuntime.clearPublishedSnapshot();
    if (ownershipRuntime.canRetireSnapshot(&ownedSnapshot))
    {
        std::cerr << "Snapshot with an active voice was incorrectly marked reclaimable.\\n";
        return 1;
    }
    std::array<float, 128> ownershipLeft {}, ownershipRight {};
    ownershipRuntime.render(ownershipLeft.data(), ownershipRight.data(), 128);
    if (ownedSnapshot.activeVoiceReferences.load(std::memory_order_seq_cst) != 0
        || !ownershipRuntime.canRetireSnapshot(&ownedSnapshot))
    {
        std::cerr << "Retired snapshot did not become reclaimable after its final voice.\\n";
        return 1;
    }
    ownershipRuntime.detachSnapshot();

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
    std::array<float, 129> pitchLeft {}, pitchRight {};
    if (!pitchRuntime.noteOn(67, 100, 1))
        return 1;
    // The renderer retires a voice at the start of the first sample after
    // its playback position reaches the clip end, so render one extra frame.
    pitchRuntime.render(pitchLeft.data(), pitchRight.data(), 129);
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

    // RR progress is independent for each articulation and velocity lane,
    // even when all lanes share the same MIDI trigger note.
    PatternClipSnapshot isolatedRoundRobin;
    isolatedRoundRobin.clips.resize(8);
    const std::array<float, 8> rrValues { 0.10f, 0.20f, 0.30f, 0.40f, 0.50f, 0.60f, 0.70f, 0.80f };
    for (std::size_t i = 0; i < rrValues.size(); ++i)
    {
        isolatedRoundRobin.clips[i].sampleRate = 48000.0;
        isolatedRoundRobin.clips[i].samples.assign(1, rrValues[i]);
    }
    isolatedRoundRobin.mappings.push_back({64, 1, 63, 0, 0, 0, 4, 1.0f, 0.0f, 1});
    isolatedRoundRobin.mappings.push_back({64, 1, 63, 1, 0, 0, 4, 1.0f, 0.0f, 2});
    isolatedRoundRobin.mappings.push_back({64, 64, 127, 2, 0, 0, 4, 1.0f, 0.0f, 1});
    isolatedRoundRobin.mappings.push_back({64, 64, 127, 3, 0, 0, 4, 1.0f, 0.0f, 2});
    isolatedRoundRobin.mappings.push_back({64, 1, 63, 4, 1, 0, 4, 1.0f, 0.0f, 1});
    isolatedRoundRobin.mappings.push_back({64, 1, 63, 5, 1, 0, 4, 1.0f, 0.0f, 2});
    isolatedRoundRobin.mappings.push_back({64, 64, 127, 6, 1, 0, 4, 1.0f, 0.0f, 1});
    isolatedRoundRobin.mappings.push_back({64, 64, 127, 7, 1, 0, 4, 1.0f, 0.0f, 2});
    if (!PatternClipRuntime::validateSnapshot(isolatedRoundRobin))
    {
        std::cerr << "Independent velocity RR lanes were rejected.\\n";
        return 1;
    }
    PatternClipRuntime isolatedRrRuntime;
    isolatedRrRuntime.prepare(48000.0);
    isolatedRrRuntime.attachSnapshot(&isolatedRoundRobin);
    const auto renderRrLane = [&](int velocity, int articulation)
    {
        std::array<float, 1> laneLeft {}, laneRight {};
        if (!isolatedRrRuntime.noteOn(64, velocity, 1, articulation))
            return -1.0f;
        isolatedRrRuntime.render(laneLeft.data(), laneRight.data(), 1);
        return laneLeft[0];
    };
    const float softFirst = renderRrLane(32, 0);
    const float alternateArticulationFirst = renderRrLane(32, 1);
    const float hardFirst = renderRrLane(96, 0);
    const float alternateArticulationHardFirst = renderRrLane(96, 1);
    const float softSecond = renderRrLane(32, 0);
    const float alternateArticulationSecond = renderRrLane(32, 1);
    const float hardSecond = renderRrLane(96, 0);
    const float alternateArticulationHardSecond = renderRrLane(96, 1);
    if (!(std::abs(softFirst - 0.10f) < 0.0001f
        && std::abs(alternateArticulationFirst - 0.50f) < 0.0001f
        && std::abs(hardFirst - 0.30f) < 0.0001f
        && std::abs(alternateArticulationHardFirst - 0.70f) < 0.0001f
        && std::abs(softSecond - 0.20f) < 0.0001f
        && std::abs(alternateArticulationSecond - 0.60f) < 0.0001f
        && std::abs(hardSecond - 0.40f) < 0.0001f
        && std::abs(alternateArticulationHardSecond - 0.80f) < 0.0001f))
    {
        std::cerr << "Round-robin counters leaked between velocity lanes.\\n";
        return 1;
    }
    isolatedRrRuntime.detachSnapshot();

    // Velocity zones must select different recorded clips without affecting
    // the round-robin sequence of another velocity zone.
    PatternClipSnapshot velocityLayers;
    velocityLayers.clips.resize(2);
    velocityLayers.clips[0].sampleRate = 48000.0;
    velocityLayers.clips[0].samples.assign(16, 0.20f);
    velocityLayers.clips[1].sampleRate = 48000.0;
    velocityLayers.clips[1].samples.assign(16, 0.70f);
    velocityLayers.mappings.push_back({72, 1, 63, 0, 0, 0, 4, 1.0f, 0.0f, 1});
    velocityLayers.mappings.push_back({72, 64, 127, 1, 0, 0, 4, 1.0f, 0.0f, 1});
    if (!PatternClipRuntime::validateSnapshot(velocityLayers))
    {
        std::cerr << "Non-overlapping velocity layers were rejected.\\n";
        return 1;
    }
    PatternClipRuntime velocityRuntime;
    velocityRuntime.prepare(48000.0);
    velocityRuntime.attachSnapshot(&velocityLayers);
    std::array<float, 2> velocityLeft {}, velocityRight {};
    if (!velocityRuntime.noteOn(72, 40, 1))
    {
        std::cerr << "Soft velocity did not trigger a mapped layer.\\n";
        return 1;
    }
    velocityRuntime.render(velocityLeft.data(), velocityRight.data(), 1);
    if (!(velocityLeft[0] > 0.19f && velocityLeft[0] < 0.21f))
    {
        std::cerr << "Soft velocity selected the wrong layer.\\n";
        return 1;
    }
    velocityRuntime.reset();
    velocityLeft.fill(0.0f);
    velocityRight.fill(0.0f);
    if (!velocityRuntime.noteOn(72, 100, 1))
    {
        std::cerr << "Hard velocity did not trigger a mapped layer.\\n";
        return 1;
    }
    velocityRuntime.render(velocityLeft.data(), velocityRight.data(), 1);
    if (!(velocityLeft[0] > 0.69f && velocityLeft[0] < 0.71f))
    {
        std::cerr << "Hard velocity selected the wrong layer.\\n";
        return 1;
    }
    velocityRuntime.detachSnapshot();

    // All Notes Off must release every active voice, regardless of channel.
    PatternClipSnapshot allNotesOffSnapshot;
    allNotesOffSnapshot.clips.resize(1);
    allNotesOffSnapshot.clips[0].sampleRate = 48000.0;
    allNotesOffSnapshot.clips[0].samples.assign(64, 0.35f);
    allNotesOffSnapshot.mappings.push_back({69, 1, 127, 0, 0, 0, 4, 1.0f, 0.0f, 1});
    PatternClipRuntime allNotesOffRuntime;
    allNotesOffRuntime.prepare(48000.0);
    allNotesOffRuntime.attachSnapshot(&allNotesOffSnapshot);
    if (!allNotesOffRuntime.noteOn(69, 100, 1)
        || !allNotesOffRuntime.noteOn(69, 100, 2))
    {
        std::cerr << "Could not start voices for All Notes Off contract.\\n";
        return 1;
    }
    allNotesOffRuntime.allNotesOff();
    std::array<float, 8> allOffLeft {}, allOffRight {};
    allNotesOffRuntime.render(allOffLeft.data(), allOffRight.data(),
                              static_cast<int>(allOffLeft.size()));
    if (allNotesOffRuntime.activeVoiceCount() != 0)
    {
        std::cerr << "All Notes Off failed to release every channel voice.\\n";
        return 1;
    }
    allNotesOffRuntime.detachSnapshot();

    // All Sound Off is immediate and must not leave a release tail.
    PatternClipSnapshot allSoundOffSnapshot;
    allSoundOffSnapshot.clips.resize(1);
    allSoundOffSnapshot.clips[0].sampleRate = 48000.0;
    allSoundOffSnapshot.clips[0].samples.assign(64, 0.45f);
    allSoundOffSnapshot.mappings.push_back({70, 1, 127, 0, 0, 0, 64, 1.0f, 0.0f, 1});
    PatternClipRuntime allSoundOffRuntime;
    allSoundOffRuntime.prepare(48000.0);
    allSoundOffRuntime.attachSnapshot(&allSoundOffSnapshot);
    if (!allSoundOffRuntime.noteOn(70, 100, 1)
        || allSoundOffRuntime.activeVoiceCount() != 1)
    {
        std::cerr << "Could not start voice for All Sound Off contract.\\n";
        return 1;
    }
    allSoundOffRuntime.allSoundOff();
    if (allSoundOffRuntime.activeVoiceCount() != 0)
    {
        std::cerr << "All Sound Off did not terminate voices immediately.\\n";
        return 1;
    }
    std::array<float, 8> allSoundLeft {}, allSoundRight {};
    allSoundOffRuntime.render(allSoundLeft.data(), allSoundRight.data(),
                              static_cast<int>(allSoundLeft.size()));
    if (std::abs(allSoundLeft[0]) > 0.000001f)
    {
        std::cerr << "All Sound Off left an audible release tail.\\n";
        return 1;
    }
    allSoundOffRuntime.detachSnapshot();

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
