#!/usr/bin/env python3
"""Measure text line boxes and font sizes from source.png as advisory hints.

Run BEFORE writing the page manifest. The output is a reference, not a
mutation: the page author reads `text_hints.json` (or looks at the labeled
`text_hints.png` overlay), matches each detected line to the text it can read
in the source, and copies the measured `box_px` and font size into
`text_boxes`. Boxes sized from these measurements should carry
`"font_size_source": "measured"` so the deterministic builder trusts the size
instead of applying its conservative shrink.

Detection is classical and dependency-free: per-tile binarization, recursive
XY-cut layout segmentation, then per-leaf ink measurement (glyph height, line
count). Solid regions (photos, color blocks) and line-like bands (dividers)
are filtered out. Detection is advisory — missed or mis-grouped lines are
filled by the author's own reading of the source image. Known limitation:
small text sharing a row band with a much taller graphic can be swallowed by
the band-relative column gap threshold and go unreported.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from build_pptx_from_manifest import choose_preview_font, content_box_for_manifest
from deck_run_state import resolve_inside
from page_text_metrics import crop_ink_mask, despeckle, glyph_em_ratio, load_gray, measure_crop


TILE = 96
MIN_GLYPH_PX = 6
MAX_TEXT_FILL = 0.65
CJK_EM_RATIO = glyph_em_ratio("中")
LATIN_EM_RATIO = glyph_em_ratio("A1")


def binarize_page(gray: np.ndarray, tile: int = TILE) -> np.ndarray:
    """Assemble a page ink mask from per-tile local binarization.

    Local Otsu adapts to dark cards versus light page background; tiles whose
    binarization is unreliable (photos, gradients) contribute no ink.
    """
    height, width = gray.shape
    mask = np.zeros((height, width), dtype=bool)
    for top in range(0, height, tile):
        for left in range(0, width, tile):
            crop = gray[top : top + tile, left : left + tile]
            ink = crop_ink_mask(crop)
            if ink["reliable"]:
                mask[top : top + crop.shape[0], left : left + crop.shape[1]] = ink["mask"]
    return despeckle(mask)


def split_runs(profile: np.ndarray, min_gap: int) -> list[tuple[int, int]]:
    """Split a 1-D has-ink profile into runs separated by gaps >= min_gap."""
    index = np.flatnonzero(profile)
    if index.size == 0:
        return []
    breaks = np.flatnonzero(np.diff(index) > min_gap)
    starts = [int(index[0]), *(int(index[i + 1]) for i in breaks)]
    ends = [*(int(index[i]) + 1 for i in breaks), int(index[-1]) + 1]
    return list(zip(starts, ends))


# Gap tolerances are asymmetric. Rows: a small absolute tolerance, so a thin
# vertical line crossing a blank band still reads as a gap while sparse small
# text (a 12px label has only ~25 ink px per row) survives. Columns: relative
# to the row band height, so connectors shorter than a quarter of the band
# (arrows between cards, dashes) no longer bridge blocks, while real glyph
# columns — which fill most of the band — stay solid.
ROW_GAP_ABS_FRACTION = 0.003
COL_GAP_BAND_FRACTION = 0.25


def xy_cut(mask: np.ndarray, x0: int, y0: int, min_gap_y: int, min_gap_x: int,
           boxes: list, depth: int = 0) -> None:
    """Recursive XY-cut: alternate row/column gap splits until leaves remain."""
    if not mask.any():
        return
    height, width = mask.shape
    row_ink = mask.sum(axis=1) > max(2, ROW_GAP_ABS_FRACTION * width)
    rows = split_runs(row_ink, min_gap_y) or [(0, height)]
    if len(rows) > 1 and depth < 16:
        for top, bottom in rows:
            xy_cut(mask[top:bottom, :], x0, y0 + top, min_gap_y, min_gap_x, boxes, depth + 1)
        return
    top, bottom = rows[0]
    column_ink = mask[top:bottom, :].sum(axis=0) > max(2, COL_GAP_BAND_FRACTION * (bottom - top))
    columns = split_runs(column_ink, min_gap_x) or [(0, width)]
    if len(columns) > 1 and depth < 16:
        for left, right in columns:
            xy_cut(mask[top:bottom, left:right], x0 + left, y0 + top, min_gap_y, min_gap_x, boxes, depth + 1)
        return
    left, right = columns[0]
    boxes.append((x0 + left, y0 + top, right - left, bottom - top))


def measure_leaves(gray: np.ndarray, page_mask: np.ndarray, boxes: list, min_glyph: int) -> list[dict]:
    """Re-measure each leaf on the grayscale source and keep text-like ones."""
    height, width = gray.shape
    lines = []
    for x, y, w, h in boxes:
        if w < min_glyph or h < min_glyph:
            continue
        # Pre-check solidity on the polarity-correct page mask: photo rims and
        # color-block slices are near-solid there, while the local re-measure
        # below can flip polarity around them and mistake their light border
        # for glyphs.
        if float(page_mask[y : y + h, x : x + w].mean()) > MAX_TEXT_FILL:
            continue
        pad = 3
        left, top = max(0, x - pad), max(0, y - pad)
        right, bottom = min(width, x + w + pad), min(height, y + h + pad)
        measured = measure_crop(gray[top:bottom, left:right], clean_border=False)
        if not measured["ok"]:
            continue
        glyph = measured["glyph_height_px"]
        if glyph < min_glyph:
            continue
        bx, by, bw, bh = measured["bbox"]
        fill = float(measured["mask"][by : by + bh, bx : bx + bw].mean())
        if fill > MAX_TEXT_FILL:
            continue  # solid region: photo, color block, badge silhouette
        if glyph > bw + 2:
            continue  # taller than wide: a graphic blob, not a horizontal text line
        # Pad the tight ink box so it is directly usable as a text_boxes
        # box_px: the builder's line-height fit needs ~1.22x the font size of
        # box height, so a tight box would force the font smaller than the
        # source. Padding: 0.30 glyph vertically, 0.35 glyph horizontally.
        pad_x = max(2, int(round(glyph * 0.35)))
        pad_y = max(1, int(round(glyph * 0.30)))
        box_left = max(0, left + bx - pad_x)
        box_top = max(0, top + by - pad_y)
        lines.append(
            {
                "box_px": [
                    box_left,
                    box_top,
                    min(width, left + bx + bw + pad_x) - box_left,
                    min(height, top + by + bh + pad_y) - box_top,
                ],
                "glyph_height_px": round(glyph, 1),
                "line_count": measured["line_count"],
            }
        )
    return lines


# Same-level text in a design uses one font size; measured glyph heights
# jitter a few percent from glyph content and antialiasing (<=3%), while
# design type scales step >=8% between levels. Groups split where the sorted
# values jump by more than MIN_LEVEL_GAP; a group that still spans more than
# MAX_GROUP_SPREAD is force-split at its largest internal jump.
SIZE_GROUP_MIN_LEVEL_GAP = 0.05
SIZE_GROUP_MAX_SPREAD = 1.12


def cluster_glyph_heights(values: list[float], min_gap: float = SIZE_GROUP_MIN_LEVEL_GAP,
                          max_spread: float = SIZE_GROUP_MAX_SPREAD) -> list[list[int]]:
    """Group indices of similar values, splitting at relative jumps."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    groups: list[list[int]] = [[order[0]]] if order else []
    for index in order[1:]:
        previous = values[groups[-1][-1]]
        if previous > 0 and values[index] / previous > 1 + min_gap:
            groups.append([index])
        else:
            groups[-1].append(index)

    final: list[list[int]] = []
    for group in groups:
        stack = [group]
        while stack:
            current = stack.pop()
            lo, hi = values[current[0]], values[current[-1]]
            if len(current) < 2 or lo <= 0 or hi / lo <= max_spread:
                final.append(current)
                continue
            jumps = [values[current[i + 1]] / max(values[current[i]], 0.1) for i in range(len(current) - 1)]
            cut = jumps.index(max(jumps)) + 1
            stack.append(current[:cut])
            stack.append(current[cut:])
    return final


