#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

from deck_run_state import (
    find_page,
    inside_or_missing,
    load_jobs,
    now_iso,
    page_dir_for,
    read_json,
    rel_to_run,
    run_dir_from_target,
    save_jobs,
    set_run_status,
    sha256_file,
    update_jobs_run_status,
)


REQUIRED_OUTPUTS = {
    "page_manifest": "manifest.json",
    "imagegen_jobs": "imagegen-jobs.json",
    "page_pptx": "page.pptx",
    "preview": "preview.png",
    "contact_sheet": "split_assets_contact.png",
    "validation": "validation.json",
    "page_result": "page_result.json",
}


SCRIPT_DIR = Path(__file__).resolve().parent


def output_path(page_dir, result, key, default):
    value = result.get(key) or default
    return inside_or_missing(page_dir, value)


def validate_page_contract(paths):
    command = [
        sys.executable,
        SCRIPT_DIR / "validate_pptx.py",
        paths["page_pptx"],
        "--manifest",
        paths["page_manifest"],
    ]
    result = subprocess.run([str(part) for part in command], text=True, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(
            "Page manifest contract validation failed before recording:\n"
            + result.stdout
            + result.stderr
        )


def main():
    parser = argparse.ArgumentParser(description="Record and verify a page reconstruction result.")
    parser.add_argument("run", help="Run directory or deck_manifest.json")
    parser.add_argument("--page", required=True, help="page_001 or 1")
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--page-result", default="page_result.json")
    args = parser.parse_args()

    run_dir = run_dir_from_target(args.run)
    jobs = load_jobs(run_dir)
    page = find_page(jobs, args.page)
    if page.get("status") == "dispatched":
        dispatch = page.get("dispatch") or {}
        if dispatch.get("agent_id") != args.agent_id:
            raise SystemExit(
                f"Agent id mismatch for {page['page_id']}: dispatch={dispatch.get('agent_id')} result={args.agent_id}"
            )
        execution_mode = dispatch.get("execution_mode") or "worker"
        record_mode = "local-main-agent" if execution_mode == "local" else "dispatched-worker"
    elif page.get("status") == "recorded":
        previous = page.get("result") or {}
        if previous.get("agent_id") != args.agent_id:
            raise SystemExit(
                f"Agent id mismatch for recorded {page['page_id']}: previous={previous.get('agent_id')} result={args.agent_id}"
            )
        record_mode = previous.get("record_mode") or "refresh-recorded-page"
    else:
        raise SystemExit(f"{page['page_id']} must be dispatched before result recording; got {page.get('status')}")

    page_dir = page_dir_for(run_dir, page)
    page_result_path = inside_or_missing(page_dir, args.page_result)
    result = read_json(page_result_path)
    validation_path = output_path(page_dir, result, "validation", REQUIRED_OUTPUTS["validation"])
    validation = read_json(validation_path)
    validation_passed = validation.get("passed") is True
    if not validation_passed:
        raise SystemExit(
            f"{page['page_id']} validation.json does not contain top-level \"passed\": true; "
            "the page is not deliverable and was not recorded. Inspect the worker's "
            "validation.json for the failure reason, fix the root cause, then run "
            f"`image2ppt run reset {run_dir} --page {page['page_id']} "
            f"--agent-id {args.agent_id} --confirm-lost` and dispatch a new worker."
        )
    paths = {key: output_path(page_dir, result, key, default) for key, default in REQUIRED_OUTPUTS.items()}
    validate_page_contract(paths)
    hashes = {key: sha256_file(path) for key, path in paths.items()}
    page["result"] = {
        "agent_id": args.agent_id,
        "record_mode": record_mode,
        "recorded_at": now_iso(),
        "outputs": {key: rel_to_run(run_dir, path) for key, path in paths.items()},
        "hashes": hashes,
        "validation_passed": validation_passed,
    }
    page["status"] = "recorded"
    update_jobs_run_status(jobs)
    save_jobs(run_dir, jobs)
    if jobs.get("run_status") == "pages_recorded":
        set_run_status(run_dir, "pages_recorded", "all pages recorded")
    print(json.dumps({"page_id": page["page_id"], "status": "recorded", "validation_passed": validation_passed}, ensure_ascii=False))


if __name__ == "__main__":
    main()
