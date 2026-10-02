#!/usr/bin/env python3
"""Generate text hints for every page of a prepared run.

Runs as part of `image2ppt prepare`, after page directories exist: each
`pages/page_NNN/` receives canonical `text_hints.json` and `text_hints.png`
files so page workers find their text measurements already in place.

Backend selection per run:
- With a PaddleOCR token (PADDLE_OCR_TOKEN env var, or PADDLE_OCR_TOKEN in the
  active config.yaml): an original PDF is submitted as one multi-page job;
  image and PPTX inputs submit each normalized source.png as its own job.
  OCR coordinates are rescaled to each page's actual source.png resolution
  and re-measured locally with the ink metrics.
- Without a token, or when the service fails: the built-in offline detector
  (`text_hints.py`) runs per page, so every page still gets hints.

Hint generation is best-effort: a page that fails is reported and skipped,
and the page worker can regenerate with `image2ppt page hints <page_dir>`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from PIL import Image

from deck_run_state import load_deck, load_jobs, page_dir_for, run_dir_from_target
from text_hints import draw_overlay, page_text_hints

HINTS_JSON = "text_hints.json"
HINTS_PNG = "text_hints.png"


def paddle_token() -> str:
    token = os.environ.get("PADDLE_OCR_TOKEN", "").strip()
    if token:
        return token
    try:
        from runtime_env import config_path, read_config_file

        return str(read_config_file(config_path()).get("PADDLE_OCR_TOKEN", "")).strip()
    except Exception:
        return ""


def write_hints(page_dir: Path, hints: dict, overlay: bool) -> None:
    (page_dir / HINTS_JSON).write_text(json.dumps(hints, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if overlay:
        draw_overlay(Image.open(page_dir / "source.png"), hints["lines"], page_dir / HINTS_PNG)


def builtin_page(page_dir: Path) -> dict:
    hints = page_text_hints(page_dir)
    hints["backend"] = "builtin-ink"
    return hints


def paddle_pages(run_dir: Path, deck: dict, page_dirs: list[Path], token: str, timeout: int) -> dict[Path, dict]:
    """Fetch OCR results without converting normalized images to a PDF."""
    from paddle_text_hints import DEFAULT_MODEL, build_page_hints, submit_and_fetch

    original_pdf = None
    if str(deck.get("input_type", "")) == "pdf":
        input_dir = run_dir / "input"
        candidates = sorted(input_dir.glob("*.pdf")) if input_dir.exists() else []
        original_pdf = candidates[0] if candidates else None

    if original_pdf is not None:
        pages = submit_and_fetch(original_pdf, token, DEFAULT_MODEL, timeout)
        if len(pages) != len(page_dirs):
            raise RuntimeError(f"OCR returned {len(pages)} pages for {len(page_dirs)} page dirs")
        return {page_dir: build_page_hints(page_dir, pruned) for page_dir, pruned in zip(page_dirs, pages)}

    results = {}
    for page_dir in page_dirs:
        pages = submit_and_fetch(page_dir / "source.png", token, DEFAULT_MODEL, timeout)
        if len(pages) != 1:
            raise RuntimeError(f"OCR returned {len(pages)} pages for {page_dir.name}; expected 1")
        results[page_dir] = build_page_hints(page_dir, pages[0])
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate per-page text hints for a prepared run.")
    parser.add_argument("run", help="Run directory or deck_manifest.json path.")
    parser.add_argument("--timeout", type=int, default=300, help="OCR job timeout in seconds.")
    parser.add_argument("--no-overlay", action="store_true", help="Skip the labeled overlay images.")
    args = parser.parse_args()

    run_dir = run_dir_from_target(args.run)
    deck = load_deck(run_dir)
    jobs = load_jobs(run_dir)
    page_dirs = [page_dir_for(run_dir, page) for page in jobs.get("pages", [])]
    page_dirs = [d for d in page_dirs if (d / "source.png").exists()]
    if not page_dirs:
        print("text-hints: no pages with source.png; skipped", file=sys.stderr)
        return 0

    token = paddle_token()
    results: dict[Path, dict] = {}
    backend = "builtin-ink"
    if not token:
        print(
            "text-hints: no PaddleOCR token configured; falling back to the built-in offline "
            "detector (geometry only — it measures where text is and how large, but cannot read "
            "it). A free PaddleOCR-VL token adds recognized text content and cleaner block "
            "boundaries, noticeably improving text fidelity in the final PPT. The free personal quota "
            "is currently more than enough for this skill, so applying is risk-free with no extra "
            "cost. ASK THE USER once "
            "before reconstructing pages: configure a token now (apply at "
            "https://aistudio.baidu.com/account/accessToken, then `image2ppt config "
            "--paddle-ocr-token <token>` and `image2ppt run hints <run>` to regenerate this run's "
            "hints), or continue with the offline result. Respect their choice and do not ask again.",
            file=sys.stderr,
        )
    if token:
        try:
            results = paddle_pages(run_dir, deck, page_dirs, token, args.timeout)
            backend = "paddleocr-vl"
        except Exception as exc:
            print(f"text-hints: PaddleOCR failed ({exc}); falling back to built-in detector", file=sys.stderr)
            results = {}

    written = 0
    for page_dir in page_dirs:
        try:
            hints = results.get(page_dir) or builtin_page(page_dir)
            # Dense diagrams can defeat the OCR layout model entirely (the
            # whole figure is classified as an image and only a headline
            # survives). When OCR found almost nothing but the offline
            # detector finds plenty, the geometric hints are more useful.
            if hints.get("backend") == "paddleocr-vl" and len(hints["lines"]) <= 2:
                offline = builtin_page(page_dir)
                if len(offline["lines"]) >= 6:
                    print(
                        f"text-hints: {page_dir.name}: OCR found {len(hints['lines'])} text lines but the "
                        f"offline detector found {len(offline['lines'])}; using the offline result for this page",
                        file=sys.stderr,
                    )
                    hints = offline
            write_hints(page_dir, hints, overlay=not args.no_overlay)
            written += 1
        except Exception as exc:
            print(f"text-hints: {page_dir.name} failed ({exc}); worker can run `image2ppt page hints` itself", file=sys.stderr)
    print(f"text-hints: wrote {written}/{len(page_dirs)} pages (backend={backend})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
