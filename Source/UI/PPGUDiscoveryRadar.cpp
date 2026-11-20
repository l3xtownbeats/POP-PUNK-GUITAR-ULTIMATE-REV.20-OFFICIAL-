#include "PPGUDiscoveryRadar.h"

PPGUDiscoveryRadar::PPGUDiscoveryRadar(std::vector<juce::Image> images, int fps)
{
    setFrames(std::move(images), fps);
}

void PPGUDiscoveryRadar::setFrames(std::vector<juce::Image> images, int fps)
{
    stopTimer();
    running = false;
    frames.clear();
    for (auto& image : images)
        if (image.isValid())
            frames.push_back(std::move(image));
    currentFrame = 0;
    frameDelayMs = 1000 / juce::jlimit(1, 60, fps);
    repaint();
}

void PPGUDiscoveryRadar::setRunning(bool shouldRun)
{
    const bool canRun = shouldRun && ! frames.empty();
    if (running == canRun)
        return;

    running = canRun;
    if (running)
        startTimer(frameDelayMs);
    else
        stopTimer();
    repaint();
}

void PPGUDiscoveryRadar::timerCallback()
{
    if (! running || frames.empty())
    {
        stopTimer();
        running = false;
        return;
    }

    currentFrame = (currentFrame + 1) % static_cast<int>(frames.size());
    repaint();
}

void PPGUDiscoveryRadar::paint(juce::Graphics& g)
{
    g.fillAll(juce::Colours::transparentBlack);
    if (frames.empty())
        return;

    const auto& frame = frames[static_cast<size_t>(currentFrame)];
    if (frame.isValid())
        g.drawImageWithin(frame, 0, 0, getWidth(), getHeight(),
                          juce::RectanglePlacement::centred);
}
