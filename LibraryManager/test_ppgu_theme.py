from __future__ import annotations

import re
import unittest

from ppgu_theme import (
    CANONICAL_SKIN_ID,
    CANONICAL_SKIN_NAME,
    LOGICAL_SKIN_SLOT,
    NEON_STAGE_PALETTE,
    NEON_STAGE_THEME,
    PALETTE_KEYS,
    _FALLBACK_PALETTE,
    load_neon_stage_theme,
    resource_path,
    configure_neon_stage_ttk,
)


class NeonStageThemeTests(unittest.TestCase):
    def test_logical_slot_resolves_to_canonical_skin_053(self) -> None:
        self.assertEqual(LOGICAL_SKIN_SLOT, "SKIN-1")
        self.assertEqual(CANONICAL_SKIN_ID, "skin-053")
        self.assertEqual(CANONICAL_SKIN_NAME, "NEON STAGE DEFAULT")
        self.assertEqual(NEON_STAGE_THEME["id"], CANONICAL_SKIN_ID)
        self.assertEqual(NEON_STAGE_THEME["name"], CANONICAL_SKIN_NAME)
        self.assertFalse(NEON_STAGE_THEME.get("_fallback", False))

    def test_all_23_palette_tokens_are_present_and_valid(self) -> None:
        self.assertEqual(set(NEON_STAGE_PALETTE), set(PALETTE_KEYS))
        for token, value in NEON_STAGE_PALETTE.items():
            with self.subTest(token=token):
                self.assertRegex(value, re.compile(r"^#[0-9A-Fa-f]{6}$"))

    def test_exact_ppgu_neon_stage_signature(self) -> None:
        self.assertEqual(NEON_STAGE_PALETTE["window_bg"], "#000612")
        self.assertEqual(NEON_STAGE_PALETTE["panel"], "#010B1C")
        self.assertEqual(NEON_STAGE_PALETTE["accent"], "#075CE8")
        self.assertEqual(NEON_STAGE_PALETTE["accent_glow"], "#00BFFF")
        self.assertEqual(NEON_STAGE_PALETTE["accent_purple"], "#7115B8")
        self.assertEqual(NEON_STAGE_PALETTE["accent_magenta"], "#E51BD4")
        self.assertEqual(NEON_STAGE_PALETTE["lcd_bg"], "#02091E")
        self.assertEqual(NEON_STAGE_PALETTE["lcd_text"], "#8CEAFF")
        self.assertTrue(NEON_STAGE_THEME["reduceInEco"])
        self.assertNotEqual(NEON_STAGE_PALETTE["accent"], "#D5FF45")
        self.assertNotEqual(NEON_STAGE_PALETTE["accent_glow"], "#DEFF6E")

    def test_missing_theme_uses_the_same_approved_fallback_palette(self) -> None:
        from unittest.mock import patch
        from pathlib import Path

        missing_manifest = Path("/definitely_missing_ppgu_theme/theme.json")
        with patch("ppgu_theme.resource_path", return_value=missing_manifest):
            fallback = load_neon_stage_theme()
        self.assertTrue(fallback.get("_fallback"))
        self.assertEqual(fallback["id"], CANONICAL_SKIN_ID)
        self.assertEqual(fallback["name"], CANONICAL_SKIN_NAME)
        self.assertEqual(fallback["palette"], _FALLBACK_PALETTE)
        self.assertEqual(fallback["palette"], NEON_STAGE_PALETTE)

    def test_theme_is_visual_only(self) -> None:
        compatibility = NEON_STAGE_THEME["compatibility"]
        self.assertFalse(compatibility["apvtsChanges"])
        self.assertFalse(compatibility["layoutChanges"])
        self.assertFalse(compatibility["audioChanges"])

    def test_shared_ttk_widgets_receive_neon_stage_colors(self) -> None:
        class FakeStyle:
            def __init__(self):
                self.configured = {}
                self.mapped = {}

            def configure(self, name, **options):
                self.configured[name] = options

            def map(self, name, **options):
                self.mapped[name] = options

        style = FakeStyle()
        configure_neon_stage_ttk(style, NEON_STAGE_PALETTE)
        for widget_style in (
            "TFrame", "TLabel", "TButton", "TCombobox", "TEntry",
            "Treeview", "Treeview.Heading", "TScrollbar",
        ):
            self.assertIn(widget_style, style.configured)
        self.assertEqual(style.configured["TFrame"]["background"], "#010B1C")
        self.assertEqual(style.configured["TLabel"]["foreground"], "#F3F7FF")
        self.assertEqual(style.configured["Treeview"]["fieldbackground"], "#000A1E")
        self.assertEqual(style.configured["Treeview.Heading"]["background"], "#06152E")
        self.assertIn("TButton", style.mapped)
        self.assertIn("Treeview", style.mapped)

    def test_real_neon_stage_art_assets_are_bundled(self) -> None:
        required = (
            resource_path("theme.json"),
            resource_path("assets", "hero.png"),
            resource_path("assets", "preview.png"),
            resource_path("svg", "bezel.svg"),
            resource_path("svg", "crest.svg"),
            resource_path("svg", "texture.svg"),
            resource_path("icons", "import_guitar.svg"),
            resource_path("icons", "settings.svg"),
            resource_path("icons", "skins.svg"),
        )
        for path in required:
            with self.subTest(path=str(path)):
                self.assertTrue(path.is_file(), f"Missing PPGU theme asset: {path}")


if __name__ == "__main__":
    unittest.main()
