#pragma once

#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <vector>

namespace ppgu::performance
{
// Immutable, fully decoded mono PCM clip. Construct and validate off the
// audio thread. The owning snapshot must outlive this runtime and all voices.
struct PatternClipPcm
{
    std::vector<float> samples;
    double sampleRate = 48000.0;
};

struct PatternClipMapping
{
    std::uint16_t triggerNote = 60;
    std::uint8_t velocityLow = 1;
    std::uint8_t velocityHigh = 127;
    std::uint16_t clipIndex = 0;
    std::uint16_t articulation = 0;
    std::uint16_t chokeGroup = 0; // zero means no choke group
    std::uint32_t releaseSamples = 2400;
    float gain = 1.0f;
    float pan = 0.0f;
};

struct PatternClipSnapshot
{
    static constexpr std::size_t maximumMappings = 512;
    static constexpr std::size_t maximumClips = 256;
    static constexpr std::size_t maximumDecodedFrames = 8U * 1024U * 1024U;
    std::vector<PatternClipPcm> clips;
    std::vector<PatternClipMapping> mappings;
};

// Fixed-voice, allocation-free renderer. Snapshot installation and destruction
// are control-thread operations and require audio processing to be suspended;
// the snapshot must remain alive until the runtime is detached and reset.
class PatternClipRuntime final
{
public:
    static constexpr std::size_t maximumVoices = 32;

    // Run on a loader/worker thread before publication. This bounds all work
    // reachable from the real-time mapping lookup and prevents invalid PCM.
    [[nodiscard]] static bool validateSnapshot(const PatternClipSnapshot& snapshot) noexcept
    {
        if (snapshot.clips.empty() || snapshot.clips.size() > PatternClipSnapshot::maximumClips
            || snapshot.mappings.empty() || snapshot.mappings.size() > PatternClipSnapshot::maximumMappings)
            return false;
        std::size_t totalFrames = 0;
        for (const auto& clip : snapshot.clips)
        {
            if (clip.samples.empty() || !std::isfinite(clip.sampleRate)
                || clip.sampleRate < 8000.0 || clip.sampleRate > 192000.0
                || clip.samples.size() > PatternClipSnapshot::maximumDecodedFrames - totalFrames)
                return false;
            totalFrames += clip.samples.size();
            for (const float sample : clip.samples)
                if (!std::isfinite(sample)) return false;
        }
        for (std::size_t i = 0; i < snapshot.mappings.size(); ++i)
        {
            const auto& mapping = snapshot.mappings[i];
            if (mapping.triggerNote > 127 || mapping.velocityLow < 1
                || mapping.velocityHigh > 127 || mapping.velocityLow > mapping.velocityHigh
                || mapping.clipIndex >= snapshot.clips.size()
                || !std::isfinite(mapping.gain) || mapping.gain < 0.0f || mapping.gain > 4.0f
                || !std::isfinite(mapping.pan) || mapping.pan < -1.0f || mapping.pan > 1.0f)
                return false;
            for (std::size_t j = 0; j < i; ++j)
            {
                const auto& prior = snapshot.mappings[j];
                if (prior.triggerNote == mapping.triggerNote
                    && prior.articulation == mapping.articulation
                    && prior.velocityLow <= mapping.velocityHigh
                    && mapping.velocityLow <= prior.velocityHigh)
                    return false;
            }
        }
        return true;
    }

    void attachSnapshot(const PatternClipSnapshot* snapshot) noexcept
    {
        reset();
        activeSnapshot.store(snapshot != nullptr && validateSnapshot(*snapshot) ? snapshot : nullptr,
                             std::memory_order_release);
    }

    void detachSnapshot() noexcept
    {
        reset();
        activeSnapshot.store(nullptr, std::memory_order_release);
    }

