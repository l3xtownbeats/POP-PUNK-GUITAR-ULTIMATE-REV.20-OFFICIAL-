"""Build relocatable PATTERN_MODE packages and validate before publication."""
from __future__ import annotations
import argparse,hashlib,json,re,shutil,tempfile
from pathlib import Path
from typing import Any
from pattern_clip_registry import load_pattern_clip_registry

def _sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(1048576),b""): h.update(block)
 return h.hexdigest().upper()

def _file(value:Any,field:str)->Path:
 if not isinstance(value,(str,Path)) or not str(value).strip(): raise ValueError(f"{field} must identify an existing file")
 p=Path(value).expanduser().resolve()
 if not p.is_file(): raise ValueError(f"{field} does not exist: {p}")
 return p

def add_pattern_clip_to_package(staging_record:dict[str,Any],package_root:Path,*,license_record:dict[str,Any],musical_review:dict[str,Any],mapping:dict[str,Any])->dict[str,Any]:
 """Copy source PCM, exact clip PCM and explicit approval evidence into a relocatable package."""
 if not isinstance(staging_record,dict): raise ValueError("staging_record must be an object")
 aid=staging_record.get("asset_id")
 if not isinstance(aid,str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,95}",aid): raise ValueError("asset_id must be a safe package identifier")
 if staging_record.get("kind")!="note_event": raise ValueError("PATTERN_MODE package accepts only note_event assets")
 targets=staging_record.get("engine_targets")
 if not isinstance(targets,list) or "PATTERN_MODE" not in targets: raise ValueError("engine_targets must include PATTERN_MODE")
 if not isinstance(mapping,dict): raise ValueError("mapping must be an explicit object")
 if not isinstance(license_record,dict): raise ValueError("license_record is required")
 if license_record.get("license_status") not in (None,"LICENSE_APPROVED"): raise ValueError("license_status must be LICENSE_APPROVED")
 if not isinstance(musical_review,dict) or musical_review.get("status")!="APPROVED": raise ValueError("explicit musical_review APPROVED is required")
 source=_file(staging_record.get("source_path"),"source_path")
 derived=_file(staging_record.get("derived_path"),"derived_path")
 evidence=_file(license_record.get("evidence_source_path"),"evidence_source_path")
 sh,dh=_sha(source),_sha(derived)
 if sh!=str(staging_record.get("source_sha256","")).upper(): raise ValueError("staging source SHA-256 mismatch")
 if dh!=str(staging_record.get("derived_sha256","")).upper(): raise ValueError("staging derived SHA-256 mismatch")
 root=Path(package_root).expanduser().resolve(); root.mkdir(parents=True,exist_ok=True); manifest=root/"pattern_clips.json"
 if manifest.exists():
  payload=json.loads(manifest.read_text(encoding="utf-8"))
  if not isinstance(payload,dict) or payload.get("schema_version")!=1 or not isinstance(payload.get("clips"),list): raise ValueError("Existing PATTERN registry has an unsupported structure")
 else: payload={"schema_version":1,"clips":[]}
 if any(isinstance(x,dict) and x.get("asset_id")==aid for x in payload["clips"]): raise ValueError(f"Duplicate asset_id in package: {aid}")
 sr=Path("sources")/f"{aid}.wav"; cr=Path("clips")/f"{aid}.wav"
 en=re.sub(r"[^A-Za-z0-9._-]","_",evidence.name)[:100] or "evidence.txt"; er=Path("licenses")/f"{aid}-{en}"
 dest=[root/sr,root/cr,root/er]
 # Never follow pre-existing directory symlinks outside the package root.
 for folder in (root/"sources",root/"clips",root/"licenses"):
  if folder.is_symlink(): raise ValueError(f"Package directory must not be a symlink: {folder}")
  folder.mkdir(parents=True,exist_ok=True)
  try: folder.resolve().relative_to(root)
  except ValueError as exc: raise ValueError(f"Package directory escapes package root: {folder}") from exc
 for p in dest:
  if p.exists() or p.is_symlink(): raise FileExistsError(f"Refusing to overwrite packaged asset: {p}")
  try: p.parent.resolve().relative_to(root)
  except ValueError as exc: raise ValueError(f"Package destination escapes package root: {p}") from exc
 copied=[]; tmp=None
 try:
  for original,target in zip((source,derived,evidence),dest): shutil.copyfile(original,target); copied.append(target)
  if _sha(dest[0])!=sh or _sha(dest[1])!=dh or _sha(dest[2])!=_sha(evidence): raise ValueError("Packaged file hash changed during copy")
  clip={"asset_id":aid,"kind":"note_event","engine_targets":sorted(set(targets)),"source_path":sr.as_posix(),"source_sha256":sh,
   "source_start_sample":staging_record.get("source_start_sample"),"source_end_sample":staging_record.get("source_end_sample"),
   "sample_rate":staging_record.get("sample_rate"),"frame_count":staging_record.get("frame_count"),
   "clip_path":cr.as_posix(),"derived_sha256":dh,"license_status":"LICENSE_APPROVED",
   "license":{"spdx_id":license_record.get("spdx_id"),"source_url":license_record.get("source_url"),"evidence_path":er.as_posix(),
    "reviewed_by":license_record.get("reviewed_by"),"reviewed_at_utc":license_record.get("reviewed_at_utc")},
   "musical_review":{"status":musical_review.get("status"),"reviewed_by":musical_review.get("reviewed_by"),
    "reviewed_at_utc":musical_review.get("reviewed_at_utc"),"boundary_basis":musical_review.get("boundary_basis")},
   "mapping":mapping,"provenance":{"extractor":staging_record.get("extractor"),"extractor_version":staging_record.get("extractor_version"),
    "source_start_seconds":staging_record.get("source_start_seconds"),"source_end_seconds":staging_record.get("source_end_seconds"),
    "staging_review_status":staging_record.get("review_status")}}
  payload["clips"].append(clip)
  fd,name=tempfile.mkstemp(prefix=".pattern_clips.",suffix=".json",dir=root); tmp=Path(name)
  with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f:
   json.dump(payload,f,ensure_ascii=False,indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
  validated=load_pattern_clip_registry(tmp)
  if not validated.ready: raise ValueError(f"Packaged PATTERN registry is not ready: {validated.status}")
  os.replace(tmp,manifest); tmp=None
  return {"manifest_path":str(manifest),"asset_id":aid,"registry_status":validated.status,"mapping_count":len(validated.mappings),
   "source_path":sr.as_posix(),"clip_path":cr.as_posix(),"license_evidence_path":er.as_posix(),"source_sha256":sh,"derived_sha256":dh}
 except Exception:
  if tmp is not None: tmp.unlink(missing_ok=True)
  for p in reversed(copied): p.unlink(missing_ok=True)
  raise

def _read_json_object(path:Path,field:str)->dict[str,Any]:
 data=json.loads(Path(path).read_text(encoding="utf-8"))
 if not isinstance(data,dict): raise ValueError(f"{field} JSON root must be an object")
 return data

def main()->int:
 parser=argparse.ArgumentParser(description="Package a reviewed PATTERN_MODE note-event WAV clip.")
 parser.add_argument("--staging-record",type=Path,required=True,help="Extractor sidecar JSON")
 parser.add_argument("--package-root",type=Path,required=True,help="Destination library package directory")
 parser.add_argument("--license-approval",type=Path,required=True,help="Human-reviewed license approval JSON")
 parser.add_argument("--musical-review",type=Path,required=True,help="Human musical approval JSON")
 parser.add_argument("--mapping",type=Path,required=True,help="Explicit MIDI/articulation/velocity mapping JSON")
 args=parser.parse_args()
 result=add_pattern_clip_to_package(
  _read_json_object(args.staging_record,"staging record"),args.package_root,
  license_record=_read_json_object(args.license_approval,"license approval"),
  musical_review=_read_json_object(args.musical_review,"musical review"),
  mapping=_read_json_object(args.mapping,"mapping"))
 print(json.dumps(result,ensure_ascii=False,indent=2))
 return 0

if __name__=="__main__":
 raise SystemExit(main())
