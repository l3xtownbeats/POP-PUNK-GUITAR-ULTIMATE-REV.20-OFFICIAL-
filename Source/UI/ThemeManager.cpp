#include "ThemeManager.h"

#include <limits>

namespace
{
    bool isAsciiHexDigit(juce_wchar character) noexcept
    {
        return (character >= '0' && character <= '9')
            || (character >= 'a' && character <= 'f')
            || (character >= 'A' && character <= 'F');
    }

    bool isHexColour(const juce::var& value)
    {
        const auto text = value.toString();
        if (text.length() != 7 || text[0] != '#')
            return false;

        for (int i = 1; i < text.length(); ++i)
            if (!isAsciiHexDigit(text[i]))
                return false;

        return true;
    }

    bool isNumber(const juce::var& value)
    {
        return value.isInt() || value.isInt64() || value.isDouble();
    }

    bool isNonEmptyString(const juce::var& value)
    {
        return value.isString() && value.toString().trim().isNotEmpty();
    }

    bool hasObject(const juce::var& parent, const juce::Identifier& key, juce::var& result)
    {
        result = parent.getProperty(key, juce::var());
        return result.isObject();
    }

    bool hasStringProperty(const juce::var& parent, const juce::Identifier& key)
    {
        return isNonEmptyString(parent.getProperty(key, juce::var()));
    }

    bool validateGroup(const juce::var& parent,
                       const juce::Identifier& groupName,
                       std::initializer_list<const char*> requiredKeys,
                       std::initializer_list<const char*> colourKeys,
                       juce::String& error)
    {
        juce::var group;
        if (!hasObject(parent, groupName, group))
        {
            error = "Missing token group: " + groupName.toString();
            return false;
        }

        for (const auto* key : requiredKeys)
        {
            const auto value = group.getProperty(key, juce::var());
            if (value.isVoid())
            {
                error = "Missing token: " + groupName.toString() + "." + key;
                return false;
            }
        }

        for (const auto* key : colourKeys)
        {
            if (!isHexColour(group.getProperty(key, juce::var())))
            {
                error = "Invalid HEX colour: " + groupName.toString() + "." + key;
                return false;
            }
        }

        return true;
    }

    bool validateButtonStyle(const juce::var& buttons,
                             const juce::Identifier& styleName,
                             juce::String& error)
    {
        juce::var style;
        if (!hasObject(buttons, styleName, style))
        {
            error = "Missing button style: " + styleName.toString();
            return false;
        }

        const juce::StringArray keys {
            "background", "foreground", "hover", "pressed", "disabled"
        };
        for (const auto& key : keys)
        {
            if (!isHexColour(style.getProperty(key, juce::var())))
            {
                error = "Invalid button colour: " + styleName.toString() + "." + key;
                return false;
            }
        }
        return true;
    }

    bool validateAssetSpec(const juce::var& assetSpec,
                           const juce::Identifier& name,
                           int width, int height, const juce::String& format,
                           juce::String& error)
    {
        juce::var spec;
        if (!hasObject(assetSpec, name, spec))
        {
            error = "Missing asset specification: " + name.toString();
            return false;
        }

        const auto widthValue = spec.getProperty("width", juce::var());
        const auto heightValue = spec.getProperty("height", juce::var());
        if ((!widthValue.isInt() && !widthValue.isInt64())
            || (!heightValue.isInt() && !heightValue.isInt64())
            // Compare in the original 64-bit domain. Narrowing before the
            // bounds check can wrap hostile int64 dimensions into valid values.
            || widthValue.toString().getLargeIntValue() != static_cast<juce::int64>(width)
            || heightValue.toString().getLargeIntValue() != static_cast<juce::int64>(height)
            || spec.getProperty("format", "").toString() != format)
        {
            error = "Invalid asset dimensions or format: " + name.toString();
            return false;
        }

        return true;
    }

    bool isSafeThemeRelativePath(const juce::String& path) noexcept
    {
        if (path.isEmpty() || path.startsWith("/") || path.startsWith("\\")
            || path.endsWith("/") || path.contains("//")
            || path.contains(":") || path.contains("\\"))
            return false;

        // Reject characters that are invalid or ambiguous on supported Windows
        // and POSIX filesystems, so a package cannot change meaning by platform.
        for (int i = 0; i < path.length(); ++i)
        {
            const auto character = path[i];
            if (character < 0x20 || character == 0x7f
                || character == '<' || character == '>' || character == '"'
                || character == '|' || character == '?' || character == '*')
                return false;
        }

        juce::StringArray segments;
        segments.addTokens(path, "/", "");
        if (segments.isEmpty())
            return false;
        for (const auto& segment : segments)
            if (segment.isEmpty() || segment == "." || segment == "..")
                return false;
        return true;
    }

