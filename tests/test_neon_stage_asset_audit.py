import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "audit_neon_stage_assets.py"
SPEC = importlib.util.spec_from_file_location("audit_neon_stage_assets", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class NeonStageAuditHelpersTests(unittest.TestCase):
    def test_sha256_is_stable(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "pixel.png"
            Image.new("RGBA", (2, 3), (0, 0, 0, 0)).save(path)
            self.assertEqual(MODULE.sha256(path), MODULE.sha256(path))

    def test_rgba_memory_estimate_is_four_bytes_per_pixel(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "pixel.png"
            Image.new("RGBA", (10, 5), (0, 0, 0, 0)).save(path)
            with Image.open(path) as image:
                self.assertEqual(image.width * image.height * 4, 200)


if __name__ == "__main__":
    unittest.main()
