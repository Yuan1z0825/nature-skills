#!/usr/bin/env python3
"""Run Image2PPT's supplemental page gate on standard image2ppt artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from runtime_paths import SCRIPT_DIR, image2ppt_command, resolve_inside
from visual_review_evidence import expected_page, validate_evidence, write_template


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except (OSError, ValueError, TypeError):
        return {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout[-8000:],
        "stderr": result.stderr[-8000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect regions, postprocess arrows, rerun image2ppt validation, inspect atomicity, and render one page"
    )
    parser.add_argument("page_dir", type=Path)
    parser.add_argument("--visual-review-status", choices=["needs_review", "reviewed", "failed"], default="needs_review")
    parser.add_argument("--visual-review-notes", default="")
    parser.add_argument("--visual-review-evidence", type=Path)
    parser.add_argument("--existing-rendered", type=Path)
    parser.add_argument("--render-timeout", type=int, default=120)
    args = parser.parse_args()

    page_dir = args.page_dir.expanduser().resolve()
    manifest = page_dir / "manifest.json"
    pptx = page_dir / "page.pptx"
    source = page_dir / "source.png"
    paths = {
        "postprocess": page_dir / "arrow_postprocess_report.json",
        "regions": page_dir / "region_decomposition_report.json",
        "source_validation": page_dir / "validation.json",
        "inspection": page_dir / "arrow_inspection_report.json",
        "render": page_dir / "render_report.json",
        "profile": page_dir / "image2ppt_qa.json",
        "review_template": page_dir / "visual-review-evidence.template.json",
    }
    errors: list[str] = []
    checks: dict[str, Any] = {}
    expected_review_pages: list[dict[str, Any]] = []
    review_evidence: dict[str, Any] = {}
    review_evidence_path: Path | None = None
    for path, label in ((manifest, "manifest.json"), (pptx, "page.pptx"), (source, "source.png")):
        if not path.is_file():
            errors.append(f"missing standard image2ppt artifact: {label}")

    if not errors:
        command = [
            sys.executable,
            str(SCRIPT_DIR / "inspect_region_decomposition.py"),
            "--manifest",
            str(manifest),
            "--out",
            str(paths["regions"]),
        ]
        checks["region_decomposition_command"] = run(command)
        checks["region_decomposition"] = read_json(paths["regions"])
        if (
            checks["region_decomposition_command"]["returncode"] != 0
            or checks["region_decomposition"].get("passed") is not True
        ):
            errors.append("semantic-region or compound-diagram inspection failed")

    if not errors:
        command = [
            sys.executable,
            str(SCRIPT_DIR / "postprocess_manifest_arrows.py"),
            str(pptx),
            "--manifest",
            str(manifest),
            "--report",
            str(paths["postprocess"]),
        ]
        checks["arrow_postprocess_command"] = run(command)
        checks["arrow_postprocess"] = read_json(paths["postprocess"])
        if checks["arrow_postprocess_command"]["returncode"] != 0 or checks["arrow_postprocess"].get("passed") is not True:
            errors.append("manifest arrow postprocessing failed")

    if not errors:
        command = [
            *image2ppt_command(),
            "page",
            "validate",
            str(page_dir),
            "--report",
            "validation.json",
        ]
        checks["image2ppt_validation_command"] = run(command)
        checks["image2ppt_validation"] = read_json(paths["source_validation"])
        if checks["image2ppt_validation_command"]["returncode"] != 0 or checks["image2ppt_validation"].get("passed") is not True:
            errors.append("local image2ppt page validation failed after arrow postprocessing")

    if not errors:
        command = [
            sys.executable,
            str(SCRIPT_DIR / "inspect_arrow_atomicity.py"),
            str(pptx),
            "--manifest",
            str(manifest),
            "--out",
            str(paths["inspection"]),
        ]
        checks["arrow_inspection_command"] = run(command)
        checks["arrow_inspection"] = read_json(paths["inspection"])
        if checks["arrow_inspection_command"]["returncode"] != 0 or checks["arrow_inspection"].get("passed") is not True:
            errors.append("one-arrow-one-object inspection failed")

    if not errors:
        command = [
            sys.executable,
            str(SCRIPT_DIR / "render_image2ppt_qa.py"),
            str(pptx),
            "--out-dir",
            str(page_dir / "render"),
            "--report",
            str(paths["render"]),
            "--source",
            str(source),
            "--timeout",
            str(args.render_timeout),
        ]
        if args.existing_rendered:
            try:
                existing_rendered = resolve_inside(page_dir, args.existing_rendered)
            except ValueError as exc:
                raise SystemExit(
                    f"existing render must stay inside page directory: {args.existing_rendered}"
                ) from exc
            command.extend(["--existing-rendered", str(existing_rendered)])
        checks["render_command"] = run(command)
        checks["render"] = read_json(paths["render"])
        if checks["render_command"]["returncode"] != 0 or checks["render"].get("status") != "rendered":
            errors.append("PowerPoint/LibreOffice rendered QA failed")
        else:
            rendered = page_dir / "render" / "rendered.png"
            expected_review_pages = [
                expected_page(
                    page_id=page_dir.name,
                    source=source,
                    rendered=rendered,
                    manifest=read_json(manifest),
                )
            ]
            write_template(paths["review_template"], expected_review_pages)

    if args.visual_review_status == "reviewed":
        try:
            review_evidence_path = resolve_inside(
                page_dir, args.visual_review_evidence or "visual-review-evidence.json"
            )
        except ValueError as exc:
            errors.append(str(exc))
        if review_evidence_path and expected_review_pages:
            review_evidence, evidence_errors = validate_evidence(
                review_evidence_path, expected_review_pages
            )
            errors.extend(evidence_errors)
        elif not expected_review_pages:
            errors.append("reviewed visual QA requires a successful current render")
    if args.visual_review_status == "failed":
        errors.append("source-versus-render comparison was marked failed")
    passed = not errors and args.visual_review_status == "reviewed"
    report = {
        "schema_version": "image2ppt-supplemental-page-qa-v1",
        "passed": passed,
        "page_dir": str(page_dir),
        "state_owner": "page_jobs.json",
        "manifest": str(manifest),
        "pptx": str(pptx),
        "visual_review": {
            "status": args.visual_review_status,
            "notes": args.visual_review_notes,
            "source": str(source),
            "rendered": str(page_dir / "render" / "rendered.png"),
            "evidence": str(review_evidence_path) if review_evidence_path else None,
            "evidence_template": str(paths["review_template"]),
            "evidence_payload": review_evidence,
        },
        "checks": checks,
        "errors": errors,
    }
    write_json(paths["profile"], report)

    # Keep the local validation document authoritative while adding the
    # supplemental gate that image2ppt run record reads through top-level passed.
    validation = read_json(paths["source_validation"])
    if not validation:
        validation = {"passed": False}
    validation["image2ppt_profile"] = {
        "passed": passed,
        "report": paths["profile"].name,
        "arrow_postprocess": paths["postprocess"].name,
        "arrow_inspection": paths["inspection"].name,
        "region_decomposition": paths["regions"].name,
        "render_report": paths["render"].name,
        "visual_review_status": args.visual_review_status,
        "visual_review_evidence": (
            str(review_evidence_path.relative_to(page_dir)) if review_evidence_path else None
        ),
        "errors": errors,
    }
    validation["passed"] = bool(validation.get("passed") is True and passed)
    write_json(paths["source_validation"], validation)
    # stdout may use a legacy code page on Windows CI. JSON escapes preserve
    # Unicode content while keeping the command-line transport ASCII-safe.
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
