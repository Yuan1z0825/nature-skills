#!/usr/bin/env python3
"""Postprocess and validate the final deck produced by ``image2ppt run finalize``."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from render_image2ppt_qa import image_diff
from runtime_paths import SCRIPT_DIR, image2ppt_runtime_script, resolve_inside
from postprocess_manifest_arrows import load_run_manifests, read_json, write_json
from visual_review_evidence import expected_page, validate_evidence, write_template


def run(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout[-8000:],
        "stderr": result.stderr[-8000:],
    }


def safe_json(path: Path) -> dict[str, Any]:
    try:
        return read_json(path) if path.is_file() else {}
    except (OSError, ValueError, TypeError):
        return {}


def page_source_entries(run_dir: Path) -> list[tuple[str, Path]]:
    deck = read_json(run_dir / "deck_manifest.json")
    sources: list[tuple[str, Path]] = []
    for page in deck.get("pages") or []:
        raw = str(page.get("source_image") or "").strip()
        if not raw:
            continue
        sources.append(
            (
                str(page.get("page_id") or f"page_{len(sources) + 1:03d}"),
                resolve_inside(run_dir, raw),
            )
        )
    return sources


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply Image2PPT arrows and supplemental QA to a finalized image2ppt deck")
    parser.add_argument("run", type=Path)
    parser.add_argument("--pptx", type=Path)
    parser.add_argument("--visual-review-status", choices=["needs_review", "reviewed", "failed"], default="needs_review")
    parser.add_argument("--visual-review-notes", default="")
    parser.add_argument("--visual-review-evidence", type=Path)
    parser.add_argument("--render-timeout", type=int, default=180)
    args = parser.parse_args()

    run_dir = args.run.expanduser().resolve()
    manifests, default_pptx = load_run_manifests(run_dir)
    try:
        pptx = resolve_inside(run_dir, args.pptx) if args.pptx else default_pptx
    except ValueError as exc:
        raise SystemExit(f"Final QA PPTX must stay inside run directory: {args.pptx}") from exc
    final_dir = pptx.parent
    paths = {
        "postprocess": final_dir / "image2ppt_arrow_postprocess.json",
        "regions": final_dir / "image2ppt_region_decomposition.json",
        "structural": final_dir / "image2ppt_structural_validation.json",
        "inspection": final_dir / "image2ppt_arrow_inspection.json",
        "render": final_dir / "image2ppt_render_report.json",
        "report": final_dir / "image2ppt_qa.json",
        "review_template": final_dir / "visual-review-evidence.template.json",
    }
    errors: list[str] = []
    checks: dict[str, Any] = {}
    expected_review_pages: list[dict[str, Any]] = []
    review_evidence: dict[str, Any] = {}
    review_evidence_path: Path | None = None
    if not pptx.is_file():
        errors.append(f"image2ppt final output is missing: {pptx}")

    if not errors:
        command = [
            sys.executable,
            str(SCRIPT_DIR / "inspect_region_decomposition.py"),
            "--run",
            str(run_dir),
            "--out",
            str(paths["regions"]),
        ]
        checks["region_decomposition_command"] = run(command)
        checks["region_decomposition"] = safe_json(paths["regions"])
        if (
            checks["region_decomposition_command"]["returncode"] != 0
            or checks["region_decomposition"].get("passed") is not True
        ):
            errors.append("final semantic-region or compound-diagram inspection failed")

    if not errors:
        command = [
            sys.executable,
            str(SCRIPT_DIR / "postprocess_manifest_arrows.py"),
            str(pptx),
            "--run",
            str(run_dir),
            "--report",
            str(paths["postprocess"]),
        ]
        checks["postprocess_command"] = run(command)
        checks["postprocess"] = safe_json(paths["postprocess"])
        if checks["postprocess_command"]["returncode"] != 0 or checks["postprocess"].get("passed") is not True:
            errors.append("final arrow postprocessing failed")

    if not errors:
        command = [
            sys.executable,
            str(image2ppt_runtime_script("validate_pptx.py")),
            str(pptx),
            "--deck-manifest",
            str(run_dir / "deck_manifest.json"),
            "--report",
            str(paths["structural"]),
        ]
        checks["image2ppt_validation_command"] = run(command)
        checks["image2ppt_validation"] = safe_json(paths["structural"])
        if checks["image2ppt_validation_command"]["returncode"] != 0 or checks["image2ppt_validation"].get("passed") is not True:
            errors.append("local image2ppt deck validation failed after arrow postprocessing")

    if not errors:
        command = [
            sys.executable,
            str(SCRIPT_DIR / "inspect_arrow_atomicity.py"),
            str(pptx),
            "--run",
            str(run_dir),
            "--out",
            str(paths["inspection"]),
        ]
        checks["arrow_inspection_command"] = run(command)
        checks["arrow_inspection"] = safe_json(paths["inspection"])
        if checks["arrow_inspection_command"]["returncode"] != 0 or checks["arrow_inspection"].get("passed") is not True:
            errors.append("final one-arrow-one-object inspection failed")

    if not errors:
        render_dir = final_dir / "image2ppt_render"
        command = [
            sys.executable,
            str(SCRIPT_DIR / "render_image2ppt_qa.py"),
            str(pptx),
            "--out-dir",
            str(render_dir),
            "--report",
            str(paths["render"]),
            "--timeout",
            str(args.render_timeout),
        ]
        checks["render_command"] = run(command)
        checks["render"] = safe_json(paths["render"])
        if checks["render_command"]["returncode"] != 0 or checks["render"].get("status") != "rendered":
            errors.append("final PowerPoint/LibreOffice render failed")
        else:
            rendered = [Path(value) for value in checks["render"].get("rendered_slides") or []]
            source_entries = page_source_entries(run_dir)
            if len(rendered) != len(source_entries) or len(manifests) != len(source_entries):
                errors.append(
                    "render/source/manifest page count mismatch: "
                    f"rendered={len(rendered)} source={len(source_entries)} manifests={len(manifests)}"
                )
            else:
                checks["page_diff_metrics"] = [
                    {"page_index": index, **image_diff(source, image)}
                    for index, ((_page_id, source), image) in enumerate(zip(source_entries, rendered), start=1)
                ]
                expected_review_pages = [
                    expected_page(
                        page_id=page_id,
                        source=source,
                        rendered=image,
                        manifest=read_json(manifest),
                    )
                    for (page_id, source), image, manifest in zip(source_entries, rendered, manifests)
                ]
                write_template(paths["review_template"], expected_review_pages)

    if args.visual_review_status == "reviewed":
        try:
            review_evidence_path = resolve_inside(
                final_dir, args.visual_review_evidence or "visual-review-evidence.json"
            )
        except ValueError as exc:
            errors.append(str(exc))
        if review_evidence_path and expected_review_pages:
            review_evidence, evidence_errors = validate_evidence(
                review_evidence_path, expected_review_pages
            )
            errors.extend(evidence_errors)
        elif not expected_review_pages:
            errors.append("reviewed final QA requires successful current renders for every page")
    if args.visual_review_status == "failed":
        errors.append("final source-versus-render comparison was marked failed")
    passed = not errors and args.visual_review_status == "reviewed"
    report = {
        "schema_version": "image2ppt-supplemental-final-qa-v1",
        "passed": passed,
        "state_owner": "page_jobs.json",
        "pptx": str(pptx),
        "manifests": [str(path) for path in manifests],
        "visual_review": {
            "status": args.visual_review_status,
            "notes": args.visual_review_notes,
            "evidence": str(review_evidence_path) if review_evidence_path else None,
            "evidence_template": str(paths["review_template"]),
            "evidence_payload": review_evidence,
        },
        "checks": checks,
        "errors": errors,
    }
    write_json(paths["report"], report)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