    // A lexical child check alone is insufficient when any directory in the
    // path is a symlink. Reject symlinks from the asset itself all the way up
    // through the selected theme root and its ancestors.
    bool hasNoSymlinkComponents(juce::File file) noexcept
    {
        for (;;)
        {
            if (file.isSymbolicLink())
                return false;

            const auto parent = file.getParentDirectory();
            if (parent == file)
                return true;
            file = parent;
        }
    }

    bool isSafeThemeAssetFile(const juce::File& themeRoot,
                              const juce::String& relativePath,
                              juce::File& resolvedFile,
                              juce::String& error,
                              const juce::String& assetType)
    {
        if (!isSafeThemeRelativePath(relativePath))
        {
            error = "Theme " + assetType + " path is not a safe relative path";
            return false;
        }

        resolvedFile = themeRoot.getChildFile(relativePath);
        if (!resolvedFile.isAChildOf(themeRoot)
            || !hasNoSymlinkComponents(resolvedFile))
        {
            error = "Theme " + assetType + " resolves outside its package or traverses a symbolic link";
            return false;
        }
        return true;
    }

    bool loadSafeSvgArtwork(const juce::File& themeRoot,
                            const juce::String& relativePath,
                            int width, int height,
                            juce::Image& destination,
                            juce::String& error)
    {
        juce::File file;
        if (!isSafeThemeAssetFile(themeRoot, relativePath, file, error, "SVG"))
            return false;

        if (!file.existsAsFile() || file.getSize() <= 0 || file.getSize() > 256 * 1024)
        {
            error = "Theme SVG is missing or exceeds the size limit";
            return false;
        }

        const auto svgText = file.loadFileAsString();
        if (svgText.isEmpty()
            || svgText.containsIgnoreCase("<script")
            || svgText.containsIgnoreCase("<foreignObject")
            || svgText.containsIgnoreCase("<image")
            || svgText.containsIgnoreCase("javascript:")
            || svgText.containsIgnoreCase("href=\"http")
            || svgText.containsIgnoreCase("href='http")
            || svgText.containsIgnoreCase("url(http")
            || svgText.containsIgnoreCase("url(\"http")
            || svgText.containsIgnoreCase("url('http")
            || svgText.containsIgnoreCase("xlink:href")
            || svgText.containsIgnoreCase("<!DOCTYPE")
            || svgText.containsIgnoreCase("<!ENTITY"))
        {
            error = "Theme SVG contains unsupported or external content";
            return false;
        }

        auto xml = juce::XmlDocument::parse(svgText);
        if (xml == nullptr || xml->getTagName() != "svg")
        {
            error = "Theme SVG could not be parsed as a safe SVG document";
            return false;
        }

        auto drawable = juce::Drawable::createFromSVG(*xml);
        if (drawable == nullptr)
        {
            error = "Theme SVG could not be rendered";
            return false;
        }

        juce::Image rendered(juce::Image::ARGB, width, height, true);
        juce::Graphics graphics(rendered);
        drawable->drawWithin(graphics, rendered.getBounds().toFloat(),
                             juce::RectanglePlacement::stretchToFit, 1.0f);
        if (!rendered.isValid())
        {
            error = "Theme SVG produced an invalid artwork image";
            return false;
        }

        destination = std::move(rendered);
        return true;
    }

    bool loadSafePngArtwork(const juce::File& themeRoot,
                            const juce::String& relativePath,
                            int width, int height,
                            juce::Image& destination,
                            juce::String& error)
    {
        juce::File file;
        if (!isSafeThemeAssetFile(themeRoot, relativePath, file, error, "PNG"))
            return false;

        if (!file.existsAsFile() || file.getSize() <= 0 || file.getSize() > 8 * 1024 * 1024)
        {
            error = "Theme PNG is missing or exceeds the size limit";
            return false;
        }

        const auto decoded = juce::ImageFileFormat::loadFrom(file);
        if (!decoded.isValid() || decoded.getWidth() != width || decoded.getHeight() != height)
        {
            error = "Theme PNG could not be decoded or has unexpected dimensions";
            return false;
        }

        destination = decoded;
        return true;
    }

