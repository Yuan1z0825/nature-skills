#!/usr/bin/env python3
"""Validate workflow path filters and immutable GitHub Action references.

The repository has several focused validators with `paths` filters so routine
skill edits only run the relevant CI jobs. This check keeps those filters honest:
if a workflow runs a local validation script, changes to that script must be in
both pull_request and push path filters. Otherwise a broken validator can be
edited without triggering its own CI job.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - developer environment guard
    raise SystemExit("Missing dependency: PyYAML. Install with `python -m pip install pyyaml`.") from exc

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = ROOT / ".github" / "workflows"
LOCAL_SCRIPT_RE = re.compile(r"\b(?:python3?|bash|sh)\s+(scripts/[\w./-]+)")
PINNED_ACTION_RE = re.compile(r"^[^@\s]+@[0-9a-fA-F]{40}$")


def read_workflow(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def workflow_events(workflow: dict[str, Any]) -> dict[str, Any]:
    # PyYAML 1.1 treats the key `on` as a boolean unless a custom loader is used.
    # Accept both forms so the validator remains portable across environments.
    events = workflow.get("on", workflow.get(True, {}))
    return events if isinstance(events, dict) else {}


def normalized_paths(event_config: Any) -> set[str] | None:
    if not isinstance(event_config, dict):
        return None
    paths = event_config.get("paths")
    if paths is None:
        return None
    if not isinstance(paths, list):
        return set()
    return {str(item) for item in paths}


def local_scripts_from_run_steps(workflow: dict[str, Any]) -> set[str]:
    scripts: set[str] = set()
    jobs = workflow.get("jobs", {})
    if not isinstance(jobs, dict):
        return scripts
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        steps = job.get("steps", [])
        if not isinstance(steps, list):
            continue
        for step in steps:
            if not isinstance(step, dict):
                continue
            run = step.get("run")
            if not isinstance(run, str):
                continue
            scripts.update(LOCAL_SCRIPT_RE.findall(run))
    return scripts


def external_action_references(workflow: dict[str, Any]) -> set[str]:
    references: set[str] = set()
    jobs = workflow.get("jobs", {})
    if not isinstance(jobs, dict):
        return references
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        job_uses = job.get("uses")
        if isinstance(job_uses, str):
            references.add(job_uses)
        steps = job.get("steps", [])
        if not isinstance(steps, list):
            continue
        for step in steps:
            if not isinstance(step, dict):
                continue
            step_uses = step.get("uses")
            if isinstance(step_uses, str):
                references.add(step_uses)
    return references


def validate_workflow(path: Path) -> list[str]:
    workflow = read_workflow(path)
    scripts = local_scripts_from_run_steps(workflow)
    errors: list[str] = []
    events = workflow_events(workflow)
    for event_name in ("pull_request", "push"):
        paths = normalized_paths(events.get(event_name))
        if paths is None:
            continue
        missing = sorted(script for script in scripts if script not in paths)
        if missing:
            errors.append(
                f"{path.relative_to(ROOT)}: {event_name}.paths missing "
                + ", ".join(missing)
            )

    for reference in sorted(external_action_references(workflow)):
        if reference.startswith(("./", "docker://")):
            continue
        if not PINNED_ACTION_RE.fullmatch(reference):
            errors.append(
                f"{path.relative_to(ROOT)}: action reference must use a full 40-character "
                f"commit SHA: {reference}"
            )
    return errors


def main() -> int:
    if not WORKFLOWS_DIR.is_dir():
        print(f"ERROR: workflow directory not found: {WORKFLOWS_DIR}", file=sys.stderr)
        return 1

    errors: list[str] = []
    workflows = sorted(WORKFLOWS_DIR.glob("*.yml")) + sorted(WORKFLOWS_DIR.glob("*.yaml"))
    for path in workflows:
        errors.extend(validate_workflow(path))

    if errors:
        print("Workflow validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Workflow validation passed: {len(workflows)} workflow files checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
