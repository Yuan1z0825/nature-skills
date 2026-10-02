#!/usr/bin/env python3
import argparse
from pathlib import Path

from deck_run_state import now_iso, read_json, write_json
from _page_artifacts import process_asset_sheet as process_sheet


def configure_default_paths(args):
    if args.job_id:
        job_id = args.job_id
        if any(value is None for value in (args.chroma, args.alpha, args.split_manifest)):
            if (
                "\x00" in job_id
                or "/" in job_id
                or "\\" in job_id
                or job_id in {".", ".."}
                or Path(job_id).is_absolute()
                or Path(job_id).name != job_id
            ):
                raise SystemExit("--job-id must be a safe filename component when default output paths are used")
        args.chroma = args.chroma or f"assets/{job_id}.asset-sheet-chroma.png"
        args.alpha = args.alpha or f"assets/{job_id}.asset-sheet-alpha.png"
        args.split_manifest = args.split_manifest or f"assets/{job_id}.split-report.json"
    else:
        args.chroma = args.chroma or "imagegen_asset_sheet_chroma.png"
        args.alpha = args.alpha or "imagegen_asset_sheet_alpha.png"
        args.split_manifest = args.split_manifest or "split_assets.json"


def use_recorded_job_output(page_dir, args):
    """Use the imported page-local output promised by the public CLI help."""
    if args.asset_sheet_source or not args.job_id:
        return
    jobs = read_json(page_dir / "imagegen-jobs.json", default={})
    for item in jobs.get("jobs", []):
        if item.get("job_id") == args.job_id and item.get("output"):
            args.asset_sheet_source = item["output"]
            return


def mark_processed(page_dir, args):
    if not args.job_id:
        return
    jobs_path = page_dir / "imagegen-jobs.json"
    jobs = read_json(jobs_path, default={"schema_version": 1, "jobs": []})
    for item in jobs.get("jobs", []):
        if item.get("job_id") == args.job_id:
            item.update(
                {
                    "status": "processed",
                    "processed_at": now_iso(),
                    "alpha": args.alpha,
                    "assets_dir": args.assets_dir,
                    "split_manifest": args.split_manifest,
                }
            )
            break
    else:
        jobs.setdefault("jobs", []).append(
            {
                "job_id": args.job_id,
                "role": "asset_sheet",
                "status": "processed",
                "processed_at": now_iso(),
                "alpha": args.alpha,
                "assets_dir": args.assets_dir,
                "split_manifest": args.split_manifest,
            }
        )
    jobs["updated_at"] = now_iso()
    write_json(jobs_path, jobs)


def main():
    parser = argparse.ArgumentParser(
        prog="image2ppt image process-sheet",
        description="Remove chroma key and split an imagegen asset sheet.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  image2ppt image process-sheet <page_dir> --job-id icon-sheet-1 --asset-sheet-source assets/sheet.png --asset-names icon-a,icon-b
""",
    )
    parser.add_argument("page_dir", help="Page directory that owns imagegen-jobs.json, manifest.json, and the assets folder.")
    parser.add_argument("--job-id", help="Image generation job id to mark as processed after splitting.")
    parser.add_argument("--asset-sheet-source", help="Generated sheet image to process. Relative paths are resolved under page_dir unless absolute. Defaults to the imported asset sheet recorded for --job-id when available.")
    parser.add_argument("--chroma", help="Intermediate chroma-key output path relative to page_dir. Defaults to a job-scoped path when --job-id is set.")
    parser.add_argument("--alpha", help="Transparent sheet output path relative to page_dir. Defaults to a job-scoped path when --job-id is set.")
    parser.add_argument("--skip-chroma", action="store_true", help="Skip chroma-key removal when processing an already-transparent sheet.")
    parser.add_argument("--force-chroma", action="store_true", help="Run chroma-key removal even if the alpha output already exists.")
    parser.add_argument("--despill", action="store_true", help="Reduce remaining chroma color around extracted asset edges.")
    parser.add_argument("--skip-split", action="store_true", help="Do not auto-split connected alpha components.")
    parser.add_argument("--transparent-threshold", default="12", help="RGB distance threshold treated as fully transparent during chroma removal.")
    parser.add_argument("--opaque-threshold", default="220", help="RGB distance threshold treated as fully opaque during chroma removal.")
    parser.add_argument("--assets-dir", default="assets", help="Output directory for split assets, relative to page_dir.")
    parser.add_argument("--asset-names", help="Comma-separated names assigned to split assets in visual order.")
    parser.add_argument("--split-sort", choices=["x", "y", "area"], default="x", help="Sort extracted alpha components by x position, y position, or area.")
    parser.add_argument("--split-min-area", default="1000", help="Minimum connected-component pixel area to keep as an extracted asset.")
    parser.add_argument("--split-merge-gap", default="18", help="Merge nearby components separated by at most this many pixels.")
    parser.add_argument("--split-merge-union-growth", default="2.4", help="Maximum bounding-box growth ratio allowed when merging nearby components.")
    parser.add_argument("--square-assets", action="store_true", help="Pad split assets to square canvases.")
    parser.add_argument("--split-manifest", help="JSON file that records split asset paths and bounding boxes. Defaults to a job-scoped path when --job-id is set.")
    args = parser.parse_args()
    configure_default_paths(args)

    page_dir = Path(args.page_dir).resolve()
    if not page_dir.exists():
        raise SystemExit(f"Page folder does not exist: {page_dir}")
    use_recorded_job_output(page_dir, args)
    process_sheet(args, page_dir)
    mark_processed(page_dir, args)


if __name__ == "__main__":
    main()
