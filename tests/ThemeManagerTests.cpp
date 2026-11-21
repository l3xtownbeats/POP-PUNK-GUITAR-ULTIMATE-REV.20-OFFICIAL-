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
    juce::ScopedJuceInitialiser_GUI juceInitialiser;
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
            const auto expectedId = juce::String("skin-") + juce::String(index).paddedLeft('0', 3);
            expect(ordinal >= 1 && ordinal <= 16, id + " logical ordinal is valid");
            expect(id == expectedId, id + " stable ID/index mapping is preserved");
            expect(ordinals.insert(ordinal).second, id + " ordinal is unique");
            expect(indices.insert(index).second, id + " index is unique");
            expect(ids.insert(id.toStdString()).second, id + " ID is unique");
            const auto manifest = skinRoot.getChildFile(path);
            expect(manifest.existsAsFile(), id + " design manifest is preserved");

            // Every approved skin must load its palette and decode all local SVG
            // artwork layers, even while a release/host gate remains pending.
            PPGUThemeManager artworkCandidate;
            const bool artworkLoaded = manifest.existsAsFile() && artworkCandidate.loadFromFile(manifest);
            expect(artworkLoaded, id + " theme manifest and local artwork load"
                   + (artworkLoaded ? juce::String{} : ": " + artworkCandidate.getLastError()));
            if (artworkLoaded)
            {
                expect(artworkCandidate.getPalette().id == id, id + " artwork candidate ID matches");
                expect(artworkCandidate.getPalette().name == entry.getProperty("name", "").toString(),
                       id + " artwork candidate display name matches");
                expect(artworkCandidate.getPalette().textureArtwork.isValid(), id + " texture artwork decoded");
                expect(artworkCandidate.getPalette().bezelArtwork.isValid(), id + " bezel artwork decoded");
                expect(artworkCandidate.getPalette().crestArtwork.isValid(), id + " crest artwork decoded");
                if (id == "skin-053")
                {
                    const auto& skinOne = artworkCandidate.getPalette();
                    expect(!skinOne.controlsSpriteSheet.isValid(),
                           "Legacy prototype controls atlas is not loaded");
                    expect(!skinOne.metersSlidersSpriteSheet.isValid(),
                           "Legacy prototype meters/sliders atlas is not loaded");
                    expect(!skinOne.framesPanelsSpriteSheet.isValid(),
                           "Legacy prototype frames/panels atlas is not loaded");
                    expect(!skinOne.iconsSpriteSheet.isValid(),
                           "Legacy prototype icon atlas is not loaded");
                    expect(skinOne.controlStateArtwork.size() == 135,
                           "All 27 controls decode their five individually authored runtime states");
                    expect(skinOne.findControlArtwork("knob01", "default") != nullptr,
                           "Main rotary artwork is available by control ID/state");
                    expect(skinOne.findControlArtwork("fx_switch07", "pressed") != nullptr,
                           "Seventh main FX switch artwork is available by control ID/state");
                    expect(skinOne.findControlArtwork("Import_Guitar", "hover") != nullptr,
                           "Import Guitar header artwork is available by control ID/state");
                    expect(skinOne.findControlArtwork("About", "disabled") != nullptr,
                           "Disabled About artwork is available by control ID/state");
                    expect(skinOne.heroArtwork.isValid()
                               && skinOne.heroArtwork.getWidth() == 800
                               && skinOne.heroArtwork.getHeight() == 450,
                           "NEON STAGE hero PNG decoded; visual reference parity remains a separate acceptance gate");
                    expect(skinOne.backgroundArtwork.isValid()
                               && skinOne.backgroundArtwork.getWidth() == 2560
                               && skinOne.backgroundArtwork.getHeight() == 1440,
                           "NEON STAGE 2560x1440 premium background decoded");
                    expect(skinOne.materialArtwork.isValid()
                               && skinOne.materialArtwork.getWidth() == 1024
                               && skinOne.materialArtwork.getHeight() == 1024,
                           "NEON STAGE 1024x1024 material texture decoded");
                    expect(skinOne.stageGlowArtwork.isValid()
                               && skinOne.stageGlowArtwork.getWidth() == 800
                               && skinOne.stageGlowArtwork.getHeight() == 450,
                           "NEON STAGE stage-glow layer decoded");
                    expect(skinOne.edgeHighlightArtwork.isValid()
                               && skinOne.edgeHighlightArtwork.getWidth() == 800
                               && skinOne.edgeHighlightArtwork.getHeight() == 450,
                           "NEON STAGE edge-highlight layer decoded");
                    expect(skinOne.specularArtwork.isValid()
                               && skinOne.specularArtwork.getWidth() == 800
                               && skinOne.specularArtwork.getHeight() == 450,
                           "NEON STAGE specular layer decoded");
                    expect(skinOne.shadowArtwork.isValid()
                               && skinOne.shadowArtwork.getWidth() == 800
                               && skinOne.shadowArtwork.getHeight() == 450,
                           "NEON STAGE shadow layer decoded");
                }
            }

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
                expect(manifest.getParentDirectory().getChildFile("assets/preview.png").existsAsFile(),
                       id + " preview artwork is present while runtime remains gated");
                expect(manifest.getParentDirectory().getChildFile("assets/hero.png").existsAsFile(),
                       id + " hero artwork is present while runtime remains gated");
                expect(!static_cast<bool>(entry.getProperty("runtimeReady", true)),
                       id + " is not selectable before REV.20 runtime acceptance");
            }
        }
    }
    expect(ordinals.size() == 16, "all 16 logical ordinals are present");
    expect(runtimeReadyCount == 16, "all 16 approved skins are runtime-ready after exact-SHA REV.20 validation");

    const auto neon = skinRoot.getChildFile("Skin_053").getChildFile("theme.json");
    const bool loaded = neon.existsAsFile() && manager.loadFromFile(neon);
    expect(loaded, "NEON STAGE DEFAULT manifest loads"
           + (loaded ? juce::String{} : ": " + manager.getLastError()));
    if (loaded)
    {
        expect(manager.getPalette().id == "skin-053", "NEON STAGE stable ID stays skin-053");
        expect(manager.getPalette().name == "NEON STAGE DEFAULT", "NEON STAGE name is canonical");
        expect(manager.getPalette().tokens.windowBg == juce::Colour(0xff080b14),
               "NEON STAGE graphite background is canonical");
        expect(manager.getPalette().tokens.accent == juce::Colour(0xff00d9ff),
               "NEON STAGE primary accent is cyan");
        expect(manager.getPalette().tokens.accentGlow == juce::Colour(0xff6b8cff),
               "NEON STAGE secondary accent is electric blue");
    }
    const auto invalid = neon.loadFileAsString().replace("\"index\": 53", "\"index\": 54");
    expect(!manager.loadFromJson(invalid), "stable ID/index mismatch is rejected");
    expect(manager.getPalette().usedFallback, "invalid theme restores safe fallback");
    std::cout << (failures == 0 ? "PASS" : "FAIL")
              << " — REV.20 16-theme registry and NEON STAGE runtime contract" << std::endl;
    return failures == 0 ? 0 : 1;
}