def attach_font_sizes(lines: list[dict], manifest_like: dict) -> None:
    source_height = float(manifest_like["source"]["height_px"])
    content_box = content_box_for_manifest(manifest_like)
    inches_per_px = float(content_box["height"]) / source_height
    if not lines:
        return
    glyphs = [line["glyph_height_px"] for line in lines]
    clusters = cluster_glyph_heights(glyphs)
    # Stable group ids ordered by size, largest first.
    clusters.sort(key=lambda cluster: -glyphs[cluster[0]])
    for group_number, cluster in enumerate(clusters, 1):
        members = sorted(glyphs[i] for i in cluster)
        median = members[len(members) // 2]
        glyph_in = median * inches_per_px
        cjk_pt = round(glyph_in / CJK_EM_RATIO * 72 * 2) / 2
        latin_pt = round(glyph_in / LATIN_EM_RATIO * 72 * 2) / 2
        for index in cluster:
            lines[index]["size_group"] = f"g{group_number}"
            lines[index]["group_glyph_px"] = median
            lines[index]["font_pt_if_cjk"] = cjk_pt
            lines[index]["font_pt_if_latin"] = latin_pt


def draw_overlay(source: Image.Image, lines: list[dict], out_path: Path) -> None:
    overlay = source.convert("RGB")
    draw = ImageDraw.Draw(overlay)
    font_path = choose_preview_font(None)
    label_size = max(14, source.size[0] // 90)
    try:
        font = ImageFont.truetype(font_path, size=label_size) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    for line in lines:
        x, y, w, h = line["box_px"]
        draw.rectangle([x, y, x + w, y + h], outline="#e02020", width=2)
        label_pt = line.get("font_pt") or line["font_pt_if_cjk"]
        label = f"{line['id']} {label_pt}pt"
        if line["line_count"] > 1:
            label += f" x{line['line_count']}"
        ly = y - label_size - 4 if y > label_size + 6 else y + h + 2
        text_w = draw.textlength(label, font=font)
        draw.rectangle([x, ly - 1, x + text_w + 4, ly + label_size + 3], fill="#fff7cc")
        draw.text((x + 2, ly), label, fill="#b00000", font=font)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(out_path)


def page_text_hints(page_dir: Path, source_name: str = "source.png",
                    min_glyph: int = MIN_GLYPH_PX) -> dict:
    source_path = resolve_inside(page_dir, source_name)
    if not source_path.exists():
        raise SystemExit(f"Missing source image: {source_path}")
    gray = load_gray(source_path)
    height, width = gray.shape

    request_path = page_dir / "page_request.json"
    manifest_like = {"source": {"width_px": width, "height_px": height}, "slide": {"width": 13.333, "height": 7.5}}
    if request_path.exists():
        request = json.loads(request_path.read_text(encoding="utf-8"))
        for key in ("slide", "content_box"):
            if request.get(key):
                manifest_like[key] = request[key]

    mask = binarize_page(gray)
    min_gap_y = max(6, round(height * 0.008))
    min_gap_x = max(14, round(width * 0.011))
    boxes: list = []
    xy_cut(mask, 0, 0, min_gap_y, min_gap_x, boxes)
    lines = measure_leaves(gray, mask, boxes, min_glyph)
    lines.sort(key=lambda line: (line["box_px"][1], line["box_px"][0]))
    for index, line in enumerate(lines, 1):
        line["id"] = f"L{index:02d}"
    attach_font_sizes(lines, manifest_like)

    return {
        "schema_version": 1,
        "backend": "builtin-ink",
        "source": {"width_px": width, "height_px": height},
        "lines": lines,
        "note": (
            "ADVISORY ONLY: these measurements are a reference, and some text lines may be "
            "missed or merged with graphics. Lines sharing a size_group are the same text "
            "level and must use exactly one font size. When assembling the final PPT: keep "
            "same-level text at identical font sizes (apply the group's size to similar "
            "lines, including ones you add yourself), and fill in every text the detector "
            "missed from your own reading of the source image. box_px values are source "
            "pixels usable directly in text_boxes. Pick font_pt_if_cjk for CJK text and "
            "font_pt_if_latin for Latin text, and add \"font_size_source\": \"measured\" "
            "to boxes you size from these hints."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure text line boxes and font sizes from source.png as advisory hints for the page author.",
    )
    parser.add_argument("page_dir", help="Page directory containing source.png.")
    parser.add_argument("--source", default="source.png", help="Source image relative to the page directory.")
    parser.add_argument("--out", default="text_hints.json", help="Hints JSON relative to the page directory.")
    parser.add_argument("--overlay", default="text_hints.png", help="Labeled overlay image. Pass an empty string to skip.")
    parser.add_argument("--min-glyph", type=int, default=MIN_GLYPH_PX, help="Smallest glyph height in px to report. Default: 6.")
    args = parser.parse_args()

    page_dir = Path(args.page_dir).expanduser().resolve()
    hints = page_text_hints(page_dir, source_name=args.source, min_glyph=args.min_glyph)

    try:
        source_path = resolve_inside(page_dir, args.source)
        out_path = resolve_inside(page_dir, args.out)
        overlay_path = resolve_inside(page_dir, args.overlay) if args.overlay else None
    except ValueError as exc:
        raise SystemExit(f"Text-hint paths must stay inside page_dir: {exc}") from exc
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(hints, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if overlay_path:
        source = Image.open(source_path)
        draw_overlay(source, hints["lines"], overlay_path)
        hints["overlay"] = args.overlay
    print(json.dumps(hints, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
