#pragma once
#include <JuceHeader.h>
#include <vector>
namespace ppgu::library
{
struct AssetCandidate
{
    juce::String relativePath, assetType, sha256, containerStatus;
    juce::int64 fileBytes = 0;
    juce::String reviewStatus { "NEEDS_REVIEW" };
    juce::String licenseStatus { "UNREVIEWED" };
};
struct ScanReport
{
    juce::String rootPath;
    std::vector<AssetCandidate> candidates;
    juce::int64 entriesVisited = 0;
    bool truncated = false;
    juce::String error;
};
class LibraryDiscovery final
{
public:
    static constexpr int defaultEntryLimit = 5000;
    static constexpr juce::int64 maximumHashBytes = 1024LL * 1024LL * 1024LL;
    static ScanReport scan(const juce::File& root, int maximumEntries = defaultEntryLimit);
};
}
