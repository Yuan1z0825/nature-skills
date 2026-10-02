#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def configure_utf8_stdio():
    """Keep Chinese paths/text printable in Windows PowerShell and Claude Code terminals."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def extract_with_pdfplumber(pdf_path, max_pages):
    import pdfplumber

    chunks = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        page_count = len(pdf.pages)
        pages = pdf.pages if max_pages is None else pdf.pages[:max_pages]
        for i, page in enumerate(pages, start=1):
            chunks.append(f"\n\n===== PAGE {i} =====\n")
            chunks.append(page.extract_text() or "")
    return page_count, "".join(chunks)


def extract_with_pypdf(pdf_path, max_pages):
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    page_count = len(reader.pages)
    pages = reader.pages if max_pages is None else reader.pages[:max_pages]
    chunks = []
    for i, page in enumerate(pages, start=1):
        chunks.append(f"\n\n===== PAGE {i} =====\n")
        chunks.append(page.extract_text() or "")
    return page_count, "".join(chunks)


def main():
    configure_utf8_stdio()

    parser = argparse.ArgumentParser(description="Extract text from a downloaded PDF for verification or reading.")
    parser.add_argument("--pdf", required=True, help="Path to PDF")
    parser.add_argument("--out", help="Optional output .txt path")
    parser.add_argument("--pages", type=int, default=3, help="Number of pages to extract; use 0 for all pages")
    parser.add_argument("--json", action="store_true", help="Print JSON metadata instead of text preview")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    max_pages = None if args.pages == 0 else args.pages

    try:
        page_count, text = extract_with_pdfplumber(pdf_path, max_pages)
        engine = "pdfplumber"
    except Exception:
        page_count, text = extract_with_pypdf(pdf_path, max_pages)
        engine = "pypdf"

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")

    meta = {
        "pdf": str(pdf_path.resolve()),
        "pages_total": page_count,
        "pages_extracted": page_count if max_pages is None else min(max_pages, page_count),
        "chars": len(text),
        "engine": engine,
        "out": str(Path(args.out).resolve()) if args.out else None,
    }

    if args.json:
        print(json.dumps(meta, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(meta, ensure_ascii=False))
        print(text[:4000])


if __name__ == "__main__":
    main()
