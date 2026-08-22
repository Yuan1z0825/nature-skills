#!/usr/bin/env python3
"""Unified CLI for image2ppt image generation or editing.

The CLI prefers local Codex OAuth auth when ~/.codex/auth.json is available.
If Codex auth is missing, it falls back to OpenAI-compatible API credentials
from the environment or the active Image2PPT config.yaml.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import ipaddress
import json
import mimetypes
import os
from pathlib import Path
import random
import re
import socket
import sys
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib import error, request
from urllib.parse import urljoin, urlparse

DEFAULT_MODEL = "gpt-image-2"
DEFAULT_SIZE = "auto"
DEFAULT_QUALITY = "auto"
DEFAULT_BACKGROUND = "auto"
DEFAULT_OUTPUT_EXTENSION = "png"
DEFAULT_OUTPUT_PATH = "output/imagegen/output.png"
DEFAULT_TIMEOUT = 600
DEFAULT_CODEX_MAX_RETRIES = 4
DEFAULT_CODEX_RETRY_BASE_DELAY_SECONDS = 0.2
GPT_IMAGE_MODEL_PREFIX = "gpt-image-"

BACKEND_AUTO = "auto"
BACKEND_CODEX_OAUTH = "codex-oauth"
BACKEND_OPENAI_COMPATIBLE = "openai-compatible-api"
ALLOWED_BACKENDS = {BACKEND_AUTO, BACKEND_CODEX_OAUTH, BACKEND_OPENAI_COMPATIBLE}

GPT_IMAGE_2_MODEL = "gpt-image-2"
GPT_IMAGE_2_MIN_PIXELS = 655_360
GPT_IMAGE_2_MAX_PIXELS = 8_294_400
GPT_IMAGE_2_MAX_EDGE = 3840
GPT_IMAGE_2_MAX_RATIO = 3.0

MAX_IMAGE_BYTES = 50 * 1024 * 1024
DEFAULT_CODEX_AUTH_FILE = "~/.codex/auth.json"
DEFAULT_CODEX_IMAGES_BASE_URL = "https://chatgpt.com/backend-api/codex"
ENV_FIELDS = (
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "IMAGE2PPT_IMAGE_MODEL",
    "IMAGE2PPT_IMAGE_BACKEND",
    "IMAGE2PPT_IMAGE_USER_AGENT",
)
MAX_CODEX_RESPONSE_BYTES = 64 * 1024 * 1024
MAX_CODEX_BASE64_CHARS = 64 * 1024 * 1024
MAX_MODEL_ID_CHARS = 256
MAX_REMOTE_REDIRECTS = 5
CHATGPT_AUTH_CLAIM = "https://api.openai.com/auth"
CHATGPT_ACCOUNT_ID_CLAIM = "chatgpt_account_id"

IMAGE_HELP_EPILOG = """\
Backend selection:
  auto: uses Codex OAuth only for GPT Image model ids when compatible auth is
  available; every other model uses the configured OpenAI Images-compatible API.
  codex-oauth: explicitly uses ~/.codex/auth.json or CODEX_AUTH_FILE.
  openai-compatible-api: explicitly uses OPENAI_API_KEY, OPENAI_BASE_URL, and
  an arbitrary provider image model id. It never receives Codex OAuth credentials.

Setup:
  codex login
  image2ppt config --api-key "your-api-key" --image-backend openai-compatible-api \
    --base-url https://example.test/v1 --model provider-image-model

Input image rules:
  generate creates a new image from prompt only.
  edit passes each --image as an edit target, visual reference, or supporting input.

Parameter surface:
  Public image parameters are model, prompt, size, and quality. Codex OAuth
  requests also set background=auto to match Codex built-in image generation.
  Edit requests also pass the input images and optional mask. Local controls
  such as --out, --force, --dry-run, and --timeout are not image API parameters.

Slide reconstruction patterns:
  Clean base: use edit --image <source.png>; preserve source composition,
  perspective, object positions, colors, lighting, material, and background identity.
  Asset sheet: use edit --image <source.png>; separate exact existing foreground
  bitmap objects on a flat chroma-key background with generous spacing. Choose
  a key color absent from the assets and far from their main fills, strokes,
  highlights, and shadows; cyan, green, magenta, red, or orange are examples,
  not fixed defaults.
  Formula assets: use image2ppt formula render-latex, not image2ppt image.

Output:
  Write outputs under the page directory when used in a deck run. Record selected
  images with image2ppt image import, then use process-sheet when asset-sheet splitting is needed.
