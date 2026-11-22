#!/usr/bin/env python3
"""Generate the original SIGNALS SKIN 001 raster artwork. Requires Pillow and NumPy."""
from pathlib import Path
import math, hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
W, H = 1920, 1080
for folder in ("assets/background", "assets/controls", "assets/fx_layers",
               "assets/spritesheets", "assets/textures", "assets/hero"):
    (ROOT / folder).mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(1001)
y, x = np.mgrid[0:H, 0:W]
rad = np.sqrt(((x-W*.5)/(W*.72))**2 + ((y-H*.42)/(H*.8))**2)
v = np.clip(1-rad*.55, .28, 1)
base = np.zeros((H, W, 3), np.float32)
for c, b in enumerate((6, 10, 16)):
    base[:, :, c] = b + (7, 13, 20)[c] * v
noise = rng.normal(0, 1.35, (H, W))
brush = rng.normal(0, .55, (H, 1))
for c, scale in enumerate((1, 1.15, 1.35)):
    base[:, :, c] += noise*scale + brush
for px, py, sx, sy, amp, col in (
    (W*.18,H*.18,W*.28,H*.35,10,(0,75,105)),
    (W*.83,H*.20,W*.25,H*.33,9,(10,48,112)),
    (W*.5,H*.92,W*.5,H*.18,5,(0,50,70))
):
    g = np.exp(-(((x-px)/sx)**2 + ((y-py)/sy)**2)*2)*amp
    for c in range(3):
        base[:, :, c] += g*col[c]/100
bg = Image.fromarray(np.uint8(np.clip(base,0,255))).convert("RGBA")
overlay = Image.new("RGBA", (W,H))
d = ImageDraw.Draw(overlay)
for yy in range(70,H,90):
    d.line((70,yy,W-70,yy), fill=(80,130,155,13))
for xx in range(70,W,120):
    d.line((xx,60,xx,H-60), fill=(80,130,155,9))
d.rounded_rectangle((34,34,W-34,H-34),28,outline=(95,143,166,90),width=2)
d.rounded_rectangle((43,43,W-43,H-43),24,outline=(3,8,14,220),width=7)
Image.alpha_composite(bg,overlay).save(ROOT/"assets/background/main.png", optimize=True)

def texture(size, rgb, seed, alpha=255):
    r = np.random.default_rng(seed)
    tile = 256
    a = np.zeros((tile,tile,4), np.uint8)
    n = r.normal(0,1.3,(tile,tile))
    rows = r.normal(0,.7,(tile,1))
    for c,b in enumerate(rgb):
        a[:,:,c] = np.uint8(np.clip(b+n+rows,0,255))
    a[:,:,3] = alpha
    t = Image.fromarray(a,"RGBA")
    out = Image.new("RGBA",(size,size))
    for yy in range(0,size,tile):
        for xx in range(0,size,tile):
            out.paste(t,(xx,yy))
    return out

texture(4096,(20,29,39),1001).save(ROOT/"assets/textures/graphite_brushed_4k.png", optimize=True)
texture(2048,(12,23,34),2001,180).save(ROOT/"assets/textures/smoked_glass_2k.png", optimize=True)

def glow(name, color, centers, blur):
    im = Image.new("RGBA",(W,H))
    dr = ImageDraw.Draw(im)
    for px,py,rx,ry,a in centers:
        dr.ellipse((px-rx,py-ry,px+rx,py+ry),fill=(*color,a))
    im.filter(ImageFilter.GaussianBlur(blur)).save(ROOT/"assets/fx_layers"/name,optimize=True)

glow("cyan_bloom.png",(0,210,245),[(250,170,260,95,90),(960,40,400,70,35),(1700,850,280,80,65)],58)
glow("blue_bloom.png",(45,100,255),[(1660,190,260,100,90),(950,1030,420,45,50)],62)
glow("edge_reflection.png",(120,210,230),[(960,60,850,5,90),(960,1020,850,4,75),(48,540,4,390,65),(1872,540,4,390,65)],8)

