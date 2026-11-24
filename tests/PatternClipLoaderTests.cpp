#include "PatternClipLoader.h"

#include <iostream>

int main()
{
    const auto directory = juce::File::getSpecialLocation(juce::File::tempDirectory)
        .getChildFile("ppgu_pattern_clip_loader_contract");
    directory.deleteRecursively();
    if (!directory.createDirectory())
        return 1;

    const auto manifest = directory.getChildFile("pattern_clips.json");
    if (!manifest.replaceWithText("{\"schema_version\":1,\"clips\":[]}"))
        return 1;
    const auto empty = ppgu::performance::PatternClipLoader::load(manifest);
    if (!empty.empty || empty.ready || empty.snapshot != nullptr || !empty.errors.empty())
    {
        std::cerr << "Empty registry must be valid but not READY.\n";
        directory.deleteRecursively();
        return 1;
    }

    if (!manifest.replaceWithText("{ malformed json"))
        return 1;
    const auto malformed = ppgu::performance::PatternClipLoader::load(manifest);
    if (malformed.ready || malformed.empty || malformed.snapshot != nullptr || malformed.errors.empty())
    {
        std::cerr << "Malformed JSON was not rejected fail-closed.\n";
        directory.deleteRecursively();
        return 1;
    }

    directory.deleteRecursively();
    std::cout << "PATTERN clip loader contract tests passed.\n";
    return 0;
}