    bool validateSkinStudioManifest(const juce::var& root,
                                    PPGUThemeManager::Palette& palette,
                                    juce::String& error)
    {
        if (root.getProperty("schemaVersion", "").toString() != "1.0.0")
        {
            error = "Unsupported Skin Studio schema version";
            return false;
        }

        const auto id = root.getProperty("id", "").toString();
        const auto indexValue = root.getProperty("index", juce::var());
        const auto index = indexValue.toString().getLargeIntValue();
        if ((!indexValue.isInt() && !indexValue.isInt64())
            || id.length() < 8 || !id.startsWith("skin-")
            || index < 52 || index > std::numeric_limits<int>::max()
            || id.substring(5).getLargeIntValue() != index)
        {
            error = "Invalid Skin Studio ID/index pair";
            return false;
        }
        for (int position = 5; position < id.length(); ++position)
        {
            if (!juce::CharacterFunctions::isDigit(id[position]))
            {
                error = "Skin Studio ID suffix must contain only digits";
                return false;
            }
        }

        const auto name = root.getProperty("name", "").toString().trim();
        if (name.isEmpty())
        {
            error = "Skin Studio theme name is missing";
            return false;
        }

        const auto family = root.getProperty("family", "").toString();
        if (family != "carbon_studio" && family != "neon_basement"
            && family != "chrome_parade" && family != "wood_summer"
            && family != "vintage_tape" && family != "sunset_suburb"
            && family != "special")
        {
            error = "Invalid Skin Studio theme family";
            return false;
        }

        const auto layout = root.getProperty("layout", "").toString();
        if (layout != "STUDIO_CONSOLE" && layout != "WORKSTATION_TOPBAR"
            && layout != "RACK_SIDE" && layout != "COMPACT_MINI")
        {
            error = "Invalid Skin Studio layout";
            return false;
        }

        juce::var typography;
        if (!hasObject(root, "typography", typography)
            || !hasStringProperty(typography, "ui")
            || !hasStringProperty(typography, "display")
            || !hasStringProperty(typography, "weight")
            || !isNumber(typography.getProperty("scale", juce::var()))
            || !isNumber(typography.getProperty("letterSpacing", juce::var())))
        {
            error = "Skin Studio typography metadata is incomplete";
            return false;
        }
        const auto fontScale = static_cast<double>(typography.getProperty("scale", 1.0));
        const auto letterSpacing = static_cast<double>(typography.getProperty("letterSpacing", 0.0));
        if (fontScale < 0.5 || fontScale > 2.0 || letterSpacing < 0.0 || letterSpacing > 2.0)
        {
            error = "Skin Studio typography scale or letter spacing is outside the supported range";
            return false;
        }

        juce::var paletteTokens;
        if (!hasObject(root, "palette", paletteTokens))
        {
            error = "Skin Studio palette object is missing";
            return false;
        }

        const juce::StringArray requiredColours {
            "window_bg", "panel", "panel_elevated", "control_bg", "control_face",
            "control_border", "text_primary", "text_secondary", "text_disabled",
            "accent", "accent_glow", "danger", "warning", "success", "lcd_bg",
            "lcd_text", "led_on", "led_off", "shadow", "highlight", "lowlight"
        };
        const auto* paletteObject = paletteTokens.getDynamicObject();
        if (paletteObject == nullptr || paletteObject->getProperties().size() != requiredColours.size())
        {
            error = "Skin Studio palette must contain exactly 21 tokens";
            return false;
        }

        for (const auto& key : requiredColours)
        {
            if (!isHexColour(paletteTokens.getProperty(key, juce::var())))
            {
                error = "Invalid Skin Studio HEX token: " + key;
                return false;
            }
        }

        juce::var controls;
        const juce::StringArray requiredControlIds {
            "preset_browser", "mode_selector", "knob01", "knob02", "knob03",
            "knob04", "knob05", "knob06", "knob07", "knob08", "knob09",
            "fx_switch01", "fx_switch02", "fx_switch03", "fx_switch04",
            "fx_switch05", "fx_switch06", "fx_switch07", "midi_keyboard",
            "LCD_display", "LED_indicator", "SKIN_button", "Import_Guitar",
            "Auto_Discover", "Curator", "Settings", "About"
        };
        if (!hasObject(root, "controls", controls)
            || controls.getDynamicObject() == nullptr
            || controls.getDynamicObject()->getProperties().size()
                   != requiredControlIds.size() + 1)
        {
            error = "Skin Studio control map must contain the exact canonical control set";
            return false;
        }

        for (const auto& controlId : requiredControlIds)
        {
            if (!controls.getDynamicObject()->hasProperty(controlId))
            {
                error = "Skin Studio control map is missing mandatory ID: " + controlId;
                return false;
            }
        }

        if (!controls.getDynamicObject()->hasProperty("sync_selector"))
        {
            error = "Skin Studio control map is missing mandatory ID: sync_selector";
            return false;
        }

        juce::var assets;
        if (!hasObject(root, "assets", assets)
            || assets.getProperty("preview", "").toString() != "assets/preview.png"
            || assets.getProperty("hero", "").toString() != "assets/hero.png"
            || !hasStringProperty(assets, "texture")
            || !hasStringProperty(assets, "bezel")
            || !hasStringProperty(assets, "crest"))
        {
            error = "Skin Studio asset paths are incomplete";
            return false;
        }

        juce::var compatibility;
        if (!hasObject(root, "compatibility", compatibility)
            || static_cast<bool>(compatibility.getProperty("apvtsChanges", true))
            || static_cast<bool>(compatibility.getProperty("layoutChanges", true))
            || static_cast<bool>(compatibility.getProperty("audioChanges", true))
            || !root.getProperty("reduceInEco", juce::var()).isBool()
            || !static_cast<bool>(root.getProperty("reduceInEco", false))
            || !root.getProperty("hotSwapFadeMs", juce::var()).isInt()
            || static_cast<int>(root.getProperty("hotSwapFadeMs", 0)) != 150)
        {
            error = "Skin Studio visual-only/ECO/hot-swap contract is invalid";
            return false;
        }

        palette = PPGUThemeManager::Palette{};
        palette.id = id;
        palette.name = name;
        palette.uiTypeface = typography.getProperty("ui", "Segoe UI").toString();
        palette.displayTypeface = typography.getProperty("display", "Consolas").toString();
        palette.typographyWeight = typography.getProperty("weight", "semibold").toString();
        palette.fontScale = static_cast<float>(fontScale);
        palette.letterSpacing = static_cast<float>(letterSpacing);

        const auto readStudioToken = [&paletteTokens](const juce::String& key)
        {
            return juce::Colour::fromString(
                "ff" + paletteTokens.getProperty(key, juce::var()).toString().substring(1));
        };

        auto& t = palette.tokens;
        t.windowBg = readStudioToken("window_bg");
        t.panel = readStudioToken("panel");
        t.panelElevated = readStudioToken("panel_elevated");
        t.controlBg = readStudioToken("control_bg");
        t.controlFace = readStudioToken("control_face");
        t.controlBorder = readStudioToken("control_border");
        t.textPrimary = readStudioToken("text_primary");
        t.textSecondary = readStudioToken("text_secondary");
        t.textDisabled = readStudioToken("text_disabled");
        t.accent = readStudioToken("accent");
        t.accentGlow = readStudioToken("accent_glow");
        t.danger = readStudioToken("danger");
        t.warning = readStudioToken("warning");
        t.success = readStudioToken("success");
        t.lcdBg = readStudioToken("lcd_bg");
        t.lcdText = readStudioToken("lcd_text");
        t.ledOn = readStudioToken("led_on");
        t.ledOff = readStudioToken("led_off");
        t.shadow = readStudioToken("shadow");
        t.highlight = readStudioToken("highlight");
        t.lowlight = readStudioToken("lowlight");

        // Keep legacy aliases coherent while the editor migrates to token access.
        palette.canvas = t.windowBg;
        palette.canvasInset = t.controlBg;
        palette.surface = t.panel;
        palette.surfaceSecondary = t.controlBg;
        palette.surfaceRaised = t.panelElevated;
        palette.text = t.textPrimary;
        palette.textSecondary = t.textSecondary;
        palette.accent = t.accent;
        palette.accentSecondary = t.accentGlow;
        palette.border = t.controlBorder;
        palette.focus = t.highlight;
        palette.usedFallback = false;
        return true;
    }
}