def knob(i):
    im = Image.new("RGBA",(256,256))
    d = ImageDraw.Draw(im)
    d.ellipse((27,27,229,229),fill=(0,0,0,130))
    d.ellipse((22,18,226,222),fill=(15,26,37),outline=(80,112,130),width=5)
    d.ellipse((34,30,214,210),fill=(29,44,58),outline=(4,10,17),width=6)
    d.arc((40,36,208,204),135,405,fill=(45,220,240,220 if i in (1,2) else 110),width=5)
    a = math.radians((-135,-45,45,135)[i])
    px, py = 128+math.cos(a)*70, 120+math.sin(a)*70
    d.line((128,120,px,py),fill=(220,247,255),width=5)
    d.ellipse((112,104,144,136),fill=(66,91,108),outline=(145,183,198),width=2)
    d.ellipse((8,8,240,240),outline=((80,120,140,120),(55,230,242,180),(68,140,255,210),(255,85,120,210))[i],width=3)
    return im

atlas = Image.new("RGBA",(1024,256))
for i in range(4):
    atlas.alpha_composite(knob(i),(i*256,0))
atlas.save(ROOT/"assets/spritesheets/knob_states_4x1.png",optimize=True)
for i,name in enumerate(("knob_default.png","knob_hover.png","knob_active.png","knob_disabled.png")):
    knob(i).save(ROOT/"assets/controls"/name,optimize=True)

buttons = Image.new("RGBA",(1024,128))
for i in range(4):
    im = Image.new("RGBA",(256,128))
    d = ImageDraw.Draw(im)
    fills = ((17,29,42),(17,65,78),(19,52,94),(60,25,42))
    edges = ((75,105,124),(55,225,239),(75,150,255),(255,85,120))
    d.rounded_rectangle((10,10,246,118),18,fill=fills[i],outline=edges[i],width=3)
    d.line((28,18,228,18),fill=(180,220,235,55),width=2)
    buttons.alpha_composite(im,(i*256,0))
buttons.save(ROOT/"assets/spritesheets/button_states_4x1.png",optimize=True)

hero = Image.new("RGBA",(1600,900))
haze = Image.new("RGBA",hero.size)
ImageDraw.Draw(haze).ellipse((120,120,1450,820),fill=(0,130,170,42))
hero = Image.alpha_composite(hero,haze.filter(ImageFilter.GaussianBlur(100)))
d = ImageDraw.Draw(hero)
d.line((940,140,620,530),fill=(8,15,23),width=74)
d.line((940,140,620,530),fill=(56,82,99),width=8)
d.ellipse((330,430,850,830),fill=(9,18,28),outline=(68,220,235,230),width=8)
d.ellipse((455,510,720,770),fill=(15,29,42),outline=(88,120,140,255),width=5)
d.polygon([(650,540),(770,590),(720,690),(610,650)],fill=(11,19,29),outline=(88,130,150))
for off in (-12,-6,0,6,12):
    d.line((940+off,140,600+off,760),fill=(155,205,220,135),width=2)
for yy in (570,680):
    d.rounded_rectangle((500,yy,700,yy+22),7,fill=(4,9,15),outline=(90,140,160,190),width=2)
hero.save(ROOT/"assets/hero/signals_stage_hero.png",optimize=True)
Image.open(ROOT/"assets/background/main.png").resize((720,405),Image.Resampling.LANCZOS).save(ROOT/"assets/preview.png",optimize=True)

assets = []
for p in sorted((ROOT/"assets").rglob("*.png")):
    im = Image.open(p)
    assets.append({
        "path":p.relative_to(ROOT).as_posix(),"width":im.width,"height":im.height,
        "format":im.format,"mode":im.mode,
        "sha256":hashlib.sha256(p.read_bytes()).hexdigest()
    })
manifest = {
    "schema_version":1,"skin":"SIGNALS","skin_number":"001",
    "base_reference":"NEON STAGE DEFAULT / SKIN-1",
    "asset_policy":"Original artwork; no third-party brand or artist imagery.",
    "spritesheets":[
        {"path":"assets/spritesheets/knob_states_4x1.png","frame_width":256,"frame_height":256,"columns":4,"rows":1,"states":["default","hover","active","disabled"]},
        {"path":"assets/spritesheets/button_states_4x1.png","frame_width":256,"frame_height":128,"columns":4,"rows":1,"states":["default","hover","active","disabled"]}
    ],
    "assets":assets
}
(ROOT/"assets/artwork_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(f"Generated {len(assets)} PNG assets under {ROOT}")
