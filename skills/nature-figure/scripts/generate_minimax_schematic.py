#!/usr/bin/env python3
"""Generate manuscript schematic drafts with the MiniMax image_generation API."""

from __future__ import annotations

import argparse
import base64
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


# Regional hosts. The global endpoint serves platform.minimax.io accounts; the
# CN endpoint serves platform.minimaxi.com accounts. Both expose the same path.
REGION_BASE_URLS = {
    "global": "https://api.minimax.io",
    "cn": "https://api.minimaxi.com",
}
IMAGE_PATH = "/v1/image_generation"
DEFAULT_MODEL = "image-01"
SUPPORTED_MODELS = ("image-01", "image-01-live")


def read_optional_text(text: str | None, path: str | None) -> str:
    parts: list[str] = []
    if text:
        parts.append(text.strip())
    if path:
        parts.append(Path(path).read_text(encoding="utf-8").strip())
    return "\n\n".join(part for part in parts if part)


def build_prompt(args: argparse.Namespace) -> str:
    custom_prompt = read_optional_text(args.prompt, args.prompt_file)
    if custom_prompt and args.raw:
        return custom_prompt

    title = args.title.strip() if args.title else ""
    abstract = read_optional_text(args.abstract, args.abstract_file)
    panel_map = args.panel_map.strip() if args.panel_map else ""

    content_blocks = []
    if title:
        content_blocks.append(f"Title: {title}")
    if abstract:
        content_blocks.append(f"Article summary:\n{abstract}")
    if panel_map:
        content_blocks.append(f"Desired panel flow:\n{panel_map}")
    if custom_prompt:
        content_blocks.append(f"Additional instructions:\n{custom_prompt}")

    if not content_blocks:
        raise SystemExit(
            "Provide --prompt/--prompt-file or at least one of --title, "
            "--abstract/--abstract-file, or --panel-map."
        )

    style = args.style or (
        "Create a clean Nature-style scientific graphical abstract / mechanism "
        "schematic for a research paper. Use a flat vector-like visual language, "
        "restrained journal palette, clear hierarchy, simple arrows, and minimal "
        "short labels. Keep the background uncluttered."
    )

    constraints = (
        "Scientific constraints: show only the mechanisms and entities described "
        "below; do not invent quantitative values, p-values, microscopy results, "
        "institutional logos, journal marks, or unsupported experimental claims. "
        "Use conceptual visual elements rather than fake data panels. Text labels "
        "must be short and easy to redraw later."
    )

    return "\n\n".join([style, constraints, *content_blocks])


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": args.model,
        "prompt": build_prompt(args),
        "response_format": args.response_format,
    }

    if args.width is not None or args.height is not None:
        if args.width is None or args.height is None:
            raise SystemExit("--width and --height must be provided together.")
        payload["width"] = args.width
        payload["height"] = args.height
    elif args.aspect_ratio is not None:
        payload["aspect_ratio"] = args.aspect_ratio

    optional_fields = {
        "seed": args.seed,
        "n": args.n,
        "prompt_optimizer": args.prompt_optimizer,
    }
    for key, value in optional_fields.items():
        if value is not None:
            payload[key] = value

    return payload


def sniff_extension(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    return ".png"


def decode_b64_image(value: str) -> bytes:
    if value.startswith("data:"):
        value = value.split(",", 1)[1]
    return base64.b64decode(value)


def request_images(payload: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"Missing API key: set {args.api_key_env}.")

    endpoint = REGION_BASE_URLS[args.region] + IMAGE_PATH
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Image generation request failed ({exc.code}): {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Image generation request failed: {exc}") from exc


def check_base_resp(response: dict[str, Any]) -> None:
    base_resp = response.get("base_resp") or {}
    status_code = base_resp.get("status_code")
    if status_code not in (0, None):
        status_msg = base_resp.get("status_msg", "unknown error")
        raise SystemExit(f"Image generation returned status {status_code}: {status_msg}")


def collect_images(response: dict[str, Any], args: argparse.Namespace) -> list[bytes]:
    data = response.get("data") or {}
    images: list[bytes] = []
    if args.response_format == "base64":
        for value in data.get("image_base64", []) or []:
            images.append(decode_b64_image(value))
    else:
        for url in data.get("image_urls", []) or []:
            with urllib.request.urlopen(url, timeout=args.timeout) as image_response:
                images.append(image_response.read())
    if not images:
        raise SystemExit(f"No images returned in response: {json.dumps(response)[:500]}")
    return images


def save_outputs(response: dict[str, Any], payload: dict[str, Any], args: argparse.Namespace) -> None:
    check_base_resp(response)
    images = collect_images(response, args)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    basename = args.basename or time.strftime("minimax_schematic_%Y%m%d_%H%M%S")

    saved: list[str] = []
    for index, data in enumerate(images, start=1):
        ext = sniff_extension(data)
        suffix = "" if len(images) == 1 else f"_{index:02d}"
        outpath = outdir / f"{basename}{suffix}{ext}"
        outpath.write_bytes(data)
        saved.append(str(outpath))

    metadata = {
        "endpoint": REGION_BASE_URLS[args.region] + IMAGE_PATH,
        "region": args.region,
        "request": payload,
        "trace_id": response.get("id"),
        "success_count": (response.get("metadata") or {}).get("success_count"),
        "failed_count": (response.get("metadata") or {}).get("failed_count"),
        "base_resp": response.get("base_resp"),
        "saved_files": saved,
    }
    metadata_path = outdir / f"{basename}_request_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Saved:")
    for path in saved:
        print(f"  {path}")
    print(f"  {metadata_path}")
    if args.response_format == "url":
        print("Note: source image URLs expire 24 hours after generation.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate manuscript schematic drafts with the MiniMax image_generation API."
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("MINIMAX_IMAGE_MODEL", DEFAULT_MODEL),
        choices=SUPPORTED_MODELS,
    )
    parser.add_argument(
        "--region",
        default=os.environ.get("MINIMAX_REGION", "global"),
        choices=sorted(REGION_BASE_URLS),
        help="global -> api.minimax.io, cn -> api.minimaxi.com.",
    )
    parser.add_argument("--title")
    parser.add_argument("--abstract")
    parser.add_argument("--abstract-file")
    parser.add_argument("--panel-map")
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file")
    parser.add_argument("--style")
    parser.add_argument("--raw", action="store_true", help="Use prompt text without the schematic scaffold.")
    parser.add_argument("--outdir", default="minimax_schematic")
    parser.add_argument("--basename")
    parser.add_argument(
        "--aspect-ratio",
        default="16:9",
        choices=["1:1", "16:9", "4:3", "3:2", "2:3", "3:4", "9:16", "21:9"],
    )
    parser.add_argument("--width", type=int, help="Image width in px [512, 2048], divisible by 8; requires --height.")
    parser.add_argument("--height", type=int, help="Image height in px [512, 2048], divisible by 8; requires --width.")
    parser.add_argument("--response-format", default="url", choices=["url", "base64"])
    parser.add_argument("--seed", type=int, help="Fixed seed for reproducible images.")
    parser.add_argument("--n", type=int, default=1, help="Number of images to generate, range [1, 9].")
    parser.add_argument(
        "--prompt-optimizer",
        action="store_true",
        help="Let the service automatically optimize the prompt.",
    )
    parser.add_argument("--api-key-env", default="MINIMAX_API_KEY")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--dry-run", action="store_true", help="Print request payload without calling the API.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.prompt_optimizer:
        args.prompt_optimizer = None
    payload = build_payload(args)

    if args.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    response = request_images(payload, args)
    save_outputs(response, payload, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
