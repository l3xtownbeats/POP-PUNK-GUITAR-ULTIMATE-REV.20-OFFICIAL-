#ifndef JucePlugin_Name
#define JucePlugin_Name "POP PUNK GUITAR ULTIMATE"
#endif

// Conflict-check: this integration test drives the real AudioProcessor path
// (MIDI -> held chord -> PatternScheduler -> SamplerEngine -> streamed WAV).
// It uses only temporary synthetic fixtures; no production sample assets or
// licensed third-party content are copied into the test.
#include "PluginProcessor.h"
#include <PPGUTestData.h>

#include <juce_audio_formats/juce_audio_formats.h>
#include <array>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <iostream>
#include <memory>
#include <thread>
#include <chrono>
#include <condition_variable>
#include <mutex>
#include <utility>

namespace
{
bool writeTone(const juce::File& file, float amplitude, double frequency)
{
    constexpr int sampleRate = 48000;
    constexpr int frames = sampleRate;
    juce::AudioBuffer<float> audio(1, frames);
    for (int i = 0; i < frames; ++i)
        audio.setSample(0, i, amplitude * std::sin(
            juce::MathConstants<double>::twoPi * frequency * static_cast<double>(i) / sampleRate));

    juce::WavAudioFormat wav;
    std::unique_ptr<juce::OutputStream> output(file.createOutputStream());
    if (!output)
        return false;

    std::unique_ptr<juce::AudioFormatWriter> writer(
        wav.createWriterFor(output.get(), sampleRate, 1, 24, {}, 0));
    if (!writer)
        return false;

    output.release();
    return writer->writeFromAudioSampleBuffer(audio, 0, frames);
}

bool setParameter(PopPunkGuitarUltimateAudioProcessor& processor,
                  const char* id, float value)
{
    auto* parameter = processor.parameters.getRawParameterValue(id);
    if (parameter == nullptr)
    {
        std::cerr << "Missing APVTS parameter: " << id << "\n";
        return false;
    }
    parameter->store(value, std::memory_order_relaxed);
    return true;
}

double rms(const juce::AudioBuffer<float>& audio, int start, int length)
{
    const int boundedStart = juce::jlimit(0, audio.getNumSamples(), start);
    const int boundedEnd = juce::jlimit(boundedStart, audio.getNumSamples(), start + length);
    if (boundedEnd <= boundedStart)
        return 0.0;

    double sum = 0.0;
    std::uint64_t count = 0;
    for (int channel = 0; channel < audio.getNumChannels(); ++channel)
    {
        const auto* data = audio.getReadPointer(channel);
        for (int i = boundedStart; i < boundedEnd; ++i)
        {
            const double value = data[i];
            sum += value * value;
            ++count;
        }
    }
    return count == 0 ? 0.0 : std::sqrt(sum / static_cast<double>(count));
}

void addChordOn(juce::MidiBuffer& midi, int sample, const std::array<int, 3>& notes)
{
    for (const int note : notes)
        midi.addEvent(juce::MidiMessage::noteOn(1, note, static_cast<juce::uint8>(110)), sample);
}

void addChordOff(juce::MidiBuffer& midi, int sample, const std::array<int, 3>& notes)
{
    for (const int note : notes)
        midi.addEvent(juce::MidiMessage::noteOff(1, note), sample);
}
}

