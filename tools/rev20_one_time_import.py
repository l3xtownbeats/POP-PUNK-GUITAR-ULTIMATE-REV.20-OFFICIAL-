from __future__ import annotations
import json, shutil, subprocess, tempfile
from pathlib import Path

ROOT = Path.cwd()
SOURCE_REPO = "https://github.com/l3xtownbeats/POP-PUNK-GUITAR-ULTIMATE-4.0-VST-L3XTOWN-.git"
SOURCE_BRANCH = "POP-PUNK-GUITAR-ULTIMATE-VST-REV.19-Build.03"

def run(*args, cwd=None):
    p = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, check=True)
    print(p.stdout)
    return p.stdout

def cp_file(src, rel):
    a = src / rel
    if not a.is_file(): raise FileNotFoundError(rel)
    b = ROOT / rel
    b.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(a, b)

def cp_tree(src, rel):
    a = src / rel
    if not a.is_dir(): raise FileNotFoundError(rel)
    b = ROOT / rel
    if b.exists(): shutil.rmtree(b)
    shutil.copytree(a, b)
    return sum(1 for p in b.rglob("*") if p.is_file())

with tempfile.TemporaryDirectory(prefix="rev20-import-") as tmp:
    src = Path(tmp) / "src"
    run("git", "clone", "--depth", "1", "--branch", SOURCE_BRANCH, SOURCE_REPO, str(src))
    print("SOURCE_HEAD=" + run("git", "rev-parse", "HEAD", cwd=src).strip())
    copied = cp_tree(src, "Source")

    excluded = {"TestSkinBatchGenerator.py", "ValidateSkinManifests.py", "test_rev18_factory_readiness.py"}
    td = ROOT / "tests"
    if td.exists(): shutil.rmtree(td)
    for p in (src / "tests").rglob("*"):
        if p.is_file() and p.name not in excluded:
            out = td / p.relative_to(src / "tests")
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, out)
            copied += 1

    explicit = [
      "CMakeLists.txt", "presets/factory_bank_300.json",
      "presets/examples/Example-Melody.ppgm", "presets/examples/Example-Pattern.ppgp",
      "assets/POP_PUNK_GUITAR_ULTIMATE_BANNER.svg", "assets/sound_hunter/registry.json",
      "licenses/META_OPEN_SOUND_CLEARANCE.md", "SKIN/approved_theme_sequence.json",
      "SKIN/control_schema.json", "SKIN/theme.schema.json",
      "docs/MELODY_SESSION_GUITARIST_PLAYABILITY.md",
      "docs/SAMPLE_LIBRARY_SOURCING_AND_LICENSE_POLICY.md",
      "docs/SAMPLE_STREAMING_PAGE_CACHE_DESIGN_RU.md", "docs/PRESET_FILE_SYSTEM.md",
      "docs/BANK_LIBRARY_SYSTEM_RU.md", "docs/AUXILIARY_PANEL_MANAGER_DESIGN_RU.md",
      "docs/REV18_NEON_STAGE_COMPONENT_MATRIX_RU.md", "docs/PPGU_REFERENCE_DESIGN_ASSET_REGISTER.md",
      "docs/META_CC0_LIBRARY_INSTALL_RU.md", "docs/SOUND_ASSET_SOURCES_AND_LICENSE_POLICY_RU.md",
      "tools/validate_apvts_layout.py", "tools/validate_factory_bank.py",
      "tools/validate_preset_files.py", "tools/validate_sound_asset_registry.py",
      "Import Sample Guitar/README_RU.md"
    ]
    for rel in explicit:
        cp_file(src, rel)
        copied += 1

    for n in range(1, 8):
        matches = list(src.glob(f"{n:02d} INTERFACE  NEON STAGE DEFAULT*.png"))
        matches = [p for p in matches if (("AUTOCHORDS" in p.name) == (n == 2))]
        if len(matches) != 1: raise RuntimeError(f"interface reference {n:02d}: {len(matches)} files")
        shutil.copy2(matches[0], ROOT / matches[0].name)
        copied += 1

    copied += cp_tree(src, "SKIN/Skin_053")
    for i in range(103, 118): copied += cp_tree(src, f"SKIN/Skin_{i}")

    sequence = json.loads((ROOT / "SKIN/approved_theme_sequence.json").read_text(encoding="utf-8"))
    themes = []
    for e in sequence["themes"]:
        ready = e["stableId"] == "skin-053"
        themes.append({
            "ordinal": e["ordinal"], "label": e["label"], "name": e["name"],
            "id": e["stableId"], "index": e["index"], "path": e["path"],
            "runtimeReady": ready,
            "status": "RUNTIME_ASSETS_PRESENT_SOURCE_AUDIT_PENDING" if ready else
                "APPROVED_DESIGN_SPEC_VECTOR_ASSETS_PRESENT_PNG_AND_RUNTIME_VALIDATION_PENDING",
            "preview": "Skin_053/assets/preview.png" if ready else None,
            "hero": "Skin_053/assets/hero.png" if ready else None
        })
    registry = {
        "schemaVersion":"1.0.0", "product":"POP PUNK GUITAR ULTIMATE",
        "contract":"REV.20 approved 16-theme visual shell registry",
        "totalSkins":16, "defaultLogicalSkin":"SKIN-1", "defaultStableId":"skin-053",
        "runtimePolicy":"Only runtimeReady=true themes are selectable. Design-only entries remain registered but are not presented as complete runtime themes.",
        "themes":themes
    }
    (ROOT / "SKIN/theme_manifest.json").write_text(json.dumps(registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT / "SKIN/README.md").write_text("""# REV.20 — 16 approved graphical shells

Exactly 16 logical themes are approved: SKIN-1 through SKIN-16.
SKIN-1 is NEON STAGE DEFAULT (skin-053). SKIN-2..SKIN-16 are the only other approved shells (skin-103..skin-117). No other theme batches or directories belong to the product.

Logical ordinals 1..16 are separate from immutable IDs/indices 53 and 103..117. Never renumber stable identities.

Only runtimeReady=true entries may be selected. At consolidation, SKIN-1 has PNG preview/hero assets. SKIN-2..SKIN-16 have approved manifests and distinct SVG foundations; their PNG preview/hero and runtime verification remain pending.

Themes are visual-only and cannot change APVTS IDs, controls, MIDI, sampler, DSP, presets or audio callback behaviour.
""",encoding="utf-8")

    ep = ROOT / "Source/PluginEditor.cpp"
    editor = ep.read_text(encoding="utf-8")
    a = editor.find("int PopPunkGuitarUltimateAudioProcessorEditor::getSkinCount() const")
    b = editor.find("void PopPunkGuitarUltimateAudioProcessorEditor::openSkinGalleryPanel()", a)
    if a < 0 or b < 0: raise RuntimeError("skin registry functions not found")
    replacement = r'''int PopPunkGuitarUltimateAudioProcessorEditor::getSkinCount() const
{
    const auto registryFile = runtimeSkinRoot.getChildFile("theme_manifest.json");
    if (!registryFile.existsAsFile()) return 0;
    const auto registry = juce::JSON::parse(registryFile.loadFileAsString());
    if (!registry.isObject()) return 0;
    const auto totalValue = registry.getProperty("totalSkins", juce::var());
    const auto* themes = registry.getProperty("themes", juce::var()).getArray();
    if ((!totalValue.isInt() && !totalValue.isInt64()) || themes == nullptr) return 0;
    const auto total = totalValue.toString().getLargeIntValue();
    if (total != 16 || total != static_cast<std::int64_t>(themes->size())
        || registry.getProperty("defaultStableId", "").toString() != "skin-053") return 0;
    std::set<int> ordinals, stableIndices;
    std::set<std::string> ids;
    for (const auto& entry : *themes)
    {
        if (!entry.isObject()) return 0;
        const auto o = entry.getProperty("ordinal", juce::var());
        const auto ix = entry.getProperty("index", juce::var());
        const auto id = entry.getProperty("id", "").toString();
        const auto path = entry.getProperty("path", "").toString();
        if ((!o.isInt() && !o.isInt64()) || (!ix.isInt() && !ix.isInt64())
            || !entry.getProperty("runtimeReady", juce::var()).isBool()
            || id.isEmpty() || path.isEmpty() || path.startsWith("/") || path.contains("..")
            || !path.startsWith("Skin_") || !path.endsWith("/theme.json")) return 0;
        const auto ordinal = o.toString().getLargeIntValue();
        const auto index = ix.toString().getLargeIntValue();
        if (ordinal < 1 || ordinal > total || index < 52
            || id != (juce::String("skin-") + juce::String(index))
            || !ordinals.insert(static_cast<int>(ordinal)).second
            || !stableIndices.insert(static_cast<int>(index)).second
            || !ids.insert(id.toStdString()).second) return 0;
    }
    return ordinals.size() == 16 ? 16 : 0;
}

juce::File PopPunkGuitarUltimateAudioProcessorEditor::getSkinManifest(int ordinal) const
{
    if (ordinal < 1 || ordinal > getSkinCount()) return {};
    const auto registryFile = runtimeSkinRoot.getChildFile("theme_manifest.json");
    if (!registryFile.existsAsFile()) return {};
    const auto registry = juce::JSON::parse(registryFile.loadFileAsString());
    const auto* themes = registry.getProperty("themes", juce::var()).getArray();
    if (themes == nullptr) return {};
    for (const auto& entry : *themes)
    {
        if (!entry.isObject()) continue;
        const auto o = entry.getProperty("ordinal", juce::var());
        if ((!o.isInt() && !o.isInt64()) || o.toString().getLargeIntValue() != ordinal) continue;
        if (!static_cast<bool>(entry.getProperty("runtimeReady", false))) return {};
        const auto path = entry.getProperty("path", "").toString();
        if (path.isEmpty() || path.startsWith("/") || path.contains("..")
            || !path.startsWith("Skin_") || !path.endsWith("/theme.json")) return {};
        const auto manifest = runtimeSkinRoot.getChildFile(path);
        return manifest.isAChildOf(runtimeSkinRoot) && manifest.existsAsFile() ? manifest : juce::File{};
    }
    return {};
}

int PopPunkGuitarUltimateAudioProcessorEditor::getSkinOrdinalForId(const juce::String& stableId) const
{
    const auto registryFile = runtimeSkinRoot.getChildFile("theme_manifest.json");
    if (!registryFile.existsAsFile()) return 0;
    const auto registry = juce::JSON::parse(registryFile.loadFileAsString());
    const auto* themes = registry.getProperty("themes", juce::var()).getArray();
    if (themes == nullptr) return 0;
    for (const auto& entry : *themes)
    {
        if (!entry.isObject() || entry.getProperty("id", "").toString() != stableId
            || !static_cast<bool>(entry.getProperty("runtimeReady", false))) continue;
        const auto o = entry.getProperty("ordinal", juce::var());
        if (o.isInt() || o.isInt64()) return static_cast<int>(o.toString().getLargeIntValue());
    }
    return 0;
}

void PopPunkGuitarUltimateAudioProcessorEditor::loadSavedSkin()
{
    auto* settings = uiProperties.getUserSettings();
    const auto id = settings ? settings->getValue("skinId", "skin-053") : juce::String("skin-053");
    const auto ordinal = getSkinOrdinalForId(id);
    if (ordinal < 1 || !loadSkinByIndex(ordinal, false))
    {
        const auto defaultOrdinal = getSkinOrdinalForId("skin-053");
        if (defaultOrdinal < 1 || !loadSkinByIndex(defaultOrdinal, false))
        {
            themeManager.resetToDefault();
            applyPalette();
        }
    }
}

bool PopPunkGuitarUltimateAudioProcessorEditor::loadSkinByIndex(int ordinal, bool save)
{
    if (ordinal < 1 || ordinal > getSkinCount()) return false;
    const auto manifest = getSkinManifest(ordinal);
    const bool loaded = manifest.existsAsFile() && themeManager.loadFromFile(manifest);
    if (!loaded) themeManager.resetToDefault();
    applyPalette();
    if (save && loaded) persistSkinPreference();
    return loaded;
}

'''
    editor = editor[:a] + replacement + editor[b:]
    editor = editor.replace(
        'const int activeIndex = activeId.startsWith("skin-") ? activeId.substring(5).getIntValue() : 0;',
        'const int activeIndex = getSkinOrdinalForId(activeId);')
    editor = editor.replace("safe->loadSkinByIndex(53, true);", "safe->loadSkinByIndex(1, true);")
    if "loadSkinByIndex(53, true)" in editor or "activeId.substring(5).getIntValue()" in editor:
        raise RuntimeError("old stable-index/logical-ordinal assumption remains")
    ep.write_text(editor, encoding="utf-8")

    hp = ROOT / "Source/PluginEditor.h"
    header = hp.read_text(encoding="utf-8")
    header = header.replace("    juce::File getSkinManifest(int index) const;\n",
                            "    juce::File getSkinManifest(int ordinal) const;\n    int getSkinOrdinalForId(const juce::String& stableId) const;\n")
    header = header.replace("    bool loadSkinByIndex(int index, bool persist);",
                            "    bool loadSkinByIndex(int ordinal, bool persist);")
    if "getSkinOrdinalForId" not in header: raise RuntimeError("stable ID resolver declaration missing")
    hp.write_text(header, encoding="utf-8")

    (ROOT / "tests/ThemeManagerTests.cpp").write_text(r'''#include "ThemeManager.h"
#include <iostream>
#include <set>
#include <string>

namespace
{
    int failures = 0;
    void expect(bool condition, const juce::String& message)
    {
        if (!condition) { ++failures; std::cerr << "FAIL: " << message << std::endl; }
    }
}

int main()
{
    PPGUThemeManager manager;
    expect(manager.getPalette().id == "skin-053", "fallback stable ID is canonical SKIN-1");
    expect(manager.getPalette().name == "NEON STAGE DEFAULT", "fallback name is NEON STAGE DEFAULT");
    expect(manager.getPalette().usedFallback, "default palette is safe fallback until manifest load");

    const auto root = juce::File::getCurrentWorkingDirectory();
    const auto skinRoot = root.getChildFile("SKIN");
    const auto registry = juce::JSON::parse(skinRoot.getChildFile("theme_manifest.json").loadFileAsString());
    const auto* themes = registry.getProperty("themes", juce::var()).getArray();
    const auto total = registry.getProperty("totalSkins", juce::var());
    expect(registry.isObject(), "REV.20 registry is a JSON object");
    expect(themes != nullptr, "REV.20 registry has a themes array");
    expect((total.isInt() || total.isInt64()) && total.toString().getLargeIntValue() == 16,
           "product contains exactly 16 logical themes");
    expect(registry.getProperty("defaultStableId", "").toString() == "skin-053",
           "SKIN-1 maps to immutable NEON STAGE ID");

    std::set<int> ordinals, indices;
    std::set<std::string> ids;
    int runtimeReadyCount = 0;
    if (themes != nullptr)
    {
        expect(themes->size() == 16, "registry contains exactly 16 entries");
        for (const auto& entry : *themes)
        {
            if (!entry.isObject()) { expect(false, "entry must be an object"); continue; }
            const auto ordinalValue = entry.getProperty("ordinal", juce::var());
            const auto indexValue = entry.getProperty("index", juce::var());
            const auto id = entry.getProperty("id", "").toString();
            const auto path = entry.getProperty("path", "").toString();
            const bool ready = static_cast<bool>(entry.getProperty("runtimeReady", false));
            expect(ordinalValue.isInt() || ordinalValue.isInt64(), id + " has logical ordinal");
            expect(indexValue.isInt() || indexValue.isInt64(), id + " has immutable index");
            expect(path.startsWith("Skin_") && path.endsWith("/theme.json"), id + " has safe manifest path");
            if ((!ordinalValue.isInt() && !ordinalValue.isInt64())
                || (!indexValue.isInt() && !indexValue.isInt64())) continue;
            const int ordinal = static_cast<int>(ordinalValue.toString().getLargeIntValue());
            const int index = static_cast<int>(indexValue.toString().getLargeIntValue());
            const auto expectedId = juce::String("skin-") + juce::String(index);
            expect(ordinal >= 1 && ordinal <= 16, id + " logical ordinal is valid");
            expect(id == expectedId, id + " stable ID/index mapping is preserved");
            expect(ordinals.insert(ordinal).second, id + " ordinal is unique");
            expect(indices.insert(index).second, id + " index is unique");
            expect(ids.insert(id.toStdString()).second, id + " ID is unique");
            const auto manifest = skinRoot.getChildFile(path);
            expect(manifest.existsAsFile(), id + " design manifest is preserved");
            if (ready)
            {
                ++runtimeReadyCount;
                const bool loaded = manifest.existsAsFile() && manager.loadFromFile(manifest);
                expect(loaded, id + " runtime-ready manifest loads"
                       + (loaded ? juce::String{} : ": " + manager.getLastError()));
                if (loaded)
                {
                    expect(manager.getPalette().id == id, id + " loaded ID matches registry");
                    expect(!manager.getPalette().usedFallback, id + " uses validated palette");
                }
            }
            else
            {
                expect(!manifest.getChildFile("assets/preview.png").existsAsFile(),
                       id + " is gated until PNG preview is present");
                expect(!manifest.getChildFile("assets/hero.png").existsAsFile(),
                       id + " is gated until PNG hero is present");
            }
        }
    }
    expect(ordinals.size() == 16, "all 16 logical ordinals are present");
    expect(runtimeReadyCount == 1, "only SKIN-1 is currently runtime-ready");

    const auto neon = skinRoot.getChildFile("Skin_053").getChildFile("theme.json");
    const bool loaded = neon.existsAsFile() && manager.loadFromFile(neon);
    expect(loaded, "NEON STAGE DEFAULT manifest loads"
           + (loaded ? juce::String{} : ": " + manager.getLastError()));
    if (loaded)
    {
        expect(manager.getPalette().id == "skin-053", "NEON STAGE stable ID stays skin-053");
        expect(manager.getPalette().name == "NEON STAGE DEFAULT", "NEON STAGE name is canonical");
        expect(manager.getPalette().tokens.windowBg == juce::Colour(0xff080b14),
               "NEON STAGE palette is canonical");
    }
    const auto invalid = neon.loadFileAsString().replace("\"index\": 53", "\"index\": 54");
    expect(!manager.loadFromJson(invalid), "stable ID/index mismatch is rejected");
    expect(manager.getPalette().usedFallback, "invalid theme restores safe fallback");
    std::cout << (failures == 0 ? "PASS" : "FAIL")
              << " — REV.20 16-theme registry and NEON STAGE runtime contract" << std::endl;
    return failures == 0 ? 0 : 1;
}
''', encoding="utf-8")

    # Remove the temporary importer from the committed snapshot, then commit the migration.
    (ROOT / "tools/rev20_one_time_import.py").unlink(missing_ok=True)
    (ROOT / ".github/workflows/rev20-one-time-import.yml").unlink(missing_ok=True)
    run("git", "add", "-A", cwd=ROOT)
    print("STAGED SUMMARY:\n" + run("git", "diff", "--cached", "--stat", cwd=ROOT))
    run("git", "config", "user.name", "github-actions[bot]", cwd=ROOT)
    run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com", cwd=ROOT)
    run("git", "commit", "-m", "REV.20: consolidate approved VST3 source and 16-theme baseline", cwd=ROOT)
    sha = run("git", "rev-parse", "HEAD", cwd=ROOT).strip()
    run("git", "push", "origin", "HEAD:main", cwd=ROOT)
    print("REV20_MIGRATION_COMMIT=" + sha)
    print("COPIED_SOURCE_FILES=" + str(copied))