    // Sample-offset callers split the render block at MIDI event positions.
    [[nodiscard]] bool noteOn(int note, int velocity, int channel,
                              int articulation = 0) noexcept
    {
        const auto* snapshot = activeSnapshot.load(std::memory_order_acquire);
        if (snapshot == nullptr || snapshot->mappings.empty()
            || snapshot->mappings.size() > PatternClipSnapshot::maximumMappings
            || note < 0 || note > 127
            || velocity < 1 || velocity > 127 || channel < 1 || channel > 16)
            return false;

        const PatternClipMapping* selected = nullptr;
        for (const auto& mapping : snapshot->mappings)
        {
            if (mapping.triggerNote == note && mapping.articulation == articulation
                && velocity >= mapping.velocityLow && velocity <= mapping.velocityHigh)
            {
                selected = &mapping;
                break;
            }
        }
        if (selected == nullptr || selected->clipIndex >= snapshot->clips.size())
            return false;

        const auto& clip = snapshot->clips[selected->clipIndex];
        if (clip.samples.empty() || !std::isfinite(clip.sampleRate)
            || clip.sampleRate <= 0.0 || !std::isfinite(selected->gain)
            || !std::isfinite(selected->pan))
            return false;

        if (selected->chokeGroup != 0)
            for (auto& voice : voices)
                if (voice.active && voice.chokeGroup == selected->chokeGroup)
                    beginFade(voice, chokeFadeSamples);

        Voice* voice = nullptr;
        for (auto& candidate : voices)
            if (!candidate.active) { voice = &candidate; break; }
        if (voice == nullptr)
        {
            voice = &voices[0];
            for (auto& candidate : voices)
                if (candidate.age < voice->age) voice = &candidate;
        }

        *voice = Voice {};
        voice->active = true;
        voice->clip = &clip;
        voice->note = note;
        voice->channel = channel;
        voice->chokeGroup = selected->chokeGroup;
        voice->releaseSamples = selected->releaseSamples;
        voice->gain = selected->gain;
        voice->pan = std::clamp(selected->pan, -1.0f, 1.0f);
        voice->increment = clip.sampleRate / outputSampleRate;
        voice->age = nextAge++;
        return true;
    }

    void noteOff(int note, int channel) noexcept
    {
        for (auto& voice : voices)
            if (voice.active && voice.note == note && voice.channel == channel
                && !voice.releasing)
                beginFade(voice, voice.releaseSamples);
    }

    void allNotesOff() noexcept
    {
        for (auto& voice : voices)
            if (voice.active && !voice.releasing)
                beginFade(voice, voice.releaseSamples);
    }

    void reset() noexcept
    {
        for (auto& voice : voices) voice = Voice {};
        nextAge = 1;
    }

    void prepare(double sampleRate) noexcept
    {
        outputSampleRate = std::isfinite(sampleRate) && sampleRate >= 8000.0
            ? sampleRate : 48000.0;
        reset();
    }

    void render(float* left, float* right, int samples) noexcept
    {
        if (left == nullptr || right == nullptr || samples <= 0)
            return;

        for (auto& voice : voices)
        {
            if (!voice.active || voice.clip == nullptr) continue;
            const auto& pcm = voice.clip->samples;
            const auto frameCount = pcm.size();
            const float leftGain = voice.gain * (voice.pan > 0.0f ? 1.0f - voice.pan : 1.0f);
            const float rightGain = voice.gain * (voice.pan < 0.0f ? 1.0f + voice.pan : 1.0f);

            for (int i = 0; i < samples && voice.active; ++i)
            {
                if (voice.position >= static_cast<double>(frameCount))
                {
                    voice.active = false;
                    break;
                }
                const auto index = static_cast<std::size_t>(voice.position);
                const auto next = std::min(index + 1, frameCount - 1);
                const float fraction = static_cast<float>(voice.position - static_cast<double>(index));
                const float source = pcm[index] + (pcm[next] - pcm[index]) * fraction;
                left[i] += source * leftGain * voice.envelope;
                right[i] += source * rightGain * voice.envelope;
                voice.position += voice.increment;

                if (voice.releasing)
                {
                    if (voice.fadeRemaining > 0)
                    {
                        voice.envelope = std::max(0.0f, voice.envelope - voice.fadeStep);
                        --voice.fadeRemaining;
                    }
                    if (voice.fadeRemaining == 0)
                        voice.active = false;
                }
            }
        }
    }

    [[nodiscard]] int activeVoiceCount() const noexcept
    {
        int count = 0;
        for (const auto& voice : voices) if (voice.active) ++count;
        return count;
    }

private:
    static constexpr std::uint32_t chokeFadeSamples = 64;

    struct Voice
    {
        const PatternClipPcm* clip = nullptr;
        double position = 0.0;
        double increment = 1.0;
        float gain = 1.0f;
        float pan = 0.0f;
        float envelope = 1.0f;
        float fadeStep = 0.0f;
        std::uint64_t age = 0;
        std::uint32_t releaseSamples = 0;
        std::uint32_t fadeRemaining = 0;
        std::uint16_t chokeGroup = 0;
        int note = -1;
        int channel = 1;
        bool active = false;
        bool releasing = false;
    };

    static void beginFade(Voice& voice, std::uint32_t length) noexcept
    {
        voice.releasing = true;
        voice.fadeRemaining = std::max<std::uint32_t>(1, length);
        // Linear de-click ramp avoids pow() on the real-time MIDI event path.
        voice.fadeStep = voice.envelope / static_cast<float>(voice.fadeRemaining);
    }

    std::atomic<const PatternClipSnapshot*> activeSnapshot { nullptr };
    std::array<Voice, maximumVoices> voices {};
    double outputSampleRate = 48000.0;
    std::uint64_t nextAge = 1;
};
} // namespace ppgu::performance
