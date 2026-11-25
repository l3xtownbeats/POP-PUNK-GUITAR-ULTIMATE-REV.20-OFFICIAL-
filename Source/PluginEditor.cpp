
#include "UI/SkinGallerySelection.h"
#include "PluginEditor.h"
#include "PPGUData.h"
#include "UI/PPGUControlState.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <string>
#include <set>
#include <limits>
#include <vector>
#if JUCE_WINDOWS
 #ifndef NOMINMAX
  #define NOMINMAX
 #endif

 #include <windows.h>
juce::String fromWidePath(const wchar_t* value, int length)
{
    if (value == nullptr || length <= 0)
        return {};
    const int required = WideCharToMultiByte(CP_UTF8, 0, value, length, nullptr, 0, nullptr, nullptr);
    if (required <= 0)
        return {};
    std::string utf8(static_cast<size_t>(required), '\0');
    const int written = WideCharToMultiByte(CP_UTF8, 0, value, length,
                                             utf8.data(), required, nullptr, nullptr);
    return written == required ? juce::String::fromUTF8(utf8.data(), written) : juce::String();
}
#endif

namespace
{
// Shared theme typography factory. It changes font metrics only; component bounds,
// control geometry and all interaction/parameter bindings remain untouched.
juce::Font makeThemeFont(const PPGUThemeManager::Palette& palette, float baseSize,
                         bool display = false, bool bold = false)
{
    const auto& family = display ? palette.displayTypeface : palette.uiTypeface;
    const auto configuredWeight = palette.typographyWeight.equalsIgnoreCase("normal")
        ? juce::Font::plain : juce::Font::bold;
    const auto style = bold ? configuredWeight : juce::Font::plain;
    return juce::Font(family, baseSize * palette.fontScale, style)
        .withExtraKerningFactor(palette.letterSpacing);
}

void drawNineSliceFrame(juce::Graphics& g, const juce::Image& atlas,
                        juce::Rectangle<int> bounds, float opacity = 0.72f)
{
    if (!atlas.isValid() || bounds.getWidth() < 40 || bounds.getHeight() < 40)
        return;

    constexpr int corner = 24;
    constexpr int edge = 10;
    const int x = bounds.getX(), y = bounds.getY();
    const int right = bounds.getRight(), bottom = bounds.getBottom();
    const int middleWidth = juce::jmax(1, bounds.getWidth() - corner * 2);
    const int middleHeight = juce::jmax(1, bounds.getHeight() - corner * 2);

    g.saveState();
    g.setOpacity(opacity);
    const auto draw = [&g, &atlas](juce::Rectangle<int> dst, juce::Rectangle<int> src)
    {
        g.drawImage(atlas, dst.getX(), dst.getY(), dst.getWidth(), dst.getHeight(),
                    src.getX(), src.getY(), src.getWidth(), src.getHeight());
    };
    draw({x,y,corner,corner}, {30,60,92,92});
    draw({right-corner,y,corner,corner}, {160,60,92,92});
    draw({x,bottom-corner,corner,corner}, {290,60,92,92});
    draw({right-corner,bottom-corner,corner,corner}, {420,60,92,92});
    draw({x+corner,y+2,middleWidth,edge}, {30,230,440,22});
    draw({x+corner,bottom-edge-2,middleWidth,edge}, {30,270,440,22});
    draw({x+2,y+corner,edge,middleHeight}, {510,220,22,180});
    draw({right-edge-2,y+corner,edge,middleHeight}, {570,220,22,180});
    g.restoreState();
}

void drawThemeArtworkLayers(juce::Graphics& g, juce::Rectangle<int> bounds,
                            const PPGUThemeManager::Palette& palette,
                            float textureOpacity = 0.10f,
                            float bezelOpacity = 0.32f,
                            float crestOpacity = 0.035f,
                            bool includePremiumStageLayers = false)
{
    const auto drawLayer = [&g, bounds](const juce::Image& image, float opacity)
    {
        if (!image.isValid() || opacity <= 0.0f)
            return;
        g.saveState();
        g.setOpacity(opacity);
        g.drawImageWithin(image, bounds.getX(), bounds.getY(), bounds.getWidth(),
                          bounds.getHeight(), juce::RectanglePlacement::stretchToFit);
        g.restoreState();
    };

    if (includePremiumStageLayers)
    {
        drawLayer(palette.backgroundArtwork, 0.36f);
        if (palette.materialArtwork.isValid())
        {
            g.saveState();
            g.setTiledImageFill(palette.materialArtwork, bounds.getX(), bounds.getY(), 0.055f);
            g.fillRect(bounds);
            g.restoreState();
        }
        drawLayer(palette.shadowArtwork, 0.18f);
        drawLayer(palette.stageGlowArtwork, 0.24f);
        drawLayer(palette.specularArtwork, 0.16f);
    }

    // Use the selected skin's hero only as a full-shell backdrop; small
    // child panels keep their own clean material treatment and readable controls.
    if (palette.heroArtwork.isValid() && bounds.getWidth() >= 640 && bounds.getHeight() >= 360)
        drawLayer(palette.heroArtwork, includePremiumStageLayers ? 0.035f : 0.055f);

    // Extended per-skin layers are optional so older approved themes retain their
    // exact appearance until their complete artwork pack is installed.
    if (palette.fxLayerArtwork.isValid())
        drawLayer(palette.fxLayerArtwork, 0.16f);

    // Per-theme control ornament layer is deliberately subtle and shell-only:
    // it enriches the control surface without covering live JUCE controls or
    // changing their hit regions, parameter bindings, or accessibility.
    if (palette.controlsArtwork.isValid()
        && bounds.getWidth() >= 640 && bounds.getHeight() >= 360)
        drawLayer(palette.controlsArtwork, 0.10f);

    if (palette.decorativeArtwork.isValid() && bounds.getWidth() >= 640 && bounds.getHeight() >= 360)
        drawLayer(palette.decorativeArtwork, 0.12f);

    if (palette.textureArtwork.isValid() && textureOpacity > 0.0f)
    {
        g.saveState();
        g.setOpacity(textureOpacity);
        g.drawImageWithin(palette.textureArtwork, bounds.getX(), bounds.getY(),
                         bounds.getWidth(), bounds.getHeight(),
                         juce::RectanglePlacement::stretchToFit);
        g.restoreState();
    }

    if (palette.bezelArtwork.isValid() && bezelOpacity > 0.0f)
    {
        g.saveState();
        g.setOpacity(bezelOpacity);
        g.drawImageWithin(palette.bezelArtwork, bounds.getX(), bounds.getY(),
                         bounds.getWidth(), bounds.getHeight(),
                         juce::RectanglePlacement::stretchToFit);
        g.restoreState();
    }

    if (includePremiumStageLayers)
        drawLayer(palette.edgeHighlightArtwork, 0.26f);

    if (palette.crestArtwork.isValid() && crestOpacity > 0.0f
        && bounds.getWidth() >= 320 && bounds.getHeight() >= 220)
    {
        const auto crestWidth = juce::jmin(420, juce::jmax(1, bounds.getWidth() - 32));
        const auto crestHeight = juce::jmin(148, juce::jmax(1, bounds.getHeight() - 32));
        const auto crestBounds = bounds.withSizeKeepingCentre(crestWidth, crestHeight);
        g.saveState();
        g.setOpacity(crestOpacity);
        g.drawImageWithin(palette.crestArtwork, crestBounds.getX(), crestBounds.getY(),
                          crestBounds.getWidth(), crestBounds.getHeight(),
                          juce::RectanglePlacement::centred);
        g.restoreState();
    }
}

}

// Scrollable visual browser for the complete registry. Preview images are loaded
// lazily by visible cards so opening the gallery does not decode all 102 PNGs.
class PPGUSkinGalleryPanel final : public juce::Component, public PPGUThemeAwarePanel
{
public:
    struct Skin { int index = 0; juce::String id, name, family, familyKey, layout; juce::File preview; juce::Colour accent { 0xff00d9ff }; bool active = false, favorite = false; };

    PPGUSkinGalleryPanel(std::vector<Skin> skinsIn, PPGUThemeManager::Palette paletteIn,
                         int activeIndex, juce::StringArray favoritesIn, std::function<void(const juce::StringArray&)> saveFavoritesIn,
                         std::function<bool(int)> previewIn, std::function<bool(int)> applyIn,
                         std::function<void(int)> cancelIn)
        : skins(std::move(skinsIn)), palette(std::move(paletteIn)), selection(activeIndex),
          favorites(std::move(favoritesIn)), saveFavorites(std::move(saveFavoritesIn)),
          preview(std::move(previewIn)), apply(std::move(applyIn)), cancel(std::move(cancelIn))
    {
        setWantsKeyboardFocus(true);
        heading.setText("VISUAL SKIN GALLERY", juce::dontSendNotification);
        heading.setFont(makeThemeFont(palette, 17.0f, false, true));
        heading.setColour(juce::Label::textColourId, palette.token("text_primary"));
        addAndMakeVisible(heading);
        subtitle.setText("Select a theme, preview it temporarily, then Apply or Cancel.", juce::dontSendNotification);
        subtitle.setFont(makeThemeFont(palette, 10.0f));
        subtitle.setColour(juce::Label::textColourId, palette.token("text_secondary"));
        addAndMakeVisible(subtitle);

        search.setTextToShowWhenEmpty("SEARCH SKINS...", palette.token("text_secondary"));
        search.setColour(juce::TextEditor::backgroundColourId, palette.token("control_bg"));
        search.setColour(juce::TextEditor::textColourId, palette.token("text_primary"));
        search.setColour(juce::TextEditor::outlineColourId, palette.token("control_border"));
        search.setColour(juce::TextEditor::focusedOutlineColourId, palette.token("accent"));
        search.onTextChange = [this] { rebuildCards(); };
        addAndMakeVisible(search);

        familyFilter.addItem("ALL SKINS", 1);
        familyFilter.addItem("FAVORITES ONLY", 2);
        familyFilter.setSelectedId(1, juce::dontSendNotification);
        familyFilter.setColour(juce::ComboBox::backgroundColourId, palette.token("control_bg"));
        familyFilter.setColour(juce::ComboBox::textColourId, palette.token("text_primary"));
        familyFilter.setColour(juce::ComboBox::outlineColourId, palette.token("control_border"));
        familyFilter.onChange = [this] { rebuildCards(); };
        addAndMakeVisible(familyFilter);

        countLabel.setColour(juce::Label::textColourId, palette.token("accent"));
        countLabel.setFont(makeThemeFont(palette, 10.5f, false, true));
        countLabel.setJustificationType(juce::Justification::centredRight);
        addAndMakeVisible(countLabel);

        previewButton.setButtonText("PREVIEW"); favoriteButton.setButtonText("☆ FAVORITE");
        applyButton.setButtonText("APPLY"); cancelButton.setButtonText("CANCEL");
        for (auto* button : { &previewButton, &favoriteButton, &applyButton, &cancelButton })
        {
            button->setColour(juce::TextButton::buttonColourId, palette.token("panel_elevated"));
            button->setColour(juce::TextButton::textColourOffId, palette.token("text_primary"));
            addAndMakeVisible(*button);
        }
        applyButton.setColour(juce::TextButton::buttonColourId, palette.token("accent"));
        applyButton.setColour(juce::TextButton::textColourOffId, palette.token("window_bg"));
        previewButton.onClick = [this] { previewDraft(); };
        favoriteButton.onClick = [this] { toggleFavorite(); };
        applyButton.onClick = [this] { applyDraft(); };
        cancelButton.onClick = [this] { cancelDraft(); };

        viewport.setViewedComponent(&grid, false);
        viewport.setOpaque(false); viewport.setScrollBarsShown(true, false);
        viewport.setScrollBarThickness(10); addAndMakeVisible(viewport);
        rebuildCards(); grabKeyboardFocus();
    }

    ~PPGUSkinGalleryPanel() override
    {
        viewport.setViewedComponent(nullptr, false);
        if (selection.shouldRestoreOnClose() && cancel) cancel(selection.originalIndex());
    }

    void setThemePalette(const PPGUThemeManager::Palette& value) override
    {
        palette = value;
        for (auto& skin : skins) skin.active = skin.id == palette.id;
        heading.setFont(makeThemeFont(palette, 17.0f, false, true));
        subtitle.setFont(makeThemeFont(palette, 10.0f));
        countLabel.setFont(makeThemeFont(palette, 10.5f, false, true));
        heading.setColour(juce::Label::textColourId, palette.token("text_primary"));
        subtitle.setColour(juce::Label::textColourId, palette.token("text_secondary"));
        search.setColour(juce::TextEditor::backgroundColourId, palette.token("control_bg"));
        search.setColour(juce::TextEditor::textColourId, palette.token("text_primary"));
        search.setColour(juce::TextEditor::outlineColourId, palette.token("control_border"));
        search.setColour(juce::TextEditor::focusedOutlineColourId, palette.token("accent"));
        search.setTextToShowWhenEmpty("SEARCH THEMES...", palette.token("text_secondary"));
        familyFilter.setColour(juce::ComboBox::backgroundColourId, palette.token("control_bg"));
        familyFilter.setColour(juce::ComboBox::textColourId, palette.token("text_primary"));
        familyFilter.setColour(juce::ComboBox::outlineColourId, palette.token("control_border"));
        countLabel.setColour(juce::Label::textColourId, palette.token("accent"));
        for (auto* button : { &previewButton, &favoriteButton, &applyButton, &cancelButton })
        {
            button->setColour(juce::TextButton::buttonColourId, palette.token("panel_elevated"));
            button->setColour(juce::TextButton::textColourOffId, palette.token("text_primary"));
        }
        applyButton.setColour(juce::TextButton::buttonColourId, palette.token("accent"));
        applyButton.setColour(juce::TextButton::textColourOffId, palette.token("window_bg"));
        grid.setPalette(palette); rebuildCards(); repaint();
    }

    void paint(juce::Graphics& g) override
    {
        g.fillAll(palette.token("window_bg"));
        drawThemeArtworkLayers(g, getLocalBounds(), palette, 0.11f, 0.30f, 0.025f);
    }

    bool keyPressed(const juce::KeyPress& key) override
    {
        if (key == juce::KeyPress::escapeKey) { cancelDraft(); return true; }
        if (key == juce::KeyPress::returnKey)
        {
            if (key.getModifiers().isCtrlDown()) applyDraft(); else previewDraft();
            return true;
        }
        const bool previous = key == juce::KeyPress::leftKey || key == juce::KeyPress::upKey;
        const bool next = key == juce::KeyPress::rightKey || key == juce::KeyPress::downKey;
        if (previous || next)
        {
            if (visibleIndices.empty()) return true;
            auto it = std::find(visibleIndices.begin(), visibleIndices.end(), selection.draftIndex());
            int position = it == visibleIndices.end() ? 0 : static_cast<int>(std::distance(visibleIndices.begin(), it));
            position = (position + (next ? 1 : static_cast<int>(visibleIndices.size()) - 1))
                % static_cast<int>(visibleIndices.size());
            selectDraft(visibleIndices[static_cast<size_t>(position)]); return true;
        }
        return juce::Component::keyPressed(key);
    }

    void resized() override
    {
        auto area = getLocalBounds().reduced(16);
        heading.setBounds(area.removeFromTop(24)); subtitle.setBounds(area.removeFromTop(18));
        area.removeFromTop(4);
        auto filters = area.removeFromTop(32);
        search.setBounds(filters.removeFromLeft(juce::jmin(300, filters.getWidth() / 2)).reduced(1, 2));
        filters.removeFromLeft(8); familyFilter.setBounds(filters.removeFromLeft(190).reduced(1, 2));
        countLabel.setBounds(filters); area.removeFromTop(4);
        auto footer = area.removeFromBottom(36);
        cancelButton.setBounds(footer.removeFromRight(100).reduced(2)); footer.removeFromRight(8);
        applyButton.setBounds(footer.removeFromRight(100).reduced(2)); footer.removeFromRight(8);
        favoriteButton.setBounds(footer.removeFromRight(130).reduced(2)); footer.removeFromRight(8);
        previewButton.setBounds(footer.removeFromRight(110).reduced(2));
        viewport.setBounds(area); rebuildCards();
    }

private:
    class Card final : public juce::Component
    {
    public:
        Card(Skin itemIn, PPGUThemeManager::Palette paletteIn, int selectedIndex,
             std::function<void(int)> selectIn)
            : item(std::move(itemIn)), palette(std::move(paletteIn)),
              selected(item.index == selectedIndex), select(std::move(selectIn))
        { setMouseCursor(juce::MouseCursor::PointingHandCursor); }

        void paint(juce::Graphics& g) override
        {
            auto bounds = getLocalBounds().toFloat().reduced(1.0f);
            g.setColour(hovered ? palette.token("panel_elevated") : palette.token("panel"));
            g.fillRoundedRectangle(bounds, 9.0f);
            g.setColour(selected ? palette.token("accent") :
                        (item.active ? item.accent : palette.token("control_border")));
            g.drawRoundedRectangle(bounds, 9.0f, selected ? 2.4f : (item.active ? 1.8f : 1.0f));
            auto previewArea = bounds.reduced(8.0f, 8.0f).removeFromTop(72.0f);
            if (item.preview.existsAsFile())
            {
                const auto image = juce::ImageCache::getFromFile(item.preview);
                if (image.isValid())
                    g.drawImageWithin(image, (int)previewArea.getX(), (int)previewArea.getY(),
                                      (int)previewArea.getWidth(), (int)previewArea.getHeight(),
                                      juce::RectanglePlacement::centred);
                else paintFallback(g, previewArea);
            }
            else paintFallback(g, previewArea);
            auto textArea = bounds.reduced(10.0f, 8.0f); textArea.removeFromTop(78);
            g.setColour(palette.token("text_primary")); g.setFont(makeThemeFont(palette, 12.5f, false, true));
            g.drawText(item.name, textArea.removeFromTop(18.0f), juce::Justification::centredLeft, true);
            g.setColour(palette.token("text_secondary")); g.setFont(makeThemeFont(palette, 9.0f));
            g.drawText("SKIN " + juce::String(item.index).paddedLeft('0', 2)
                           + "  /  " + item.layout, textArea.removeFromTop(14.0f),
                       juce::Justification::centredLeft, true);
            const auto tag = item.active ? juce::String("ACTIVE")
                : (selected ? juce::String("SELECTED") : juce::String("AVAILABLE"));
            g.setColour(item.active ? item.accent : palette.token("accent"));
            g.fillRoundedRectangle(getWidth() - 68.0f, 10.0f, 58.0f, 17.0f, 5.0f);
            g.setColour(palette.token("window_bg")); g.setFont(makeThemeFont(palette, 7.5f, false, true));
            g.drawText(tag, getWidth() - 68, 10, 58, 17, juce::Justification::centred);
            if (item.favorite)
            {
                g.setColour(palette.token("warning"));
                g.setFont(makeThemeFont(palette, 15.0f, false, true));
                g.drawText("★", getWidth() - 94, 8, 20, 20, juce::Justification::centred);
            }
        }
        void setPalette(const PPGUThemeManager::Palette& value) { palette = value; repaint(); }
        void setSelected(bool value) { if (selected != value) { selected = value; repaint(); } }
        int getIndex() const noexcept { return item.index; }
        void mouseEnter(const juce::MouseEvent&) override { hovered = true; repaint(); }
        void mouseExit(const juce::MouseEvent&) override { hovered = false; repaint(); }
        void mouseUp(const juce::MouseEvent& event) override
        { if (event.mouseWasClicked() && select) select(item.index); }
    private:
        void paintFallback(juce::Graphics& g, juce::Rectangle<float> area)
        {
            g.setGradientFill(juce::ColourGradient(palette.token("panel_elevated"), area.getX(), area.getY(),
                item.accent.withAlpha(0.75f), area.getRight(), area.getBottom(), false));
            g.fillRoundedRectangle(area, 6.0f); g.setColour(palette.token("text_primary").withAlpha(0.72f));
            g.setFont(makeThemeFont(palette, 15.0f, false, true));
            g.drawText("PPGU  /  " + item.family, area, juce::Justification::centred, true);
        }
        Skin item; PPGUThemeManager::Palette palette; bool selected = false, hovered = false;
        std::function<void(int)> select;
    };

    class Grid final : public juce::Component
    {
    public:
        void setPalette(const PPGUThemeManager::Palette& value) { for (auto& card : cards) card->setPalette(value); }
        void clearCards() { cards.clear(); }
        void addCard(std::unique_ptr<Card> card) { addAndMakeVisible(*card); cards.push_back(std::move(card)); }
        void setSelectedIndex(int index)
        { for (auto& card : cards) card->setSelected(card->getIndex() == index); }
        void resized() override
        {
            constexpr int gap = 12, minCardWidth = 205, cardHeight = 136;
            const int columns = juce::jmax(1, (getWidth() - gap) / (minCardWidth + gap));
            const int cardWidth = juce::jmax(160, (getWidth() - gap * (columns + 1)) / columns);
            for (int i = 0; i < static_cast<int>(cards.size()); ++i)
            {
                const int column = i % columns, row = i / columns;
                cards[static_cast<size_t>(i)]->setBounds(gap + column * (cardWidth + gap),
                    gap + row * (cardHeight + gap), cardWidth, cardHeight);
            }
        }
    private: std::vector<std::unique_ptr<Card>> cards;
    };

    void selectDraft(int index)
    {
        if (selection.select(index))
        {
            grid.setSelectedIndex(index);
            favoriteButton.setButtonText(favorites.contains(skinIdForIndex(index)) ? "★ FAVORITE" : "☆ FAVORITE");
        }
    }
    juce::String skinIdForIndex(int index) const
    {
        for (const auto& skin : skins) if (skin.index == index) return skin.id;
        return {};
    }
    void toggleFavorite()
    {
        const auto id = skinIdForIndex(selection.draftIndex());
        if (id.isEmpty()) return;
        const int existing = favorites.indexOf(id);
        if (existing >= 0) favorites.remove(existing); else favorites.add(id);
        if (saveFavorites) saveFavorites(favorites);
        favoriteButton.setButtonText(existing >= 0 ? "☆ FAVORITE" : "★ FAVORITE");
        rebuildCards();
    }
    void previewDraft() { if (preview && preview(selection.draftIndex())) selection.markPreviewed(); }
    void applyDraft()
    {
        const int index = selection.draftIndex();
        if (apply && apply(index) && selection.commit()) finalized = true;
    }
    void cancelDraft()
    {
        if (finalized) return;
        const int restoreIndex = selection.cancel(); finalized = true;
        if (cancel) cancel(restoreIndex);
    }
    void rebuildCards()
    {
        grid.clearCards(); visibleIndices.clear();
        const auto query = search.getText().trim().toLowerCase();
        const int selectedFilter = familyFilter.getSelectedId();
        const bool favoritesOnly = selectedFilter == 2;
        for (const auto& item : skins)
        {
            const bool isFavorite = favorites.contains(item.id);
            if (favoritesOnly && !isFavorite) continue;
            auto cardItem = item; cardItem.favorite = isFavorite;
            const auto haystack = (item.name + " " + item.family + " " + item.layout).toLowerCase();
            if (query.isNotEmpty() && !haystack.contains(query)) continue;
            visibleIndices.push_back(item.index);
            auto safe = juce::Component::SafePointer<PPGUSkinGalleryPanel>(this);
            grid.addCard(std::make_unique<Card>(cardItem, palette, selection.draftIndex(),
                [safe](int index) { if (safe != nullptr) safe->selectDraft(index); }));
        }
        const int visibleCount = grid.getNumChildComponents();
        countLabel.setText(juce::String(visibleCount) + " / " + juce::String(skins.size()) + " THEMES",
                           juce::dontSendNotification);
        previewButton.setEnabled(selection.draftIndex() > 0);
        applyButton.setEnabled(selection.draftIndex() > 0);
        favoriteButton.setEnabled(selection.draftIndex() > 0);
        favoriteButton.setButtonText(favorites.contains(skinIdForIndex(selection.draftIndex())) ? "★ FAVORITE" : "☆ FAVORITE");
        constexpr int gap = 12, minCardWidth = 205, cardHeight = 136;
        const int columns = juce::jmax(1, (viewport.getWidth() - gap) / (minCardWidth + gap));
        const int rows = (visibleCount + columns - 1) / columns;
        grid.setSize(juce::jmax(1, viewport.getWidth()),
                     juce::jmax(viewport.getHeight(), gap + rows * (cardHeight + gap)));
        grid.resized();
    }

    std::vector<Skin> skins; PPGUThemeManager::Palette palette;
    ppgu::ui::SkinGallerySelection selection;
    juce::StringArray favorites;
    std::function<void(const juce::StringArray&)> saveFavorites;
    std::function<bool(int)> preview, apply;
    std::function<void(int)> cancel;
    bool finalized = false;
    std::vector<int> visibleIndices;
    juce::Label heading, subtitle, countLabel;
    juce::TextEditor search; juce::ComboBox familyFilter;
    juce::TextButton previewButton, favoriteButton, applyButton, cancelButton;
    Grid grid; juce::Viewport viewport;
};;

