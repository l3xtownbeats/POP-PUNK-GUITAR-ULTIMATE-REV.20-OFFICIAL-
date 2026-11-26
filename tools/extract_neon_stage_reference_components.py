#!/usr/bin/env python3
"""Extract source-faithful NEON STAGE reference crops for review and component mapping.

1x preserves the original source pixels. 2x is an LANCZOS resample, not native
2x artwork. Some crops include baked labels/scales; see the JSON manifest.
This package is a visual reference aid and is not automatically JUCE-runtime-ready.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, zipfile
from pathlib import Path
from PIL import Image, ImageDraw

BUTTON_SOURCE = "Meshy_AI_neon_stage_buttons_and_switches.png"
KNOB_SOURCE = "Meshy_AI_neon_stage_knobs_and_meters (1).png"
CROPS = []

def add(asset, source, box, description, baked=False):
    CROPS.append({"asset_id": asset, "source": source, "box": box,
                  "description": description, "baked_text_or_scale": baked})

# FX chain card states.
for state, box in [
    ("normal",(20,35,310,220)),("hover",(310,35,610,220)),
    ("pressed",(610,35,910,220)),("active",(910,35,1210,220)),
    ("disabled",(1210,35,1520,220)),
]:
    add(f"buttons/fx_compressor_{state}",BUTTON_SOURCE,box,
        f"FX chain / Compressor / {state}",True)

# Selector and rhythm buttons, normal and active states.
for family,names,y0,y1 in [
    ("selector",["major","minor","custom"],294,378),
    ("rhythm",["strum","arp","latch"],398,482),
]:
    for name,(x0,x1) in zip(names,[(30,270),(280,520),(525,765)]):
        add(f"buttons/{family}_{name}_normal",BUTTON_SOURCE,(x0,y0,x1,y1),
            f"{family} / {name} / normal",True)
    for name,(x0,x1) in zip(names,[(770,1015),(1015,1265),(1265,1520)]):
        add(f"buttons/{family}_{name}_active",BUTTON_SOURCE,(x0,y0,x1,y1),
            f"{family} / {name} / active",True)

# Main modes and the Punk Group reference pair (not a REV.20 main mode).
for name,normal,active in [
    ("melody",(20,518,270,605),(265,518,520,605)),
    ("pattern",(515,518,775,605),(765,518,1025,605)),
    ("punk_group_reference",(1020,518,1278,605),(1265,518,1528,605)),
]:
    add(f"buttons/mode_{name}_normal",BUTTON_SOURCE,normal,
        f"mode / {name} / normal",True)
    add(f"buttons/mode_{name}_active",BUTTON_SOURCE,active,
        f"mode / {name} / active",True)

# Toggles, actions and status LEDs.
for asset,box,description in [
    ("switches/toggle_on",(20,690,260,775),"toggle / ON"),
    ("switches/toggle_off",(260,690,510,775),"toggle / OFF"),
    ("buttons/action_apply_all",(510,690,790,775),"action / Apply All"),
    ("buttons/action_load_library",(790,690,1070,775),"action / Load Library"),
    ("leds/status_on_green",(1090,690,1205,777),"LED / green ON"),
    ("leds/status_error_red",(1205,690,1310,777),"LED / red ERROR"),
    ("leds/status_active_cyan",(1310,690,1415,777),"LED / cyan ACTIVE"),
    ("leds/status_off_gray",(1415,690,1525,777),"LED / gray OFF"),
]:
    add(asset,BUTTON_SOURCE,box,description,True)

# Large rotary poses and four small amp-style rotary examples.
for name,box in [
    ("00_percent",(5,35,185,212)),("25_percent",(180,35,365,212)),
    ("50_percent",(355,35,540,212)),("75_percent",(530,35,720,212)),
    ("100_percent",(705,35,900,212)),
]:
    add(f"knobs/rotary_{name}",KNOB_SOURCE,box,
        f"rotary knob / {name.replace('_',' ')} pose")
for name,box in [
    ("gain",(930,78,1075,225)),("bass",(1075,78,1225,225)),
    ("middle",(1225,78,1375,225)),("treble",(1375,78,1528,225)),
]:
    add(f"knobs/mini_amp_{name}",KNOB_SOURCE,box,
        f"mini amp knob / {name}; fixed label and scale included",True)

# Horizontal sliders and standalone thumb variants.
for name,box in [
    ("idle",(15,315,545,405)),("low",(15,405,545,500)),
    ("mid",(15,500,545,595)),("high",(15,595,545,695)),
    ("max",(15,695,545,800)),
]:
    add(f"sliders/horizontal_{name}",KNOB_SOURCE,box,
        f"horizontal slider / {name} example")
for name,box in [
    ("ring",(550,315,645,405)),("disc",(645,315,735,405)),
    ("knurled",(735,315,820,405)),("vertical",(820,315,910,405)),
    ("rail_capsule",(910,315,1030,405)),
]:
    add(f"sliders/thumb_{name}",KNOB_SOURCE,box,f"slider thumb / {name}")

# Vertical meters, horizontal progress bars, and individual meter segments.
add("meters/vertical_gain_reduction",KNOB_SOURCE,(620,448,780,855),
    "vertical gain-reduction meter / fixed scale labels included",True)
add("meters/vertical_output_level",KNOB_SOURCE,(830,448,1000,855),
    "vertical output meter / fixed scale labels included",True)
for name,box in [
    ("striped",(1060,315,1528,382)),("filled",(1060,382,1528,445)),
    ("segmented",(1060,445,1528,508)),("ticks",(1060,508,1528,575)),
    ("short_fill",(1060,575,1528,645)),
]:
    add(f"meters/horizontal_progress_{name}",KNOB_SOURCE,box,
        f"horizontal progress / {name}")
add("meters/level_meter_segments_multicolor",KNOB_SOURCE,(1065,710,1525,815),
    "multicolor level meter segments")
SEGMENTS=[
    (1077,728,20,56),(1114,728,21,63),(1149,727,22,66),(1184,727,23,67),
    (1224,728,21,64),(1259,728,22,64),(1295,728,22,64),(1331,728,21,64),
    (1368,728,23,65),(1403,727,22,66),(1438,727,22,66),(1473,728,23,65),
]
for index,(x,y,w,h) in enumerate(SEGMENTS,1):
    add(f"meters/segments/segment_{index:02d}",KNOB_SOURCE,
        (x-4,y-5,x+w+4,y+h+5),f"individual level segment {index:02d}")

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--buttons",type=Path,required=True)
    parser.add_argument("--knobs",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    sources={BUTTON_SOURCE:args.buttons,KNOB_SOURCE:args.knobs}
    for p in sources.values():
        if not p.is_file(): raise SystemExit(f"Missing source reference: {p}")
        with Image.open(p) as im: im.verify()
    out=args.output
    if out.exists(): shutil.rmtree(out)
    one,two=out/"reference_components_1x",out/"reference_components_2x"
    one.mkdir(parents=True); two.mkdir(parents=True)
    source_manifest={}
    for name,p in sources.items():
        with Image.open(p) as im:
            source_manifest[name]={"width":im.width,"height":im.height,"mode":im.mode,
                "bytes":p.stat().st_size,"sha256":digest(p)}
    records=[]; tiles=[]
    for crop in CROPS:
        with Image.open(sources[crop["source"]]) as im:
            im=im.convert("RGBA")
            x0,y0,x1,y1=crop["box"]
            if not (0<=x0<x1<=im.width and 0<=y0<y1<=im.height):
                raise SystemExit(f"Crop outside source: {crop['asset_id']} {crop['box']} {im.size}")
            native=im.crop(crop["box"])
        if native.getchannel("A").getbbox() is None:
            raise SystemExit(f"Fully transparent crop: {crop['asset_id']}")
        for scale,destination in ((1,one),(2,two)):
            result=native if scale==1 else native.resize(
                (native.width*2,native.height*2),Image.Resampling.LANCZOS)
            path=destination/(crop["asset_id"]+".png")
            path.parent.mkdir(parents=True,exist_ok=True)
            result.save(path,optimize=True)
            records.append({
                "asset_id":crop["asset_id"],"file":f"{destination.name}/{crop['asset_id']}.png",
                "source_reference":crop["source"],"crop_xyxy":crop["box"],"scale":scale,
                "width":result.width,"height":result.height,
                "description":crop["description"],
                "baked_text_or_scale":crop["baked_text_or_scale"],
                "source_native_1x":scale==1,"bytes":path.stat().st_size,
                "sha256":digest(path),
                "validation_status":"REFERENCE_CROP_REVIEW_ONLY_NOT_RUNTIME_APPROVED"})
        thumb=native.copy(); thumb.thumbnail((260,180),Image.Resampling.LANCZOS)
        tile=Image.new("RGBA",(280,218),(7,12,22,255))
        tile.alpha_composite(thumb,((280-thumb.width)//2,5))
        draw=ImageDraw.Draw(tile)
        draw.text((7,190),crop["asset_id"],fill=(220,245,255,255))
        if crop["baked_text_or_scale"]:
            draw.text((7,204),"BAKED LABEL / SCALE",fill=(255,190,85,255))
        tiles.append(tile.convert("RGB"))
    columns=4; rows=(len(tiles)+columns-1)//columns
    contact=Image.new("RGB",(columns*280,rows*218),(7,12,22))
    for i,tile in enumerate(tiles): contact.paste(tile,((i%columns)*280,(i//columns)*218))
    contact_path=out/"PPGU_REFERENCE_COMPONENTS_CONTACT_SHEET.jpg"
    contact.save(contact_path,quality=93,optimize=True)
    manifest={
        "schema":"ppgu.reference-component-crops/2",
        "theme":"SKIN-1 / NEON STAGE DEFAULT / skin-053",
        "purpose":"Source-faithful 1x crops from the provided button/switch and knob/meter reference sheets; 2x copies are resampled for review.",
        "important_limitations":[
            "These crops are not automatically approved for JUCE runtime registration.",
            "Crops marked baked_text_or_scale contain fixed text, labels or scale marks in the source artwork.",
            "2x files are LANCZOS resamples of 1x pixels and do not contain additional source detail.",
            "Dynamic values, labels, note states and meters must be rendered live by JUCE where required."
        ],
        "source_sheets":source_manifest,"unique_crop_count":len(CROPS),
        "file_count_all_scales":len(records),"contact_sheet":contact_path.name,"records":records}
    manifest_path=out/"PPGU_REFERENCE_COMPONENT_CROP_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    (out/"README_RU.txt").write_text(
        "PPGU REV.20 — референсные компоненты NEON STAGE\n\n"
        "Каталог содержит отдельные вырезки из исходных листов кнопок/переключателей и кнобов/слайдеров/метров.\n"
        "reference_components_1x — исходные пиксели без масштабирования. reference_components_2x — LANCZOS-увеличение тех же изображений, не нативная 2x-детализация.\n\n"
        "Вырезки сохраняют рисунок исходника, включая свечение и прозрачность. Часть элементов содержит запечённые надписи или шкалы; отметки есть в JSON-манифесте.\n"
        "Пакет предназначен для визуальной сверки и подготовки runtime-слоёв. Не подключать к JUCE автоматически без отдельной проверки границ, alpha, динамического текста, hit regions, состояний и REV.20 bindings.\n",
        encoding="utf-8")
    zip_path=out/"PPGU-NEON-STAGE-REFERENCE-COMPONENTS.zip"
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for p in out.rglob("*"):
            if p.is_file() and p!=zip_path: archive.write(p,p.relative_to(out))
    print(f"PASS: {len(CROPS)} unique reference crops; {len(records)} PNG files at 1x/2x.")
    print(f"Contact sheet: {contact_path}")
    print(f"Manifest: {manifest_path}")
    print(f"ZIP: {zip_path} ({zip_path.stat().st_size} bytes; SHA-256 {digest(zip_path)})")
    return 0

if __name__=="__main__": raise SystemExit(main())
