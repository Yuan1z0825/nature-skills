#!/usr/bin/env python3
"""Generate manuscript schematic drafts with OpenRouter's Images API."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


API_URL = "https://openrouter.ai/api/v1/images"
DEFAULT_MODEL = "openai/gpt-image-2"


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


def reference_to_payload(value: str) -> dict[str, Any]:
    if value.startswith(("http://", "https://", "data:")):
        url = value
    else:
        path = Path(value)
        if not path.exists():
            raise SystemExit(f"Reference image not found: {value}")
        media_type = mimetypes.guess_type(path.name)[0] or "image/png"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        url = f"data:{media_type};base64,{encoded}"
    return {"type": "image_url", "image_url": {"url": url}}


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": args.model,
        "prompt": build_prompt(args),
    }

    optional_fields = {
        "aspect_ratio": args.aspect_ratio,
        "resolution": args.resolution,
        "quality": args.quality,
        "output_format": args.output_format,
        "background": args.background,
        "size": args.size,
        "n": args.n,
    }
    for key, value in optional_fields.items():
        if value is not None:
            payload[key] = value

    if args.reference_image:
        payload["input_references"] = [
            reference_to_payload(value) for value in args.reference_image
        ]

    return payload


def media_extension(media_type: str | None, output_format: str | None) -> str:
    if media_type == "image/svg+xml":
        return ".svg"
    if media_type == "image/jpeg":
        return ".jpg"
    if media_type == "image/webp":
        return ".webp"
    if media_type == "image/png":
        return ".png"
    if output_format == "jpeg":
        return ".jpg"
    if output_format in {"png", "webp"}:
        return f".{output_format}"
    return ".png"


def decode_b64_image(value: str) -> bytes:
    if value.startswith("data:"):
        value = value.split(",", 1)[1]
    return base64.b64decode(value)


def request_images(payload: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"Missing API key: set {args.api_key_env}.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    site_url = args.site_url or os.environ.get("OPENROUTER_SITE_URL")
    app_name = args.app_name or os.environ.get("OPENROUTER_APP_NAME")
    if site_url:
        headers["HTTP-Referer"] = site_url
    if app_name:
        headers["X-Title"] = app_name

    request = urllib.request.Request(
        args.api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Image request failed ({exc.code}) at {args.api_url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Image request failed at {args.api_url}: {exc}") from exc


def save_outputs(response: dict[str, Any], payload: dict[str, Any], args: argparse.Namespace) -> None:
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    basename = args.basename or time.strftime("openrouter_schematic_%Y%m%d_%H%M%S")

    saved: list[str] = []
    for index, item in enumerate(response.get("data", []), start=1):
        media_type = item.get("media_type")
        ext = media_extension(media_type, args.output_format)
        suffix = "" if len(response.get("data", [])) == 1 else f"_{index:02d}"
        outpath = outdir / f"{basename}{suffix}{ext}"

        if "b64_json" in item:
            outpath.write_bytes(decode_b64_image(item["b64_json"]))
            saved.append(str(outpath))
        elif "url" in item:
            with urllib.request.urlopen(item["url"], timeout=args.timeout) as image_response:
                outpath.write_bytes(image_response.read())
            saved.append(str(outpath))
        else:
            raise SystemExit(f"No image bytes or URL in response item {index}: {item}")

    metadata = {
        "api_url": args.api_url,
        "request": payload,
        "response_usage": response.get("usage"),
        "created": response.get("created"),
        "saved_files": saved,
    }
    metadata_path = outdir / f"{basename}_request_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Saved:")
    for path in saved:
        print(f"  {path}")
    print(f"  {metadata_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate manuscript schematic drafts with OpenRouter's Images API."
    )
    parser.add_argument("--model", default=os.environ.get("OPENROUTER_IMAGE_MODEL", DEFAULT_MODEL))
    parser.add_argument("--title")
    parser.add_argument("--abstract")
    parser.add_argument("--abstract-file")
    parser.add_argument("--panel-map")
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file")
    parser.add_argument("--style")
    parser.add_argument("--raw", action="store_true", help="Use prompt text without the schematic scaffold.")
    parser.add_argument("--reference-image", action="append", help="Path, URL, or data URL for image-to-image guidance.")
    parser.add_argument("--outdir", default="openrouter_schematic")
    parser.add_argument("--basename")
    parser.add_argument("--aspect-ratio", default="16:9")
    parser.add_argument("--resolution", default="2K")
    parser.add_argument("--size", help="Optional OpenRouter size shorthand, such as 2048x2048.")
    parser.add_argument("--quality", default="high", choices=["auto", "low", "medium", "high"])
    parser.add_argument("--output-format", default="png", choices=["png", "jpeg", "webp"])
    parser.add_argument("--background", choices=["auto", "transparent", "opaque"])
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument(
        "--api-url",
        default=os.environ.get("SCHEMATIC_IMAGE_API_URL", API_URL),
        help=(
            "Images endpoint to call. Defaults to OpenRouter; point it at any "
            "OpenAI-compatible images endpoint to use that service instead."
        ),
    )
    parser.add_argument("--site-url")
    parser.add_argument("--app-name")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--dry-run", action="store_true", help="Print request payload without calling the API.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args)

    if args.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    response = request_images(payload, args)
    save_outputs(response, payload, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
