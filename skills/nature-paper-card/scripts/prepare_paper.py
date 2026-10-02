#!/usr/bin/env python3
"""Prepare a stable source bundle for the nature-paper-card workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


SECTION_NAMES = {
    "abstract",
    "introduction",
    "background",
    "related work",
    "method",
    "methods",
    "methodology",
    "experiments",
    "experimental setup",
    "experimental results",
    "results",
    "method analysis",
    "discussion",
    "limitations",
    "conclusion",
    "conclusions",
    "acknowledgments",
    "acknowledgements",
    "references",
    "appendix",
}

CAPTION_RE = re.compile(r"^\s*(Figure|Fig\.|Table)\s+(\d+[A-Za-z]?)\s*:\s*(.*)$", re.I)
EQUATION_RE = re.compile(r"\((\d{1,2})\)\s*$")
PRINTED_PAGE_RE = re.compile(r"^\s*(\d{4,6})\s*$", re.M)
PAGE_LOCATOR_FIELDS = ("page", "page_number", "pdf_page")
POSITIVE_INTEGER_RE = re.compile(r"^[1-9]\d*$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.splitlines()).strip()


def printed_page_label(text: str) -> str | None:
    candidates = PRINTED_PAGE_RE.findall(text)
    return candidates[-1] if candidates else None


def heading_candidates(
    text: str, pdf_page: int | None, printed_page: str | None
) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    for line in text.splitlines():
        value = " ".join(line.split()).strip(" :")
        lower = value.lower()
        numbered = re.match(r"^(?:\d+(?:\.\d+)*)\s+([A-Z][A-Za-z0-9 ,/&-]{2,80})$", value)
        if lower in SECTION_NAMES or numbered:
            headings.append(
                {
                    "title": value,
                    "pdf_page": pdf_page,
                    "printed_page": printed_page,
                }
            )
    return headings


def collect_caption(lines: list[str], start: int) -> str:
    match = CAPTION_RE.match(lines[start])
    if not match:
        return ""
    parts = [match.group(3).strip()]
    for line in lines[start + 1 : start + 4]:
        value = " ".join(line.split())
        if not value or CAPTION_RE.match(value) or value.lower() in SECTION_NAMES:
            break
        if re.match(r"^[A-Z][A-Za-z ]{2,40}$", value) and not value.endswith("."):
            break
        parts.append(value)
    return " ".join(part for part in parts if part)


def evidence_from_pages(pages: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    figures: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    equations: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for page in pages:
        lines = page["text"].splitlines()
        for index, line in enumerate(lines):
            caption_match = CAPTION_RE.match(line)
            if caption_match:
                kind = caption_match.group(1).lower()
                number = caption_match.group(2)
                canonical = "Table" if kind == "table" else "Figure"
                key = (canonical, number)
                if key not in seen:
                    seen.add(key)
                    item = {
                        "id": f"{canonical} {number}",
                        "caption": collect_caption(lines, index),
                        "pdf_page": page["pdf_page"],
                        "printed_page": page.get("printed_page"),
                    }
                    (tables if canonical == "Table" else figures).append(item)

            equation_match = EQUATION_RE.search(line)
            if equation_match:
                number = equation_match.group(1)
                key = ("Equation", number)
                if key not in seen:
                    seen.add(key)
                    context_start = max(0, index - 3)
                    equations.append(
                        {
                            "id": f"Equation {number}",
                            "context": " ".join(lines[context_start : index + 1]).strip(),
                            "pdf_page": page["pdf_page"],
                            "printed_page": page.get("printed_page"),
                        }
                    )

    def natural_key(item: dict[str, Any]) -> tuple[int, str]:
        match = re.match(r"\D+(\d+)(.*)", item["id"])
        return (int(match.group(1)), match.group(2)) if match else (999999, item["id"])

    return {
        "figures": sorted(figures, key=natural_key),
        "tables": sorted(tables, key=natural_key),
        "equations": sorted(equations, key=natural_key),
    }


def prepare_pdf(path: Path, render_dir: Path | None, render_scale: float) -> dict[str, Any]:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError(
            "PyMuPDF is required for PDF input. Install it with: python -m pip install pymupdf"
        ) from exc

    document = fitz.open(path)
    pages: list[dict[str, Any]] = []
    sections: list[dict[str, Any]] = []

    if render_dir:
        render_dir.mkdir(parents=True, exist_ok=True)

    for index, page in enumerate(document):
        text = clean_text(page.get_text("text"))
        pdf_page = index + 1
        printed_page = printed_page_label(text)
        page_record = {
            "pdf_page": pdf_page,
            "printed_page": printed_page,
            "text": text,
            "character_count": len(text),
        }
        pages.append(page_record)
        sections.extend(heading_candidates(text, pdf_page, printed_page))

        if render_dir:
            matrix = fitz.Matrix(render_scale, render_scale)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            pixmap.save(render_dir / f"page-{pdf_page:03d}.png")

    metadata = {key: value for key, value in document.metadata.items() if value not in (None, "")}
    evidence = evidence_from_pages(pages)
    return {
        "schema_version": "1.0",
        "source_type": "pdf",
        "source_path": str(path.resolve()),
        "source_sha256": sha256_file(path),
        "metadata": metadata,
        "page_count": document.page_count,
        "pages": pages,
        "sections": sections,
        "evidence_inventory": evidence,
        "rendered_pages_dir": str(render_dir.resolve()) if render_dir else None,
        "extraction": {
            "engine": "PyMuPDF",
            "visual_pages_rendered": bool(render_dir),
            "confidence": "high" if all(page["character_count"] > 50 for page in pages) else "mixed",
        },
    }


def flatten_source_map(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if not isinstance(data, dict):
        return []
    for key in ("blocks", "source_blocks", "items", "entries"):
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def page_locator(block: dict[str, Any]) -> tuple[int | None, str, str | None, Any]:
    """Return a verified 1-based page or an explicit missing/invalid state."""
    locator_field: str | None = None
    locator_value: Any = None
    for field in PAGE_LOCATOR_FIELDS:
        if field not in block:
            continue
        value = block[field]
        if value is None or (isinstance(value, str) and not value.strip()):
            if locator_field is None:
                locator_field = field
                locator_value = value
            continue
        locator_field = field
        locator_value = value
        break
    else:
        return None, "missing", locator_field, locator_value

    if isinstance(locator_value, bool):
        return None, "invalid", locator_field, locator_value
    if isinstance(locator_value, int):
        return (
            (locator_value, "verified", locator_field, locator_value)
            if locator_value > 0
            else (None, "invalid", locator_field, locator_value)
        )
    if isinstance(locator_value, float):
        return (
            (int(locator_value), "verified", locator_field, locator_value)
            if locator_value.is_integer() and locator_value > 0
            else (None, "invalid", locator_field, locator_value)
        )
    if isinstance(locator_value, str) and POSITIVE_INTEGER_RE.fullmatch(locator_value.strip()):
        return int(locator_value.strip()), "verified", locator_field, locator_value
    return None, "invalid", locator_field, locator_value


def source_block_text(block: dict[str, Any]) -> str:
    text = (
        block.get("original")
        or block.get("source_text")
        or block.get("text")
        or block.get("content")
        or ""
    )
    return clean_text(str(text)) if text else ""


def unlocated_block_record(
    block: dict[str, Any], index: int, text: str, status: str, field: str | None, value: Any
) -> dict[str, Any]:
    source_id = block.get("id") or block.get("block_id") or f"U{index:03d}"
    return {
        "id": str(source_id),
        "block_type": block.get("type"),
        "section": block.get("section") or block.get("section_title"),
        "text": text,
        "character_count": len(text),
        "locator_status": status,
        "locator_field": field,
        "locator_value": value,
    }


def prepare_source_map(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    grouped: dict[int, list[str]] = defaultdict(list)
    unlocated_blocks: list[dict[str, Any]] = []
    verified_block_count = 0
    missing_locator_count = 0
    invalid_locator_count = 0

    for index, block in enumerate(flatten_source_map(data), start=1):
        text = source_block_text(block)
        if not text:
            continue
        page_number, locator_status, locator_field, locator_value = page_locator(block)
        if locator_status == "verified" and page_number is not None:
            verified_block_count += 1
            grouped[page_number].append(text)
            continue
        if locator_status == "missing":
            missing_locator_count += 1
        else:
            invalid_locator_count += 1
        unlocated_blocks.append(
            unlocated_block_record(
                block, index, text, locator_status, locator_field, locator_value
            )
        )

    pages = [
        {
            "pdf_page": page_number,
            "printed_page": None,
            "text": clean_text("\n".join(grouped[page_number])),
            "character_count": len(clean_text("\n".join(grouped[page_number]))),
        }
        for page_number in sorted(grouped)
    ]
    structure_units = pages + [
        {
            "pdf_page": None,
            "printed_page": None,
            "text": block["text"],
            "character_count": block["character_count"],
        }
        for block in unlocated_blocks
    ]
    sections = [
        heading
        for page in structure_units
        for heading in heading_candidates(page["text"], page["pdf_page"], page["printed_page"])
    ]
    if unlocated_blocks and verified_block_count:
        locator_reliability = "mixed"
    elif unlocated_blocks:
        locator_reliability = "unavailable"
    else:
        locator_reliability = "reliable"
    return {
        "schema_version": "1.1",
        "source_type": "source_map",
        "source_path": str(path.resolve()),
        "source_sha256": sha256_file(path),
        "metadata": data.get("metadata", {}) if isinstance(data, dict) else {},
        "page_count": len(pages),
        "pages": pages,
        "unlocated_blocks": unlocated_blocks,
        "locator_summary": {
            "verified_page_blocks": verified_block_count,
            "missing_page_locator_blocks": missing_locator_count,
            "invalid_page_locator_blocks": invalid_locator_count,
            "page_locator_reliability": locator_reliability,
        },
        "sections": sections,
        "evidence_inventory": evidence_from_pages(structure_units),
        "rendered_pages_dir": None,
        "extraction": {
            "engine": "source-map-normalizer",
            "visual_pages_rendered": False,
            "confidence": "mixed",
            "page_locator_reliability": locator_reliability,
        },
    }


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    page_count = bundle.get("page_count", 0)
    pages = bundle.get("pages", [])
    metadata = bundle.get("metadata", {})
    inventory = bundle.get("evidence_inventory", {})
    source_type = bundle.get("source_type")
    unlocated_blocks = bundle.get("unlocated_blocks", [])
    locator_summary = bundle.get("locator_summary", {})

    if not isinstance(page_count, int) or page_count < 0:
        errors.append("page_count must be a non-negative integer")
    if not isinstance(pages, list) or len(pages) != page_count:
        errors.append("pages must contain exactly page_count records")
    else:
        located_text_available = any(page.get("character_count", 0) >= 50 for page in pages)
        unlocated_text_available = isinstance(unlocated_blocks, list) and any(
            block.get("character_count", 0) >= 50
            for block in unlocated_blocks
            if isinstance(block, dict)
        )
        if not located_text_available and not unlocated_text_available:
            errors.append("no source block contains enough extractable text")

    if source_type == "pdf" and page_count <= 0:
        errors.append("PDF page_count must be a positive integer")

    if source_type == "source_map":
        if not isinstance(unlocated_blocks, list):
            errors.append("unlocated_blocks must be an array")
        if not isinstance(locator_summary, dict):
            errors.append("locator_summary must be an object")
        else:
            missing_count = locator_summary.get("missing_page_locator_blocks", 0)
            invalid_count = locator_summary.get("invalid_page_locator_blocks", 0)
            if isinstance(missing_count, int) and missing_count > 0:
                warnings.append(
                    f"{missing_count} source block(s) have no page locator; retained in unlocated_blocks"
                )
            if isinstance(invalid_count, int) and invalid_count > 0:
                warnings.append(
                    f"{invalid_count} source block(s) have invalid page locators; retained in unlocated_blocks"
                )

    if not isinstance(metadata, dict) or not metadata.get("title"):
        warnings.append("document title is unavailable")

    if isinstance(inventory, dict):
        evidence_count = sum(
            len(inventory.get(key, [])) for key in ("figures", "tables", "equations")
        )
        if evidence_count == 0:
            warnings.append("no figures, tables, or equations were detected")
    else:
        errors.append("evidence_inventory must be an object")

    if errors:
        locator_mode = "source-limited"
    elif source_type == "pdf":
        locator_mode = "page-grounded"
    else:
        locator_mode = "structure-grounded"

    return {
        "status": "invalid" if errors else ("valid_with_warnings" if warnings else "valid"),
        "errors": errors,
        "warnings": warnings,
        "recommended_locator_mode": locator_mode,
        "printed_page_labels_required": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a normalized source bundle from a paper PDF or nature-reader JSON."
    )
    parser.add_argument("input", type=Path, help="Input PDF or source-map JSON.")
    parser.add_argument("--output", type=Path, required=True, help="Output source_bundle.json.")
    parser.add_argument("--render-dir", type=Path, help="Optional directory for rendered PDF pages.")
    parser.add_argument("--render-scale", type=float, default=1.25, help="PDF render scale.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.input.resolve()
    if not source.is_file():
        print(f"ERROR: input file does not exist: {source}", file=sys.stderr)
        return 2

    try:
        if source.suffix.lower() == ".pdf":
            bundle = prepare_pdf(source, args.render_dir, args.render_scale)
        elif source.suffix.lower() == ".json":
            bundle = prepare_source_map(source)
        else:
            print("ERROR: input must be a PDF or JSON source map.", file=sys.stderr)
            return 2
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    bundle["validation"] = validate_bundle(bundle)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")

    inventory = bundle["evidence_inventory"]
    print(f"Wrote source bundle: {output}")
    print(f"Pages: {bundle['page_count']}")
    print(f"Sections: {len(bundle['sections'])}")
    print(f"Figures: {len(inventory['figures'])}")
    print(f"Tables: {len(inventory['tables'])}")
    print(f"Equations: {len(inventory['equations'])}")
    validation = bundle["validation"]
    print(f"Bundle validation: {validation['status']}")
    print(f"Recommended locator mode: {validation['recommended_locator_mode']}")
    for warning in validation["warnings"]:
        print(f"WARNING: {warning}")
    for error in validation["errors"]:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if validation["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
