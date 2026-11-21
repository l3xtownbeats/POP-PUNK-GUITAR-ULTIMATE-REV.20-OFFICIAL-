#pragma once

#include <array>
#include <atomic>
#include <cstdint>
#include <type_traits>

namespace ppgu::performance
{
    // Immutable plain-data snapshot copied from the audio thread to UI readers.
    // Notes are MIDI note numbers; unused entries are -1. playMode: 0 = MELODY,
    // 1 = PATTERN. scaleMode: 0 = Chromatic, 1 = Major, 2 = Minor.
    struct AutoChordDisplayState
    {
        std::array<int, 6> inputNotes {{ -1, -1, -1, -1, -1, -1 }};
        std::array<int, 6> generatedNotes {{ -1, -1, -1, -1, -1, -1 }};
        int inputNoteCount = 0;
        int noteCount = 0;
        int scaleRoot = 0;
        int scaleMode = 0;
        int playMode = 0;
        bool enabled = false;
        bool active = false;
        bool autoChordApplied = false;
        std::uint32_t generation = 0;
    };

    // Non-blocking two-slot snapshot exchange. The audio thread is the sole
    // publisher; any number of UI readers may copy a snapshot. A writer only
    // writes an inactive slot after reserving it with an atomic writer bit.
    // If a UI reader still owns that slot, publish() skips this update rather
    // than waiting. No heap allocation, mutex, or spin-wait is used by writer.
    class AutoChordDisplayStateStore final
    {
        static_assert(std::atomic<std::uint32_t>::is_always_lock_free,
                      "AutoChord display requires lock-free 32-bit atomics.");

        static constexpr std::uint32_t writerFlag = 0x80000000u;
        static constexpr std::uint32_t readerMask = 0x7fffffffu;

    public:
        AutoChordDisplayStateStore() = default;
        AutoChordDisplayStateStore(const AutoChordDisplayStateStore&) = delete;
        AutoChordDisplayStateStore& operator=(const AutoChordDisplayStateStore&) = delete;

        [[nodiscard]] bool publish(const AutoChordDisplayState& value) noexcept
        {
            const int current = activeSlot.load(std::memory_order_acquire);
            const int target = 1 - current;
            std::uint32_t expected = 0;
            if (!slotAccess[static_cast<std::size_t>(target)].compare_exchange_strong(
                    expected, writerFlag, std::memory_order_acq_rel, std::memory_order_relaxed))
                return false;

            slots[static_cast<std::size_t>(target)] = value;
            activeSlot.store(target, std::memory_order_release);
            slotAccess[static_cast<std::size_t>(target)].store(0, std::memory_order_release);
            return true;
        }

        [[nodiscard]] bool read(AutoChordDisplayState& destination) const noexcept
        {
            for (int attempt = 0; attempt < 4; ++attempt)
            {
                const int selected = activeSlot.load(std::memory_order_acquire);
                auto& access = slotAccess[static_cast<std::size_t>(selected)];
                auto observed = access.load(std::memory_order_acquire);

                while ((observed & writerFlag) == 0u)
                {
                    if ((observed & readerMask) == readerMask)
                        break;
                    if (access.compare_exchange_weak(observed, observed + 1u,
                                                      std::memory_order_acq_rel,
                                                      std::memory_order_acquire))
                    {
                        if (selected != activeSlot.load(std::memory_order_acquire))
                        {
                            access.fetch_sub(1u, std::memory_order_release);
                            break;
                        }

                        destination = slots[static_cast<std::size_t>(selected)];
                        access.fetch_sub(1u, std::memory_order_release);
                        return true;
                    }
                }
            }
            return false;
        }

    private:
        // A zero access word is free, writerFlag means exclusively reserved,
        // and otherwise the low bits count active readers.
        mutable std::array<std::atomic<std::uint32_t>, 2> slotAccess {{ 0u, 0u }};
        std::array<AutoChordDisplayState, 2> slots {};
        std::atomic<int> activeSlot { 0 };
    };
}
