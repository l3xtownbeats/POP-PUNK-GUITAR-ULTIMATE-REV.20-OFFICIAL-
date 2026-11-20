#include "Performance/AutoChordGenerator.h"

#include <array>
#include <iostream>

namespace
{
    bool expect(const char* label, int root, int key, int mode,
                const std::array<int, 3>& expected)
    {
        const auto actual = ppgu::performance::generateDiatonicTriad(root, key, mode);
        if (actual.count != 3
            || actual.notes[0] != expected[0]
            || actual.notes[1] != expected[1]
            || actual.notes[2] != expected[2])
        {
            std::cerr << label << " failed: count=" << actual.count
                      << " notes=" << actual.notes[0] << ","
                      << actual.notes[1] << "," << actual.notes[2] << "\n";
            return false;
        }
        return true;
    }
}

int main()
{
    bool ok = true;
    ok = expect("C major tonic", 60, 0, 1, {{ 60, 64, 67 }}) && ok;
    ok = expect("D minor in C major", 62, 0, 1, {{ 62, 65, 69 }}) && ok;
    ok = expect("B diminished in C major", 71, 0, 1, {{ 71, 74, 77 }}) && ok;
    ok = expect("A minor tonic", 57, 9, 2, {{ 57, 60, 64 }}) && ok;
    ok = expect("G major tonic", 67, 7, 1, {{ 67, 71, 74 }}) && ok;
    ok = expect("Chromatic major fallback", 61, 0, 0, {{ 61, 65, 68 }}) && ok;
    ok = expect("Out-of-scale major fallback", 58, 0, 1, {{ 58, 62, 65 }}) && ok;

    const auto invalidNote = ppgu::performance::generateDiatonicTriad(128, 0, 1);
    if (invalidNote.count != 0)
    {
        std::cerr << "Out-of-range MIDI note was accepted.\n";
        ok = false;
    }

    const auto invalidKey = ppgu::performance::generateDiatonicTriad(60, 12, 1);
    if (invalidKey.count != 0)
    {
        std::cerr << "Out-of-range scale root was accepted.\n";
        ok = false;
    }

    const auto highNote = ppgu::performance::generateDiatonicTriad(126, 0, 1);
    if (highNote.count != 1 || highNote.notes[0] != 126)
    {
        std::cerr << "Chord notes outside MIDI range were not safely omitted.\n";
        ok = false;
    }

    if (ok)
        std::cout << "AutoChord diatonic triad contract tests passed.\n";
    return ok ? 0 : 1;
}
