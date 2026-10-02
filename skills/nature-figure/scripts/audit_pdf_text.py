#!/usr/bin/env python3
"""Audit text font sizes used by PDF content-stream ``Tf`` operators.

This dependency-free check catches reduced mathtext superscripts/subscripts and
other glyph runs that can fall below a journal font-size floor even when the
parent matplotlib ``fontsize`` is compliant. It supports plain and FlateDecode
content streams, which covers normal matplotlib PDF output.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path


STREAM_START = re.compile(rb"stream\r?\n")
TF_OPERATOR = re.compile(
    rb"/([^\s/<>]+)\s+([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)\s+Tf\b"
)


@dataclass(frozen=True)
class TextRun:
    stream: int
    font: str
    size_pt: float


def decoded_streams(data: bytes) -> tuple[list[bytes], list[str]]:
    streams: list[bytes] = []
    warnings: list[str] = []
    cursor = 0
    stream_number = 0
    while True:
        match = STREAM_START.search(data, cursor)
        if not match:
            break
        stream_number += 1
        end = data.find(b"endstream", match.end())
        if end < 0:
            warnings.append(f"stream {stream_number} has no endstream marker")
            break
        # Keep the raw stream bytes. zlib accepts PDF's trailing line break,
        # while stripping could accidentally remove a legitimate compressed
        # byte that happens to equal CR or LF.
        payload = data[match.end() : end]
        header = data[max(0, match.start() - 2048) : match.start()]
        dictionary_start = header.rfind(b"<<")
        dictionary = header[dictionary_start:] if dictionary_start >= 0 else header
        if b"/FlateDecode" in dictionary:
            try:
                payload = zlib.decompress(payload)
            except zlib.error as exc:
                warnings.append(f"stream {stream_number} FlateDecode failed: {exc}")
                cursor = end + len(b"endstream")
                continue
        elif b"/Filter" in dictionary:
            warnings.append(f"stream {stream_number} uses an unsupported PDF filter")
            cursor = end + len(b"endstream")
            continue
        streams.append(payload)
        cursor = end + len(b"endstream")
    return streams, warnings


def audit_pdf(data: bytes, minimum_pt: float = 5.0) -> dict[str, object]:
    streams, warnings = decoded_streams(data)
    runs: list[TextRun] = []
    for stream_index, stream in enumerate(streams, 1):
        for match in TF_OPERATOR.finditer(stream):
            try:
                font = match.group(1).decode("ascii", errors="replace")
                size = float(match.group(2))
            except ValueError:
                continue
            if size > 0:
                runs.append(TextRun(stream=stream_index, font=font, size_pt=size))
    below = [run for run in runs if run.size_pt < minimum_pt]
    return {
        "auditable": bool(runs),
        "minimum_required_pt": minimum_pt,
        "minimum_found_pt": min((run.size_pt for run in runs), default=None),
        "text_run_count": len(runs),
        "below_minimum_count": len(below),
        "below_minimum": [asdict(run) for run in below],
        "warnings": warnings,
    }


def render_text(path: Path, result: dict[str, object]) -> str:
    lines = [
        "Nature Figure PDF Text Audit",
        f"pdf: {path}",
        f"minimum required: {result['minimum_required_pt']:g} pt",
    ]
    if not result["auditable"]:
        lines.append("verdict: NOT AUDITABLE — no supported Tf text operators were found")
    else:
        lines.extend(
            [
                f"minimum found: {result['minimum_found_pt']:g} pt",
                f"text runs: {result['text_run_count']}",
                f"below minimum: {result['below_minimum_count']}",
                f"verdict: {'FAIL' if result['below_minimum_count'] else 'PASS'}",
            ]
        )
    for run in result["below_minimum"]:
        lines.append(f"  - stream {run['stream']}: /{run['font']} {run['size_pt']:g} Tf")
    for warning in result["warnings"]:
        lines.append(f"warning: {warning}")
    lines.append("note: Tf scanning does not replace final-size visual inspection or account for every PDF transform")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="exported PDF figure")
    parser.add_argument("--min-pt", type=float, default=5.0, help="minimum allowed Tf font size in points")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.min_pt <= 0:
        print("error: --min-pt must be positive", file=sys.stderr)
        return 2
    try:
        data = args.pdf.read_bytes()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not data.startswith(b"%PDF-"):
        print(f"error: not a PDF file: {args.pdf}", file=sys.stderr)
        return 2
    result = audit_pdf(data, minimum_pt=args.min_pt)
    if args.json:
        print(json.dumps({"pdf": str(args.pdf), **result}, indent=2, ensure_ascii=False))
    else:
        print(render_text(args.pdf, result))
    if not result["auditable"]:
        return 2
    return 1 if result["below_minimum_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
