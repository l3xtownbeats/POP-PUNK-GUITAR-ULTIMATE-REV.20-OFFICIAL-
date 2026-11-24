#include "PatternClipLoader.h"
#include <juce_cryptography/juce_cryptography.h>

#include <algorithm>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <map>
#include <set>
#include <stdexcept>

namespace ppgu::performance
{
namespace
{
using Var = juce::var;

std::string textValue(const Var& value, const char* field)
{
    if (!value.isString() || value.toString().trim().isEmpty())
        throw std::runtime_error(std::string(field) + " must be a non-empty string");
    return value.toString().trim().toStdString();
}

int intValue(const Var& value, const char* field, int minimum = 0)
{
    if ((!value.isInt() && !value.isInt64()) || value.isBool())
        throw std::runtime_error(std::string(field) + " must be an integer");
    const auto number = static_cast<int64_t>(value);
    if (number < minimum || number > 2147483647LL)
        throw std::runtime_error(std::string(field) + " is outside the permitted range");
    return static_cast<int>(number);
}

Var property(const Var& object, const char* name)
{
    if (!object.isObject() || !object.hasProperty(name))
        throw std::runtime_error(std::string("Missing manifest property: ") + name);
    return object.getProperty(name, {});
}

std::filesystem::path canonicalInside(const std::filesystem::path& root,
                                      const std::string& raw, const char* field)
{
    std::string normalized = raw;
    std::replace(normalized.begin(), normalized.end(), '\\', '/');
    const std::filesystem::path relative(normalized);
    if (relative.empty() || relative.is_absolute() || relative.has_root_name()
        || relative.has_root_directory())
        throw std::runtime_error(std::string(field) + " must be a safe relative path");
    for (const auto& component : relative)
        if (component == "." || component == "..")
            throw std::runtime_error(std::string(field) + " contains traversal components");

    std::error_code ec;
    const auto candidate = std::filesystem::canonical(root / relative, ec);
    if (ec || !std::filesystem::is_regular_file(candidate, ec) || ec)
        throw std::runtime_error(std::string(field) + " does not resolve to a packaged file");

    auto rootIt = root.begin();
    auto candidateIt = candidate.begin();
    for (; rootIt != root.end() && candidateIt != candidate.end(); ++rootIt, ++candidateIt)
        if (*rootIt != *candidateIt)
            throw std::runtime_error(std::string(field) + " resolves outside the package root");
    if (rootIt != root.end())
        throw std::runtime_error(std::string(field) + " resolves outside the package root");
    return candidate;
}

std::string sha256(const juce::File& file)
{
    return juce::SHA256(file).toHexString().toUpperCase().toStdString();
}

void verifyLicense(const Var& record, const std::filesystem::path& root,
                   const std::string& assetId)
{
    if (textValue(property(record, "license_status"), "license_status") != "LICENSE_APPROVED")
        throw std::runtime_error(assetId + ": license_status must be LICENSE_APPROVED");
    const auto license = property(record, "license");
    (void) textValue(property(license, "spdx_id"), "license.spdx_id");
    const auto url = textValue(property(license, "source_url"), "license.source_url");
    if (url.rfind("https://", 0) != 0)
        throw std::runtime_error(assetId + ": license source_url must use HTTPS");
    (void) textValue(property(license, "reviewed_by"), "license.reviewed_by");
    (void) textValue(property(license, "reviewed_at_utc"), "license.reviewed_at_utc");
    const auto evidence = canonicalInside(
        root, textValue(property(license, "evidence_path"), "license.evidence_path"),
        "license.evidence_path");
    if (std::filesystem::file_size(evidence) == 0)
        throw std::runtime_error(assetId + ": license evidence file is empty");
}

void verifyMusicalReview(const Var& record, const std::string& assetId)
{
    const auto review = property(record, "musical_review");
    if (textValue(property(review, "status"), "musical_review.status") != "APPROVED")
        throw std::runtime_error(assetId + ": musical_review must be APPROVED");
    (void) textValue(property(review, "reviewed_by"), "musical_review.reviewed_by");
    (void) textValue(property(review, "reviewed_at_utc"), "musical_review.reviewed_at_utc");
    (void) textValue(property(review, "boundary_basis"), "musical_review.boundary_basis");
}

std::unique_ptr<juce::AudioFormatReader> openPcmWav(
    juce::AudioFormatManager& formats, const std::filesystem::path& path,
    const std::string& assetId, const char* role)
{
    auto reader = std::unique_ptr<juce::AudioFormatReader>(
        formats.createReaderFor(juce::File(juce::String(path.string()))));
    if (!reader)
        throw std::runtime_error(assetId + ": cannot decode " + role + " WAV");
    auto extension = path.extension().string();
    std::transform(extension.begin(), extension.end(), extension.begin(),
                   [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
    if (extension != ".wav" || reader->numChannels < 1 || reader->numChannels > 2
        || reader->bitsPerSample < 16 || reader->bitsPerSample > 32
        || reader->usesFloatingPointData
        || reader->sampleRate < 8000.0 || reader->sampleRate > 192000.0
        || reader->lengthInSamples == 0)
        throw std::runtime_error(assetId + ": unsupported " + role + " PCM WAV format");
    return reader;
}

float monoFrame(const juce::AudioBuffer<float>& buffer, int frame)
{
    if (buffer.getNumChannels() == 1)
        return buffer.getSample(0, frame);
    return 0.5f * (buffer.getSample(0, frame) + buffer.getSample(1, frame));
}

int articulationCode(const std::string& id)
{
    // Numeric values match the existing APVTS Articulation choice order.
    if (id == "open") return 0;
    if (id == "palm_mute") return 1;
    if (id == "flageolet") return 2;
    if (id == "tremolo") return 3;
    throw std::runtime_error("Unsupported articulation_id: " + id);
}
} // namespace

PatternClipLoadResult PatternClipLoader::load(const juce::File& manifestFile)
{
    PatternClipLoadResult result;
    try
    {
        if (!manifestFile.existsAsFile())
            throw std::runtime_error("PATTERN clip manifest does not exist");
        if (manifestFile.getSize() <= 0
            || static_cast<uint64_t>(manifestFile.getSize()) > maximumManifestBytes)
            throw std::runtime_error("PATTERN clip manifest size is outside the permitted limit");

        juce::var document;
        const auto parseResult = juce::JSON::parse(manifestFile.loadFileAsString(), document);
        if (parseResult.failed() || !document.isObject())
            throw std::runtime_error("Invalid PATTERN clip JSON: " + parseResult.getErrorMessage().toStdString());
        if (intValue(property(document, "schema_version"), "schema_version") != 1)
            throw std::runtime_error("Unsupported PATTERN clip registry schema_version");

        const auto clipsVar = property(document, "clips");
        const auto* clips = clipsVar.getArray();
        if (clips == nullptr)
            throw std::runtime_error("Registry clips must be an array");
        if (clips->isEmpty())
        {
            result.empty = true;
            return result;
        }
        if (clips->size() > static_cast<int>(PatternClipSnapshot::maximumClips)
            || clips->size() > static_cast<int>(PatternClipSnapshot::maximumMappings))
            throw std::runtime_error("PATTERN registry exceeds the clip/mapping limit");

        std::error_code ec;
        const auto root = std::filesystem::canonical(
            std::filesystem::path(manifestFile.getParentDirectory().getFullPathName().toStdString()), ec);
        if (ec)
            throw std::runtime_error("Cannot canonicalize PATTERN package root");

        struct Pending { PatternClipMapping mapping; std::string rr; };
        std::vector<Pending> pending;
        pending.reserve(static_cast<std::size_t>(clips->size()));
        std::set<std::string> assetIds, rrGroups;
        auto snapshot = std::make_unique<PatternClipSnapshot>();
        snapshot->clips.reserve(static_cast<std::size_t>(clips->size()));
        snapshot->mappings.reserve(static_cast<std::size_t>(clips->size()));
        juce::AudioFormatManager formats;
        formats.registerBasicFormats();
        std::size_t totalFrames = 0;

        for (const auto& record : *clips)
        {
            if (!record.isObject())
                throw std::runtime_error("Every registry clip entry must be an object");
            const auto assetId = textValue(property(record, "asset_id"), "asset_id");
            if (!assetIds.insert(assetId).second)
                throw std::runtime_error("Duplicate asset_id: " + assetId);
            if (textValue(property(record, "kind"), "kind") != "note_event")
                throw std::runtime_error(assetId + ": kind must be note_event");

            const auto targets = property(record, "engine_targets");
            const auto* targetArray = targets.getArray();
            bool hasPatternTarget = false;
            if (targetArray != nullptr)
                for (const auto& target : *targetArray)
                    if (target.isString() && target.toString() == "PATTERN_MODE")
                        hasPatternTarget = true;
            if (!hasPatternTarget)
                throw std::runtime_error(assetId + ": engine_targets must include PATTERN_MODE");

            verifyLicense(record, root, assetId);
            verifyMusicalReview(record, assetId);

            const auto sourcePath = canonicalInside(
                root, textValue(property(record, "source_path"), "source_path"), "source_path");
            const auto sourceHash = textValue(property(record, "source_sha256"), "source_sha256");
            if (sourceHash.size() != 64 || sha256(juce::File(juce::String(sourcePath.string()))) !=
                juce::String(sourceHash).toUpperCase().toStdString())
                throw std::runtime_error(assetId + ": source WAV SHA-256 mismatch");

            const int start = intValue(property(record, "source_start_sample"), "source_start_sample");
            const int end = intValue(property(record, "source_end_sample"), "source_end_sample", 1);
            const int sampleRate = intValue(property(record, "sample_rate"), "sample_rate", 1);
            const int frameCount = intValue(property(record, "frame_count"), "frame_count", 1);
            if (end <= start || frameCount != end - start)
                throw std::runtime_error(assetId + ": invalid source range/frame_count");
            auto sourceReader = openPcmWav(formats, sourcePath, assetId, "source");
            if (sourceReader->sampleRate != sampleRate
                || static_cast<uint64_t>(end) > sourceReader->lengthInSamples)
                throw std::runtime_error(assetId + ": source WAV rate/range mismatch");

            const auto clipPath = canonicalInside(
                root, textValue(property(record, "clip_path"), "clip_path"), "clip_path");
            const auto derivedHash = textValue(property(record, "derived_sha256"), "derived_sha256");
            if (derivedHash.size() != 64 || sha256(juce::File(juce::String(clipPath.string()))) !=
                juce::String(derivedHash).toUpperCase().toStdString())
                throw std::runtime_error(assetId + ": derived clip SHA-256 mismatch");
            auto clipReader = openPcmWav(formats, clipPath, assetId, "derived clip");
            if (clipReader->sampleRate != sampleRate || clipReader->lengthInSamples != frameCount)
                throw std::runtime_error(assetId + ": derived WAV rate/frame_count mismatch");

            if (static_cast<std::size_t>(frameCount) >
                PatternClipSnapshot::maximumDecodedFrames - totalFrames)
                throw std::runtime_error("PATTERN decoded PCM frame budget exceeded");
            totalFrames += static_cast<std::size_t>(frameCount);

            // Decode in small bounded chunks. The immutable cache stores mono
            // floats; never allocate a second full-size stereo decode buffer.
            constexpr int decodeChunkFrames = 8192;
            const int decodeChannels = static_cast<int>(clipReader->numChannels);
            juce::AudioBuffer<float> decoded(decodeChannels,
                juce::jmin(decodeChunkFrames, frameCount));
            PatternClipPcm pcm;
            pcm.sampleRate = clipReader->sampleRate;
            pcm.samples.resize(static_cast<std::size_t>(frameCount));
            for (int offset = 0; offset < frameCount; offset += decodeChunkFrames)
            {
                const int chunk = juce::jmin(decodeChunkFrames, frameCount - offset);
                decoded.clear();
                if (!clipReader->read(&decoded, 0, chunk, offset, true, true))
                    throw std::runtime_error(assetId + ": failed to decode complete derived WAV");
                for (int frame = 0; frame < chunk; ++frame)
                {
                    const float sample = monoFrame(decoded, frame);
                    if (!std::isfinite(sample))
                        throw std::runtime_error(assetId + ": decoded PCM contains non-finite samples");
                    pcm.samples[static_cast<std::size_t>(offset + frame)] = sample;
                }
            }

            const auto mapping = property(record, "mapping");
            const int trigger = intValue(property(mapping, "trigger_midi_note"), "trigger_midi_note");
            const int sourceNote = intValue(property(mapping, "source_midi_note"), "source_midi_note");
            const int velocityLow = intValue(property(mapping, "velocity_min"), "velocity_min", 1);
            const int velocityHigh = intValue(property(mapping, "velocity_max"), "velocity_max", 1);
            if (trigger > 127 || sourceNote > 127 || std::abs(trigger - sourceNote) > 24
                || velocityHigh > 127 || velocityLow > velocityHigh)
                throw std::runtime_error(assetId + ": MIDI/velocity mapping out of range");
            const auto articulation = textValue(property(mapping, "articulation_id"), "articulation_id");
            const int articulationId = articulationCode(articulation);
            const auto rr = mapping.hasProperty("round_robin_group")
                ? textValue(mapping.getProperty("round_robin_group", {}), "round_robin_group")
                : std::string("RR-1");
            rrGroups.insert(rr);

            PatternClipMapping runtimeMapping;
            runtimeMapping.triggerNote = static_cast<uint16_t>(trigger);
            runtimeMapping.velocityLow = static_cast<uint8_t>(velocityLow);
            runtimeMapping.velocityHigh = static_cast<uint8_t>(velocityHigh);
            runtimeMapping.clipIndex = static_cast<uint16_t>(snapshot->clips.size());
            runtimeMapping.articulation = static_cast<uint16_t>(articulationId);
            runtimeMapping.releaseSamples = 2400;
            runtimeMapping.pitchRatio = std::pow(2.0f,
                static_cast<float>(trigger - sourceNote) / 12.0f);
            snapshot->clips.push_back(std::move(pcm));
            pending.push_back({runtimeMapping, rr});
        }

        // Sorted unique IDs are deterministic and collision-free; no hash truncation.
        std::map<std::string, uint16_t> rrIds;
        uint32_t nextId = 1;
        for (const auto& group : rrGroups)
        {
            if (nextId > 65535)
                throw std::runtime_error("Too many distinct round_robin_group values");
            rrIds.emplace(group, static_cast<uint16_t>(nextId++));
        }
        for (const auto& item : pending)
        {
            auto mapping = item.mapping;
            mapping.roundRobinGroup = rrIds.at(item.rr);
            snapshot->mappings.push_back(mapping);
        }

        if (!PatternClipRuntime::validateSnapshot(*snapshot))
            throw std::runtime_error("Decoded PATTERN snapshot failed runtime validation");
        result.ready = true;
        result.snapshot = std::move(snapshot);
    }
    catch (const std::exception& error)
    {
        result.errors.push_back(error.what());
        result.snapshot.reset();
        result.ready = false;
    }
    return result;
}
} // namespace ppgu::performance
