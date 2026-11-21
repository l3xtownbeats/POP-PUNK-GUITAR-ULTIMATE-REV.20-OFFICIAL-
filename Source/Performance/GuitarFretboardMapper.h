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
        // Finger: -1 = muted, 0 = open string, 1..4 = fretting-hand fingers,
        // 5 = thumb-over (only considered for the low-E string).
        std::array<int, 6> fingersByString {{ -1, -1, -1, -1, -1, -1 }};
        int noteCount = 0;
        int fingerCount = 0;
        int barreCount = 0;
        int thumbStringIndex = -1;
        int thumbFret = 0;
        int baseFret = 1;
        int minFret = 0;
        int maxFret = 0;
        bool usesThumb = false;
        bool valid = false;
    };

    // Standard guitar tuning, low to high: E2 A2 D3 G3 B3 E4.
    inline constexpr std::array<int, 6> standardGuitarOpenNotes {{
        40, 45, 50, 55, 59, 64
    }};

    // Finds a playable one-note-per-string assignment. The bounded search
    // checks at most 6! assignments, prefers compact positions and open
    // strings, and rejects voicings requiring more than four fingers unless
    // a unique low-E note can safely be assigned to the thumb.
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
        int bestFingerCount = std::numeric_limits<int>::max();
        int bestOpenCount = -1;
        int bestSpan = std::numeric_limits<int>::max();
        int bestFretSum = std::numeric_limits<int>::max();
        int bestThumbString = -1;
        int bestThumbFret = 0;
        bool found = false;

        const auto search = [&](auto&& self, int noteIndex, int fretSum,
                                int currentMin, int currentMax) noexcept -> void
        {
            if (noteIndex == noteCount)
            {
                const int span = currentMax - currentMin;
                if (span > maximumFretSpan)
                    return;

                std::array<int, 6> fretLevels {};
                int fretLevelCount = 0;
                int openCount = 0;
                for (int i = 0; i < noteCount; ++i)
                {
                    const int fret = candidateFrets[static_cast<std::size_t>(i)];
                    if (fret == 0)
                    {
                        ++openCount;
                        continue;
                    }
                    bool alreadyPresent = false;
                    for (int level = 0; level < fretLevelCount; ++level)
                        alreadyPresent = alreadyPresent || fretLevels[static_cast<std::size_t>(level)] == fret;
                    if (!alreadyPresent)
                        fretLevels[static_cast<std::size_t>(fretLevelCount++)] = fret;
                }
                std::sort(fretLevels.begin(), fretLevels.begin() + fretLevelCount);

                int thumbString = -1;
                int thumbFret = 0;
                if (fretLevelCount > 4)
                {
                    // Thumb-over is a controlled fallback, not the default:
                    // the low-E fretted note must own a unique fret position.
                    for (int i = 0; i < noteCount; ++i)
                    {
                        if (candidateStrings[static_cast<std::size_t>(i)] != 0
                            || candidateFrets[static_cast<std::size_t>(i)] == 0)
                            continue;
                        const int lowEFret = candidateFrets[static_cast<std::size_t>(i)];
                        bool sharedFret = false;
                        for (int j = 0; j < noteCount; ++j)
                            if (j != i && candidateFrets[static_cast<std::size_t>(j)] == lowEFret)
                                sharedFret = true;
                        if (!sharedFret)
                        {
                            thumbString = 0;
                            thumbFret = lowEFret;
                            break;
                        }
                    }
                    if (thumbString < 0)
                        return;
                    for (int level = 0; level < fretLevelCount; ++level)
                        if (fretLevels[static_cast<std::size_t>(level)] == thumbFret)
                        {
                            for (int move = level; move + 1 < fretLevelCount; ++move)
                                fretLevels[static_cast<std::size_t>(move)] =
                                    fretLevels[static_cast<std::size_t>(move + 1)];
                            --fretLevelCount;
                            break;
                        }
                }

                if (fretLevelCount > 4)
                    return;

                const bool better =
                    !found
                    || (thumbString < 0 && bestThumbString >= 0)
                    || ((thumbString < 0) == (bestThumbString < 0)
                        && (fretLevelCount < bestFingerCount
                            || (fretLevelCount == bestFingerCount
                                && (span < bestSpan
                                    || (span == bestSpan
                                        && (openCount > bestOpenCount
                                            || (openCount == bestOpenCount && fretSum < bestFretSum)))))));
                if (better)
                {
                    found = true;
                    bestFingerCount = fretLevelCount;
                    bestOpenCount = openCount;
                    bestSpan = span;
                    bestFretSum = fretSum;
                    bestFrets = candidateFrets;
                    bestStrings = candidateStrings;
                    bestThumbString = thumbString;
                    bestThumbFret = thumbFret;
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
        result.fingersByString.fill(-1);
        result.noteCount = noteCount;
        result.fingerCount = bestFingerCount;
        result.thumbStringIndex = bestThumbString;
        result.thumbFret = bestThumbFret;
        result.usesThumb = bestThumbString >= 0;
        result.minFret = std::numeric_limits<int>::max();
        result.maxFret = 0;

        std::array<int, 6> fretLevels {};
        int fretLevelCount = 0;
        for (int i = 0; i < noteCount; ++i)
        {
            const auto source = static_cast<std::size_t>(i);
            const auto stringIndex = static_cast<std::size_t>(bestStrings[source]);
            const int fret = bestFrets[source];
            result.fretsByString[stringIndex] = fret;
            result.notesByString[stringIndex] = notes[source];
            if (fret == 0)
                result.fingersByString[stringIndex] = 0;
            else if (static_cast<int>(stringIndex) == bestThumbString)
                result.fingersByString[stringIndex] = 5;
            else
            {
                bool present = false;
                for (int level = 0; level < fretLevelCount; ++level)
                    present = present || fretLevels[static_cast<std::size_t>(level)] == fret;
                if (!present)
                    fretLevels[static_cast<std::size_t>(fretLevelCount++)] = fret;
            }
            if (fret > 0)
                result.minFret = (std::min)(result.minFret, fret);
            result.maxFret = (std::max)(result.maxFret, fret);
        }
        std::sort(fretLevels.begin(), fretLevels.begin() + fretLevelCount);

        for (int i = 0; i < 6; ++i)
        {
            if (result.fretsByString[static_cast<std::size_t>(i)] <= 0
                || i == bestThumbString)
                continue;
            const int fret = result.fretsByString[static_cast<std::size_t>(i)];
            for (int level = 0; level < fretLevelCount; ++level)
                if (fretLevels[static_cast<std::size_t>(level)] == fret)
                {
                    result.fingersByString[static_cast<std::size_t>(i)] = level + 1;
                    break;
                }
        }

        // Notes sharing one fret level share a finger (a partial barre).
        for (int level = 0; level < fretLevelCount; ++level)
        {
            int notesOnFret = 0;
            for (const int fret : result.fretsByString)
                if (fret == fretLevels[static_cast<std::size_t>(level)])
                    ++notesOnFret;
            if (notesOnFret > 1)
                ++result.barreCount;
        }

        if (result.minFret == std::numeric_limits<int>::max())
            result.minFret = 0;
        result.baseFret = result.minFret > 0 ? result.minFret : 1;
        result.valid = true;
        return result;
    }
}
