#pragma once

#include <JuceHeader.h>

/**
 * Visual-only state mapping for Skin-1 authored control artwork.
 *
 * Skin-1 runtime manifests use: default, hover, pressed, disabled, dragged.
 * Active toggles ask for an optional "active" image; the current Skin-1 pack
 * has no separate active PNG, so the LookAndFeel falls back to its ON atlas.
 * The APVTS toggle itself remains the source of truth for the parameter.
 */
enum class PPGUArtworkState
{
    Normal,
    Hover,
    Pressed,
    Active,
    Disabled,
    Dragged
};

inline juce::String ppguArtworkStateName(PPGUArtworkState state)
{
    switch (state)
    {
        case PPGUArtworkState::Hover:    return "hover";
        case PPGUArtworkState::Pressed:  return "pressed";
        case PPGUArtworkState::Active:   return "active";
        case PPGUArtworkState::Disabled: return "disabled";
        case PPGUArtworkState::Dragged:  return "dragged";
        case PPGUArtworkState::Normal:   return "default";
    }
    return "default";
}

inline juce::String ppguSliderArtworkState(const juce::Slider& slider)
{
    if (! slider.isEnabled())
        return ppguArtworkStateName(PPGUArtworkState::Disabled);
    if (slider.isMouseButtonDown())
        return ppguArtworkStateName(PPGUArtworkState::Dragged);
    if (slider.isMouseOverOrDragging())
        return ppguArtworkStateName(PPGUArtworkState::Hover);
    return ppguArtworkStateName(PPGUArtworkState::Normal);
}

inline juce::String ppguButtonArtworkState(const juce::Button& button,
                                           bool hovered, bool pressed)
{
    if (! button.isEnabled())
        return ppguArtworkStateName(PPGUArtworkState::Disabled);
    if (pressed)
        return ppguArtworkStateName(PPGUArtworkState::Pressed);
    if (button.getToggleState())
        return ppguArtworkStateName(PPGUArtworkState::Active);
    if (hovered)
        return ppguArtworkStateName(PPGUArtworkState::Hover);
    return ppguArtworkStateName(PPGUArtworkState::Normal);
}
