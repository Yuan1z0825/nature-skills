#!/usr/bin/env python3
"""Reset a failed or inactive page back to pending so it can be re-dispatched."""
import argparse
import json

from deck_run_state import (
    find_page,
    load_jobs,
    now_iso,
    run_dir_from_target,
    save_jobs,
    update_jobs_run_status,
)


def main():
    parser = argparse.ArgumentParser(
        description="Reset a dispatched or recorded page back to pending for re-dispatch."
    )
    parser.add_argument("run", help="Run directory or deck_manifest.json")
    parser.add_argument("--page", required=True, help="page_001 or 1")
    parser.add_argument("--agent-id", help="Required for dispatched pages; must match the recorded worker id.")
    parser.add_argument(
        "--confirm-lost",
        action="store_true",
        help="Required for dispatched pages. Confirms the original worker is no longer active or must be abandoned.",
    )
    args = parser.parse_args()

    run_dir = run_dir_from_target(args.run)
    jobs = load_jobs(run_dir)
    page = find_page(jobs, args.page)
    status = page.get("status")
    if status not in {"dispatched", "recorded"}:
        raise SystemExit(
            f"{page['page_id']} cannot be reset from status {status}; "
            "reset only applies to dispatched or recorded pages"
        )
    if status == "dispatched":
        dispatch = page.get("dispatch") or {}
        expected_agent_id = dispatch.get("agent_id")
        if not args.confirm_lost:
            raise SystemExit(
                f"{page['page_id']} is still dispatched. Do not reset active workers because they are slow. "
                "Use --confirm-lost with --agent-id only after explicit worker failure, terminal state, "
                "user cancellation, or lost-worker verification."
            )
        if not args.agent_id:
            raise SystemExit(f"{page['page_id']} dispatched reset requires --agent-id.")
        if expected_agent_id and args.agent_id != expected_agent_id:
            raise SystemExit(
                f"Agent id mismatch for {page['page_id']}: "
                f"dispatch={expected_agent_id} reset={args.agent_id}"
            )
    page["status"] = "pending"
    page["dispatch"] = None
    page["result"] = None
    page["reset_at"] = now_iso()
    update_jobs_run_status(jobs)
    save_jobs(run_dir, jobs)
    print(
        json.dumps(
            {
                "page_id": page["page_id"],
                "status": "pending",
                "next": "rebuild the worker prompt and dispatch a new worker",
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
