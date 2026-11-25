#pragma once

#include "PatternClipRuntime.h"
#include <JuceHeader.h>
#include <memory>
#include <string>
#include <vector>

namespace ppgu::performance
{
struct PatternClipLoadResult
{
    std::unique_ptr<PatternClipSnapshot> snapshot;
    std::vector<std::string> errors;
    bool ready = false;
    bool empty = false;
};

// Performs JSON, path, SHA-256, license-evidence and WAV decoding work on
// the caller's control/worker thread. Never call from processBlock().
class PatternClipLoader final
{
public:
    static constexpr std::size_t maximumManifestBytes = 2U * 1024U * 1024U;
    static constexpr std::size_t maximumDecodedBytes =
        PatternClipSnapshot::maximumDecodedFrames * sizeof(float);

    [[nodiscard]] static PatternClipLoadResult load(const juce::File& manifestFile);
};
} // namespace ppgu::performance