// UI-only settings panel: controls the auxiliary workspace and theme preference.
class PPGUSettingsPanel final : public juce::Component, public PPGUThemeAwarePanel
{
public:
    PPGUSettingsPanel(PPGUThemeManager::Palette paletteIn, float panelScaleIn, int panelGapIn,
                      std::function<void(float)> scaleChangedIn,
                      std::function<void(int)> gapChangedIn,
                      std::function<void()> restoreThemeIn,
                      std::function<void()> openGalleryIn)
        : palette(std::move(paletteIn)), scaleChanged(std::move(scaleChangedIn)),
          gapChanged(std::move(gapChangedIn)), restoreTheme(std::move(restoreThemeIn)),
          openGallery(std::move(openGalleryIn))
    {
        heading.setText("WORKSPACE SETTINGS", juce::dontSendNotification);
        heading.setFont(makeThemeFont(palette, 16.0f, false, true));
        heading.setColour(juce::Label::textColourId, palette.token("text_primary"));
        addAndMakeVisible(heading);

        description.setText("These options affect auxiliary panels and visual preferences only. "
                             "Audio processing, MIDI and instrument parameters are not changed.",
                             juce::dontSendNotification);
        description.setColour(juce::Label::textColourId, palette.token("text_secondary"));
        description.setFont(makeThemeFont(palette, 10.0f, false, false));
        description.setJustificationType(juce::Justification::topLeft);
        addAndMakeVisible(description);

        scaleLabel.setText("AUXILIARY PANEL SCALE  /  1x · 2x · 3x", juce::dontSendNotification);
        gapLabel.setText("SPACE BETWEEN PANELS", juce::dontSendNotification);
        for (auto* label : { &scaleLabel, &gapLabel })
        {
            label->setFont(makeThemeFont(palette, 9.5f, false, true));
            label->setColour(juce::Label::textColourId, palette.token("accent"));
            addAndMakeVisible(*label);
        }

        configureSlider(scaleSlider, 0.5, 3.0, 0.05, panelScaleIn);
        scaleSlider.setTextValueSuffix(" x");
        scaleSlider.onValueChange = [this]
        {
            if (scaleChanged)
                scaleChanged(static_cast<float>(scaleSlider.getValue()));
        };
        addAndMakeVisible(scaleSlider);

        configureSlider(gapSlider, 0.0, 32.0, 1.0, panelGapIn);
        gapSlider.setTextValueSuffix(" px");
        gapSlider.onValueChange = [this]
        {
            if (gapChanged)
                gapChanged(static_cast<int>(std::lround(gapSlider.getValue())));
        };
        addAndMakeVisible(gapSlider);

        restoreButton.setButtonText("RESTORE NEON STAGE DEFAULT");
        restoreButton.setColour(juce::TextButton::buttonColourId, palette.token("panel_elevated"));
        restoreButton.setColour(juce::TextButton::textColourOffId, palette.token("text_primary"));
        restoreButton.onClick = [this] { if (restoreTheme) restoreTheme(); };
        addAndMakeVisible(restoreButton);

        galleryButton.setButtonText("OPEN SKIN GALLERY");
        galleryButton.setColour(juce::TextButton::buttonColourId, palette.token("accent"));
        galleryButton.setColour(juce::TextButton::textColourOffId, palette.token("window_bg"));
        galleryButton.onClick = [this] { if (openGallery) openGallery(); };
        addAndMakeVisible(galleryButton);
    }

    void setThemePalette(const PPGUThemeManager::Palette& value) override
    {
        palette = value;
        heading.setFont(makeThemeFont(palette, 16.0f, false, true));
        description.setFont(makeThemeFont(palette, 10.0f));
        scaleLabel.setFont(makeThemeFont(palette, 9.5f, false, true));
        gapLabel.setFont(makeThemeFont(palette, 9.5f, false, true));
        heading.setColour(juce::Label::textColourId, palette.token("text_primary"));
        description.setColour(juce::Label::textColourId, palette.token("text_secondary"));
        scaleLabel.setColour(juce::Label::textColourId, palette.token("accent"));
        gapLabel.setColour(juce::Label::textColourId, palette.token("accent"));
        configureSlider(scaleSlider, 0.5, 3.0, 0.05, scaleSlider.getValue());
        configureSlider(gapSlider, 0.0, 32.0, 1.0, gapSlider.getValue());
        restoreButton.setColour(juce::TextButton::buttonColourId, palette.token("panel_elevated"));
        restoreButton.setColour(juce::TextButton::textColourOffId, palette.token("text_primary"));
        galleryButton.setColour(juce::TextButton::buttonColourId, palette.token("accent"));
        galleryButton.setColour(juce::TextButton::textColourOffId, palette.token("window_bg"));
        repaint();
    }

    void paint(juce::Graphics& g) override
    {
        auto bounds = getLocalBounds();
        g.fillAll(palette.token("window_bg"));
        drawThemeArtworkLayers(g, bounds, palette, 0.12f, 0.34f, 0.04f);

        const auto drawSettingCard = [&g, this](juce::Rectangle<int> card, bool highlighted)
        {
            if (card.isEmpty())
                return;
            auto area = card.toFloat();
            g.setColour(palette.token("panel_elevated").withAlpha(0.82f));
            g.fillRoundedRectangle(area, 7.0f);
            g.setColour((highlighted ? palette.token("accent") : palette.token("control_border"))
                            .withAlpha(highlighted ? 0.42f : 0.72f));
            g.drawRoundedRectangle(area.reduced(0.5f), 7.0f, 1.0f);
        };
        drawSettingCard(scaleSlider.getBounds().expanded(5, 4), false);
        drawSettingCard(gapSlider.getBounds().expanded(5, 4), false);
        drawSettingCard(restoreButton.getBounds().expanded(4, 3), false);
        drawSettingCard(galleryButton.getBounds().expanded(4, 3), true);


    }

    void resized() override
    {
        auto area = getLocalBounds().reduced(12);
        heading.setBounds(area.removeFromTop(20));
        description.setBounds(area.removeFromTop(24));
        area.removeFromTop(2);
        scaleLabel.setBounds(area.removeFromTop(14));
        scaleSlider.setBounds(area.removeFromTop(20));
        area.removeFromTop(2);
        gapLabel.setBounds(area.removeFromTop(14));
        gapSlider.setBounds(area.removeFromTop(20));
        area.removeFromTop(2);
        restoreButton.setBounds(area.removeFromTop(22).removeFromLeft(270));
        area.removeFromTop(2);
        galleryButton.setBounds(area.removeFromTop(22).removeFromLeft(220));
    }

private:
    void configureSlider(juce::Slider& slider, double minimum, double maximum,
                         double interval, double value)
    {
        slider.setSliderStyle(juce::Slider::LinearHorizontal);
        slider.setTextBoxStyle(juce::Slider::TextBoxRight, false, 52, 18);
        slider.setRange(minimum, maximum, interval);
        slider.setValue(juce::jlimit(minimum, maximum, value), juce::dontSendNotification);
        slider.setColour(juce::Slider::trackColourId, palette.token("control_border"));
        slider.setColour(juce::Slider::backgroundColourId, palette.token("control_bg"));
        slider.setColour(juce::Slider::thumbColourId, palette.token("accent"));
        slider.setColour(juce::Slider::textBoxTextColourId, palette.token("text_primary"));
        slider.setColour(juce::Slider::textBoxBackgroundColourId, palette.token("control_bg"));
        slider.setColour(juce::Slider::textBoxOutlineColourId, palette.token("control_border"));
    }

    PPGUThemeManager::Palette palette;
    std::function<void(float)> scaleChanged;
    std::function<void(int)> gapChanged;
    std::function<void()> restoreTheme, openGallery;
    juce::Label heading, description, scaleLabel, gapLabel;
    juce::Slider scaleSlider, gapSlider;
    juce::TextButton restoreButton, galleryButton;
};

// Import panel delegates to the existing asynchronous SFZ loader and reports its real result.
class PPGUImportGuitarPanel final : public juce::Component,
                                         public PPGUThemeAwarePanel,
                                         private juce::Timer
{
public:
    explicit PPGUImportGuitarPanel(std::function<void(juce::Label*, juce::Button*)> loadActionIn,
                                  juce::String initialStatus)
        : loadAction(std::move(loadActionIn))
    {
        heading.setText("LICENSED GUITAR LIBRARY", juce::dontSendNotification);
        heading.setFont(makeThemeFont(palette, 18.0f, false, true));
        heading.setJustificationType(juce::Justification::centredLeft);
        addAndMakeVisible(heading);
        description.setText("Load one SFZ definition and its referenced WAV samples. "
                            "The report below lists actual regions, samples, warnings and errors.",
                            juce::dontSendNotification);
        description.setJustificationType(juce::Justification::topLeft);
        description.setColour(juce::Label::textColourId, palette.token("text_secondary"));
        addAndMakeVisible(description);
        status.setText(initialStatus.isNotEmpty() ? initialStatus
            : juce::String("No SFZ library loaded in this session."), juce::dontSendNotification);
        status.setJustificationType(juce::Justification::topLeft);
        status.setColour(juce::Label::textColourId, palette.token("lcd_text"));
        addAndMakeVisible(status);
        loadButton.setButtonText("LOAD SFZ");
        loadButton.onClick = [this] { if (loadAction) loadAction(&status, &loadButton); };
        addAndMakeVisible(loadButton);
        startTimerHz(8);
    }
    void setThemePalette(const PPGUThemeManager::Palette& value) override
    {
        palette = value;
        heading.setFont(makeThemeFont(palette, 18.0f, false, true));
        description.setFont(makeThemeFont(palette, 10.0f));
        status.setFont(makeThemeFont(palette, 10.0f));
        heading.setColour(juce::Label::textColourId, palette.token("text_primary"));
        description.setColour(juce::Label::textColourId, palette.token("text_secondary"));
        status.setColour(juce::Label::textColourId, palette.token("lcd_text"));
        loadButton.setColour(juce::TextButton::buttonColourId, palette.token("accent"));
        loadButton.setColour(juce::TextButton::textColourOffId, palette.token("window_bg"));
        repaint();
    }

    void paint(juce::Graphics& g) override
    {
        g.fillAll(palette.token("window_bg"));
        drawThemeArtworkLayers(g, getLocalBounds(), palette, 0.12f, 0.34f, 0.04f);

        // This indicator mirrors the real asynchronous SFZ loader status text.
        // It is steady-state only: no decorative blinking or simulated progress.
        const auto loadButtonBounds = loadButton.getBounds();
        const auto ledBounds = juce::Rectangle<float>(
            static_cast<float>(loadButtonBounds.getRight() + 18),
            static_cast<float>(loadButtonBounds.getY() + loadButtonBounds.getHeight() * 0.5f - 5),
            10.0f, 10.0f);
        juce::Colour led = palette.token("led_off");
        juce::String stateText = "STANDBY";
        if (loadState == LoadState::loading)
        {
            led = palette.token("accent");
            stateText = "LOADING";
        }
        else if (loadState == LoadState::ready)
        {
            led = palette.token("success");
            stateText = "READY";
        }
        else if (loadState == LoadState::error)
        {
            led = palette.token("danger");
            stateText = "ERROR";
        }
        if (loadState != LoadState::standby)
        {
            g.setColour(led.withAlpha(0.25f));
            g.fillEllipse(ledBounds.expanded(4.0f));
        }
        g.setColour(led);
        g.fillEllipse(ledBounds);
        g.setColour(palette.token("control_border"));
        g.drawEllipse(ledBounds, 1.0f);
        g.setColour(palette.token("text_secondary"));
        g.setFont(makeThemeFont(palette, 9.0f, false, true));
        g.drawText(stateText, loadButton.getRight() + 34, loadButton.getY(),
                   juce::jmax(72, getWidth() - loadButton.getRight() - 52),
                   loadButton.getHeight(), juce::Justification::centredLeft);
    }

    void resized() override
    {
        auto area = getLocalBounds().reduced(18);
        heading.setBounds(area.removeFromTop(34));
        area.removeFromTop(12);
        description.setBounds(area.removeFromTop(64));
        area.removeFromTop(18);
        loadButton.setBounds(area.removeFromTop(42).removeFromLeft(180));
        area.removeFromTop(16);
        status.setBounds(area.removeFromTop(juce::jmax(120, area.getHeight())));
    }
private:
    enum class LoadState { standby, loading, ready, error };

    void timerCallback() override
    {
        const auto message = status.getText().trim();
        LoadState next = LoadState::standby;
        if (!loadButton.isEnabled() || message.startsWithIgnoreCase("Loading SFZ")
            || message.startsWithIgnoreCase("LOADING SFZ"))
            next = LoadState::loading;
        else if (message.startsWithIgnoreCase("READY")
                 || message.startsWithIgnoreCase("SAVED LIBRARY"))
            next = LoadState::ready;
        else if (message.startsWithIgnoreCase("LIBRARY FILE NOT FOUND")
                 || message.containsIgnoreCase("FAILED")
                 || message.containsIgnoreCase("ERROR")
                 || message.containsIgnoreCase("NOT FOUND"))
            next = LoadState::error;
        else if (message.isNotEmpty()
                 && message != "No SFZ library loaded in this session.")
            next = LoadState::error;
        if (next != loadState)
        {
            loadState = next;
            repaint();
        }
    }

    PPGUThemeManager::Palette palette;
    std::function<void(juce::Label*, juce::Button*)> loadAction;
    juce::Label heading, description, status;
    juce::TextButton loadButton;
    LoadState loadState = LoadState::standby;
};

// Compact live harmony monitor. It observes the existing MIDI keyboard state and
// scale parameters only; it never writes to APVTS or changes processor behaviour.
class PPGUPerformanceDisplay final : public juce::Component, private juce::Timer
{
public:
    explicit PPGUPerformanceDisplay(PopPunkGuitarUltimateAudioProcessor& processorIn)
        : processor(processorIn), parameters(processorIn.parameters)
    {
        setOpaque(false);
        refreshState();
        startTimerHz(20);
    }

    void setPalette(const PPGUThemeManager::Palette& value)
    {
        palette = value;
        repaint();
    }

    void paint(juce::Graphics& g) override
    {
        auto bounds = getLocalBounds().toFloat();
        g.setGradientFill(juce::ColourGradient(palette.tokens.panelElevated,
                                               bounds.getX(), bounds.getY(),
                                               palette.tokens.panel,
                                               bounds.getX(), bounds.getBottom(), false));
        g.fillRoundedRectangle(bounds, 9.0f);
        drawThemeArtworkLayers(g, getLocalBounds(), palette, 0.045f, 0.0f, 0.0f);
        g.setColour(palette.tokens.controlBorder.withAlpha(0.9f));
        g.drawRoundedRectangle(bounds.reduced(0.5f), 9.0f, 1.0f);
        g.setColour(palette.tokens.accent);
        g.fillRoundedRectangle(bounds.getX() + 1.0f, bounds.getY() + 8.0f, 3.0f,
                               juce::jmax(8.0f, bounds.getHeight() - 16.0f), 1.5f);

        auto area = getLocalBounds().reduced(14, 5);
        auto harmony = area.removeFromLeft(190);
        g.setColour(palette.tokens.textSecondary);
        g.setFont(makeThemeFont(palette, 8.5f, false, true));
        g.drawText("LIVE HARMONY", harmony.removeFromTop(13), juce::Justification::left);
        g.setColour(palette.tokens.accent);
        g.setFont(makeThemeFont(palette, 23.0f, false, true));
        g.drawFittedText(chordText, harmony, juce::Justification::centredLeft, 1);

        area.removeFromLeft(10);
        auto keyArea = area.removeFromRight(148);
        g.setColour(palette.tokens.textSecondary);
        g.setFont(makeThemeFont(palette, 8.5f, false, true));
        g.drawText("SCALE / KEY", keyArea.removeFromTop(13), juce::Justification::left);
        g.setColour(palette.tokens.textPrimary);
        g.setFont(makeThemeFont(palette, 12.0f, false, true));
        g.drawFittedText(keyText, keyArea, juce::Justification::centredLeft, 1);

        area.removeFromRight(8);
        g.setColour(palette.tokens.textSecondary);
        g.setFont(makeThemeFont(palette, 8.5f, false, true));
        auto notesHeading = area.removeFromTop(13);
        g.drawText("MIDI INPUT  /  " + juce::String(heldNoteCount) + " NOTES HELD", notesHeading, juce::Justification::left);
        const float midiLedX = static_cast<float>(notesHeading.getRight() - 9);
        const float midiLedY = static_cast<float>(notesHeading.getCentreY());
        const auto midiLedColour = midiActive ? palette.token("accent") : palette.token("led_off");
        if (midiActive)
        {
            g.setColour(midiLedColour.withAlpha(0.28f));
            g.fillEllipse(midiLedX - 6.0f, midiLedY - 6.0f, 12.0f, 12.0f);
        }
        g.setColour(midiLedColour);
        g.fillEllipse(midiLedX - 2.5f, midiLedY - 2.5f, 5.0f, 5.0f);
        g.setColour(palette.tokens.textPrimary);
        g.setFont(makeThemeFont(palette, 12.0f, false, false));
        g.drawFittedText(notesText, area, juce::Justification::centredLeft, 1);
    }

private:
    struct ChordShape
    {
        const char* suffix;
        std::vector<int> intervals;
        int priority;
    };

    static juce::String pitchName(int pitchClass)
    {
        static const char* names[] = {
            "C", "C#", "D", "D#", "E", "F",
            "F#", "G", "G#", "A", "A#", "B"
        };
        return names[juce::jlimit(0, 11, pitchClass)];
    }

    static juce::String noteName(int midiNote)
    {
        return pitchName(midiNote % 12) + juce::String(midiNote / 12 - 1);
    }

    juce::String detectChord(const std::vector<int>& notes) const
    {
        if (notes.empty())
            return "-";

        if (notes.size() == 1)
            return noteName(notes.front());

        std::array<bool, 12> present {};
        int pitchClassCount = 0;
        for (const auto note : notes)
        {
            const int pc = note % 12;
            if (!present[static_cast<size_t>(pc)])
            {
                present[static_cast<size_t>(pc)] = true;
                ++pitchClassCount;
            }
        }

        static const std::vector<ChordShape> shapes {
            { "m",    { 0, 3, 7 },       12 },
            { "maj",  { 0, 4, 7 },       11 },
            { "m7",   { 0, 3, 7, 10 },  10 },
            { "7",    { 0, 4, 7, 10 },   9 },
            { "maj7", { 0, 4, 7, 11 },   9 },
            { "sus2", { 0, 2, 7 },       8 },
            { "sus4", { 0, 5, 7 },       8 },
            { "dim",  { 0, 3, 6 },       7 },
            { "aug",  { 0, 4, 8 },       7 },
            { "m7b5", { 0, 3, 6, 10 },   6 },
            { "dim7", { 0, 3, 6, 9 },    6 },
            { "6",    { 0, 4, 7, 9 },    5 },
            { "m6",   { 0, 3, 7, 9 },    5 },
            { "mMaj7",{ 0, 3, 7, 11 },  4 },
            { "5",    { 0, 7 },          2 }
        };

        const int bassPc = notes.front() % 12;
        int bestScore = std::numeric_limits<int>::min();
        juce::String best;

        for (int root = 0; root < 12; ++root)
        {
            for (const auto& shape : shapes)
            {
                bool complete = true;
                for (const auto interval : shape.intervals)
                    if (!present[static_cast<size_t>((root + interval) % 12)])
                    {
                        complete = false;
                        break;
                    }

                if (!complete)
                    continue;

                const int extras = pitchClassCount - static_cast<int>(shape.intervals.size());
                const int score = 100 - extras * 18 + shape.priority + (root == bassPc ? 4 : 0);
                if (score > bestScore)
                {
                    bestScore = score;
                    best = pitchName(root) + shape.suffix;
                }
            }
        }

        if (best.isNotEmpty())
            return best;

        return pitchName(bassPc) + "  /  " + juce::String(pitchClassCount) + " tones";
    }

    void refreshState()
    {
        std::vector<int> held;
        held.reserve(8);
        for (int note = 0; note < 128; ++note)
        {
            bool isHeld = false;
            isHeld = processor.isMidiNoteHeld(note);
            if (isHeld)
                held.push_back(note);
        }

        juce::StringArray noteNames;
        for (size_t i = 0; i < held.size() && i < 6; ++i)
            noteNames.add(noteName(held[i]));
        if (held.size() > 6)
            noteNames.add("+" + juce::String(static_cast<int>(held.size() - 6)));

        const auto newChord = detectChord(held);
        const auto newNotes = held.empty() ? juce::String("Waiting for MIDI input")
                                           : noteNames.joinIntoString("   /   ");
        const bool newMidiActive = !held.empty();

        auto* rootParameter = parameters.getRawParameterValue("scaleRoot");
        auto* modeParameter = parameters.getRawParameterValue("scaleMode");
        const int root = rootParameter != nullptr
            ? juce::jlimit(0, 11, static_cast<int>(rootParameter->load(std::memory_order_relaxed))) : 0;
        const int mode = modeParameter != nullptr
            ? juce::jlimit(0, 2, static_cast<int>(modeParameter->load(std::memory_order_relaxed))) : 0;
        const auto newKey = mode == 1 ? pitchName(root) + " MAJOR"
                         : mode == 2 ? pitchName(root) + " MINOR"
                                     : juce::String("CHROMATIC");

        const int newHeldNoteCount = static_cast<int>(held.size());
        if (newChord != chordText || newNotes != notesText
            || newKey != keyText || newMidiActive != midiActive
            || newHeldNoteCount != heldNoteCount)
        {
            chordText = newChord;
            notesText = newNotes;
            keyText = newKey;
            midiActive = newMidiActive;
            heldNoteCount = newHeldNoteCount;
            repaint();
        }
    }

    void timerCallback() override { refreshState(); }

    PopPunkGuitarUltimateAudioProcessor& processor;
    juce::AudioProcessorValueTreeState& parameters;
    PPGUThemeManager::Palette palette;
    juce::String chordText { "—" };
    juce::String notesText { "Waiting for MIDI input" };
    juce::String keyText { "CHROMATIC" };
    bool midiActive = false;
    int heldNoteCount = 0;
};


namespace
{
class PPGUNeonVUMeter final : public juce::Component
{
public:
    void setPalette(const PPGUThemeManager::Palette& value) { palette = value; repaint(); }
    void setLevel(float value)
    {
        const auto next = juce::jlimit(0.0f, 1.0f, value);
        if (std::abs(next - level) > 0.002f)
        {
            level = next;
            repaint();
        }
    }

    void paint(juce::Graphics& g) override
    {
        auto area = getLocalBounds().toFloat().reduced(2.0f);
        if (area.isEmpty())
            return;

        // Skin-1 provides eight authored VU states (1..8 active segments) in
        // the meters/sliders atlas. Select the closest authored state for the
        // live peak level; keep the semantic vector meter for all other skins
        // and for the true zero state, which has no active atlas frame.
        if (palette.id == "skin-053" && palette.metersSlidersSpriteSheet.isValid())
        {
            const int activeSegments = juce::jlimit(0, 8, juce::roundToInt(level * 8.0f));
            if (activeSegments > 0)
            {
                constexpr int sourceX = 43;
                constexpr int sourceY = 34;
                constexpr int frameStride = 117;
                constexpr int sourceWidth = 82;
                constexpr int sourceHeight = 286;
                const int frameX = sourceX + (activeSegments - 1) * frameStride;
                g.setImageResamplingQuality(juce::Graphics::highResamplingQuality);
                g.drawImage(palette.metersSlidersSpriteSheet,
                            getLocalBounds().getX(), getLocalBounds().getY(),
                            getLocalBounds().getWidth(), getLocalBounds().getHeight(),
                            frameX, sourceY, sourceWidth, sourceHeight);
                return;
            }
        }

        constexpr int segments = 20;
        constexpr float gap = 2.0f;
        const float segmentHeight = juce::jmax(1.0f,
            (area.getHeight() - gap * static_cast<float>(segments - 1)) / static_cast<float>(segments));
        const int activeCount = juce::roundToInt(level * static_cast<float>(segments));
        for (int i = 0; i < segments; ++i)
        {
            const int levelIndex = segments - 1 - i;
            auto segment = juce::Rectangle<float>(area.getX(),
                area.getY() + static_cast<float>(i) * (segmentHeight + gap),
                area.getWidth(), segmentHeight);
            const float fraction = static_cast<float>(levelIndex) / static_cast<float>(segments);
            // Meter thresholds use the active skin's semantic palette tokens,
            // not fixed NEON-only RGB values. This keeps all 16 themes coherent.
            const auto colour = fraction >= 0.92f ? palette.token("danger")
                : fraction >= 0.80f ? palette.token("warning")
                : fraction >= 0.60f ? palette.token("highlight")
                                    : palette.token("success");
            const bool lit = i < activeCount;
            g.setColour(lit ? colour : palette.token("control_bg").brighter(0.04f));
            g.fillRoundedRectangle(segment, 1.2f);
            if (lit)
            {
                const float intensity = fraction >= 0.92f ? 0.34f
                    : (fraction >= 0.80f ? 0.27f : 0.20f);
                g.setColour(colour.withAlpha(intensity));
                g.drawRoundedRectangle(segment.expanded(0.9f), 1.5f, 1.0f);
                // A fine inner highlight improves readability at compact sizes.
                g.setColour(palette.token("text_primary").withAlpha(0.10f));
                g.drawLine(segment.getX() + 2.0f, segment.getY() + 1.0f,
                           segment.getRight() - 2.0f, segment.getY() + 1.0f, 0.6f);
            }
        }
    }

private:
    PPGUThemeManager::Palette palette;
    float level = 0.0f;
};

class PPGUOutputMeter final : public juce::Component, private juce::Timer
{
public:
    explicit PPGUOutputMeter(PopPunkGuitarUltimateAudioProcessor& source) : processor(source)
    {
        setOpaque(false);
        left.setPalette(palette);
        right.setPalette(palette);
        addAndMakeVisible(left);
        addAndMakeVisible(right);
        startTimerHz(30);
    }

