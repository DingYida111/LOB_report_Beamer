#!/usr/bin/env python3
"""
Build a PowerPoint twin of the Beamer deck using only Python standard library.

This avoids LaTeX and python-pptx dependencies in isolated intranet environments.
Edit deck_spec.json, then run:

    python build_pptx.py
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


EMU = 914400
SLIDE_W = 13.333333
SLIDE_H = 7.5
PPTX_W = int(SLIDE_W * EMU)
PPTX_H = int(SLIDE_H * EMU)

COLORS = {
    "orange": "F35D00",
    "orange_dark": "B84300",
    "orange_light": "FFEFE8",
    "ink": "222222",
    "gray": "5B5B5B",
    "blue": "1C4C84",
    "blue_light": "E2EFFF",
    "green": "227C56",
    "green_light": "E5F6ED",
    "purple": "60478F",
    "purple_light": "EFE9F9",
    "white": "FFFFFF",
}


def emu(v: float) -> int:
    return int(round(v * EMU))


def xesc(value: Any) -> str:
    return escape(str(value), {"\"": "&quot;"})


def font_size(points: float) -> int:
    return int(points * 100)


class Slide:
    def __init__(self, title: str | None = None):
        self.parts: list[str] = []
        self.rels: list[tuple[str, str, str]] = []
        self.next_id = 2
        if title:
            self.header(title)

    def _id(self) -> int:
        value = self.next_id
        self.next_id += 1
        return value

    def header(self, title: str) -> None:
        self.text(
            0.78,
            0.42,
            11.4,
            0.45,
            title,
            size=22,
            bold=True,
            color=COLORS["orange"],
            valign="mid",
        )
        self.rect(0.78, 1.04, 11.35, 0.035, fill=COLORS["orange"], line=COLORS["orange"])
        self.rect(0.58, 0.61, 0.12, 0.12, fill=COLORS["orange"], line=COLORS["orange"])

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str = COLORS["white"],
        line: str | None = COLORS["gray"],
        radius: bool = False,
        text: str | None = None,
        size: float = 10,
        bold: bool = False,
        color: str = COLORS["ink"],
        align: str = "ctr",
        valign: str = "mid",
        margin: float = 0.08,
    ) -> None:
        shape_id = self._id()
        geom = "roundRect" if radius else "rect"
        line_xml = "<a:ln><a:noFill/></a:ln>" if line is None else f"""
          <a:ln w="9525"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>"""
        tx = ""
        if text is not None:
            tx = self._tx_body(text, size, bold, color, align, valign, margin)
        self.parts.append(
            f"""
        <p:sp>
          <p:nvSpPr><p:cNvPr id="{shape_id}" name="Shape {shape_id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
          <p:spPr>
            <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
            <a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>
            <a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>
            {line_xml}
          </p:spPr>
          {tx}
        </p:sp>"""
        )

    def text(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        text: str,
        size: float = 10,
        bold: bool = False,
        color: str = COLORS["ink"],
        align: str = "l",
        valign: str = "top",
        margin: float = 0.02,
    ) -> None:
        self.rect(
            x,
            y,
            w,
            h,
            fill=COLORS["white"],
            line=None,
            text=text,
            size=size,
            bold=bold,
            color=color,
            align=align,
            valign=valign,
            margin=margin,
        )

    def block(self, x: float, y: float, w: float, h: float, title: str, items: list[str]) -> None:
        self.rect(x, y, w, h, fill=COLORS["orange_light"], line=None)
        self.rect(x, y, w, 0.48, fill=COLORS["orange"], line=COLORS["orange"])
        self.text(x + 0.10, y + 0.08, w - 0.20, 0.30, title, size=14, color=COLORS["white"], align="l")
        bullet_text = "\n".join([f"> {item}" for item in items])
        self.text(x + 0.28, y + 0.62, w - 0.42, h - 0.72, bullet_text, size=10.5, color=COLORS["ink"], align="l")

    def _tx_body(
        self,
        text: str,
        size: float,
        bold: bool,
        color: str,
        align: str,
        valign: str,
        margin: float,
    ) -> str:
        anchor = {"top": "t", "mid": "ctr", "bottom": "b"}.get(valign, "ctr")
        paragraphs = []
        for raw_line in str(text).split("\n"):
            line = raw_line
            bullet = False
            if line.startswith("> "):
                bullet = True
                line = line[2:]
            ppr = f'<a:pPr algn="{align}">'
            if bullet:
                ppr += '<a:buChar char="&#9656;"/>'
            ppr += "</a:pPr>"
            bold_attr = ' b="1"' if bold else ""
            paragraphs.append(
                f"""
              <a:p>{ppr}<a:r><a:rPr lang="en-US" sz="{font_size(size)}"{bold_attr}>
                <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
              </a:rPr><a:t>{xesc(line)}</a:t></a:r></a:p>"""
            )
        inset = emu(margin)
        return f"""
          <p:txBody>
            <a:bodyPr wrap="square" anchor="{anchor}" lIns="{inset}" rIns="{inset}" tIns="{inset}" bIns="{inset}"/>
            <a:lstStyle/>
            {''.join(paragraphs)}
          </p:txBody>"""

    def line(self, x1: float, y1: float, x2: float, y2: float, color: str = COLORS["gray"], arrow: bool = True) -> None:
        shape_id = self._id()
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1) or 0.01
        h = abs(y2 - y1) or 0.01
        flip_h = ' flipH="1"' if x2 < x1 else ""
        flip_v = ' flipV="1"' if y2 < y1 else ""
        tail = '<a:tailEnd type="triangle"/>' if arrow else ""
        self.parts.append(
            f"""
        <p:cxnSp>
          <p:nvCxnSpPr><p:cNvPr id="{shape_id}" name="Connector {shape_id}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>
          <p:spPr>
            <a:xfrm{flip_h}{flip_v}><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
            <a:prstGeom prst="line"><a:avLst/></a:prstGeom>
            <a:ln w="19050"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{tail}</a:ln>
          </p:spPr>
        </p:cxnSp>"""
        )

    def picture(self, x: float, y: float, w: float, h: float, media_name: str, rid: str) -> None:
        shape_id = self._id()
        self.parts.append(
            f"""
        <p:pic>
          <p:nvPicPr><p:cNvPr id="{shape_id}" name="{xesc(media_name)}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>
          <p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
          <p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
        </p:pic>"""
        )

    def xml(self) -> str:
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{PPTX_W}" cy="{PPTX_H}"/><a:chOff x="0" y="0"/><a:chExt cx="{PPTX_W}" cy="{PPTX_H}"/></a:xfrm></p:grpSpPr>
      {''.join(self.parts)}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>
"""


