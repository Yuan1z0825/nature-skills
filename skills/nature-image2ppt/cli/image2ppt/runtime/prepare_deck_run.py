#!/usr/bin/env python3
import argparse
from pathlib import Path

from PIL import Image

from deck_run_state import now_iso, page_dir_for, read_json, rel_to_run, save_deck, set_run_status, sha256_file, write_json
from deck_run_state import DEFAULT_MAX_CONCURRENT_PAGES
from _input_normalization import normalize_inputs


WIDE_SLIDE = {"width": 13.333, "height": 7.5, "size_mode": "wide"}
PX_PER_INCH = 96
ASPECT_16_9 = 16 / 9
ASPECT_TOLERANCE = 0.03


def source_size(path):
    with Image.open(path) as image:
        return image.size


def is_close_to_wide(width_px, height_px):
    if not width_px or not height_px:
        return False
    return abs((width_px / height_px) / ASPECT_16_9 - 1) <= ASPECT_TOLERANCE


def source_size_slide(width_px, height_px):
    return {
        "width": width_px / PX_PER_INCH,
        "height": height_px / PX_PER_INCH,
        "size_mode": "source",
        "px_per_inch": PX_PER_INCH,
    }


def slide_for_source(width_px, height_px):
    if is_close_to_wide(width_px, height_px):
        return dict(WIDE_SLIDE)
    return source_size_slide(width_px, height_px)


def fit_content_box(width_px, height_px, slide):
    slide_width = float(slide["width"])
    slide_height = float(slide["height"])
    source_aspect = width_px / height_px
    slide_aspect = slide_width / slide_height
    if source_aspect >= slide_aspect:
        width = slide_width
        height = width / source_aspect
        left = 0
        top = (slide_height - height) / 2
    else:
        height = slide_height
        width = height * source_aspect
        left = (slide_width - width) / 2
        top = 0
    return {"left": left, "top": top, "width": width, "height": height, "fit": "contain"}


def page_source_size(run_dir, page):
    source = (run_dir / page["source_image"]).resolve()
    width_px, height_px = source_size(source)
    return source, width_px, height_px


def deck_slide_layout(run_dir, deck):
    first_page = deck.get("pages", [{}])[0]
    _source, width_px, height_px = page_source_size(run_dir, first_page)
    return slide_for_source(width_px, height_px)


def page_request(run_dir, deck, page):
    page_dir = page_dir_for(run_dir, page)
    source, width_px, height_px = page_source_size(run_dir, page)
    slide = dict(deck["slide"])
    page_id = page["page_id"]
    return {
        "schema_version": 1,
        "run_id": deck["run_id"],
        "page_id": page_id,
        "page_index": page["page_index"],
        "page_dir": str(page_dir),
        "source_image": str(source),
        "source_size_px": {"width": width_px, "height": height_px},
        "slide": slide,
        "content_box": fit_content_box(width_px, height_px, slide),
        "max_concurrent_pages": deck["max_concurrent_pages"],
        "allowed_write_scope": str(page_dir),
        "forbidden_paths": [
            str(run_dir / "deck_manifest.json"),
            str(run_dir / "page_jobs.json"),
            str(run_dir / "notes_manifest.json"),
            str(run_dir / "final"),
            str(run_dir / "input"),
        ],
        "required_outputs": {
            "manifest": str(page_dir / "manifest.json"),
            "imagegen_jobs": str(page_dir / "imagegen-jobs.json"),
            "page_pptx": str(page_dir / "page.pptx"),
            "preview": str(page_dir / "preview.png"),
            "contact_sheet": str(page_dir / "split_assets_contact.png"),
            "validation": str(page_dir / "validation.json"),
            "page_result": str(page_dir / "page_result.json"),
        },
    }


def write_page_jobs(run_dir, deck):
    jobs = {
        "schema_version": 1,
        "run_id": deck["run_id"],
        "run_status": "inputs_prepared",
        "max_concurrent_pages": deck["max_concurrent_pages"],
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "pages": [],
    }
    for page in deck["pages"]:
        page_dir = page_dir_for(run_dir, page)
        request_path = page_dir / "page_request.json"
        request = page_request(run_dir, deck, page)
        write_json(request_path, request)
        write_json(
            page_dir / "imagegen-jobs.json",
            {"schema_version": 1, "run_id": deck["run_id"], "page_id": page["page_id"], "jobs": []},
        )
        jobs["pages"].append(
            {
                "page_id": page["page_id"],
                "page_index": page["page_index"],
                "status": "pending",
                "page_dir": page["page_dir"],
                "source": page["source_image"],
                "page_request": rel_to_run(run_dir, request_path),
                "manifest": page["manifest"],
                "validation": page["validation"],
                "dispatch": None,
                "result": None,
                "accepted": False,
            }
        )
    write_json(run_dir / "page_jobs.json", jobs)


def upgrade_deck_manifest(deck_path, max_concurrent_pages):
    run_dir = deck_path.parent
    deck = read_json(deck_path)
    run_id = run_dir.name
    output_name = Path(deck.get("output", f"{run_id}_edited.pptx")).name
    deck.update(
        {
            "schema_version": 1,
            "run_id": run_id,
            "prepared_at": now_iso(),
            "output": f"final/{output_name}",
            "page_jobs": "page_jobs.json",
            "run_state": "run_state.json",
            "max_concurrent_pages": max_concurrent_pages,
        }
    )
    deck["slide"] = deck_slide_layout(run_dir, deck)
    for index, page in enumerate(deck.get("pages", []), start=1):
        page_id = f"page_{index:03d}"
        page["page_id"] = page_id
        page["status"] = "pending"
        page["page_request"] = f"{page['page_dir']}/page_request.json"
        page["dispatch"] = None
        page["result"] = None
        page["accepted"] = False
    save_deck(run_dir, deck)
    write_page_jobs(run_dir, deck)
    set_run_status(run_dir, "inputs_prepared", "prepared inputs and page jobs")
    return deck


def main():
    parser = argparse.ArgumentParser(description="Create a stable image2ppt run directory.")
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--out-root", default="output/image2ppt")
    parser.add_argument("--job-dir")
    parser.add_argument("--dpi", type=int, default=180)
    parser.add_argument(
        "--max-concurrent-pages",
        type=int,
        default=DEFAULT_MAX_CONCURRENT_PAGES,
        help=f"Maximum page subagents that may be dispatched at the same time. Default: {DEFAULT_MAX_CONCURRENT_PAGES}.",
    )
    args = parser.parse_args()
    if args.max_concurrent_pages < 1:
        raise SystemExit("--max-concurrent-pages must be >= 1")

    deck_path = normalize_inputs(args.inputs, out_root=args.out_root, job_dir=args.job_dir, dpi=args.dpi)
    run_dir = deck_path.parent
    if not (run_dir / "pages").exists():
        raise SystemExit(f"Input normalization did not create pages/: {run_dir}")
    deck = upgrade_deck_manifest(deck_path, args.max_concurrent_pages)
    print(deck_path)
    print(f"run_id={deck['run_id']}")
    print(f"pages={deck['page_count']}")
    print(f"max_concurrent_pages={deck['max_concurrent_pages']}")


if __name__ == "__main__":
    main()
