#include "PPGULibraryDiscovery.h"
#include <algorithm>
#include <cstring>
#include <set>
namespace ppgu::library
{
namespace
{
bool hasSupportedExtension(const juce::File& file, juce::String& kind)
{
    const auto extension = file.getFileExtension().toLowerCase();
    if (extension == ".wav" || extension == ".wave") { kind = "WAV_CANDIDATE"; return true; }
    if (extension == ".sfz") { kind = "SFZ_INSTRUMENT_CANDIDATE"; return true; }
    return false;
}
juce::String inspectWavContainer(const juce::File& file)
{
    juce::FileInputStream input(file);
    if (!input.openedOk()) return "READ_ERROR";
    char header[12] {};
    if (input.read(header, 12) != 12) return "INVALID_HEADER";
    const bool riff = std::memcmp(header, "RIFF", 4) == 0 || std::memcmp(header, "RIFX", 4) == 0;
    const bool wave = std::memcmp(header + 8, "WAVE", 4) == 0;
    return riff && wave ? "RIFF_WAVE_HEADER" : "INVALID_WAV_HEADER";
}
bool isSafeChild(const juce::File& child, const juce::File& root)
{
    if (child.isSymbolicLink() || !child.isAChildOf(root)) return false;
    const auto relative = child.getRelativePathFrom(root);
    return relative.isNotEmpty() && !relative.startsWith("..")
        && !relative.contains(":") && !relative.startsWith("/");
}
}
ScanReport LibraryDiscovery::scan(const juce::File& root, int maximumEntries)
{
    ScanReport report;
    report.rootPath = root.getFullPathName();
    if (!root.exists() || !root.isDirectory() || root.isSymbolicLink())
    {
        report.error = "Choose an existing local folder (symbolic-link roots are not supported).";
        return report;
    }
    maximumEntries = juce::jlimit(1, 100000, maximumEntries);
    std::vector<juce::File> pendingDirectories { root };
    std::set<juce::String> visitedDirectories;
    juce::int64 remainingHashBudget = maximumTotalHashBytes;
    while (!pendingDirectories.empty())
    {
        const auto directory = pendingDirectories.back();
        pendingDirectories.pop_back();
        if (!visitedDirectories.insert(directory.getFullPathName()).second) continue;
        juce::Array<juce::File> children;
        directory.findChildFiles(children, juce::File::findFilesAndDirectories, false, "*",
                                 juce::File::FollowSymlinks::no);
        for (const auto& child : children)
        {
            if (!isSafeChild(child, root)) continue;
            ++report.entriesVisited;
            if (report.entriesVisited > maximumEntries)
            {
                report.truncated = true;
                pendingDirectories.clear();
                break;
            }
            if (child.isDirectory()) { pendingDirectories.push_back(child); continue; }
            juce::String assetType;
            if (!hasSupportedExtension(child, assetType)) continue;
            AssetCandidate candidate;
            candidate.relativePath = child.getRelativePathFrom(root);
            candidate.assetType = assetType;
            candidate.fileBytes = child.getSize();
            candidate.containerStatus = assetType == "WAV_CANDIDATE"
                ? inspectWavContainer(child) : "SFZ_CONTENT_NOT_PARSED";
            if (candidate.fileBytes >= 0
                && candidate.fileBytes <= maximumHashBytes
                && candidate.fileBytes <= remainingHashBudget)
            {
                candidate.sha256 = juce::SHA256(child).toHexString();
                remainingHashBudget -= candidate.fileBytes;
            }
            else
            {
                candidate.sha256 = "HASH_SKIPPED_SCAN_BUDGET";
            }
            candidate.reviewStatus = "NEEDS_REVIEW";
            candidate.licenseStatus = "UNREVIEWED";
            report.candidates.push_back(std::move(candidate));
        }
    }
    std::sort(report.candidates.begin(), report.candidates.end(),
        [](const AssetCandidate& a, const AssetCandidate& b)
        { return a.relativePath.compareIgnoreCase(b.relativePath) < 0; });
    return report;
}
}
