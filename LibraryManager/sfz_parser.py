"""Conservative SFZ parser for library auditing; read-only, no source mutation."""
from __future__ import annotations
import re
from pathlib import Path

TAG_RE = re.compile(r"<\s*([A-Za-z_][A-Za-z0-9_]*)\s*>")
OP_RE = re.compile(r"""([A-Za-z][A-Za-z0-9_]*)\s*=\s*("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|[^\s]+)""")
INCLUDE_RE = re.compile(r"""^\s*#include\s+["']([^"']+)["']""", re.I)
DEFINE_RE = re.compile(r"""^\s*#define\s+(\S+)\s+(.+?)\s*$""", re.I)

def _clean_line(line: str) -> str:
    out=[]; quote=None; escaped=False; i=0
    while i < len(line):
        c=line[i]
        if quote:
            out.append(c)
            if escaped: escaped=False
            elif c=="\\": escaped=True
            elif c==quote: quote=None
            i+=1; continue
        if c in "\"'": quote=c; out.append(c); i+=1; continue
        if line.startswith("//",i): break
        out.append(c); i+=1
    return "".join(out)

def _unquote(value: str) -> str:
    value=value.strip()
    if len(value)>=2 and value[0]==value[-1] and value[0] in "\"'":
        return value[1:-1].replace(r'\"','"').replace(r"\'","'")
    return value

def _int(opcodes: dict, key: str):
    try: return int(float(opcodes[key]))
    except (KeyError,TypeError,ValueError): return None

def parse_sfz_file(sfz_path: Path, library_root: Path) -> list[dict]:
    sfz_path=sfz_path.resolve(); library_root=library_root.resolve()
    rows=[]; defines={}; region_counter=0

    def parse_file(path: Path, inherited: dict, inherited_default: str, stack: tuple):
        nonlocal region_counter
        path=path.resolve()
        if path in stack:
            rows.append({"sfz_file":str(sfz_path),"source_sfz":str(path),"region":"",
                         "sample_opcode":"","resolved_sample":"","status":"INCLUDE_CYCLE"})
            return
        if not path.is_file():
            rows.append({"sfz_file":str(sfz_path),"source_sfz":str(path),"region":"",
                         "sample_opcode":"","resolved_sample":"","status":"INCLUDE_MISSING"})
            return
        try: lines=path.read_text(encoding="utf-8-sig",errors="replace").splitlines()
        except OSError as exc:
            rows.append({"sfz_file":str(sfz_path),"source_sfz":str(path),"region":"",
                         "sample_opcode":"","resolved_sample":"",
                         "status":"SFZ_READ_ERROR:"+type(exc).__name__})
            return
        scopes={"global":{},"master":{},"group":{},"region":{}}
        active=None; local_default=inherited_default; pending=""

        def emit_region():
            nonlocal region_counter
            region=scopes["region"]
            if not region.get("sample"): return
            merged={**inherited,**scopes["global"],**scopes["master"],
                    **scopes["group"],**region}
            sample=merged["sample"]
            base=(path.parent / local_default.replace("\\","/")) if local_default else path.parent
            candidate=(base / sample.replace("\\","/")).resolve()
            try: candidate.relative_to(library_root); inside=True
            except ValueError: inside=False
            region_counter+=1
            lo_key,hi_key=_int(merged,"lokey"),_int(merged,"hikey")
            lo_vel,hi_vel=_int(merged,"lovel"),_int(merged,"hivel")
            rows.append({
                "sfz_file":str(sfz_path),"source_sfz":str(path),"region":region_counter,
                "sample_opcode":sample,"resolved_sample":str(candidate),
                "status":"FOUND" if candidate.is_file() else ("OUTSIDE_LIBRARY" if not inside else "MISSING"),
                "lokey":lo_key if lo_key is not None else (hi_key if hi_key is not None else ""),
                "hikey":hi_key if hi_key is not None else (lo_key if lo_key is not None else ""),
                "lovel":lo_vel if lo_vel is not None else (hi_vel if hi_vel is not None else ""),
                "hivel":hi_vel if hi_vel is not None else (lo_vel if lo_vel is not None else ""),
                "key_range_source":"SFZ" if lo_key is not None or hi_key is not None else "UNSPECIFIED",
                "velocity_range_source":"SFZ" if lo_vel is not None or hi_vel is not None else "UNSPECIFIED",
                "group_label":scopes["group"].get("group_label",""),
                "seq_position":merged.get("seq_position",""),
                "trigger":merged.get("trigger",""),
                "loop_mode":merged.get("loop_mode",""),
                "pitch_keycenter":merged.get("pitch_keycenter",""),
            })
            scopes["region"]={}

        for raw in lines:
            line=_clean_line(raw).strip()
            if not line: continue
            inc=INCLUDE_RE.match(line)
            if inc:
                target=(path.parent / inc.group(1).replace("\\","/")).resolve()
                parent={**inherited,**scopes["global"],**scopes["master"],**scopes["group"]}
                parse_file(target,parent,local_default,stack+(path,))
                continue
            dm=DEFINE_RE.match(line)
            if dm: defines[dm.group(1)]=dm.group(2).strip(); continue
            line=re.sub(r'\$[A-Za-z_][A-Za-z0-9_]*',
                        lambda m:defines.get(m.group(0),m.group(0)),line)
            pending += " " + line
            while True:
                tm=TAG_RE.search(pending)
                if not tm: break
                before=pending[:tm.start()].strip()
                if active and before:
                    scopes[active].update({k.lower():_unquote(v) for k,v in OP_RE.findall(before)})
                tag=tm.group(1).lower()
                if tag=="region":
                    emit_region(); scopes["region"]={}
                elif tag=="group":
                    emit_region(); scopes["group"]={}; scopes["region"]={}
                active=tag if tag in scopes or tag=="control" else None
                pending=pending[tm.end():]
            if active:
                ops={k.lower():_unquote(v) for k,v in OP_RE.findall(pending)}
                if active=="control":
                    if "default_path" in ops: local_default=ops["default_path"]
                else: scopes[active].update(ops)
            pending=""
        if active and pending.strip():
            scopes[active].update({k.lower():_unquote(v) for k,v in OP_RE.findall(pending)})
        emit_region()

    parse_file(sfz_path,{},"",())
    return rows
