#!/usr/bin/env python3
"""Structural contract tests for NEON STAGE DEFAULT / Skin-1."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIN = ROOT / "SKIN" / "Skin_053"
CONTROL_MANIFEST = SKIN / "assets" / "controls" / "control_states_manifest.json"
SPRITE_MANIFEST = SKIN / "assets" / "spritesheets" / "neon_stage_spritesheet_manifest.json"


class NeonStageContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controls = json.loads(CONTROL_MANIFEST.read_text(encoding="utf-8"))
        cls.sprites = json.loads(SPRITE_MANIFEST.read_text(encoding="utf-8"))

    def test_exact_control_inventory(self):
        ids = self.controls["controlIds"]
        self.assertEqual(len(ids), 27)
        self.assertEqual(len(set(ids)), 27)
        self.assertEqual(sum(x.startswith("knob") for x in ids), 9)
        self.assertEqual(sum(x.startswith("fx_switch") for x in ids), 7)

    def test_every_declared_control_state_has_one_existing_png_pair(self):
        states = self.controls["states"]
        records = self.controls["records"]
        self.assertEqual(set(states), {"default", "hover", "pressed", "disabled", "dragged"})
        self.assertEqual(len(records), len(self.controls["controlIds"]) * len(states))
        keys = [(r["controlId"], r["state"]) for r in records]
        self.assertEqual(len(keys), len(set(keys)))
        expected = {(cid, state) for cid in self.controls["controlIds"] for state in states}
        self.assertEqual(set(keys), expected)
        for record in records:
            for key in ("master", "runtime"):
                path = SKIN / record[key].replace("assets/", "assets/", 1)
                self.assertTrue(path.is_file(), f"Missing control PNG: {path}")
                self.assertEqual(path.suffix.lower(), ".png")

    def test_four_sprite_sheets_and_eight_rotary_frames(self):
        sheets = self.sprites["sheets"]
        self.assertEqual(len(sheets), 4)
        for name, spec in sheets.items():
            path = SKIN / "assets" / "spritesheets" / name
            self.assertTrue(path.is_file(), f"Missing sprite sheet: {name}")
            self.assertEqual(spec["resolution"], [1024, 1024])
        controls = sheets["neon_stage_controls_spritesheet.png"]["elements"]
        self.assertEqual(controls["knobs"]["frames"], 8)

    def test_seven_fx_switches_are_present_in_manifest(self):
        ids = set(self.controls["controlIds"])
        self.assertEqual({f"fx_switch{i:02d}" for i in range(1, 8)}, 
                         {x for x in ids if x.startswith("fx_switch")})

    def test_generator_and_atlas_manifest_use_graphite_cyan_blue_palette(self):
        generator = (ROOT / "tools" / "generate_neon_stage_spritesheets.py").read_text(encoding="utf-8").lower()
        manifest_text = SPRITE_MANIFEST.read_text(encoding="utf-8").lower()
        self.assertNotIn("magenta", generator)
        self.assertNotIn("#ff007f", generator)
        self.assertNotIn("magenta", manifest_text)
        self.assertNotIn("#ff007f", manifest_text)
        palette = self.sprites["base_palette"]
        self.assertEqual(palette["accent_blue"], "#0048FF")
        self.assertNotIn("accent_magenta", palette)


if __name__ == "__main__":
    unittest.main()
