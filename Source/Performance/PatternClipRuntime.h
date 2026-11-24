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
    std::uint16_t roundRobinGroup = 0;
    float pitchRatio = 1.0f; // target MIDI pitch relative to source_midi_note
};

struct PatternClipSnapshot
{
    static constexpr std::size_t maximumMappings = 512;
    static constexpr std::size_t maximumClips = 256;
    static constexpr std::size_t maximumDecodedFrames = 8U * 1024U * 1024U;
    std::vector<PatternClipPcm> clips;
    std::vector<PatternClipMapping> mappings;

    // Audio voices retain this immutable snapshot across render blocks.
    // Copying a snapshot creates a fresh, unreferenced ownership generation.
    // Voice lifetime bookkeeping is logically const: snapshots stay immutable
    // to the audio renderer while their external reference count changes.
    mutable std::atomic<std::uint32_t> activeVoiceReferences { 0 };

    PatternClipSnapshot() = default;
    PatternClipSnapshot(const PatternClipSnapshot& other)
        : clips(other.clips), mappings(other.mappings) {}
    PatternClipSnapshot& operator=(const PatternClipSnapshot& other)
    {
        if (this != &other)
        {
            clips = other.clips;
            mappings = other.mappings;
            activeVoiceReferences.store(0, std::memory_order_relaxed);
        }
        return *this;
    }
};

