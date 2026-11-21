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

    // A fretted note receives a stable finger assignment; open and muted
    // strings are represented explicitly, and the thumb is limited to low E.
    int frettedFingerCount = 0;
    int openStringCount = 0;
    int thumbCount = 0;
    for (std::size_t string = 0; string < 6; ++string)
    {
        const int fret = cMajor.fretsByString[string];
        const int finger = cMajor.fingersByString[string];
        if (fret < 0 && finger != -1) return 7;
        if (fret == 0 && finger != 0) return 8;
        if (fret > 0)
        {
            if (finger < 1 || finger > 5) return 9;
            if (finger == 5)
            {
                ++thumbCount;
                if (string != 0 || !cMajor.usesThumb) return 10;
            }
            else
                ++frettedFingerCount;
        }
    }
    if (thumbCount > 1 || frettedFingerCount > 4
        || cMajor.fingerCount > 4 || cMajor.usesThumb != (thumbCount == 1))
        return 11;

    const auto aMinorOpen = mapNotesToGuitarFretboard({{ 57, 60, 64, -1, -1, -1 }}, 3);
    if (!aMinorOpen.valid || aMinorOpen.fingersByString[5] != 0)
    {
        std::cerr << "A minor voicing did not preserve its open high-E string.\n";
        return 12;
    }

    const auto invalid = mapNotesToGuitarFretboard({{ 60, 64, 128, -1, -1, -1 }}, 3);
    if (invalid.valid)
    {
        std::cerr << "Invalid MIDI pitch was accepted.\n";
        return 13;
    }

    const auto impossible = mapNotesToGuitarFretboard({{ 0, 1, 2, 3, 4, 5 }}, 6);
    if (impossible.valid)
    {
        std::cerr << "Impossible voicing was accepted by octave-shifting notes.\n";
        return 14;
    }

    std::cout << "Guitar fretboard mapper contracts passed.\n";
    return 0;
}
