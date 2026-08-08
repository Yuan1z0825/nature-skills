#!/usr/bin/env python3
"""Validate equation rendering and traceability in a nature-reader bundle."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


EQUATION_ID_RE = re.compile(r"^E\d{3,}$")
EQUATION_ANCHOR_RE = re.compile(
    r"<a\s+(?:id|name)=[\"'](E\d{3,})[\"']\s*></a>", re.IGNORECASE
)
GENERIC_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})([^\n]*)$", re.MULTILINE)
LATEX_COMMAND_RE = re.compile(
    r"\\(?:frac|dfrac|tfrac|sum|prod|int|oint|sqrt|begin|end|left|right|"
    r"alpha|beta|gamma|delta|theta|lambda|mu|sigma|omega|partial|nabla|"
    r"mathcal|mathrm|mathbf|operatorname|overline|underline|widetilde|hat)\b"
)
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*]\(([^)]+)\)")
CHINESE_LINE_RE = re.compile(
    r"^\s*\*\*中文(?:说明|图注)?[:：]\*\*.*$", re.MULTILINE
)
PAREN_PSEUDO_MATH_RE = re.compile(
    r"\((?:[^()\n]*\\[A-Za-z]+[^()\n]*|"
    r"[A-Za-z][A-Za-z0-9]*_(?:\{[^}]+\}|[A-Za-z0-9]+)|"
    r"[^()\n]*=[^()\n]*)\)"
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    line: int | None = None


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def mask_ranges(text: str, ranges: list[tuple[int, int]]) -> str:
    chars = list(text)
    for start, end in ranges:
        for index in range(max(0, start), min(len(chars), end)):
            if chars[index] != "\n":
                chars[index] = " "
    return "".join(chars)


def fenced_ranges(
    text: str,
) -> tuple[list[tuple[int, int]], list[tuple[int, int]], list[Finding]]:
    """Return all fenced ranges, math-fence ranges, and fence errors."""
    ranges: list[tuple[int, int]] = []
    math_ranges: list[tuple[int, int]] = []
    findings: list[Finding] = []
    open_fence: tuple[str, int, int, int, bool] | None = None

    for match in GENERIC_FENCE_RE.finditer(text):
        marker = match.group(1)
        if open_fence is None:
            language = match.group(2).strip().split(maxsplit=1)[0].lower() if match.group(2).strip() else ""
            open_fence = (marker[0], len(marker), match.start(), match.end(), language in {"math", "latex"})
            continue
        char, length, start, body_start, is_math = open_fence
        if marker[0] == char and len(marker) >= length:
            ranges.append((start, match.end()))
            if is_math:
                math_ranges.append((start, match.end()))
                if not text[body_start : match.start()].strip():
                    findings.append(
                        Finding(
                            "FAIL",
                            "EMPTY_DISPLAY_MATH",
                            "Fenced math block is empty.",
                            line_number(text, start),
                        )
                    )
            open_fence = None

    if open_fence is not None:
        findings.append(
            Finding(
                "FAIL",
                "UNCLOSED_FENCE",
                "Markdown contains an unclosed fenced code/math block.",
                line_number(text, open_fence[2]),
            )
        )
        ranges.append((open_fence[2], len(text)))
    return ranges, math_ranges, findings


def display_math_ranges(text: str) -> tuple[list[tuple[int, int]], list[Finding]]:
    """Locate $$ blocks after generic fenced blocks have been masked."""
    ranges: list[tuple[int, int]] = []
    findings: list[Finding] = []
    tokens = list(re.finditer(r"(?<!\\)\$\$", text))
    if len(tokens) % 2:
        token = tokens[-1]
        findings.append(
            Finding(
                "FAIL",
                "UNBALANCED_DISPLAY_MATH",
                "Display-math delimiter '$$' is not balanced.",
                line_number(text, token.start()),
            )
        )
    for index in range(0, len(tokens) - 1, 2):
        start = tokens[index].start()
        end = tokens[index + 1].end()
        body = text[tokens[index].end() : tokens[index + 1].start()].strip()
        if not body:
            findings.append(
                Finding(
                    "FAIL",
                    "EMPTY_DISPLAY_MATH",
                    "Display-math block is empty.",
                    line_number(text, start),
                )
            )
        ranges.append((start, end))
    return ranges, findings


def find_inline_dollar_problem(text: str) -> Finding | None:
    offsets = [match.start() for match in re.finditer(r"(?<!\\)(?<!\$)\$(?!\$)", text)]
    if len(offsets) % 2:
        offset = offsets[-1]
        return Finding(
            "FAIL",
            "UNBALANCED_INLINE_MATH",
            "Inline-math delimiter '$' is not balanced.",
            line_number(text, offset),
        )
    return None


def validate_markdown(text: str) -> tuple[list[Finding], list[str], list[str]]:
    findings: list[Finding] = []
    fence_ranges, math_fence_ranges, fence_findings = fenced_ranges(text)
    findings.extend(fence_findings)
    without_fences = mask_ranges(text, fence_ranges)

    display_ranges, display_findings = display_math_ranges(without_fences)
    findings.extend(display_findings)

    normalized_displays: dict[str, list[int]] = {}
    for start, end in display_ranges:
        body = without_fences[start + 2 : end - 2].strip()
        normalized = re.sub(r"\s+", "", body).rstrip(",.;")
        if normalized:
            normalized_displays.setdefault(normalized, []).append(start)
    for offsets in normalized_displays.values():
        if len(offsets) > 1:
            findings.append(
                Finding(
                    "WARN",
                    "DUPLICATE_DISPLAY_EQUATION",
                    "The same display equation appears more than once; use one shared E... block for the bilingual pair.",
                    line_number(text, offsets[1]),
                )
            )

    prose = mask_ranges(without_fences, display_ranges)

    inline_problem = find_inline_dollar_problem(prose)
    if inline_problem:
        findings.append(inline_problem)

    # Mask inline math before looking for raw commands in prose.
    inline_tokens = list(re.finditer(r"(?<!\\)(?<!\$)\$(?!\$)", prose))
    inline_ranges = [
        (inline_tokens[i].start(), inline_tokens[i + 1].end())
        for i in range(0, len(inline_tokens) - 1, 2)
    ]
    plain_prose = mask_ranges(prose, inline_ranges)
    for match in LATEX_COMMAND_RE.finditer(plain_prose):
        findings.append(
            Finding(
                "FAIL",
                "BARE_LATEX",
                f"LaTeX command '{match.group(0)}' appears outside a math block.",
                line_number(text, match.start()),
            )
        )

    for line_match in CHINESE_LINE_RE.finditer(plain_prose):
        line_text = line_match.group(0)
        if "\t" in line_text:
            findings.append(
                Finding(
                    "FAIL",
                    "TAB_IN_CHINESE_MATH_PROSE",
                    "A tab appears in a Chinese line; this can indicate a corrupted command such as \\tau.",
                    line_number(text, line_match.start()),
                )
            )
        for pseudo_match in PAREN_PSEUDO_MATH_RE.finditer(line_text):
            findings.append(
                Finding(
                    "FAIL",
                    "PARENTHESIZED_PSEUDO_MATH",
                    f"Use math delimiters instead of ordinary parentheses: {pseudo_match.group(0)!r}.",
                    line_number(text, line_match.start() + pseudo_match.start()),
                )
            )

    anchors = EQUATION_ANCHOR_RE.findall(text)
    duplicates = sorted({item for item in anchors if anchors.count(item) > 1})
    for equation_id in duplicates:
        findings.append(
            Finding("FAIL", "DUPLICATE_EQUATION_ID", f"Duplicate equation anchor: {equation_id}.")
        )

    if anchors:
        numeric = [int(item[1:]) for item in anchors]
        expected = list(range(1, len(numeric) + 1))
        if numeric != expected:
            findings.append(
                Finding(
                    "WARN",
                    "NONSEQUENTIAL_EQUATION_IDS",
                    "Equation anchors should follow reading order without gaps: E001, E002, ...",
                )
            )

    display_count = len(display_ranges) + len(math_fence_ranges)
    if display_count and not anchors:
        findings.append(
            Finding(
                "FAIL",
                "MISSING_EQUATION_ANCHORS",
                "Display equations exist, but paper.md has no E... anchors.",
            )
        )
    if display_count >= 3 and not re.search(r"^#{1,6}\s+(?:公式索引|Equation Index)\s*$", text, re.MULTILINE | re.IGNORECASE):
        findings.append(
            Finding(
                "WARN",
                "MISSING_EQUATION_INDEX",
                "Three or more display equations require an equation index.",
            )
        )

    image_paths = [match.group(1).strip().split()[0].strip("<>") for match in MARKDOWN_IMAGE_RE.finditer(text)]
    return findings, anchors, image_paths


def equation_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for item in data.get("blocks", []):
        if isinstance(item, dict) and item.get("type") == "equation" and isinstance(item.get("id"), str):
            entries[item["id"]] = item
    for item in data.get("equations", []):
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            entries[item["id"]] = {**entries.get(item["id"], {}), **item}
    return list(entries.values())


def validate_source_map(
    source_map_path: Path, anchors: list[str], markdown_image_paths: list[str]
) -> list[Finding]:
    findings: list[Finding] = []
    try:
        data = json.loads(source_map_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [Finding("FAIL", "INVALID_SOURCE_MAP", f"Cannot parse source map: {exc}")]

    if not isinstance(data, dict):
        return [Finding("FAIL", "INVALID_SOURCE_MAP", "Source map root must be a JSON object.")]

    entries = equation_entries(data)
    map_ids = [item.get("id") for item in entries]
    duplicates = sorted({item for item in map_ids if map_ids.count(item) > 1})
    for equation_id in duplicates:
        findings.append(Finding("FAIL", "DUPLICATE_SOURCE_MAP_ID", f"Duplicate source-map ID: {equation_id}."))

    for item in entries:
        equation_id = item.get("id")
        if not isinstance(equation_id, str) or not EQUATION_ID_RE.fullmatch(equation_id):
            findings.append(Finding("FAIL", "INVALID_EQUATION_ID", f"Invalid equation ID: {equation_id!r}."))
            continue
        if equation_id not in anchors:
            findings.append(
                Finding(
                    "FAIL",
                    "SOURCE_MAP_ORPHAN",
                    f"Source-map equation {equation_id} has no matching paper.md anchor.",
                )
            )
        if not isinstance(item.get("page"), int) or item["page"] < 1:
            findings.append(Finding("FAIL", "MISSING_PAGE", f"{equation_id} needs a positive page number."))
        if item.get("confidence") not in {"high", "medium", "low"}:
            findings.append(
                Finding("FAIL", "MISSING_CONFIDENCE", f"{equation_id} needs high, medium, or low confidence.")
            )
        latex = item.get("latex")
        image_path = item.get("image_path")
        if not (isinstance(latex, str) and latex.strip()) and not (
            isinstance(image_path, str) and image_path.strip()
        ):
            findings.append(
                Finding("FAIL", "MISSING_REPRESENTATION", f"{equation_id} needs latex or image_path.")
            )
        if isinstance(image_path, str) and image_path.strip():
            candidate = (source_map_path.parent / image_path).resolve()
            if not candidate.is_file():
                findings.append(
                    Finding("FAIL", "MISSING_EQUATION_IMAGE", f"{equation_id} image does not exist: {image_path}.")
                )
            if image_path not in markdown_image_paths:
                findings.append(
                    Finding(
                        "FAIL",
                        "UNUSED_EQUATION_IMAGE",
                        f"{equation_id} image_path is not displayed in paper.md: {image_path}.",
                    )
                )

    for equation_id in anchors:
        if equation_id not in map_ids:
            findings.append(
                Finding(
                    "FAIL",
                    "MISSING_SOURCE_MAP_ENTRY",
                    f"paper.md equation {equation_id} has no matching source-map equation entry.",
                )
            )
    return findings


def run_validation(paper_path: Path, source_map_path: Path | None) -> list[Finding]:
    try:
        text = paper_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [Finding("FAIL", "UNREADABLE_MARKDOWN", f"Cannot read paper.md: {exc}")]
    findings, anchors, image_paths = validate_markdown(text)
    if source_map_path is not None:
        findings.extend(validate_source_map(source_map_path, anchors, image_paths))
    elif anchors:
        findings.append(
            Finding(
                "WARN",
                "SOURCE_MAP_NOT_CHECKED",
                "Equation anchors exist, but --source-map was not provided.",
            )
        )
    return findings


def self_test() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "assets/equations").mkdir(parents=True)
        (root / "assets/equations/E002.png").write_bytes(b"test")
        good_markdown = """# Paper