    void setPalette(const PPGUThemeManager::Palette& value)
    {
        palette = value;
        left.setPalette(value);
        right.setPalette(value);
        repaint();
    }

    void paint(juce::Graphics& g) override
    {
        auto area = getLocalBounds().toFloat();
        g.setColour(palette.token("control_bg"));
        g.fillRoundedRectangle(area, 7.0f);
        g.setColour(palette.token("control_border"));
        g.drawRoundedRectangle(area.reduced(0.5f), 7.0f, 1.0f);
        g.setColour(palette.token("text_secondary"));
        g.setFont(makeThemeFont(palette, 8.0f, false, true));
        g.drawText("OUTPUT", getLocalBounds().removeFromTop(15), juce::Justification::centred);
        g.setFont(makeThemeFont(palette, 7.0f, false, true));
        g.drawText("L", left.getBounds().translated(0, -12), juce::Justification::centredTop);
        g.drawText("R", right.getBounds().translated(0, -12), juce::Justification::centredTop);
    }

    void resized() override
    {
        auto area = getLocalBounds().reduced(5);
        area.removeFromTop(14);
        const int gap = 5;
        const int width = juce::jmax(1, (area.getWidth() - gap) / 2);
        left.setBounds(area.removeFromLeft(width));
        area.removeFromLeft(gap);
        right.setBounds(area);
    }

private:
    static float toDisplayLevel(float peak) noexcept
    {
        const auto db = juce::Decibels::gainToDecibels(juce::jmax(0.000001f, peak), -60.0f);
        return juce::jlimit(0.0f, 1.0f, (db + 48.0f) / 51.0f);
    }

    void timerCallback() override
    {
        const float leftPeak = toDisplayLevel(processor.getOutputPeak(0));
        const float rightPeak = toDisplayLevel(processor.getOutputPeak(1));
        leftLevel = juce::jmax(leftPeak, leftLevel * 0.91f);
        rightLevel = juce::jmax(rightPeak, rightLevel * 0.91f);
        left.setLevel(leftLevel);
        right.setLevel(rightLevel);
    }

    PopPunkGuitarUltimateAudioProcessor& processor;
    PPGUThemeManager::Palette palette;
    PPGUNeonVUMeter left, right;
    float leftLevel = 0.0f, rightLevel = 0.0f;
};

class PPGUFXEditPanel final : public juce::Component,
                                  public PPGUThemeAwarePanel,
                                  private juce::Timer
{
public:
    explicit PPGUFXEditPanel(PopPunkGuitarUltimateAudioProcessor& source, int initialEffect)
        : apvts(source.parameters), outputMeter(source)
    {
        groups = {
            { "COMPRESSOR", "compressorOn", { { "THRESHOLD", "compressorThreshold" }, { "RATIO", "compressorRatio" }, { "ATTACK", "compressorAttack" }, { "RELEASE", "compressorRelease" }, { "AMOUNT", "compressorAmount" } } },
            { "EQ", "eqOn", { { "LOW", "eqLow" }, { "MID", "eqMid" }, { "HIGH", "eqHigh" }, { "LOW FREQ", "eqLowFreq" }, { "MID FREQ", "eqMidFreq" }, { "MID Q", "eqMidQ" }, { "HIGH FREQ", "eqHighFreq" } } },
            { "DISTORTION", "distortionOn", { { "DRIVE", "distortionDrive" }, { "TONE", "distortionTone" }, { "MIX", "distortionMix" } } },
            { "CHORUS", "chorusOn", { { "RATE", "chorusRate" }, { "DEPTH", "chorusDepth" }, { "MIX", "chorusMix" } } },
            { "FLANGER", "flangerOn", { { "RATE", "flangerRate" }, { "DEPTH", "flangerDepth" }, { "FEEDBACK", "flangerFeedback" }, { "MIX", "flangerMix" } } },
            { "DELAY", "delayOn", { { "TIME", "delayTime" }, { "FEEDBACK", "delayFeedback" }, { "MIX", "delayMix" } } },
            { "REVERB", "reverbOn", { { "ROOM", "reverbRoomSize" }, { "DAMPING", "reverbDamping" }, { "MIX", "reverbMix" } } },
            { "CABINET IR", "cabinetOn", { { "MIX", "cabinetMix" }, { "LOW CUT", "cabinetLowCut" }, { "HIGH CUT", "cabinetHighCut" } } }
        };

        title.setText("NEON STAGE  /  FX EDIT", juce::dontSendNotification);
        title.setFont(makeThemeFont(palette, 20.0f, false, true));
        title.setColour(juce::Label::textColourId, palette.token("accent"));
        addAndMakeVisible(title);

        for (size_t i = 0; i < groups.size(); ++i)
            effectSelector.addItem(groups[i].name, static_cast<int>(i + 1));
        effectSelector.setSelectedId(juce::jlimit(1, static_cast<int>(groups.size()), initialEffect + 1), juce::dontSendNotification);
        effectSelector.onChange = [this] { selectGroup(effectSelector.getSelectedId() - 1); };
        addAndMakeVisible(effectSelector);

        powerButton.setButtonText("POWER");
        powerButton.setClickingTogglesState(true);
        addAndMakeVisible(powerButton);
        graphCaption.setText("DSP RESPONSE  /  READ-ONLY TELEMETRY", juce::dontSendNotification);
        graphCaption.setColour(juce::Label::textColourId, palette.token("text_secondary"));
        addAndMakeVisible(graphCaption);
        status.setText("Controls are attached to the existing APVTS parameters.", juce::dontSendNotification);
        status.setColour(juce::Label::textColourId, palette.token("text_secondary"));
        addAndMakeVisible(status);
        addAndMakeVisible(outputMeter);

        for (size_t groupIndex = 0; groupIndex < groups.size(); ++groupIndex)
        {
            for (const auto& item : groups[groupIndex].parameters)
            {
                auto label = std::make_unique<juce::Label>();
                label->setText(item.first, juce::dontSendNotification);
                label->setColour(juce::Label::textColourId, palette.token("text_secondary"));
                label->setFont(makeThemeFont(palette, 11.0f, false, true));
                addAndMakeVisible(*label);

                auto slider = std::make_unique<juce::Slider>();
                slider->setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
                slider->setTextBoxStyle(juce::Slider::TextBoxBelow, false, 70, 18);
                slider->setColour(juce::Slider::rotarySliderFillColourId, palette.token("accent"));
                slider->setColour(juce::Slider::rotarySliderOutlineColourId, palette.token("control_border"));
                slider->setColour(juce::Slider::thumbColourId, palette.token("text_primary"));
                slider->setColour(juce::Slider::textBoxTextColourId, palette.token("text_primary"));
                addAndMakeVisible(*slider);

                auto attachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment>(apvts, item.second, *slider);
                controls.push_back({ static_cast<int>(groupIndex), std::move(label), std::move(slider), std::move(attachment) });
            }
        }
        selectGroup(effectSelector.getSelectedId() - 1);
        refreshPowerState();
        startTimerHz(10);
    }

    void setThemePalette(const PPGUThemeManager::Palette& value) override
    {
        palette = value;
        title.setFont(makeThemeFont(palette, 20.0f, false, true));
        for (auto& control : controls)
            control.label->setFont(makeThemeFont(palette, 11.0f, false, true));
        title.setColour(juce::Label::textColourId, palette.token("text_primary"));
        graphCaption.setColour(juce::Label::textColourId, palette.token("text_secondary"));
        status.setColour(juce::Label::textColourId, palette.token("text_secondary"));
        outputMeter.setPalette(palette);
        effectSelector.setColour(juce::ComboBox::backgroundColourId, palette.token("control_bg"));
        effectSelector.setColour(juce::ComboBox::textColourId, palette.token("text_primary"));
        effectSelector.setColour(juce::ComboBox::outlineColourId, palette.token("control_border"));
        effectSelector.setColour(juce::ComboBox::arrowColourId, palette.token("accent"));
        powerButton.setColour(juce::TextButton::buttonColourId, palette.token("panel_elevated"));
        powerButton.setColour(juce::TextButton::buttonOnColourId, palette.token("accent"));
        powerButton.setColour(juce::TextButton::textColourOffId, palette.token("text_primary"));
        powerButton.setColour(juce::TextButton::textColourOnId, palette.token("window_bg"));
        for (auto& control : controls)
        {
            control.label->setColour(juce::Label::textColourId, palette.token("text_secondary"));
            control.slider->setColour(juce::Slider::rotarySliderFillColourId, palette.token("accent"));
            control.slider->setColour(juce::Slider::rotarySliderOutlineColourId, palette.token("control_border"));
            control.slider->setColour(juce::Slider::thumbColourId, palette.token("text_primary"));
            control.slider->setColour(juce::Slider::textBoxTextColourId, palette.token("text_primary"));
            control.slider->setColour(juce::Slider::textBoxBackgroundColourId, palette.token("control_bg"));
            control.slider->setColour(juce::Slider::textBoxOutlineColourId, palette.token("control_border"));
        }
        repaint();
    }

    void setSelectedGroup(int index)
    {
        selectedGroup = juce::jlimit(0, static_cast<int>(groups.size()) - 1, index);
        effectSelector.setSelectedId(selectedGroup + 1, juce::dontSendNotification);
        selectGroup(selectedGroup);
    }

    void paint(juce::Graphics& g) override
    {
        g.fillAll(palette.token("window_bg"));
        drawThemeArtworkLayers(g, getLocalBounds(), palette, 0.10f, 0.32f, 0.035f);

        // The FX LED mirrors the currently selected APVTS bypass parameter.
        const auto powerBounds = powerButton.getBounds().toFloat();
        if (!powerBounds.isEmpty())
        {
            const float ledX = powerBounds.getRight() - 10.0f;
            const float ledY = powerBounds.getCentreY();
            const auto led = lastEffectEnabled ? palette.token("accent")
                                               : palette.token("led_off");
            if (lastEffectEnabled)
            {
                g.setColour(led.withAlpha(0.30f));
                g.fillEllipse(ledX - 7.0f, ledY - 7.0f, 14.0f, 14.0f);
            }
            g.setColour(led);
            g.fillEllipse(ledX - 3.0f, ledY - 3.0f, 6.0f, 6.0f);
            g.setColour(palette.token("control_border"));
            g.drawEllipse(ledX - 3.0f, ledY - 3.0f, 6.0f, 6.0f, 0.8f);
        }

        auto area = getLocalBounds().toFloat().reduced(12.0f);
        g.setColour(palette.token("control_border"));
        g.drawRoundedRectangle(area, 10.0f, 1.0f);
        if (!graphArea.isEmpty())
        {
            auto graph = graphArea.toFloat();
            g.setColour(palette.token("control_bg"));
            g.fillRoundedRectangle(graph, 8.0f);
            g.setColour(palette.token("control_border"));
            for (int i = 1; i < 5; ++i)
                g.drawHorizontalLine(graphArea.getY() + graphArea.getHeight() * i / 5, graphArea.getX(), graphArea.getRight());
            for (int i = 1; i < 9; ++i)
                g.drawVerticalLine(graphArea.getX() + graphArea.getWidth() * i / 9, graphArea.getY(), graphArea.getBottom());
            // Keep this display explicitly telemetry-gated. No response curve is
            // rendered until the processor exposes measured DSP response data.
            auto notice = graphArea.reduced(10, 4);
            g.setColour(palette.token("accent").withAlpha(0.72f));
            g.setFont(makeThemeFont(palette, 9.0f, false, true));
            g.drawFittedText("DSP RESPONSE TELEMETRY NOT EXPOSED",
                             notice, juce::Justification::centred, 1);
        }
    }

    void resized() override
    {
        auto area = getLocalBounds().reduced(20);
        title.setBounds(area.removeFromTop(34));
        auto top = area.removeFromTop(44);
        effectSelector.setBounds(top.removeFromLeft(230).reduced(2, 4));
        powerButton.setBounds(top.removeFromLeft(110).reduced(2, 4));
        graphCaption.setBounds(top);
        const int graphHeight = getHeight() >= 600 ? 140
            : (getHeight() >= 390 ? 90 : (getHeight() >= 300 ? 54 : 0));
        graphCaption.setVisible(graphHeight > 0);
        if (graphHeight > 0)
        {
            auto graphAndMeter = area.removeFromBottom(graphHeight).reduced(4, 8);
            outputMeter.setBounds(graphAndMeter.removeFromRight(62));
            graphArea = graphAndMeter;
        }
        else
        {
            graphArea = {};
            outputMeter.setBounds(juce::Rectangle<int>{});
        }
        outputMeter.setVisible(graphHeight > 0);
        status.setBounds(area.removeFromBottom(24));
        area.removeFromBottom(8);
        const int visibleCount = static_cast<int>(std::count_if(controls.begin(), controls.end(),
            [this](const Control& c) { return c.group == selectedGroup; }));
        const int columns = visibleCount > 5 ? 4 : juce::jmax(1, visibleCount);
        const int rows = (visibleCount + columns - 1) / columns;
        const int cellWidth = juce::jmax(1, area.getWidth() / columns);
        const int cellHeight = juce::jmax(1, area.getHeight() / juce::jmax(1, rows));
        int index = 0;
        for (auto& control : controls)
        {
            if (control.group != selectedGroup)
            {
                control.label->setVisible(false);
                control.slider->setVisible(false);
                continue;
            }
            control.label->setVisible(true);
            control.slider->setVisible(true);
            const int column = index % columns;
            const int row = index / columns;
            auto cell = juce::Rectangle<int>(area.getX() + column * cellWidth,
                area.getY() + row * cellHeight, cellWidth, cellHeight).reduced(6, 2);
            control.label->setBounds(cell.removeFromTop(20));
            control.slider->setBounds(cell);
            ++index;
        }
    }

private:
    struct Group
    {
        juce::String name, enabledParameter;
        std::vector<std::pair<juce::String, juce::String>> parameters;
    };
    struct Control
    {
        int group;
        std::unique_ptr<juce::Label> label;
        std::unique_ptr<juce::Slider> slider;
        std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> attachment;
    };
    void selectGroup(int index)
    {
        selectedGroup = juce::jlimit(0, static_cast<int>(groups.size()) - 1, index);
        powerAttachment.reset();
        powerAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment>(
            apvts, groups[static_cast<size_t>(selectedGroup)].enabledParameter, powerButton);
        refreshPowerState();
        resized();
        repaint();
    }

    void refreshPowerState()
    {
        const auto& group = groups[static_cast<size_t>(selectedGroup)];
        if (const auto* value = apvts.getRawParameterValue(group.enabledParameter))
        {
            const bool enabled = value->load(std::memory_order_relaxed) > 0.5f;
            const bool stateChanged = enabled != lastEffectEnabled;
            lastEffectEnabled = enabled;

            // Keep the textual state correct on first open and after changing groups,
            // even when the newly selected effect happens to be bypassed (false).
            const auto controlCount = static_cast<int>(group.parameters.size());
            const auto expectedStatus = group.name
                + (enabled ? "  /  ACTIVE" : "  /  BYPASSED")
                + "  /  " + juce::String(controlCount) + " CONTROLS";
            if (status.getText() != expectedStatus)
                status.setText(expectedStatus, juce::dontSendNotification);
            if (stateChanged)
                repaint();
        }
    }

    void timerCallback() override { refreshPowerState(); }

    PPGUThemeManager::Palette palette;
    juce::AudioProcessorValueTreeState& apvts;
    PPGUOutputMeter outputMeter;
    std::vector<Group> groups;
    std::vector<Control> controls;
    juce::Label title, graphCaption, status;
    juce::ComboBox effectSelector;
    juce::TextButton powerButton;
    std::unique_ptr<juce::AudioProcessorValueTreeState::ButtonAttachment> powerAttachment;
    juce::Rectangle<int> graphArea;
    int selectedGroup = 0;
    bool lastEffectEnabled = false;
};


class PPGUPatternSectionPanel final : public juce::Component,
                                           public PPGUThemeAwarePanel,
                                           private juce::Timer
{
public:
    PPGUPatternSectionPanel(PopPunkGuitarUltimateAudioProcessor& processorIn,
                            juce::String selectedTonePreset,
                            std::function<void()> importGuitarAction,
                            std::function<void()> openAutoChordsAction,
                            std::function<void()> openPlayingStyleWindowAction)
        : processor(processorIn), originalSection(processorIn.getSelectedSongSection()),
          tonePresetName(std::move(selectedTonePreset)), importAction(std::move(importGuitarAction)),
          autoChordsAction(std::move(openAutoChordsAction)),
          playingStyleAction(std::move(openPlayingStyleWindowAction))
    {
        title.setText("PATTERN  /  SONG SECTION ROUTING", juce::dontSendNotification);
        title.setFont(makeThemeFont(palette, 19.0f, false, true));
        addAndMakeVisible(title);
        sectionLabel.setText("SONG SECTION", juce::dontSendNotification);
        patternLabel.setText("RHYTHM CATALOG", juce::dontSendNotification);
        sourceLabel.setText("GUITAR / INSTRUMENT SOURCE", juce::dontSendNotification);
        toneLabel.setText("TONE PRESET", juce::dontSendNotification);
        performanceLabel.setText("PLAYING STYLE", juce::dontSendNotification);
        openPlayingStyle.setButtonText("OPEN PLAYING STYLE  >");
        openPlayingStyle.setTooltip("Open the coordinated second PATTERN window: playing style and verified articulations.");
        openPlayingStyle.onClick = [this] { if (playingStyleAction) playingStyleAction(); };
        addAndMakeVisible(openPlayingStyle);
        sourceValue.setJustificationType(juce::Justification::centredLeft);
        sourceValue.setText("NO SFZ INSTRUMENT LOADED", juce::dontSendNotification);
        toneValue.setJustificationType(juce::Justification::centredLeft);
        toneValue.setText(tonePresetName.isNotEmpty() ? tonePresetName : "SELECT A FACTORY PRESET",
                             juce::dontSendNotification);
        performanceValue.setJustificationType(juce::Justification::centredLeft);
        performanceValue.setText("SECOND WINDOW  /  STYLE & MAPPING STATUS",
                                 juce::dontSendNotification);
        performanceValue.setTooltip("Playing-style and articulation selection are managed in the coordinated second PATTERN window.");
        importSource.setButtonText("IMPORT GUITAR");
        importSource.onClick = [this] { if (importAction) importAction(); };
        for (auto* label : { &sectionLabel, &patternLabel, &sourceLabel, &toneLabel,
                             &performanceLabel, &sourceValue, &toneValue, &performanceValue, &status })
            addAndMakeVisible(*label);
        addAndMakeVisible(importSource);
        openAutoChords.setButtonText("OPEN AUTOCHORDS");
        openAutoChords.onClick = [this] { if (autoChordsAction) autoChordsAction(); };
        addAndMakeVisible(openAutoChords);

        for (int i = 0; i < static_cast<int>(patternCards.size()); ++i)
        {
            auto& card = patternCards[static_cast<size_t>(i)];
            card.setButtonText("PATTERN SLOT  " + juce::String(i + 1).paddedLeft('0', 2));
            card.setTooltip("Pattern slot " + juce::String(i + 1)
                + ". Selecting a slot does not claim that a recorded rhythm library is installed.");
            card.onClick = [this, i]
            {
                patternBox.setSelectedId(i + 1, juce::dontSendNotification);
                refreshPatternCards();
                updateStatus("PATTERN SLOT " + juce::String(i + 1)
                    + " selected. Press PREVIEW to audition or APPLY to assign.");
            };
            addAndMakeVisible(card);
        }
        refreshInstrumentSource();
        startTimerHz(2);
        sectionBox.addItemList({ "INTRO", "VERSE", "CHORUS", "BRIDGE", "OUTRO" }, 1);
        for (int i = 0; i < 8; ++i)
            patternBox.addItem("PATTERN " + juce::String(i + 1), i + 1);
        sectionBox.setSelectedId(processor.getSelectedSongSection() + 1, juce::dontSendNotification);
        const int assigned = processor.getSectionPatternSlot(processor.getSelectedSongSection());
        const int legacy = static_cast<int>(processor.parameters.getRawParameterValue("patternSlot")->load());
        patternBox.setSelectedId((assigned >= 0 ? assigned : legacy) + 1, juce::dontSendNotification);
        addAndMakeVisible(sectionBox);
        patternBox.setVisible(false); // Retained as the existing slot-selection model for APVTS/routing.
        refreshPatternCards();
        preview.setButtonText("PREVIEW");
        apply.setButtonText("APPLY");
        cancel.setButtonText("CANCEL");
        for (auto* button : { &preview, &apply, &cancel })
            addAndMakeVisible(*button);
        sectionBox.onChange = [this] { selectSection(); };
        patternBox.onChange = [this]
        {
            refreshPatternCards();
            updateStatus("Pattern slot selected — press PREVIEW to audition.");
        };
        preview.onClick = [this]
        {
            const int slot = patternBox.getSelectedId() - 1;
            processor.setPatternPreviewSlot(slot);
            updateStatus("PREVIEW ARMED — play a MIDI chord. Assignment is not saved.");
        };
        apply.onClick = [this]
        {
            const int section = sectionBox.getSelectedId() - 1;
            const int slot = patternBox.getSelectedId() - 1;
            if (section >= 0 && section < PopPunkGuitarUltimateAudioProcessor::songSectionCount && slot >= 0 && slot < 8)
            {
                processor.setSectionPatternSlot(section, slot);
                processor.clearPatternPreview();
                updateStatus("APPLIED — " + sectionBox.getText() + " uses PATTERN " + juce::String(slot + 1) + ".");
            }
        };
        cancel.onClick = [this]
        {
            processor.clearPatternPreview();
            processor.setSelectedSongSection(originalSection);
            sectionBox.setSelectedId(originalSection + 1, juce::dontSendNotification);
            refreshPatternSelection();
            updateStatus("CANCELLED — preview cleared; previous section restored.");
        };
        updateStatus("Choose a song section, then select a rhythm pattern.");
        setThemePalette(palette);
    }

    void setThemePalette(const PPGUThemeManager::Palette& value) override
    {
        palette = value;
        title.setFont(makeThemeFont(palette, 19.0f, false, true));
        title.setColour(juce::Label::textColourId, palette.token("text_primary"));
        for (auto* label : { &sectionLabel, &patternLabel, &sourceLabel, &toneLabel, &performanceLabel })
        {
            label->setFont(makeThemeFont(palette, 9.5f, false, true));
            label->setColour(juce::Label::textColourId, palette.token("text_secondary"));
        }
        for (auto* value : { &sourceValue, &toneValue, &performanceValue })
        {
            value->setFont(makeThemeFont(palette, 10.5f));
            value->setColour(juce::Label::textColourId, palette.token("text_primary"));
        }
        importSource.setColour(juce::TextButton::buttonColourId, palette.token("panel_elevated"));
        importSource.setColour(juce::TextButton::textColourOffId, palette.token("accent"));
        status.setFont(makeThemeFont(palette, 11.0f));
        status.setColour(juce::Label::textColourId, palette.token("accent"));
        for (auto* box : { &sectionBox, &patternBox })
        {
            box->setColour(juce::ComboBox::backgroundColourId, palette.token("control_bg"));
            box->setColour(juce::ComboBox::textColourId, palette.token("text_primary"));
            box->setColour(juce::ComboBox::outlineColourId, palette.token("control_border"));
        }
        for (auto* button : { &preview, &apply, &cancel })
        {
            button->setColour(juce::TextButton::buttonColourId, palette.token("panel_elevated"));
            button->setColour(juce::TextButton::textColourOffId, palette.token("text_primary"));
        }
        openAutoChords.setColour(juce::TextButton::buttonColourId, palette.token("panel_elevated"));
        openAutoChords.setColour(juce::TextButton::textColourOffId, palette.token("accent"));
        openPlayingStyle.setColour(juce::TextButton::buttonColourId, palette.token("panel_elevated"));
        openPlayingStyle.setColour(juce::TextButton::textColourOffId, palette.token("accent"));
        openPlayingStyle.setColour(juce::TextButton::buttonOnColourId, palette.token("accent"));

        for (auto& card : patternCards)
        {
            card.setColour(juce::TextButton::buttonColourId, palette.token("control_bg"));
            card.setColour(juce::TextButton::buttonOnColourId, palette.token("accent"));
            card.setColour(juce::TextButton::textColourOffId, palette.token("text_secondary"));
            card.setColour(juce::TextButton::textColourOnId, palette.token("window_bg"));
        }
        refreshPatternCards();
        apply.setColour(juce::TextButton::buttonColourId, palette.token("accent"));
        apply.setColour(juce::TextButton::textColourOffId, palette.token("window_bg"));
    }

    void paint(juce::Graphics& g) override
    {
        g.fillAll(palette.token("window_bg"));
        drawThemeArtworkLayers(g, getLocalBounds(), palette, 0.10f, 0.30f, 0.035f);
    }

    void resized() override
    {
        auto area = getLocalBounds().reduced(18);
        title.setBounds(area.removeFromTop(28));
        area.removeFromTop(4);

        sourceLabel.setBounds(area.removeFromTop(12));
        auto sourceRow = area.removeFromTop(25);
        importSource.setBounds(sourceRow.removeFromRight(112));
        sourceRow.removeFromRight(8);
        sourceValue.setBounds(sourceRow);

        area.removeFromTop(3);
        toneLabel.setBounds(area.removeFromTop(12));
        toneValue.setBounds(area.removeFromTop(21));
        area.removeFromTop(3);
        performanceLabel.setBounds(area.removeFromTop(12));
        auto styleRow = area.removeFromTop(25);
        openPlayingStyle.setBounds(styleRow.removeFromRight(176));
        styleRow.removeFromRight(8);
        performanceValue.setBounds(styleRow);

        area.removeFromTop(5);
        auto sectionRow = area.removeFromTop(29);
        sectionLabel.setBounds(sectionRow.removeFromLeft(112));
        sectionBox.setBounds(sectionRow.removeFromLeft(190).reduced(0, 1));

        area.removeFromTop(5);
        auto patternHeader = area.removeFromTop(24);
        patternLabel.setBounds(patternHeader.removeFromLeft(150));
        openAutoChords.setBounds(patternHeader.removeFromRight(150).reduced(0, 1));


        area.removeFromTop(3);
        const int cardGap = 7;
        const int cardHeight = juce::jmax(22, juce::jmin(31,
            (area.getHeight() - 68 - cardGap * 3) / 4));
        for (int row = 0; row < 4; ++row)
        {
            auto rowArea = area.removeFromTop(cardHeight);
            auto left = rowArea.removeFromLeft((rowArea.getWidth() - cardGap) / 2);
            rowArea.removeFromLeft(cardGap);
            auto right = rowArea;
            patternCards[static_cast<size_t>(row * 2)].setBounds(left);
            patternCards[static_cast<size_t>(row * 2 + 1)].setBounds(right);
            if (row < 3) area.removeFromTop(cardGap);
        }

        area.removeFromTop(5);
        auto footer = area.removeFromTop(30);
        preview.setBounds(footer.removeFromLeft(104));
        footer.removeFromLeft(8);
        apply.setBounds(footer.removeFromLeft(104));
        footer.removeFromLeft(8);
        cancel.setBounds(footer.removeFromLeft(104));
        status.setBounds(area.removeFromTop(28));
    }

private:
    void timerCallback() override
    {
        refreshInstrumentSource();
        refreshActiveArticulation();
    }
    void refreshInstrumentSource()
    {
        const auto currentPath = processor.getCurrentSfzFilePath();
        const auto display = currentPath.isNotEmpty()
            ? juce::File(currentPath).getFileName()
            : juce::String("NO SFZ INSTRUMENT LOADED");
        if (sourceValue.getText() != display)
            sourceValue.setText(display, juce::dontSendNotification);
        sourceValue.setTooltip(currentPath);
    }
    void refreshActiveArticulation()
    {
        const int switchNote = processor.getActiveArticulationSwitch(1);
        const auto label = processor.getActiveArticulationLabel(1);
        juce::String display;
        if (switchNote < 0)
            display = "NO RECORDED ARTICULATION MAP";
        else if (label.isNotEmpty())
            display = "ACTIVE  /  " + label + "   [KEY " + juce::String(switchNote) + "]";
        else
            display = "ACTIVE SWITCH " + juce::String(switchNote)
                + "  /  SOURCE LABEL NOT PROVIDED";
        if (performanceValue.getText() != display)
            performanceValue.setText(display, juce::dontSendNotification);
        performanceValue.setTooltip(label.isNotEmpty()
            ? "Read from the loaded SFZ sw_label metadata. Availability still depends on a matching recorded zone."
            : "The loaded SFZ declares a switch, but does not provide a matching sw_label for this position.");
    }
    void selectSection()
    {
        const int section = sectionBox.getSelectedId() - 1;
        if (section < 0 || section >= PopPunkGuitarUltimateAudioProcessor::songSectionCount)
            return;
        processor.clearPatternPreview();
        processor.setSelectedSongSection(section);
        refreshPatternSelection();
        updateStatus("Selected " + sectionBox.getText() + ". Rhythm assignment is unchanged until APPLY.");
    }
    void refreshPatternSelection()
    {
        const int section = sectionBox.getSelectedId() - 1;
        const int assigned = processor.getSectionPatternSlot(section);
        const int legacy = static_cast<int>(processor.parameters.getRawParameterValue("patternSlot")->load());
        patternBox.setSelectedId((assigned >= 0 ? assigned : legacy) + 1, juce::dontSendNotification);
        refreshPatternCards();
    }
    void refreshPatternCards()
    {
        const int selected = patternBox.getSelectedId();
        for (int i = 0; i < static_cast<int>(patternCards.size()); ++i)
            patternCards[static_cast<size_t>(i)].setToggleState(i + 1 == selected,
                                                               juce::dontSendNotification);
    }
    void updateStatus(const juce::String& message) { status.setText(message, juce::dontSendNotification); }

    PopPunkGuitarUltimateAudioProcessor& processor;
    int originalSection = 0;
    PPGUThemeManager::Palette palette;
    juce::String tonePresetName;
    std::function<void()> importAction, autoChordsAction, playingStyleAction;
    juce::Label title, sourceLabel, sourceValue, toneLabel, toneValue,
                performanceLabel, performanceValue, sectionLabel, patternLabel, status;
    juce::ComboBox sectionBox, patternBox;
    std::array<juce::TextButton, 8> patternCards;
    juce::TextButton importSource, openAutoChords, openPlayingStyle, preview, apply, cancel;
};

class PPGUPlayingStylePanel final : public juce::Component,
                                    public PPGUThemeAwarePanel,
                                    private juce::Timer
{
public:
    explicit PPGUPlayingStylePanel(PopPunkGuitarUltimateAudioProcessor& processorIn)
        : processor(processorIn)
    {
        title.setText("PLAYING STYLE  /  PERFORMANCE WORKSPACE", juce::dontSendNotification);
        subtitle.setText("PATTERN  /  ARTICULATION CATALOG", juce::dontSendNotification);
        styleLabel.setText("PLAYING STYLE", juce::dontSendNotification);
        articulationLabel.setText("ARTICULATION", juce::dontSendNotification);
        // Candidate articulation names are deliberately not rendered here.
        // A name may enter the UI only after the loaded instrument provides both
        // playable sample material and a complete, validated articulation mapping.
        styleEntry.setVisible(false);
        styleLabel.setVisible(false);
        playingStatus.setText("NO VERIFIED PLAYING MAP\nLOAD A SOURCE WITH VALIDATED PERFORMANCE DATA",
                              juce::dontSendNotification);
        playingStatus.setTooltip("Playing techniques remain unavailable until the loaded instrument provides validated sample zones and performance mappings.");
        availability.setText("NO VERIFIED ARTICULATIONS AVAILABLE", juce::dontSendNotification);
        availability.setTooltip("Articulation names are hidden until the loaded source has playable sample zones and complete, validated SFZ/MIDI mappings. A switch label alone is insufficient.");
        activeLabel.setText("ACTIVE PERFORMANCE  /  NONE VERIFIED", juce::dontSendNotification);
        sourceLabel.setText("INSTRUMENT SOURCE  /  " + (processor.getCurrentSfzFilePath().isNotEmpty()
            ? juce::File(processor.getCurrentSfzFilePath()).getFileName()
            : juce::String("NO SFZ INSTRUMENT LOADED")), juce::dontSendNotification);
        addAndMakeVisible(title);
        addAndMakeVisible(subtitle);
        styleLabel.setText("01  /  PLAYING", juce::dontSendNotification);
        articulationLabel.setText("03  /  ARTICULATIONS", juce::dontSendNotification);
        patternLabel.setText("02  /  PATTERN", juce::dontSendNotification);
        patternStatus.setText("NO VERIFIED PATTERN DATA", juce::dontSendNotification);
        addAndMakeVisible(styleLabel);
        addAndMakeVisible(playingStatus);
        addAndMakeVisible(patternLabel);
        addAndMakeVisible(patternStatus);
        addAndMakeVisible(articulationLabel);
        addAndMakeVisible(availability);
        addAndMakeVisible(activeLabel);
        addAndMakeVisible(sourceLabel);
        // Keep the candidate list empty until a source-map registry can prove availability.
        setThemePalette(palette);
        startTimerHz(2);
    }

    void setThemePalette(const PPGUThemeManager::Palette& value) override
    {
        palette = value;
        title.setFont(makeThemeFont(palette, 19.0f, false, true));
        subtitle.setFont(makeThemeFont(palette, 10.0f, false, true));
        for (auto* label : { &title, &subtitle, &styleLabel, &playingStatus, &patternLabel,
                             &patternStatus, &articulationLabel, &availability, &activeLabel, &sourceLabel })
            label->setColour(juce::Label::textColourId,
                label == &title ? palette.token("text_primary")
                : ((label == &availability || label == &patternStatus)
                    ? palette.token("warning") : palette.token("text_secondary")));
        for (auto* label : { &styleLabel, &patternLabel, &articulationLabel })
            label->setFont(makeThemeFont(palette, 10.0f, false, true));
        for (auto* label : { &playingStatus, &patternStatus, &availability, &activeLabel, &sourceLabel })
            label->setFont(makeThemeFont(palette, 11.0f));
        styleEntry.setColour(juce::TextButton::buttonColourId, palette.token("lowlight"));
        styleEntry.setColour(juce::TextButton::textColourOffId, palette.token("text_disabled"));
        styleEntry.setColour(juce::TextButton::buttonOnColourId, palette.token("accent"));
        repaint();
    }

    void paint(juce::Graphics& g) override
    {
        g.fillAll(palette.token("window_bg"));
        drawThemeArtworkLayers(g, getLocalBounds(), palette, 0.10f, 0.30f, 0.035f);
        auto area = getLocalBounds().reduced(22, 104);
        const int gap = 12;
        const int cardWidth = (area.getWidth() - gap * 2) / 3;
        const std::array<juce::Rectangle<int>, 3> cards {
            area.removeFromLeft(cardWidth), juce::Rectangle<int>(), juce::Rectangle<int>()
        };
        auto remaining = area;
        auto second = remaining.removeFromLeft(gap);
        juce::ignoreUnused(second);
        auto card2 = remaining.removeFromLeft(cardWidth);
        remaining.removeFromLeft(gap);
        auto card3 = remaining;
        const std::array<juce::Rectangle<int>, 3> panels { cards[0], card2, card3 };
        for (int i = 0; i < static_cast<int>(panels.size()); ++i)
        {
            auto card = panels[static_cast<size_t>(i)].toFloat();
            g.setColour(palette.token("shadow").withAlpha(0.55f));
            g.fillRoundedRectangle(card.translated(0.0f, 3.0f), 8.0f);
            const auto panelTop = palette.token("panel_elevated");
            const auto panelBottom = palette.token("panel");
            g.setGradientFill(juce::ColourGradient(panelTop.withAlpha(0.98f),
                card.getX(), card.getY(), panelBottom, card.getX(), card.getBottom(), false));
            g.fillRoundedRectangle(card, 8.0f);

            // Restrained metallic bevel: a soft upper edge and a darker inner
            // boundary give the card depth without introducing fake activity.
            auto inner = card.reduced(1.0f);
            g.setColour(palette.token("highlight").withAlpha(0.13f));
            g.drawRoundedRectangle(inner.removeFromTop(1.0f), 0.5f, 1.0f);
            g.setColour(palette.token("control_border").withAlpha(0.92f));
            g.drawRoundedRectangle(card, 8.0f, 1.0f);
            g.setColour(palette.token("lowlight").withAlpha(0.62f));
            g.drawRoundedRectangle(card.reduced(2.0f), 6.0f, 0.7f);

            auto top = card.removeFromTop(3.0f);
            const auto accent = i == 1 ? palette.token("accent_glow")
                                       : palette.token("accent").withAlpha(0.78f);
            g.setColour(accent.withAlpha(0.16f));
            g.fillRoundedRectangle(top.expanded(2.0f, 1.0f), 2.0f);
            g.setColour(accent);
            g.fillRoundedRectangle(top, 1.5f);
        }
    }

    void resized() override
    {
        auto area = getLocalBounds().reduced(22, 18);
        title.setBounds(area.removeFromTop(30));
        subtitle.setBounds(area.removeFromTop(18));
        area.removeFromTop(22);
        const int gap = 12;
        const int cardWidth = (area.getWidth() - gap * 2) / 3;
        auto first = area.removeFromLeft(cardWidth).reduced(14, 12);
        area.removeFromLeft(gap);
        auto second = area.removeFromLeft(cardWidth).reduced(14, 12);
        area.removeFromLeft(gap);
        auto third = area.reduced(14, 12);
        styleLabel.setBounds(first.removeFromTop(22));
        first.removeFromTop(12);
        playingStatus.setBounds(first.removeFromTop(54));
        patternLabel.setBounds(second.removeFromTop(22));
        second.removeFromTop(12);
        patternStatus.setBounds(second.removeFromTop(30));
        articulationLabel.setBounds(third.removeFromTop(22));
        third.removeFromTop(12);
        availability.setBounds(third.removeFromTop(30));
        third.removeFromTop(16);
        activeLabel.setBounds(third.removeFromTop(24));
        sourceLabel.setBounds(third.removeFromTop(24));
    }

private:
    void timerCallback() override
    {
        const auto path = processor.getCurrentSfzFilePath();
        const auto source = path.isNotEmpty() ? juce::File(path).getFileName()
                                               : juce::String("NO SFZ INSTRUMENT LOADED");
        const auto sourceText = "INSTRUMENT SOURCE  /  " + source;
        if (sourceLabel.getText() != sourceText)
            sourceLabel.setText(sourceText, juce::dontSendNotification);

        // Do not expose raw keyswitch metadata as a playable articulation.
        // Until sample-zone and mapping validation is available, no articulation
        // can be declared active or selectable.
        const juce::String activeText("ACTIVE PERFORMANCE  /  NONE VERIFIED");
        if (activeLabel.getText() != activeText)
            activeLabel.setText(activeText, juce::dontSendNotification);
    }

    PopPunkGuitarUltimateAudioProcessor& processor;
    PPGUThemeManager::Palette palette;
    juce::Label title, subtitle, styleLabel, playingStatus, patternLabel, patternStatus,
                articulationLabel, availability, activeLabel, sourceLabel;
    juce::TextButton styleEntry;
};

class PPGUChordDiagram final : public juce::Component, public PPGUThemeAwarePanel
{
public:
    PPGUChordDiagram() = default;

