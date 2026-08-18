#!/usr/bin/env python3
"""Text hints backed by the PaddleOCR-VL cloud API (experimental).

Same contract as `text_hints.py`, with a different detector: the page is sent
to the PaddleOCR-VL service, only TEXT blocks (text / paragraph_title /
vision_footnote) are kept from the layout parsing result, and each block is
then re-measured locally with the ink metrics so the reported glyph height
and font size stay pixel-accurate. Output: `paddle_hints.json` plus a labeled
`paddle_hints.png` overlay on the source image.

Requires network access and a token in the PADDLE_OCR_TOKEN environment
variable (or --token). The built-in `image2ppt page hints` stays the offline
default; this script is the content-aware alternative.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from PIL import Image

from deck_run_state import resolve_inside
from page_text_metrics import contains_cjk, load_gray, measure_crop
from text_hints import attach_font_sizes, draw_overlay

JOB_URL = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
DEFAULT_MODEL = "PaddleOCR-VL-1.6"
TEXT_LABELS = {"text", "paragraph_title", "vision_footnote"}
USAGE_NOTE = (
    "ADVISORY ONLY: these measurements are a reference, and some text lines may be "
    "missed or merged. Lines sharing a size_group are the same text level and must "
    "use exactly one font size. When assembling the final PPT: keep same-level text "
    "at identical font sizes (apply the group's size to similar lines, including "
    "ones you add yourself), and fill in every text the detector missed from your "
    "own reading of the source image. box_px values are source pixels usable "
    "directly in text_boxes; font_pt is already chosen per line (CJK vs Latin). Add "
    "\"font_size_source\": \"measured\" to boxes you size from these hints. "
    "Recognition text may contain occasional wrong characters — trust your own "
    "reading of the source for the final text content."
)


def submit_and_fetch(file_path: Path, token: str, model: str, timeout: int) -> list[dict]:
    """Submit an image or multi-page PDF; return one prunedResult per page."""
    headers = {"Authorization": f"bearer {token}"}
    optional = {"useDocOrientationClassify": False, "useDocUnwarping": False, "useChartRecognition": False}
    with file_path.open("rb") as handle:
        response = requests.post(
            JOB_URL,
            headers=headers,
            data={"model": model, "optionalPayload": json.dumps(optional)},
            files={"file": handle},
            timeout=60,
        )
    if response.status_code != 200:
        raise RuntimeError(f"PaddleOCR job submit failed ({response.status_code}): {response.text[:300]}")
    job_id = response.json()["data"]["jobId"]
    print(f"job submitted: {job_id}", file=sys.stderr)

    started = time.time()
    while True:
        status = requests.get(f"{JOB_URL}/{job_id}", headers=headers, timeout=60).json()["data"]
        state = status["state"]
        if state == "done":
            break
        if state == "failed":
            raise RuntimeError(f"PaddleOCR job failed: {status.get('errorMsg')}")
        if time.time() - started > timeout:
            raise RuntimeError(f"PaddleOCR job timed out after {timeout}s (state={state})")
        time.sleep(5)

    jsonl = requests.get(status["resultUrl"]["jsonUrl"], timeout=60)
    jsonl.raise_for_status()
    pages = []
    for line in jsonl.text.strip().split("\n"):
        if not line.strip():
            continue
        for result in json.loads(line)["result"]["layoutParsingResults"]:
            pages.append(result["prunedResult"])
    if not pages:
        raise RuntimeError("PaddleOCR returned no pages")
    return pages


def text_blocks_to_lines(pruned: dict, gray, min_glyph: int,
                         scale_x: float = 1.0, scale_y: float = 1.0) -> list[dict]:
    """Keep text blocks only and re-measure each with local ink metrics.

    scale_x/scale_y map OCR-page coordinates onto the gray image when the OCR
    service rendered the page at a different resolution than source.png
    (typical for PDF inputs).
    """
    height, width = gray.shape
    lines = []
    for block in pruned.get("parsing_res_list", []):
        if block.get("block_label") not in TEXT_LABELS:
            continue
        text = str(block.get("block_content", "")).strip()
        bx1, by1, bx2, by2 = (float(v) for v in block["block_bbox"])
        x1, y1 = int(round(bx1 * scale_x)), int(round(by1 * scale_y))
        x2, y2 = int(round(bx2 * scale_x)), int(round(by2 * scale_y))
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(width, x2), min(height, y2)
        if x2 - x1 < 4 or y2 - y1 < 4:
            continue
        entry = {"text": text, "block_label": block.get("block_label")}
        measured = measure_crop(gray[y1:y2, x1:x2], clean_border=False)
        if measured["ok"] and measured["glyph_height_px"] >= min_glyph:
            glyph = measured["glyph_height_px"]
            bx, by, bw, bh = measured["bbox"]
            pad_x = max(2, int(round(glyph * 0.35)))
            pad_y = max(1, int(round(glyph * 0.30)))
            left = max(0, x1 + bx - pad_x)
            top = max(0, y1 + by - pad_y)
            entry.update(
                box_px=[left, top, min(width, x1 + bx + bw + pad_x) - left, min(height, y1 + by + bh + pad_y) - top],
                glyph_height_px=round(glyph, 1),
                line_count=measured["line_count"],
                glyph_source="ink-measured",
            )
        else:
            # Ink measurement failed (low contrast inside the block); fall
            # back to the OCR block box and approximate the glyph from it.
            line_count = max(1, text.count("\n") + 1)
            entry.update(
                box_px=[x1, y1, x2 - x1, y2 - y1],
                glyph_height_px=round((y2 - y1) / (line_count * 1.3), 1),
                line_count=line_count,
                glyph_source="bbox-estimate",
            )
        lines.append(entry)
    lines.sort(key=lambda line: (line["box_px"][1], line["box_px"][0]))
    for index, line in enumerate(lines, 1):
        line["id"] = f"P{index:02d}"
    return lines


def build_page_hints(page_dir: Path, pruned: dict, source_name: str = "source.png",
                     min_glyph: int = 6) -> dict:
    """Turn one page's prunedResult into the hints payload for its page dir."""
    source_path = resolve_inside(page_dir, source_name)
    gray = load_gray(source_path)
    height, width = gray.shape
    scale_x = width / float(pruned["width"]) if pruned.get("width") else 1.0
    scale_y = height / float(pruned["height"]) if pruned.get("height") else 1.0
    lines = text_blocks_to_lines(pruned, gray, min_glyph, scale_x, scale_y)

    manifest_like = {"source": {"width_px": width, "height_px": height}, "slide": {"width": 13.333, "height": 7.5}}
    request_path = page_dir / "page_request.json"
    if request_path.exists():
        request = json.loads(request_path.read_text(encoding="utf-8"))
        for key in ("slide", "content_box"):
            if request.get(key):
                manifest_like[key] = request[key]
    attach_font_sizes(lines, manifest_like)
    for line in lines:
        line["font_pt"] = line["font_pt_if_cjk"] if contains_cjk(line["text"]) else line["font_pt_if_latin"]
    return {
        "schema_version": 1,
        "backend": "paddleocr-vl",
        "source": {"width_px": width, "height_px": height},
        "lines": lines,
        "note": USAGE_NOTE,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Text hints via the PaddleOCR-VL cloud API: text blocks with content, re-measured locally for font sizes.",
    )
    parser.add_argument("page_dir", help="Page directory containing source.png.")
    parser.add_argument("--source", default="source.png", help="Source image relative to the page directory.")
    parser.add_argument("--out", default="paddle_hints.json", help="Hints JSON relative to the page directory.")
    parser.add_argument("--overlay", default="paddle_hints.png", help="Labeled overlay image. Pass an empty string to skip.")
    parser.add_argument("--token", default=os.environ.get("PADDLE_OCR_TOKEN", ""), help="API token; defaults to $PADDLE_OCR_TOKEN.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=int, default=300, help="Job polling timeout in seconds.")
    parser.add_argument("--min-glyph", type=int, default=6)
    args = parser.parse_args()

    if not args.token:
        raise SystemExit("Missing token: set PADDLE_OCR_TOKEN or pass --token.")
    page_dir = Path(args.page_dir).expanduser().resolve()
    try:
        source_path = resolve_inside(page_dir, args.source)
        out_path = resolve_inside(page_dir, args.out)
        overlay_path = resolve_inside(page_dir, args.overlay) if args.overlay else None
    except ValueError as exc:
        raise SystemExit(f"OCR hint paths must stay inside page_dir: {exc}") from exc
    if not source_path.exists():
        raise SystemExit(f"Missing source image: {source_path}")

    started = time.time()
    try:
        pages = submit_and_fetch(source_path, args.token, args.model, args.timeout)
    except RuntimeError as exc:
        raise SystemExit(str(exc))
    hints = build_page_hints(page_dir, pages[0], source_name=args.source, min_glyph=args.min_glyph)
    hints["elapsed_seconds"] = round(time.time() - started, 1)
    lines = hints["lines"]
    out_path.write_text(json.dumps(hints, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if overlay_path:
        draw_overlay(Image.open(source_path), lines, overlay_path)
        hints["overlay"] = args.overlay
    print(json.dumps({"lines": len(lines), "elapsed_seconds": hints["elapsed_seconds"],
                      "out": str(out_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
