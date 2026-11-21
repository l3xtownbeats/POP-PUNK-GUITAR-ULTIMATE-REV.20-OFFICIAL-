#pragma once

#include <JuceHeader.h>
#include <map>
#include <string>

// Runtime contract for visual-only themes. The manager is intentionally isolated
// from PluginProcessor, APVTS, DSP, sampler and scheduler code.
class PPGUThemeManager final
{
public:
    struct Palette
    {
        struct Tokens
        {
            juce::Colour windowBg { 0xff08090d };
            juce::Colour panel { 0xff14161b };
            juce::Colour panelElevated { 0xff20232b };
            juce::Colour controlBg { 0xff0e1015 };
            juce::Colour controlFace { 0xff292d36 };
            juce::Colour controlBorder { 0xff656b76 };
            juce::Colour textPrimary { 0xfff2f0f4 };
            juce::Colour textSecondary { 0xffb9b5bf };
            juce::Colour textDisabled { 0xff77727d };
            juce::Colour accent { 0xffe6007e };
            juce::Colour accentGlow { 0xff7b2c91 };
            juce::Colour danger { 0xffd7264d };
            juce::Colour warning { 0xffffbe55 };
            juce::Colour success { 0xff55c98a };
            juce::Colour lcdBg { 0xff08090d };
            juce::Colour lcdText { 0xfff0dce8 };
            juce::Colour ledOn { 0xffe6007e };
            juce::Colour ledOff { 0xff38313b };
            juce::Colour shadow { 0xff030305 };
            juce::Colour highlight { 0xffd9d7df };
            juce::Colour lowlight { 0xff090a0e };
        };

        juce::String id { "skin-053" };
        juce::String name { "NEON STAGE DEFAULT" };
        juce::String uiTypeface { "Segoe UI" };
        juce::String displayTypeface { "Consolas" };
        juce::String typographyWeight { "semibold" };
        float fontScale = 1.0f;
        float letterSpacing = 0.35f;
        Tokens tokens;
        // Decoded on the UI/message thread from the active theme's local SVG assets.
        // juce::Image is reference-counted, so Palette copies share the same pixels.
        juce::Image textureArtwork;
        juce::Image bezelArtwork;
        juce::Image crestArtwork;
        // High-resolution Skin-1 stage stack. These images are decoded only while
        // the visual theme is loaded on the message thread; audio code never sees them.
        juce::Image backgroundArtwork;
        juce::Image materialArtwork;
        juce::Image stageGlowArtwork;
        juce::Image edgeHighlightArtwork;
        juce::Image specularArtwork;
        juce::Image shadowArtwork;
        // Optional NEON STAGE sprite atlases. Only SKIN-1 supplies these;
        // other approved themes continue using the shared vector fallback.
        juce::Image controlsSpriteSheet;
        juce::Image metersSlidersSpriteSheet;
        juce::Image framesPanelsSpriteSheet;
        juce::Image iconsSpriteSheet;
        // Skin-1 authored state images are decoded on the UI thread and cached
        // at 128px to keep the editor's resident artwork footprint bounded.
        std::map<std::string, juce::Image> controlStateArtwork;
        const juce::Image* findControlArtwork(const juce::String& controlId,
                                              const juce::String& state) const
        {
            const auto key = (controlId + "|" + state).toStdString();
            const auto found = controlStateArtwork.find(key);
            return found != controlStateArtwork.end() ? &found->second : nullptr;
        }
        // Compatibility aliases used by the existing editor shell.
        juce::Colour canvas { 0xff08090d };
        juce::Colour canvasInset { 0xff0e1015 };
        juce::Colour surface { 0xff14161b };
        juce::Colour surfaceSecondary { 0xff0e1015 };
        juce::Colour surfaceRaised { 0xff20232b };
        juce::Colour text { 0xfff2f0f4 };
        juce::Colour textSecondary { 0xffb9b5bf };
        juce::Colour accent { 0xffe6007e };
        juce::Colour accentSecondary { 0xff7b2c91 };
        juce::Colour border { 0xff656b76 };
        juce::Colour focus { 0xffd9d7df };
        bool usedFallback = true;

        juce::Colour token(const juce::String& name) const noexcept;
    };

    PPGUThemeManager() = default;

    // Parsing and file access are UI/control-thread operations only.
    // A failed load always restores the canonical NEON STAGE DEFAULT palette.
    bool loadFromJson(const juce::String& jsonText);
    bool loadFromFile(const juce::File& manifestFile);
    void resetToDefault() noexcept;

    const Palette& getPalette() const noexcept { return activePalette; }
    juce::String getLastError() const { return lastError; }

private:
    static bool readColour(const juce::var& object, const juce::Identifier& key,
                           juce::Colour& destination);
    static bool validateManifest(const juce::var& root, Palette& palette,
                                 juce::String& error);

    Palette activePalette;
    juce::String lastError;
};
