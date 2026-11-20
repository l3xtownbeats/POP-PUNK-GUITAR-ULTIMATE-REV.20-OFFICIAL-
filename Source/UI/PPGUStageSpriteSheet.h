#pragma once

#include <juce_graphics/juce_graphics.h>
#include <vector>

/**
 * Safe in-memory sprite-sheet slicing for editor artwork.
 * Call only from the UI/control thread after the source image has been decoded.
 * Source alpha is preserved; no luminance keying or destructive conversion occurs.
 */
class PPGUStageSpriteSheet final
{
public:
    static bool isValidRegion(const juce::Image& image, int x, int y,
                              int width, int height) noexcept;

    static std::vector<juce::Image> sliceHorizontal(const juce::Image& image,
        int frameWidth, int frameHeight, int totalFrames,
        int yOffset = 0, int xOffset = 0);

    static std::vector<juce::Image> sliceGrid(const juce::Image& image,
        int cellWidth, int cellHeight, int columns, int rows,
        int startX = 0, int startY = 0);
};
