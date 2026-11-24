import hashlib,tempfile,unittest,wave
from pathlib import Path
from asset_pipeline import extract_reviewed_wav
from pattern_package_builder import add_pattern_clip_to_package
from pattern_clip_registry import load_pattern_clip_registry

class PatternPackageBuilderTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.source=self.root/"source.wav"
  with wave.open(str(self.source),"wb") as w:
   w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes(b"".join((i%200).to_bytes(2,"little") for i in range(128)))
  self.staging=extract_reviewed_wav(self.source,self.root/"staging",16,96,kind="note_event",engines=["PATTERN_MODE"])
  self.evidence=self.root/"CC0.txt"; self.evidence.write_text("Test CC0 evidence\n",encoding="utf-8")
  self.license={"license_status":"LICENSE_APPROVED","spdx_id":"CC0-1.0","source_url":"https://example.org/audio","evidence_source_path":str(self.evidence),"reviewed_by":"test reviewer","reviewed_at_utc":"2026-11-24T00:00:00Z"}
  self.review={"status":"APPROVED","reviewed_by":"test reviewer","reviewed_at_utc":"2026-11-24T00:00:00Z","boundary_basis":"human-auditioned exact sample range"}
  self.mapping={"trigger_midi_note":60,"source_midi_note":60,"articulation_id":"open","velocity_min":1,"velocity_max":127,"round_robin_group":"RR-1"}
 def tearDown(self): self.tmp.cleanup()
 def package(self,**kwargs):
  args={"license_record":self.license,"musical_review":self.review,"mapping":self.mapping}; args.update(kwargs)
  return add_pattern_clip_to_package(self.staging,self.root/"package",**args)
 def test_package_is_relocatable_and_validator_ready(self):
  result=self.package(); root=self.root/"package"
  self.assertEqual(result["registry_status"],"READY_VALIDATED")
  self.assertTrue(load_pattern_clip_registry(root/"pattern_clips.json").ready)
  import json
  record=json.loads((root/"pattern_clips.json").read_text())["clips"][0]
  for key in ("source_path","clip_path"):
   self.assertFalse(Path(record[key]).is_absolute()); self.assertTrue((root/record[key]).is_file())
  evidence=record["license"]["evidence_path"]; self.assertFalse(Path(evidence).is_absolute()); self.assertTrue((root/evidence).is_file())
  self.assertEqual(record["source_start_sample"],16); self.assertEqual(record["source_end_sample"],96)
 def test_missing_license_evidence_does_not_publish(self):
  bad=dict(self.license,evidence_source_path=str(self.root/"missing.txt"))
  with self.assertRaisesRegex(ValueError,"does not exist"): self.package(license_record=bad)
  self.assertFalse((self.root/"package"/"pattern_clips.json").exists())
 def test_unapproved_musical_review_is_rejected(self):
  bad=dict(self.review,status="NEEDS_MUSICAL_REVIEW")
  with self.assertRaisesRegex(ValueError,"musical_review APPROVED"): self.package(musical_review=bad)
  self.assertFalse((self.root/"package"/"pattern_clips.json").exists())
 def test_wrong_pcm_even_with_updated_hash_is_rejected(self):
  clip=Path(self.staging["derived_path"])
  with wave.open(str(clip),"wb") as w:
   w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes(b"\x01\x00"*80)
  self.staging["derived_sha256"]=hashlib.sha256(clip.read_bytes()).hexdigest().upper()
  with self.assertRaisesRegex(ValueError,"does not match declared source sample range"): self.package()
  self.assertFalse((self.root/"package"/"pattern_clips.json").exists())
if __name__=="__main__": unittest.main()