int main()
{
    int result = 0;
    if (PPGUTestData::ppgu_test_data_txtSize <= 0)
    {
        std::cerr << "Generated PPGU test binary-data fixture is empty.\\n";
        return 1;
    }

    juce::ScopedJuceInitialiser_GUI juceInitialiser;
    const auto root = std::filesystem::temp_directory_path() / "ppgu-processor-pattern-integration";
    std::error_code cleanupError;

    // Exercise the newly wired recorded-clip route through the real processor.
    // A single MIDI key must play one clip directly, unaffected by AutoChords.
    {
        PopPunkGuitarUltimateAudioProcessor clipProcessor;
        clipProcessor.prepareToPlay(48000.0, 256);
        auto snapshot = std::make_unique<ppgu::performance::PatternClipSnapshot>();
        snapshot->clips.resize(1);
        snapshot->clips[0].sampleRate = 48000.0;
        snapshot->clips[0].samples.assign(2048, 0.25f);
        snapshot->mappings.push_back({72, 1, 127, 0, 0, 0, 64, 1.0f, 0.0f});
        if (!clipProcessor.installPatternClipSnapshot(std::move(snapshot)))
        {
            std::cerr << "Processor rejected a valid immutable PATTERN clip snapshot.\\n";
            result = 1;
        }
        setParameter(clipProcessor, "playMode", 1.0f);
        setParameter(clipProcessor, "articulation", 0.0f);
        setParameter(clipProcessor, "singleMidiNoteAsChordRoot", 1.0f);
        setParameter(clipProcessor, "ampGain", 5.0f);
        setParameter(clipProcessor, "master", 1.0f);
        setParameter(clipProcessor, "eqOn", 0.0f);
        setParameter(clipProcessor, "compressorOn", 0.0f);
        setParameter(clipProcessor, "distortionOn", 0.0f);
        setParameter(clipProcessor, "chorusOn", 0.0f);
        setParameter(clipProcessor, "flangerOn", 0.0f);
        setParameter(clipProcessor, "delayOn", 0.0f);
        setParameter(clipProcessor, "reverbOn", 0.0f);
        setParameter(clipProcessor, "cabinetOn", 0.0f);
        juce::AudioBuffer<float> clipBlock(2, 256);
        juce::MidiBuffer clipMidi;
        clipMidi.addEvent(juce::MidiMessage::noteOn(1, 72, static_cast<juce::uint8>(100)), 32);
        clipMidi.addEvent(juce::MidiMessage::noteOff(1, 72), 96);
        clipProcessor.processBlock(clipBlock, clipMidi);
        const auto* left = clipBlock.getReadPointer(0);
        bool exactStart = true;
        for (int i = 0; i < 32; ++i)
            if (std::abs(left[i]) > 1.0e-7f) exactStart = false;
        if (!exactStart || !(left[32] > 0.15f) || std::abs(left[180]) > 1.0e-6f)
        {
            std::cerr << "Recorded PATTERN clip did not respect sample-accurate Note On / Note Off release.\\n";
            result = 1;
        }
    }

    // Exercise the asynchronous registry path: decoding/publication happens
    // off the message thread, completion is marshalled back to it, and a valid
    // empty registry explicitly clears an already-published snapshot.
    {
        const auto asyncRoot = std::filesystem::temp_directory_path()
            / "ppgu-pattern-async-empty-registry";
        std::error_code asyncCleanupError;
        std::filesystem::remove_all(asyncRoot, asyncCleanupError);
        std::filesystem::create_directories(asyncRoot);
        const juce::File asyncManifest(asyncRoot.string() + "/pattern_clips.json");
        const juce::File invalidManifest(asyncRoot.string() + "/invalid_pattern_clips.json");
        if (!asyncManifest.replaceWithText("{\n  \"schema_version\": 1,\n  \"clips\": []\n}")
            || !invalidManifest.replaceWithText("{ malformed json"))
        {
            std::cerr << "Could not create asynchronous PATTERN registry fixture.\n";
            result = 1;
        }
        else
        {
            PopPunkGuitarUltimateAudioProcessor asyncProcessor;
            asyncProcessor.prepareToPlay(48000.0, 256);
            auto asyncSnapshot = std::make_unique<ppgu::performance::PatternClipSnapshot>();
            asyncSnapshot->clips.resize(1);
            asyncSnapshot->clips[0].sampleRate = 48000.0;
            asyncSnapshot->clips[0].samples.assign(1024, 0.25f);
            asyncSnapshot->mappings.push_back({72, 1, 127, 0, 0, 0, 64, 1.0f, 0.0f});
            if (!asyncProcessor.installPatternClipSnapshot(std::move(asyncSnapshot)))
            {
                std::cerr << "Could not publish seed snapshot for async registry test.\\n";
                result = 1;
            }

            setParameter(asyncProcessor, "playMode", 1.0f);
            setParameter(asyncProcessor, "articulation", 0.0f);
            setParameter(asyncProcessor, "ampGain", 5.0f);
            setParameter(asyncProcessor, "master", 1.0f);
            setParameter(asyncProcessor, "eqOn", 0.0f);
            setParameter(asyncProcessor, "compressorOn", 0.0f);
            setParameter(asyncProcessor, "distortionOn", 0.0f);
            setParameter(asyncProcessor, "chorusOn", 0.0f);
            setParameter(asyncProcessor, "flangerOn", 0.0f);
            setParameter(asyncProcessor, "delayOn", 0.0f);
            setParameter(asyncProcessor, "reverbOn", 0.0f);
            setParameter(asyncProcessor, "cabinetOn", 0.0f);

            // First prove the seeded snapshot is genuinely audible. Without this
            // baseline, a broken MIDI route could make the later clear assertion
            // pass trivially because the processor was silent all along.
            juce::AudioBuffer<float> baselineBlock(2, 256);
            juce::MidiBuffer baselineMidi;
            baselineMidi.addEvent(
                juce::MidiMessage::noteOn(1, 72, static_cast<juce::uint8>(110)), 0);
            baselineMidi.addEvent(juce::MidiMessage::noteOff(1, 72), 128);
            asyncProcessor.processBlock(baselineBlock, baselineMidi);
            double baselinePeak = 0.0;
            for (int channel = 0; channel < baselineBlock.getNumChannels(); ++channel)
                for (int sample = 0; sample < baselineBlock.getNumSamples(); ++sample)
                    baselinePeak = juce::jmax(baselinePeak, std::abs(
                        static_cast<double>(baselineBlock.getSample(channel, sample))));
            if (!(baselinePeak > 0.05))
            {
                std::cerr << "Seed PATTERN snapshot produced no audible baseline; async clear test is invalid. Peak="
                          << baselinePeak << "\n";
                result = 1;
            }

            std::atomic<bool> completed { false };
            std::atomic<bool> invalidCallbackOnMessageThread { false };
            std::atomic<bool> invalidRejected { false };
            std::atomic<bool> retainedSnapshotAudible { false };
            std::atomic<bool> emptyCallbackOnMessageThread { false };
            std::atomic<bool> reportedEmpty { false };

            // A malformed registry must fail closed and leave the already
            // published snapshot usable. Once that is verified, load a valid
            // empty registry and verify that it explicitly clears the snapshot.
            asyncProcessor.loadPatternClipRegistryAsync(invalidManifest,
                [&](ppgu::performance::PatternClipLoadResult invalidResult)
                {
                    invalidCallbackOnMessageThread.store(
                        juce::MessageManager::getInstance()->isThisTheMessageThread(),
                        std::memory_order_release);
                    const bool rejected = !invalidResult.ready && !invalidResult.empty
                        && invalidResult.snapshot == nullptr && !invalidResult.errors.empty();
                    invalidRejected.store(rejected, std::memory_order_release);

                    juce::AudioBuffer<float> retainedBlock(2, 256);
                    juce::MidiBuffer retainedMidi;
                    retainedMidi.addEvent(
                        juce::MidiMessage::noteOn(1, 72, static_cast<juce::uint8>(110)), 0);
                    retainedMidi.addEvent(juce::MidiMessage::noteOff(1, 72), 128);
                    asyncProcessor.processBlock(retainedBlock, retainedMidi);
                    double retainedPeak = 0.0;
                    for (int channel = 0; channel < retainedBlock.getNumChannels(); ++channel)
                        for (int sample = 0; sample < retainedBlock.getNumSamples(); ++sample)
                            retainedPeak = juce::jmax(retainedPeak, std::abs(
                                static_cast<double>(retainedBlock.getSample(channel, sample))));
                    retainedSnapshotAudible.store(retainedPeak > 0.05,
                                                  std::memory_order_release);

                    asyncProcessor.loadPatternClipRegistryAsync(asyncManifest,
                        [&](ppgu::performance::PatternClipLoadResult emptyResult)
                        {
                            emptyCallbackOnMessageThread.store(
                                juce::MessageManager::getInstance()->isThisTheMessageThread(),
                                std::memory_order_release);
                            reportedEmpty.store(emptyResult.empty && !emptyResult.ready
                                                    && emptyResult.errors.empty()
                                                    && emptyResult.snapshot == nullptr,
                                                std::memory_order_release);
                            completed.store(true, std::memory_order_release);
                        });
                });

            auto* messageManager = juce::MessageManager::getInstance();
            std::atomic<bool> timedOut { false };
            std::thread timeoutThread([&]
            {
                const auto deadline = std::chrono::steady_clock::now()
                    + std::chrono::seconds(5);
                while (!completed.load(std::memory_order_acquire)
                       && std::chrono::steady_clock::now() < deadline)
                    std::this_thread::sleep_for(std::chrono::milliseconds(1));

                if (!completed.load(std::memory_order_acquire))
                {
                    timedOut.store(true, std::memory_order_release);
                    messageManager->stopDispatchLoop();
                }
            });

            messageManager->runDispatchLoop();
            timeoutThread.join();

            if (!completed.load(std::memory_order_acquire)
                || timedOut.load(std::memory_order_acquire))
            {
                std::cerr << "Asynchronous PATTERN registry completion timed out.\n";
                result = 1;
            }
            else if (!invalidCallbackOnMessageThread.load(std::memory_order_acquire)
                     || !invalidRejected.load(std::memory_order_acquire)
                     || !retainedSnapshotAudible.load(std::memory_order_acquire)
                     || !emptyCallbackOnMessageThread.load(std::memory_order_acquire)
                     || !reportedEmpty.load(std::memory_order_acquire))
            {
                std::cerr << "Asynchronous PATTERN invalid-retention / empty-clear contract failed."
                          << " invalidThread="
                          << invalidCallbackOnMessageThread.load(std::memory_order_acquire)
                          << " invalidRejected=" << invalidRejected.load(std::memory_order_acquire)
                          << " retainedAudible=" << retainedSnapshotAudible.load(std::memory_order_acquire)
                          << " emptyThread="
                          << emptyCallbackOnMessageThread.load(std::memory_order_acquire)
                          << " reportedEmpty=" << reportedEmpty.load(std::memory_order_acquire)
                          << "\n";
                result = 1;
            }
            else
            {
                juce::AudioBuffer<float> clearedBlock(2, 256);
                juce::MidiBuffer clearedMidi;
                clearedMidi.addEvent(
                    juce::MidiMessage::noteOn(1, 72, static_cast<juce::uint8>(110)), 0);
                asyncProcessor.processBlock(clearedBlock, clearedMidi);
                double clearedPeak = 0.0;
                for (int channel = 0; channel < clearedBlock.getNumChannels(); ++channel)
                    for (int sample = 0; sample < clearedBlock.getNumSamples(); ++sample)
                        clearedPeak = juce::jmax(clearedPeak, std::abs(
                            static_cast<double>(clearedBlock.getSample(channel, sample))));
                if (clearedPeak > 1.0e-7)
                {
                    std::cerr << "A valid empty async registry did not clear the published PATTERN snapshot.\n";
                    result = 1;
                }
            }
        }
        std::filesystem::remove_all(asyncRoot, asyncCleanupError);
        if (asyncCleanupError)
        {
            std::cerr << "Could not remove async PATTERN fixtures: "
                      << asyncCleanupError.message() << "\n";
            result = 1;
        }
    }

    // Deterministic A/B load race: A starts first and is held inside its
    // injected decoder; B starts on the second worker and publishes first.
    // Only after B's message-thread completion do we release A, then wait for
    // A's worker-side stale-generation check to finish before inspecting audio.
    {
        PopPunkGuitarUltimateAudioProcessor raceProcessor;
        raceProcessor.prepareToPlay(48000.0, 256);
        setParameter(raceProcessor, "playMode", 1.0f);
        setParameter(raceProcessor, "articulation", 0.0f);
        setParameter(raceProcessor, "singleMidiNoteAsChordRoot", 1.0f);
        setParameter(raceProcessor, "ampGain", 5.0f);
        setParameter(raceProcessor, "master", 1.0f);
        setParameter(raceProcessor, "eqOn", 0.0f);
        setParameter(raceProcessor, "compressorOn", 0.0f);
        setParameter(raceProcessor, "distortionOn", 0.0f);
        setParameter(raceProcessor, "chorusOn", 0.0f);
        setParameter(raceProcessor, "flangerOn", 0.0f);
        setParameter(raceProcessor, "delayOn", 0.0f);
        setParameter(raceProcessor, "reverbOn", 0.0f);
        setParameter(raceProcessor, "cabinetOn", 0.0f);

        std::mutex raceMutex;
        std::condition_variable raceCv;
        bool aStarted = false;
        bool releaseA = false;
        std::atomic<bool> aWorkerFinished { false };
        std::atomic<bool> aCallbackCalled { false };
        std::atomic<bool> bCallbackOnMessageThread { false };
        std::atomic<bool> bPublishedAudible { false };
        std::atomic<bool> raceCompleted { false };
        std::atomic<bool> raceTimedOut { false };

        const auto makeLoadResult = [](float amplitude)
        {
            ppgu::performance::PatternClipLoadResult loaded;
            loaded.snapshot = std::make_unique<ppgu::performance::PatternClipSnapshot>();
            loaded.snapshot->clips.resize(1);
            loaded.snapshot->clips[0].sampleRate = 48000.0;
            loaded.snapshot->clips[0].samples.assign(2048, amplitude);
            loaded.snapshot->mappings.push_back({72, 1, 127, 0, 0, 0, 64, 1.0f, 0.0f});
            loaded.ready = true;
            return loaded;
        };

        const juce::File loadA("race-load-A.json");
        const juce::File loadB("race-load-B.json");
        raceProcessor.loadPatternClipRegistryAsyncForTesting(
            loadA,
            [&](ppgu::performance::PatternClipLoadResult)
            {
                aCallbackCalled.store(true, std::memory_order_release);
            },
            [&](const juce::File&)
            {
                std::unique_lock<std::mutex> lock(raceMutex);
                aStarted = true;
                raceCv.notify_all();
                raceCv.wait(lock, [&] { return releaseA; });
                lock.unlock();
                return makeLoadResult(0.10f);
            },
            [&]
            {
                aWorkerFinished.store(true, std::memory_order_release);
                raceCv.notify_all();
            });

        {
            std::unique_lock<std::mutex> lock(raceMutex);
            if (!raceCv.wait_for(lock, std::chrono::seconds(3), [&] { return aStarted; }))
            {
                std::cerr << "PATTERN race test: load A did not enter its controlled decoder.\n";
                result = 1;
                releaseA = true;
                raceCv.notify_all();
            }
        }

        if (aStarted)
        {
            raceProcessor.loadPatternClipRegistryAsyncForTesting(
                loadB,
                [&](ppgu::performance::PatternClipLoadResult loadedB)
                {
                    bCallbackOnMessageThread.store(
                        juce::MessageManager::getInstance()->isThisTheMessageThread()
                            && loadedB.ready && loadedB.errors.empty(),
                        std::memory_order_release);
                    {
                        std::lock_guard<std::mutex> lock(raceMutex);
                        releaseA = true;
                    }
                    raceCv.notify_all();

                    {
                        std::unique_lock<std::mutex> lock(raceMutex);
                        if (!raceCv.wait_for(lock, std::chrono::seconds(3), [&]
                            {
                                return aWorkerFinished.load(std::memory_order_acquire);
                            }))
                        {
                            raceTimedOut.store(true, std::memory_order_release);
                        }
                    }

                    juce::AudioBuffer<float> rendered(2, 256);
                    juce::MidiBuffer midi;
                    midi.addEvent(
                        juce::MidiMessage::noteOn(1, 72, static_cast<juce::uint8>(110)), 0);
                    midi.addEvent(juce::MidiMessage::noteOff(1, 72), 128);
                    raceProcessor.processBlock(rendered, midi);
                    double peak = 0.0;
                    for (int channel = 0; channel < rendered.getNumChannels(); ++channel)
                        for (int sample = 0; sample < rendered.getNumSamples(); ++sample)
                            peak = juce::jmax(peak, std::abs(
                                static_cast<double>(rendered.getSample(channel, sample))));
                    bPublishedAudible.store(peak > 0.25, std::memory_order_release);
                    raceCompleted.store(true, std::memory_order_release);
                },
                [&](const juce::File&)
                {
                    return makeLoadResult(0.55f);
                },
                {});

            auto* messageManager = juce::MessageManager::getInstance();
            std::thread timeoutThread([&]
            {
                const auto deadline = std::chrono::steady_clock::now()
                    + std::chrono::seconds(5);
                while (!raceCompleted.load(std::memory_order_acquire)
                       && std::chrono::steady_clock::now() < deadline)
                    std::this_thread::sleep_for(std::chrono::milliseconds(1));
                if (!raceCompleted.load(std::memory_order_acquire))
                {
                    raceTimedOut.store(true, std::memory_order_release);
                    {
                        std::lock_guard<std::mutex> lock(raceMutex);
                        releaseA = true;
                    }
                    raceCv.notify_all();
                    messageManager->stopDispatchLoop();
                }
            });
            messageManager->runDispatchLoop();
            timeoutThread.join();
        }

        if (raceTimedOut.load(std::memory_order_acquire)
            || !aWorkerFinished.load(std::memory_order_acquire)
            || !bCallbackOnMessageThread.load(std::memory_order_acquire)
            || !bPublishedAudible.load(std::memory_order_acquire)
            || aCallbackCalled.load(std::memory_order_acquire))
        {
            std::cerr << "PATTERN A/B generation race contract failed."
                      << " aFinished=" << aWorkerFinished.load(std::memory_order_acquire)
                      << " bCallback=" << bCallbackOnMessageThread.load(std::memory_order_acquire)
                      << " bAudible=" << bPublishedAudible.load(std::memory_order_acquire)
                      << " staleACallback=" << aCallbackCalled.load(std::memory_order_acquire)
                      << " timeout=" << raceTimedOut.load(std::memory_order_acquire) << "\n";
            result = 1;
        }
    }

    std::filesystem::remove_all(root, cleanupError);
    std::filesystem::create_directories(root);

    const juce::File directory(root.string());
    const auto firstTone = directory.getChildFile("first-chord.wav");
    const auto secondTone = directory.getChildFile("second-chord.wav");
    const auto thirdTone = directory.getChildFile("third-chord.wav");
    const auto sfz = directory.getChildFile("pattern-test.sfz");

    // Different source levels make the chord identity observable in rendered
    // audio: chord A is deliberately 3x louder than chord B.
    if (!writeTone(firstTone, 0.60f, 220.0)
        || !writeTone(secondTone, 0.40f, 330.0)
        || !writeTone(thirdTone, 0.20f, 440.0))
    {
        std::cerr << "Could not create deterministic WAV fixtures.\n";
        return 1;
    }

    const auto sfzText =
        "<region> sample=first-chord.wav key=60 ampeg_release=0.01\n"
        "<region> sample=first-chord.wav key=64 ampeg_release=0.01\n"
        "<region> sample=first-chord.wav key=67 ampeg_release=0.01\n"
        "<region> sample=second-chord.wav key=62 ampeg_release=0.01\n"
        "<region> sample=second-chord.wav key=66 ampeg_release=0.01\n"
        "<region> sample=second-chord.wav key=69 ampeg_release=0.01\n"
        "<region> sample=third-chord.wav key=55 ampeg_release=0.01\n"
        "<region> sample=third-chord.wav key=59 ampeg_release=0.01\n"
        "<region> sample=third-chord.wav key=62 ampeg_release=0.01\n";
    if (!sfz.replaceWithText(sfzText))
    {
        std::cerr << "Could not create SFZ fixture.\n";
        return 1;
    }

    {
        PopPunkGuitarUltimateAudioProcessor processor;
        // Section routing is independent of the legacy global APVTS slot.
        processor.setSelectedSongSection(1);
        processor.setSectionPatternSlot(1, 3);
        processor.setPatternPreviewSlot(5);
        if (processor.getSelectedSongSection() != 1
            || processor.getSectionPatternSlot(1) != 3
            || processor.getPatternPreviewSlot() != 5)
        {
            std::cerr << "Pattern section routing API contract failed.\\n";
            result = 1;
        }
        juce::MemoryBlock sectionState;
        processor.getStateInformation(sectionState);
        PopPunkGuitarUltimateAudioProcessor restoredSections;
        restoredSections.setStateInformation(sectionState.getData(), static_cast<int>(sectionState.getSize()));
        if (restoredSections.getSelectedSongSection() != 1
            || restoredSections.getSectionPatternSlot(1) != 3
            || restoredSections.getPatternPreviewSlot() != -1)
        {
            std::cerr << "Pattern section persistence / transient preview contract failed.\\n";
            result = 1;
        }
        processor.clearPatternPreview();
        processor.setSelectedSongSection(0);
        processor.setSectionPatternSlot(1, -1);

        processor.prepareToPlay(48000.0, 13000);
        const auto load = processor.loadSfzFile(sfz);
        if (!load.success)
        {
            std::cerr << "Processor failed to load SFZ fixture.\n";
            for (const auto& error : load.errors)
                std::cerr << error << "\n";
            result = 1;
        }

        const std::array<std::pair<const char*, float>, 17> settings {{
            { "playMode", 1.0f }, { "syncMode", 2.0f }, { "patternSlot", 0.0f },
            { "patternLength", 0.0f }, { "patternQuantize", 0.0f }, { "bpm", 120.0f },
            { "startOnFirstChord", 1.0f }, { "voices", 64.0f }, { "master", 1.0f },
            { "ampGain", 5.0f }, { "eqOn", 0.0f }, { "compressorOn", 0.0f },
            { "distortionOn", 0.0f }, { "chorusOn", 0.0f }, { "flangerOn", 0.0f },
            { "delayOn", 0.0f }, { "reverbOn", 0.0f }
        }};
        for (const auto& setting : settings)
            if (!setParameter(processor, setting.first, setting.second))
                result = 1;
        if (!setParameter(processor, "cabinetOn", 0.0f)
            || !setParameter(processor, "doubleTrackOn", 0.0f))
            result = 1;

        if (result == 0)
        {
            const std::array<int, 3> chordA { 60, 64, 67 };
            const std::array<int, 3> chordB { 62, 66, 69 };
            const std::array<int, 3> chordC { 55, 59, 62 };

            // Warm the first chord's streaming page before measuring audio.
            // The first note is deliberately sent through the real processor.
            juce::AudioBuffer<float> warmBlock(2, 128);
            juce::MidiBuffer warmMidi;
            addChordOn(warmMidi, 16, chordA);
            processor.processBlock(warmBlock, warmMidi);
            std::this_thread::sleep_for(std::chrono::milliseconds(30));

            // One real processor block contains two distinct chord replacements.
            // The second replacement must not expose a transient empty chord or
            // restart the pattern cycle. The third chord should drive step 2.
            juce::AudioBuffer<float> blockA(2, 13000);
            juce::MidiBuffer midiA;
            addChordOff(midiA, 5872, chordA); // absolute sample 6000
            addChordOn(midiA, 5872, chordB);
            addChordOff(midiA, 8872, chordB); // absolute sample 9000
            addChordOn(midiA, 8872, chordC);
            processor.processBlock(blockA, midiA);
            std::this_thread::sleep_for(std::chrono::milliseconds(30));

            // The first step of the next 8th-note slot is at absolute sample
            // 12016. Its source page may have missed the cache in block A, so
            // the streaming reader must retain the cursor into this block.
            juce::AudioBuffer<float> blockB(2, 13000);
            juce::MidiBuffer midiB;
            processor.processBlock(blockB, midiB);

            const double firstChordRms = rms(blockA, 256, 4200);
            const double finalChordRms = rms(blockB, 1000, 7000);
            if (!(firstChordRms > 0.04))
            {
                std::cerr << "First chord did not reach the real sampler output; RMS="
                          << firstChordRms << "\n";
                result = 1;
            }
            if (!(finalChordRms > 0.008 && finalChordRms < firstChordRms * 0.65))
            {
                std::cerr << "Final chord snapshot was not rendered after two same-block chord replacements; "
                          << "first RMS=" << firstChordRms
                          << ", final RMS=" << finalChordRms << "\n";
                result = 1;
            }
        }
    }

    std::filesystem::remove_all(root, cleanupError);
    if (cleanupError)
    {
        std::cerr << "Could not remove temporary integration fixtures: "
                  << cleanupError.message() << "\n";
        result = 1;
    }

    if (result == 0)
        std::cout << "Processor Pattern MIDI integration test passed.\n";
    return result;
}
