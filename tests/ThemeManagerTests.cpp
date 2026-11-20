#include "ThemeManager.h"
#include <iostream>
#include <set>
#include <string>

namespace
{
    int failures = 0;
    void expect(bool condition, const juce::String& message)
    {
        if (!condition) { ++failures; std::cerr << "FAIL: " << message << std::endl; }
    }
}

int main()
{
    PPGUThemeManager manager;
    expect(manager.getPalette().id == "skin-053", "fallback stable ID is canonical SKIN-1");
    expect(manager.getPalette().name == "NEON STAGE DEFAULT", "fallback name is NEON STAGE DEFAULT");
    expect(manager.getPalette().usedFallback, "default palette is safe fallback until manifest load");

    const auto root = juce::File::getCurrentWorkingDirectory();
    const auto skinRoot = root.getChildFile("SKIN");
    const auto registry = juce::JSON::parse(skinRoot.getChildFile("theme_manifest.json").loadFileAsString());
    const auto* themes = registry.getProperty("themes", juce::var()).getArray();
    const auto total = registry.getProperty("totalSkins", juce::var());
    expect(registry.isObject(), "REV.20 registry is a JSON object");
    expect(themes != nullptr, "REV.20 registry has a themes array");
    expect((total.isInt() || total.isInt64()) && total.toString().getLargeIntValue() == 16,
           "product contains exactly 16 logical themes");
    expect(registry.getProperty("defaultStableId", "").toString() == "skin-053",
           "SKIN-1 maps to immutable NEON STAGE ID");

    std::set<int> ordinals, indices;
    std::set<std::string> ids;
    int runtimeReadyCount = 0;
    if (themes != nullptr)
    {
        expect(themes->size() == 16, "registry contains exactly 16 entries");
        for (const auto& entry : *themes)
        {
            if (!entry.isObject()) { expect(false, "entry must be an object"); continue; }
            const auto ordinalValue = entry.getProperty("ordinal", juce::var());
            const auto indexValue = entry.getProperty("index", juce::var());
            const auto id = entry.getProperty("id", "").toString();
            const auto path = entry.getProperty("path", "").toString();
            const bool ready = static_cast<bool>(entry.getProperty("runtimeReady", false));
            expect(ordinalValue.isInt() || ordinalValue.isInt64(), id + " has logical ordinal");
            expect(indexValue.isInt() || indexValue.isInt64(), id + " has immutable index");
            expect(path.startsWith("Skin_") && path.endsWith("/theme.json"), id + " has safe manifest path");
            if ((!ordinalValue.isInt() && !ordinalValue.isInt64())
                || (!indexValue.isInt() && !indexValue.isInt64())) continue;
            const int ordinal = static_cast<int>(ordinalValue.toString().getLargeIntValue());
            const int index = static_cast<int>(indexValue.toString().getLargeIntValue());
            const auto expectedId = juce::String("skin-") + juce::String(index);
            expect(ordinal >= 1 && ordinal <= 16, id + " logical ordinal is valid");
            expect(id == expectedId, id + " stable ID/index mapping is preserved");
            expect(ordinals.insert(ordinal).second, id + " ordinal is unique");
            expect(indices.insert(index).second, id + " index is unique");
            expect(ids.insert(id.toStdString()).second, id + " ID is unique");
            const auto manifest = skinRoot.getChildFile(path);
            expect(manifest.existsAsFile(), id + " design manifest is preserved");
            if (ready)
            {
                ++runtimeReadyCount;
                const bool loaded = manifest.existsAsFile() && manager.loadFromFile(manifest);
                expect(loaded, id + " runtime-ready manifest loads"
                       + (loaded ? juce::String{} : ": " + manager.getLastError()));
                if (loaded)
                {
                    expect(manager.getPalette().id == id, id + " loaded ID matches registry");
                    expect(!manager.getPalette().usedFallback, id + " uses validated palette");
                }
            }
            else
            {
                // Artwork may be complete while the theme remains gated from runtime selection.
                expect(manifest.getChildFile("assets/preview.png").existsAsFile(),
                       id + " preview artwork is present while runtime remains gated");
                expect(manifest.getChildFile("assets/hero.png").existsAsFile(),
                       id + " hero artwork is present while runtime remains gated");
                expect(entry.getProperty("runtimeReady", true) == false,
                       id + " is not selectable before REV.20 runtime acceptance");
            }
        }
    }
    expect(ordinals.size() == 16, "all 16 logical ordinals are present");
    expect(runtimeReadyCount == 1, "only SKIN-1 is currently runtime-ready");

    const auto neon = skinRoot.getChildFile("Skin_053").getChildFile("theme.json");
    const bool loaded = neon.existsAsFile() && manager.loadFromFile(neon);
    expect(loaded, "NEON STAGE DEFAULT manifest loads"
           + (loaded ? juce::String{} : ": " + manager.getLastError()));
    if (loaded)
    {
        expect(manager.getPalette().id == "skin-053", "NEON STAGE stable ID stays skin-053");
        expect(manager.getPalette().name == "NEON STAGE DEFAULT", "NEON STAGE name is canonical");
        expect(manager.getPalette().tokens.windowBg == juce::Colour(0xff080b14),
               "NEON STAGE palette is canonical");
    }
    const auto invalid = neon.loadFileAsString().replace("\"index\": 53", "\"index\": 54");
    expect(!manager.loadFromJson(invalid), "stable ID/index mismatch is rejected");
    expect(manager.getPalette().usedFallback, "invalid theme restores safe fallback");
    std::cout << (failures == 0 ? "PASS" : "FAIL")
              << " — REV.20 16-theme registry and NEON STAGE runtime contract" << std::endl;
    return failures == 0 ? 0 : 1;
}
