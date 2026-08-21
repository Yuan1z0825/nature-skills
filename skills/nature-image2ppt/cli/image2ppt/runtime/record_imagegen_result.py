#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from deck_run_state import now_iso, read_json, resolve_inside, sha256_file, write_json


def main():
    parser = argparse.ArgumentParser(
        prog="image2ppt image import",
        description="Copy a selected generated image into a page directory and record provenance.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  image2ppt image import <page_dir> --job-id clean-base-1 --source-image /tmp/generated.png --dest assets/clean_base.png --role clean_base --backend builtin-imagegen
  image2ppt image import <page_dir> --job-id icon-sheet-1 --source-image sheet.png --dest assets/sheet.png --role asset_sheet --prompt-file prompts/icon-sheet.md --backend codex-oauth --fallback-reason tool-error
""",
    )
    parser.add_argument("page_dir", help="Page directory that owns imagegen-jobs.json and receives the copied asset.")
    parser.add_argument("--job-id", required=True, help="Stable job id to create or update inside imagegen-jobs.json.")
    parser.add_argument("--source-image", required=True, help="Generated image selected by the agent, usually from image2ppt image output or another approved image backend output.")
    parser.add_argument("--dest", required=True, help="Destination path relative to page_dir; absolute paths are rejected.")
    parser.add_argument("--role", default="asset", help="Asset role recorded in the job, for example clean_base, asset_sheet, or asset.")
    parser.add_argument("--prompt-file", help="Optional prompt file path used to create the selected image.")
    parser.add_argument(
        "--backend",
        choices=["builtin-imagegen", "codex-oauth", "openai-compatible-api", "unknown"],
        required=True,
        help="Actual image backend that produced the selected image.",
    )
    parser.add_argument(
        "--model",
        help="Optional exact image model id reported or requested for this output.",
    )
    parser.add_argument(
        "--fallback-reason",
        choices=["tool-unavailable", "tool-error", "input-unreadable", "no-valid-local-output"],
        help="Optional fallback event explaining why the preferred image backend was not used.",
    )
    parser.add_argument("--note", help="Short provenance or approval note recorded with the job.")
    args = parser.parse_args()

    page_dir = Path(args.page_dir).resolve()
    if not page_dir.exists():
        raise SystemExit(f"Page dir does not exist: {page_dir}")
    source = Path(args.source_image).expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"Generated image is not a file: {source}")
    try:
        with Image.open(source) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise SystemExit(f"Generated image is unreadable: {source}: {exc}") from exc

    cli_backends = {"codex-oauth", "openai-compatible-api"}
    if args.fallback_reason and args.backend not in cli_backends:
        raise SystemExit("--fallback-reason requires --backend codex-oauth or openai-compatible-api")

    request = read_json(page_dir / "page_request.json", default={})
    contract = request.get("image_backend") or {}
    preferred_backend = contract.get("backend_id")
    if preferred_backend == "builtin-imagegen":
        if args.backend == "unknown":
            raise SystemExit("A builtin-imagegen page contract requires a known producing backend")
        if args.backend in cli_backends and not args.fallback_reason:
            raise SystemExit("CLI output under a builtin-imagegen contract requires --fallback-reason")
        allowed_reasons = (contract.get("fallback_policy") or {}).get("on") or []
        if args.fallback_reason and args.fallback_reason not in allowed_reasons:
            raise SystemExit(f"Fallback reason is not permitted by page_request.json: {args.fallback_reason}")
    elif preferred_backend == "image2ppt-image-cli":
        if args.backend not in cli_backends:
            raise SystemExit("An image2ppt-image-cli page contract requires --backend codex-oauth or openai-compatible-api")
        if args.fallback_reason:
            raise SystemExit("--fallback-reason requires a builtin-imagegen page contract")
    elif preferred_backend == "openai-compatible-api":
        if args.backend != "openai-compatible-api":
            raise SystemExit("An openai-compatible-api page contract requires --backend openai-compatible-api")
        if args.fallback_reason:
            raise SystemExit("--fallback-reason requires a builtin-imagegen page contract")
    elif preferred_backend:
        raise SystemExit(f"Unsupported image backend in page_request.json: {preferred_backend}")
    elif args.fallback_reason:
        raise SystemExit("--fallback-reason requires a builtin-imagegen page contract")

    dest = resolve_inside(page_dir, args.dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if source != dest:
        shutil.copy2(source, dest)

    jobs_path = page_dir / "imagegen-jobs.json"
    jobs = read_json(jobs_path, default={"schema_version": 1, "jobs": []})
    existing = None
    for item in jobs.get("jobs", []):
        if item.get("job_id") == args.job_id:
            existing = item
            break
    if existing is None:
        existing = {"job_id": args.job_id}
        jobs.setdefault("jobs", []).append(existing)
    existing.update(
        {
            "role": args.role,
            "status": "recorded",
            "source_image": str(source),
            "output": dest.relative_to(page_dir).as_posix(),
            "output_sha256": sha256_file(dest),
            "prompt_file": args.prompt_file,
            "backend": args.backend,
            "model": args.model,
            "fallback_reason": args.fallback_reason,
            "note": args.note,
            "recorded_at": now_iso(),
        }
    )
    jobs["updated_at"] = now_iso()
    write_json(jobs_path, jobs)
    print(dest)


if __name__ == "__main__":
    main()