def slide_cover(data: dict[str, Any]) -> Slide:
    s = Slide()
    s.rect(0, 0, SLIDE_W, SLIDE_H, fill=COLORS["orange"], line=COLORS["orange"])
    s.text(1.0, 2.28, 11.33, 1.15, data["title"], size=24, bold=True, color=COLORS["white"], align="ctr", valign="mid")
    s.text(1.0, 3.75, 11.33, 0.42, data["subtitle"], size=14, color=COLORS["white"], align="ctr", valign="mid")
    s.text(1.0, 4.55, 11.33, 0.36, data["byline"], size=11, color=COLORS["white"], align="ctr", valign="mid")
    return s


def slide_desk_layer(data: dict[str, Any]) -> Slide:
    s = Slide(data["title"])
    s.text(1.55, 1.35, 2.2, 0.25, "Trading paths", size=9, bold=True, color=COLORS["blue"], align="ctr")
    s.rect(1.05, 1.85, 2.75, 0.72, fill=COLORS["blue_light"], line=COLORS["blue"], radius=True, text=data["trading_paths"][0], size=9.2)
    s.rect(1.05, 3.10, 2.75, 0.72, fill=COLORS["purple_light"], line=COLORS["purple"], radius=True, text=data["trading_paths"][1], size=9.2)

    s.text(4.65, 1.35, 2.2, 0.25, "Smart execution control", size=9, bold=True, color=COLORS["orange_dark"], align="ctr")
    s.rect(4.65, 1.65, 2.65, 0.42, fill=COLORS["white"], line=COLORS["blue"], radius=True, text=data["state_inputs"][0], size=9.2)
    s.rect(4.25, 2.38, 3.35, 0.90, fill=COLORS["orange_light"], line=COLORS["orange"], radius=True, text=data["control"], size=10, bold=True)
    s.rect(3.45, 3.95, 2.62, 0.42, fill=COLORS["white"], line=COLORS["purple"], radius=True, text=data["state_inputs"][1], size=9.2)
    s.rect(6.25, 3.95, 2.62, 0.42, fill=COLORS["white"], line=COLORS["green"], radius=True, text=data["state_inputs"][2], size=9.2)

    s.text(9.05, 1.35, 2.4, 0.25, "Efficiency levers", size=9, bold=True, color=COLORS["green"], align="ctr")
    s.rect(8.05, 2.38, 4.85, 0.90, fill=COLORS["green_light"], line=COLORS["green"], radius=True, text=data["levers"], size=9.3, bold=True)
    s.rect(8.15, 4.55, 4.65, 0.66, fill=COLORS["white"], line=COLORS["orange"], radius=True, text=data["ledger"], size=9.2, bold=True)

    s.line(3.80, 2.20, 4.25, 2.72, COLORS["orange"])
    s.line(3.80, 3.45, 4.25, 2.92, COLORS["orange"])
    s.line(5.97, 2.07, 5.97, 2.38, COLORS["gray"])
    s.line(4.76, 3.95, 5.25, 3.28, COLORS["gray"])
    s.line(7.56, 3.95, 6.50, 3.28, COLORS["gray"])
    s.line(7.60, 2.83, 8.05, 2.83, COLORS["orange"])
    s.line(10.48, 3.28, 10.48, 4.55, COLORS["gray"])
    return s


