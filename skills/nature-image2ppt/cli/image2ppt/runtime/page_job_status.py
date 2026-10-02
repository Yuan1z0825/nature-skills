#!/usr/bin/env python3
import argparse
import json
from collections import Counter, defaultdict

from deck_run_state import (
    active_pages,
    dispatch_slots_available,
    dispatchable_pages,
    load_jobs,
    load_run_state,
    max_concurrent_pages,
    run_dir_from_target,
)


def main():
    parser = argparse.ArgumentParser(description="Print page job status without modifying run state.")
    parser.add_argument("run", help="Run directory or deck_manifest.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    run_dir = run_dir_from_target(args.run)
    jobs = load_jobs(run_dir)
    state = load_run_state(run_dir)
    by_status = defaultdict(list)
    for page in jobs.get("pages", []):
        by_status[page.get("status", "unknown")].append(page.get("page_id"))
    summary = {
        "run_dir": str(run_dir),
        "run_status": state.get("status"),
        "page_count": len(jobs.get("pages", [])),
        "max_concurrent_pages": max_concurrent_pages(jobs),
        "active_dispatches": [page.get("page_id") for page in active_pages(jobs)],
        "dispatch_slots_available": dispatch_slots_available(jobs),
        "dispatchable_pages": [page.get("page_id") for page in dispatchable_pages(jobs)],
        "counts": dict(Counter(page.get("status", "unknown") for page in jobs.get("pages", []))),
        "pages": dict(sorted(by_status.items())),
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return
    print(f"run_dir={summary['run_dir']}")
    print(f"run_status={summary['run_status']}")
    print(f"max_concurrent_pages={summary['max_concurrent_pages']}")
    print(f"active_dispatches={', '.join(summary['active_dispatches']) if summary['active_dispatches'] else '-'}")
    print(f"dispatch_slots_available={summary['dispatch_slots_available']}")
    print(f"dispatchable_pages={', '.join(summary['dispatchable_pages']) if summary['dispatchable_pages'] else '-'}")
    for status, pages in summary["pages"].items():
        print(f"{status}: {', '.join(pages) if pages else '-'}")


if __name__ == "__main__":
    main()