bool PPGUThemeManager::readColour(const juce::var& object,
                                  const juce::Identifier& key,
                                  juce::Colour& destination)
{
    if (!object.isObject())
        return false;

    const auto value = object.getProperty(key, juce::var());
    if (!isHexColour(value))
        return false;

    destination = juce::Colour::fromString("ff" + value.toString().substring(1));
    return destination.isOpaque();
}

bool PPGUThemeManager::validateManifest(const juce::var& root,
                                        Palette& palette,
                                        juce::String& error)
{
    if (!root.isObject())
    {
        error = "Theme manifest is not a JSON object";
        return false;
    }

    if (root.getProperty("schemaVersion", "").toString() != "1.0.0")
    {
        error = "Unsupported theme schema version";
        return false;
    }

    const auto id = root.getProperty("id", "").toString();
    const auto indexValue = root.getProperty("index", juce::var());
    const int index = static_cast<int>(indexValue);
    if (!indexValue.isInt() && !indexValue.isInt64())
    {
        error = "Theme index must be an integer";
        return false;
    }
    if (id.length() >= 8)
        return validateSkinStudioManifest(root, palette, error);

    if (id.length() != 7 || !id.startsWith("skin-")
        || !juce::CharacterFunctions::isDigit(id[5])
        || !juce::CharacterFunctions::isDigit(id[6])
        || index < 1 || index > 51
        || id.substring(5).getIntValue() != index)
    {
        error = "Invalid theme ID/index pair";
        return false;
    }

    const auto name = root.getProperty("name", "").toString().trim();
    if (name.isEmpty() || !root.getProperty("description", juce::var()).isString())
    {
        error = "Theme name or description is invalid";
        return false;
    }

    const auto cluster = root.getProperty("cluster", "").toString();
    if (cluster != "A" && cluster != "B" && cluster != "C")
    {
        error = "Invalid theme cluster";
        return false;
    }

    juce::var identity;
    if (!hasObject(root, "identity", identity)
        || !hasStringProperty(identity, "material")
        || !hasStringProperty(identity, "lighting")
        || !hasStringProperty(identity, "mood"))
    {
        error = "Theme identity is incomplete";
        return false;
    }

    juce::var tokens;
    if (!hasObject(root, "tokens", tokens))
    {
        error = "Theme tokens object is missing";
        return false;
    }

    if (!validateGroup(tokens, "canvas", { "base", "inset" }, { "base", "inset" }, error)
        || !validateGroup(tokens, "surfaces", { "primary", "secondary", "raised", "overlay" }, { "primary", "secondary", "raised", "overlay" }, error)
        || !validateGroup(tokens, "borders", { "subtle", "strong", "focus" }, { "subtle", "strong", "focus" }, error)
        || !validateGroup(tokens, "typography", { "primary", "secondary", "disabled", "onAccent" }, { "primary", "secondary", "disabled", "onAccent" }, error)
        || !validateGroup(tokens, "rotary", { "body", "ring", "track", "value", "pointer", "disabled" }, { "body", "ring", "track", "value", "pointer", "disabled" }, error)
        || !validateGroup(tokens, "sliders", { "track", "fill", "thumb", "disabled" }, { "track", "fill", "thumb", "disabled" }, error)
        || !validateGroup(tokens, "tabs", { "activeBackground", "activeText", "inactiveBackground", "inactiveText", "indicator" }, { "activeBackground", "activeText", "inactiveBackground", "inactiveText", "indicator" }, error)
        || !validateGroup(tokens, "comboBoxes", { "background", "foreground", "border", "hover", "menuBackground", "selection" }, { "background", "foreground", "border", "hover", "menuBackground", "selection" }, error)
        || !validateGroup(tokens, "keyboard", { "whiteKey", "blackKey", "whitePressed", "blackPressed", "keyBorder", "octaveLabel" }, { "whiteKey", "blackKey", "whitePressed", "blackPressed", "keyBorder", "octaveLabel" }, error)
        || !validateGroup(tokens, "meters", { "low", "medium", "high", "background" }, { "low", "medium", "high", "background" }, error)
        || !validateGroup(tokens, "icons", { "primary", "secondary", "accent", "disabled" }, { "primary", "secondary", "accent", "disabled" }, error)
        || !validateGroup(tokens, "thumbnails", { "background", "border", "selected", "caption" }, { "background", "border", "selected", "caption" }, error)
        || !validateGroup(tokens, "windowChrome", { "background", "title", "border", "close" }, { "background", "title", "border", "close" }, error)
        || !validateGroup(tokens, "hero", { "background", "accent", "secondaryAccent", "highlight" }, { "background", "accent", "secondaryAccent", "highlight" }, error)
        || !validateGroup(tokens, "accents", { "primary", "secondary", "tertiary" }, { "primary", "secondary", "tertiary" }, error)
        || !validateGroup(tokens, "lighting", { "profile", "glow", "glowIntensity", "edgeHighlight" }, { "glow", "edgeHighlight" }, error))
        return false;

    juce::var buttons;
    if (!hasObject(tokens, "buttons", buttons)
        || !validateButtonStyle(buttons, "primary", error)
        || !validateButtonStyle(buttons, "secondary", error))
    {
        if (error.isEmpty())
            error = "Button token group is incomplete";
        return false;
    }

    juce::var texture;
    if (!hasObject(tokens, "texture", texture)
        || !hasStringProperty(texture, "material")
        || !texture.getProperty("enabled", juce::var()).isBool()
        || !isNumber(texture.getProperty("intensity", juce::var()))
        || static_cast<double>(texture.getProperty("intensity", 0.0)) < 0.0
        || static_cast<double>(texture.getProperty("intensity", 0.0)) > 1.0)
    {
        error = "Texture token group is invalid";
        return false;
    }

    const auto* textureObject = texture.getDynamicObject();
    if (textureObject == nullptr || !textureObject->hasProperty("asset"))
    {
        error = "Texture asset property is missing";
        return false;
    }
    const auto textureAsset = texture.getProperty("asset", juce::var());
    if (!textureAsset.isString() && !textureAsset.isVoid())
    {
        error = "Texture asset must be a string or null";
        return false;
    }

    juce::var lighting;
    if (!hasObject(tokens, "lighting", lighting)
        || !hasStringProperty(lighting, "profile")
        || !isNumber(lighting.getProperty("glowIntensity", juce::var()))
        || static_cast<double>(lighting.getProperty("glowIntensity", 0.0)) < 0.0
        || static_cast<double>(lighting.getProperty("glowIntensity", 0.0)) > 1.0)
    {
        error = "Lighting intensity/profile is invalid";
        return false;
    }

    juce::var assets;
    if (!hasObject(root, "assets", assets)
        || !hasStringProperty(assets, "preview")
        || !hasStringProperty(assets, "hero"))
    {
        error = "Theme asset paths are incomplete";
        return false;
    }

    const auto optionalTexturePath = assets.getProperty("texture", juce::var());
    if (!optionalTexturePath.isVoid() && !optionalTexturePath.isString())
    {
        error = "Theme texture path must be a string or null";
        return false;
    }

    juce::var assetSpec;
    if (!hasObject(root, "assetSpec", assetSpec)
        || !validateAssetSpec(assetSpec, "preview", 480, 300, "png", error)
        || !validateAssetSpec(assetSpec, "hero", 1200, 420, "webp", error))
        return false;

    juce::var compatibility;
    if (!hasObject(root, "compatibility", compatibility)
        || !hasStringProperty(compatibility, "minimumPluginVersion")
        || static_cast<bool>(compatibility.getProperty("apvtsChanges", true))
        || static_cast<bool>(compatibility.getProperty("layoutChanges", true))
        || static_cast<bool>(compatibility.getProperty("audioChanges", true)))
    {
        error = "Theme violates the visual-only compatibility contract";
        return false;
    }

    juce::var validation;
    if (!hasObject(root, "validation", validation)
        || !hasStringProperty(validation, "json")
        || !hasStringProperty(validation, "assets")
        || !hasStringProperty(validation, "runtime")
        || !hasStringProperty(validation, "flStudio20"))
    {
        error = "Theme validation metadata is incomplete";
        return false;
    }

    palette = Palette{};
    palette.id = id;
    palette.name = name;
    palette.usedFallback = false;

    if (!readColour(tokens.getProperty("canvas", juce::var()), "base", palette.canvas)
        || !readColour(tokens.getProperty("canvas", juce::var()), "inset", palette.canvasInset)
        || !readColour(tokens.getProperty("surfaces", juce::var()), "primary", palette.surface)
        || !readColour(tokens.getProperty("surfaces", juce::var()), "secondary", palette.surfaceSecondary)
        || !readColour(tokens.getProperty("surfaces", juce::var()), "raised", palette.surfaceRaised)
        || !readColour(tokens.getProperty("typography", juce::var()), "primary", palette.text)
        || !readColour(tokens.getProperty("typography", juce::var()), "secondary", palette.textSecondary)
        || !readColour(tokens.getProperty("accents", juce::var()), "primary", palette.accent)
        || !readColour(tokens.getProperty("accents", juce::var()), "secondary", palette.accentSecondary)
        || !readColour(tokens.getProperty("borders", juce::var()), "strong", palette.border)
        || !readColour(tokens.getProperty("borders", juce::var()), "focus", palette.focus))
    {
        error = "One or more palette colours could not be decoded";
        return false;
    }

    // Legacy skins predate the flat Skin Studio palette. Preserve their own
    // visual identity and supply deterministic semantic fallbacks for tokens
    // that the legacy schema never defined.
    auto& t = palette.tokens;
    t.windowBg = palette.canvas;
    t.panel = palette.surface;
    t.panelElevated = palette.surfaceRaised;
    t.controlBg = palette.canvasInset;
    t.controlFace = palette.surfaceRaised;
    t.controlBorder = palette.border;
    t.textPrimary = palette.text;
    t.textSecondary = palette.textSecondary;
    t.textDisabled = palette.textSecondary.darker(0.28f);
    t.accent = palette.accent;
    t.accentGlow = palette.accentSecondary;
    t.lcdBg = palette.canvas.darker(0.55f);
    t.lcdText = palette.text;
    t.ledOn = palette.accent;
    t.ledOff = palette.surfaceSecondary.darker(0.45f);
    t.shadow = palette.canvas.darker(0.40f);
    t.highlight = palette.focus;
    t.lowlight = palette.canvas.darker(0.18f);

    return true;
}