    void setPalette(const PPGUThemeManager::Palette& value)
    {
        palette = value;
        repaint();
    }

    void setThemePalette(const PPGUThemeManager::Palette& value) override
    {
        setPalette(value);
    }

    // fret values: -1 = muted, 0 = open, 1..4 = fretted within this diagram.
    void setVoicing(const juce::String& name, const std::array<int, 6>& positions)
    {
        chordName = name.isNotEmpty() ? name : "UNNAMED";
        hasVoicing = true;
        for (size_t i = 0; i < frets.size(); ++i)
            frets[i] = juce::jlimit(-1, 4, positions[i]);
        repaint();
    }

    void paint(juce::Graphics& g) override
    {
        const auto bounds = getLocalBounds().toFloat().reduced(1.0f);
        g.setColour(palette.token("panel"));
        g.fillRoundedRectangle(bounds, 8.0f);
        g.setColour(palette.token("control_border"));
        g.drawRoundedRectangle(bounds, 8.0f, 1.0f);

        auto heading = getLocalBounds().reduced(10, 7);
        g.setColour(palette.token("text_secondary"));
        g.setFont(makeThemeFont(palette, 8.5f, false, true));
        g.drawText("REFERENCE VOICING", heading.removeFromTop(15), juce::Justification::centredLeft);
        g.setColour(palette.token("accent"));
        g.setFont(makeThemeFont(palette, 11.0f, false, true));
        g.drawText(chordName, heading.removeFromTop(17), juce::Justification::centredLeft);

        const auto grid = getLocalBounds().reduced(20, 42);
        if (grid.getWidth() < 40 || grid.getHeight() < 35)
            return;

        // The fingering database is not connected yet. Never present the old
        // hard-coded A-major sample shape as if it matched the selected harmony.
        if (!hasVoicing)
        {
            g.setColour(palette.token("text_secondary"));
            g.setFont(makeThemeFont(palette, 9.0f, false, true));
            g.drawFittedText("NO VERIFIED GUITAR VOICING DATA",
                             grid.reduced(4), juce::Justification::centred, 2);
            return;
        }

        constexpr int stringCount = 6;
        constexpr int fretCount = 4;
        const float dx = static_cast<float>(grid.getWidth()) / static_cast<float>(stringCount - 1);
        const float dy = static_cast<float>(grid.getHeight()) / static_cast<float>(fretCount);

        const float x1 = static_cast<float>(grid.getX());
        const float x2 = static_cast<float>(grid.getRight());
        const float y1 = static_cast<float>(grid.getY());
        const float y2 = static_cast<float>(grid.getBottom());

        g.setColour(palette.token("highlight"));
        g.drawLine(x1, y1, x2, y1, 2.8f); // Nut
        g.setColour(palette.token("control_border"));
        for (int fret = 1; fret <= fretCount; ++fret)
        {
            const float y = y1 + static_cast<float>(fret) * dy;
            g.drawLine(x1, y, x2, y, 1.0f);
        }

        for (int stringIndex = 0; stringIndex < stringCount; ++stringIndex)
        {
            const float x = x1 + static_cast<float>(stringIndex) * dx;
            g.setColour(palette.token("text_secondary").withAlpha(0.78f));
            g.drawLine(x, y1, x, y2, 1.15f);

            const int fret = frets[static_cast<size_t>(stringIndex)];
            if (fret < 0)
            {
                g.setColour(palette.token("danger"));
                g.setFont(makeThemeFont(palette, 9.0f, false, true));
                g.drawText("X", juce::Rectangle<int>(juce::roundToInt(x - 5.0f),
                    juce::roundToInt(y1 - 15.0f), 10, 12), juce::Justification::centred);
            }
            else if (fret == 0)
            {
                g.setColour(palette.token("text_secondary"));
                g.drawEllipse(x - 3.0f, y1 - 9.0f, 6.0f, 6.0f, 1.0f);
            }
            else if (fret <= fretCount)
            {
                const float y = y1 + (static_cast<float>(fret) - 0.5f) * dy;
                g.setColour(palette.token("accent_glow").withAlpha(0.28f));
                g.fillEllipse(x - 7.0f, y - 7.0f, 14.0f, 14.0f);
                g.setColour(palette.token("accent"));
                g.fillEllipse(x - 4.5f, y - 4.5f, 9.0f, 9.0f);
                g.setColour(palette.token("text_primary"));
                g.drawEllipse(x - 4.5f, y - 4.5f, 9.0f, 9.0f, 0.8f);
            }
        }
    }

private:
    PPGUThemeManager::Palette palette;
    juce::String chordName { "VOICING DATA PENDING" };
    std::array<int, 6> frets {{ -1, -1, -1, -1, -1, -1 }};
    bool hasVoicing = false;
};

class PPGUAutoChordsPanel final : public juce::Component, public PPGUThemeAwarePanel,
                                  private juce::Timer
{
public:
    explicit PPGUAutoChordsPanel(juce::AudioProcessorValueTreeState& state) : apvts(state)
    {
        startTimerHz(12);
        title.setText("AUTOCHORDS  /  HARMONY SETUP", juce::dontSendNotification);
        title.setFont(makeThemeFont(palette, 20.0f, false, true));
        title.setColour(juce::Label::textColourId, palette.token("text_primary"));
        addAndMakeVisible(title);
        stateLabel.setText("PATTERN MODE ONLY: ONE HELD NOTE EXPANDS TO A SCALE-BASED TRIAD. MELODY MODE REMAINS SINGLE-NOTE.",
                            juce::dontSendNotification);
        stateLabel.setColour(juce::Label::textColourId, palette.token("text_secondary"));
        addAndMakeVisible(stateLabel);
        offButton.setButtonText("AUTOCHORDS  /  ON-OFF");
        offButton.setClickingTogglesState(true);
        offButton.setEnabled(true);
        offButton.setTooltip("Toggle single-note to diatonic-triad generation in PATTERN mode. MELODY mode is unchanged.");
        offButton.setColour(juce::TextButton::buttonOnColourId, palette.token("accent"));
        offButton.setColour(juce::TextButton::textColourOnId, palette.token("window_bg"));
        if (auto* parameter = apvts.getRawParameterValue("singleMidiNoteAsChordRoot"))
            offButton.setToggleState(parameter->load(std::memory_order_relaxed) > 0.5f,
                                     juce::dontSendNotification);
        offButton.setButtonText(isAutoChordsEnabled() ? "AUTOCHORDS  /  ON" : "AUTOCHORDS  /  OFF");
        addAndMakeVisible(offButton);
        autoChordAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment>(
            apvts, "singleMidiNoteAsChordRoot", offButton);

        keyBox.addItemList({ "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B" }, 1);
        modeBox.addItemList({ "Chromatic", "Major", "Minor" }, 1);
        patternBox.addItemList({ "Pattern 1", "Pattern 2", "Pattern 3", "Pattern 4",
                                   "Pattern 5", "Pattern 6", "Pattern 7", "Pattern 8" }, 1);
        addAndMakeVisible(keyBox);
        addAndMakeVisible(modeBox);
        addAndMakeVisible(patternBox);
        chordDiagram.setPalette(palette);
        addAndMakeVisible(chordDiagram);
        keyAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ComboBoxAttachment>(apvts, "scaleRoot", keyBox);
        modeAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ComboBoxAttachment>(apvts, "scaleMode", modeBox);
        patternAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ComboBoxAttachment>(apvts, "patternSlot", patternBox);
        for (auto* label : { &keyLabel, &modeLabel, &patternLabel })
        {
            label->setColour(juce::Label::textColourId, palette.token("text_secondary"));
            addAndMakeVisible(*label);
        }
        keyLabel.setText("KEY", juce::dontSendNotification);
        modeLabel.setText("SCALE / QUALITY", juce::dontSendNotification);
        patternLabel.setText("RHYTHM PATTERN SLOT", juce::dontSendNotification);
    }
    void setThemePalette(const PPGUThemeManager::Palette& value) override
    {
        palette = value;
        title.setFont(makeThemeFont(palette, 20.0f, false, true));
        for (auto* label : { &keyLabel, &modeLabel, &patternLabel })
            label->setFont(makeThemeFont(palette, 9.5f, false, true));
        title.setColour(juce::Label::textColourId, palette.token("text_primary"));
        stateLabel.setColour(juce::Label::textColourId,
            isAutoChordsEnabled() ? palette.token("success") : palette.token("text_secondary"));
        for (auto* label : { &keyLabel, &modeLabel, &patternLabel })
            label->setColour(juce::Label::textColourId, palette.token("text_secondary"));
        offButton.setColour(juce::TextButton::buttonColourId, palette.token("panel_elevated"));
        offButton.setColour(juce::TextButton::textColourOffId, palette.token("text_primary"));
        offButton.setColour(juce::TextButton::buttonOnColourId, palette.token("accent"));
        offButton.setColour(juce::TextButton::textColourOnId, palette.token("window_bg"));
        for (auto* box : { &keyBox, &modeBox, &patternBox })
        {
            box->setColour(juce::ComboBox::backgroundColourId, palette.token("control_bg"));
            box->setColour(juce::ComboBox::textColourId, palette.token("text_primary"));
            box->setColour(juce::ComboBox::outlineColourId, palette.token("control_border"));
            box->setColour(juce::ComboBox::arrowColourId, palette.token("accent"));
        }
        chordDiagram.setPalette(palette);
        repaint();
    }

    void paint(juce::Graphics& g) override
    {
        g.fillAll(palette.token("window_bg"));
        drawThemeArtworkLayers(g, getLocalBounds(), palette, 0.10f, 0.30f, 0.035f);
        g.setColour(palette.token("control_border"));
        g.drawRoundedRectangle(getLocalBounds().toFloat().reduced(12), 10, 1);

        // Status LED is driven by the same APVTS parameter as the real button.
        const auto button = offButton.getBounds().toFloat();
        const float cx = button.getRight() - 15.0f;
        const float cy = button.getCentreY();
        const bool enabled = isAutoChordsEnabled();
        const auto led = enabled ? palette.token("accent") : palette.token("text_disabled");
        if (enabled)
        {
            g.setColour(palette.token("accent_glow").withAlpha(0.42f));
            g.fillEllipse(cx - 10.0f, cy - 10.0f, 20.0f, 20.0f);
        }
        g.setColour(led.withAlpha(enabled ? 0.95f : 0.65f));
        g.fillEllipse(cx - 4.0f, cy - 4.0f, 8.0f, 8.0f);
        g.setColour(palette.token("control_border"));
        g.drawEllipse(cx - 4.0f, cy - 4.0f, 8.0f, 8.0f, 1.0f);
    }
    void resized() override
    {
        auto area = getLocalBounds().reduced(24);
        title.setBounds(area.removeFromTop(38));
        stateLabel.setBounds(area.removeFromTop(32));
        offButton.setBounds(area.removeFromTop(44).removeFromLeft(210).reduced(2));
        area.removeFromTop(24);
        auto controls = area.removeFromLeft(300);
        auto diagramArea = area.removeFromRight(196);
        chordDiagram.setBounds(diagramArea.removeFromTop(176).reduced(3));

        keyLabel.setBounds(controls.removeFromTop(22));
        keyBox.setBounds(controls.removeFromTop(44).removeFromLeft(260));
        controls.removeFromTop(20);
        modeLabel.setBounds(controls.removeFromTop(22));
        modeBox.setBounds(controls.removeFromTop(44).removeFromLeft(260));
        controls.removeFromTop(20);
        patternLabel.setBounds(controls.removeFromTop(22));
        patternBox.setBounds(controls.removeFromTop(44).removeFromLeft(280));
    }
private:
    bool isAutoChordsEnabled() const noexcept
    {
        if (const auto* value = apvts.getRawParameterValue("singleMidiNoteAsChordRoot"))
            return value->load(std::memory_order_relaxed) > 0.5f;
        return false;
    }
    void timerCallback() override
    {
        const bool enabled = isAutoChordsEnabled();
        const auto text = enabled
            ? "AUTOCHORDS ENABLED  /  PATTERN MODE ONLY"
            : "AUTOCHORDS STANDBY  /  MELODY MODE UNAFFECTED";
        const auto buttonText = enabled ? "AUTOCHORDS  /  ON" : "AUTOCHORDS  /  OFF";
        bool changed = false;
        if (stateLabel.getText() != text)
        {
            stateLabel.setText(text, juce::dontSendNotification);
            stateLabel.setColour(juce::Label::textColourId,
                enabled ? palette.token("success") : palette.token("text_secondary"));
            changed = true;
        }
        if (offButton.getButtonText() != buttonText)
        {
            offButton.setButtonText(buttonText);
            changed = true;
        }
        if (changed)
            repaint();
    }
    PPGUThemeManager::Palette palette;
    juce::AudioProcessorValueTreeState& apvts;
    juce::Label title, stateLabel, keyLabel, modeLabel, patternLabel;
    PPGUChordDiagram chordDiagram;
    juce::TextButton offButton;
    juce::ComboBox keyBox, modeBox, patternBox;
    std::unique_ptr<juce::AudioProcessorValueTreeState::ComboBoxAttachment> keyAttachment, modeAttachment, patternAttachment;
    std::unique_ptr<juce::AudioProcessorValueTreeState::ButtonAttachment> autoChordAttachment;
};
}

