#include "ThemeManager.h"
#include <array>
#include <iostream>
#include <utility>
#include <vector>
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
    expect(manager.getPalette().tokens.warning == juce::Colour(0xfff2a900),
           "NEON STAGE fallback warning token matches the approved amber value");

    expect(!manager.loadFromJson({}), "empty theme JSON is rejected");
    expect(manager.getPalette().usedFallback, "empty JSON restores the safe fallback palette");
    expect(manager.getLastError().contains("empty"), "empty JSON reports a useful diagnostic");

    const auto oversizedBytes = std::string(1024 * 1024 + 1, ' ');
    const auto oversizedManifest = juce::String::fromUTF8(oversizedBytes.c_str());
    expect(!manager.loadFromJson(oversizedManifest), "oversized theme JSON is rejected before parsing");
    expect(manager.getPalette().usedFallback, "oversized JSON restores the safe fallback palette");
    expect(manager.getLastError().contains("1 MiB"), "oversized JSON reports the configured size limit");

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
            expect(artworkLoaded, id + " theme manifest and SVG artwork load"
                   + (artworkLoaded ? juce::String{} : ": " + artworkCandidate.getLastError()));
            if (artworkLoaded)
            {
                expect(artworkCandidate.getPalette().id == id, id + " artwork candidate ID matches");
                expect(artworkCandidate.getPalette().name == entry.getProperty("name", "").toString(),
                       id + " artwork candidate display name matches");
                expect(artworkCandidate.getPalette().textureArtwork.isValid(), id + " texture SVG decoded");
                expect(artworkCandidate.getPalette().bezelArtwork.isValid(), id + " bezel SVG decoded");
                expect(artworkCandidate.getPalette().crestArtwork.isValid(), id + " crest SVG decoded");
                if (id == "skin-053")
                {
                    expect(artworkCandidate.getPalette().controlsSpriteSheet.isValid(),
                           "NEON STAGE controls sprite atlas decoded");
                    expect(artworkCandidate.getPalette().metersSlidersSpriteSheet.isValid(),
                           "NEON STAGE meters/sliders atlas decoded");
                    expect(artworkCandidate.getPalette().framesPanelsSpriteSheet.isValid(),
                           "NEON STAGE frames/panels atlas decoded");
                    expect(artworkCandidate.getPalette().iconsSpriteSheet.isValid(),
                           "NEON STAGE icon atlas decoded");
                    const auto& skinOne = artworkCandidate.getPalette();
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
        const auto& p = manager.getPalette().tokens;
        const std::vector<std::pair<juce::Colour, juce::uint32>> canonicalPalette {
            { p.windowBg, 0xff08090d }, { p.panel, 0xff14161b },
            { p.panelElevated, 0xff20232b }, { p.controlBg, 0xff0e1015 },
            { p.controlFace, 0xff292d36 }, { p.controlBorder, 0xff656b76 },
            { p.textPrimary, 0xfff2f0f4 }, { p.textSecondary, 0xffb9b5bf },
            { p.textDisabled, 0xff77727d }, { p.accent, 0xffe6007e },
            { p.accentGlow, 0xff7b2c91 }, { p.danger, 0xffd7264d },
            { p.warning, 0xfff2a900 }, { p.success, 0xff55c98a },
            { p.lcdBg, 0xff08090d }, { p.lcdText, 0xfff0dce8 },
            { p.ledOn, 0xffe6007e }, { p.ledOff, 0xff38313b },
            { p.shadow, 0xff030305 }, { p.highlight, 0xffd9d7df },
            { p.lowlight, 0xff090a0e }
        };
        const std::array<const char*, 21> paletteNames {
            "window_bg", "panel", "panel_elevated", "control_bg", "control_face",
            "control_border", "text_primary", "text_secondary", "text_disabled",
            "accent", "accent_glow", "danger", "warning", "success", "lcd_bg",
            "lcd_text", "led_on", "led_off", "shadow", "highlight", "lowlight"
        };
        expect(canonicalPalette.size() == paletteNames.size(),
               "NEON STAGE canonical palette contains all 21 required tokens");
        for (size_t i = 0; i < canonicalPalette.size(); ++i)
            expect(canonicalPalette[i].first.getARGB() == canonicalPalette[i].second,
                   juce::String("NEON STAGE token matches approved graphite/magenta value: ")
                       + paletteNames[i]);
    }
    // A package that passes JSON/schema validation but references an unsafe
    // artwork path must not publish its candidate palette or discard NEON STAGE.
    auto tamperedManifest = juce::JSON::parse(neon.loadFileAsString());
    auto tamperedAssets = tamperedManifest.getProperty("assets", juce::var());
    if (auto* assetsObject = tamperedAssets.getDynamicObject())
    {
        assetsObject->setProperty("texture", "../escape.svg");
        tamperedManifest.getDynamicObject()->setProperty("assets", tamperedAssets);
        const auto tempDirectory = juce::File::getSpecialLocation(juce::File::tempDirectory)
            .getChildFile("ppgu-theme-transaction-" + juce::String(juce::Time::getMillisecondCounter()));
        const auto madeDirectory = tempDirectory.createDirectory();
        expect(madeDirectory.wasOk(), "transaction test temporary directory is created");
        const auto badManifest = tempDirectory.getChildFile("theme.json");
        expect(badManifest.replaceWithText(juce::JSON::toString(tamperedManifest)),
               "transaction test manifest is written");
        const bool badLoad = manager.loadFromFile(badManifest);
        expect(!badLoad, "unsafe artwork path rejects the complete theme candidate");
        expect(manager.getPalette().id == "skin-053"
                   && manager.getPalette().name == "NEON STAGE DEFAULT",
               "failed file load preserves the last-known-good NEON STAGE palette");
        expect(manager.getPalette().textureArtwork.isValid(),
               "failed file load preserves last-known-good decoded artwork");
        expect(manager.getLastError().isNotEmpty(),
               "failed transactional load reports a diagnostic");
        badManifest.deleteFile();
        tempDirectory.deleteRecursively();
    }
    else
    {
        expect(false, "transaction test can access manifest assets object");
    }

    const auto lastGoodId = manager.getPalette().id;
    const auto lastGoodName = manager.getPalette().name;
    const auto invalid = neon.loadFileAsString().replace("\"index\": 53", "\"index\": 54");
    expect(!manager.loadFromJson(invalid), "stable ID/index mismatch is rejected");
    expect(manager.getPalette().id == lastGoodId && manager.getPalette().name == lastGoodName,
           "invalid JSON load preserves the last-known-good theme");
    expect(manager.getPalette().textureArtwork.isValid(),
           "invalid JSON load preserves last-known-good decoded artwork");
    expect(manager.getLastError().isNotEmpty(), "invalid JSON load keeps a useful diagnostic");

    manager.resetToDefault();
    expect(manager.getPalette().usedFallback, "resetToDefault restores the canonical NEON STAGE fallback");
    expect(manager.getPalette().id == "skin-053"
               && manager.getPalette().name == "NEON STAGE DEFAULT",
           "resetToDefault restores the immutable NEON STAGE identity");
    expect(manager.getLastError().isEmpty(),
           "resetToDefault clears stale load diagnostics");

    std::cout << (failures == 0 ? "PASS" : "FAIL")
              << " — REV.20 16-theme registry and NEON STAGE runtime contract" << std::endl;
    return failures == 0 ? 0 : 1;
}