"""

GENERATE_HELP_EPILOG = """\
Backend:
  Uses --backend or IMAGE2PPT_IMAGE_BACKEND. In auto mode, Codex OAuth is used
  only for GPT Image model ids; other model ids use the OpenAI-compatible API.

Use for:
  New supporting images that do not need to preserve an existing slide object.

Examples:
  image2ppt image generate --prompt "flat blue cloud icon, no text" --out pages/page_001/assets/cloud.png
  image2ppt image generate --prompt-file prompt.txt --size 1536x1024 --quality high --out output.png
"""

EDIT_HELP_EPILOG = """\
Backend:
  Uses --backend or IMAGE2PPT_IMAGE_BACKEND. In auto mode, Codex OAuth is used
  only for GPT Image model ids; other model ids use the OpenAI-compatible API.

Use for:
  Background cleanup, clean base creation, foreground icon extraction, and
  source-faithful asset sheets. Pass the original slide through --image so the
  model receives it as the edit target and strict visual reference.

Prompt patterns:
  Clean base: preserve source canvas ratio, composition, perspective, object
  positions, colors, lighting, texture, and background identity; remove the
  foreground text/objects that will be rebuilt.
  Asset sheet: extract exact existing non-text foreground objects from the
  source into a sparse chroma-key sheet; preserve shape, stroke geometry, color,
  proportions, internal cutouts, and visual identity. Choose a key color absent
  from the target objects and far from their main fills, strokes, highlights,
  and shadows; cyan, green, magenta, red, or orange are examples, not fixed
  defaults.

Examples:
  image2ppt image edit --image pages/page_001/source.png --prompt-file clean-base.prompt.txt --out pages/page_001/assets/clean-base.png
  image2ppt image edit --image pages/page_001/source.png --prompt-file asset-sheet.prompt.txt --out pages/page_001/assets/asset-sheet.png
  image2ppt image edit --image source.png --image style.png --prompt "Use source as target and style as supporting reference" --out out.png
