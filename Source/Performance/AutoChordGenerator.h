#pragma once

#include <array>

namespace ppgu::performance
{
    struct AutoChordResult
    {
        std::array<int, 6> notes {{ -1, -1, -1, -1, -1, -1 }};
        int count = 0;
    };

    // Builds a close-position triad from one incoming MIDI root note.
    // scaleMode: 0 = chromatic (major-triad fallback), 1 = major, 2 = natural minor.
    // When the input pitch is outside the selected scale, a major triad is used
    // without moving the played root. The function is allocation-free and bounded.
    inline AutoChordResult generateDiatonicTriad(int rootNote,
                                                 int scaleRoot,
                                                 int scaleMode) noexcept
    {
        AutoChordResult result;
        if (rootNote < 0 || rootNote > 127 || scaleRoot < 0 || scaleRoot > 11)
            return result;

        result.notes[0] = rootNote;
        result.count = 1;

        constexpr std::array<int, 7> majorScale {{ 0, 2, 4, 5, 7, 9, 11 }};
        constexpr std::array<int, 7> minorScale {{ 0, 2, 3, 5, 7, 8, 10 }};
        const auto& scale = scaleMode == 2 ? minorScale : majorScale;

        const int relativePitchClass = (rootNote % 12 - scaleRoot + 12) % 12;
        int degree = -1;
        if (scaleMode == 1 || scaleMode == 2)
        {
            for (int i = 0; i < static_cast<int>(scale.size()); ++i)
            {
                if (scale[static_cast<std::size_t>(i)] == relativePitchClass)
                {
                    degree = i;
                    break;
                }
            }
        }

        int thirdSemitones = 4;
        int fifthSemitones = 7;
        if (degree >= 0)
        {
            const int thirdDegree = degree + 2;
            const int fifthDegree = degree + 4;
            thirdSemitones = scale[static_cast<std::size_t>(thirdDegree % 7)]
                + (thirdDegree >= 7 ? 12 : 0) - scale[static_cast<std::size_t>(degree)];
            fifthSemitones = scale[static_cast<std::size_t>(fifthDegree % 7)]
                + (fifthDegree >= 7 ? 12 : 0) - scale[static_cast<std::size_t>(degree)];
        }

        const int third = rootNote + thirdSemitones;
        const int fifth = rootNote + fifthSemitones;
        if (third <= 127)
            result.notes[static_cast<std::size_t>(result.count++)] = third;
        if (fifth <= 127)
            result.notes[static_cast<std::size_t>(result.count++)] = fifth;
        return result;
    }
}
