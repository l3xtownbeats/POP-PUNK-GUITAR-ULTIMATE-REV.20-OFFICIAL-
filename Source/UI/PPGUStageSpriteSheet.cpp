#include "PPGUStageSpriteSheet.h"

namespace
{
juce::Image copyRegionPreservingAlpha(const juce::Image& source,
                                      int x, int y, int width, int height)
{
    // Copy pixels explicitly instead of returning a clipped/shared image.
    // This keeps the source alpha channel intact across JUCE 7 and JUCE 9.
    juce::Image frame(source.getFormat(), width, height, true);
    for (int row = 0; row < height; ++row)
        for (int column = 0; column < width; ++column)
            frame.setPixelAt(column, row, source.getPixelAt(x + column, y + row));
    return frame;
}
}

bool PPGUStageSpriteSheet::isValidRegion(const juce::Image& image, int x, int y,
                                         int width, int height) noexcept
{
    return image.isValid() && x >= 0 && y >= 0 && width > 0 && height > 0
        && x <= image.getWidth() - width
        && y <= image.getHeight() - height;
}

std::vector<juce::Image> PPGUStageSpriteSheet::sliceHorizontal(
    const juce::Image& image, int frameWidth, int frameHeight, int totalFrames,
    int yOffset, int xOffset)
{
    std::vector<juce::Image> frames;
    if (! image.isValid() || frameWidth <= 0 || frameHeight <= 0
        || totalFrames <= 0 || xOffset < 0 || yOffset < 0
        || frameWidth > image.getWidth() || frameHeight > image.getHeight())
        return frames;

    const auto available = (image.getWidth() - xOffset) / frameWidth;
    if (xOffset >= image.getWidth() || yOffset > image.getHeight() - frameHeight
        || totalFrames > available)
        return frames;

    frames.reserve(static_cast<size_t>(totalFrames));
    for (int index = 0; index < totalFrames; ++index)
    {
        const int x = xOffset + index * frameWidth;
        if (! isValidRegion(image, x, yOffset, frameWidth, frameHeight))
        {
            frames.clear();
            return frames;
        }
        frames.push_back(copyRegionPreservingAlpha(image, x, yOffset, frameWidth, frameHeight));
    }
    return frames;
}

std::vector<juce::Image> PPGUStageSpriteSheet::sliceGrid(
    const juce::Image& image, int cellWidth, int cellHeight, int columns, int rows,
    int startX, int startY)
{
    std::vector<juce::Image> frames;
    if (! image.isValid() || cellWidth <= 0 || cellHeight <= 0
        || columns <= 0 || rows <= 0 || startX < 0 || startY < 0)
        return frames;

    const auto requiredWidth = static_cast<long long>(cellWidth) * columns;
    const auto requiredHeight = static_cast<long long>(cellHeight) * rows;
    if (requiredWidth > image.getWidth() - startX
        || requiredHeight > image.getHeight() - startY)
        return frames;

    frames.reserve(static_cast<size_t>(columns) * static_cast<size_t>(rows));
    for (int row = 0; row < rows; ++row)
        for (int column = 0; column < columns; ++column)
        {
            const int x = startX + column * cellWidth;
            const int y = startY + row * cellHeight;
            if (! isValidRegion(image, x, y, cellWidth, cellHeight))
            {
                frames.clear();
                return frames;
            }
            frames.push_back(copyRegionPreservingAlpha(image, x, y, cellWidth, cellHeight));
        }
    return frames;
}
