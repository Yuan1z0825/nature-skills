import json
import shutil
import subprocess
import sys
from pathlib import Path

from deck_run_state import resolve_inside
from split_alpha_components import parse_names as parse_asset_names


SCRIPT_DIR = Path(__file__).resolve().parent


def run(command):
    print("+ " + " ".join(str(part) for part in command), flush=True)
    subprocess.run([str(part) for part in command], check=True)


def resolve_input_path(page_dir, value):
    raw = Path(value).expanduser()
    if raw.is_absolute() or raw.drive:
        return raw.resolve()
    try:
        return resolve_inside(page_dir, raw)
    except ValueError as exc:
        raise SystemExit(
            f"Relative input path must stay inside page_dir: {value}"
        ) from exc


def resolve_output_path(page_dir, value):
    raw = Path(value).expanduser()
    if raw.is_absolute() or raw.drive:
        raise SystemExit(f"Output path must be relative to page_dir: {value}")
    try:
        return resolve_inside(page_dir, raw)
    except ValueError as exc:
        raise SystemExit(f"Output path must stay inside page_dir: {value}") from exc


def imagegen_chroma_helper():
    helper = SCRIPT_DIR / "remove_chroma_key.py"
    if not helper.exists():
        raise SystemExit(f"Missing chroma helper: {helper}")
    return helper


def process_asset_sheet(args, page_dir):
    parse_asset_names(args.asset_names, "--asset-names")
    chroma = resolve_output_path(page_dir, args.chroma)
    alpha = resolve_output_path(page_dir, args.alpha)
    assets_dir = resolve_output_path(page_dir, args.assets_dir)
    split_manifest = resolve_output_path(page_dir, args.split_manifest)
    if not args.asset_sheet_source and not chroma.exists() and not alpha.exists():
        return
    if not args.asset_sheet_source and args.skip_chroma and args.skip_split:
        return

    if not args.skip_chroma and alpha.exists() and not args.force_chroma:
        raise SystemExit(f"Output already exists: {alpha} (use --force-chroma to overwrite)")

    if args.asset_sheet_source:
        source = resolve_input_path(page_dir, args.asset_sheet_source)
        if not source.exists():
            raise SystemExit(f"Asset sheet source does not exist: {source}")
        chroma.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, chroma)
        print(f"Wrote {chroma}")

    if not args.skip_chroma:
        if not chroma.exists():
            raise SystemExit(f"Chroma input does not exist: {chroma}")
        command = [
            sys.executable,
            imagegen_chroma_helper(),
            "--input",
            chroma,
            "--out",
            alpha,
            "--auto-key",
            "border",
            "--soft-matte",
            "--transparent-threshold",
            args.transparent_threshold,
            "--opaque-threshold",
            args.opaque_threshold,
        ]
        if args.despill:
            command.append("--despill")
        if args.force_chroma:
            command.append("--force")
        run(command)

    if args.skip_split:
        return
    if not alpha.exists():
        raise SystemExit(f"Alpha sheet does not exist: {alpha}")

    command = [
        sys.executable,
        SCRIPT_DIR / "split_alpha_components.py",
        "--input",
        alpha,
        "--out-dir",
        assets_dir,
        "--sort",
        args.split_sort,
        "--min-area",
        args.split_min_area,
        "--merge-gap",
        args.split_merge_gap,
        "--merge-union-growth",
        args.split_merge_union_growth,
        "--manifest",
        split_manifest,
    ]
    if args.square_assets:
        command.append("--square")
    if args.asset_names:
        command.extend(["--names", args.asset_names])
    run(command)


def fit_image(image, size):
    if image.size == size:
        return image
    return image.resize(size)


def write_pair(source_path, preview_path, out_path):
    from PIL import Image, ImageDraw

    source = Image.open(source_path).convert("RGB")
    rebuilt = Image.open(preview_path).convert("RGB")
    source = fit_image(source, rebuilt.size)

    label_h = 32
    gap = 18
    width, height = rebuilt.size
    canvas = Image.new("RGB", (width * 2 + gap, height + label_h), "#f5f7fb")
    canvas.paste(source, (0, label_h))
    canvas.paste(rebuilt, (width + gap, label_h))
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 9), "origin", fill="black")
    draw.text((width + gap + 10, 9), "preview", fill="black")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    print(f"Wrote {out_path}")
