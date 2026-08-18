#!/usr/bin/env python3
"""Resolve only resources bundled inside the Image2PPT Skill."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
CLI_ENTRY = SKILL_ROOT / "cli" / "image2ppt" / "cli.py"
RUNTIME_ROOT = SKILL_ROOT / "cli" / "image2ppt" / "runtime"


def resolve_inside(base: Path, value: str | Path) -> Path:
    """Resolve a task path and reject traversal or absolute-path escape."""

    root = base.expanduser().resolve()
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path must stay inside {root}: {value}") from exc
    return candidate


def image2ppt_command() -> list[str]:
    """Return the source-tree CLI command for this exact Skill checkout."""

    return [sys.executable, str(CLI_ENTRY)]


def image2ppt_runtime_script(name: str) -> Path:
    """Resolve a runtime module and reject paths outside the bundled runtime."""

    candidate = (RUNTIME_ROOT / name).resolve()
    try:
        candidate.relative_to(RUNTIME_ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"runtime module must stay inside {RUNTIME_ROOT}: {name}") from exc
    return candidate


def required_runtime_files() -> dict[str, Path]:
    """Return the complete local resource surface required by the workflow."""

    files = {
        "skill": SKILL_ROOT / "SKILL.md",
        "cli": CLI_ENTRY,
        "package_manifest": SKILL_ROOT / "cli" / "pyproject.toml",
        "worker_prompt_base": SKILL_ROOT / "prompts" / "page-worker-base.md",
        "worker_prompt_addendum": SKILL_ROOT / "prompts" / "page-worker.md",
        "prompt_builder": SCRIPT_DIR / "build_page_worker_prompt.py",
        "arrow_postprocessor": SCRIPT_DIR / "postprocess_manifest_arrows.py",
        "arrow_inspector": SCRIPT_DIR / "inspect_arrow_atomicity.py",
        "region_inspector": SCRIPT_DIR / "inspect_region_decomposition.py",
        "page_qa": SCRIPT_DIR / "run_image2ppt_qa.py",
        "final_qa": SCRIPT_DIR / "run_final_image2ppt_qa.py",
        "visual_review_evidence": SCRIPT_DIR / "visual_review_evidence.py",
        "renderer": SCRIPT_DIR / "render_image2ppt_qa.py",
        "manifest_schema": SKILL_ROOT / "references" / "manifest-schema.md",
        "manifest_json_schema": SKILL_ROOT / "schemas" / "page-manifest-v2.schema.json",
        "decision_tree": SKILL_ROOT / "references" / "page-decision-tree.md",
        "cli_contract": SKILL_ROOT / "references" / "cli-helper.md",
        "ocr_contract": SKILL_ROOT / "references" / "ocr-text-hints-contract.md",
        "region_contract": SKILL_ROOT / "references" / "region-decomposition.md",
        "object_routing": SKILL_ROOT / "references" / "object-routing.md",
        "arrow_contract": SKILL_ROOT / "references" / "manifest-arrow-extension.md",
        "qa_contract": SKILL_ROOT / "references" / "qa-contract.md",
        "dependency_contract": SKILL_ROOT / "references" / "runtime-dependencies.md",
        "asset_contract": SKILL_ROOT / "references" / "assets-provenance-contract.md",
    }
    for module in (
        "_input_normalization.py",
        "build_pptx_from_manifest.py",
        "deck_run_state.py",
        "deck_text_hints.py",
        "finalize_deck_run.py",
        "paddle_text_hints.py",
        "prepare_deck_run.py",
        "runtime_env.py",
        "text_hints.py",
        "validate_pptx.py",
    ):
        files[f"runtime_{module.removesuffix('.py')}"] = image2ppt_runtime_script(module)
    return files


def runtime_path_report() -> dict[str, Any]:
    files = required_runtime_files()
    return {
        "skill_root": str(SKILL_ROOT),
        "cli_entry": str(CLI_ENTRY),
        "runtime_root": str(RUNTIME_ROOT),
        "command": image2ppt_command(),
        "files": {
            key: {"path": str(path), "exists": path.is_file()}
            for key, path in files.items()
        },
    }