// Fixed-voice, allocation-free renderer. Published snapshots are immutable.
// A short lock-free call guard protects pointer acquisition; each active voice
// holds an atomic snapshot reference until it is retired. Owners may reclaim an
// unpublished snapshot only when canRetireSnapshot() returns true.
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
                || !std::isfinite(mapping.pan) || mapping.pan < -1.0f || mapping.pan > 1.0f
                || !std::isfinite(mapping.pitchRatio) || mapping.pitchRatio < 0.25f || mapping.pitchRatio > 4.0f)
                return false;
            for (std::size_t j = 0; j < i; ++j)
            {
                const auto& prior = snapshot.mappings[j];
                if (prior.triggerNote == mapping.triggerNote
                    && prior.articulation == mapping.articulation
                    && prior.roundRobinGroup == mapping.roundRobinGroup
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

    // Publish a fully validated immutable snapshot from a non-audio thread.
    // Existing voices keep a counted reference to their original snapshot.
    [[nodiscard]] bool publishSnapshot(const PatternClipSnapshot* snapshot) noexcept
    {
        if (snapshot == nullptr || !validateSnapshot(*snapshot))
            return false;
        activeSnapshot.store(snapshot, std::memory_order_seq_cst);
        return true;
    }

    // Called by the non-audio owner while it holds ownership of snapshot.
    // A zero call count plus zero voice references proves no audio operation
    // can still acquire or dereference this retired snapshot.
    [[nodiscard]] bool canRetireSnapshot(const PatternClipSnapshot* snapshot) const noexcept
    {
        if (snapshot == nullptr || activeCalls.load(std::memory_order_seq_cst) != 0
            || activeSnapshot.load(std::memory_order_seq_cst) == snapshot)
            return false;
        return snapshot->activeVoiceReferences.load(std::memory_order_seq_cst) == 0;
    }

    // Stop assigning new notes to the current snapshot. Existing voices keep
    // rendering from their retained immutable snapshot until release/end.
    void clearPublishedSnapshot() noexcept
    {
        activeSnapshot.store(nullptr, std::memory_order_seq_cst);
    }

    [[nodiscard]] bool hasSnapshot() const noexcept
    {
        return activeSnapshot.load(std::memory_order_seq_cst) != nullptr;
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
        const ActiveCall activeCall(*this);
        const auto* snapshot = activeSnapshot.load(std::memory_order_seq_cst);
        if (snapshot == nullptr || snapshot->mappings.empty()
            || snapshot->mappings.size() > PatternClipSnapshot::maximumMappings
            || note < 0 || note > 127
            || velocity < 1 || velocity > 127 || channel < 1 || channel > 16)
            return false;

        std::array<const PatternClipMapping*, PatternClipSnapshot::maximumMappings> matches {};
        std::size_t matchCount = 0;
        std::size_t rrCounterIndex = 0;
        for (std::size_t mappingIndex = 0; mappingIndex < snapshot->mappings.size(); ++mappingIndex)
        {
            const auto& mapping = snapshot->mappings[mappingIndex];
            if (mapping.triggerNote == note && mapping.articulation == articulation
                && velocity >= mapping.velocityLow && velocity <= mapping.velocityHigh
                && matchCount < matches.size())
            {
                if (matchCount == 0)
                    rrCounterIndex = mappingIndex;
                matches[matchCount++] = &mapping;
            }
        }
        if (matchCount == 0)
            return false;
        // The first matching mapping is a stable identity for this key,
        // articulation and velocity zone. Keep independent RR progress for
        // each such lane rather than coupling all articulations on one key.
        const auto selectedIndex = static_cast<std::size_t>(
            roundRobinCounters[rrCounterIndex]++ % static_cast<std::uint32_t>(matchCount));
        const auto* selected = matches[selectedIndex];
        if (selected->clipIndex >= snapshot->clips.size())
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

        retireVoice(*voice);
        *voice = Voice {};
        voice->snapshot = snapshot;
        snapshot->activeVoiceReferences.fetch_add(1, std::memory_order_seq_cst);
        voice->active = true;
        voice->clip = &clip;
        voice->note = note;
        voice->channel = channel;
        voice->chokeGroup = selected->chokeGroup;
        voice->releaseSamples = selected->releaseSamples;
        voice->gain = selected->gain;
        voice->pan = std::clamp(selected->pan, -1.0f, 1.0f);
        voice->increment = (clip.sampleRate / outputSampleRate) * selected->pitchRatio;
        voice->age = nextAge++;
        return true;
    }

    void noteOff(int note, int channel) noexcept
    {
        const ActiveCall activeCall(*this);
        for (auto& voice : voices)
            if (voice.active && voice.note == note && voice.channel == channel
                && !voice.releasing)
                beginFade(voice, voice.releaseSamples);
    }

    void allNotesOff() noexcept
    {
        const ActiveCall activeCall(*this);
        for (auto& voice : voices)
            if (voice.active && !voice.releasing)
                beginFade(voice, voice.releaseSamples);
    }

    void reset() noexcept
    {
        const ActiveCall activeCall(*this);
        for (auto& voice : voices)
        {
            retireVoice(voice);
            voice = Voice {};
        }
        nextAge = 1;
        roundRobinCounters.fill(0);
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
        const ActiveCall activeCall(*this);

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
                    retireVoice(voice);
                    break;
                }
                const auto index = static_cast<std::size_t>(voice.position);
                const auto next = std::min(index + 1, frameCount - 1);
                const float fraction = static_cast<float>(voice.position - static_cast<double>(index));
                const float source = pcm[index] + (pcm[next] - pcm[index]) * fraction;
                left[i] += source * leftGain * voice.envelope;
                if (right != left)
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
                    {
                        voice.active = false;
                        retireVoice(voice);
                    }
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

    struct ActiveCall
    {
        explicit ActiveCall(const PatternClipRuntime& owner) noexcept : runtime(owner)
        {
            runtime.activeCalls.fetch_add(1, std::memory_order_seq_cst);
        }
        ~ActiveCall()
        {
            runtime.activeCalls.fetch_sub(1, std::memory_order_seq_cst);
        }
        const PatternClipRuntime& runtime;
    };

    struct Voice
    {
        const PatternClipSnapshot* snapshot = nullptr;
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

    static void retireVoice(Voice& voice) noexcept
    {
        if (voice.snapshot != nullptr)
        {
            voice.snapshot->activeVoiceReferences.fetch_sub(1, std::memory_order_seq_cst);
            voice.snapshot = nullptr;
        }
    }

    static void beginFade(Voice& voice, std::uint32_t length) noexcept
    {
        voice.releasing = true;
        voice.fadeRemaining = std::max<std::uint32_t>(1, length);
        // Linear de-click ramp avoids pow() on the real-time MIDI event path.
        voice.fadeStep = voice.envelope / static_cast<float>(voice.fadeRemaining);
    }

    std::atomic<const PatternClipSnapshot*> activeSnapshot { nullptr };
    mutable std::atomic<std::uint32_t> activeCalls { 0 };
    std::array<Voice, maximumVoices> voices {};
    std::array<std::uint32_t, PatternClipSnapshot::maximumMappings> roundRobinCounters {};
    double outputSampleRate = 48000.0;
    std::uint64_t nextAge = 1;
};
} // namespace ppgu::performance