def slide_fak(data: dict[str, Any]) -> Slide:
    s = Slide(data["title"])
    x, y = 0.85, 1.28
    fills = [COLORS["blue_light"], COLORS["orange_light"], COLORS["purple_light"], COLORS["green_light"]]
    lines = [COLORS["blue"], COLORS["orange"], COLORS["purple"], COLORS["green"]]
    for idx, item in enumerate(data["pipeline"]):
        s.rect(x, y + idx * 0.90, 3.35, 0.62, fill=fills[idx], line=lines[idx], radius=True, text=item, size=8.6)
        if idx < len(data["pipeline"]) - 1:
            s.line(x + 1.67, y + idx * 0.62 + idx * 0.90, x + 1.67, y + 0.90 + idx * 0.90, COLORS["orange"])
    s.rect(4.35, 2.70, 2.45, 0.78, fill=COLORS["white"], line=COLORS["gray"], radius=True, text=data["output"], size=8.8)
    s.line(4.20, 4.52, 5.58, 3.48, COLORS["gray"])
    s.block(7.35, 1.45, 5.00, 1.75, data["case_1_title"], data["case_1"])
    s.block(7.35, 3.50, 5.00, 2.05, data["case_2_title"], data["case_2"])
    return s


def slide_liquidity(data: dict[str, Any]) -> Slide:
    s = Slide(data["title"])
    s.text(0.85, 1.26, 4.6, 0.55, data["vector"], size=7.7, color=COLORS["ink"], align="l")
    cx, cy = 2.8, 3.10
    labels = ["Cost", "Capacity", "Immediacy", "Resiliency", "Toxicity", "Internal fit"]
    angles = [270, 330, 30, 90, 150, 210]
    for r in [0.55, 1.10, 1.65]:
        points = []
        for a in angles:
            rad = math.radians(a)
            points.append((cx + math.cos(rad) * r, cy + math.sin(rad) * r))
        for i, p in enumerate(points):
            q = points[(i + 1) % len(points)]
            s.line(p[0], p[1], q[0], q[1], "C9C9C9", arrow=False)
    for a in angles:
        rad = math.radians(a)
        s.line(cx, cy, cx + math.cos(rad) * 1.75, cy + math.sin(rad) * 1.75, "C9C9C9", arrow=False)
    for label, a in zip(labels, angles):
        rad = math.radians(a)
        s.text(cx + math.cos(rad) * 2.00 - 0.50, cy + math.sin(rad) * 2.00 - 0.12, 1.0, 0.25, label, size=8.0, bold=True, align="ctr")
    s.rect(cx - 0.52, cy - 0.23, 1.04, 0.46, fill=COLORS["white"], line=None, text="liquidity\nstate", size=8.0, bold=True)
    s.block(6.65, 1.25, 5.70, 2.95, "How to read the state", data["state_rules"])
    s.rect(6.65, 4.55, 5.70, 0.90, fill=COLORS["orange_light"], line=None)
    s.rect(6.65, 4.55, 5.70, 0.48, fill=COLORS["orange"], line=COLORS["orange"], text="Design rule", size=14, color=COLORS["white"], align="l")
    s.text(7.05, 5.12, 4.90, 0.34, data["design_rule"], size=10.2, bold=True, align="ctr")
    s.text(0.80, 6.95, 11.8, 0.25, data["source"], size=6.6, color=COLORS["gray"], align="l")
    return s


