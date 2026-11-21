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

double toneMagnitude(const juce::AudioBuffer<float>& audio, int start, int length,
                     double frequency, double sampleRate)
{
    if (audio.getNumChannels() == 0 || length <= 0)
        return 0.0;
    const auto* data = audio.getReadPointer(0);
    const int begin = juce::jlimit(0, audio.getNumSamples(), start);
    const int end = juce::jlimit(begin, audio.getNumSamples(), start + length);
    if (end <= begin)
        return 0.0;

    double real = 0.0;
    double imaginary = 0.0;
    for (int sample = begin; sample < end; ++sample)
    {
        const double phase = juce::MathConstants<double>::twoPi * frequency
            * static_cast<double>(sample - begin) / sampleRate;
        real += static_cast<double>(data[sample]) * std::cos(phase);
        imaginary -= static_cast<double>(data[sample]) * std::sin(phase);
    }
    return 2.0 * std::sqrt(real * real + imaginary * imaginary)
        / static_cast<double>(end - begin);
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
    if (PPGUTestData::ppgu_test_data_txtSize <= 0)
    {
        std::cerr << "Generated PPGU test binary-data fixture is empty.\\n";
        return 1;
    }

    juce::ScopedJuceInitialiser_GUI juceInitialiser;
    const auto root = std::filesystem::temp_directory_path() / "ppgu-processor-pattern-integration";
    std::error_code cleanupError;
    std::filesystem::remove_all(root, cleanupError);
    std::filesystem::create_directories(root);

    const juce::File directory(root.string());
    const auto firstTone = directory.getChildFile("first-chord.wav");
    const auto secondTone = directory.getChildFile("second-chord.wav");
    const auto thirdTone = directory.getChildFile("third-chord.wav");
    const auto sfz = directory.getChildFile("pattern-test.sfz");
    const auto autoChordSfz = directory.getChildFile("autochord-spectral-test.sfz");

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

    // Separate spectral fixture ensures the auto-generated triad test cannot
    // alter the velocity/loudness behavior of the existing chord scenarios.
    const auto autoChordSfzText =
        "<region> sample=first-chord.wav key=60 ampeg_release=0.01\n"
        "<region> sample=second-chord.wav key=64 ampeg_release=0.01\n"
        "<region> sample=third-chord.wav key=67 ampeg_release=0.01\n";
    if (!autoChordSfz.replaceWithText(autoChordSfzText))
    {
        std::cerr << "Could not create AutoChords spectral SFZ fixture.\n";
        return 1;
    }

    int result = 0;
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

        const std::array<std::pair<const char*, float>, 20> settings {{
            { "playMode", 1.0f }, { "syncMode", 2.0f }, { "patternSlot", 0.0f },
            { "patternLength", 0.0f }, { "patternQuantize", 0.0f }, { "bpm", 120.0f },
            { "startOnFirstChord", 1.0f }, { "voices", 64.0f }, { "master", 1.0f },
            { "ampGain", 5.0f }, { "eqOn", 0.0f }, { "compressorOn", 0.0f },
            { "distortionOn", 0.0f }, { "chorusOn", 0.0f }, { "flangerOn", 0.0f },
            { "delayOn", 0.0f }, { "reverbOn", 0.0f },
            { "singleMidiNoteAsChordRoot", 1.0f }, { "scaleRoot", 0.0f }, { "scaleMode", 1.0f }
        }};
        for (const auto& setting : settings)
            if (!setParameter(processor, setting.first, setting.second))
                result = 1;
        if (!setParameter(processor, "cabinetOn", 0.0f)
            || !setParameter(processor, "doubleTrackOn", 0.0f))
            result = 1;
        const auto spectralLoad = processor.loadSfzFile(autoChordSfz);
        if (!spectralLoad.success)
        {
            std::cerr << "Could not load isolated AutoChords spectral fixture.\n";
            result = 1;
        }

        if (result == 0)
        {
            const std::array<int, 3> chordA { 60, 64, 67 };
            const std::array<int, 3> chordB { 62, 66, 69 };
            const std::array<int, 3> chordC { 55, 59, 62 };

            // A single incoming C4 must be expanded by the real AutoChord
            // path to C4-E4-G4, then scheduled into the same SamplerEngine.
            juce::AudioBuffer<float> warmBlock(2, 128);
            juce::MidiBuffer warmMidi;
            warmMidi.addEvent(juce::MidiMessage::noteOn(1, 60, static_cast<juce::uint8>(110)), 16);
            processor.processBlock(warmBlock, warmMidi);

            ppgu::performance::AutoChordDisplayState autoChordState;
            if (!processor.getAutoChordDisplayState(autoChordState)
                || autoChordState.inputNoteCount != 1 || autoChordState.inputNotes[0] != 60
                || autoChordState.noteCount != 3
                || autoChordState.generatedNotes[0] != 60
                || autoChordState.generatedNotes[1] != 64
                || autoChordState.generatedNotes[2] != 67
                || !autoChordState.enabled || !autoChordState.autoChordApplied
                || autoChordState.playMode != 1)
            {
                std::cerr << "Single-root AutoChords display/processor contract failed.\\n";
                result = 1;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(30));

            // Render a fresh block while only C4 is physically held. The SFZ
            // maps generated C4/E4/G4 to distinct 220/330/440 Hz fixtures, so
            // all three spectral components prove that the generated notes
            // reached the sampler voices (not merely the UI snapshot).
            juce::AudioBuffer<float> autoChordAudioBlock(2, 13000);
            juce::MidiBuffer noAdditionalMidi;
            processor.processBlock(autoChordAudioBlock, noAdditionalMidi);
            // The pattern's first gate is 0.20 beat (about 100 ms) long.
            // Inspect an early window in the following block, before its
            // sample-accurate NoteOff, rather than after the gate has closed.
            const double autoChordRms = rms(autoChordAudioBlock, 1000, 3000);
            const double c4Magnitude = toneMagnitude(autoChordAudioBlock, 1000, 3000, 220.0, 48000.0);
            const double e4Magnitude = toneMagnitude(autoChordAudioBlock, 1000, 3000, 330.0, 48000.0);
            const double g4Magnitude = toneMagnitude(autoChordAudioBlock, 1000, 3000, 440.0, 48000.0);
            if (!(autoChordRms > 0.01 && c4Magnitude > 0.005
                && e4Magnitude > 0.005 && g4Magnitude > 0.005))
            {
                std::cerr << "Generated C4/E4/G4 did not all reach the sampler audio output; RMS="
                          << autoChordRms << ", C4=" << c4Magnitude
                          << ", E4=" << e4Magnitude << ", G4=" << g4Magnitude << "\n";
                result = 1;
            }

            // Restore the original SFZ mapping before the pre-existing
            // chord loudness and transition assertions below.
            const auto restoredLoad = processor.loadSfzFile(sfz);
            if (!restoredLoad.success)
            {
                std::cerr << "Could not restore the original integration SFZ fixture.\n";
                result = 1;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(30));

            // AutoChords OFF in PATTERN must preserve a single incoming pitch.
            if (!setParameter(processor, "singleMidiNoteAsChordRoot", 0.0f))
                result = 1;
            juce::AudioBuffer<float> offBlock(2, 128);
            juce::MidiBuffer offMidi;
            offMidi.addEvent(juce::MidiMessage::allNotesOff(1), 0);
            offMidi.addEvent(juce::MidiMessage::noteOn(1, 60, static_cast<juce::uint8>(100)), 16);
            processor.processBlock(offBlock, offMidi);
            if (!processor.getAutoChordDisplayState(autoChordState)
                || autoChordState.inputNoteCount != 1 || autoChordState.noteCount != 1
                || autoChordState.generatedNotes[0] != 60 || autoChordState.autoChordApplied)
            {
                std::cerr << "AutoChords OFF did not pass through the original MIDI note.\\n";
                result = 1;
            }

            // Two simultaneous held notes are treated as a user chord, not
            // expanded into an additional AutoChord triad.
            if (!setParameter(processor, "singleMidiNoteAsChordRoot", 1.0f))
                result = 1;
            juce::AudioBuffer<float> multiBlock(2, 128);
            juce::MidiBuffer multiMidi;
            multiMidi.addEvent(juce::MidiMessage::allNotesOff(1), 0);
            multiMidi.addEvent(juce::MidiMessage::noteOn(1, 60, static_cast<juce::uint8>(100)), 16);
            multiMidi.addEvent(juce::MidiMessage::noteOn(1, 64, static_cast<juce::uint8>(100)), 16);
            processor.processBlock(multiBlock, multiMidi);
            if (!processor.getAutoChordDisplayState(autoChordState)
                || autoChordState.inputNoteCount != 2 || autoChordState.noteCount != 2
                || autoChordState.generatedNotes[0] != 60
                || autoChordState.generatedNotes[1] != 64
                || autoChordState.autoChordApplied)
            {
                std::cerr << "Multiple held keys were expanded instead of passed through.\\n";
                result = 1;
            }

            // Releasing the final held input notes must clear the UI snapshot.
            juce::AudioBuffer<float> releaseBlock(2, 128);
            juce::MidiBuffer releaseMidi;
            releaseMidi.addEvent(juce::MidiMessage::noteOff(1, 60), 16);
            releaseMidi.addEvent(juce::MidiMessage::noteOff(1, 64), 16);
            processor.processBlock(releaseBlock, releaseMidi);
            if (!processor.getAutoChordDisplayState(autoChordState)
                || autoChordState.active || autoChordState.inputNoteCount != 0
                || autoChordState.noteCount != 0)
            {
                std::cerr << "Releasing the final key did not clear AutoChords display state.\\n";
                result = 1;
            }

            // Switching to MELODY must display the original notes only, even
            // while the AutoChords parameter itself remains ON.
            if (!setParameter(processor, "playMode", 0.0f))
                result = 1;
            juce::AudioBuffer<float> melodyBlock(2, 128);
            juce::MidiBuffer melodyMidi;
            melodyMidi.addEvent(juce::MidiMessage::allNotesOff(1), 0);
            melodyMidi.addEvent(juce::MidiMessage::noteOn(1, 69, static_cast<juce::uint8>(100)), 16);
            processor.processBlock(melodyBlock, melodyMidi);
            if (!processor.getAutoChordDisplayState(autoChordState)
                || autoChordState.playMode != 0 || autoChordState.noteCount != 1
                || autoChordState.generatedNotes[0] != 69 || autoChordState.autoChordApplied)
            {
                std::cerr << "MELODY mode did not preserve one-key/one-note display.\\n";
                result = 1;
            }

            // Switching PATTERN while a MELODY key is still held must not
            // resurrect that stale input or leave the dynamic fretboard lit.
            if (!setParameter(processor, "playMode", 1.0f))
                result = 1;
            juce::AudioBuffer<float> switchBackBlock(2, 128);
            juce::MidiBuffer noSwitchMidi;
            processor.processBlock(switchBackBlock, noSwitchMidi);
            if (!processor.getAutoChordDisplayState(autoChordState)
                || autoChordState.active || autoChordState.inputNoteCount != 0
                || autoChordState.noteCount != 0)
            {
                std::cerr << "A held MELODY note survived the switch back to PATTERN.\n";
                result = 1;
            }

            // With one root still held, toggling AutoChords OFF and back ON
            // must update the generated-note snapshot without requiring a
            // fresh NoteOn event.
            if (!setParameter(processor, "singleMidiNoteAsChordRoot", 0.0f))
                result = 1;
            juce::AudioBuffer<float> toggleOffBlock(2, 128);
            juce::MidiBuffer toggleMidi;
            toggleMidi.addEvent(juce::MidiMessage::noteOn(1, 60, static_cast<juce::uint8>(100)), 16);
            processor.processBlock(toggleOffBlock, toggleMidi);
            if (!processor.getAutoChordDisplayState(autoChordState)
                || autoChordState.noteCount != 1 || autoChordState.autoChordApplied)
            {
                std::cerr << "AutoChords OFF failed to preserve the held root.\n";
                result = 1;
            }
            if (!setParameter(processor, "singleMidiNoteAsChordRoot", 1.0f))
                result = 1;
            juce::AudioBuffer<float> toggleOnBlock(2, 128);
            juce::MidiBuffer noToggleMidi;
            processor.processBlock(toggleOnBlock, noToggleMidi);
            if (!processor.getAutoChordDisplayState(autoChordState)
                || autoChordState.noteCount != 3 || !autoChordState.autoChordApplied
                || autoChordState.generatedNotes[0] != 60
                || autoChordState.generatedNotes[1] != 64
                || autoChordState.generatedNotes[2] != 67)
            {
                std::cerr << "Re-enabling AutoChords did not expand the currently held root.\n";
                result = 1;
            }
            juce::AudioBuffer<float> clearToggleBlock(2, 128);
            juce::MidiBuffer clearToggleMidi;
            clearToggleMidi.addEvent(juce::MidiMessage::allNotesOff(1), 0);
            processor.processBlock(clearToggleBlock, clearToggleMidi);
            if (!processor.getAutoChordDisplayState(autoChordState)
                || autoChordState.active || autoChordState.inputNoteCount != 0)
            {
                std::cerr << "All Notes Off did not clear the AutoChords state after a mode toggle.\n";
                result = 1;
            }

            // A fresh processor with no sample bank must remain safe and still
            // publish the input/generation state without crashing.
            {
                PopPunkGuitarUltimateAudioProcessor emptyProcessor;
                emptyProcessor.prepareToPlay(48000.0, 128);
                if (!setParameter(emptyProcessor, "playMode", 1.0f)
                    || !setParameter(emptyProcessor, "singleMidiNoteAsChordRoot", 1.0f)
                    || !setParameter(emptyProcessor, "scaleRoot", 0.0f)
                    || !setParameter(emptyProcessor, "scaleMode", 1.0f))
                    result = 1;
                juce::AudioBuffer<float> emptyBankBlock(2, 128);
                juce::MidiBuffer emptyBankMidi;
                emptyBankMidi.addEvent(juce::MidiMessage::noteOn(1, 60, static_cast<juce::uint8>(100)), 16);
                emptyProcessor.processBlock(emptyBankBlock, emptyBankMidi);
                ppgu::performance::AutoChordDisplayState emptyBankState;
                if (!emptyProcessor.getAutoChordDisplayState(emptyBankState)
                    || emptyBankState.noteCount != 3 || !emptyBankState.autoChordApplied)
                {
                    std::cerr << "AutoChords failed safely when no SFZ library was loaded.\\n";
                    result = 1;
                }
            }

            // Restore PATTERN mode before the existing transition/audio assertions.
            if (!setParameter(processor, "playMode", 1.0f))
                result = 1;

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

            // Chord B is injected at sample 5872 and strummed across the
            // next 576 samples; measure after all three voices have started,
            // before chord C replaces it at sample 8872.
            const double firstChordRms = rms(blockA, 6500, 1800);
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