juce::Colour PPGUThemeManager::Palette::token(const juce::String& key) const noexcept
{
    if (key == "window_bg") return tokens.windowBg;
    if (key == "panel") return tokens.panel;
    if (key == "panel_elevated") return tokens.panelElevated;
    if (key == "control_bg") return tokens.controlBg;
    if (key == "control_face") return tokens.controlFace;
    if (key == "control_border") return tokens.controlBorder;
    if (key == "text_primary") return tokens.textPrimary;
    if (key == "text_secondary") return tokens.textSecondary;
    if (key == "text_disabled") return tokens.textDisabled;
    if (key == "accent") return tokens.accent;
    if (key == "accent_glow") return tokens.accentGlow;
    if (key == "danger") return tokens.danger;
    if (key == "warning") return tokens.warning;
    if (key == "success") return tokens.success;
    if (key == "lcd_bg") return tokens.lcdBg;
    if (key == "lcd_text") return tokens.lcdText;
    if (key == "led_on") return tokens.ledOn;
    if (key == "led_off") return tokens.ledOff;
    if (key == "shadow") return tokens.shadow;
    if (key == "highlight") return tokens.highlight;
    if (key == "lowlight") return tokens.lowlight;
    return {};
}

bool PPGUThemeManager::loadFromJson(const juce::String& jsonText)
{
    // Manifests are user-provided files. Bound parsing work before constructing
    // a JUCE var tree, and reject empty/oversized input deterministically.
    constexpr int maximumManifestCharacters = 1024 * 1024;
    if (jsonText.isEmpty() || jsonText.length() > maximumManifestCharacters)
    {
        lastError = jsonText.isEmpty()
            ? "Theme manifest is empty"
            : "Theme manifest exceeds the 1 MiB parsing limit";
        return false;
    }

    const auto root = juce::JSON::parse(jsonText);
    Palette candidate;
    juce::String error;

    if (!validateManifest(root, candidate, error))
    {
        lastError = error.isNotEmpty() ? error : "Theme manifest is invalid JSON or failed validation";
        return false;
    }

    activePalette = std::move(candidate);
    lastError.clear();
    return true;
}

