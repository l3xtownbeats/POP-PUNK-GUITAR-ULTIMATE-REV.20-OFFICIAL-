#include "PatternClipLoader.h"
#include <juce_core/juce_core.h>

#include <iostream>
#include <cmath>
#include <string>
#include <memory>

namespace
{
bool writeFixtureWav(const juce::File& file)
{
    juce::WavAudioFormat wav;
    auto stream = file.createOutputStream();
    if (!stream)
        return false;
    std::unique_ptr<juce::AudioFormatWriter> writer(
        wav.createWriterFor(std::move(stream), 48000.0, 1, 16, {}, 0));
    if (!writer)
        return false;

    juce::AudioBuffer<float> samples(1, 480);
    for (int i = 0; i < samples.getNumSamples(); ++i)
        samples.setSample(0, i, 0.2f * std::sin(juce::MathConstants<float>::twoPi
            * 440.0f * static_cast<float>(i) / 48000.0f));
    return writer->writeFromAudioSampleBuffer(samples, 0, samples.getNumSamples());
}

juce::String digest(const juce::File& file)
{
    return juce::SHA256(file).toHexString().toUpperCase();
}

juce::String makeManifest(const juce::String& sourceHash,
                          const juce::String& clipHash,
                          const juce::String& clipPath = "clips/fixture.wav",
                          const juce::String& licenseStatus = "LICENSE_APPROVED")
{
    return "{"
        "\"schema_version\":1,"
        "\"clips\":[{"
        "\"asset_id\":\"LOADER-TEST-001\","
        "\"kind\":\"note_event\","
        "\"engine_targets\":[\"PATTERN_MODE\"],"
        "\"source_path\":\"sources/source.wav\","
        "\"source_sha256\":\"" + sourceHash + "\","
        "\"source_start_sample\":0,"
        "\"source_end_sample\":480,"
        "\"sample_rate\":48000,"
        "\"frame_count\":480,"
        "\"clip_path\":\"" + clipPath + "\","
        "\"derived_sha256\":\"" + clipHash + "\","
        "\"license_status\":\"" + licenseStatus + "\","
        "\"license\":{"
        "\"spdx_id\":\"CC0-1.0\","
        "\"source_url\":\"https://example.org/audio\","
        "\"evidence_path\":\"licenses/CC0.txt\","
        "\"reviewed_by\":\"automated fixture\","
        "\"reviewed_at_utc\":\"2026-11-24T00:00:00Z\"},"
        "\"musical_review\":{"
        "\"status\":\"APPROVED\","
        "\"reviewed_by\":\"automated fixture\","
        "\"reviewed_at_utc\":\"2026-11-24T00:00:00Z\","
        "\"boundary_basis\":\"test fixture exact frame range\"},"
        "\"mapping\":{"
        "\"trigger_midi_note\":60,"
        "\"source_midi_note\":60,"
        "\"articulation_id\":\"open\","
        "\"velocity_min\":1,"
        "\"velocity_max\":127,"
        "\"round_robin_group\":\"RR-A\"}}]}";
}
}

int main()
{
    const auto directory = juce::File::getSpecialLocation(juce::File::tempDirectory)
        .getChildFile("ppgu_pattern_clip_loader_contract");
    directory.deleteRecursively();
    if (!directory.createDirectory())
        return 1;

    const auto sources = directory.getChildFile("sources");
    const auto clips = directory.getChildFile("clips");
    const auto licenses = directory.getChildFile("licenses");
    if (!sources.createDirectory() || !clips.createDirectory() || !licenses.createDirectory())
        return 1;

    const auto source = sources.getChildFile("source.wav");
    const auto clip = clips.getChildFile("fixture.wav");
    const auto evidence = licenses.getChildFile("CC0.txt");
    const auto manifest = directory.getChildFile("pattern_clips.json");
    if (!writeFixtureWav(source) || !writeFixtureWav(clip)
        || !evidence.replaceWithText("Synthetic test-only license evidence"))
    {
        directory.deleteRecursively();
        return 1;
    }

    const auto sourceHash = digest(source);
    const auto clipHash = digest(clip);
    if (!manifest.replaceWithText(makeManifest(sourceHash, clipHash)))
        return 1;

    const auto valid = ppgu::performance::PatternClipLoader::load(manifest);
    if (!valid.ready || valid.empty || !valid.snapshot
        || valid.snapshot->clips.size() != 1 || valid.snapshot->mappings.size() != 1
        || valid.snapshot->mappings.front().triggerNote != 60
        || valid.snapshot->mappings.front().pitchRatio != 1.0f)
    {
        std::cerr << "Valid synthetic package was not loaded into an immutable snapshot.\n";
        directory.deleteRecursively();
        return 1;
    }

    if (!manifest.replaceWithText(makeManifest(juce::String(std::string(64, 'B')), clipHash)))
        return 1;
    const auto badHash = ppgu::performance::PatternClipLoader::load(manifest);
    if (badHash.ready || badHash.snapshot || badHash.errors.empty())
    {
        std::cerr << "Source SHA-256 mismatch was not rejected fail-closed.\n";
        directory.deleteRecursively();
        return 1;
    }

    if (!manifest.replaceWithText(makeManifest(sourceHash, clipHash, "../fixture.wav")))
        return 1;
    const auto traversal = ppgu::performance::PatternClipLoader::load(manifest);
    if (traversal.ready || traversal.snapshot || traversal.errors.empty())
    {
        std::cerr << "Path traversal was not rejected fail-closed.\n";
        directory.deleteRecursively();
        return 1;
    }

    if (!manifest.replaceWithText(makeManifest(sourceHash, clipHash,
                                               "clips/fixture.wav", "UNREVIEWED")))
        return 1;
    const auto unlicensed = ppgu::performance::PatternClipLoader::load(manifest);
    if (unlicensed.ready || unlicensed.snapshot || unlicensed.errors.empty())
    {
        std::cerr << "Unapproved license status was not rejected fail-closed.\n";
        directory.deleteRecursively();
        return 1;
    }

    if (!manifest.replaceWithText("{\"schema_version\":1,\"clips\":[]}"))
        return 1;
    const auto empty = ppgu::performance::PatternClipLoader::load(manifest);
    if (!empty.empty || empty.ready || empty.snapshot || !empty.errors.empty())
    {
        std::cerr << "Empty registry must be valid but not READY.\n";
        directory.deleteRecursively();
        return 1;
    }

    if (!manifest.replaceWithText("{ malformed json"))
        return 1;
    const auto malformed = ppgu::performance::PatternClipLoader::load(manifest);
    if (malformed.ready || malformed.empty || malformed.snapshot || malformed.errors.empty())
    {
        std::cerr << "Malformed JSON was not rejected fail-closed.\n";
        directory.deleteRecursively();
        return 1;
    }

    directory.deleteRecursively();
    std::cout << "PATTERN clip loader contract tests passed.\n";
    return 0;
}
