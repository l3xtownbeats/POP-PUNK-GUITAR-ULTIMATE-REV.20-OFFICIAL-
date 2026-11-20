#include "PPGULibraryDiscovery.h"
#include <iostream>
namespace
{
bool writeWavHeader(const juce::File& file)
{
    const char header[12] { 'R','I','F','F',0,0,0,0,'W','A','V','E' };
    return file.replaceWithData(header, sizeof(header));
}
bool expect(bool value, const char* message)
{
    if (!value) std::cerr << message << "\n";
    return value;
}
}
int main()
{
    auto root = juce::File::createTempFile("ppgu-library-discovery").getSiblingFile(
        "ppgu-library-discovery-" + juce::Uuid().toString());
    if (!root.createDirectory()) { std::cerr << "Could not create temporary root.\n"; return 1; }
    bool ok = true;
    const auto nested = root.getChildFile("nested");
    ok = expect(nested.createDirectory(), "Could not create nested folder.") && ok;
    const auto wav = root.getChildFile("guitar-note.wav");
    const auto sfz = nested.getChildFile("guitar.sfz");
    const auto ignored = root.getChildFile("readme.txt");
    ok = expect(writeWavHeader(wav), "Could not create WAV fixture.") && ok;
    ok = expect(sfz.replaceWithText("<region> sample=note.wav key=60\n"), "Could not create SFZ fixture.") && ok;
    ok = expect(ignored.replaceWithText("not a sample"), "Could not create ignored fixture.") && ok;
    const auto hashBefore = juce::SHA256(wav).toHexString();
    const auto report = ppgu::library::LibraryDiscovery::scan(root);
    ok = expect(report.error.isEmpty(), "Valid folder scan unexpectedly failed.") && ok;
    ok = expect(report.candidates.size() == 2, "Expected one WAV and one SFZ candidate.") && ok;
    ok = expect(!report.truncated, "Small scan should not be truncated.") && ok;
    ok = expect(juce::SHA256(wav).toHexString() == hashBefore, "WAV changed during read-only scan.") && ok;
    ok = expect(wav.existsAsFile() && sfz.existsAsFile() && ignored.existsAsFile(), "Source files must remain.") && ok;
    if (report.candidates.size() == 2)
    {
        for (const auto& item : report.candidates)
        {
            ok = expect(!item.relativePath.startsWith("/") && !item.relativePath.contains(":"),
                        "Candidate path must be relative.") && ok;
            ok = expect(item.reviewStatus == "NEEDS_REVIEW", "Candidate must need review.") && ok;
            ok = expect(item.licenseStatus == "UNREVIEWED", "Licence must stay unreviewed.") && ok;
            ok = expect(item.sha256.length() == 64, "Candidate SHA-256 missing.") && ok;
        }
        ok = expect(report.candidates[0].relativePath.compareIgnoreCase(report.candidates[1].relativePath) < 0,
                    "Candidate list must be sorted.") && ok;
    }
    const auto limited = ppgu::library::LibraryDiscovery::scan(root, 1);
    ok = expect(limited.truncated, "Entry limit must flag incomplete inventory.") && ok;
    ok = expect(limited.candidates.size() <= 1, "Entry limit must bound candidate count.") && ok;
    const auto invalid = ppgu::library::LibraryDiscovery::scan(root.getChildFile("missing"));
    ok = expect(invalid.error.isNotEmpty() && invalid.candidates.empty(), "Missing root must report an error.") && ok;
    root.deleteRecursively();
    if (ok) std::cout << "Library discovery read-only contract tests passed.\n";
    return ok ? 0 : 1;
}
