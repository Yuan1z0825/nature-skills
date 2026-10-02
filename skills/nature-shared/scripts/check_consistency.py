#!/usr/bin/env python3
"""Find mechanically detectable consistency risks in manuscript text files."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Sequence


DEFAULT_TERM_GROUPS = {
    "self-reference": ("this study", "this work", "this paper", "this article"),
    "standard-deviation": ("standard deviation", "SD", "Std"),
}

LENGTH_FACTORS_METRES = {
    "um": Decimal("0.000001"),
    "mm": Decimal("0.001"),
    "cm": Decimal("0.01"),
    "m": Decimal("1"),
}


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class Occurrence:
    path: Path
    line: int
    value: str

    def label(self) -> str:
        return f"{self.path}:{self.line}: {self.value}"


def read_sources(paths: Sequence[Path]) -> dict[Path, str]:
    return {
        path: path.read_text(encoding="utf-8", errors="replace")
        for path in paths
    }


def visible_lines(text: str) -> Iterable[tuple[int, str]]:
    """Yield lines after removing Markdown fences and unescaped LaTeX comments."""
    in_fence = False
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        if re.match(r"^\s*```", raw_line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = re.sub(r"(?<!\\)%.*$", "", raw_line)
        yield line_number, line


def phrase_pattern(phrase: str) -> re.Pattern[str]:
    escaped = re.escape(phrase).replace(r"\ ", r"\s+")
    prefix = r"(?<![\w-])" if phrase[0].isalnum() else ""
    suffix = r"(?![\w-])" if phrase[-1].isalnum() else ""
    return re.compile(prefix + escaped + suffix, re.IGNORECASE)


def find_phrase_occurrences(
    sources: dict[Path, str], phrase: str
) -> list[Occurrence]:
    pattern = phrase_pattern(phrase)
    occurrences: list[Occurrence] = []
    for path, text in sources.items():
        for line_number, line in visible_lines(text):
            for match in pattern.finditer(line):
                occurrences.append(Occurrence(path, line_number, match.group(0)))
    return occurrences


def check_term_groups(
    sources: dict[Path, str], groups: dict[str, tuple[str, ...]]
) -> list[Finding]:
    findings: list[Finding] = []
    for group_name, variants in groups.items():
        present: list[tuple[str, list[Occurrence]]] = []
        for variant in variants:
            occurrences = find_phrase_occurrences(sources, variant)
            if occurrences:
                present.append((variant, occurrences))
        if len(present) < 2:
            continue
        counts = ", ".join(f"{variant}={len(items)}" for variant, items in present)
        evidence = tuple(
            occurrence.label()
            for _, items in present
            for occurrence in items[:3]
        )
        findings.append(
            Finding(
                code="TERM_VARIANTS_PRESENT",
                message=f"term group '{group_name}' uses multiple variants: {counts}",
                evidence=evidence,
            )
        )
    return findings


NUMBER_PATTERN = re.compile(r"(?<![\w.])([+-]?(?:\d+\.\d+|\d+))(?![\w.])")


def decimal_places(token: str) -> int:
    unsigned = token.lstrip("+-")
    return len(unsigned.partition(".")[2]) if "." in unsigned else 0


def check_numeric_precision(sources: dict[Path, str]) -> list[Finding]:
    values: dict[Decimal, dict[int, list[Occurrence]]] = {}
    for path, text in sources.items():
        for line_number, line in visible_lines(text):
            for match in NUMBER_PATTERN.finditer(line):
                token = match.group(1)
                try:
                    value = Decimal(token)
                except InvalidOperation:
                    continue
                places = decimal_places(token)
                values.setdefault(value, {}).setdefault(places, []).append(
                    Occurrence(path, line_number, token)
                )

    findings: list[Finding] = []
    for value, precision_groups in values.items():
        if len(precision_groups) < 2:
            continue
        precision_summary = ", ".join(
            f"{places} decimal place(s)={len(items)}"
            for places, items in sorted(precision_groups.items())
        )
        evidence = tuple(
            occurrence.label()
            for _, items in sorted(precision_groups.items())
            for occurrence in items[:3]
        )
        findings.append(
            Finding(
                code="NUMERIC_PRECISION_VARIANT",
                message=f"numeric value {value} appears at multiple precisions: {precision_summary}",
                evidence=evidence,
            )
        )
    return findings


LENGTH_PATTERN = re.compile(
    r"(?<![\w.])([+-]?(?:\d+\.\d+|\d+))\s*(?:\\,\s*)?"
    r"(?:\\(?:mathrm|text)\s*\{\s*)?(μm|µm|um|mm|cm|m)(?:\s*\})?"
    r"(?![A-Za-z])",
    re.IGNORECASE,
)


def normalized_unit(unit: str) -> str:
    unit = unit.lower()
    return "um" if unit in {"μm", "µm"} else unit


def check_equivalent_length_units(sources: dict[Path, str]) -> list[Finding]:
    values: dict[Decimal, dict[str, list[Occurrence]]] = {}
    for path, text in sources.items():
        for line_number, line in visible_lines(text):
            for match in LENGTH_PATTERN.finditer(line):
                number, raw_unit = match.groups()
                unit = normalized_unit(raw_unit)
                metres = Decimal(number) * LENGTH_FACTORS_METRES[unit]
                values.setdefault(metres, {}).setdefault(unit, []).append(
                    Occurrence(path, line_number, match.group(0))
                )

    findings: list[Finding] = []
    for metres, unit_groups in values.items():
        if len(unit_groups) < 2:
            continue
        counts = ", ".join(
            f"{unit}={len(items)}" for unit, items in sorted(unit_groups.items())
        )
        evidence = tuple(
            occurrence.label()
            for _, items in sorted(unit_groups.items())
            for occurrence in items[:3]
        )
        findings.append(
            Finding(
                code="EQUIVALENT_LENGTH_UNIT_VARIANT",
                message=f"equivalent length {metres} m appears in multiple units: {counts}",
                evidence=evidence,
            )
        )
    return findings


def parse_term_group(value: str) -> tuple[str, tuple[str, ...]]:
    name, separator, raw_variants = value.partition("=")
    variants = tuple(item.strip() for item in raw_variants.split("|") if item.strip())
    if not separator or not name.strip() or len(variants) < 2:
        raise argparse.ArgumentTypeError(
            "term groups must use NAME=variant one|variant two with at least two variants"
        )
    return name.strip(), variants


def run_checks(
    paths: Sequence[Path],
    term_groups: dict[str, tuple[str, ...]] | None = None,
) -> list[Finding]:
    sources = read_sources(paths)
    findings = check_term_groups(sources, term_groups or {})
    findings.extend(check_numeric_precision(sources))
    findings.extend(check_equivalent_length_units(sources))
    return findings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find terminology, numeric-precision, and equivalent-unit variants."
    )
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument(
        "--term-group",
        action="append",
        default=[],
        type=parse_term_group,
        metavar="NAME=TERM|VARIANT",
        help="Add a manuscript-specific terminology group. Repeat as needed.",
    )
    parser.add_argument(
        "--no-default-term-groups",
        action="store_true",
        help="Disable the built-in self-reference and standard-deviation groups.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Return exit status 1 when warnings are found.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    groups = {} if args.no_default_term_groups else dict(DEFAULT_TERM_GROUPS)
    groups.update(dict(args.term_group))
    findings = run_checks(args.paths, groups)

    if args.as_json:
        print(json.dumps([asdict(item) for item in findings], ensure_ascii=False, indent=2))
    elif findings:
        for finding in findings:
            print(f"{finding.code}\t{finding.message}")
            for item in finding.evidence:
                print(f"  {item}")
    else:
        print("No mechanical consistency warnings found.")

    return 1 if findings and args.fail_on_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
