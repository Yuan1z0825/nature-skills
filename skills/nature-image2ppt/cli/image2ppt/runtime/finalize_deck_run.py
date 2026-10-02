#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

from deck_run_state import load_deck, load_jobs, now_iso, resolve_inside, run_dir_from_target, save_deck, save_jobs, set_run_status, write_json


SCRIPT_DIR = Path(__file__).resolve().parent


def run(command):
    print("+ " + " ".join(str(part) for part in command), flush=True)
    subprocess.run([str(part) for part in command], check=True)


def final_output_path(run_dir, deck):
    try:
        return resolve_inside(run_dir, deck.get("output", "final/deck_edited.pptx"))
    except ValueError as exc:
        raise SystemExit(f"Final output must stay inside run directory: {deck.get('output')}") from exc


def assert_pages_ready(run_dir, jobs):
    problems = []
    for page in jobs.get("pages", []):
        if page.get("status") not in {"recorded", "accepted"}:
            problems.append(f"{page['page_id']} status={page.get('status')}")
            continue
        result = page.get("result") or {}
        if result.get("validation_passed") is not True:
            problems.append(f"{page['page_id']} validation_passed={result.get('validation_passed')}")
    if problems:
        raise SystemExit("Pages are not ready for finalize:\n" + "\n".join(problems))


def main():
    parser = argparse.ArgumentParser(description="Build and validate the final editable PPTX from recorded pages.")
    parser.add_argument("run", help="Run directory or deck_manifest.json")
    args = parser.parse_args()

    run_dir = run_dir_from_target(args.run)
    deck = load_deck(run_dir)
    jobs = load_jobs(run_dir)
    assert_pages_ready(run_dir, jobs)

    out = final_output_path(run_dir, deck)
    out.parent.mkdir(parents=True, exist_ok=True)
    run([sys.executable, SCRIPT_DIR / "build_pptx_from_manifest.py", "--deck-manifest", run_dir / "deck_manifest.json", "--out", out])
    set_run_status(run_dir, "deck_built", "final pptx built")

    validation = out.parent / "validation.json"
    run([sys.executable, SCRIPT_DIR / "validate_pptx.py", out, "--deck-manifest", run_dir / "deck_manifest.json", "--report", validation])
    set_run_status(run_dir, "deck_validated", "final pptx validation passed")

    for page in jobs.get("pages", []):
        page["status"] = "accepted"
        page["accepted"] = True
        page["accepted_at"] = now_iso()
    jobs["run_status"] = "complete"
    jobs["updated_at"] = now_iso()
    save_jobs(run_dir, jobs)
    deck["completed_at"] = now_iso()
    save_deck(run_dir, deck)
    summary = {
        "schema_version": 1,
        "run_id": deck.get("run_id"),
        "status": "complete",
        "page_count": len(jobs.get("pages", [])),
        "output": str(out),
        "validation": str(validation),
        "completed_at": now_iso(),
    }
    write_json(out.parent / "run_summary.json", summary)
    set_run_status(run_dir, "complete", "final deck complete")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
