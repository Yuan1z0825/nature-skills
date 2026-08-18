#!/usr/bin/env python3
"""Create and validate page-by-page visual review evidence."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "image2ppt-visual-review-evidence-v1"
BASE_CHECKS = (
    "composition_layout",
    "text_content",
    "object_completeness",
    "render_integrity",
)
GENERIC_OBSERVATIONS = {
    "good",
    "looks good",
    "looks fine",
    "ok",
    "okay",
    "pass",
    "passed",
    "reviewed",
    "checked",
    "fine",
    "没问题",
    "看起来不错",
    "通过",
    "已检查",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def required_checks(manifest: dict[str, Any]) -> list[str]:
    checks = list(BASE_CHECKS)
    shapes = manifest.get("shapes") or []
    if any(
        shape.get("start_arrow") not in {None, "", "none"}
        or shape.get("end_arrow") not in {None, "", "none"}
        or str(shape.get("preset") or "").lower().endswith("arrow")
        for shape in shapes
        if isinstance(shape, dict)
    ):
        checks.append("arrow_geometry")
    if manifest.get("images"):
        checks.append("raster_assets")
    if manifest.get("formula_inventory"):
        checks.append("formulas")
    regions = ((manifest.get("image2ppt_region_decomposition") or {}).get("regions") or [])
    if any(isinstance(region, dict) and region.get("compound_diagram") for region in regions):
        checks.append("compound_diagram")
    return checks


def expected_page(
    *, page_id: str, source: Path, rendered: Path, manifest: dict[str, Any]
) -> dict[str, Any]:
    return {
        "page_id": page_id,
        "source": str(source.resolve()),
        "rendered": str(rendered.resolve()),
        "source_sha256": sha256_file(source),
        "rendered_sha256": sha256_file(rendered),
        "required_checks": required_checks(manifest),
    }


def template_payload(expected_pages: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "pages": [
            {
                "page_id": page["page_id"],
                "source": page["source"],
                "rendered": page["rendered"],
                "source_sha256": page["source_sha256"],
                "rendered_sha256": page["rendered_sha256"],
                "reviewed": False,
                "checks": {name: "" for name in page["required_checks"]},
            }
            for page in expected_pages
        ],
    }


def write_template(path: Path, expected_pages: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(template_payload(expected_pages), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def observation_is_specific(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    stripped = value.strip()
    normalized = re.sub(r"[\s.!。！?？_-]+", " ", stripped.lower()).strip()
    if normalized in GENERIC_OBSERVATIONS:
        return False
    compact = re.sub(r"\s+", "", stripped)
    return len(compact) >= 12


def validate_evidence(
    path: Path, expected_pages: list[dict[str, Any]]
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    try:
        payload = read_json(path)
    except (OSError, ValueError, TypeError) as exc:
        return {}, [f"unable to read visual review evidence: {path}: {exc}"]
    if payload.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"visual review evidence schema_version must be {SCHEMA_VERSION}")
    pages = payload.get("pages")
    if not isinstance(pages, list):
        return payload, [*errors, "visual review evidence pages must be a list"]
    by_id = {
        str(page.get("page_id")): page
        for page in pages
        if isinstance(page, dict) and page.get("page_id")
    }
    expected_ids = {page["page_id"] for page in expected_pages}
    if set(by_id) != expected_ids:
        errors.append(
            "visual review evidence page ids do not match rendered pages: "
            f"expected={sorted(expected_ids)} actual={sorted(by_id)}"
        )
    for expected in expected_pages:
        page_id = expected["page_id"]
        page = by_id.get(page_id)
        if not page:
            continue
        if page.get("reviewed") is not True:
            errors.append(f"{page_id}: reviewed must be true")
        for hash_name in ("source_sha256", "rendered_sha256"):
            if page.get(hash_name) != expected[hash_name]:
                errors.append(f"{page_id}: {hash_name} does not match the current artifact")
        for path_name in ("source", "rendered"):
            if page.get(path_name) != expected[path_name]:
                errors.append(f"{page_id}: {path_name} path does not match the current artifact")
        checks = page.get("checks")
        if not isinstance(checks, dict):
            errors.append(f"{page_id}: checks must be an object")
            continue
        for name in expected["required_checks"]:
            if not observation_is_specific(checks.get(name)):
                errors.append(
                    f"{page_id}: check {name} requires a specific observation of at least 12 characters"
                )
    return payload, errors
