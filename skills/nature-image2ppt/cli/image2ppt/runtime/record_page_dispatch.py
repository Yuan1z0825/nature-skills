#!/usr/bin/env python3
import argparse
from pathlib import Path

from deck_run_state import (
    find_page,
    load_jobs,
    now_iso,
    page_dir_for,
    rel_to_run,
    run_dir_from_target,
    save_jobs,
    set_run_status,
    sha256_file,
    update_jobs_run_status,
)


def resolve_prompt_path(run_dir, page_dir, value):
    path = Path(value).expanduser()
    if path.is_absolute():
        prompt_path = path.resolve()
    elif path.parts[:1] == ("pages",):
        prompt_path = (run_dir / path).resolve()
    else:
        prompt_path = (page_dir / path).resolve()
    try:
        prompt_path.relative_to(page_dir)
    except ValueError as exc:
        raise SystemExit(f"Prompt file must live inside page dir: {prompt_path}") from exc
    return prompt_path


def main():
    parser = argparse.ArgumentParser(description="Record that a page was dispatched to a worker or claimed for local reconstruction.")
    parser.add_argument("run", help="Run directory or deck_manifest.json")
    parser.add_argument("--page", required=True, help="page_001 or 1")
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--agent-nickname")
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--local", action="store_true", help="Claim a single-page run for main-agent local reconstruction.")
    args = parser.parse_args()

    run_dir = run_dir_from_target(args.run)
    jobs = load_jobs(run_dir)
    page = find_page(jobs, args.page)
    page_dir = page_dir_for(run_dir, page)
    prompt_path = resolve_prompt_path(run_dir, page_dir, args.prompt_file)
    if not prompt_path.exists():
        raise SystemExit(f"Prompt file does not exist: {prompt_path}")

    if page.get("status") != "pending":
        raise SystemExit(f"{page['page_id']} must be pending before dispatch; got {page.get('status')}")
    if args.local and len(jobs.get("pages", [])) != 1:
        raise SystemExit("--local dispatch is only allowed when the run has exactly one page")

    page_request = (run_dir / page["page_request"]).resolve()
    if not page_request.exists():
        raise SystemExit(f"Missing page_request.json: {page_request}")

    page["dispatch"] = {
        "agent_id": args.agent_id,
        "agent_nickname": args.agent_nickname,
        "prompt": rel_to_run(run_dir, prompt_path),
        "prompt_sha256": sha256_file(prompt_path),
        "page_request_sha256": sha256_file(page_request),
        "dispatched_at": now_iso(),
        "execution_mode": "local" if args.local else "worker",
    }
    page["status"] = "dispatched"
    update_jobs_run_status(jobs)
    save_jobs(run_dir, jobs)
    if jobs.get("run_status") == "pages_dispatched":
        set_run_status(run_dir, "pages_dispatched", "all pages dispatched")
    print(f"{page['page_id']} -> dispatched")


if __name__ == "__main__":
    main()
