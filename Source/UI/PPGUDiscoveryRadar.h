#pragma once

#include <juce_gui_basics/juce_gui_basics.h>
#include <vector>

/**
 * Optional visual radar for a future discovery backend.
 * It is stopped by default. The UI must not enable it as a substitute for a
 * real Auto Sound Hunter/search backend.
 */
class PPGUDiscoveryRadar final : public juce::Component, private juce::Timer
{
public:
    PPGUDiscoveryRadar() = default;
    PPGUDiscoveryRadar(std::vector<juce::Image> frames, int fps = 12);

    void setFrames(std::vector<juce::Image> frames, int fps = 12);
    void setRunning(bool shouldRun);
    bool isRunning() const noexcept { return running; }
    int getFrameCount() const noexcept { return static_cast<int>(frames.size()); }

    void paint(juce::Graphics& g) override;

private:
    void timerCallback() override;
    std::vector<juce::Image> frames;
    int currentFrame = 0;
    int frameDelayMs = 83;
    bool running = false;
};
