#include "UI/PPGUStageSpriteSheet.h"

#include <cstdlib>
#include <iostream>

namespace
{
void expect(bool condition, const char* message)
{
    if (! condition)
    {
        std::cerr << "FAIL: " << message << "\n";
        std::exit(1);
    }
}
}

int main()
{
    juce::Image sheet(juce::Image::ARGB, 16, 8, true);
    juce::Graphics g(sheet);
    g.fillAll(juce::Colours::transparentBlack);
    g.setColour(juce::Colour::fromRGBA(0, 255, 255, 128));
    g.fillRect(0, 0, 4, 4);
    g.setColour(juce::Colours::magenta);
    g.fillRect(4, 0, 4, 4);

    const auto horizontal = PPGUStageSpriteSheet::sliceHorizontal(sheet, 4, 4, 4);
    expect(horizontal.size() == 4, "valid horizontal sheet returns requested frame count");
    expect(horizontal[0].getWidth() == 4 && horizontal[0].getHeight() == 4,
           "horizontal frame dimensions are exact");
    expect(horizontal[0].getPixelAt(0, 0).getAlpha() == 128,
           "semi-transparent source alpha is preserved exactly");

    const auto grid = PPGUStageSpriteSheet::sliceGrid(sheet, 4, 4, 4, 2);
    expect(grid.size() == 8, "valid grid returns row-major frames");
    expect(grid[0].getPixelAt(0, 0).getAlpha() == 128,
           "grid slicing preserves semi-transparent alpha");
    expect(grid[1].getPixelAt(0, 0) == juce::Colours::magenta,
           "grid frame order is row-major");

    expect(PPGUStageSpriteSheet::sliceHorizontal(sheet, 0, 4, 2).empty(),
           "zero frame width is rejected");
    expect(PPGUStageSpriteSheet::sliceHorizontal(sheet, 4, 4, 5).empty(),
           "horizontal out-of-bounds request is rejected");
    expect(PPGUStageSpriteSheet::sliceGrid(sheet, 4, 4, 5, 2).empty(),
           "grid out-of-bounds request is rejected");
    expect(PPGUStageSpriteSheet::sliceGrid(sheet, 4, 4, 0, 2).empty(),
           "empty grid is rejected");

    std::cout << "PASS — native sprite slicing validates bounds and preserves source alpha.\n";
    return 0;
}