def slide_internal_flow(data: dict[str, Any]) -> Slide:
    s = Slide(data["title"])
    labels = data["matrix_labels"]
    s.line(1.05, 5.10, 6.95, 5.10, COLORS["gray"])
    s.line(1.05, 5.10, 1.05, 2.05, COLORS["gray"])
    s.text(3.15, 5.35, 2.6, 0.25, labels["x"], size=8.3, color=COLORS["gray"], align="ctr")
    s.text(0.28, 3.20, 1.55, 0.25, labels["y"], size=8.3, color=COLORS["gray"], align="ctr")
    s.rect(2.45, 1.30, 2.75, 0.65, fill=COLORS["white"], line=COLORS["orange"], radius=True, text="Policy map from\ninternal fit score", size=9, bold=True)
    s.rect(1.25, 2.20, 2.55, 1.35, fill=COLORS["orange_light"], line=None, text=labels["top_left"], size=9, bold=True)
    s.rect(3.95, 2.20, 2.55, 1.35, fill=COLORS["green_light"], line=None, text=labels["top_right"], size=9, bold=True)
    s.rect(1.25, 3.70, 2.55, 1.35, fill=COLORS["purple_light"], line=None, text=labels["bottom_left"], size=9, bold=True)
    s.rect(3.95, 3.70, 2.55, 1.35, fill=COLORS["blue_light"], line=None, text=labels["bottom_right"], size=9, bold=True)
    s.block(8.10, 1.55, 4.90, 2.20, "Fit score inputs", data["fit_inputs"])
    s.block(8.10, 4.05, 4.90, 1.95, "Decision principle", data["principles"])
    return s


