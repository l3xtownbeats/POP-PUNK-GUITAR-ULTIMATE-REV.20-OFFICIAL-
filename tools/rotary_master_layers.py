#!/usr/bin/env python3
"""Extract alpha-separated layers from the canonical PPGU rotary SVG master.

The SVG master remains the sole geometry source. This module never invents new
knob silhouettes, tick positions or metal details. The same authored physical
control is reused for all nine REV.20 parameters; JUCE draws the live pointer
and value telemetry from the real APVTS value.
"""
from __future__ import annotations

import copy
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

LAYER_ORDER = ("BASE", "RIM", "FACE", "POINTER", "SCALE", "GLOW")
EXPECTED_CHILD_TAGS = [
    "circle", "circle", "circle", "circle", "circle", "circle",
    "g", "g", "g", "circle", "path", "path", "circle", "circle",
    "circle", "path", "circle",
]


def _tag_name(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def load_rotary_master_layers(repository_root: Path) -> dict[str, str]:
    """Return six standalone 512x512 SVG documents derived from the master."""
    source = (repository_root / "SKIN" / "Skin_053" / "assets"
              / "vector" / "rotary_knob_master.svg")
    if not source.is_file():
        raise FileNotFoundError(f"Canonical rotary SVG master is missing: {source}")

    root = ET.parse(source).getroot()
    if _tag_name(root) != "svg":
        raise ValueError("Canonical rotary source root must be <svg>")
    if root.attrib.get("viewBox") != "0 0 512 512":
        raise ValueError("Canonical rotary master viewBox must remain 0 0 512 512")
    if root.attrib.get("width") != "512" or root.attrib.get("height") != "512":
        raise ValueError("Canonical rotary master canvas must remain 512x512")

    defs = next((child for child in list(root) if _tag_name(child) == "defs"), None)
    if defs is None:
        raise ValueError("Canonical rotary SVG must retain its gradients and filters")

    shell_groups = [
        child for child in list(root)
        if _tag_name(child) == "g" and child.attrib.get("filter") == "url(#drop)"
    ]
    if len(shell_groups) != 1:
        raise ValueError("Expected one canonical rotary shell group with drop shadow")
    shell = shell_groups[0]
    nodes = list(shell)
    found_tags = [_tag_name(node) for node in nodes]
    if found_tags != EXPECTED_CHILD_TAGS:
        raise ValueError(
            "Canonical rotary SVG structure changed; update the explicit layer map "
            f"after reviewing the artwork. Found child tags: {found_tags}"
        )

    arc_group = nodes[6]
    arc_nodes = list(arc_group)
    if len(arc_nodes) != 3 or any(_tag_name(node) != "path" for node in arc_nodes):
        raise ValueError("Canonical rotary arc group must contain 3 individual paths")

    # Each mapping retains original source SVG elements verbatim:
    # base shadow and outer silhouette; machined outer metal/bezel; inset face;
    # pointer/hub; unblurred arcs and radial index marks; blurred cyan arc only.
    mapped = {
        "BASE": [nodes[0], nodes[16]],
        "RIM": [nodes[1], nodes[2]],
        "FACE": [nodes[3], nodes[4], nodes[5], nodes[9], nodes[15]],
        "POINTER": [nodes[10], nodes[11], nodes[12], nodes[13], nodes[14]],
        "SCALE": [],
        "GLOW": [arc_nodes[0]],
    }

    scale_arcs = ET.Element(f"{{{SVG_NS}}}g", {"stroke-linecap": "round"})
    for node in arc_nodes[1:]:
        scale_arcs.append(copy.deepcopy(node))
    mapped["SCALE"] = [scale_arcs, nodes[7], nodes[8]]

    output: dict[str, str] = {}
    for layer_name in LAYER_ORDER:
        svg = ET.Element(f"{{{SVG_NS}}}svg", {
            "width": "512", "height": "512", "viewBox": "0 0 512 512",
            "version": "1.1",
        })
        svg.append(copy.deepcopy(defs))
        attributes = {"id": f"layer-{layer_name.lower()}"}
        if layer_name == "BASE":
            # The source master applies a global cast shadow; retain that optical
            # treatment once on the outer silhouette rather than duplicating it
            # on every independently composited layer.
            attributes["filter"] = "url(#drop)"
        group = ET.SubElement(svg, f"{{{SVG_NS}}}g", attributes)
        for node in mapped[layer_name]:
            group.append(copy.deepcopy(node))
        output[layer_name] = ET.tostring(svg, encoding="unicode")

    if any(not value for value in output.values()):
        raise ValueError("Canonical rotary layer extraction produced an empty SVG")
    return output


# Portable Pillow raster counterpart used by Windows build pipelines. Coordinates,
# radii, paths and source colors below mirror the SVG elements above. This avoids
# a native Cairo DLL dependency in the VST3 build while retaining the canonical
# source geometry and palette.
def _rgba(hex_colour: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = hex_colour.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16),
            int(value[4:6], 16), alpha)


