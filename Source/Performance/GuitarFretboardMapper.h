#pragma once

#include <array>
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <limits>

namespace ppgu::performance
{
    struct GuitarFretboardVoicing
    {
        // String index 0 is low E (string 6); index 5 is high E (string 1).
        // Per-string fret: -1 = muted, 0 = open, 1..maxFret = fretted.
        std::array<int, 6> fretsByString {{ -1, -1, -1, -1, -1, -1 }};
        std::array<int, 6> notesByString {{ -1, -1, -1, -1, -1, -1 }};
        int noteCount = 0;
        int baseFret = 1;
        int minFret = 0;
        int maxFret = 0;
        bool valid = false;
    };

    // Standard guitar tuning, low to high: E2 A2 D3 G3 B3 E4.
    inline constexpr std::array<int, 6> standardGuitarOpenNotes {{
        40, 45, 50, 55, 59, 64
    }};

    // Finds a playable one-note-per-string assignment. The bounded search
    // checks at most 6! assignments and prefers the smallest fret span, then
    // lower positions. Invalid MIDI notes and notes outside the fret range
    // are rejected instead of silently octave-shifted.
    inline GuitarFretboardVoicing mapNotesToGuitarFretboard(
        const std::array<int, 6>& notes,
        int noteCount,
        int maximumFret = 12,
        int maximumFretSpan = 3) noexcept
    {
        GuitarFretboardVoicing result;
        if (noteCount < 1 || noteCount > 6 || maximumFret < 0 || maximumFret > 24
            || maximumFretSpan < 0 || maximumFretSpan > maximumFret)
            return result;

        std::array<int, 6> candidateFrets {};
        std::array<int, 6> candidateStrings {};
        std::array<bool, 6> usedStrings {};
        std::array<int, 6> bestFrets {};
        std::array<int, 6> bestStrings {};
        int bestSpan = std::numeric_limits<int>::max();
        int bestFretSum = std::numeric_limits<int>::max();
        bool found = false;

        const auto search = [&](auto&& self, int noteIndex, int fretSum,
                                int currentMin, int currentMax) noexcept -> void
        {
            if (noteIndex == noteCount)
            {
                const int span = currentMax - currentMin;
                if (span > maximumFretSpan)
                    return;
                if (!found || span < bestSpan || (span == bestSpan && fretSum < bestFretSum))
                {
                    found = true;
                    bestSpan = span;
                    bestFretSum = fretSum;
                    bestFrets = candidateFrets;
                    bestStrings = candidateStrings;
                }
                return;
            }

            const int midiNote = notes[static_cast<std::size_t>(noteIndex)];
            if (midiNote < 0 || midiNote > 127)
                return;

            for (int stringIndex = 0; stringIndex < 6; ++stringIndex)
            {
                if (usedStrings[static_cast<std::size_t>(stringIndex)])
                    continue;
                const int fret = midiNote - standardGuitarOpenNotes[static_cast<std::size_t>(stringIndex)];
                if (fret < 0 || fret > maximumFret)
                    continue;

                const int nextMin = (noteIndex == 0) ? fret : (std::min)(currentMin, fret);
                const int nextMax = (noteIndex == 0) ? fret : (std::max)(currentMax, fret);
                if (nextMax - nextMin > maximumFretSpan)
                    continue;

                usedStrings[static_cast<std::size_t>(stringIndex)] = true;
                candidateFrets[static_cast<std::size_t>(noteIndex)] = fret;
                candidateStrings[static_cast<std::size_t>(noteIndex)] = stringIndex;
                self(self, noteIndex + 1, fretSum + fret, nextMin, nextMax);
                usedStrings[static_cast<std::size_t>(stringIndex)] = false;
            }
        };

        search(search, 0, 0, 0, 0);
        if (!found)
            return result;

        result.fretsByString.fill(-1);
        result.notesByString.fill(-1);
        result.noteCount = noteCount;
        result.minFret = std::numeric_limits<int>::max();
        result.maxFret = 0;
        for (int i = 0; i < noteCount; ++i)
        {
            const auto source = static_cast<std::size_t>(i);
            const auto stringIndex = static_cast<std::size_t>(bestStrings[source]);
            result.fretsByString[stringIndex] = bestFrets[source];
            result.notesByString[stringIndex] = notes[source];
            if (bestFrets[source] > 0)
                result.minFret = (std::min)(result.minFret, bestFrets[source]);
            result.maxFret = (std::max)(result.maxFret, bestFrets[source]);
        }
        if (result.minFret == std::numeric_limits<int>::max())
            result.minFret = 0;
        result.baseFret = result.minFret > 0 ? result.minFret : 1;
        result.valid = true;
        return result;
    }
}
