#!/usr/bin/env python3
"""Audit effective text sizes in PDF content streams.

The size is ``Tf`` size scaled by the text matrix (``Tm``) and ``cm`` transforms.

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
TOKEN = re.compile(
    rb"%[^\r\n]*"  # comment
    rb"|\((?:\\.|[^\\()])*\)"  # literal string (no nested parentheses)
    rb"|<<|>>|<[0-9A-Fa-f\s]*>"  # dict delimiters / hex string
    rb"|[\[\]]"
    rb"|/[^\s/<>\[\]()%]*"  # name
    rb"|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?"  # number
    rb"|[^\s/<>\[\]()%]+",  # operator
    re.S,
)
NUMBER = re.compile(rb"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?$")
SHOW_OPERATORS = {b"Tj", b"TJ", b"'", b'"'}
IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def multiply(first: tuple[float, ...], second: tuple[float, ...]) -> tuple[float, ...]:
    """Return ``first x second`` for PDF row-vector matrices ``[a b c d e f]``."""
    a1, b1, c1, d1, e1, f1 = first
    a2, b2, c2, d2, e2, f2 = second
    return (
        a1 * a2 + b1 * c2,
        a1 * b2 + b1 * d2,
        c1 * a2 + d1 * c2,
        c1 * b2 + d1 * d2,
        e1 * a2 + f1 * c2 + e2,
        e1 * b2 + f1 * d2 + f2,
    )


def matrix_scale(matrix: tuple[float, ...]) -> float:
    """Isotropic scale factor of the linear part (square root of |det|)."""
    return abs(matrix[0] * matrix[3] - matrix[1] * matrix[2]) ** 0.5


@dataclass(frozen=True)
class TextRun:
    stream: int
    font: str
    size_pt: float


def scan_text_runs(stream: bytes, stream_index: int) -> list[TextRun]:
    """Return glyph runs with the effective size ``Tf size x Tm x CTM``.

    Runs are recorded when text is shown, so a ``Tm`` that follows ``Tf`` (as in
    Cairo output using ``1 Tf``) is applied to the size.
    """
    runs: list[TextRun] = []
    operands: list[bytes] = []
    ctm = IDENTITY
    ctm_stack: list[tuple[float, ...]] = []
    text_matrix = IDENTITY
    font = ""
    font_size = 0.0
    last: tuple[str, float] | None = None
    for match in TOKEN.finditer(stream):
        token = match.group(0)
        if token.startswith(b"%"):
            continue
        if token.startswith(b"("):
            operands.append(b"(")
            continue
        if token[:1] in (b"/", b"[", b"]", b"<") or NUMBER.match(token):
            operands.append(token)
            continue
        operator = token
        if operator == b"q":
            ctm_stack.append(ctm)
        elif operator == b"Q":
            if ctm_stack:
                ctm = ctm_stack.pop()
        elif operator == b"cm" and len(operands) >= 6:
            try:
                values = tuple(float(value) for value in operands[-6:])
            except ValueError:
                values = None
            if values:
                ctm = multiply(values, ctm)
        elif operator == b"BT":
            text_matrix = IDENTITY
        elif operator == b"Tm" and len(operands) >= 6:
            try:
                text_matrix = tuple(float(value) for value in operands[-6:])
            except ValueError:
                pass
        elif operator == b"Tf" and len(operands) >= 2:
            try:
                font = operands[-2].lstrip(b"/").decode("ascii", errors="replace")
                font_size = float(operands[-1])
            except ValueError:
                pass
        elif operator in SHOW_OPERATORS:
            size = abs(font_size) * matrix_scale(multiply(text_matrix, ctm))
            if size > 0 and last != (font, size):
                runs.append(TextRun(stream=stream_index, font=font, size_pt=size))
                last = (font, size)
        operands.clear()
    return runs


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
        runs.extend(scan_text_runs(stream, stream_index))
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
        lines.append("verdict: NOT AUDITABLE — no supported text-showing operators were found")
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
        lines.append(f"  - stream {run['stream']}: /{run['font']} {run['size_pt']:g} pt")
    for warning in result["warnings"]:
        lines.append(f"warning: {warning}")
    lines.append("note: content-stream scanning does not replace final-size visual inspection or account for every PDF transform (e.g. Form XObject matrices)")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="exported PDF figure")
    parser.add_argument("--min-pt", type=float, default=5.0, help="minimum allowed effective font size in points")
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