def _interpolate(stops: list[tuple[float, tuple[int, int, int, int]]],
                 amount: float) -> tuple[int, int, int, int]:
    amount = max(0.0, min(1.0, amount))
    for index in range(1, len(stops)):
        if amount <= stops[index][0]:
            p0, c0 = stops[index - 1]
            p1, c1 = stops[index]
            blend = 0.0 if p1 == p0 else (amount - p0) / (p1 - p0)
            return tuple(round(c0[channel] + (c1[channel] - c0[channel]) * blend)
                         for channel in range(4))
    return stops[-1][1]


def _gradient_disc(size: int, centre: tuple[float, float], radius: float,
                   stops: list[tuple[float, tuple[int, int, int, int]]],
                   kind: str = "radial", direction: tuple[float, float] = (0.9, 1.0)):
    from PIL import Image
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pixels = image.load()
    cx, cy = centre
    left = max(0, int(cx - radius - 1))
    right = min(size, int(cx + radius + 2))
    top = max(0, int(cy - radius - 1))
    bottom = min(size, int(cy + radius + 2))
    dx, dy = direction
    denominator = max(1e-9, 2.0 * radius * (abs(dx) + abs(dy)))
    for y in range(top, bottom):
        for x in range(left, right):
            rx, ry = x - cx, y - cy
            distance = (rx * rx + ry * ry) ** 0.5
            if distance > radius:
                continue
            if kind == "linear":
                t = ((rx + radius) * dx + (ry + radius) * dy) / denominator
            else:
                t = distance / radius
            pixels[x, y] = _interpolate(stops, t)
    return image