def slide_pnl(data: dict[str, Any]) -> Slide:
    s = Slide(data["title"])
    s.rect(0.78, 1.42, 5.60, 2.20, fill=COLORS["orange_light"], line=None)
    s.rect(0.78, 1.42, 5.60, 0.56, fill=COLORS["orange"], line=COLORS["orange"], text=data["target_title"], size=14, color=COLORS["white"], align="l")
    s.text(0.78, 2.12, 5.60, 0.62, data["target_value"], size=26, bold=True, color=COLORS["orange_dark"], align="ctr")
    s.text(0.78, 2.82, 5.60, 0.30, data["target_subtitle"], size=10.5, align="ctr")
    s.text(1.10, 3.90, 5.0, 1.0, "\n".join(["> " + item for item in data["formula_items"]]), size=9.5)
    x = 0.95
    for item, fill in zip(data["rollout"], [COLORS["blue_light"], COLORS["orange_light"], COLORS["purple_light"], COLORS["green_light"]]):
        s.rect(x, 5.78, 1.15, 0.34, fill=fill, line=COLORS["gray"], radius=True, text=item, size=7.8)
        x += 1.25
    s.text(8.00, 1.35, 3.5, 0.25, data["attribution_title"], size=8.8, color=COLORS["gray"], align="ctr")
    y = 1.82
    fills = [COLORS["orange_light"], COLORS["blue_light"], COLORS["purple_light"]]
    lines = [COLORS["orange"], COLORS["blue"], COLORS["purple"]]
    for idx, (name, desc) in enumerate(data["attribution"]):
        s.rect(6.78, y + idx * 0.88, 5.55, 0.50, fill=fills[idx], line=lines[idx], radius=True, text=f"{name}        {desc}", size=8.0, bold=False, align="l")
    s.rect(6.78, 5.00, 5.55, 0.72, fill=COLORS["green_light"], line=COLORS["green"], radius=True, text=data["ledger"], size=8.5, bold=True)
    s.line(9.55, 2.32, 9.55, 5.00, COLORS["gray"])
    return s


SLIDE_BUILDERS = [
    ("cover", slide_cover),
    ("desk_layer", slide_desk_layer),
    ("fak", slide_fak),
    ("liquidity_state", slide_liquidity),
    ("internal_flow", slide_internal_flow),
    ("pnl", slide_pnl),
]


def content_types(num_slides: int) -> str:
    slides = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, num_slides + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Default Extension="jpg" ContentType="image/jpeg"/>
  <Default Extension="jpeg" ContentType="image/jpeg"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  {slides}
</Types>
"""


def root_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


def presentation_xml(num_slides: int) -> str:
    ids = "\n".join(f'<p:sldId id="{255 + i}" r:id="rId{i}"/>' for i in range(1, num_slides + 1))
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId{num_slides + 1}"/></p:sldMasterIdLst>
  <p:sldIdLst>{ids}</p:sldIdLst>
  <p:sldSz cx="{PPTX_W}" cy="{PPTX_H}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>
"""