// Premium NEON STAGE shell. Visual theme code never touches processor/audio state.

namespace { void getPluginModuleAnchor() {} }

void PPGUPremiumLookAndFeel::drawRotarySlider(juce::Graphics& g, int x, int y, int w, int h,
                                                    float pos, float start, float end, juce::Slider& slider)
{
    // Render authored PNG knob faces with the highest JUCE resampling mode.
    // This is evaluated only when the control repaints; it does not add timers,
    // interpolation work to the audio thread, or alter the APVTS value.
    g.setImageResamplingQuality(juce::Graphics::highResamplingQuality);
    const auto controlId = slider.getComponentID();
    if (palette.rotarySpriteSheet.isValid())
    {
        // Canonical NEON STAGE rotary atlas: 61 authored positions in an 8x8
        // grid of 128px cells. Frame selection follows the live normalized
        // Slider value; the underlying APVTS value remains continuous.
        const int frame = juce::jlimit(0, 60, juce::roundToInt(pos * 60.0f));
        constexpr int cellSize = 128;
        const int sourceX = (frame % 8) * cellSize;
        const int sourceY = (frame / 8) * cellSize;
        const int diameter = juce::jmax(1, juce::jmin(w, h) - 2);
        const int destinationX = x + (w - diameter) / 2;
        const int destinationY = y + (h - diameter) / 2;
        g.drawImage(palette.rotarySpriteSheet, destinationX, destinationY,
                    diameter, diameter, sourceX, sourceY, cellSize, cellSize);

        // Premium value ring: its position is the real APVTS value, while
        // hover/focus only change the optical response (never the parameter).
        const bool rotaryEnabled = slider.isEnabled();
        const bool rotaryHovered = rotaryEnabled && slider.isMouseOverOrDragging();
        const bool rotaryFocused = rotaryEnabled && slider.hasKeyboardFocus(true);
        const float centreX = static_cast<float>(destinationX) + diameter * 0.5f;
        const float centreY = static_cast<float>(destinationY) + diameter * 0.5f;
        const float arcRadius = static_cast<float>(diameter) * 0.455f;
        const float valueAngle = start + pos * (end - start);
        juce::Path arcTrack;
        arcTrack.addCentredArc(centreX, centreY, arcRadius, arcRadius,
                               0.0f, start, end, true);
        g.setColour(rotaryEnabled ? palette.token("control_border").withAlpha(0.88f)
                                  : palette.token("text_disabled").withAlpha(0.45f));
        g.strokePath(arcTrack, juce::PathStrokeType(3.2f,
            juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
        if (rotaryEnabled && pos > 0.0001f)
        {
            juce::Path valueArc;
            valueArc.addCentredArc(centreX, centreY, arcRadius, arcRadius,
                                   0.0f, start, valueAngle, true);
            const auto liveAccent = rotaryFocused ? palette.token("highlight")
                : (rotaryHovered ? palette.token("accent") : palette.token("accent_glow"));
            g.setColour(liveAccent.withAlpha(rotaryHovered ? 0.58f : 0.38f));
            g.strokePath(valueArc, juce::PathStrokeType(rotaryHovered ? 9.0f : 7.0f,
                juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
            g.setColour(rotaryFocused ? palette.token("highlight")
                                      : palette.token("accent").withAlpha(0.99f));
            g.strokePath(valueArc, juce::PathStrokeType(rotaryHovered ? 3.4f : 2.8f,
                juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
        }

        // Every knob keeps its continuous 61-frame rotary animation, while its
        // dedicated five-state PNG remains part of the live visual state stack.
        // State art is a restrained overlay so it cannot obscure the moving
        // pointer or quantize the APVTS value.
        if (controlId.startsWith("knob"))
        {
            const auto stateName = ppguSliderArtworkState(slider);
            if (const auto* stateArtwork = palette.findControlArtwork(controlId, stateName))
            {
                if (stateArtwork->isValid() && stateName != "default")
                {
                    g.saveState();
                    g.setOpacity(stateName == "disabled" ? 0.42f : 0.18f);
                    g.drawImageWithin(*stateArtwork, destinationX, destinationY,
                                      diameter, diameter, juce::RectanglePlacement::centred);
                    g.restoreState();
                }
            }
        }

        if (! slider.isEnabled())
        {
            g.setColour(palette.token("window_bg").withAlpha(0.30f));
            g.fillEllipse(static_cast<float>(destinationX), static_cast<float>(destinationY),
                          static_cast<float>(diameter), static_cast<float>(diameter));
        }
        else if (slider.isMouseOverOrDragging() || slider.hasKeyboardFocus(true))
        {
            const auto ringColour = slider.isMouseOverOrDragging()
                ? palette.token("accent") : palette.token("highlight");
            g.setColour(ringColour.withAlpha(slider.isMouseOverOrDragging() ? 0.82f : 0.58f));
            g.drawEllipse(static_cast<float>(destinationX) + 1.5f,
                          static_cast<float>(destinationY) + 1.5f,
                          static_cast<float>(diameter) - 3.0f,
                          static_cast<float>(diameter) - 3.0f, 1.5f);
        }
        return;
    }

    if (controlId.startsWith("knob"))
    {
        const auto stateName = ppguSliderArtworkState(slider);
        if (const auto* artwork = palette.findControlArtwork(controlId, stateName))
        {
            if (artwork->isValid())
            {
                const int diameter = juce::jmax(1, juce::jmin(w, h) - 2);
                const int destinationX = x + (w - diameter) / 2;
                const int destinationY = y + (h - diameter) / 2;
                g.drawImageWithin(*artwork, destinationX, destinationY, diameter, diameter,
                                  juce::RectanglePlacement::centred);
                // The artwork is the physical knob face; the value arc and pointer
                // are live overlays driven by the attached APVTS slider value.
                const float cx = static_cast<float>(x) + static_cast<float>(w) * 0.5f;
                const float cy = static_cast<float>(y) + static_cast<float>(h) * 0.5f;
                const float radius = static_cast<float>(diameter) * 0.30f;
                const float arcRadius = static_cast<float>(diameter) * 0.405f;
                const float angle = start + pos * (end - start);
                const bool enabled = slider.isEnabled();
                const bool hovered = enabled && slider.isMouseOverOrDragging();
                const bool focused = enabled && slider.hasKeyboardFocus(true);

                juce::Path arcTrack;
                arcTrack.addCentredArc(cx, cy, arcRadius, arcRadius, 0.0f,
                                       start, end, true);
                g.setColour(enabled ? palette.token("led_off").withAlpha(0.92f)
                                    : palette.token("text_disabled").withAlpha(0.42f));
                g.strokePath(arcTrack, juce::PathStrokeType(3.0f,
                    juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

                juce::Path valueArc;
                valueArc.addCentredArc(cx, cy, arcRadius, arcRadius, 0.0f,
                                       start, angle, true);
                if (enabled && pos > 0.0001f)
                {
                    g.setColour(palette.token("accent_glow").withAlpha(hovered ? 0.58f : 0.34f));
                    g.strokePath(valueArc, juce::PathStrokeType(6.0f,
                        juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
                    g.setColour(focused ? palette.token("highlight") : palette.token("accent"));
                    g.strokePath(valueArc, juce::PathStrokeType(2.7f,
                        juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
                }

                juce::Path pointer;
                pointer.startNewSubPath(cx, cy);
                pointer.lineTo(cx + std::sin(angle) * radius,
                               cy - std::cos(angle) * radius);
                g.setColour(palette.token("text_primary"));
                g.strokePath(pointer, juce::PathStrokeType(2.2f,
                    juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
                return;
            }
        }
    }

    if (palette.controlsSpriteSheet.isValid())
    {
        // Eight authored 100x100 frames at 45-degree increments. Quantization
        // is visual only; the Slider's continuous parameter value is unchanged.
        const int frame = juce::jlimit(0, 7, juce::roundToInt(pos * 7.0f));
        const int sourceX = 65 + (frame % 4) * 110;
        const int sourceY = frame < 4 ? 120 : 220;
        const int diameter = juce::jmax(1, juce::roundToInt(
            static_cast<float>(juce::jmin(w, h)) * 0.82f));
        const int destinationX = x + (w - diameter) / 2;
        const int destinationY = y + (h - diameter) / 2;
        g.drawImage(palette.controlsSpriteSheet, destinationX, destinationY,
                    diameter, diameter, sourceX, sourceY, 100, 100);

        // The legacy 8-frame atlas is only the physical knob face. Keep the
        // continuous parameter value and interaction state visible above it.
        const float cx = static_cast<float>(destinationX) + diameter * 0.5f;
        const float cy = static_cast<float>(destinationY) + diameter * 0.5f;
        const float radius = static_cast<float>(diameter) * 0.30f;
        const float arcRadius = static_cast<float>(diameter) * 0.455f;
        const float angle = start + pos * (end - start);
        const bool enabled = slider.isEnabled();
        const bool hovered = enabled && slider.isMouseOverOrDragging();
        const bool focused = enabled && slider.hasKeyboardFocus(true);

        juce::Path arcTrack;
        arcTrack.addCentredArc(cx, cy, arcRadius, arcRadius, 0.0f,
                               start, end, true);
        g.setColour(enabled ? palette.token("control_border").withAlpha(0.92f)
                            : palette.token("text_disabled").withAlpha(0.48f));
        g.strokePath(arcTrack, juce::PathStrokeType(3.0f,
            juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

        if (enabled && pos > 0.0001f)
        {
            juce::Path valueArc;
            valueArc.addCentredArc(cx, cy, arcRadius, arcRadius, 0.0f,
                                   start, angle, true);
            g.setColour(palette.token("accent_glow").withAlpha(hovered ? 0.62f : 0.36f));
            g.strokePath(valueArc, juce::PathStrokeType(hovered ? 8.0f : 6.0f,
                juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
            g.setColour(focused ? palette.token("highlight") : palette.token("accent"));
            g.strokePath(valueArc, juce::PathStrokeType(hovered ? 3.5f : 2.8f,
                juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
        }

        juce::Path pointer;
        pointer.startNewSubPath(cx, cy);
        pointer.lineTo(cx + std::sin(angle) * radius,
                       cy - std::cos(angle) * radius);
        g.setColour(enabled ? palette.token("text_primary")
                            : palette.token("text_disabled"));
        g.strokePath(pointer, juce::PathStrokeType(2.2f,
            juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

        if (!enabled)
        {
            g.setColour(palette.token("window_bg").withAlpha(0.48f));
            g.fillEllipse(static_cast<float>(destinationX), static_cast<float>(destinationY),
                          static_cast<float>(diameter), static_cast<float>(diameter));
        }
        else if (hovered || focused)
        {
            const auto stateColour = focused ? palette.token("highlight")
                                             : palette.token("accent");
            g.setColour(stateColour.withAlpha(hovered ? 0.78f : 0.58f));
            g.drawEllipse(static_cast<float>(destinationX) + 1.5f,
                          static_cast<float>(destinationY) + 1.5f,
                          static_cast<float>(diameter) - 3.0f,
                          static_cast<float>(diameter) - 3.0f, 1.5f);
        }
        return;
    }

    const float d = juce::jmin(static_cast<float>(w), static_cast<float>(h)) * 0.76f;
    const float r = d * 0.5f;
    const float cx = x + w * 0.5f;
    const float cy = y + h * 0.5f - 2.0f;
    const float angle = start + pos * (end - start);
    const bool enabled = slider.isEnabled();
    const bool hovered = enabled && slider.isMouseOverOrDragging();
    const bool focused = enabled && slider.hasKeyboardFocus(true);

    g.setColour(palette.token("shadow").withAlpha(0.34f));
    g.fillEllipse(cx - r - 1.0f, cy - r + 3.0f, d + 2.0f, d + 2.0f);

    juce::Path track;
    track.addCentredArc(cx, cy, r + 5.0f, r + 5.0f, 0.0f, start, end, true);
    g.setColour(enabled ? palette.border : palette.token("text_disabled").withAlpha(0.55f));
    g.strokePath(track, juce::PathStrokeType(4.0f, juce::PathStrokeType::curved,
                                             juce::PathStrokeType::rounded));

    juce::Path value;
    value.addCentredArc(cx, cy, r + 5.0f, r + 5.0f, 0.0f, start, angle, true);
    g.setColour(enabled ? (hovered ? palette.accent.brighter(0.12f) : palette.accent)
                        : palette.token("text_disabled").withAlpha(0.42f));
    g.strokePath(value, juce::PathStrokeType(4.0f, juce::PathStrokeType::curved,
                                             juce::PathStrokeType::rounded));

    const auto faceTop = enabled ? palette.surfaceRaised.brighter(0.12f)
                                 : palette.surfaceSecondary;
    const auto faceBottom = enabled ? palette.canvasInset.darker(0.12f)
                                    : palette.canvasInset;
    g.setGradientFill(juce::ColourGradient(faceTop, cx, cy - r, faceBottom, cx, cy + r, false));
    g.fillEllipse(cx - r + 4.0f, cy - r + 4.0f, d - 8.0f, d - 8.0f);
    g.setColour(focused ? palette.focus : palette.border);
    g.drawEllipse(cx - r + 4.0f, cy - r + 4.0f, d - 8.0f, d - 8.0f,
                  focused ? 2.0f : 1.2f);

    // Machined-metal face treatment for themes without authored rotary PNGs.
    // These highlights are paint-only: no bounds, hit-testing or parameter changes.
    const auto faceBounds = juce::Rectangle<float>(cx - r + 6.0f, cy - r + 6.0f,
                                                    d - 12.0f, d - 12.0f);
    juce::Path upperBevel;
    upperBevel.addCentredArc(cx, cy, r - 7.0f, r - 7.0f, 0.0f,
                             juce::MathConstants<float>::pi * 1.12f,
                             juce::MathConstants<float>::pi * 1.88f, true);
    g.setColour(palette.token("highlight").withAlpha(enabled ? 0.20f : 0.06f));
    g.strokePath(upperBevel, juce::PathStrokeType(1.15f,
        juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

    juce::Path lowerBevel;
    lowerBevel.addCentredArc(cx, cy, r - 7.0f, r - 7.0f, 0.0f,
                             juce::MathConstants<float>::pi * 0.12f,
                             juce::MathConstants<float>::pi * 0.88f, true);
    g.setColour(palette.token("shadow").withAlpha(enabled ? 0.30f : 0.12f));
    g.strokePath(lowerBevel, juce::PathStrokeType(1.0f,
        juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

    g.setColour(palette.token("highlight").withAlpha(enabled ? 0.045f : 0.015f));
    g.fillEllipse(faceBounds.reduced(faceBounds.getWidth() * 0.16f,
                                     faceBounds.getHeight() * 0.16f));

    juce::Path pointer;
    pointer.startNewSubPath(cx, cy);
    pointer.lineTo(cx + std::sin(angle) * r * 0.56f,
                   cy - std::cos(angle) * r * 0.56f);
    g.setColour(enabled ? palette.text : palette.token("text_disabled"));
    g.strokePath(pointer, juce::PathStrokeType(2.6f, juce::PathStrokeType::curved,
                                                juce::PathStrokeType::rounded));
    g.setColour(enabled ? palette.accentSecondary : palette.token("text_disabled"));
    g.fillEllipse(cx - 2.5f, cy - 2.5f, 5.0f, 5.0f);
}

void PPGUPremiumLookAndFeel::drawLinearSlider(juce::Graphics& g, int x, int y, int width, int height,
                                               float sliderPos, float minSliderPos, float maxSliderPos,
                                               juce::Slider::SliderStyle style, juce::Slider& slider)
{
    juce::ignoreUnused(minSliderPos, maxSliderPos);
    if (style != juce::Slider::LinearHorizontal)
    {
        juce::LookAndFeel_V4::drawLinearSlider(g, x, y, width, height,
                                               sliderPos, minSliderPos, maxSliderPos, style, slider);
        return;
    }

    const bool enabled = slider.isEnabled();
    const bool hovered = enabled && slider.isMouseOverOrDragging();
    const bool focused = enabled && slider.hasKeyboardFocus(true);
    const bool dragging = enabled && slider.isMouseButtonDown();
    const bool useLongTrack = width >= 420;
    const auto track = juce::Rectangle<float>(
        static_cast<float>(x + 4), static_cast<float>(y + (height - 12) / 2),
        static_cast<float>(juce::jmax(1, width - 8)), 12.0f);
    const float proportion = juce::jlimit(0.0f, 1.0f,
        (sliderPos - static_cast<float>(x + 4))
            / static_cast<float>(juce::jmax(1, width - 8)));
    const float thumbSize = static_cast<float>(juce::jlimit(16, 30, height + 8));
    const float thumbX = juce::jlimit(track.getX() - thumbSize * 0.5f,
        track.getRight() - thumbSize * 0.5f,
        sliderPos - thumbSize * 0.5f);
    const float thumbY = track.getCentreY() - thumbSize * 0.5f;

    if (palette.metersSlidersSpriteSheet.isValid())
    {
        g.setImageResamplingQuality(juce::Graphics::highResamplingQuality);
        const int sourceX = 60;
        const int sourceY = useLongTrack ? 445 : 570;
        const int sourceWidth = useLongTrack ? 820 : 390;
        g.drawImage(palette.metersSlidersSpriteSheet,
                    track.getX(), track.getY(), track.getWidth(), track.getHeight(),
                    sourceX, sourceY, sourceWidth, 22);
        g.drawImage(palette.metersSlidersSpriteSheet,
                    static_cast<int>(thumbX), static_cast<int>(thumbY),
                    static_cast<int>(thumbSize), static_cast<int>(thumbSize),
                    910, 640, 32, 32);
    }
    else
    {
        const auto trackTop = enabled ? palette.token("control_face")
                                      : palette.token("lowlight");
        const auto trackBottom = palette.token("window_bg");
        g.setGradientFill(juce::ColourGradient(trackTop, track.getX(), track.getY(),
                                               trackBottom, track.getX(), track.getBottom(), false));
        g.fillRoundedRectangle(track, 6.0f);
        g.setColour(palette.token("control_border").withAlpha(enabled ? 0.92f : 0.42f));
        g.drawRoundedRectangle(track, 6.0f, 1.0f);
    }

    const float fillWidth = track.getWidth() * proportion;
    if (enabled && fillWidth > 0.0f)
    {
        const auto fill = track.withWidth(fillWidth).reduced(1.0f);
        g.setColour(palette.token("accent_glow").withAlpha(hovered || dragging ? 0.70f : 0.38f));
        g.fillRoundedRectangle(fill.expanded(1.0f, 1.5f), 5.0f);
        g.setColour(focused ? palette.token("highlight") : palette.token("accent"));
        g.fillRoundedRectangle(fill.reduced(0.0f, 3.5f), 2.5f);
    }

    if (!palette.metersSlidersSpriteSheet.isValid())
    {
        const auto thumbTop = enabled ? palette.token("highlight") : palette.token("text_disabled");
        const auto thumbBottom = enabled ? palette.token("control_face") : palette.token("lowlight");
        g.setGradientFill(juce::ColourGradient(thumbTop, thumbX, thumbY,
                                               thumbBottom, thumbX, thumbY + thumbSize, false));
        g.fillEllipse(thumbX, thumbY, thumbSize, thumbSize);
        g.setColour(focused ? palette.token("highlight") : palette.token("control_border"));
        g.drawEllipse(thumbX, thumbY, thumbSize, thumbSize, focused ? 2.0f : 1.1f);
        g.setColour(enabled ? palette.token("accent") : palette.token("text_disabled"));
        g.fillEllipse(thumbX + thumbSize * 0.39f, thumbY + thumbSize * 0.39f,
                      thumbSize * 0.22f, thumbSize * 0.22f);
    }

    if (!enabled)
    {
        g.setColour(palette.token("window_bg").withAlpha(0.42f));
        g.fillRoundedRectangle(track.expanded(1.0f), 6.0f);
        g.fillEllipse(thumbX, thumbY, thumbSize, thumbSize);
    }
    else if (hovered || focused || dragging)
    {
        const auto stateColour = focused ? palette.token("highlight")
            : (dragging ? palette.token("accent") : palette.token("accent_glow"));
        g.setColour(stateColour.withAlpha(focused ? 0.82f : 0.58f));
        g.drawRoundedRectangle(track.expanded(2.0f), 6.0f, focused ? 1.8f : 1.2f);
        g.drawEllipse(thumbX - 1.5f, thumbY - 1.5f,
                      thumbSize + 3.0f, thumbSize + 3.0f,
                      dragging ? 2.0f : 1.25f);
    }
}

void PPGUPremiumLookAndFeel::drawButtonBackground(juce::Graphics& g, juce::Button& button,
                                                   const juce::Colour& base, bool hovered, bool down)
{
    // Keep PNG button-state art and atlas icons crisp at non-native UI scales.
    g.setImageResamplingQuality(juce::Graphics::highResamplingQuality);
    const auto controlId = button.getComponentID();
    const auto drawKeyboardFocus = [&g, &button, this]
    {
        if (! button.isEnabled() || ! button.hasKeyboardFocus(true))
            return;
        const auto focusBounds = button.getLocalBounds().toFloat().reduced(1.5f);
        g.setColour(palette.token("highlight").withAlpha(0.88f));
        g.drawRoundedRectangle(focusBounds, 5.0f, 1.6f);
    };

    const auto drawFxActiveIndicator = [&g, &button, this, controlId]
    {
        // FX LED follows the attached APVTS toggle; bypassed modules stay dark.
        if (!controlId.startsWith("fx_switch") || !button.isEnabled()
            || !button.getToggleState())
            return;
        const auto bounds = button.getLocalBounds().toFloat();
        const float cx = bounds.getRight() - 10.0f;
        const float cy = bounds.getCentreY();
        g.setColour(palette.token("accent_glow").withAlpha(0.36f));
        g.fillEllipse(cx - 7.0f, cy - 7.0f, 14.0f, 14.0f);
        g.setColour(palette.token("accent").withAlpha(0.98f));
        g.fillEllipse(cx - 3.0f, cy - 3.0f, 6.0f, 6.0f);
        g.setColour(palette.token("text_primary").withAlpha(0.92f));
        g.drawEllipse(cx - 3.0f, cy - 3.0f, 6.0f, 6.0f, 0.7f);
    };

    const auto drawAtlasIcon = [&g, &button, this, controlId]
    {
        if (! palette.iconsSpriteSheet.isValid())
            return;
        juce::String icon;
        if (controlId.startsWith("fx_switch01")) icon = "wave";
        else if (controlId.startsWith("fx_switch02")) icon = "eq";
        else if (controlId.startsWith("fx_switch03")) icon = "distortion";
        else if (controlId.startsWith("fx_switch04")) icon = "chorus";
        else if (controlId.startsWith("fx_switch05")) icon = "delay";
        else if (controlId.startsWith("fx_switch06")) icon = "reverb";
        else if (controlId.startsWith("fx_switch07")) icon = "cabinet";
        else if (controlId == "Settings") icon = "settings";
        else if (controlId == "About") icon = "info";
        else if (controlId == "SKIN_button") icon = "palette";
        else if (controlId == "Import_Guitar") icon = "guitar";
        else if (controlId == "Auto_Discover") icon = "antenna";
        else if (controlId == "Curator") icon = "crown";
        if (icon.isEmpty()) return;

        static const std::map<std::string, juce::Rectangle<int>> iconBounds {
            { "wave", {32,75,144,144} }, { "eq", {196,75,144,144} },
            { "distortion", {360,75,144,144} }, { "chorus", {524,75,144,144} },
            { "delay", {688,75,144,144} }, { "reverb", {852,75,144,144} },
            { "cabinet", {32,360,144,144} }, { "crown", {196,360,144,144} },
            { "settings", {524,360,144,144} }, { "info", {688,360,144,144} },
            { "guitar", {196,645,144,144} }, { "antenna", {360,645,144,144} },
            { "palette", {524,645,144,144} }
        };
        const auto found = iconBounds.find(icon.toStdString());
        if (found == iconBounds.end()) return;
        const auto bounds = button.getLocalBounds();
        const int size = juce::jlimit(14, 24, bounds.getHeight() - 8);
        const int x = bounds.getX() + 7;
        const int y = bounds.getCentreY() - size / 2;
        const auto source = found->second;
        g.drawImage(palette.iconsSpriteSheet, x, y, size, size,
                    source.getX(), source.getY(), source.getWidth(), source.getHeight());
    };
    if (controlId.startsWith("fx_switch") || controlId == "Import_Guitar"
        || controlId == "Auto_Discover" || controlId == "Curator"
        || controlId == "Settings" || controlId == "About"
        || controlId == "SKIN_button")
    {
        const auto stateName = ppguButtonArtworkState(button, hovered, down);
        if (const auto* artwork = palette.findControlArtwork(controlId, stateName))
        {
            if (artwork->isValid())
            {
                const auto bounds = button.getLocalBounds();
                g.drawImageWithin(*artwork, bounds.getX(), bounds.getY(),
                    bounds.getWidth(), bounds.getHeight(), juce::RectanglePlacement::centred);
                // State artwork supplies the physical switch; the atlas icon
                // is layered independently so labels and hit targets remain live.
                drawAtlasIcon();
                drawFxActiveIndicator();
                drawKeyboardFocus();
                return;
            }
        }
    }

    if (palette.controlsSpriteSheet.isValid() && button.isEnabled())
    {
        // Atlas state boxes are authored at 225x125; JUCE draws the button's
        // text/icon afterwards, so labels remain live and accessible.
        int sourceX = 25;
        int sourceY = 690;
        int sourceWidth = 225;
        int sourceHeight = 125;
        if (button.getClickingTogglesState())
        {
            // FX bypass and power controls use the dedicated OFF/ON switch art.
            sourceX = button.getToggleState() ? 535 : 65;
            sourceY = 430;
            sourceWidth = 400;
            sourceHeight = 170;
        }
        else if (down) sourceX = 505;
        else if (button.getToggleState()) sourceX = 745;
        else if (hovered) sourceX = 265;
        const auto bounds = button.getLocalBounds();
        g.drawImage(palette.controlsSpriteSheet, bounds.getX(), bounds.getY(),
                    bounds.getWidth(), bounds.getHeight(), sourceX, sourceY,
                    sourceWidth, sourceHeight);
        drawAtlasIcon();
        drawFxActiveIndicator();
        drawKeyboardFocus();
        return;
    }

    auto bounds = button.getLocalBounds().toFloat().reduced(0.5f);
    const bool enabled = button.isEnabled();
    const bool focused = enabled && button.hasKeyboardFocus(true);
    auto face = button.getToggleState() ? palette.accent : base;

    if (!enabled)
        face = palette.surfaceSecondary;
    else if (down)
        face = face.darker(0.18f);
    else if (hovered)
        face = face.brighter(0.12f);

    g.setGradientFill(juce::ColourGradient(face.brighter(enabled ? 0.08f : 0.02f),
        bounds.getX(), bounds.getY(), face.darker(0.16f), bounds.getX(), bounds.getBottom(), false));
    g.fillRoundedRectangle(bounds, 7.0f);

    g.setColour(focused ? palette.focus : (enabled ? palette.border : palette.token("lowlight")));
    g.drawRoundedRectangle(bounds, 7.0f, focused ? 2.0f : 1.0f);

    // Subtle machined top/bottom edge for the non-atlas button fallback.
    // Keep this strictly inside the existing paint bounds; no layout or hit-test changes.
    if (enabled)
    {
        const auto edge = bounds.reduced(1.5f);
        g.setColour(palette.token("highlight").withAlpha(hovered ? 0.34f : 0.20f));
        g.drawLine(edge.getX() + 6.0f, edge.getY() + 0.8f,
                   edge.getRight() - 6.0f, edge.getY() + 0.8f, 0.8f);
        g.setColour(palette.token("lowlight").withAlpha(down ? 0.52f : 0.30f));
        g.drawLine(edge.getX() + 6.0f, edge.getBottom() - 0.8f,
                   edge.getRight() - 6.0f, edge.getBottom() - 0.8f, 0.8f);
    }

    if (button.getToggleState() && enabled)
    {
        g.setColour(palette.accentSecondary);
        g.fillRoundedRectangle(bounds.removeFromLeft(3.0f), 1.5f);

        // Active toggle state is visible across all 16 themes, including skins
        // that do not ship a dedicated PNG state atlas.
        const auto activeBounds = button.getLocalBounds().toFloat().reduced(2.0f);
        g.setColour(palette.token("accent_glow").withAlpha(0.18f));
        g.drawRoundedRectangle(activeBounds, 6.0f, 2.0f);
    }

    if (enabled && down)
    {
        // Pressed controls gain a restrained inset edge rather than changing
        // component bounds or interfering with JUCE's hit-testing.
        const auto inset = button.getLocalBounds().toFloat().reduced(2.5f);
        g.setColour(palette.token("lowlight").withAlpha(0.72f));
        g.drawRoundedRectangle(inset, 5.0f, 1.25f);
        g.setColour(palette.token("highlight").withAlpha(0.16f));
        g.drawLine(inset.getX() + 4.0f, inset.getY() + 1.0f,
                   inset.getRight() - 4.0f, inset.getY() + 1.0f, 0.8f);
    }

    if (!enabled)
    {
        // Consistent disabled veil for themes without authored disabled frames.
        const auto disabledBounds = button.getLocalBounds().toFloat().reduced(1.0f);
        g.setColour(palette.token("window_bg").withAlpha(0.22f));
        g.fillRoundedRectangle(disabledBounds, 6.0f);
    }

    // Keep functional feedback available even when optional button atlases
    // are absent: active FX still gets its real-state LED and keyboard users
    // retain the same visible focus ring as the artwork-backed path.
    drawFxActiveIndicator();
    drawKeyboardFocus();
}

void PPGUPremiumLookAndFeel::drawComboBox(juce::Graphics& g, int w, int h, bool down,
                                           int, int, int, int, juce::ComboBox& box)
{
    auto bounds = juce::Rectangle<float>(0.5f, 0.5f, static_cast<float>(w) - 1.0f,
                                         static_cast<float>(h) - 1.0f);
    const bool enabled = box.isEnabled();
    const bool focused = enabled && box.hasKeyboardFocus(true);
    auto face = box.findColour(juce::ComboBox::backgroundColourId);
    if (!enabled)
        face = palette.surfaceSecondary;
    else if (down || box.isMouseOver())
        face = face.brighter(0.08f);

    const auto topFace = enabled ? face.brighter(down ? 0.015f : 0.075f)
                                 : face.brighter(0.025f);
    const auto bottomFace = enabled ? face.darker(down ? 0.22f : 0.15f)
                                    : face.darker(0.08f);
    g.setGradientFill(juce::ColourGradient(topFace, bounds.getX(), bounds.getY(),
                                           bottomFace, bounds.getX(), bounds.getBottom(), false));
    g.fillRoundedRectangle(bounds, 7.0f);

    // Fine upper bevel and inset edge make the selector read as a machined
    // control, while hover/press/focus remain driven by JUCE's real state.
    auto inner = bounds.reduced(1.0f);
    g.setColour(palette.token("highlight").withAlpha(enabled ? (box.isMouseOver() ? 0.24f : 0.13f) : 0.05f));
    g.drawRoundedRectangle(inner, 6.0f, 0.8f);
    g.setColour(palette.token("lowlight").withAlpha(0.72f));
    g.drawRoundedRectangle(bounds.reduced(2.0f), 5.0f, 0.65f);
    g.setColour(focused ? palette.focus : (enabled ? palette.border : palette.token("lowlight")));
    g.drawRoundedRectangle(bounds, 7.0f, focused ? 2.0f : 1.0f);

    const float cx = bounds.getRight() - 17.0f;
    const float cy = bounds.getCentreY();
    juce::Path arrow;
    arrow.startNewSubPath(cx - 4.0f, cy - 2.0f);
    arrow.lineTo(cx, cy + 2.0f);
    arrow.lineTo(cx + 4.0f, cy - 2.0f);
    if (focused || down)
    {
        g.setColour(palette.token("accent_glow").withAlpha(0.28f));
        g.strokePath(arrow, juce::PathStrokeType(4.0f, juce::PathStrokeType::curved,
                                                  juce::PathStrokeType::rounded));
    }
    g.setColour(enabled ? palette.accent : palette.token("text_disabled"));
    g.strokePath(arrow, juce::PathStrokeType(1.8f, juce::PathStrokeType::curved,
                                              juce::PathStrokeType::rounded));
}


void PPGUPremiumLookAndFeel::drawToggleButton(juce::Graphics& g,
                                               juce::ToggleButton& button,
                                               bool highlighted, bool down)
{
    const auto bounds = button.getLocalBounds().toFloat();
    if (bounds.isEmpty())
        return;

    const bool enabled = button.isEnabled();
    const bool active = enabled && button.getToggleState();
    const bool focused = enabled && button.hasKeyboardFocus(true);
    const bool hovered = enabled && (highlighted || button.isMouseOver());
    const float scale = juce::jlimit(0.75f, 1.25f,
        bounds.getHeight() / 28.0f);
    const float switchWidth = 34.0f * scale;
    const float switchHeight = 18.0f * scale;
    const float switchX = bounds.getX() + 2.0f * scale;
    const float switchY = bounds.getCentreY() - switchHeight * 0.5f;
    const auto switchBounds = juce::Rectangle<float>(switchX, switchY,
                                                       switchWidth, switchHeight);

    const auto trackColour = !enabled ? palette.token("lowlight")
        : active ? palette.token("accent").withAlpha(0.92f)
        : hovered ? palette.token("control_face").brighter(0.12f)
        : palette.token("control_bg");
    g.setColour(trackColour);
    g.fillRoundedRectangle(switchBounds, switchHeight * 0.5f);

    // Fine metallic rim; active state remains bound to the real ToggleButton state.
    const auto trackInset = switchBounds.reduced(1.0f * scale);
    g.setColour(palette.token("highlight").withAlpha(enabled ? 0.22f : 0.06f));
    g.drawLine(trackInset.getX() + 4.0f * scale, trackInset.getY() + 0.6f * scale,
               trackInset.getRight() - 4.0f * scale, trackInset.getY() + 0.6f * scale,
               0.75f * scale);
    g.setColour(palette.token("lowlight").withAlpha(enabled ? 0.46f : 0.24f));
    g.drawLine(trackInset.getX() + 4.0f * scale, trackInset.getBottom() - 0.6f * scale,
               trackInset.getRight() - 4.0f * scale, trackInset.getBottom() - 0.6f * scale,
               0.75f * scale);

    g.setColour(focused ? palette.token("highlight")
                        : palette.token("control_border").withAlpha(enabled ? 0.95f : 0.42f));
    g.drawRoundedRectangle(switchBounds, switchHeight * 0.5f,
                           focused ? 1.8f : 1.0f);

    const float knobDiameter = switchHeight - 5.0f * scale;
    const float knobTravel = switchWidth - knobDiameter - 5.0f * scale;
    const float knobX = switchX + 2.5f * scale
        + (active ? knobTravel : 0.0f);
    const float knobY = switchY + 2.5f * scale;
    const auto knobBounds = juce::Rectangle<float>(knobX, knobY,
                                                     knobDiameter, knobDiameter);
    g.setColour(enabled ? palette.token("highlight") : palette.token("text_disabled"));
    g.fillEllipse(knobBounds);
    const auto knobHighlight = knobBounds.reduced(2.0f * scale);
    g.setColour(palette.token("text_primary").withAlpha(enabled ? 0.28f : 0.08f));
    g.drawLine(knobHighlight.getX() + 1.0f * scale, knobHighlight.getY() + 1.0f * scale,
               knobHighlight.getRight() - 1.0f * scale, knobHighlight.getY() + 1.0f * scale,
               0.7f * scale);
    g.setColour(palette.token("shadow").withAlpha(0.35f));
    g.drawEllipse(knobBounds, 0.8f);

    if (hovered || down || focused)
    {
        const auto stateColour = focused ? palette.token("highlight")
            : (down ? palette.token("accent") : palette.token("accent_glow"));
        g.setColour(stateColour.withAlpha(focused ? 0.58f : 0.30f));
        g.drawRoundedRectangle(switchBounds.expanded(2.0f * scale),
                               switchHeight * 0.6f, focused ? 1.5f : 1.0f);
    }

    const auto textBounds = bounds.withLeft(switchBounds.getRight() + 9.0f * scale)
                                  .reduced(0.0f, 1.0f);
    g.setColour(enabled ? palette.token("text_primary")
                        : palette.token("text_disabled"));
    g.setFont(makeThemeFont(palette, juce::jmax(10.0f,
        juce::jmin(15.0f, bounds.getHeight() * 0.52f)), false, active));
    g.drawFittedText(button.getButtonText(), textBounds.toNearestInt(),
                     juce::Justification::centredLeft, 1);
}

void PPGUPremiumLookAndFeel::fillTextEditorBackground(juce::Graphics& g, int width, int height,
                                                            juce::TextEditor& editor)
{
    const auto surface = editor.isEnabled() ? palette.token("control_bg")
                                            : palette.token("lowlight");
    g.setColour(surface);
    g.fillRoundedRectangle(0.5f, 0.5f, static_cast<float>(width) - 1.0f,
                           static_cast<float>(height) - 1.0f, 6.0f);
}

void PPGUPremiumLookAndFeel::drawTextEditorOutline(juce::Graphics& g, int width, int height,
                                                    juce::TextEditor& editor)
{
    const bool enabled = editor.isEnabled();
    const bool focused = enabled && editor.hasKeyboardFocus(true);
    const bool hovered = enabled && editor.isMouseOver();

    const auto outline = !enabled ? palette.token("lowlight")
        : focused ? palette.token("highlight")
        : hovered ? palette.token("accent")
        : palette.token("control_border");

    g.setColour(outline);
    g.drawRoundedRectangle(0.5f, 0.5f, static_cast<float>(width) - 1.0f,
                           static_cast<float>(height) - 1.0f, 6.0f,
                           focused ? 2.0f : 1.0f);
}

PopPunkGuitarUltimateAudioProcessorEditor::PopPunkGuitarUltimateAudioProcessorEditor(PopPunkGuitarUltimateAudioProcessor& p)
    : AudioProcessorEditor(&p), processor(p)
{
    setWantsKeyboardFocus(true);
    setLookAndFeel(&premiumLookAndFeel);
    runtimeSkinRoot = getRuntimeSkinRoot();
    // Medium first-launch footprint for FL Studio; the JUCE resize corner remains enabled.
    // The responsive layout below keeps the main controls visible down to the minimum size.
    setSize(1024, 700);
    setResizable(true, true);
    setResizeLimits(900, 640, 1600, 1100);
    titleLabel.setText("PPGU", juce::dontSendNotification);
    titleLabel.setFont(makeThemeFont(themeManager.getPalette(), 28.0f, true, true));
    titleLabel.setColour(juce::Label::textColourId, themeManager.getPalette().token("text_primary"));
    addAndMakeVisible(titleLabel);
    subtitleLabel.setText("L3XTOWN AUDIO LAB", juce::dontSendNotification);
    subtitleLabel.setFont(makeThemeFont(themeManager.getPalette(), 9.5f, false, true));
    subtitleLabel.setColour(juce::Label::textColourId, themeManager.getPalette().token("accent"));
    addAndMakeVisible(subtitleLabel);
    presetBox.setTextWhenNothingSelected("FACTORY PRESET CATALOG");
    presetBox.setColour(juce::ComboBox::backgroundColourId, themeManager.getPalette().token("control_bg"));
    presetBox.setColour(juce::ComboBox::textColourId, themeManager.getPalette().token("text_primary"));
    presetBox.setColour(juce::ComboBox::outlineColourId, themeManager.getPalette().token("accent").withAlpha(0.5f));
    addAndMakeVisible(presetBox);
    categoryBox.addItem("ALL PRESETS", 1);
    categoryBox.addItem("MELODY", 2);
    categoryBox.addItem("PATTERN", 3);
    categoryBox.setSelectedId(1, juce::dontSendNotification);
    categoryBox.setColour(juce::ComboBox::backgroundColourId, themeManager.getPalette().token("control_bg"));
    categoryBox.setColour(juce::ComboBox::textColourId, themeManager.getPalette().token("text_primary"));
    addAndMakeVisible(categoryBox);
    presetSearch.setTextToShowWhenEmpty("SEARCH PRESETS...", themeManager.getPalette().token("text_secondary"));
    presetSearch.setColour(juce::TextEditor::backgroundColourId, themeManager.getPalette().token("control_bg"));
    presetSearch.setColour(juce::TextEditor::textColourId, themeManager.getPalette().token("text_primary"));
    presetSearch.setColour(juce::TextEditor::outlineColourId, themeManager.getPalette().token("accent").withAlpha(0.4f));
    addAndMakeVisible(presetSearch);
    loadFactoryPresetCatalog();
    presetBox.onChange = [this] { if (presetBox.getSelectedId() > 0 && presetBox.getSelectedId() <= static_cast<int>(visiblePresetIndices.size())) applyFactoryPreset(visiblePresetIndices[static_cast<size_t>(presetBox.getSelectedId()-1)]); };
    auto refreshPresetList = [this] {
        // Keep the current sound selected when it remains in the filtered list.
        // Filtering must never silently load a different preset.
        int previouslySelectedPreset = -1;
        const int oldSelectedId = presetBox.getSelectedId();
        if (oldSelectedId > 0 && oldSelectedId <= static_cast<int>(visiblePresetIndices.size()))
            previouslySelectedPreset = visiblePresetIndices[static_cast<size_t>(oldSelectedId - 1)];

        const auto query = presetSearch.getText().trim().toLowerCase();
        const int category = categoryBox.getSelectedId();
        visiblePresetIndices.clear();
        presetBox.clear(juce::dontSendNotification);
        for (size_t i = 0; i < factoryPresets.size(); ++i) {
            const auto& item = factoryPresets[i];
            if (category == 2 && item.mode != "MELODY") continue;
            if (category == 3 && item.mode != "PATTERN") continue;

            const auto matchesQuery = query.isEmpty()
                || item.name.toLowerCase().contains(query)
                || item.category.toLowerCase().contains(query)
                || item.mode.toLowerCase().contains(query)
                || item.soundCharacter.toLowerCase().contains(query)
                || item.groove.toLowerCase().contains(query)
                || item.articulation.toLowerCase().contains(query);
            if (!matchesQuery) continue;

            visiblePresetIndices.push_back(static_cast<int>(i));
            presetBox.addItem(item.name, static_cast<int>(visiblePresetIndices.size()));
        }

        const auto selected = std::find(visiblePresetIndices.begin(), visiblePresetIndices.end(),
                                        previouslySelectedPreset);
        if (previouslySelectedPreset >= 0 && selected != visiblePresetIndices.end())
            presetBox.setSelectedId(static_cast<int>(std::distance(visiblePresetIndices.begin(), selected)) + 1,
                                    juce::dontSendNotification);
        else
            presetBox.setSelectedId(0, juce::dontSendNotification);
    };
    categoryBox.onChange = refreshPresetList;
    presetSearch.onTextChange = refreshPresetList;
    refreshPresetList();
    loadButton.setComponentID("Import_Guitar");
    loadButton.setColour(juce::TextButton::buttonColourId, themeManager.getPalette().token("accent"));
    loadButton.setColour(juce::TextButton::textColourOffId, themeManager.getPalette().token("window_bg"));
    loadButton.onClick = [this] { openImportGuitarPanel(); };
    addAndMakeVisible(loadButton);
    auxiliaryWorkspace = std::make_unique<PPGUMultiWindowWorkspace>();
    if (auto* workspaceSettings = uiProperties.getUserSettings())
    {
        auxiliaryWorkspace->setPanelScale(static_cast<float>(
            workspaceSettings->getDoubleValue("workspacePanelScale", 1.0)));
        auxiliaryWorkspace->setPanelGap(
            workspaceSettings->getIntValue("workspacePanelGap", 12));
    }
    auxiliaryWorkspace->setSurfaceColours(themeManager.getPalette().token("window_bg"),
        themeManager.getPalette().token("panel"), themeManager.getPalette().token("control_border"),
        themeManager.getPalette().token("accent"), themeManager.getPalette().token("text_primary"));
    addAndMakeVisible(*auxiliaryWorkspace);
    auxiliaryWorkspace->setVisible(false);
    settingsButton.setComponentID("Settings");
    settingsButton.setTooltip("Workspace scale, panel spacing and visual defaults.");
    settingsButton.setColour(juce::TextButton::buttonColourId, themeManager.getPalette().token("panel_elevated"));
    settingsButton.setColour(juce::TextButton::textColourOffId, themeManager.getPalette().token("text_primary"));
    settingsButton.onClick = [this] { openSettingsPanel(); };
    addAndMakeVisible(settingsButton);
    skinButton.setComponentID("SKIN_button");
    skinButton.setTooltip("Open the premium visual skin gallery. Ctrl+K.");
    skinButton.onClick = [this] { openSkinGalleryPanel(); };
    addAndMakeVisible(skinButton);
    autoChordsButton.setTooltip("Open chord and harmony configuration workspace.");
    autoChordsButton.setColour(juce::TextButton::buttonColourId, themeManager.getPalette().token("control_bg"));
    autoChordsButton.setColour(juce::TextButton::textColourOffId, themeManager.getPalette().token("text_primary"));
    autoChordsButton.onClick = [this] { openAutoChordsPanel(); };
    addAndMakeVisible(autoChordsButton);

    // Local discovery and curation remain gated until their safe backends are ready.
    autoSoundHunterButton.setComponentID("Auto_Discover");
    curatorButton.setComponentID("Curator");
    for (auto* unavailable : { &autoSoundHunterButton, &curatorButton })
    {
        unavailable->setEnabled(false);
        unavailable->setColour(juce::TextButton::buttonColourId, themeManager.getPalette().token("lowlight"));
        unavailable->setColour(juce::TextButton::textColourOffId, themeManager.getPalette().token("text_disabled"));
        addAndMakeVisible(*unavailable);
    }
    autoSoundHunterButton.setTooltip("AUTO SOUND HUNTER is not implemented yet. No search or auto-import action is available.");
    curatorButton.setTooltip("CURATOR is not implemented yet. No asset is marked approved.");

    aboutButton.setComponentID("About");
    aboutButton.setEnabled(true);
    aboutButton.setTooltip("ABOUT — verified product and build information.");
    aboutButton.setColour(juce::TextButton::buttonColourId, themeManager.getPalette().token("panel_elevated"));
    aboutButton.setColour(juce::TextButton::textColourOffId, themeManager.getPalette().token("text_primary"));
    aboutButton.onClick = [this]
    {
        juce::AlertWindow::showMessageBoxAsync(
            juce::MessageBoxIconType::NoIcon,
            "ABOUT  /  POP PUNK GUITAR ULTIMATE",
            juce::String(JucePlugin_Name) + "\nVersion 4.0.0"
            + "\nVST3 Instrument  /  Windows x64"
            + "\n\nNEON STAGE interface, MIDI guitar performance, pattern playback and built-in effects."
            + "\n\nAudio sample rate and buffer size are controlled by the host DAW."
            + "\n\nSample libraries remain user-managed; use only content whose licence permits your use.");
    };
    addAndMakeVisible(aboutButton);
    statusLabel.setText("NO LIBRARY LOADED  /  LOAD A LICENSED SFZ INSTRUMENT", juce::dontSendNotification);
    const auto savedSfzPath = processor.getCurrentSfzFilePath();
    if (savedSfzPath.isNotEmpty())
    {
        const juce::File savedSfzFile(savedSfzPath);
        statusLabel.setText(savedSfzFile.existsAsFile()
            ? "SAVED LIBRARY  /  " + savedSfzFile.getFileName()
            : "LIBRARY FILE NOT FOUND  /  " + savedSfzFile.getFileName(),
            juce::dontSendNotification);
    }
    statusLabel.setColour(juce::Label::textColourId, themeManager.getPalette().token("text_secondary"));
    statusLabel.setFont(makeThemeFont(themeManager.getPalette(), 11.0f, false, false));
    addAndMakeVisible(statusLabel);
    melodyTab.setClickingTogglesState(false);
    patternTab.setClickingTogglesState(false);
    for (auto* b : { &melodyTab, &patternTab }) {
        b->setColour(juce::TextButton::buttonColourId, themeManager.getPalette().token("control_bg"));
        b->setColour(juce::TextButton::textColourOffId, themeManager.getPalette().token("text_primary"));
        addAndMakeVisible(*b);
    }
    modeBox.addItem("MELODY", 1);
    modeBox.addItem("PATTERN", 2);
    modeBox.setColour(juce::ComboBox::backgroundColourId, themeManager.getPalette().token("control_bg"));
    modeBox.setColour(juce::ComboBox::textColourId, themeManager.getPalette().token("text_primary"));
    modeBox.setColour(juce::ComboBox::outlineColourId, themeManager.getPalette().token("accent").withAlpha(0.5f));
    addAndMakeVisible(modeBox);
    modeAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ComboBoxAttachment>(processor.parameters, "playMode", modeBox);
    startModeBox.addItem("HOST", 1);
    startModeBox.addItem("HOST START", 2);
    startModeBox.addItem("INTERNAL", 3);
    startModeBox.setColour(juce::ComboBox::backgroundColourId, themeManager.getPalette().token("control_bg"));
    startModeBox.setColour(juce::ComboBox::textColourId, themeManager.getPalette().token("text_primary"));
    startModeBox.setColour(juce::ComboBox::outlineColourId, themeManager.getPalette().token("accent").withAlpha(0.5f));
    addAndMakeVisible(startModeBox);
    startModeAttachment = std::make_unique<juce::AudioProcessorValueTreeState::ComboBoxAttachment>(processor.parameters, "syncMode", startModeBox);
    chordDiagram = std::make_unique<PPGUChordDiagram>();
    if (auto* diagram = dynamic_cast<PPGUChordDiagram*>(chordDiagram.get()))
        diagram->setPalette(themeManager.getPalette());
    addAndMakeVisible(*chordDiagram);

    // FX EDIT is an auxiliary workspace, not the central PLAYING CORE surface.
    // Keep the component factory-independent; each rack switch opens its own editor window.
    mainFxEdit = std::make_unique<PPGUFXEditPanel>(processor, 0);
    addChildComponent(*mainFxEdit);

    keyboard = std::make_unique<juce::MidiKeyboardComponent>(processor.keyboardState, juce::MidiKeyboardComponent::horizontalKeyboard);
    keyboard->setAvailableRange(36, 84);
    keyboard->setKeyWidth(18.0f);
    keyboard->setColour(juce::MidiKeyboardComponent::whiteNoteColourId, themeManager.getPalette().token("highlight"));
    keyboard->setColour(juce::MidiKeyboardComponent::blackNoteColourId, themeManager.getPalette().token("control_bg"));
    keyboard->setColour(juce::MidiKeyboardComponent::keySeparatorLineColourId, themeManager.getPalette().token("control_border"));
    keyboard->setColour(juce::MidiKeyboardComponent::mouseOverKeyOverlayColourId, themeManager.getPalette().token("accent").withAlpha(0.35f));
    keyboard->setColour(juce::MidiKeyboardComponent::keyDownOverlayColourId, themeManager.getPalette().token("accent").withAlpha(0.85f));
    addAndMakeVisible(*keyboard);
    performanceDisplay = std::make_unique<PPGUPerformanceDisplay>(processor);
    addAndMakeVisible(*performanceDisplay);
    melodyTab.onClick = [this] { modeBox.setSelectedId(1); };
    patternTab.onClick = [this] { modeBox.setSelectedId(2); openPatternSectionPanel(); };
    modeBox.onChange = [this]
    {
        const bool isMelody = modeBox.getSelectedId() == 1;
        melodyTab.setToggleState(isMelody, juce::dontSendNotification);
        patternTab.setToggleState(!isMelody, juce::dontSendNotification);
        if (chordDiagram != nullptr)
            chordDiagram->setVisible(!isMelody);
        melodyTab.repaint();
        patternTab.repaint();
    };
    modeBox.onChange();
    for (size_t i = 0; i < knobs.size(); ++i) {
        configureKnob(knobs[i], knobLabels[i], knobNames[i]);
        knobs[i].setComponentID("knob" + juce::String(static_cast<int>(i + 1)).paddedLeft('0', 2));
        knobAttachments[i] = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment>(processor.parameters, parameterIDs[i], knobs[i]);
    }
    static constexpr std::array<const char*, 7> fxTooltips {{
        "COMPRESSOR — enable or bypass dynamics compression. Click to open detailed controls.",
        "EQ — enable or bypass the tone equalizer. Click to open detailed controls.",
        "DISTORTION — enable or bypass the distortion stage. Click to open detailed controls.",
        "CHORUS — enable or bypass stereo modulation. Click to open detailed controls.",
        "DELAY — enable or bypass tempo-aware delay. Click to open detailed controls.",
        "REVERB — enable or bypass the room/space processor. Click to open detailed controls.",
        "CABINET IR — enable or bypass cabinet impulse response. Click to open detailed controls."
    }};
    for (size_t i = 0; i < fxButtons.size(); ++i) {
        auto& b = fxButtons[i];
        b.setTooltip(fxTooltips[i]);
        b.setName(b.getButtonText());
        b.setClickingTogglesState(true);
        b.setColour(juce::TextButton::buttonColourId, themeManager.getPalette().token("control_bg"));
        b.setColour(juce::TextButton::buttonOnColourId, themeManager.getPalette().token("accent"));
        b.setColour(juce::TextButton::textColourOffId, themeManager.getPalette().token("text_primary"));
        b.setColour(juce::TextButton::textColourOnId, themeManager.getPalette().token("window_bg"));
        fxAttachments[i] = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment>(processor.parameters, fxParameterIDs[i], b);
        b.setComponentID("fx_switch" + juce::String(static_cast<int>(i + 1)).paddedLeft('0', 2));
        b.onClick = [this, i]
        {
            // The detail editor keeps FLANGER as an optional processor page,
            // while the approved primary chain remains seven items.
            static constexpr std::array<int, 7> detailGroups {{ 0, 1, 2, 3, 5, 6, 7 }};
            openFxEditPanel(detailGroups[i]);
        };
        addAndMakeVisible(b);
    }
    ampTitle.setText("AMP & TONE", juce::dontSendNotification);
    ampTitle.setTooltip("Amplifier and tone controls. Use the PLAYING CORE knobs for gain and EQ.");
    fxTitle.setText("FX CHAIN", juce::dontSendNotification);
    fxTitle.setTooltip("Seven real-time effect bypass switches. Click a switch to open its detailed editor.");
    playbackTitle.setText("PLAYBACK", juce::dontSendNotification);
    for (auto* l : { &ampTitle, &fxTitle, &playbackTitle }) {
        l->setFont(makeThemeFont(themeManager.getPalette(), 15.0f, false, true));
        l->setColour(juce::Label::textColourId, themeManager.getPalette().token("accent"));
        addAndMakeVisible(*l);
    }
    juce::PropertiesFile::Options options;
    options.applicationName = "PPGU";
    options.filenameSuffix = "settings";
    options.folderName = "L3XTOWN";
    uiProperties.setStorageParameters(options);
    int restoredWidth = 1024;
    int restoredHeight = 700;
    if (auto* settings = uiProperties.getUserSettings())
    {
        auxiliaryWorkspace->setPanelScale(static_cast<float>(settings->getDoubleValue("workspacePanelScale", 1.0)));
        auxiliaryWorkspace->setPanelGap(settings->getIntValue("workspacePanelGap", 12));
        restoredWidth = settings->getIntValue("editorWidth", restoredWidth);
        restoredHeight = settings->getIntValue("editorHeight", restoredHeight);
    }
    loadSavedSkin();
    applyPalette();
    uiSettingsReady = true;
    setSize(juce::jlimit(900, 1600, restoredWidth),
            juce::jlimit(640, 1100, restoredHeight));
}

PopPunkGuitarUltimateAudioProcessorEditor::~PopPunkGuitarUltimateAudioProcessorEditor()
{
    stopTimer();
    timerCallback();
    setLookAndFeel(nullptr);
}

void PopPunkGuitarUltimateAudioProcessorEditor::timerCallback()
{
    stopTimer();
    if (!uiSettingsReady)
        return;
    if (auto* settings = uiProperties.getUserSettings())
    {
        settings->setValue("editorWidth", getWidth());
        settings->setValue("editorHeight", getHeight());
        settings->saveIfNeeded();
    }
}

void PopPunkGuitarUltimateAudioProcessorEditor::configureKnob(juce::Slider& s, juce::Label& l, const juce::String& name)
{
    s.setSliderStyle(juce::Slider::RotaryHorizontalVerticalDrag);
    s.setName(name);
    s.setTooltip(name + " — adjust the live instrument parameter. The numeric readout shows the current value.");
    s.setTextBoxStyle(juce::Slider::TextBoxBelow, false, 46, 16);
    s.setColour(juce::Slider::rotarySliderFillColourId, themeManager.getPalette().token("accent"));
    s.setColour(juce::Slider::rotarySliderOutlineColourId, themeManager.getPalette().token("control_border"));
    s.setColour(juce::Slider::thumbColourId, themeManager.getPalette().token("text_primary"));
    s.setColour(juce::Slider::textBoxTextColourId, themeManager.getPalette().token("text_primary"));
    s.setColour(juce::Slider::textBoxOutlineColourId, juce::Colours::transparentBlack);
    addAndMakeVisible(s);
    l.setText(name, juce::dontSendNotification);
    l.setFont(makeThemeFont(themeManager.getPalette(), 9.5f, false, true));
    l.setColour(juce::Label::textColourId, themeManager.getPalette().token("text_secondary"));
    l.setJustificationType(juce::Justification::centred);
    addAndMakeVisible(l);
}

void PopPunkGuitarUltimateAudioProcessorEditor::drawPanel(
    juce::Graphics& g, juce::Rectangle<int> area, const juce::String& sectionTitle)
{
    const auto& p = themeManager.getPalette();
    const auto bounds = area.toFloat();

    // Layered graphite chassis: a restrained soft shadow separates each
    // module from the stage without introducing a fake animated highlight.
    juce::DropShadow(p.token("shadow").withAlpha(0.78f), 14, { 0, 5 })
        .drawForRectangle(g, area);
    g.setGradientFill(juce::ColourGradient(p.token("panel_elevated"),
                                           bounds.getX(), bounds.getY(),
                                           p.token("panel"),
                                           bounds.getX(), bounds.getBottom(), false));
    g.fillRoundedRectangle(bounds, 12.0f);
    drawThemeArtworkLayers(g, area, p, 0.10f, 0.42f, 0.0f);
    if (p.framesPanelsSpriteSheet.isValid())
    {
        const auto header = area.reduced(1, 1).removeFromTop(30);
        g.drawImage(p.framesPanelsSpriteSheet, header.getX(), header.getY(),
                    header.getWidth(), header.getHeight(), 30, 650, 450, 60);
    }

    // Machined double-bezel: cool upper specular edge, dark lower bevel and
    // a fine inner contour. All colours come from the active skin palette.
    g.setColour(p.token("highlight").withAlpha(0.30f));
    g.drawRoundedRectangle(bounds.reduced(1.0f), 11.0f, 1.0f);
    g.setColour(p.token("lowlight").withAlpha(0.92f));
    g.drawLine(bounds.getX() + 12.0f, bounds.getBottom() - 1.5f,
               bounds.getRight() - 12.0f, bounds.getBottom() - 1.5f, 1.2f);
    g.setColour(p.token("control_border").withAlpha(0.78f));
    g.drawRoundedRectangle(bounds.reduced(0.5f), 12.0f, 1.0f);
    g.setColour(p.token("highlight").withAlpha(0.12f));
    g.drawRoundedRectangle(bounds.reduced(3.0f), 9.0f, 0.7f);
    drawNineSliceFrame(g, p.framesPanelsSpriteSheet, area, 0.58f);

    // Section chrome belongs to the visual shell; it does not create or
    // reassign controls and follows the active theme's semantic palette.
    g.setColour(p.token("text_secondary"));
    g.setFont(makeThemeFont(p, 9.5f, false, true));
    auto heading = area.reduced(15, 7).removeFromTop(19);
    g.drawText(sectionTitle, heading, juce::Justification::centredLeft, true);

    g.setColour(p.token("accent").withAlpha(0.9f));
    g.fillRoundedRectangle(bounds.getX() + 15.0f, bounds.getY() + 29.0f,
                           34.0f, 2.0f, 1.0f);
    g.setColour(p.token("control_border").withAlpha(0.45f));
    g.drawHorizontalLine(static_cast<int>(bounds.getY() + 33.0f),
                         bounds.getX() + 15.0f, bounds.getRight() - 15.0f);
}

void PopPunkGuitarUltimateAudioProcessorEditor::paint(juce::Graphics& g)
{
    const auto& p = themeManager.getPalette();
    g.fillAll(p.token("window_bg"));
    drawThemeArtworkLayers(g, getLocalBounds(), p, 0.16f, 0.78f, 0.055f, true);

    auto area = getLocalBounds().reduced(14);
    area.removeFromTop(48);
    area.removeFromBottom(132);
    area.removeFromTop(8);

    const int leftWidth = juce::jlimit(180, 220, area.getWidth() / 5);
    const int rightWidth = juce::jlimit(240, 285, area.getWidth() / 4);
    auto left = area.removeFromLeft(leftWidth);
    area.removeFromLeft(10);
    auto right = area.removeFromRight(rightWidth);
    area.removeFromRight(10);

    drawPanel(g, left, "PRESETS");
    drawPanel(g, area, "PLAYING CORE");
    if (p.heroArtwork.isValid())
    {
        // The approved main-screen reference gives the guitar artwork its own
        // stage/banner above the nine-control strip, not a watermark behind knobs.
        auto stage = area.reduced(8, 6);
        stage.removeFromTop(38);
        const int stageHeight = juce::jlimit(72, 150, juce::jmax(1, area.getHeight() - 45) / 3);
        stage = stage.removeFromTop(juce::jmin(stageHeight, stage.getHeight()));
        g.saveState();
        g.reduceClipRegion(stage);
        g.setOpacity(0.96f);
        g.drawImageWithin(p.heroArtwork, stage.getX(), stage.getY(),
                          juce::jmax(1, stage.getWidth()),
                          juce::jmax(1, stage.getHeight()),
                          juce::RectanglePlacement::centred);
        g.setColour(p.token("window_bg").withAlpha(0.16f));
        g.fillRect(stage);
        g.restoreState();
        g.setColour(p.token("control_border").withAlpha(0.8f));
        g.drawRoundedRectangle(stage.toFloat(), 7.0f, 1.0f);
    }
    drawPanel(g, right, "AMP & TONE");
}

void PopPunkGuitarUltimateAudioProcessorEditor::resized()
{
    // Debounce disk persistence while the user drags the resize corner.
    if (uiSettingsReady)
        startTimer(450);

    auto bounds = getLocalBounds().reduced(14);
    if (auxiliaryWorkspace != nullptr)
        auxiliaryWorkspace->setBounds(bounds);

    // Approved NEON STAGE three-zone composition:
    // LEFT preset browser / CENTER Playing Core (nine controls) / RIGHT Amp & Tone + FX rack.
    auto header = bounds.removeFromTop(48);
    titleLabel.setBounds(header.removeFromLeft(105).reduced(2, 4));
    subtitleLabel.setBounds(18, 47, 150, 14);
    header.removeFromLeft(8);
    skinButton.setBounds(header.removeFromRight(78).reduced(2, 5));
    aboutButton.setBounds(header.removeFromRight(72).reduced(2, 5));
    settingsButton.setBounds(header.removeFromRight(92).reduced(2, 5));
    curatorButton.setBounds(header.removeFromRight(88).reduced(2, 5));
    autoSoundHunterButton.setBounds(header.removeFromRight(112).reduced(2, 5));
    autoChordsButton.setBounds(header.removeFromRight(112).reduced(2, 5));
    loadButton.setBounds(header.removeFromRight(112).reduced(2, 5));
    header.removeFromRight(8);

    // Lower performance strip: live display, 49-key MIDI keyboard and library status.
    auto footer = bounds.removeFromBottom(132);
    statusLabel.setBounds(footer.removeFromBottom(22).reduced(3, 1));
    footer.removeFromBottom(4);
    if (performanceDisplay != nullptr)
        performanceDisplay->setBounds(footer.removeFromTop(42).reduced(2, 1));
    footer.removeFromTop(5);
    if (keyboard != nullptr)
        keyboard->setBounds(footer.reduced(2, 2));

    bounds.removeFromTop(8);
    constexpr int workspaceGap = 10;
    const int leftWidth = juce::jlimit(180, 220, bounds.getWidth() / 5);
    const int rightWidth = juce::jlimit(240, 285, bounds.getWidth() / 4);
    auto left = bounds.removeFromLeft(leftWidth);
    bounds.removeFromLeft(workspaceGap);
    auto right = bounds.removeFromRight(rightWidth);
    bounds.removeFromRight(workspaceGap);
    auto centre = bounds;

    // LEFT: searchable factory catalog and the PATTERN-only chord reference.
    left.removeFromTop(34);
    categoryBox.setBounds(left.removeFromTop(34).reduced(4, 2));
    left.removeFromTop(4);
    presetSearch.setBounds(left.removeFromTop(34).reduced(4, 2));
    left.removeFromTop(4);
    presetBox.setBounds(left.removeFromTop(40).reduced(4, 2));
    left.removeFromTop(6);
    if (chordDiagram != nullptr)
    {
        chordDiagram->setVisible(modeBox.getSelectedId() == 2);
        chordDiagram->setBounds(left.reduced(4, 2));
    }

    // CENTER: approved reference layout — all nine real APVTS controls in one horizontal row.
    auto modeRow = centre.removeFromTop(38);
    melodyTab.setBounds(modeRow.removeFromLeft(92).reduced(2, 3));
    patternTab.setBounds(modeRow.removeFromLeft(92).reduced(2, 3));
    modeBox.setBounds(modeRow.removeFromLeft(138).reduced(2, 3));
    startModeBox.setBounds(modeRow.reduced(2, 3));
    centre.removeFromTop(7);

    // Dedicated guitar stage/banner above the controls, matching the approved
    // main-screen reference. Artwork is decorative only; no control hit target
    // or processor parameter is placed over this region.
    const int stageHeight = juce::jlimit(72, 150, centre.getHeight() / 3);
    centre.removeFromTop(juce::jmin(stageHeight, centre.getHeight()));
    centre.removeFromTop(6);

    // Keep the nine controls in a single evenly-spaced row at every supported
    // editor size. The APVTS attachments, IDs, ordering and DSP are unchanged.
    const int knobCellWidth = centre.getWidth() / static_cast<int>(knobs.size());
    const int knobDiameter = juce::jmax(32,
        juce::jmin(92, juce::jmin(knobCellWidth - 8, centre.getHeight() - 26)));
    const int labelHeight = 20;
    const int rowHeight = knobDiameter + labelHeight;
    const int rowY = centre.getY() + juce::jmax(0, (centre.getHeight() - rowHeight) / 2);
    for (size_t i = 0; i < knobs.size(); ++i)
    {
        const int x = centre.getX() + static_cast<int>(i) * knobCellWidth;
        const int cellWidth = (i + 1 == knobs.size())
            ? centre.getRight() - x : knobCellWidth;
        const int diameter = juce::jmin(knobDiameter, cellWidth - 6);
        const int knobX = x + (cellWidth - diameter) / 2;
        knobs[i].setBounds(knobX, rowY, diameter, diameter);
        knobLabels[i].setBounds(x + 1, rowY + knobDiameter + 2,
                                juce::jmax(1, cellWidth - 2), labelHeight);
    }

    // RIGHT: AMP & TONE rack with exactly seven real APVTS FX switches.
    right.removeFromTop(34);
    const int ampHeaderHeight = juce::jlimit(30, 42, right.getHeight() / 4);
    ampTitle.setBounds(right.removeFromTop(ampHeaderHeight).reduced(5, 1));
    fxTitle.setVisible(true);
    fxTitle.setBounds(right.removeFromTop(24).reduced(5, 1));
    right.removeFromTop(3);

    // Seven existing FX bypass controls form one horizontal chain, as in the
    // approved reference. Each button remains bound to its original APVTS ID.
    const int fxCellWidth = right.getWidth() / static_cast<int>(fxButtons.size());
    for (size_t i = 0; i < fxButtons.size(); ++i)
    {
        const int x = right.getX() + static_cast<int>(i) * fxCellWidth;
        const int width = (i + 1 == fxButtons.size())
            ? right.getRight() - x : fxCellWidth;
        fxButtons[i].setBounds(x + 1, right.getY() + 2,
                               juce::jmax(1, width - 2), juce::jmax(1, right.getHeight() - 4));
    }
    if (mainFxEdit != nullptr)
        mainFxEdit->setVisible(false);
    playbackTitle.setVisible(false);
}

juce::File PopPunkGuitarUltimateAudioProcessorEditor::getRuntimeSkinRoot() const
{
#if JUCE_WINDOWS
 HMODULE module=nullptr;auto address=reinterpret_cast<LPCWSTR>(reinterpret_cast<std::uintptr_t>(&getPluginModuleAnchor));
 DWORD flags=GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT;
 if(GetModuleHandleExW(flags,address,&module)!=0&&module){std::array<wchar_t,32768> path{};DWORD n=GetModuleFileNameW(module,path.data(),(DWORD)path.size());
  if(n>0&&n<path.size()){juce::File f(fromWidePath(path.data(), static_cast<int>(n)));for(int i=0;i<8;++i){auto d=f.isDirectory()?f:f.getParentDirectory();if(d.getFileName().endsWithIgnoreCase(".vst3"))return d.getParentDirectory().getChildFile("Skins");f=d.getParentDirectory();}}}
#endif
 auto exe=juce::File::getSpecialLocation(juce::File::currentExecutableFile);auto beside=exe.getParentDirectory().getChildFile("Skins");if(beside.isDirectory())return beside;
 auto dev=juce::File::getCurrentWorkingDirectory().getChildFile("SKIN");return dev.isDirectory()?dev:beside;
}
int PopPunkGuitarUltimateAudioProcessorEditor::getSkinCount() const
{
    const auto registryFile = runtimeSkinRoot.getChildFile("theme_manifest.json");
    // The plugin always contains STILLWATER as an embedded fallback theme.
    // Without a neighbouring Skins package, keep the 16-slot ordinal model so
    // slot 10 remains addressable; unavailable external themes are simply omitted.
    if (!registryFile.existsAsFile()) return 16;
    const auto registry = juce::JSON::parse(registryFile.loadFileAsString());
    if (!registry.isObject()) return 16;
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
    // STILLWATER is shipped in the plugin binary; it does not depend on the
    // external skin package's runtimeReady flag or a neighbouring Skins folder.
    if (stableId == "skin-111")
        return 10;

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
            // A standalone VST3 still has a complete embedded visual theme.
            if (!loadSkinByIndex(10, false))
            {
                themeManager.resetToDefault();
                applyPalette();
            }
        }
    }
}

bool PopPunkGuitarUltimateAudioProcessorEditor::loadSkinByIndex(int ordinal, bool save)
{
    if (ordinal < 1 || ordinal > getSkinCount()) return false;
    const bool loaded = ordinal == 10
        ? themeManager.loadEmbeddedStillwater()
        : (getSkinManifest(ordinal).existsAsFile()
            && themeManager.loadFromFile(getSkinManifest(ordinal)));
    if (!loaded) themeManager.resetToDefault();
    applyPalette();
    if (save && loaded) persistSkinPreference();
    return loaded;
}

void PopPunkGuitarUltimateAudioProcessorEditor::openSkinGalleryPanel()
{
    if (auxiliaryWorkspace == nullptr) return;
    constexpr int galleryPanelId = 5;
    if (!auxiliaryWorkspace->isPanelOpen(galleryPanelId))
    {
        std::vector<PPGUSkinGalleryPanel::Skin> skins;
        const auto activeId = themeManager.getPalette().id;
        const int activeIndex = getSkinOrdinalForId(activeId);
        const auto count = getSkinCount();
        skins.reserve(static_cast<size_t>(juce::jmax(0, count)));
        for (int index = 1; index <= count; ++index)
        {
            const auto manifest = getSkinManifest(index);
            PPGUThemeManager candidate;
            juce::var root;
            if (index == 10)
            {
                if (!candidate.loadEmbeddedStillwater()) continue;
                int embeddedJsonSize = 0;
                const auto* embeddedJson = BinaryData::getNamedResource("theme_json", embeddedJsonSize);
                if (embeddedJson == nullptr || embeddedJsonSize <= 0) continue;
                root = juce::JSON::parse(juce::String::fromUTF8(embeddedJson, embeddedJsonSize));
            }
            else
            {
                if (!manifest.existsAsFile() || !candidate.loadFromFile(manifest)) continue;
                root = juce::JSON::parse(manifest.loadFileAsString());
            }
            const auto familyKey = root.getProperty("family", juce::var()).toString();
            const auto legacyCluster = root.getProperty("cluster", juce::var()).toString();
            const auto family = familyKey.isNotEmpty()
                ? familyKey.replace("_", " ").toUpperCase() : "LEGACY / CLUSTER " + legacyCluster;
            juce::File previewFile;
            const auto assets = root.getProperty("assets", juce::var());
            auto previewRelative = assets.getProperty("preview", juce::var()).toString();
            if (previewRelative.isEmpty()) previewRelative = "assets/preview.png";
            if (candidate.getPalette().id == "skin-053")
                previewRelative = "assets/background/main.png";
            if (!previewRelative.startsWith("/") && !previewRelative.contains(".."))
            {
                const auto candidatePreview = manifest.getParentDirectory().getChildFile(previewRelative);
                if (candidatePreview.isAChildOf(manifest.getParentDirectory()) && candidatePreview.existsAsFile())
                    previewFile = candidatePreview;
            }
            PPGUSkinGalleryPanel::Skin item;
            item.index = index; item.id = candidate.getPalette().id; item.name = candidate.getPalette().name;
            item.family = family; item.familyKey = familyKey.isNotEmpty() ? familyKey : "legacy";
            item.layout = root.getProperty("layout", "CLASSIC").toString().replace("_", " ");
            item.preview = previewFile; item.accent = candidate.getPalette().token("accent");
            item.active = candidate.getPalette().id == activeId; skins.push_back(std::move(item));
        }

        juce::Component::SafePointer<PopPunkGuitarUltimateAudioProcessorEditor> safe(this);
        const auto gallerySkinCount = static_cast<int>(skins.size());
        const auto closeGalleryAsync = [safe]()
        {
            juce::MessageManager::callAsync([safe]
            {
                if (safe == nullptr || safe->auxiliaryWorkspace == nullptr) return;
                safe->auxiliaryWorkspace->closePanel(5);
                if (safe->auxiliaryWorkspace->getOpenPanelCount() == 0)
                    safe->auxiliaryWorkspace->setVisible(false);
            });
        };
        juce::StringArray favoriteSkinIds;
        if (auto* settings = uiProperties.getUserSettings())
            favoriteSkinIds.addTokens(settings->getValue("skinGalleryFavorites"), ",", "");
        auto saveFavoriteSkinIds = [safe](const juce::StringArray& values)
        {
            if (safe == nullptr) return;
            if (auto* settings = safe->uiProperties.getUserSettings())
            {
                settings->setValue("skinGalleryFavorites", values.joinIntoString(","));
                settings->saveIfNeeded();
            }
        };
        auto gallery = std::make_unique<PPGUSkinGalleryPanel>(
            std::move(skins), themeManager.getPalette(), activeIndex, std::move(favoriteSkinIds),
            std::move(saveFavoriteSkinIds),
            [safe](int index) { return safe != nullptr && safe->loadSkinByIndex(index, false); },
            [safe, closeGalleryAsync](int index)
            {
                if (safe == nullptr || !safe->loadSkinByIndex(index, true)) return false;
                closeGalleryAsync(); return true;
            },
            [safe, closeGalleryAsync](int originalIndex)
            {
                if (safe != nullptr && originalIndex > 0) safe->loadSkinByIndex(originalIndex, false);
                closeGalleryAsync();
            });
        PPGUMultiWindowWorkspace::PanelSpec spec;
        spec.id = galleryPanelId;
        spec.title = "SKIN GALLERY  /  " + juce::String(gallerySkinCount) + " THEMES";
        spec.desired = { 940, 700 }; spec.minimum = { 500, 360 };
        spec.content = std::move(gallery);
        auxiliaryWorkspace->openPanel(std::move(spec));
    }
    auxiliaryWorkspace->setVisible(true); auxiliaryWorkspace->toFront(false);
}

void PopPunkGuitarUltimateAudioProcessorEditor::openSettingsPanel()
{
    if (auxiliaryWorkspace == nullptr)
        return;

    constexpr int settingsPanelId = 6;
    if (!auxiliaryWorkspace->isPanelOpen(settingsPanelId))
    {
        auto* properties = uiProperties.getUserSettings();
        const auto panelScale = properties != nullptr
            ? static_cast<float>(properties->getDoubleValue("workspacePanelScale", 1.0)) : 1.0f;
        const auto panelGap = properties != nullptr
            ? properties->getIntValue("workspacePanelGap", 12) : 12;

        juce::Component::SafePointer<PopPunkGuitarUltimateAudioProcessorEditor> safe(this);
        auto content = std::make_unique<PPGUSettingsPanel>(
            themeManager.getPalette(), panelScale, panelGap,
            [safe](float value)
            {
                if (safe == nullptr || safe->auxiliaryWorkspace == nullptr)
                    return;
                safe->auxiliaryWorkspace->setPanelScale(value);
                if (auto* settings = safe->uiProperties.getUserSettings())
                {
                    settings->setValue("workspacePanelScale", static_cast<double>(value));
                    settings->saveIfNeeded();
                }
            },
            [safe](int value)
            {
                if (safe == nullptr || safe->auxiliaryWorkspace == nullptr)
                    return;
                safe->auxiliaryWorkspace->setPanelGap(value);
                if (auto* settings = safe->uiProperties.getUserSettings())
                {
                    settings->setValue("workspacePanelGap", value);
                    settings->saveIfNeeded();
                }
            },
            [safe]
            {
                if (safe != nullptr)
                    safe->loadSkinByIndex(1, true);
            },
            [safe]
            {
                if (safe != nullptr)
                    safe->openSkinGalleryPanel();
            });

        PPGUMultiWindowWorkspace::PanelSpec spec;
        spec.id = settingsPanelId;
        spec.title = "SETTINGS  /  WORKSPACE";
        spec.desired = { 700, 520 };
        spec.minimum = { 420, 260 };
        spec.content = std::move(content);
        auxiliaryWorkspace->openPanel(std::move(spec));
    }

    auxiliaryWorkspace->setVisible(true);
    auxiliaryWorkspace->toFront(false);
}

void PopPunkGuitarUltimateAudioProcessorEditor::applyPalette()
{
 const auto& p=themeManager.getPalette();
 if (auto* diagram = dynamic_cast<PPGUChordDiagram*>(chordDiagram.get()))
     diagram->setPalette(p);
 if (auto* fxPanel = dynamic_cast<PPGUThemeAwarePanel*>(mainFxEdit.get()))
     fxPanel->setThemePalette(p);
 premiumLookAndFeel.setPalette(p);titleLabel.setFont(makeThemeFont(p, 28.0f, true, true));subtitleLabel.setFont(makeThemeFont(p, 9.5f, false, true));statusLabel.setFont(makeThemeFont(p, 11.0f));ampTitle.setFont(makeThemeFont(p, 15.0f, false, true));fxTitle.setFont(makeThemeFont(p, 15.0f, false, true));playbackTitle.setFont(makeThemeFont(p, 15.0f, false, true));if(performanceDisplay)performanceDisplay->setPalette(p);
 if (auxiliaryWorkspace != nullptr)
 {
     auxiliaryWorkspace->setSurfaceColours(p.token("window_bg"), p.token("panel"),
         p.token("control_border"), p.token("accent"), p.token("text_primary"));
     auxiliaryWorkspace->setThemePalette(p);
 }
 titleLabel.setColour(juce::Label::textColourId,p.token("text_primary"));subtitleLabel.setColour(juce::Label::textColourId,p.token("text_secondary"));statusLabel.setColour(juce::Label::textColourId,p.token("text_secondary"));
 ampTitle.setColour(juce::Label::textColourId,p.token("accent"));fxTitle.setColour(juce::Label::textColourId,p.token("accent"));playbackTitle.setColour(juce::Label::textColourId,p.token("accent"));
 for(auto* b:{&presetBox,&categoryBox,&modeBox,&startModeBox}){b->setColour(juce::ComboBox::backgroundColourId,p.token("control_bg"));b->setColour(juce::ComboBox::textColourId,p.token("text_primary"));b->setColour(juce::ComboBox::outlineColourId,p.token("control_border"));b->setColour(juce::ComboBox::arrowColourId,p.token("accent"));}
 presetSearch.setColour(juce::TextEditor::backgroundColourId,p.token("control_bg"));presetSearch.setColour(juce::TextEditor::textColourId,p.token("text_primary"));presetSearch.setColour(juce::TextEditor::outlineColourId,p.token("control_border"));presetSearch.setColour(juce::TextEditor::focusedOutlineColourId,p.token("highlight"));presetSearch.setColour(juce::TextEditor::highlightColourId,p.token("accent").withAlpha(.3f));
 loadButton.setColour(juce::TextButton::buttonColourId,p.token("accent"));loadButton.setColour(juce::TextButton::textColourOffId,p.token("window_bg"));settingsButton.setColour(juce::TextButton::buttonColourId,p.token("panel_elevated"));settingsButton.setColour(juce::TextButton::textColourOffId,p.token("text_primary"));skinButton.setColour(juce::TextButton::buttonColourId,p.token("panel_elevated"));skinButton.setColour(juce::TextButton::textColourOffId,p.token("text_primary"));skinButton.setTooltip("Active skin: "+p.name+"  /  Ctrl+K");
 for (auto* unavailable : { &autoSoundHunterButton, &curatorButton }) { unavailable->setColour(juce::TextButton::buttonColourId,p.token("lowlight")); unavailable->setColour(juce::TextButton::textColourOffId,p.token("text_disabled")); unavailable->setEnabled(false); }
 aboutButton.setEnabled(true); aboutButton.setColour(juce::TextButton::buttonColourId,p.token("panel_elevated")); aboutButton.setColour(juce::TextButton::textColourOffId,p.token("text_primary"));
 for(auto* b:{&melodyTab,&patternTab}){b->setColour(juce::TextButton::buttonColourId,p.token("control_bg"));b->setColour(juce::TextButton::buttonOnColourId,p.token("accent"));b->setColour(juce::TextButton::textColourOffId,p.token("text_primary"));b->setColour(juce::TextButton::textColourOnId,p.token("window_bg"));}
 for(auto& s:knobs){s.setColour(juce::Slider::rotarySliderFillColourId,p.token("accent"));s.setColour(juce::Slider::rotarySliderOutlineColourId,p.token("control_border"));s.setColour(juce::Slider::thumbColourId,p.token("text_primary"));s.setColour(juce::Slider::textBoxTextColourId,p.token("text_primary"));}
 for(auto& l:knobLabels){l.setFont(makeThemeFont(p,9.5f,false,true));l.setColour(juce::Label::textColourId,p.token("text_secondary"));}
 for(auto& b:fxButtons){b.setColour(juce::TextButton::buttonColourId,p.token("control_bg"));b.setColour(juce::TextButton::buttonOnColourId,p.token("accent"));b.setColour(juce::TextButton::textColourOffId,p.token("text_primary"));b.setColour(juce::TextButton::textColourOnId,p.token("window_bg"));}
 if(keyboard){keyboard->setColour(juce::MidiKeyboardComponent::whiteNoteColourId,p.token("highlight"));keyboard->setColour(juce::MidiKeyboardComponent::blackNoteColourId,p.token("control_bg"));keyboard->setColour(juce::MidiKeyboardComponent::keySeparatorLineColourId,p.token("control_border"));keyboard->setColour(juce::MidiKeyboardComponent::mouseOverKeyOverlayColourId,p.token("accent_glow").withAlpha(.3f));keyboard->setColour(juce::MidiKeyboardComponent::keyDownOverlayColourId,p.token("accent").withAlpha(.88f));}
 repaint();
}
void PopPunkGuitarUltimateAudioProcessorEditor::persistSkinPreference(){if(auto* s=uiProperties.getUserSettings()){s->setValue("skinId",themeManager.getPalette().id);s->saveIfNeeded();}}
bool PopPunkGuitarUltimateAudioProcessorEditor::keyPressed(const juce::KeyPress& k){if(k.getKeyCode()=='K'&&k.getModifiers().isCtrlDown()){openSkinGalleryPanel();return true;}return juce::AudioProcessorEditor::keyPressed(k);}

void PopPunkGuitarUltimateAudioProcessorEditor::loadFactoryPresetCatalog()
{
    factoryPresets.clear();
    const auto jsonText = juce::String::fromUTF8(BinaryData::factory_bank_300_json, BinaryData::factory_bank_300_jsonSize);
    const auto root = juce::JSON::parse(jsonText);
    if (!root.isObject()) { statusLabel.setText("FACTORY PRESET CATALOG ERROR", juce::dontSendNotification); return; }
    const auto append = [this](const juce::var& array, const juce::String& mode) {
        if (auto* values = array.getArray()) for (const auto& value : *values) {
            if (!value.isObject()) continue;
            FactoryPreset preset;
            auto reference = value.getProperty("referenceArtist", "").toString();
            auto displayName = value.getProperty("name", "Unnamed").toString();
            if (reference.isNotEmpty() && displayName.startsWithIgnoreCase(reference))
                displayName = displayName.substring(reference.length()).trim();
            preset.name = displayName;
            preset.category = "Original";
            preset.mode = mode;
            preset.soundCharacter = value.getProperty("soundCharacter", "Electric").toString();
            preset.groove = value.getProperty("groove", "").toString();
            preset.articulation = value.getProperty("articulation", "").toString();
            const auto params = value.getProperty("parameters", juce::var());
            preset.drive = static_cast<float>(params.getProperty("drive", 0.0));
            preset.tone = static_cast<float>(params.getProperty("tone", 5.0));
            preset.reverb = static_cast<float>(params.getProperty("reverb", 0.0));
            preset.outputDb = static_cast<float>(params.getProperty("outputDb", 0.0));
            factoryPresets.push_back(std::move(preset));
        }
    };
    append(root.getProperty("melodyPresets", juce::var()), "MELODY");
    append(root.getProperty("patternPresets", juce::var()), "PATTERN");
    statusLabel.setText("FACTORY CATALOG: "+juce::String(static_cast<int>(factoryPresets.size()))+" PRESETS", juce::dontSendNotification);
}

void PopPunkGuitarUltimateAudioProcessorEditor::applyFactoryPreset(int index)
{
    if (index < 0 || index >= static_cast<int>(factoryPresets.size())) return;
    const auto& preset = factoryPresets[static_cast<size_t>(index)];
    const auto setParameter = [this](const juce::String& id, float value) {
        if (auto* parameter = processor.parameters.getParameter(id))
            parameter->setValueNotifyingHost(parameter->convertTo0to1(value));
    };
    setParameter("distortionDrive", juce::jlimit(0.0f, 1.0f, preset.drive));
    setParameter("tone", juce::jlimit(0.0f, 10.0f, preset.tone));
    setParameter("reverbMix", juce::jlimit(0.0f, 1.0f, preset.reverb));
    setParameter("output", juce::jlimit(-24.0f, 12.0f, preset.outputDb));
    modeBox.setSelectedId(preset.mode == "PATTERN" ? 2 : 1, juce::sendNotification);
    if (preset.mode == "PATTERN")
    {
        const auto detail = preset.soundCharacter + (preset.groove.isNotEmpty() ? "  /  " + preset.groove : juce::String{});
        statusLabel.setText("PATTERN STYLE: " + detail + "  /  " + preset.articulation + "  /  PERFORMANCE ENGINE REQUIRED", juce::dontSendNotification);
    }
    else
        statusLabel.setText("MELODY TONE: " + preset.soundCharacter + "  /  ONE KEY = ONE NOTE  /  LOAD A LICENSED SFZ BANK", juce::dontSendNotification);
}
void PopPunkGuitarUltimateAudioProcessorEditor::openFxEditPanel(int selectedEffect)
{
    if (auxiliaryWorkspace == nullptr)
        return;
    constexpr int fxEditPanelId = 2101;
    if (auxiliaryWorkspace->isPanelOpen(fxEditPanelId))
    {
        if (auto* content = auxiliaryWorkspace->getPanelContent(fxEditPanelId))
            if (auto* panel = dynamic_cast<PPGUFXEditPanel*>(content))
                panel->setSelectedGroup(selectedEffect);
    }
    else
    {
        PPGUMultiWindowWorkspace::PanelSpec spec;
        spec.id = fxEditPanelId;
        spec.title = "FX EDIT  /  NEON STAGE";
        spec.desired = { 1000, 680 };
        spec.minimum = { 620, 440 };
        spec.content = std::make_unique<PPGUFXEditPanel>(processor, selectedEffect);
        if (!auxiliaryWorkspace->openPanel(std::move(spec)))
            return;
    }
    auxiliaryWorkspace->setVisible(true);
    auxiliaryWorkspace->toFront(false);
}


void PopPunkGuitarUltimateAudioProcessorEditor::openPatternSectionPanel()
{
    if (auxiliaryWorkspace == nullptr)
        return;
    constexpr int patternSectionPanelId = 2103;
    if (!auxiliaryWorkspace->isPanelOpen(patternSectionPanelId))
    {
        PPGUMultiWindowWorkspace::PanelSpec spec;
        spec.id = patternSectionPanelId;
        spec.title = "PATTERN  /  RHYTHM";
        spec.desired = { 620, 430 };
        spec.minimum = { 500, 420 };
        juce::Component::SafePointer<PopPunkGuitarUltimateAudioProcessorEditor> safeThis(this);
        spec.content = std::make_unique<PPGUPatternSectionPanel>(
            processor, presetBox.getText(),
            [safeThis] { if (safeThis != nullptr) safeThis->openImportGuitarPanel(); },
            [safeThis] { if (safeThis != nullptr) safeThis->openAutoChordsPanel(); },
            [safeThis] { if (safeThis != nullptr) safeThis->openPlayingStylePanel(); });
        if (!auxiliaryWorkspace->openPanel(std::move(spec)))
            return;
    }
    auxiliaryWorkspace->setVisible(true);
    auxiliaryWorkspace->toFront(false);
}

void PopPunkGuitarUltimateAudioProcessorEditor::openPlayingStylePanel()
{
    if (auxiliaryWorkspace == nullptr)
        return;
    constexpr int playingStylePanelId = 2104;
    if (!auxiliaryWorkspace->isPanelOpen(playingStylePanelId))
    {
        PPGUMultiWindowWorkspace::PanelSpec spec;
        spec.id = playingStylePanelId;
        spec.title = "PLAYING STYLE  /  ARTICULATION";
        spec.desired = { 760, 500 };
        spec.minimum = { 520, 380 };
        spec.content = std::make_unique<PPGUPlayingStylePanel>(processor);
        if (!auxiliaryWorkspace->openPanel(std::move(spec)))
            return;
    }
    auxiliaryWorkspace->setVisible(true);
    auxiliaryWorkspace->toFront(false);
}

void PopPunkGuitarUltimateAudioProcessorEditor::openAutoChordsPanel()
{
    if (auxiliaryWorkspace == nullptr)
        return;
    constexpr int autoChordsPanelId = 2102;
    if (!auxiliaryWorkspace->isPanelOpen(autoChordsPanelId))
    {
        PPGUMultiWindowWorkspace::PanelSpec spec;
        spec.id = autoChordsPanelId;
        spec.title = "AUTOCHORDS  /  HARMONY WORKSPACE";
        spec.desired = { 900, 620 };
        spec.minimum = { 560, 420 };
        spec.content = std::make_unique<PPGUAutoChordsPanel>(processor.parameters);
        if (!auxiliaryWorkspace->openPanel(std::move(spec)))
            return;
    }
    auxiliaryWorkspace->setVisible(true);
    auxiliaryWorkspace->toFront(false);
}

void PopPunkGuitarUltimateAudioProcessorEditor::openImportGuitarPanel()
{
    if (auxiliaryWorkspace == nullptr)
        return;
    constexpr int importGuitarPanelId = 1001;
    if (!auxiliaryWorkspace->isPanelOpen(importGuitarPanelId))
    {
        juce::Component::SafePointer<PopPunkGuitarUltimateAudioProcessorEditor> safeThis(this);
        PPGUMultiWindowWorkspace::PanelSpec spec;
        spec.id = importGuitarPanelId;
        spec.title = "IMPORT GUITAR";
        spec.desired = { 560, 360 };
        spec.minimum = { 300, 220 };
        const auto currentSfzPath = processor.getCurrentSfzFilePath();
        juce::String initialImportStatus;
        if (currentSfzPath.isNotEmpty())
        {
            const juce::File currentSfz(currentSfzPath);
            initialImportStatus = currentSfz.existsAsFile()
                ? "SAVED LIBRARY  /  " + currentSfz.getFileName()
                : "LIBRARY FILE NOT FOUND  /  " + currentSfz.getFileName();
        }
        spec.content = std::make_unique<PPGUImportGuitarPanel>(
            [safeThis](juce::Label* targetStatus, juce::Button* targetButton)
            {
                if (safeThis != nullptr)
                    safeThis->chooseSfzFile(targetStatus, targetButton);
            }, initialImportStatus);
        if (!auxiliaryWorkspace->openPanel(std::move(spec)))
            return;
    }
    auxiliaryWorkspace->setVisible(true);
    auxiliaryWorkspace->toFront(false);
    resized();
}

void PopPunkGuitarUltimateAudioProcessorEditor::chooseSfzFile(juce::Label* panelStatus, juce::Button* panelLoadButton)
{
    fileChooser=std::make_unique<juce::FileChooser>("Choose an SFZ guitar instrument",juce::File::getSpecialLocation(juce::File::userHomeDirectory),"*.sfz");
    juce::Component::SafePointer<PopPunkGuitarUltimateAudioProcessorEditor> safeThis(this);
    juce::Component::SafePointer<juce::Label> safePanelStatus(panelStatus);
    juce::Component::SafePointer<juce::Button> safePanelLoadButton(panelLoadButton);
    fileChooser->launchAsync(juce::FileBrowserComponent::openMode|juce::FileBrowserComponent::canSelectFiles,[safeThis, safePanelStatus, safePanelLoadButton](const juce::FileChooser& chooser){
        if(safeThis==nullptr) return; const auto selected=chooser.getResult(); if(selected==juce::File{}) return;
        safeThis->loadButton.setEnabled(false);
        if (safePanelLoadButton != nullptr)
            safePanelLoadButton->setEnabled(false);
        safeThis->statusLabel.setText("LOADING SFZ IN BACKGROUND...", juce::dontSendNotification);
        if (safePanelStatus != nullptr)
            safePanelStatus->setText("Loading SFZ in background...", juce::dontSendNotification);
        safeThis->processor.loadSfzFileAsync(selected, [safeThis, safePanelStatus, safePanelLoadButton, selected](ppgu::sampler::LoadReport report)
        {
            if (safeThis == nullptr)
                return;
            safeThis->loadButton.setEnabled(true);
            if (safePanelLoadButton != nullptr)
                safePanelLoadButton->setEnabled(true);
            const auto warningCount = static_cast<int>(report.warnings.size());
            const auto errorCount = static_cast<int>(report.errors.size());
            const auto fileName = selected.getFileName();
            const auto summary = juce::String(report.success ? "READY" : "LOAD FAILED")
                + "  /  " + fileName
                + "  /  " + juce::String(static_cast<int>(report.loadedRegions)) + " REGIONS"
                + "  /  " + juce::String(static_cast<int>(report.loadedSamples)) + " WAV SAMPLES"
                + "  /  " + juce::String(warningCount) + " WARNINGS"
                + "  /  " + juce::String(errorCount) + " ERRORS";
            safeThis->statusLabel.setText(summary, juce::dontSendNotification);

            if (safePanelStatus != nullptr)
            {
                juce::String details = summary;
                details += "\nSFZ DEFINITION: 1 selected file";
                if (!report.warnings.empty())
                {
                    details += "\n\nWARNINGS:";
                    const auto shown = juce::jmin(3, warningCount);
                    for (int i = 0; i < shown; ++i)
                        details += "\n• " + juce::String(report.warnings[static_cast<size_t>(i)]);
                    if (warningCount > shown)
                        details += "\n• ... +" + juce::String(warningCount - shown) + " more";
                }
                if (!report.errors.empty())
                {
                    details += "\n\nERRORS:";
                    const auto shown = juce::jmin(3, errorCount);
                    for (int i = 0; i < shown; ++i)
                        details += "\n• " + juce::String(report.errors[static_cast<size_t>(i)]);
                    if (errorCount > shown)
                        details += "\n• ... +" + juce::String(errorCount - shown) + " more";
                }
                safePanelStatus->setText(details, juce::dontSendNotification);
            }
        });
    });
}