def draw_rotary_master_layer_pillow(layer_name: str, size: int = 128):
    """Rasterize the canonical SVG-master design using portable Pillow primitives."""
    from PIL import Image, ImageChops, ImageDraw, ImageFilter

    if layer_name not in LAYER_ORDER:
        raise ValueError(f"Unknown rotary layer: {layer_name}")
    canvas = 512
    centre = (256, 256)
    cx, cy = centre
    image = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    def ellipse(radius, fill=None, outline=None, width=1):
        box = (cx-radius, cy-radius, cx+radius, cy+radius)
        draw.ellipse(box, fill=fill, outline=outline, width=max(1, round(width)))

    def arc(radius, start, end, fill, width):
        box = (cx-radius, cy-radius, cx+radius, cy+radius)
        draw.arc(box, start=start, end=end, fill=fill, width=max(1, round(width)))

    if layer_name == "BASE":
        # Source SVG: drop filter on the r=222 black outer silhouette.
        shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.ellipse((34, 46, 478, 490), fill=(0, 0, 0, 158))
        shadow = shadow.filter(ImageFilter.GaussianBlur(10))
        image.alpha_composite(shadow)
        draw = ImageDraw.Draw(image)
        ellipse(222, fill=_rgba("#02050A"), outline=_rgba("#000000"), width=8)
        # Source SVG radial shadow overlay: transparent until 68%, black at 100%.
        shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
        sp = shade.load()
        for y in range(42, 470):
            for x in range(42, 470):
                distance = (((x-cx)**2 + (y-cy)**2)**0.5) / 214.0
                if distance > 0.68:
                    alpha = round(0.72 * 255 * min(1.0, (distance - 0.68) / 0.32))
                    sp[x, y] = (0, 0, 0, alpha)
        image.alpha_composite(shade)

    elif layer_name == "RIM":
        outer = _gradient_disc(canvas, centre, 214, [
            (0.00, _rgba("#F4F8FC")), (0.12, _rgba("#AEBFCE")),
            (0.28, _rgba("#657A8E")), (0.47, _rgba("#D7E0E8")),
            (0.66, _rgba("#485D72")), (0.86, _rgba("#9AACBA")),
            (1.00, _rgba("#24384C")),
        ])
        image.alpha_composite(outer)
        draw = ImageDraw.Draw(image)
        ellipse(214, outline=_rgba("#D4E2EA", 166), width=3)
        bezel = _gradient_disc(canvas, centre, 199, [
            (0.00, _rgba("#AFC1D0")), (0.18, _rgba("#26394A")),
            (0.48, _rgba("#0A111B")), (0.76, _rgba("#34495B")),
            (1.00, _rgba("#050A11")),
        ], kind="linear", direction=(0.9, 1.0))
        image.alpha_composite(bezel)
        draw = ImageDraw.Draw(image)
        ellipse(199, outline=_rgba("#050A10"), width=8)

    elif layer_name == "FACE":
        draw = ImageDraw.Draw(image)
        ellipse(181, fill=_rgba("#050B13"),
                outline=_rgba("#72899C", 184), width=3)
        face = _gradient_disc(canvas, centre, 169, [
            (0.00, _rgba("#26394C")), (0.38, _rgba("#101C2A")),
            (0.78, _rgba("#080F19")), (1.00, _rgba("#02060B")),
        ])
        # The source gradient hotspot is at (34%,24%), not at the centre.
        # Rebuild the gradient disc using that exact SVG focal point.
        face = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
        fp = face.load()
        focal = (0.34 * canvas, 0.24 * canvas)
        for y in range(87, 426):
            for x in range(87, 426):
                if (x-cx)**2 + (y-cy)**2 <= 169**2:
                    t = min(1.0, (((x-focal[0])**2 + (y-focal[1])**2)**0.5) / (0.88*169))
                    fp[x, y] = _interpolate([
                        (0.00, _rgba("#26394C")), (0.38, _rgba("#101C2A")),
                        (0.78, _rgba("#080F19")), (1.00, _rgba("#02060B")),
                    ], t)
        image.alpha_composite(face)
        draw = ImageDraw.Draw(image)
        ellipse(169, outline=_rgba("#1D3447"), width=4)
        ellipse(156, outline=_rgba("#7890A4", 56), width=2)
        ellipse(126, outline=_rgba("#000000", 140), width=3)
        # Source SVG specular reflection arc.
        draw.arc((82, 82, 430, 430), start=215, end=315,
                 fill=_rgba("#FFFFFF", 28), width=3)

    elif layer_name == "SCALE":
        draw = ImageDraw.Draw(image)
        # Source arc group: bright upper-right cyan arc and muted upper-left arc.
        arc(201, 270, 360, _rgba("#00D9FF", 140), 2)
        arc(201, 180, 270, _rgba("#71889A", 115), 2)
        major = [
            ((256,77),(256,98)), ((166,98),(176,116)),
            ((102,166),(120,176)), ((77,256),(99,256)),
            ((102,346),(120,336)), ((166,414),(176,396)),
            ((346,414),(336,396)), ((410,346),(392,336)),
            ((435,256),(413,256)), ((410,166),(392,176)),
            ((346,98),(336,116)),
        ]
        for p0,p1 in major:
            draw.line((p0,p1), fill=_rgba("#A9BDCC", 191), width=3)
        minor = [
            ((211,82),(216,96)), ((121,121),(135,135)),
            ((82,211),(96,216)), ((82,301),(96,296)),
            ((121,391),(135,377)), ((211,430),(216,416)),
            ((301,430),(296,416)), ((391,391),(377,377)),
            ((430,301),(416,296)), ((430,211),(416,216)),
            ((391,121),(377,135)), ((301,82),(296,96)),
        ]
        for p0,p1 in minor:
            draw.line((p0,p1), fill=_rgba("#50697D", 204), width=2)

    elif layer_name == "GLOW":
        glow = Image.new("RGBA", image.size, (0,0,0,0))
        gd = ImageDraw.Draw(glow)
        gd.arc((55,55,457,457), start=270, end=360,
               fill=_rgba("#00D9FF", 51), width=5)
        image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(7)))

    elif layer_name == "POINTER":
        # Static default-angle pointer is exported as an independent layer.
        grad = Image.new("RGBA", image.size, (0,0,0,0))
        gp = grad.load()
        for y in range(125, 259):
            t = max(0.0, min(1.0, (y-125)/131))
            colour = _interpolate([
                (0.0, _rgba("#F7FDFF")), (0.55, _rgba("#A9C4D4")),
                (1.0, _rgba("#00D9FF")),
            ], t)
            for x in range(240, 273):
                gp[x,y] = colour
        mask = Image.new("L", image.size, 0)
        md = ImageDraw.Draw(mask)
        md.polygon([(256,256),(244,139),(256,125),(268,139),(264,256)], fill=255)
        grad.putalpha(ImageChops.multiply(grad.getchannel("A"), mask))
        image.alpha_composite(grad)
        draw = ImageDraw.Draw(image)
        draw.line((256,256,256,145), fill=_rgba("#FFFFFF",179), width=2)
        hub = _gradient_disc(canvas, centre, 25, [
            (0.00,_rgba("#F4F8FC")),(0.25,_rgba("#AEBFCE")),
            (0.55,_rgba("#657A8E")),(0.80,_rgba("#9AACBA")),
            (1.00,_rgba("#24384C")),
        ])
        image.alpha_composite(hub)
        draw = ImageDraw.Draw(image)
        ellipse(25, outline=_rgba("#D9F7FF"), width=3)
        ellipse(14, fill=_rgba("#07121D"), outline=_rgba("#00D9FF"), width=3)
        ellipse(5, fill=_rgba("#DDFBFF"))

    else:
        raise ValueError(f"Unknown rotary layer: {layer_name}")

    return image.resize((size, size), Image.Resampling.LANCZOS)