def presentation_rels(num_slides: int) -> str:
    rels = [
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, num_slides + 1)
    ]
    rels.append(
        f'<Relationship Id="rId{num_slides + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    )
    rels.append(
        f'<Relationship Id="rId{num_slides + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>'
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {' '.join(rels)}
</Relationships>
"""


def simple_rels(target: str, rel_type: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="{rel_type}" Target="{target}"/>
</Relationships>
"""


def slide_rels(slide: Slide) -> str:
    rels = [
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
    ]
    for rid, rel_type, target in slide.rels:
        rels.append(f'<Relationship Id="{rid}" Type="{rel_type}" Target="{target}"/>')
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {' '.join(rels)}
</Relationships>
"""


def slide_master() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{PPTX_W}" cy="{PPTX_H}"/><a:chOff x="0" y="0"/><a:chExt cx="{PPTX_W}" cy="{PPTX_H}"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
</p:sldMaster>
"""


def slide_layout() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
</p:sldLayout>
"""


def theme() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="LOB Smart Execution">
  <a:themeElements>
    <a:clrScheme name="LOB">
      <a:dk1><a:srgbClr val="{COLORS['ink']}"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="{COLORS['gray']}"/></a:dk2><a:lt2><a:srgbClr val="F7F7F7"/></a:lt2>
      <a:accent1><a:srgbClr val="{COLORS['orange']}"/></a:accent1>
      <a:accent2><a:srgbClr val="{COLORS['blue']}"/></a:accent2>
      <a:accent3><a:srgbClr val="{COLORS['green']}"/></a:accent3>
      <a:accent4><a:srgbClr val="{COLORS['purple']}"/></a:accent4>
      <a:accent5><a:srgbClr val="{COLORS['orange_dark']}"/></a:accent5>
      <a:accent6><a:srgbClr val="{COLORS['gray']}"/></a:accent6>
      <a:hlink><a:srgbClr val="{COLORS['blue']}"/></a:hlink><a:folHlink><a:srgbClr val="{COLORS['purple']}"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Arial"><a:majorFont><a:latin typeface="Arial"/></a:majorFont><a:minorFont><a:latin typeface="Arial"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="LOB"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme>
  </a:themeElements>
</a:theme>
"""


def core_props(meta: dict[str, Any]) -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{xesc(meta.get('title', 'LOB report'))}</dc:title>
  <dc:creator>{xesc(meta.get('author', ''))}</dc:creator>
  <cp:lastModifiedBy>{xesc(meta.get('author', ''))}</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>
"""


def app_props(num_slides: int) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Python stdlib PPTX builder</Application>
  <PresentationFormat>On-screen Show (16:9)</PresentationFormat>
  <Slides>{num_slides}</Slides>
</Properties>
"""


def build(spec_path: Path, output_path: Path | None = None) -> Path:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    slide_data = spec["slides"]
    slides = [builder(slide_data[key]) for key, builder in SLIDE_BUILDERS]
    output = output_path or spec_path.parent / spec.get("output", "LOB_report_internal_template.pptx")
    media_entries: list[tuple[Path, str]] = []

    for idx, overlay in enumerate(spec.get("image_overlays", []), start=1):
        slide_no = int(overlay["slide"])
        if slide_no < 1 or slide_no > len(slides):
            raise ValueError(f"image_overlays[{idx}] has invalid slide number: {slide_no}")
        image_path = Path(overlay["path"])
        if not image_path.is_absolute():
            image_path = spec_path.parent / image_path
        if not image_path.exists():
            raise FileNotFoundError(f"Missing overlay image: {image_path}")
        ext = image_path.suffix.lower().lstrip(".")
        if ext not in {"png", "jpg", "jpeg"}:
            raise ValueError(f"Unsupported image extension for {image_path}; use png/jpg/jpeg")
        media_name = f"image{idx}.{ext}"
        slide = slides[slide_no - 1]
        rid = f"rId{len(slide.rels) + 2}"
        slide.rels.append((rid, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image", f"../media/{media_name}"))
        slide.picture(float(overlay["x"]), float(overlay["y"]), float(overlay["w"]), float(overlay["h"]), media_name, rid)
        media_entries.append((image_path, media_name))

    tmp = output.with_suffix(".tmp")
    if tmp.exists():
        tmp.unlink()

    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types(len(slides)))
        z.writestr("_rels/.rels", root_rels())
        z.writestr("docProps/core.xml", core_props(spec.get("meta", {})))
        z.writestr("docProps/app.xml", app_props(len(slides)))
        z.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(slides)))
        z.writestr("ppt/theme/theme1.xml", theme())
        z.writestr("ppt/slideMasters/slideMaster1.xml", slide_master())
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", simple_rels("../slideLayouts/slideLayout1.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"))
        z.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout())
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", simple_rels("../slideMasters/slideMaster1.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster"))
        for idx, slide in enumerate(slides, start=1):
            z.writestr(f"ppt/slides/slide{idx}.xml", slide.xml())
            z.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", slide_rels(slide))
        for image_path, media_name in media_entries:
            z.write(image_path, f"ppt/media/{media_name}")

    if output.exists():
        output.unlink()
    shutil.move(tmp, output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Build PPTX twin for intranet editing.")
    parser.add_argument("--spec", default="deck_spec.json", help="Path to JSON spec.")
    parser.add_argument("--out", default=None, help="Output PPTX path.")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.is_absolute():
        spec_path = Path(__file__).resolve().parent / spec_path
    output = Path(args.out) if args.out else None
    built = build(spec_path, output)
    print(f"Built {built}")


if __name__ == "__main__":
    main()