bool PPGUThemeManager::loadFromFile(const juce::File& manifestFile)
{
    // Do not follow a manifest symlink: theme manifests must be regular files
    // inside the selected skin package, not pointers to arbitrary user files.
    if (!manifestFile.existsAsFile() || manifestFile.isDirectory()
        || !hasNoSymlinkComponents(manifestFile))
    {
        lastError = "Theme manifest is missing, not a regular file, or is a symbolic link";

        return false;
    }

    constexpr juce::int64 maximumManifestBytes = 1024 * 1024;
    const auto manifestSize = manifestFile.getSize();
    if (manifestSize <= 0 || manifestSize > maximumManifestBytes)
    {
        lastError = "Theme manifest is empty or exceeds the 1 MiB file limit";

        return false;
    }

    const auto jsonText = manifestFile.loadFileAsString();
    if (jsonText.isEmpty())
    {
        lastError = "Theme manifest could not be read";
        return false;
    }

    // Validate into an isolated candidate; publish only after every mandatory
    // artwork resource has passed validation.
    PPGUThemeManager parsedCandidate;
    if (!parsedCandidate.loadFromJson(jsonText))
    {
        lastError = parsedCandidate.getLastError();
        return false;
    }

    const auto root = juce::JSON::parse(jsonText);
    const auto id = root.getProperty("id", "").toString();
    auto candidate = parsedCandidate.activePalette;
    if (id.length() < 8)
    {
        activePalette = std::move(candidate);
        lastError.clear();
        return true;
    }

    const auto assets = root.getProperty("assets", juce::var());
    const auto themeRoot = manifestFile.getParentDirectory();
    juce::String error;

    if (!loadSafeSvgArtwork(themeRoot, assets.getProperty("texture", "").toString(),
                            512, 512, candidate.textureArtwork, error)
        || !loadSafeSvgArtwork(themeRoot, assets.getProperty("bezel", "").toString(),
                               800, 450, candidate.bezelArtwork, error)
        || !loadSafeSvgArtwork(themeRoot, assets.getProperty("crest", "").toString(),
                               480, 168, candidate.crestArtwork, error))
    {
        lastError = error.isNotEmpty() ? error : "Theme artwork loading failed";

        return false;
    }

    // The default NEON STAGE shell has a four-atlas visual package.
    // Atlases are decoded only on the UI/control thread and never touched by audio code.
    if (id == "skin-053")
    {
        juce::var spriteSheets;
        if (!hasObject(assets, "spriteSheets", spriteSheets)
            || !loadSafePngArtwork(themeRoot, spriteSheets.getProperty("controls", "").toString(),
                                  1024, 1024, candidate.controlsSpriteSheet, error)
            || !loadSafePngArtwork(themeRoot, spriteSheets.getProperty("meters_sliders", "").toString(),
                                   1024, 1024, candidate.metersSlidersSpriteSheet, error)
            || !loadSafePngArtwork(themeRoot, spriteSheets.getProperty("frames_panels", "").toString(),
                                   1024, 1024, candidate.framesPanelsSpriteSheet, error)
            || !loadSafePngArtwork(themeRoot, spriteSheets.getProperty("icons", "").toString(),
                                   1024, 1024, candidate.iconsSpriteSheet, error)
            || !loadSafePngArtwork(themeRoot, "assets/background/main.png",
                                   2560, 1440, candidate.backgroundArtwork, error)
            || !loadSafePngArtwork(themeRoot, "assets/textures/material.png",
                                   1024, 1024, candidate.materialArtwork, error)
            || !loadSafePngArtwork(themeRoot, "assets/fx_layers/stage_glow.png",
                                   800, 450, candidate.stageGlowArtwork, error)
            || !loadSafePngArtwork(themeRoot, "assets/fx_layers/edge_highlight.png",
                                   800, 450, candidate.edgeHighlightArtwork, error)
            || !loadSafePngArtwork(themeRoot, "assets/fx_layers/specular.png",
                                   800, 450, candidate.specularArtwork, error)
            || !loadSafePngArtwork(themeRoot, "assets/fx_layers/shadow.png",
                                   800, 450, candidate.shadowArtwork, error))
        {
            lastError = error.isNotEmpty() ? error : "NEON STAGE sprite atlas or premium artwork manifest is incomplete";

            return false;
        }

        const auto controlManifestFile = themeRoot.getChildFile("assets/controls/control_states_manifest.json");
        if (!controlManifestFile.existsAsFile() || !controlManifestFile.isAChildOf(themeRoot)
            || !hasNoSymlinkComponents(controlManifestFile)
            || controlManifestFile.getSize() <= 0 || controlManifestFile.getSize() > 512 * 1024)
        {
            lastError = "NEON STAGE control-state manifest is missing or unsafe";

            return false;
        }
        const auto controlManifestText = controlManifestFile.loadFileAsString();
        if (controlManifestText.isEmpty())
        {
            lastError = "NEON STAGE control-state manifest could not be read";
            return false;
        }
        const auto controlManifest = juce::JSON::parse(controlManifestText);
        const auto statesVar = controlManifest.getProperty("states", juce::var());
        const auto idsVar = controlManifest.getProperty("controlIds", juce::var());
        const auto recordsVar = controlManifest.getProperty("records", juce::var());
        const auto* states = statesVar.getArray();
        const auto* ids = idsVar.getArray();
        const auto* records = recordsVar.getArray();
        juce::StringArray requiredStates { "default", "hover", "pressed", "disabled", "dragged" };
        juce::StringArray requiredIds {
            "preset_browser", "mode_selector", "knob01", "knob02", "knob03",
            "knob04", "knob05", "knob06", "knob07", "knob08", "knob09",
            "fx_switch01", "fx_switch02", "fx_switch03", "fx_switch04",
            "fx_switch05", "fx_switch06", "fx_switch07", "midi_keyboard",
            "LCD_display", "LED_indicator", "SKIN_button", "Import_Guitar",
            "Auto_Discover", "Curator", "Settings", "About"
        };
        if (controlManifest.getProperty("schemaVersion", "").toString() != "1.0.0"
            || controlManifest.getProperty("skinId", "").toString() != "skin-053"
            || states == nullptr || ids == nullptr || records == nullptr
            || states->size() != 5 || ids->size() != 27 || records->size() != 135)
        {
            lastError = "NEON STAGE control-state manifest has an invalid schema or record count";

            return false;
        }
        juce::StringArray actualStates, actualIds;
        for (const auto& value : *states) actualStates.add(value.toString());
        for (const auto& value : *ids) actualIds.add(value.toString());
        actualStates.sort(false);
        requiredStates.sort(false);
        actualIds.sort(false);
        requiredIds.sort(false);
        if (actualStates != requiredStates || actualIds != requiredIds)
        {
            lastError = "NEON STAGE control-state manifest IDs/states do not match the approved contract";

            return false;
        }

        std::map<std::string, juce::Image> decodedControlStates;
        for (const auto& record : *records)
        {
            const auto controlId = record.getProperty("controlId", "").toString();
            const auto state = record.getProperty("state", "").toString();
            const auto relativePath = record.getProperty("runtime", "").toString();
            if (!actualIds.contains(controlId) || !requiredStates.contains(state)
                || !relativePath.startsWith("assets/controls/"))
            {
                lastError = "NEON STAGE control-state record contains an unknown ID, state or path";

                return false;
            }
            const auto key = (controlId + "|" + state).toStdString();
            if (decodedControlStates.find(key) != decodedControlStates.end())
            {
                lastError = "NEON STAGE control-state manifest contains a duplicate record";

                return false;
            }
            juce::Image decoded;
            if (!loadSafePngArtwork(themeRoot, relativePath, 256, 256, decoded, error))
            {
                lastError = error.isNotEmpty() ? error : "NEON STAGE control-state image failed validation";

                return false;
            }
            // The authored PNGs are square presentation tiles. Crop the control
            // face out of the tile before caching so a knob/switch is not rendered
            // with its surrounding label card inside a small JUCE control.
            auto controlFace = decoded;
            int cacheWidth = 128;
            int cacheHeight = 128;
            if (controlId.startsWith("knob"))
            {
                controlFace = decoded.getClippedImage({ 28, 20, 200, 200 });
            }
            else if (controlId.startsWith("fx_switch"))
            {
                controlFace = decoded.getClippedImage({ 22, 60, 212, 140 });
                cacheHeight = 84;
            }
            if (!controlFace.isValid())
            {
                lastError = "NEON STAGE control-state crop produced an invalid image";

                return false;
            }
            decodedControlStates.emplace(key, controlFace.rescaled(
                cacheWidth, cacheHeight, juce::Graphics::highResamplingQuality));
        }
        if (decodedControlStates.size() != 135)
        {
            lastError = "NEON STAGE control-state image set is incomplete";

            return false;
        }
        candidate.controlStateArtwork = std::move(decodedControlStates);
    }

    activePalette = std::move(candidate);
    lastError.clear();
    return true;
}

void PPGUThemeManager::resetToDefault() noexcept
{
    activePalette = Palette{};
}
