#!/usr/bin/env python3
"""Audit rendered PDF figures for probable text and graphic collisions.

The audit is backend-neutral: Python and R figures are both checked from their
final PDF geometry. Reliable collisions (text-text, text crossed by a stroked
path, and text clipped by the page) block delivery. Partial text overlap with a
filled shape or raster image is reported for review because in-bar labels,
heatmap values, microscopy annotations, and scale bars can be intentional.

PyMuPDF is imported lazily so ``--self-test`` can exercise the geometry core in
minimal CI environments. Install the runtime dependency with
``python -m pip install -r skills/nature-figure/requirements.txt``.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Sequence


Rect = tuple[float, float, float, float]
Point = tuple[float, float]
Segment = tuple[Point, Point]


@dataclass(frozen=True)
class TextBox:
    index: int
    text: str
    bbox: Rect


@dataclass(frozen=True)
class StrokePath:
    index: int
    bbox: Rect
    width: float
    segments: tuple[Segment, ...]


@dataclass(frozen=True)
class FilledRegion:
    index: int
    bbox: Rect
    source: str


@dataclass(frozen=True)
class TraceBox:
    index: int
    text: str
    bbox: Rect


@dataclass
class PageGeometry:
    page: int
    bbox: Rect
    texts: list[TextBox] = field(default_factory=list)
    traces: list[TraceBox] = field(default_factory=list)
    strokes: list[StrokePath] = field(default_factory=list)
    fills: list[FilledRegion] = field(default_factory=list)
    images: list[FilledRegion] = field(default_factory=list)


@dataclass(frozen=True)
class CollisionFinding:
    severity: str
    kind: str
    page: int
    message: str
    text: str
    text_bbox: Rect
    other_text: str | None = None
    other_bbox: Rect | None = None
    object_count: int = 1
    object_indexes: tuple[int, ...] = ()


def normalize_rect(rect: Sequence[float]) -> Rect:
    x0, y0, x1, y1 = (float(value) for value in rect)
    return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)


def rect_width(rect: Rect) -> float:
    return max(0.0, rect[2] - rect[0])


def rect_height(rect: Rect) -> float:
    return max(0.0, rect[3] - rect[1])


def rect_area(rect: Rect) -> float:
    return rect_width(rect) * rect_height(rect)


def rect_intersection(first: Rect, second: Rect) -> Rect | None:
    x0 = max(first[0], second[0])
    y0 = max(first[1], second[1])
    x1 = min(first[2], second[2])
    y1 = min(first[3], second[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return x0, y0, x1, y1


def rect_overlap_ratio(first: Rect, second: Rect) -> float:
    intersection = rect_intersection(first, second)
    if intersection is None:
        return 0.0
    denominator = min(rect_area(first), rect_area(second))
    return rect_area(intersection) / denominator if denominator > 0 else 0.0


def rect_contains(outer: Rect, inner: Rect, tolerance: float = 0.0) -> bool:
    return (
        inner[0] >= outer[0] - tolerance
        and inner[1] >= outer[1] - tolerance
        and inner[2] <= outer[2] + tolerance
        and inner[3] <= outer[3] + tolerance
    )


def rect_inset(rect: Rect, amount: float) -> Rect:
    maximum = max(0.0, min(rect_width(rect), rect_height(rect)) * 0.2)
    inset = min(max(0.0, amount), maximum)
    return rect[0] + inset, rect[1] + inset, rect[2] - inset, rect[3] - inset


def rect_expand(rect: Rect, amount: float) -> Rect:
    pad = max(0.0, amount)
    return rect[0] - pad, rect[1] - pad, rect[2] + pad, rect[3] + pad


def union_rects(rectangles: Iterable[Rect]) -> Rect | None:
    rows = list(rectangles)
    if not rows:
        return None
    return (
        min(row[0] for row in rows),
        min(row[1] for row in rows),
        max(row[2] for row in rows),
        max(row[3] for row in rows),
    )


def point_in_rect(point: Point, rect: Rect) -> bool:
    return rect[0] <= point[0] <= rect[2] and rect[1] <= point[1] <= rect[3]


def segment_intersects_rect(segment: Segment, rect: Rect) -> bool:
    """Return whether a line segment intersects a rectangle (Liang-Barsky)."""
    (x0, y0), (x1, y1) = segment
    if point_in_rect((x0, y0), rect) or point_in_rect((x1, y1), rect):
        return True
    dx = x1 - x0
    dy = y1 - y0
    p = (-dx, dx, -dy, dy)
    q = (x0 - rect[0], rect[2] - x0, y0 - rect[1], rect[3] - y0)
    lower, upper = 0.0, 1.0
    for denominator, numerator in zip(p, q):
        if abs(denominator) < 1e-12:
            if numerator < 0:
                return False
            continue
        ratio = numerator / denominator
        if denominator < 0:
            lower = max(lower, ratio)
        else:
            upper = min(upper, ratio)
        if lower > upper:
            return False
    return True


def cubic_segments(points: Sequence[Point], steps: int = 16) -> list[Segment]:
    if len(points) != 4:
        return []
    p0, p1, p2, p3 = points
    samples: list[Point] = []
    for index in range(steps + 1):
        t = index / steps
        u = 1.0 - t
        samples.append(
            (
                u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
                u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
            )
        )
    return list(zip(samples, samples[1:]))


def rectangle_segments(rect: Rect) -> tuple[Segment, ...]:
    x0, y0, x1, y1 = rect
    return (
        ((x0, y0), (x1, y0)),
        ((x1, y0), (x1, y1)),
        ((x1, y1), (x0, y1)),
        ((x0, y1), (x0, y0)),
    )


def _point(value: Any) -> Point:
    return float(value.x), float(value.y)


def _segments_from_items(items: Sequence[Sequence[Any]]) -> tuple[Segment, ...]:
    segments: list[Segment] = []
    for item in items:
        if not item:
            continue
        operator = item[0]
        if operator == "l" and len(item) >= 3:
            segments.append((_point(item[1]), _point(item[2])))
        elif operator == "c" and len(item) >= 5:
            segments.extend(cubic_segments([_point(value) for value in item[1:5]]))
        elif operator == "re" and len(item) >= 2:
            segments.extend(rectangle_segments(normalize_rect(tuple(item[1]))))
        elif operator == "qu" and len(item) >= 2:
            quad = item[1]
            points = [_point(quad.ul), _point(quad.ur), _point(quad.lr), _point(quad.ll)]
            segments.extend(zip(points, points[1:] + points[:1]))
    return tuple(segments)


def _text_from_chars(chars: Sequence[Sequence[Any]]) -> str:
    output: list[str] = []
    for char in chars:
        try:
            codepoint = int(char[0])
            output.append(chr(codepoint) if codepoint >= 0 else "�")
        except (TypeError, ValueError, OverflowError):
            output.append("�")
    return "".join(output).strip()


def extract_pdf_geometry(path: Path) -> list[PageGeometry]:
    try:
        import pymupdf as fitz  # type: ignore
    except ImportError:
        try:
            import fitz  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "PyMuPDF is required for rendered collision QA. Install it with: "
                "python -m pip install -r skills/nature-figure/requirements.txt"
            ) from exc

    document = fitz.open(path)
    pages: list[PageGeometry] = []
    try:
        for page_index, page in enumerate(document, 1):
            geometry = PageGeometry(page=page_index, bbox=normalize_rect(tuple(page.rect)))

            trace_rows: list[TraceBox] = []
            for trace_index, trace in enumerate(page.get_texttrace()):
                text = _text_from_chars(trace.get("chars", ()))
                if not text:
                    continue
                trace_rows.append(
                    TraceBox(index=trace_index, text=text, bbox=normalize_rect(trace["bbox"]))
                )
            geometry.traces.extend(trace_rows)

            text_dict = page.get_text("dict")
            text_index = 0
            used_trace_indexes: set[int] = set()
            for block in text_dict.get("blocks", []):
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    spans = [span for span in line.get("spans", []) if span.get("text", "").strip()]
                    if not spans:
                        continue
                    loose_bbox = union_rects(normalize_rect(span["bbox"]) for span in spans)
                    if loose_bbox is None:
                        continue
                    matched_traces = [
                        trace
                        for trace in trace_rows
                        if trace.index not in used_trace_indexes
                        and rect_overlap_ratio(trace.bbox, loose_bbox) >= 0.3
                    ]
                    bbox = union_rects(trace.bbox for trace in matched_traces) or loose_bbox
                    used_trace_indexes.update(trace.index for trace in matched_traces)
                    text = "".join(span.get("text", "") for span in spans).strip()
                    geometry.texts.append(TextBox(index=text_index, text=text, bbox=bbox))
                    text_index += 1

            for trace in trace_rows:
                if trace.index in used_trace_indexes:
                    continue
                if rect_intersection(trace.bbox, geometry.bbox) is None:
                    continue
                geometry.texts.append(
                    TextBox(index=text_index, text=trace.text, bbox=trace.bbox)
                )
                text_index += 1

            for drawing_index, drawing in enumerate(page.get_drawings()):
                drawing_type = str(drawing.get("type", ""))
                drawing_bbox = normalize_rect(tuple(drawing["rect"]))
                if "s" in drawing_type and drawing.get("stroke_opacity", 1.0) not in (None, 0):
                    segments = _segments_from_items(drawing.get("items", ()))
                    if segments:
                        geometry.strokes.append(
                            StrokePath(
                                index=drawing_index,
                                bbox=drawing_bbox,
                                width=float(drawing.get("width") or 0.0),
                                segments=segments,
                            )
                        )
                if "f" in drawing_type and drawing.get("fill_opacity", 1.0) not in (None, 0):
                    rectangle_items = [item for item in drawing.get("items", ()) if item and item[0] == "re"]
                    if rectangle_items:
                        for offset, item in enumerate(rectangle_items):
                            geometry.fills.append(
                                FilledRegion(
                                    index=drawing_index * 1000 + offset,
                                    bbox=normalize_rect(tuple(item[1])),
                                    source="fill",
                                )
                            )
                    else:
                        geometry.fills.append(
                            FilledRegion(index=drawing_index, bbox=drawing_bbox, source="fill")
                        )

            image_index = 0
            seen_images: set[tuple[int, int, int, int]] = set()
            for image in page.get_images(full=True):
                xref = int(image[0])
                for image_rect in page.get_image_rects(xref):
                    bbox = normalize_rect(tuple(image_rect))
                    key = tuple(round(value * 10) for value in bbox)
                    if key in seen_images:
                        continue
                    seen_images.add(key)
                    geometry.images.append(
                        FilledRegion(index=image_index, bbox=bbox, source="image")
                    )
                    image_index += 1

            pages.append(geometry)
    finally:
        document.close()
    return pages


def _outside_distance(inner: Rect, outer: Rect) -> float:
    return max(
        outer[0] - inner[0],
        outer[1] - inner[1],
        inner[2] - outer[2],
        inner[3] - outer[3],
        0.0,
    )


def _finding_sort_key(finding: CollisionFinding) -> tuple[Any, ...]:
    severity_order = {"FAIL": 0, "WARN": 1}
    return severity_order.get(finding.severity, 2), finding.page, finding.kind, finding.text_bbox


def audit_page_geometry(
    page: PageGeometry,
    *,
    text_inset_pt: float = 0.6,
    min_overlap_ratio: float = 0.05,
    clipping_tolerance_pt: float = 0.5,
    background_area_ratio: float = 0.2,
) -> tuple[list[CollisionFinding], dict[str, int]]:
    findings: list[CollisionFinding] = []
    info = {"contained_fill_overlays": 0, "contained_image_overlays": 0}

    for first, second in combinations(page.texts, 2):
        ratio = rect_overlap_ratio(first.bbox, second.bbox)
        if ratio < min_overlap_ratio:
            continue
        findings.append(
            CollisionFinding(
                severity="FAIL",
                kind="text-text",
                page=page.page,
                message=f"Text boxes overlap by {ratio:.1%} of the smaller box",
                text=first.text,
                text_bbox=first.bbox,
                other_text=second.text,
                other_bbox=second.bbox,
            )
        )

    for text in page.texts:
        inner = rect_inset(text.bbox, text_inset_pt)
        hit_indexes: list[int] = []
        hit_rectangles: list[Rect] = []
        for stroke in page.strokes:
            expanded = rect_expand(inner, max(0.0, stroke.width) / 2)
            if rect_intersection(expanded, rect_expand(stroke.bbox, stroke.width / 2)) is None:
                continue
            if any(segment_intersects_rect(segment, expanded) for segment in stroke.segments):
                hit_indexes.append(stroke.index)
                hit_rectangles.append(stroke.bbox)
        if hit_indexes:
            findings.append(
                CollisionFinding(
                    severity="FAIL",
                    kind="text-stroke",
                    page=page.page,
                    message=f"Text is crossed by {len(hit_indexes)} stroked path(s)",
                    text=text.text,
                    text_bbox=text.bbox,
                    other_bbox=union_rects(hit_rectangles),
                    object_count=len(hit_indexes),
                    object_indexes=tuple(hit_indexes),
                )
            )

    page_area = max(rect_area(page.bbox), 1.0)
    for regions, kind, info_key in (
        (page.fills, "text-fill-edge", "contained_fill_overlays"),
        (page.images, "text-image-edge", "contained_image_overlays"),
    ):
        for text in page.texts:
            partial_indexes: list[int] = []
            partial_rectangles: list[Rect] = []
            for region in regions:
                if rect_area(region.bbox) / page_area >= background_area_ratio:
                    continue
                ratio = rect_overlap_ratio(text.bbox, region.bbox)
                if ratio < min_overlap_ratio:
                    continue
                if rect_contains(region.bbox, text.bbox, tolerance=0.25):
                    info[info_key] += 1
                    continue
                partial_indexes.append(region.index)
                partial_rectangles.append(region.bbox)
            if partial_indexes:
                label = "filled region" if kind == "text-fill-edge" else "raster image"
                findings.append(
                    CollisionFinding(
                        severity="WARN",
                        kind=kind,
                        page=page.page,
                        message=f"Text partially overlaps the edge of {len(partial_indexes)} {label}(s)",
                        text=text.text,
                        text_bbox=text.bbox,
                        other_bbox=union_rects(partial_rectangles),
                        object_count=len(partial_indexes),
                        object_indexes=tuple(partial_indexes),
                    )
                )

    clipped_seen: set[tuple[str, tuple[int, int, int, int]]] = set()
    for trace in page.traces:
        if _outside_distance(trace.bbox, page.bbox) <= clipping_tolerance_pt:
            continue
        key = (trace.text, tuple(round(value * 10) for value in trace.bbox))
        if key in clipped_seen:
            continue
        clipped_seen.add(key)
        findings.append(
            CollisionFinding(
                severity="FAIL",
                kind="text-page-clipping",
                page=page.page,
                message="Text extends beyond the final PDF page boundary",
                text=trace.text,
                text_bbox=trace.bbox,
                other_bbox=page.bbox,
                object_indexes=(trace.index,),
            )
        )

    return sorted(findings, key=_finding_sort_key), info


def audit_geometries(
    pages: Sequence[PageGeometry],
    *,
    text_inset_pt: float = 0.6,
    min_overlap_ratio: float = 0.05,
    clipping_tolerance_pt: float = 0.5,
) -> dict[str, Any]:
    findings: list[CollisionFinding] = []
    contained_fill_overlays = 0
    contained_image_overlays = 0
    for page in pages:
        page_findings, info = audit_page_geometry(
            page,
            text_inset_pt=text_inset_pt,
            min_overlap_ratio=min_overlap_ratio,
            clipping_tolerance_pt=clipping_tolerance_pt,
        )
        findings.extend(page_findings)
        contained_fill_overlays += info["contained_fill_overlays"]
        contained_image_overlays += info["contained_image_overlays"]

    fail_count = sum(finding.severity == "FAIL" for finding in findings)
    warn_count = sum(finding.severity == "WARN" for finding in findings)
    visible_text_count = sum(len(page.texts) for page in pages)
    trace_count = sum(len(page.traces) for page in pages)
    auditable = visible_text_count > 0 or trace_count > 0
    verdict = (
        "NOT AUDITABLE"
        if not auditable
        else "FIX BEFORE DELIVERY"
        if fail_count
        else "REVIEW REQUIRED"
        if warn_count
        else "PASS"
    )
    return {
        "auditable": auditable,
        "verdict": verdict,
        "page_count": len(pages),
        "visible_text_box_count": visible_text_count,
        "text_trace_count": trace_count,
        "stroke_path_count": sum(len(page.strokes) for page in pages),
        "filled_region_count": sum(len(page.fills) for page in pages),
        "image_region_count": sum(len(page.images) for page in pages),
        "summary": {
            "fail": fail_count,
            "warn": warn_count,
            "contained_fill_overlays": contained_fill_overlays,
            "contained_image_overlays": contained_image_overlays,
        },
        "thresholds": {
            "text_inset_pt": text_inset_pt,
            "min_overlap_ratio": min_overlap_ratio,
            "clipping_tolerance_pt": clipping_tolerance_pt,
        },
        "findings": [asdict(finding) for finding in sorted(findings, key=_finding_sort_key)],
    }


def audit_pdf(
    path: Path,
    *,
    text_inset_pt: float = 0.6,
    min_overlap_ratio: float = 0.05,
    clipping_tolerance_pt: float = 0.5,
) -> dict[str, Any]:
    pages = extract_pdf_geometry(path)
    return {
        "pdf": str(path),
        **audit_geometries(
            pages,
            text_inset_pt=text_inset_pt,
            min_overlap_ratio=min_overlap_ratio,
            clipping_tolerance_pt=clipping_tolerance_pt,
        ),
    }


def write_overlay_pdf(source: Path, destination: Path, findings: Sequence[dict[str, Any]]) -> None:
    try:
        import pymupdf as fitz  # type: ignore
    except ImportError:
        try:
            import fitz  # type: ignore
        except ImportError as exc:
            raise RuntimeError("PyMuPDF is required to write the diagnostic overlay PDF") from exc
    if source.resolve() == destination.resolve():
        raise ValueError("overlay PDF must not overwrite the source PDF")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.stem}.",
        suffix=".tmp.pdf",
        dir=destination.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    temporary.unlink()
    try:
        document = fitz.open(source)
        try:
            for finding in findings:
                page_number = int(finding["page"]) - 1
                if not 0 <= page_number < len(document):
                    continue
                page = document[page_number]
                color = (0.9, 0.05, 0.05) if finding["severity"] == "FAIL" else (1.0, 0.55, 0.0)
                page.draw_rect(fitz.Rect(finding["text_bbox"]), color=color, width=1.2, overlay=True)
                other_bbox = finding.get("other_bbox")
                if other_bbox:
                    page.draw_rect(
                        fitz.Rect(other_bbox),
                        color=color,
                        width=0.6,
                        dashes="[2 2] 0",
                        overlay=True,
                    )
            document.save(temporary)
        finally:
            document.close()
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def render_text(result: dict[str, Any], strict: bool = False) -> str:
    summary = result["summary"]
    lines = [
        "Nature Figure Rendered Collision Audit",
        f"pdf: {result.get('pdf', '<geometry fixture>')}",
        f"pages: {result['page_count']}",
        f"visible text boxes: {result['visible_text_box_count']}",
        f"stroke paths: {result['stroke_path_count']}",
        "",
    ]
    for finding in result["findings"]:
        lines.append(
            f"[{finding['severity']}] page {finding['page']} {finding['kind']}: "
            f"{finding['message']} — {finding['text']!r}"
        )
        if finding.get("other_text"):
            lines.append(f"  other text: {finding['other_text']!r}")
        lines.append(f"  text bbox: {finding['text_bbox']}")
    lines.extend(
        [
            "",
            f"summary: {summary['fail']} fail, {summary['warn']} warn, "
            f"{summary['contained_fill_overlays']} contained fill overlays, "
            f"{summary['contained_image_overlays']} contained image overlays",
            f"verdict: {result['verdict']}",
            "note: contained overlays can be intentional; WARN findings need final-size visual review",
        ]
    )
    if strict and summary["warn"]:
        lines.append("strict verdict: FIX BEFORE DELIVERY (WARN is blocking)")
    return "\n".join(lines)


def exit_code(result: dict[str, Any], strict: bool = False) -> int:
    if not result["auditable"]:
        return 2
    summary = result["summary"]
    if summary["fail"] or (strict and summary["warn"]):
        return 1
    return 0


def run_self_tests() -> None:
    clean = PageGeometry(
        page=1,
        bbox=(0, 0, 200, 120),
        texts=[TextBox(0, "Clear", (50, 20, 90, 32))],
        traces=[TraceBox(0, "Clear", (50, 20, 90, 32))],
        strokes=[StrokePath(0, (20, 70, 180, 70), 1.0, (((20, 70), (180, 70)),))],
    )
    clean_result = audit_geometries([clean])
    assert clean_result["verdict"] == "PASS", clean_result

    crossed = PageGeometry(
        page=1,
        bbox=(0, 0, 200, 120),
        texts=[TextBox(0, "Crossed", (50, 40, 100, 54))],
        traces=[TraceBox(0, "Crossed", (50, 40, 100, 54))],
        strokes=[StrokePath(0, (20, 47, 180, 47), 1.0, (((20, 47), (180, 47)),))],
    )
    crossed_result = audit_geometries([crossed])
    assert crossed_result["verdict"] == "FIX BEFORE DELIVERY", crossed_result
    assert crossed_result["findings"][0]["kind"] == "text-stroke", crossed_result

    intentional_fill = PageGeometry(
        page=1,
        bbox=(0, 0, 200, 120),
        texts=[TextBox(0, "Inside", (60, 40, 90, 52))],
        traces=[TraceBox(0, "Inside", (60, 40, 90, 52))],
        fills=[FilledRegion(0, (50, 30, 100, 60), "fill")],
    )
    fill_result = audit_geometries([intentional_fill])
    assert fill_result["verdict"] == "PASS", fill_result
    assert fill_result["summary"]["contained_fill_overlays"] == 1, fill_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", nargs="?", type=Path, help="final exported PDF figure")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--json-out", type=Path, help="write a machine-readable JSON report")
    parser.add_argument("--overlay-pdf", type=Path, help="write a QA-only PDF with collision boxes")
    parser.add_argument("--strict", action="store_true", help="treat WARN findings as blocking")
    parser.add_argument("--text-inset-pt", type=float, default=0.6)
    parser.add_argument("--min-overlap-ratio", type=float, default=0.05)
    parser.add_argument("--clipping-tolerance-pt", type=float, default=0.5)
    parser.add_argument("--self-test", action="store_true", help="run dependency-free geometry tests")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        run_self_tests()
        print("audit_figure_collisions.py self-test: PASS")
        return 0
    if args.pdf is None:
        print("error: PDF path is required unless --self-test is used", file=sys.stderr)
        return 2
    for name, value in (
        ("--text-inset-pt", args.text_inset_pt),
        ("--min-overlap-ratio", args.min_overlap_ratio),
        ("--clipping-tolerance-pt", args.clipping_tolerance_pt),
    ):
        if value < 0 or not math.isfinite(value):
            print(f"error: {name} must be a finite non-negative number", file=sys.stderr)
            return 2
    if not 0 <= args.min_overlap_ratio <= 1:
        print("error: --min-overlap-ratio must be between 0 and 1", file=sys.stderr)
        return 2
    try:
        result = audit_pdf(
            args.pdf,
            text_inset_pt=args.text_inset_pt,
            min_overlap_ratio=args.min_overlap_ratio,
            clipping_tolerance_pt=args.clipping_tolerance_pt,
        )
        if args.json_out:
            args.json_out.parent.mkdir(parents=True, exist_ok=True)
            args.json_out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if args.overlay_pdf and result["findings"]:
            write_overlay_pdf(args.pdf, args.overlay_pdf, result["findings"])
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else render_text(result, args.strict))
    return exit_code(result, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