"""


def _die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def _warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


def _runtime_env_path() -> Path:
    try:
        from .runtime_env import config_path
    except ImportError:
        from runtime_env import config_path
    return config_path()


def _load_runtime_env() -> None:
    path = _runtime_env_path()
    if not path.exists():
        return
    try:
        import yaml
    except ImportError as exc:
        _die(
            "PyYAML is required to read the active Image2PPT config.yaml. "
            "Reinstall image2ppt with pipx so package dependencies are installed."
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        _die(f"Invalid config file: {path}")
    for key, value in data.items():
        if key not in ENV_FIELDS or os.getenv(key):
            continue
        os.environ[key] = str(value)


def _default_model() -> str:
    return os.getenv("IMAGE2PPT_IMAGE_MODEL", DEFAULT_MODEL)


def _default_backend() -> str:
    return os.getenv("IMAGE2PPT_IMAGE_BACKEND", BACKEND_AUTO).strip().lower() or BACKEND_AUTO


def _image_user_agent() -> Optional[str]:
    value = os.getenv("IMAGE2PPT_IMAGE_USER_AGENT", "").strip()
    if len(value) > 512 or any(ord(ch) < 32 for ch in value):
        _die("IMAGE2PPT_IMAGE_USER_AGENT must be at most 512 characters with no control characters.")
    return value or None


def _api_base_url() -> Optional[str]:
    return os.getenv("OPENAI_BASE_URL") or None


def _api_target_label() -> str:
    base_url = _api_base_url()
    if base_url:
        return f"OpenAI-compatible proxy (OPENAI_BASE_URL={base_url})"
    return "official OpenAI API (OPENAI_BASE_URL unset)"


def _is_codex_compatible_model(model: str) -> bool:
    return GPT_IMAGE_MODEL_PREFIX in model.lower()


def _validate_backend(backend: str) -> None:
    if backend not in ALLOWED_BACKENDS:
        _die(
            "backend must be one of auto, codex-oauth, or openai-compatible-api."
        )


def _select_backend(backend: str, model: str) -> str:
    _validate_backend(backend)
    if backend == BACKEND_CODEX_OAUTH:
        if not _is_codex_compatible_model(model):
            _die(
                "codex-oauth supports GPT Image model ids only. Use "
                "--backend openai-compatible-api for provider-specific image models."
            )
        if not _codex_available():
            _die(f"Codex OAuth auth is missing. Expected {_codex_auth_file()}.")
        return BACKEND_CODEX_OAUTH
    if backend == BACKEND_OPENAI_COMPATIBLE:
        return BACKEND_OPENAI_COMPATIBLE
    if _is_codex_compatible_model(model) and _codex_available():
        return BACKEND_CODEX_OAUTH
    return BACKEND_OPENAI_COMPATIBLE


def _codex_auth_file() -> Path:
    return Path(os.getenv("CODEX_AUTH_FILE", DEFAULT_CODEX_AUTH_FILE)).expanduser()


def _decode_jwt_payload(token: str) -> Dict[str, Any]:
    parts = token.split(".")
    if len(parts) < 2:
        return {}
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    try:
        raw = base64.urlsafe_b64decode(payload.encode("ascii"))
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _infer_codex_account_id(tokens: Dict[str, Any]) -> Optional[str]:
    account_id = tokens.get("account_id")
    if isinstance(account_id, str) and account_id.strip():
        return account_id.strip()

    id_token = tokens.get("id_token")
    if not isinstance(id_token, str) or not id_token.strip():
        return None
    auth_claim = _decode_jwt_payload(id_token).get(CHATGPT_AUTH_CLAIM)
    if not isinstance(auth_claim, dict):
        return None
    chatgpt_account_id = auth_claim.get(CHATGPT_ACCOUNT_ID_CLAIM)
    if isinstance(chatgpt_account_id, str) and chatgpt_account_id.strip():
        return chatgpt_account_id.strip()
    return None


def _load_codex_auth() -> Optional[Tuple[str, Optional[str]]]:
    path = _codex_auth_file()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    tokens = data.get("tokens")
    if not isinstance(tokens, dict):
        return None
    token = tokens.get("access_token")
    if isinstance(token, str) and token.strip():
        return token.strip(), _infer_codex_account_id(tokens)
    return None


def _load_codex_access_token() -> Optional[str]:
    auth = _load_codex_auth()
    return auth[0] if auth else None


def _codex_available() -> bool:
    return _load_codex_access_token() is not None


def _codex_base_url() -> str:
    raw = (
        os.getenv("CODEX_IMAGES_BASE_URL")
        or DEFAULT_CODEX_IMAGES_BASE_URL
    ).strip()
    if not raw:
        return DEFAULT_CODEX_IMAGES_BASE_URL
    if re.fullmatch(r"https://chatgpt\.com/backend-api(?:/codex)?(?:/v1)?/?", raw, re.I):
        return DEFAULT_CODEX_IMAGES_BASE_URL
    raise RuntimeError(
        "Refusing CODEX_IMAGES_BASE_URL override: Codex OAuth credentials may only be sent "
        f"to {DEFAULT_CODEX_IMAGES_BASE_URL}. Use OPENAI_API_KEY and OPENAI_BASE_URL for "
        "third-party image endpoints."
    )


def _codex_image_url(operation: str) -> str:
    endpoint = "images/edits" if operation == "edit" else "images/generations"
    return f"{_codex_base_url()}/{endpoint}"


def _validate_codex_image_url(url: str) -> None:
    if re.fullmatch(
        r"https://chatgpt\.com/backend-api/codex/images/(?:generations|edits)",
        url,
    ):
        return
    raise RuntimeError(
        "Refusing Codex OAuth request: credentials may only be sent to the official "
        "ChatGPT Images endpoint."
    )


class _NoCodexRedirectHandler(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise error.HTTPError(
            req.full_url,
            code,
            f"Refusing Codex OAuth redirect to {newurl}",
            headers,
            fp,
        )


_CODEX_OPENER = request.build_opener(_NoCodexRedirectHandler())


def _open_codex_request(req: request.Request, timeout: int):
    return _CODEX_OPENER.open(req, timeout=timeout)


def _guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if mime and mime.startswith("image/"):
        return mime
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    return "image/png"


def _image_to_data_url(path: Path) -> str:
    data = path.read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{_guess_mime(path)};base64,{encoded}"


def _codex_image_reference(path: Path) -> Dict[str, str]:
    return {"image_url": _image_to_data_url(path)}


def _codex_image_body(
    *,
    prompt: str,
    image_paths: List[Path],
    mask_path: Optional[Path],
    model: str,
    size: str,
    quality: str,
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "prompt": prompt,
        "model": model,
        "size": size,
        "quality": quality,
        "background": DEFAULT_BACKGROUND,
    }
    if image_paths:
        body["images"] = [_codex_image_reference(path) for path in image_paths]
    if mask_path:
        body["mask"] = _codex_image_reference(mask_path)
    return body


def _codex_retry_delay(attempt: int) -> float:
    exp = 2 ** max(attempt - 1, 0)
    jitter = random.uniform(0.9, 1.1)
    return DEFAULT_CODEX_RETRY_BASE_DELAY_SECONDS * exp * jitter


def _should_retry_codex_http(status: int) -> bool:
    return 500 <= status <= 599


def _format_attempts(attempts: int) -> str:
    if attempts <= 1:
        return ""
    return f" after {attempts} attempts"


def _post_codex_image_json(url: str, body: Dict[str, Any], timeout: int) -> Dict[str, Any]:
    _validate_codex_image_url(url)
    auth = _load_codex_auth()
    if not auth:
        _die(f"Codex OAuth auth is missing. Expected {_codex_auth_file()}.")
    token, account_id = auth
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "originator": "image2ppt-image-cli",
        "User-Agent": "image2ppt-image-cli/1.1.0",
    }
    if account_id:
        headers["ChatGPT-Account-ID"] = account_id
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")

    for attempt in range(DEFAULT_CODEX_MAX_RETRIES + 1):
        req = request.Request(
            url,
            data=data,
            method="POST",
            headers=headers,
        )
        try:
            with _open_codex_request(req, timeout) as resp:
                text = resp.read(MAX_CODEX_RESPONSE_BYTES).decode("utf-8", errors="replace")
            break
        except error.HTTPError as exc:
            detail = exc.read(4096).decode("utf-8", errors="replace")
            if attempt < DEFAULT_CODEX_MAX_RETRIES and _should_retry_codex_http(exc.code):
                time.sleep(_codex_retry_delay(attempt + 1))
                continue
            attempts = attempt + 1
            raise RuntimeError(
                f"Codex Images request failed{_format_attempts(attempts)} "
                f"(HTTP {exc.code}): {detail}"
            ) from exc
        except (error.URLError, TimeoutError, socket.timeout) as exc:
            if attempt < DEFAULT_CODEX_MAX_RETRIES:
                time.sleep(_codex_retry_delay(attempt + 1))
                continue
            attempts = attempt + 1
            reason = getattr(exc, "reason", exc)
            raise RuntimeError(
                f"Codex Images request failed{_format_attempts(attempts)}: {reason}"
            ) from exc
    else:
        raise RuntimeError("Codex Images request failed after retry limit.")

    try:
        response = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Expected JSON Codex Images response, got: {text[:500]}") from exc
    if not isinstance(response, dict):
        raise RuntimeError("Expected JSON object Codex Images response.")
    return response


def _extract_codex_image_payloads(response: Dict[str, Any]) -> List[str]:
    error_obj = response.get("error")
    if isinstance(error_obj, dict):
        message = error_obj.get("message") or error_obj.get("code")
        raise RuntimeError(str(message or "Codex image generation failed."))
    data = response.get("data")
    if not isinstance(data, list):
        raise RuntimeError("Codex image response did not include a data array.")
    payloads: List[str] = []
    for item in data:
        if isinstance(item, dict) and isinstance(item.get("b64_json"), str):
            payloads.append(item["b64_json"])
    if not payloads:
        raise RuntimeError("No image payload found in Codex image response.")
    return payloads


def _runtime_python_path() -> str:
    return sys.executable


def _cli_reinstall_hint() -> str:
    return "`pipx install --force --editable <path-to-image2ppt>/cli`"


def _dependency_hint(package: str, *, upgrade: bool = False) -> str:
    package_arg = f"-U {package}" if upgrade else package
    runtime_python = _runtime_python_path()
    return (
        "Install image2ppt with pipx so CLI dependencies are installed, for example "
        f"{_cli_reinstall_hint()}, "
        f"or install {package} directly in this environment with `{runtime_python} -m pip install {package_arg}`."
    )


def _ensure_api_key(dry_run: bool) -> None:
    if os.getenv("OPENAI_API_KEY"):
        print(f"OPENAI_API_KEY is set. API target: {_api_target_label()}.", file=sys.stderr)
        return
    if dry_run:
        _warn(f"OPENAI_API_KEY is not set; dry-run only. API target: {_api_target_label()}.")
        return
    base_url = _api_base_url()
    model = _default_model()
    if base_url:
        command = (
            'image2ppt config --api-key "your-api-key" '
            f'--base-url "{base_url}" --model {model}'
        )
        target_hint = f"Detected third-party OpenAI-compatible API via OPENAI_BASE_URL={base_url}."
    else:
        command = f'image2ppt config --api-key "your-api-key" --model {model}'
        target_hint = "Detected official OpenAI API mode because OPENAI_BASE_URL is not set."
    _die(
        "The selected openai-compatible-api backend requires OPENAI_API_KEY.\n"
        f"{target_hint}\n"
        "Configure the active Image2PPT config.yaml once:\n"
        f"  {command}\n"
        "For a third-party endpoint, also set OPENAI_BASE_URL and the provider's model id."
    )


def _read_prompt(prompt: Optional[str], prompt_file: Optional[str]) -> str:
    if prompt and prompt_file:
        _die("Use --prompt or --prompt-file, not both.")
    if prompt_file:
        if prompt_file == "-":
            return sys.stdin.read().strip()
        path = Path(prompt_file)
        if not path.exists():
            _die(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8").strip()
    if prompt:
        return prompt.strip()
    _die("Missing prompt. Use --prompt or --prompt-file.")
    return ""  # unreachable


def _check_image_paths(paths: Iterable[str]) -> List[Path]:
    resolved: List[Path] = []
    for raw in paths:
        path = Path(raw)
        if not path.exists():
            _die(f"Image file not found: {path}")
        if path.stat().st_size > MAX_IMAGE_BYTES:
            _warn(f"Image exceeds 50MB limit: {path}")
        resolved.append(path)
    return resolved


def _parse_size(size: str) -> Optional[Tuple[int, int]]:
    match = re.fullmatch(r"([1-9][0-9]*)x([1-9][0-9]*)", size)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def _validate_gpt_image_2_size(size: str) -> None:
    if size == "auto":
        return

    parsed = _parse_size(size)
    if parsed is None:
        _die("size must be auto or WIDTHxHEIGHT, for example 1024x1024.")

    width, height = parsed
    max_edge = max(width, height)
    min_edge = min(width, height)
    total_pixels = width * height

    if max_edge > GPT_IMAGE_2_MAX_EDGE:
        _die("gpt-image-2 size maximum edge length must be less than or equal to 3840px.")
    if width % 16 != 0 or height % 16 != 0:
        _die("gpt-image-2 size width and height must be multiples of 16px.")
    if max_edge / min_edge > GPT_IMAGE_2_MAX_RATIO:
        _die("gpt-image-2 size long edge to short edge ratio must not exceed 3:1.")
    if total_pixels < GPT_IMAGE_2_MIN_PIXELS or total_pixels > GPT_IMAGE_2_MAX_PIXELS:
        _die(
            "gpt-image-2 size total pixels must be at least 655,360 and no more than 8,294,400."
        )


def _validate_size(size: str, model: str) -> None:
    if _is_gpt_image_2_model(model):
        _validate_gpt_image_2_size(size)
        return
    if not isinstance(size, str) or not size.strip() or any(ord(ch) < 32 for ch in size):
        _die("size must be a non-empty provider value without control characters.")


def _validate_quality(quality: str) -> None:
    if not isinstance(quality, str) or not quality.strip() or any(ord(ch) < 32 for ch in quality):
        _die("quality must be a non-empty provider value without control characters.")


def _validate_model(model: str) -> None:
    if not isinstance(model, str) or not model.strip():
        _die("model must be a non-empty image model id.")
    if len(model) > MAX_MODEL_ID_CHARS or any(ord(ch) < 32 for ch in model):
        _die(
            f"model must be at most {MAX_MODEL_ID_CHARS} characters and contain no control characters."
        )


def _is_gpt_image_2_model(model: str) -> bool:
    return GPT_IMAGE_2_MODEL in model


def _build_output_paths(out: str) -> List[Path]:
    out_path = Path(out)
    if out_path.exists() and out_path.is_dir():
        return [out_path / f"image_1.{DEFAULT_OUTPUT_EXTENSION}"]

    if out_path.suffix == "":
        out_path = out_path.with_suffix(f".{DEFAULT_OUTPUT_EXTENSION}")
    return [out_path]


def _print_request(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _decode_and_write(images: List[str], outputs: List[Path], force: bool) -> None:
    for idx, image_b64 in enumerate(images):
        if idx >= len(outputs):
            break
        if len(image_b64) > MAX_CODEX_BASE64_CHARS:
            _die("Image payload exceeded size limit.")
        out_path = outputs[idx]
        if out_path.exists() and not force:
            _die(f"Output already exists: {out_path} (use --force to overwrite)")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(base64.b64decode(image_b64))
        print(f"Wrote {out_path}")


def _result_field(item: object, field: str) -> Optional[str]:
    value = item.get(field) if isinstance(item, dict) else getattr(item, field, None)
    return value if isinstance(value, str) and value.strip() else None


def _validate_remote_image_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise RuntimeError("Image result URL must be an absolute HTTPS URL.")
    hostname = parsed.hostname.rstrip(".").lower()
    if hostname == "localhost" or hostname.endswith(".localhost") or hostname.endswith(".local"):
        raise RuntimeError("Image result URL may not target localhost or a local hostname.")
    try:
        addresses = {
            info[4][0]
            for info in socket.getaddrinfo(
                hostname,
                parsed.port or 443,
                type=socket.SOCK_STREAM,
            )
        }
    except socket.gaierror as exc:
        raise RuntimeError(f"Could not resolve image result URL host: {hostname}") from exc
    if not addresses:
        raise RuntimeError(f"Image result URL host resolved to no addresses: {hostname}")
    for address in addresses:
        ip = ipaddress.ip_address(address.split("%", 1)[0])
        if not ip.is_global:
            raise RuntimeError("Image result URL may not resolve to a private or reserved address.")
    return raw_url


class _SafeImageRedirectHandler(request.HTTPRedirectHandler):
    max_redirections = MAX_REMOTE_REDIRECTS

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _validate_remote_image_url(urljoin(req.full_url, newurl))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_IMAGE_DOWNLOAD_OPENER = request.build_opener(_SafeImageRedirectHandler())


def _download_image_result(raw_url: str, timeout: int) -> bytes:
    url = _validate_remote_image_url(raw_url)
    headers = {"Accept": "image/*"}
    if _image_user_agent():
        headers["User-Agent"] = _image_user_agent()
    req = request.Request(url, headers=headers, method="GET")
    try:
        with _IMAGE_DOWNLOAD_OPENER.open(req, timeout=timeout) as response:
            final_url = response.geturl()
            _validate_remote_image_url(final_url)
            payload = response.read(MAX_IMAGE_BYTES + 1)
    except (error.HTTPError, error.URLError, TimeoutError, socket.timeout) as exc:
        raise RuntimeError(f"Failed to download image result URL: {exc}") from exc
    if not payload:
        raise RuntimeError("Downloaded image result was empty.")
    if len(payload) > MAX_IMAGE_BYTES:
        raise RuntimeError("Downloaded image result exceeded 50MB limit.")
    return payload


def _api_result_bytes(item: object, timeout: int) -> bytes:
    image_b64 = _result_field(item, "b64_json")
    if image_b64:
        if len(image_b64) > MAX_CODEX_BASE64_CHARS:
            raise RuntimeError("Image payload exceeded size limit.")
        try:
            payload = base64.b64decode(image_b64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise RuntimeError("Image API returned invalid base64 image data.") from exc
        if not payload:
            raise RuntimeError("Image API returned an empty base64 image payload.")
        return payload
    image_url = _result_field(item, "url")
    if image_url:
        return _download_image_result(image_url, timeout)
    raise RuntimeError("Image API result included neither b64_json nor url.")


def _write_api_results(items: Iterable[object], outputs: List[Path], force: bool, timeout: int) -> None:
    wrote = 0
    for idx, item in enumerate(items):
        if idx >= len(outputs):
            break
        out_path = outputs[idx]
        if out_path.exists() and not force:
            _die(f"Output already exists: {out_path} (use --force to overwrite)")
        payload = _api_result_bytes(item, timeout)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(payload)
        print(f"Wrote {out_path}")
        wrote += 1
    if wrote == 0:
        raise RuntimeError("Image API response did not include a usable image result.")


def _run_codex_image(
    *,
    prompt: str,
    image_paths: List[Path],
    mask_path: Optional[Path],
    args: argparse.Namespace,
    output_paths: List[Path],
    endpoint_label: str,
) -> bool:
    if getattr(args, "selected_backend", None) != BACKEND_CODEX_OAUTH:
        return False
    operation = "edit" if image_paths else "generate"
    body = _codex_image_body(
        prompt=prompt,
        image_paths=image_paths,
        mask_path=mask_path,
        model=args.model,
        size=args.size,
        quality=args.quality,
    )
    endpoint_url = _codex_image_url(operation)
    if args.dry_run:
        _print_request(
            {
                "backend": "codex-oauth",
                "endpoint": endpoint_url,
                "operation": operation,
                "outputs": [str(p) for p in output_paths],
                "auth_file": str(_codex_auth_file()),
                "image_model": args.model,
                "input_images": [str(p) for p in image_paths],
                "mask": str(mask_path) if mask_path else None,
                "size": args.size,
                "quality": args.quality,
                "background": body["background"],
            }
        )
        return True

    print(
        f"Calling Codex OAuth image backend ({endpoint_label}) with {len(image_paths)} input image(s).",
        file=sys.stderr,
    )
    started = time.time()
    response = _post_codex_image_json(endpoint_url, body, int(getattr(args, "timeout", DEFAULT_TIMEOUT)))
    payloads = _extract_codex_image_payloads(response)
    elapsed = time.time() - started
    print(f"Codex OAuth image completed in {elapsed:.1f}s.", file=sys.stderr)
    _decode_and_write(payloads, output_paths, force=args.force)
    return True


def _create_client():
    try:
        from openai import OpenAI
    except ImportError:
        _die(f"openai SDK not installed in the active environment. {_dependency_hint('openai')}")
    kwargs = dict(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL") or None,
    )
    if _image_user_agent():
        kwargs["default_headers"] = {"User-Agent": _image_user_agent()}
    return OpenAI(**kwargs)


def _api_payload(model: str, prompt: str, size: str, quality: str) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"model": model, "prompt": prompt}
    # For a provider-neutral API, auto means "let the provider choose" and is
    # omitted. Explicit provider values are forwarded unchanged.
    if size != DEFAULT_SIZE:
        payload["size"] = size
    if quality != DEFAULT_QUALITY:
        payload["quality"] = quality
    return payload


def _check_mask_path(mask: Optional[str]) -> Optional[Path]:
    if not mask:
        return None
    mask_path = Path(mask)
    if not mask_path.exists():
        _die(f"Mask file not found: {mask_path}")
    if mask_path.suffix.lower() != ".png":
        _warn(f"Mask should be a PNG with an alpha channel: {mask_path}")
    if mask_path.stat().st_size > MAX_IMAGE_BYTES:
        _warn(f"Mask exceeds 50MB limit: {mask_path}")
    return mask_path


def _generate(args: argparse.Namespace) -> None:
    prompt = _read_prompt(args.prompt, args.prompt_file)

    payload = _api_payload(args.model, prompt, args.size, args.quality)
    output_paths = _build_output_paths(args.out)

    if args.dry_run:
        if _run_codex_image(
            prompt=prompt,
            image_paths=[],
            mask_path=None,
            args=args,
            output_paths=output_paths,
            endpoint_label="generate",
        ):
            return
        _print_request(
            {
                "backend": "openai-compatible-api",
                "endpoint": "/v1/images/generations",
                "outputs": [str(p) for p in output_paths],
                **payload,
            }
        )
        return

    if _run_codex_image(
        prompt=prompt,
        image_paths=[],
        mask_path=None,
        args=args,
        output_paths=output_paths,
        endpoint_label="generate",
    ):
        return

    print(
        "Calling Image API (generation). This can take up to a couple of minutes.",
        file=sys.stderr,
    )
    started = time.time()
    client = _create_client()
    result = client.images.generate(**payload)
    elapsed = time.time() - started
    print(f"Generation completed in {elapsed:.1f}s.", file=sys.stderr)

    _write_api_results(result.data, output_paths, force=args.force, timeout=args.timeout)


def _edit(args: argparse.Namespace) -> None:
    prompt = _read_prompt(args.prompt, args.prompt_file)

    image_paths = _check_image_paths(args.image)
    mask_path = _check_mask_path(args.mask)

    payload = _api_payload(args.model, prompt, args.size, args.quality)
    output_paths = _build_output_paths(args.out)

    if args.dry_run:
        if _run_codex_image(
            prompt=prompt,
            image_paths=image_paths,
            mask_path=mask_path,
            args=args,
            output_paths=output_paths,
            endpoint_label="edit",
        ):
            return
        payload_preview = dict(payload)
        payload_preview["image"] = [str(p) for p in image_paths]
        if mask_path:
            payload_preview["mask"] = str(mask_path)
        _print_request(
            {
                "backend": "openai-compatible-api",
                "endpoint": "/v1/images/edits",
                "outputs": [str(p) for p in output_paths],
                **payload_preview,
            }
        )
        return

    if _run_codex_image(
        prompt=prompt,
        image_paths=image_paths,
        mask_path=mask_path,
        args=args,
        output_paths=output_paths,
        endpoint_label="edit",
    ):
        return

    print(
        f"Calling Image API (edit) with {len(image_paths)} image(s).",
        file=sys.stderr,
    )
    started = time.time()
    client = _create_client()

    with _open_files(image_paths) as image_files, _open_mask(mask_path) as mask_file:
        request = dict(payload)
        request["image"] = image_files if len(image_files) > 1 else image_files[0]
        if mask_file is not None:
            request["mask"] = mask_file
        result = client.images.edit(**request)

    elapsed = time.time() - started
    print(f"Edit completed in {elapsed:.1f}s.", file=sys.stderr)
    _write_api_results(result.data, output_paths, force=args.force, timeout=args.timeout)


def _open_files(paths: List[Path]):
    return _FileBundle(paths)


def _open_mask(mask_path: Optional[Path]):
    if mask_path is None:
        return _NullContext()
    return _SingleFile(mask_path)


class _NullContext:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


class _SingleFile:
    def __init__(self, path: Path):
        self._path = path
        self._handle = None

    def __enter__(self):
        self._handle = self._path.open("rb")
        return self._handle

    def __exit__(self, exc_type, exc, tb):
        if self._handle:
            try:
                self._handle.close()
            except Exception:
                pass
        return False


class _FileBundle:
    def __init__(self, paths: List[Path]):
        self._paths = paths
        self._handles: List[object] = []

    def __enter__(self):
        self._handles = [p.open("rb") for p in self._paths]
        return self._handles

    def __exit__(self, exc_type, exc, tb):
        for handle in self._handles:
            try:
                handle.close()
            except Exception:
                pass
        return False


def _add_shared_args(
    parser: argparse.ArgumentParser,
    *,
    include_prompt: bool = True,
    include_out: bool = True,
) -> None:
    parser.add_argument(
        "--backend",
        choices=sorted(ALLOWED_BACKENDS),
        default=_default_backend(),
        help=(
            "Image transport backend. Defaults to IMAGE2PPT_IMAGE_BACKEND or auto. "
            "Use openai-compatible-api for provider-specific models."
        ),
    )
    parser.add_argument(
        "--model",
        default=_default_model(),
        help="Provider image model id. Defaults to IMAGE2PPT_IMAGE_MODEL or gpt-image-2.",
    )
    if include_prompt:
        parser.add_argument("--prompt", help="Prompt text. Use this or --prompt-file.")
        parser.add_argument("--prompt-file", help="Read prompt text from a file, or '-' for stdin.")
    parser.add_argument(
        "--size",
        default=DEFAULT_SIZE,
        help="Provider output-size value. auto omits the API field; explicit values pass through.",
    )
    parser.add_argument(
        "--quality",
        default=DEFAULT_QUALITY,
        help="Provider quality value. auto omits the API field; explicit values pass through.",
    )
    if include_out:
        parser.add_argument("--out", default=DEFAULT_OUTPUT_PATH, help="Output file for one image.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing output files.")
    parser.add_argument("--dry-run", action="store_true", help="Validate arguments and show the selected backend without calling it.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Network timeout in seconds.")


def main() -> int:
    _load_runtime_env()
    parser = argparse.ArgumentParser(
        prog="image2ppt image",
        description="""Unified image generation/editing backend for image2ppt.

Use this command for generated images, image edits, clean bases, and foreground
asset sheets in image2ppt runs.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=IMAGE_HELP_EPILOG,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser(
        "generate",
        help="Create a new image",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=GENERATE_HELP_EPILOG,
    )
    _add_shared_args(gen_parser)
    gen_parser.set_defaults(func=_generate)

    edit_parser = subparsers.add_parser(
        "edit",
        help="Edit one or more images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EDIT_HELP_EPILOG,
    )
    _add_shared_args(edit_parser)
    edit_parser.add_argument("--image", action="append", required=True, help="Input image path. Repeat for multiple inputs.")
    edit_parser.add_argument("--mask", help="Optional mask image path.")
    edit_parser.set_defaults(func=_edit)

    args = parser.parse_args()
    args.model = args.model.strip()
    args.size = args.size.strip()
    args.quality = args.quality.strip()
    _validate_model(args.model)
    _validate_size(args.size, args.model)
    _validate_quality(args.quality)
    args.selected_backend = _select_backend(args.backend, args.model)
    if args.selected_backend == BACKEND_OPENAI_COMPATIBLE:
        _ensure_api_key(args.dry_run)

    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
