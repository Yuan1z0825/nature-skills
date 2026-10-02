#!/usr/bin/env python3
"""Audit a Paper Card against its source bundle and output contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SECTION_RE = re.compile(r"^##\s+(\d{2})\b.*$", re.M)
PAPER_POINTER_RE = re.compile(r"\[Paper:\s*([^\]]+)\]")
FORBIDDEN_SECTION_RE = re.compile(r"^##\s+(17|18)\b", re.M)

OUT_OF_SCOPE_TERMS = [
    "academic english",
    "self-quiz",
    "comprehension quiz",
    "public article",
    "social-media copy",
    "\u5b66\u672f\u82f1\u6587",
    "\u81ea\u6d4b",
    "\u516c\u4f17\u53f7",
]

IDEA_STATUS_TERMS = [
    "innovation status",
    "\u521b\u65b0\u72b6\u6001",
]

IDEA_VALIDATION_TERMS = [
    "validation",
    "how to test",
    "\u5982\u4f55\u9a8c\u8bc1",
]

IDEA_FAILURE_TERMS = [
    "failure mode",
    "possible failure",
    "\u53ef\u80fd\u5931\u8d25",
]

LOCATOR_MODES = ("page-grounded", "structure-grounded", "source-limited")
SOURCE_LIMITED_LOCATORS = ("abstract", "metadata", "user-provided excerpt")


def finding(level: str, code: str, message: str, **details: Any) -> dict[str, Any]:
    item: dict[str, Any] = {"level": level, "code": code, "message": message}
    if details:
        item["details"] = details
    return item


def contains_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term.lower() in lower for term in terms)


def section_text(card: str, number: str) -> str:
    match = re.search(
        rf"^##\s+{re.escape(number)}\b[^\n]*\n(.*?)(?=^##\s+\d{{2}}\b|\Z)",
        card,
        re.M | re.S,
    )
    return match.group(1) if match else ""


def evidence_item_mentioned(card: str, item_id: str) -> bool:
    match = re.match(r"^(Figure|Table|Equation)\s+(\d+[A-Za-z]?)$", item_id)
    if not match:
        return item_id.lower() in card.lower()

    kind, number = match.groups()
    aliases = {
        "Figure": [
            f"Figure {number}",
            f"Fig. {number}",
            f"\u56fe{number}",
            f"\u56fe {number}",
        ],
        "Table": [
            f"Table {number}",
            f"\u8868{number}",
            f"\u8868 {number}",
        ],
        "Equation": [
            f"Equation {number}",
            f"Eq. {number}",
            f"Eq.{number}",
            f"\u516c\u5f0f{number}",
            f"\u516c\u5f0f {number}",
        ],
    }
    lower = card.lower()
    return any(alias.lower() in lower for alias in aliases[kind])


def audit(
    card: str,
    bundle: dict[str, Any] | None,
    locator_mode: str,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    sections = SECTION_RE.findall(card)
    expected = [f"{number:02d}" for number in range(1, 17)]

    if sections == expected:
        findings.append(finding("pass", "sections", "Sections 01-16 are present in order."))
    else:
        findings.append(
            finding(
                "error",
                "sections",
                "Sections 01-16 are missing, duplicated, or out of order.",
                expected=expected,
                found=sections,
            )
        )

    forbidden_sections = FORBIDDEN_SECTION_RE.findall(card)
    if forbidden_sections:
        findings.append(
            finding("error", "forbidden_sections", "Sections 17 or 18 must not be present.")
        )
    else:
        findings.append(finding("pass", "forbidden_sections", "No Sections 17 or 18 found."))

    preamble = card.split("## 01", 1)[0]
    metadata_lines = [line for line in preamble.splitlines() if line.lstrip().startswith(">")]
    if len(metadata_lines) >= 7:
        findings.append(
            finding("pass", "status_header", "The evidence-status header has at least seven fields.")
        )
    else:
        findings.append(
            finding(
                "error",
                "status_header",
                "The evidence-status header must contain at least seven blockquote fields.",
                found=len(metadata_lines),
            )
        )

    if locator_mode in preamble.lower():
        findings.append(
            finding(
                "pass",
                "locator_mode_declaration",
                f"The card declares locator mode: {locator_mode}.",
            )
        )
    else:
        findings.append(
            finding(
                "error",
                "locator_mode_declaration",
                f"The card header must declare canonical locator mode: {locator_mode}.",
            )
        )

    pointers = PAPER_POINTER_RE.findall(card)
    if pointers:
        findings.append(
            finding("pass", "paper_pointers", f"Found {len(pointers)} paper source pointers.")
        )
    else:
        findings.append(finding("error", "paper_pointers", "No [Paper: ...] pointers found."))

    page_pointers = [
        pointer
        for pointer in pointers
        if "PDF p." in pointer or "PDF pp." in pointer
    ]
    ambiguous = [
        pointer
        for pointer in pointers
        if re.search(r"\bpp?\.", pointer)
        and "PDF p." not in pointer
        and "PDF pp." not in pointer
    ]

    if locator_mode == "page-grounded":
        if bundle is None:
            findings.append(
                finding(
                    "error",
                    "bundle_required",
                    "Page-grounded mode requires a source bundle.",
                )
            )
        if not page_pointers:
            findings.append(
                finding(
                    "error",
                    "page_grounding",
                    "Page-grounded mode requires at least one PDF page pointer.",
                )
            )
        elif ambiguous:
            findings.append(
                finding(
                    "error",
                    "ambiguous_pages",
                    "Page pointers must distinguish PDF page indices.",
                    pointers=ambiguous,
                )
            )
        else:
            findings.append(
                finding("pass", "page_grounding", "PDF page pointers are explicit and unambiguous.")
            )
    else:
        if page_pointers or ambiguous:
            findings.append(
                finding(
                    "error",
                    "page_pointers_forbidden",
                    f"{locator_mode} mode must not emit page-number citations.",
                    pointers=page_pointers + ambiguous,
                )
            )
        else:
            findings.append(
                finding(
                    "pass",
                    "page_pointers_forbidden",
                    f"{locator_mode} mode contains no page-number citations.",
                )
            )

    inventory = bundle.get("evidence_inventory", {}) if bundle else {}
    if bundle is not None:
        for key, label in (("figures", "figure"), ("tables", "table"), ("equations", "equation")):
            items = inventory.get(key, []) if isinstance(inventory, dict) else []
            missing = [
                item.get("id", "")
                for item in items
                if not evidence_item_mentioned(card, item.get("id", ""))
            ]
            if missing:
                findings.append(
                    finding(
                        "error",
                        f"{key}_coverage",
                        f"Not every main {label} from the source bundle appears in the card.",
                        missing=missing,
                    )
                )
            else:
                findings.append(
                    finding(
                        "pass",
                        f"{key}_coverage",
                        f"All {len(items)} inventoried {key} appear in the card.",
                    )
                )
    else:
        findings.append(
            finding(
                "warning",
                "source_inventory_unavailable",
                "No source bundle was supplied; figure, table, and equation coverage was not audited.",
            )
        )

    if locator_mode == "source-limited" and pointers:
        invalid_limited = [
            pointer
            for pointer in pointers
            if not any(token in pointer.lower() for token in SOURCE_LIMITED_LOCATORS)
        ]
        if invalid_limited:
            findings.append(
                finding(
                    "error",
                    "source_limited_scope",
                    "Source-limited pointers must use only Abstract, Metadata, or User-provided excerpt.",
                    pointers=invalid_limited,
                )
            )
        else:
            findings.append(
                finding(
                    "pass",
                    "source_limited_scope",
                    "All source-limited pointers use allowed source scopes.",
                )
            )

    section_12 = section_text(card, "12")
    section_13 = section_text(card, "13")
    if section_12 and section_13:
        findings.append(
            finding("pass", "limitations_split", "Sections 12 and 13 are both present.")
        )

    section_16 = section_text(card, "16")
    if section_16:
        checks = {
            "idea_status": contains_any(section_16, IDEA_STATUS_TERMS),
            "idea_validation": contains_any(section_16, IDEA_VALIDATION_TERMS),
            "idea_failure": contains_any(section_16, IDEA_FAILURE_TERMS),
        }
        for code, passed in checks.items():
            findings.append(
                finding(
                    "pass" if passed else "warning",
                    code,
                    (
                        f"Section 16 includes the required {code.replace('idea_', '')} field."
                        if passed
                        else f"Section 16 may be missing the {code.replace('idea_', '')} field."
                    ),
                )
            )

    out_of_scope = [term for term in OUT_OF_SCOPE_TERMS if term.lower() in card.lower()]
    if out_of_scope:
        findings.append(
            finding(
                "error",
                "out_of_scope",
                "The card contains content excluded by the skill scope.",
                terms=out_of_scope,
            )
        )
    else:
        findings.append(finding("pass", "out_of_scope", "No excluded content detected."))

    errors = sum(item["level"] == "error" for item in findings)
    warnings = sum(item["level"] == "warning" for item in findings)
    passes = sum(item["level"] == "pass" for item in findings)
    return {
        "schema_version": "1.0",
        "summary": {
            "status": "fail" if errors else ("pass_with_warnings" if warnings else "pass"),
            "passes": passes,
            "warnings": warnings,
            "errors": errors,
        },
        "metrics": {
            "locator_mode": locator_mode,
            "sections_found": sections,
            "paper_pointer_count": len(pointers),
            "figures_in_bundle": len(inventory.get("figures", [])),
            "tables_in_bundle": len(inventory.get("tables", [])),
            "equations_in_bundle": len(inventory.get("equations", [])),
        },
        "findings": findings,
    }


def print_report(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print(
        f"Audit status: {summary['status']} "
        f"(passes={summary['passes']}, warnings={summary['warnings']}, errors={summary['errors']})"
    )
    for item in report["findings"]:
        print(f"{item['level'].upper():7} {item['code']}: {item['message']}")
        details = item.get("details")
        if details:
            print(f"        {json.dumps(details, ensure_ascii=False)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit a Paper Card and its locator mode.")
    parser.add_argument("--card", type=Path, required=True, help="Paper Card Markdown file.")
    parser.add_argument("--bundle", type=Path, help="Optional source_bundle.json.")
    parser.add_argument(
        "--locator-mode",
        required=True,
        choices=LOCATOR_MODES,
        help="Grounding mode declared by the Paper Card.",
    )
    parser.add_argument("--report", type=Path, help="Optional JSON audit report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.card.is_file():
        print("ERROR: --card must point to an existing file.", file=sys.stderr)
        return 2
    if args.bundle and not args.bundle.is_file():
        print("ERROR: --bundle does not exist.", file=sys.stderr)
        return 2
    if args.locator_mode == "page-grounded" and not args.bundle:
        print("ERROR: page-grounded mode requires --bundle.", file=sys.stderr)
        return 2

    try:
        card = args.card.read_text(encoding="utf-8")
        bundle = json.loads(args.bundle.read_text(encoding="utf-8")) if args.bundle else None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    report = audit(card, bundle, args.locator_mode)
    print_report(report)

    if args.report:
        output = args.report.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote audit report: {output}")

    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
