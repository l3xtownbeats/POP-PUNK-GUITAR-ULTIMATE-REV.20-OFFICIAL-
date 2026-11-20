import tempfile
import unittest
from pathlib import Path
from sfz_parser import parse_sfz_file

class SfzParserTests(unittest.TestCase):
    def test_scope_inheritance_default_path_and_ranges(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"Samples").mkdir()
            (root/"Samples"/"C4.wav").write_bytes(b"fixture")
            sfz=root/"Samples"/"instrument.sfz"
            sfz.write_text('''<control> default_path="."
<global> lovel=1 hivel=127
<group> group_label="Clean"
<region> sample="C4.wav" lokey=60 hikey=60
''',encoding="utf-8")
            rows=parse_sfz_file(sfz,root/"Samples")
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["status"],"FOUND")
            self.assertEqual(rows[0]["lokey"],60)
            self.assertEqual(rows[0]["lovel"],1)
            self.assertEqual(rows[0]["group_label"],"Clean")

    def test_include_missing_and_cycle_are_reported(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"Samples"; root.mkdir()
            main=root/"main.sfz"; child=root/"child.sfz"
            main.write_text('#include "child.sfz"\n',encoding="utf-8")
            child.write_text('#include "main.sfz"\n',encoding="utf-8")
            rows=parse_sfz_file(main,root)
            self.assertTrue(any(r["status"]=="INCLUDE_CYCLE" for r in rows))

    def test_multiple_regions_keep_individual_ranges(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.wav").write_bytes(b"a")
            (root/"b.wav").write_bytes(b"b")
            sfz=root/"multi.sfz"
            sfz.write_text('<region> sample="a.wav" lokey=40 hikey=45\n<region> sample="b.wav" lokey=46 hikey=50\\n',encoding="utf-8")
            rows=parse_sfz_file(sfz,root)
            self.assertEqual(len(rows),2)
            self.assertEqual([r["sample_opcode"] for r in rows],["a.wav","b.wav"])
            self.assertEqual(rows[1]["lokey"],46)

    def test_missing_sample(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            sfz=root/"test.sfz"
            sfz.write_text('<region> sample="absent.wav" lovel=20 hivel=80\n',encoding="utf-8")
            rows=parse_sfz_file(sfz,root)
            self.assertEqual(rows[0]["status"],"MISSING")
            self.assertEqual(rows[0]["hivel"],80)

if __name__=="__main__":
    unittest.main()