<a id="E001"></a>
**Source:** p.1 E001 · Eq. (1)

$$
\\frac{a}{b} = c
$$

**中文:** 其中 $a$、$b$ 和 $c$ 保持原始数学符号。

<a id="E002"></a>
**Source:** p.2 E002 · low confidence

![Original equation E002](assets/equations/E002.png)
"""
        good_map = {
            "blocks": [
                {"id": "E001", "type": "equation", "page": 1, "confidence": "high", "latex": "\\\\frac{a}{b}=c", "image_path": None},
                {"id": "E002", "type": "equation", "page": 2, "confidence": "low", "latex": None, "image_path": "assets/equations/E002.png"},
            ]
        }
        paper = root / "paper.md"
        source_map = root / "source_map.json"
        paper.write_text(good_markdown, encoding="utf-8")
        source_map.write_text(json.dumps(good_map), encoding="utf-8")
        good_findings = run_validation(paper, source_map)
        if good_findings:
            print("Self-test failed: valid fixture was rejected.", file=sys.stderr)
            for item in good_findings:
                print(asdict(item), file=sys.stderr)
            return 1

        bad_markdown = """# Broken
<a id="E001"></a>
Raw formula: \\frac{a}{b}
**中文:** 其中 (I_0) 为峰值强度。
$$
x+y
"""
        paper.write_text(bad_markdown, encoding="utf-8")
        bad_findings = run_validation(paper, None)
        bad_codes = {item.code for item in bad_findings if item.severity == "FAIL"}
        required = {"BARE_LATEX", "UNBALANCED_DISPLAY_MATH", "PARENTHESIZED_PSEUDO_MATH"}
        if not required.issubset(bad_codes):
            print(f"Self-test failed: missing expected failures {sorted(required - bad_codes)}.", file=sys.stderr)
            return 1

    print("Self-test passed.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper", nargs="?", type=Path, help="Path to paper.md")
    parser.add_argument("--source-map", type=Path, help="Path to source_map.json")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as validation failures")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print machine-readable JSON")
    parser.add_argument("--self-test", action="store_true", help="Run built-in valid and invalid fixtures")
    args = parser.parse_args()
    if not args.self_test and args.paper is None:
        parser.error("paper is required unless --self-test is used")
    return args


def main() -> int:
    args = parse_args()
    if args.self_test:
        return self_test()

    findings = run_validation(args.paper, args.source_map)
    failed = any(item.severity == "FAIL" or (args.strict and item.severity == "WARN") for item in findings)
    payload = {
        "ready": not failed,
        "strict": args.strict,
        "summary": {
            "fail": sum(item.severity == "FAIL" for item in findings),
            "warn": sum(item.severity == "WARN" for item in findings),
        },
        "findings": [asdict(item) for item in findings],
    }
    if args.json_output:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif findings:
        for item in findings:
            location = f" line {item.line}" if item.line else ""
            print(f"[{item.severity}] {item.code}{location}: {item.message}")
        print(f"Ready: {'yes' if not failed else 'no'}")
    else:
        print("No math validation findings. Ready: yes")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
