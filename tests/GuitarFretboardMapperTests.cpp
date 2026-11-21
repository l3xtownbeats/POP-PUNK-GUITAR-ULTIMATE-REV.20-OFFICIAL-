#include "Performance/GuitarFretboardMapper.h"

#include <array>
#include <iostream>

using ppgu::performance::mapNotesToGuitarFretboard;

int main()
{
    const auto cMajor = mapNotesToGuitarFretboard({{ 60, 64, 67, -1, -1, -1 }}, 3);
    if (!cMajor.valid || cMajor.noteCount != 3 || cMajor.maxFret - cMajor.minFret > 3)
    {
        std::cerr << "C major triad was not mapped to a playable voicing.\n";
        return 1;
    }

    std::array<bool, 6> occupied {};
    int mapped = 0;
    for (std::size_t string = 0; string < 6; ++string)
    {
        if (cMajor.fretsByString[string] < 0)
            continue;
        occupied[string] = true;
        const int expected = ppgu::performance::standardGuitarOpenNotes[string]
            + cMajor.fretsByString[string];
        if (expected != cMajor.notesByString[string])
            return 2;
        ++mapped;
    }
    if (mapped != 3)
        return 3;

    const auto aMinor = mapNotesToGuitarFretboard({{ 57, 60, 64, -1, -1, -1 }}, 3);
    if (!aMinor.valid || aMinor.noteCount != 3)
    {
        std::cerr << "A minor triad was not mapped.\n";
        return 4;
    }

    const auto invalid = mapNotesToGuitarFretboard({{ 60, 64, 128, -1, -1, -1 }}, 3);
    if (invalid.valid)
    {
        std::cerr << "Invalid MIDI pitch was accepted.\n";
        return 5;
    }

    const auto impossible = mapNotesToGuitarFretboard({{ 0, 1, 2, 3, 4, 5 }}, 6);
    if (impossible.valid)
    {
        std::cerr << "Impossible voicing was accepted by octave-shifting notes.\n";
        return 6;
    }

    std::cout << "Guitar fretboard mapper contracts passed.\n";
    return 0;
}
