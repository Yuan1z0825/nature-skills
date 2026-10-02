#!/usr/bin/env python3
"""Lightweight PPTX QA for nature-paper2ppt outputs.

The script intentionally uses only the Python standard library so it can run in
minimal environments. It inspects PPTX XML for common delivery defects; it does
not replace rendered-slide visual review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


EMU_PER_INCH = 914400
EMU_PER_POINT = 12700
DEFAULT_SLIDE_CX = 12192000
DEFAULT_SLIDE_CY = 6858000

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}

AI_PATTERNS = [
    ("一句话总结", re.compile(r"一句话总结")),
    ("最有价值的后续方向", re.compile(r"最有价值的后续方向")),
    ("不是……而是……", re.compile(r"不是.{0,18}而是")),
    ("不只是……更是……", re.compile(r"不只是.{0,18}更是")),
    ("值得注意的是", re.compile(r"值得注意的是")),
    ("总的来说", re.compile(r"总的来说")),
    ("从某种意义上", re.compile(r"从某种意义上")),
    ("提供了新的视角", re.compile(r"提供.{0,8}新的视角")),
    ("具有重要意义", re.compile(r"具有重要意义")),
    ("未来可以进一步探索", re.compile(r"未来可以进一步探索")),
]


@dataclass
class Finding:
    severity: str
    slide: int | None
    code: str
    message: str


@dataclass
class ShapeInfo:
    kind: str
    left: int
    top: int
    width: int
    height: int
    text: str
    cropped: bool = False
    crop_values: dict[str, int] | None = None

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    @property
    def area_fraction(self) -> float:
        return (self.width * self.height) / (DEFAULT_SLIDE_CX * DEFAULT_SLIDE_CY)


def parse_xml(raw: bytes, path: str) -> ET.Element:
    try:
        return ET.fromstring(raw)
    except ET.ParseError as exc:
        raise SystemExit(f"Failed to parse {path}: {exc}") from exc


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def slide_number_from_path(path: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", path)
    return int(match.group(1)) if match else 0


def get_slide_size(zf: zipfile.ZipFile) -> tuple[int, int]:
    try:
        root = parse_xml(zf.read("ppt/presentation.xml"), "ppt/presentation.xml")
    except KeyError:
        return DEFAULT_SLIDE_CX, DEFAULT_SLIDE_CY
    size = root.find(".//p:sldSz", NS)
    if size is None:
        return DEFAULT_SLIDE_CX, DEFAULT_SLIDE_CY
    return int(size.get("cx", DEFAULT_SLIDE_CX)), int(size.get("cy", DEFAULT_SLIDE_CY))


def text_from_node(node: ET.Element) -> str:
    return "".join(t.text or "" for t in node.findall(".//a:t", NS)).strip()


def shape_bounds(node: ET.Element) -> tuple[int, int, int, int] | None:
    xfrm = node.find(".//a:xfrm", NS)
    if xfrm is None:
        xfrm = node.find(".//p:xfrm", NS)
    if xfrm is None:
        return None
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return None
    return (
        int(off.get("x", "0")),
        int(off.get("y", "0")),
        int(ext.get("cx", "0")),
        int(ext.get("cy", "0")),
    )


def crop_info(node: ET.Element) -> tuple[bool, dict[str, int] | None]:
    src_rect = node.find(".//a:srcRect", NS)
    if src_rect is None:
        return False, None
    values = {key: int(src_rect.get(key, "0")) for key in ("l", "r", "t", "b")}
    return any(value != 0 for value in values.values()), values


def extract_shapes(root: ET.Element) -> list[ShapeInfo]:
    shapes: list[ShapeInfo] = []
    for node in root.iter():
        name = local_name(node.tag)
        if name not in {"sp", "pic", "graphicFrame"}:
            continue
        bounds = shape_bounds(node)
        if bounds is None:
            continue
        left, top, width, height = bounds
        text = text_from_node(node)
        cropped, crops = crop_info(node)
        kind = "image" if name == "pic" else "table" if name == "graphicFrame" else "text"
        shapes.append(ShapeInfo(kind, left, top, width, height, text, cropped, crops))
    return shapes


def chars_per_square_inch(text: str, width: int, height: int) -> float:
    if not text or width <= 0 or height <= 0:
        return 0.0
    area = (width / EMU_PER_INCH) * (height / EMU_PER_INCH)
    return len(text) / max(area, 0.01)


def add_bounds_findings(findings: list[Finding], slide_no: int, shapes: list[ShapeInfo], slide_cx: int, slide_cy: int) -> None:
    for shape in shapes:
        if shape.left < 0 or shape.top < 0 or shape.right > slide_cx or shape.bottom > slide_cy:
            findings.append(
                Finding(
                    "high",
                    slide_no,
                    "shape_out_of_bounds",
                    f"{shape.kind} shape extends outside slide bounds",
                )
            )


def add_text_findings(findings: list[Finding], slide_no: int, shapes: list[ShapeInfo]) -> None:
    for shape in shapes:
        if not shape.text:
            continue
        for label, pattern in AI_PATTERNS:
            if pattern.search(shape.text):
                findings.append(
                    Finding(
                        "medium",
                        slide_no,
                        "ai_template_phrase",
                        f"Template-like phrase found: {label}",
                    )
                )
        density = chars_per_square_inch(shape.text, shape.width, shape.height)
        if len(shape.text) >= 60 and density > 80:
            findings.append(
                Finding(
                    "medium",
                    slide_no,
                    "text_overload",
                    f"Text box may overflow or feel dense ({len(shape.text)} chars)",
                )
            )


def add_image_findings(findings: list[Finding], slide_no: int, shapes: list[ShapeInfo], slide_cx: int, slide_cy: int) -> None:
    slide_area = slide_cx * slide_cy
    for shape in shapes:
        if shape.kind != "image":
            continue
        fraction = (shape.width * shape.height) / max(slide_area, 1)
        if shape.cropped:
            crop_sum = sum((shape.crop_values or {}).values())
            severity = "high" if crop_sum >= 25000 else "medium"
            findings.append(
                Finding(
                    severity,
                    slide_no,
                    "image_crop_applied",
                    f"Image has PPT crop settings {shape.crop_values}; confirm axes, legends, panel labels, and scale bars are preserved",
                )
            )
        if fraction < 0.08:
            findings.append(
                Finding(
                    "medium",
                    slide_no,
                    "small_evidence_image",
                    f"Image occupies only {fraction:.1%} of slide area; main evidence may be unreadable",
                )
            )


def near_miss_pairs(values: list[tuple[int, ShapeInfo]], threshold_min: int, threshold_max: int) -> Iterable[tuple[ShapeInfo, ShapeInfo, int]]:
    for index, (value_a, shape_a) in enumerate(values):
        for value_b, shape_b in values[index + 1 :]:
            delta = abs(value_a - value_b)
            if threshold_min <= delta <= threshold_max:
                yield shape_a, shape_b, delta


def add_alignment_findings(findings: list[Finding], slide_no: int, shapes: list[ShapeInfo]) -> None:
    meaningful = [s for s in shapes if s.width > EMU_PER_POINT * 20 and s.height > EMU_PER_POINT * 12]
    min_delta = 2 * EMU_PER_POINT
    max_delta = 8 * EMU_PER_POINT
    emitted = 0
    for axis, values in (
        ("left", [(s.left, s) for s in meaningful]),
        ("top", [(s.top, s) for s in meaningful]),
    ):
        for _, _, delta in near_miss_pairs(values, min_delta, max_delta):
            findings.append(
                Finding(
                    "low",
                    slide_no,
                    "alignment_near_miss",
                    f"Two objects have {axis}-edge near-miss alignment ({delta / EMU_PER_POINT:.1f} pt apart)",
                )
            )
            emitted += 1
            if emitted >= 4:
                return


def audit_pptx(path: Path) -> dict:
    findings: list[Finding] = []
    slide_summaries: list[dict] = []
    with zipfile.ZipFile(path) as zf:
        slide_cx, slide_cy = get_slide_size(zf)
        slide_paths = sorted(
            (name for name in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", name)),
            key=slide_number_from_path,
        )
        media_count = len([name for name in zf.namelist() if name.startswith("ppt/media/")])
        notes_count = len([name for name in zf.namelist() if name.startswith("ppt/notesSlides/notesSlide") and name.endswith(".xml")])
        for slide_path in slide_paths:
            slide_no = slide_number_from_path(slide_path)
            root = parse_xml(zf.read(slide_path), slide_path)
            shapes = extract_shapes(root)
            add_bounds_findings(findings, slide_no, shapes, slide_cx, slide_cy)
            add_text_findings(findings, slide_no, shapes)
            add_image_findings(findings, slide_no, shapes, slide_cx, slide_cy)
            add_alignment_findings(findings, slide_no, shapes)
            slide_summaries.append(
                {
                    "slide": slide_no,
                    "shape_count": len(shapes),
                    "image_count": sum(1 for s in shapes if s.kind == "image"),
                    "text_chars": sum(len(s.text) for s in shapes if s.text),
                }
            )

    counts = {"high": 0, "medium": 0, "low": 0}
    for finding in findings:
        counts[finding.severity] += 1
    return {
        "file": str(path),
        "slide_count": len(slide_summaries),
        "media_count": media_count,
        "notes_count": notes_count,
        "finding_counts": counts,
        "findings": [asdict(finding) for finding in findings],
        "slides": slide_summaries,
    }


def markdown_report(result: dict) -> str:
    lines = [
        "# PPTX Quality Audit",
        "",
        f"- File: `{result['file']}`",
        f"- Slides: {result['slide_count']}",
        f"- Embedded media: {result['media_count']}",
        f"- Notes slides: {result['notes_count']}",
        f"- Findings: high={result['finding_counts']['high']}, medium={result['finding_counts']['medium']}, low={result['finding_counts']['low']}",
        "",
        "## Findings",
        "",
    ]
    if not result["findings"]:
        lines.append("No structural findings detected by the XML audit.")
    else:
        lines.append("| Severity | Slide | Code | Message |")
        lines.append("|---|---:|---|---|")
        for item in result["findings"]:
            slide = "" if item["slide"] is None else str(item["slide"])
            message = item["message"].replace("|", "\\|")
            lines.append(f"| {item['severity']} | {slide} | `{item['code']}` | {message} |")
    lines.extend(
        [
            "",
            "## Scope",
            "",
            "This XML audit checks structural risk signals. It does not verify scientific correctness or replace rendered-slide visual inspection.",
        ]
    )
    return "\n".join(lines) + "\n"


def severity_rank(name: str) -> int:
    return {"none": 99, "low": 1, "medium": 2, "high": 3}[name]


def should_fail(result: dict, fail_on: str) -> bool:
    if fail_on == "none":
        return False
    threshold = severity_rank(fail_on)
    return any(severity_rank(item["severity"]) >= threshold for item in result["findings"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit PPTX structure for nature-paper2ppt quality issues.")
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--report", type=Path, help="Write a Markdown report to this path.")
    parser.add_argument("--json", type=Path, help="Write raw JSON audit data to this path.")
    parser.add_argument("--fail-on", choices=["high", "medium", "low", "none"], default="high")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.pptx.exists():
        raise SystemExit(f"PPTX not found: {args.pptx}")
    result = audit_pptx(args.pptx)
    report = markdown_report(result)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report, encoding="utf-8")
    else:
        print(report)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if should_fail(result, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
