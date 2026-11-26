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
