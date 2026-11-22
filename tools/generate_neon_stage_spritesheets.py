#!/usr/bin/env python3
"""Generate the canonical NEON STAGE DEFAULT 1024x1024 sprite atlases.

The generated atlases are visual-only. They do not change APVTS IDs, DSP,
sampler, MIDI, preset data, control geometry, or the audio callback.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SKIN" / "Skin_053" / "assets" / "spritesheets"
OUT.mkdir(parents=True, exist_ok=True)
SIZE = (1024, 1024)
P = {
    "background": "#05070E",
    "metal_border": "#00D2FF",
    "glow_cyan": "#00E5FF",
    "glow_blue": "#0048FF",
    "accent_warning": "#FFB454",
    "metal": "#101622",
    "metal_light": "#1B2A3B",
    "text": "#FFFFFF",
    "dim": "#7A8C9E",
}
def rgba(value, alpha=255):
    value = value.lstrip("#")
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)
def font(size=12, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()
def label(draw, box, text, color=None, size=11, bold=True):
    x1,y1,x2,y2 = box
    ft = font(size,bold)
    bb = draw.textbbox((0,0), text, font=ft)
    draw.text((x1+(x2-x1-(bb[2]-bb[0]))/2, y1+(y2-y1-(bb[3]-bb[1]))/2-1),
              text, font=ft, fill=rgba(color or P["dim"]))
def add_glow(im, draw_fn, color, radius=7):
    layer = Image.new("RGBA", im.size, (0,0,0,0))
    draw_fn(ImageDraw.Draw(layer), rgba(color,220))
    return Image.alpha_composite(im, layer.filter(ImageFilter.GaussianBlur(radius)))
def save(im, name):
    path = OUT / name
    im.save(path, format="PNG", optimize=True)
    return path

manifest = {
  "schemaVersion":"1.0.0",
  "project":"NEON_STAGE_MANAGER_3_0",
  "theme":"NEON_STAGE_DEFAULT_SKIN_1",
  "canvas":[1024,1024],
  "base_palette":{
    "background":P["background"], "metal_border":P["metal_border"],
    "glow_cyan":P["glow_cyan"], "glow_blue":P["glow_blue"],
    "semantic_warning":P["accent_warning"]
  },
  "sheets":{}
}

# ---------------------------------------------------------------------------
# 1. Controls: 8 rotary frames, OFF/ON toggle, 4 button states.
# ---------------------------------------------------------------------------
im = Image.new("RGBA", SIZE, (0,0,0,0))
knob_frames=[]
def draw_knob(frame):
    tile=Image.new("RGBA",(100,100),(0,0,0,0))
    tile=add_glow(tile,lambda d,c:d.ellipse((8,8,92,92),outline=c,width=4),P["glow_blue"],7)
    d=ImageDraw.Draw(tile)
    d.ellipse((9,9,91,91),fill=rgba("#24364A"),outline=rgba("#B8C8D8"),width=3)
    d.ellipse((16,16,84,84),fill=rgba("#09121F"),outline=rgba(P["metal_border"]),width=2)
    d.ellipse((23,23,77,77),fill=rgba("#14263A"),outline=rgba("#60788E"),width=1)
    for a in range(-135,136,15):
        rad=math.radians(a)
        d.line((50+34*math.cos(rad),50+34*math.sin(rad),
                50+39*math.cos(rad),50+39*math.sin(rad)),fill=rgba(P["dim"]),width=1)
    angle=frame*45
    rad=math.radians(angle)
    d.line((50+7*math.cos(rad),50+7*math.sin(rad),
            50+29*math.cos(rad),50+29*math.sin(rad)),fill=rgba("#FFFFFF"),width=4)
    d.ellipse((44,44,56,56),fill=rgba(P["glow_cyan"]),outline=rgba("#FFFFFF"),width=1)
    return tile
knob_x=[65,175,285,395]
for row,y in enumerate([120,220]):
    for col,x in enumerate(knob_x):
        idx=row*4+col
        im.alpha_composite(draw_knob(idx),(x,y))
        knob_frames.append({"frame":idx,"angle_deg":idx*45,"bbox":[x,y,x+100,y+100]})
# Switch OFF and ON exact boxes.
toggle_boxes={"OFF":[65,430,465,600],"ON":[535,430,935,600]}
for state,box in toggle_boxes.items():
    x1,y1,x2,y2=box; is_on=state=="ON"
    glow=P["glow_cyan"] if is_on else P["glow_blue"]
    im=add_glow(im,lambda d,c:d.rounded_rectangle((x1+9,y1+36,x2-9,y2-36),radius=64,outline=c,width=7),glow,8)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((x1+9,y1+36,x2-9,y2-36),radius=64,fill=rgba("#07111E"),outline=rgba(P["metal_border"] if is_on else "#53677A"),width=3)
    # State text is supplied by the live JUCE button label, not baked into the atlas.
    cx=x2-105 if is_on else x1+105
    d.ellipse((cx-52,y1+33,cx+52,y1+137),fill=rgba("#263B50"),outline=rgba("#D7F7FF"),width=3)
    d.ellipse((cx-40,y1+45,cx+40,y1+125),fill=rgba(P["glow_cyan"] if is_on else "#586C80"),outline=rgba(P["metal_border"]),width=2)
    d.ellipse((cx-21,y1+64,cx+21,y1+106),fill=rgba("#EAFBFF" if is_on else "#26384A"))
# Button state bboxes exact as requested.
button_boxes={
 "normal":[25,690,250,815],
 "hover":[265,690,490,815],
 "pressed":[505,690,730,815],
 "active":[745,690,970,815],
}
for state,box in button_boxes.items():
    x1,y1,x2,y2=box
    if state in ("hover","active"):
        im=add_glow(im,lambda d,c:d.rounded_rectangle((x1+3,y1+3,x2-3,y2-3),radius=16,outline=c,width=5),P["glow_cyan"],7)
    d=ImageDraw.Draw(im)
    face="#07101C" if state=="pressed" else "#0E1C2C"
    edge=P["glow_cyan"] if state in ("hover","active") else (P["metal_border"] if state=="pressed" else "#536A80")
    d.rounded_rectangle((x1+3,y1+3,x2-3,y2-3),radius=14,fill=rgba(face),outline=rgba(edge),width=3)
    d.rounded_rectangle((x1+10,y1+10,x2-10,y2-10),radius=10,outline=rgba("#8AA7BD",130),width=1)
    label(d,box,state.upper(),P["text"],16)
save(im,"neon_stage_controls_spritesheet.png")
manifest["sheets"]["neon_stage_controls_spritesheet.png"]={
 "resolution":[1024,1024],
 "elements":{
  "knobs":{"type":"rotary","frames":8,"angle_step_deg":45,"size":[100,100],"row_y":[120,220],"frames_bbox":knob_frames},
  "toggle_switch":{"states":{k:{"bbox":v} for k,v in toggle_boxes.items()}},
  "buttons":{"states":{k:{"bbox":v} for k,v in button_boxes.items()}}
 }
}

# ---------------------------------------------------------------------------
# 2. Eight-segment VU meters, long/short sliders, round/square status LEDs.
# ---------------------------------------------------------------------------
im=Image.new("RGBA",SIZE,(0,0,0,0))
d=ImageDraw.Draw(im)
label(d,(30,2,970,22),"VERTICAL LED METERS / 8 SEGMENTS",P["text"],12)
meter_boxes=[]
for i in range(8):
    x=43+i*117; y=34; w=82; h=286
    im=add_glow(im,lambda dd,c:dd.rounded_rectangle((x,y,x+w,y+h),radius=7,outline=c,width=2),P["glow_blue"],4)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((x,y,x+w,y+h),radius=7,fill=rgba("#080F19"),outline=rgba(P["metal_border"]),width=2)
    active=i+1
    for seg in range(8):
        sy=y+h-20-(seg*31)
        col=P["glow_cyan"] if seg<5 else (P["glow_blue"] if seg<7 else P["accent_warning"])
        d.rounded_rectangle((x+17,sy,x+w-17,sy+18),radius=3,
                            fill=rgba(col,255 if seg<active else 30),
                            outline=rgba(col,100 if seg<active else 25),width=1)
    label(d,(x,y+4,x+w,y+23),f"CH {i+1}",P["dim"],8)
    meter_boxes.append({"meter":i+1,"bbox":[x,y,x+w,y+h],"segments":8,"active_segments":active})
label(d,(30,350,970,375),"HORIZONTAL SLIDERS / LONG + SHORT",P["text"],12)
slider_boxes={}
def slider(name,x,y,w):
    global im
    d=ImageDraw.Draw(im)
    d.text((x,y-24),name.upper(),font=font(9,True),fill=rgba(P["dim"]))
    d.rounded_rectangle((x,y,x+w,y+22),radius=9,fill=rgba("#07101B"),outline=rgba("#405A70"),width=2)
    slider_boxes[name]={"track_bbox":[x,y,x+w,y+22]}
slider("long_slider",60,445,820)
slider("short_slider",60,570,390)
# Reusable cyan thumb sprite; JUCE positions it dynamically at the live value.
thumb_box=[910,640,942,672]
im=add_glow(im,lambda dd,c:dd.ellipse(thumb_box,outline=c,width=4),P["glow_cyan"],6)
d=ImageDraw.Draw(im)
d.ellipse(thumb_box,fill=rgba("#19334A"),outline=rgba(P["glow_cyan"]),width=3)
slider_boxes["thumb"]={"bbox":thumb_box}
label(ImageDraw.Draw(im),(30,755,970,780),"STATUS LEDS / ROUND + SQUARE",P["text"],12)
led_states=["off","cyan","blue","warning"]
led_colors={"off":"#344354","cyan":P["glow_cyan"],"blue":P["glow_blue"],"warning":P["accent_warning"]}
led_boxes={"round":{},"square":{}}
for shape,x_start in (("round",50),("square",570)):
    for y in (810,920):
        row_key=str(y)
        led_boxes[shape][row_key]={}
        for i,state in enumerate(led_states):
            x=x_start+i*110
            col=led_colors[state]
            if state!="off":
                if shape=="round":
                    im=add_glow(im,lambda dd,c:dd.ellipse((x-10,y-10,x+50,y+50),outline=c,width=4),col,6)
                else:
                    im=add_glow(im,lambda dd,c:dd.rounded_rectangle((x-10,y-10,x+50,y+50),radius=8,outline=c,width=4),col,6)
            d=ImageDraw.Draw(im)
            if shape=="round":
                d.ellipse((x,y,x+40,y+40),fill=rgba(col),outline=rgba("#D7F7FF"),width=2)
            else:
                d.rounded_rectangle((x,y,x+40,y+40),radius=5,fill=rgba(col),outline=rgba("#D7F7FF"),width=2)
            led_boxes[shape][row_key][state]={"bbox":[x,y,x+40,y+40]}
            d.text((x-5,y+46),state.upper(),font=font(8,True),fill=rgba(P["dim"]))
save(im,"neon_stage_meters_sliders_sheet.png")
manifest["sheets"]["neon_stage_meters_sliders_sheet.png"]={
 "resolution":[1024,1024],
 "elements":{
  "vu_meters":{"type":"vertical_led","levels_count":8,"bbox_area":[30,25,970,350],"instances":meter_boxes},
  "sliders":{"types":["long_slider","short_slider"],"bbox_area":[30,380,970,760],"instances":slider_boxes},
  "status_leds":{"round":{"states":led_states,"row_y":[810,920],"instances":led_boxes["round"]},
                 "square":{"states":led_states,"row_y":[810,920],"instances":led_boxes["square"]}}
 }
}

# ---------------------------------------------------------------------------
# 3. Reusable panel frame components and display grid.
# ---------------------------------------------------------------------------
im=Image.new("RGBA",SIZE,(0,0,0,0)); d=ImageDraw.Draw(im)
label(d,(25,18,500,42),"9-SLICE CORNERS",P["text"],13)
corners={}
for name,x,y in (("top_left",30,60),("top_right",160,60),("bottom_left",290,60),("bottom_right",420,60)):
    box=[x,y,x+92,y+92]
    d.rounded_rectangle(box,radius=12,fill=rgba(P["metal"]),outline=rgba(P["metal_border"]),width=3)
    if "left" in name: d.line((x+8,y+8,x+8,y+84),fill=rgba(P["glow_cyan"]),width=3)
    else: d.line((x+84,y+8,x+84,y+84),fill=rgba(P["glow_cyan"]),width=3)
    d.ellipse((x+15,y+15,x+25,y+25),fill=rgba(P["dim"]))
    d.text((x,y+98),name,font=font(8),fill=rgba(P["dim"]))
    corners[name]={"bbox":box}
label(d,(30,190,450,215),"BORDERS",P["text"],13)
borders={}
for name,box in {
 "top_border":[30,230,470,252],"bottom_border":[30,270,470,292],
 "left_border":[510,220,532,400],"right_border":[570,220,592,400]
}.items():
    d.rounded_rectangle(box,radius=4,fill=rgba(P["metal"]),outline=rgba(P["metal_border"]),width=2)
    if box[2]-box[0] > box[3]-box[1]:
        d.line((box[0]+8,(box[1]+box[3])//2,box[2]-8,(box[1]+box[3])//2),fill=rgba(P["glow_cyan"]),width=2)
    else:
        d.line(((box[0]+box[2])//2,box[1]+8,(box[0]+box[2])//2,box[3]-8),fill=rgba(P["glow_cyan"]),width=2)
    borders[name]={"bbox":box}
label(d,(30,425,450,450),"DIVIDERS",P["text"],13)
dividers={}
for name,box,width in [
 ("horizontal_thin",[30,470,450,474],2),("horizontal_thick",[30,510,450,518],5),
 ("vertical_thin",[500,460,504,560],2),("vertical_thick",[550,460,558,560],5)
]:
    d.rounded_rectangle(box,radius=2,fill=rgba(P["metal_border"]))
    dividers[name]={"bbox":box,"stroke_px":width}
label(d,(30,610,970,635),"HEADER BARS",P["text"],13)
headers={}
for name,box in (("standard_header",[30,650,480,710]),("compact_header",[520,650,970,700])):
    im=add_glow(im,lambda dd,c,b=box:dd.rounded_rectangle(b,radius=7,outline=c,width=3),P["glow_blue"],5)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle(box,radius=7,fill=rgba(P["metal"]),outline=rgba(P["metal_border"]),width=2)
    # Header text is drawn live by the JUCE component using its current section title.
    headers[name]={"bbox":box}
label(ImageDraw.Draw(im),(30,745,970,775),"DISPLAY BACKGROUND / DARK TRANSLUCENT CYAN GRID",P["text"],12)
display=[30,785,970,990]
d=ImageDraw.Draw(im)
d.rounded_rectangle(display,radius=8,fill=rgba("#071321",225),outline=rgba(P["metal_border"]),width=2)
for x in range(50,970,40): d.line((x,795,x,980),fill=rgba(P["glow_cyan"],40),width=1)
for y in range(805,990,25): d.line((40,y,960,y),fill=rgba(P["glow_cyan"],40),width=1)
save(im,"neon_stage_frames_panels_sheet.png")
manifest["sheets"]["neon_stage_frames_panels_sheet.png"]={
 "resolution":[1024,1024],
 "elements":{
  "9_slice_corners":corners,"borders":borders,"dividers":dividers,
  "header_bars":headers,"display_bg":{"bbox":display,"grid":True,"tint":"dark_translucent_cyan"}
 }
}

# ---------------------------------------------------------------------------
# 4. FX and navigation icon atlas, 17 icons in transparent 144x144 cells.
# ---------------------------------------------------------------------------
im=Image.new("RGBA",SIZE,(0,0,0,0))
fx=["wave","eq","distortion","chorus","delay","reverb","cabinet"]
nav=["crown","power","settings","info","folder","search","guitar","antenna","palette","play"]
all_names=fx+nav
icon_records={}
def draw_icon(name,box):
    x1,y1,x2,y2=box; cx=(x1+x2)//2; cy=(y1+y2)//2
    global im
    im=add_glow(im,lambda dd,c:dd.ellipse((cx-42,cy-42,cx+42,cy+42),outline=c,width=3),P["glow_blue"],6)
    d=ImageDraw.Draw(im); col=rgba(P["glow_cyan"]); white=rgba("#DDFBFF")
    d.rounded_rectangle(box,radius=12,fill=rgba("#0B1420",205),outline=rgba(P["metal_border"],210),width=2)
    def line(points,width=5,fill=col): d.line(points,fill=fill,width=width,joint="curve")
    inner=(x1+28,y1+25,x2-28,y2-28)
    if name=="wave":
        pts=[]
        for k in range(61):
            xx=x1+24+k*(x2-x1-48)/60
            yy=cy+24*math.sin(k/60*math.pi*4)
            pts.append((xx,yy))
        line(pts,5)
    elif name=="eq":
        for k,h in enumerate((42,72,55,88,34)):
            xx=x1+36+k*15
            d.rounded_rectangle((xx,cy-h/2,xx+8,cy+h/2),radius=4,fill=col)
    elif name=="distortion":
        pts=[(x1+25,cy+24),(x1+48,cy+24),(x1+58,cy-25),(x1+78,cy-25),(x1+88,cy+24),(x2-25,cy+24)]
        line(pts,5)
    elif name=="chorus":
        for off in (-9,9):
            pts=[(x1+24+k*(x2-x1-48)/60,cy+off+19*math.sin(k/60*math.pi*4)) for k in range(61)]
            line(pts,3,white if off<0 else col)
    elif name=="delay":
        for k in range(3):
            xx=x1+32+k*22; yy=y1+35+k*12
            d.rounded_rectangle((xx,yy,xx+48,yy+66),radius=7,outline=col,width=4)
    elif name=="reverb":
        for r in (18,32,46):
            d.arc((cx-r,cy-r,cx+r,cy+r),200,520,fill=col,width=4)
    elif name=="cabinet":
        d.rounded_rectangle((cx-34,cy-43,cx+34,cy+43),radius=6,outline=col,width=4)
        d.ellipse((cx-22,cy-22,cx+22,cy+22),outline=white,width=4)
        d.ellipse((cx-6,cy-6,cx+6,cy+6),fill=col)
    elif name=="crown":
        line([(x1+30,y1+88),(x1+25,y1+45),(x1+53,y1+64),(cx,y1+28),(x2-53,y1+64),(x2-25,y1+45),(x2-30,y1+88),(x1+30,y1+88)],5)
        line([(x1+34,y1+99),(x2-34,y1+99)],4,white)
    elif name=="power":
        d.arc((cx-38,cy-38,cx+38,cy+38),35,325,fill=col,width=7)
        line([(cx,cy-48),(cx,cy+3)],7,white)
    elif name=="settings":
        d.ellipse((cx-28,cy-28,cx+28,cy+28),outline=col,width=7)
        d.ellipse((cx-9,cy-9,cx+9,cy+9),outline=white,width=5)
        for a in range(0,360,45):
            r=math.radians(a); line([(cx+31*math.cos(r),cy+31*math.sin(r)),(cx+44*math.cos(r),cy+44*math.sin(r))],7)
    elif name=="info":
        d.ellipse((cx-42,cy-42,cx+42,cy+42),outline=col,width=5)
        d.ellipse((cx-4,cy-24,cx+4,cy-16),fill=white)
        line([(cx,cy-4),(cx,cy+27)],6,white)
    elif name=="folder":
        line([(x1+25,y1+52),(x1+55,y1+52),(x1+67,y1+66),(x2-25,y1+66),(x2-32,y2-35),(x1+25,y2-35),(x1+25,y1+52)],5)
    elif name=="search":
        d.ellipse((cx-32,cy-36,cx+22,cy+18),outline=col,width=6)
        line([(cx+16,cy+14),(cx+43,cy+42)],7,white)
    elif name=="guitar":
        d.ellipse((cx-35,cy+2,cx+8,cy+47),outline=col,width=5)
        d.ellipse((cx-25,cy-22,cx+15,cy+22),outline=col,width=5)
        line([(cx-4,cy-9),(cx+37,cy-48)],8,white)
        line([(cx+27,cy-38),(cx+47,cy-58)],5)
        for off in (-3,2,7): line([(cx+3,cy+1+off),(cx+42,cy-42+off)],1,white)
    elif name=="antenna":
        line([(cx,cy+42),(cx,cy-20)],5,white)
        d.ellipse((cx-7,cy-28,cx+7,cy-14),fill=col)
        d.arc((cx-30,cy-55,cx+30,cy+5),205,335,fill=col,width=5)
        d.arc((cx-48,cy-72,cx+48,cy+23),205,335,fill=col,width=4)
    elif name=="palette":
        d.ellipse((cx-43,cy-38,cx+43,cy+39),outline=col,width=5)
        for ox,oy,cc in [(-20,-12,P["accent_warning"]),(7,-22,P["glow_blue"]),(25,4,P["glow_cyan"]),(-12,22,"#FFFFFF")]:
            d.ellipse((cx+ox-6,cy+oy-6,cx+ox+6,cy+oy+6),fill=rgba(cc))
    elif name=="play":
        d.polygon([(cx-22,cy-38),(cx+38,cy),(cx-22,cy+38)],fill=col)
    return
for i,name in enumerate(all_names):
    col=i%6; row=i//6
    x=32+col*164; y=75+row*285
    box=[x,y,x+144,y+144]
    draw_icon(name,box)
    d=ImageDraw.Draw(im)
    label(d,(x,y+150,x+144,y+178),name.upper(),P["text"],9)
    icon_records[name]={"category":"fx" if name in fx else "nav","bbox":box}
save(im,"neon_stage_icons_sheet.png")
manifest["sheets"]["neon_stage_icons_sheet.png"]={
 "resolution":[1024,1024],
 "elements":{"fx_icons":fx,"nav_icons":nav,"icons":icon_records,"cell_size":[144,144]}
}

(OUT/"neon_stage_spritesheet_manifest.json").write_text(
    json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("Generated 4 NEON STAGE 1024x1024 RGBA sprite sheets and manifest:")
for path in sorted(OUT.glob("*")):
    print(f"{path.relative_to(ROOT)}\t{path.stat().st_size} bytes")
