#!/usr/bin/env python3
"""Configuration and independent runtime diagnostics for Image2PPT."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
from pathlib import Path


DEFAULT_CONFIG_HOME = "~/.image2ppt"
DEFAULT_CODEX_AUTH_FILE = "~/.codex/auth.json"
DEFAULT_IMAGE_MODEL = "gpt-image-2"
DEFAULT_IMAGE_BACKEND = "auto"
ALLOWED_IMAGE_BACKENDS = {"auto", "codex-oauth", "openai-compatible-api"}
ENV_FIELDS = (
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "IMAGE2PPT_IMAGE_MODEL",
    "IMAGE2PPT_IMAGE_BACKEND",
    "IMAGE2PPT_IMAGE_USER_AGENT",
    "PADDLE_OCR_TOKEN",
)
PADDLE_TOKEN_APPLY_URL = "https://aistudio.baidu.com/account/accessToken"
PADDLE_ENDPOINT = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
PADDLE_MODEL = "PaddleOCR-VL-1.6"
SKILL_ROOT = Path(__file__).resolve().parents[3]
CLI_ENTRY = SKILL_ROOT / "cli" / "image2ppt" / "cli.py"


def cli_reinstall_hint() -> str:
    return "`python -m pip install -r <image2ppt-root>/requirements.txt`"


def project_config_path() -> Path:
    return SKILL_ROOT / "config.yaml"


def user_config_path() -> Path:
    return Path(DEFAULT_CONFIG_HOME).expanduser() / "config.yaml"


def config_path(home: Path | None = None) -> Path:
    if home is not None:
        return Path(home).expanduser() / "config.yaml"
    explicit_home = os.getenv("IMAGE2PPT_CONFIG_HOME", "").strip()
    if explicit_home:
        return Path(explicit_home).expanduser() / "config.yaml"
    project = project_config_path()
    if project.is_file():
        return project
    user = user_config_path()
    if user.is_file():
        return user
    # A fresh project-local Skill creates config.yaml beside config.example.yaml.
    return project


def runtime_home() -> Path:
    return config_path().parent


def config_scope(path: Path | None = None) -> str:
    resolved = (path or config_path()).resolve()
    if resolved == project_config_path().resolve():
        return "project"
    if resolved == user_config_path().resolve():
        return "user"
    return "override"


def read_config_file(path: Path) -> dict:
    path = Path(path).expanduser()
    if not path.exists():
        return {}
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(f"PyYAML is required to read Image2PPT config. Install with {cli_reinstall_hint()}.") from exc
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid config file: {path}")
    return data


def write_config_file(path: Path, values: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(f"PyYAML is required to write Image2PPT config. Install with {cli_reinstall_hint()}.") from exc
    data = {key: values[key] for key in ENV_FIELDS if values.get(key)}
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, allow_unicode=True, sort_keys=True)


def mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}...{value[-4:]}"


def codex_auth_file() -> Path:
    return Path(os.getenv("CODEX_AUTH_FILE", DEFAULT_CODEX_AUTH_FILE)).expanduser()


def codex_oauth_ready() -> bool:
    path = codex_auth_file()
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    tokens = data.get("tokens")
    return isinstance(tokens, dict) and bool(str(tokens.get("access_token") or "").strip())


def codex_model_compatible(model: str) -> bool:
    return "gpt-image-" in str(model).lower()


def select_image_backend(values: dict, codex_ready: bool, api_ready: bool) -> tuple[str, bool]:
    preference = str(values.get("IMAGE2PPT_IMAGE_BACKEND") or DEFAULT_IMAGE_BACKEND).strip().lower()
    if preference not in ALLOWED_IMAGE_BACKENDS:
        return "invalid", False
    model = str(values.get("IMAGE2PPT_IMAGE_MODEL") or DEFAULT_IMAGE_MODEL)
    if preference == "codex-oauth":
        return "codex-oauth", bool(codex_ready and codex_model_compatible(model))
    if preference == "openai-compatible-api":
        return "openai-compatible-api", api_ready
    if codex_ready and codex_model_compatible(model):
        return "codex-oauth", True
    return "openai-compatible-api", api_ready


def config(args: argparse.Namespace) -> int:
    home = runtime_home()
    values = read_config_file(config_path(home))
    before = dict(values)
    if args.api_key:
        values["OPENAI_API_KEY"] = args.api_key
    if args.base_url is not None:
        values["OPENAI_BASE_URL"] = args.base_url.strip()
    if args.clear_base_url:
        values.pop("OPENAI_BASE_URL", None)
    if args.model is not None:
        values["IMAGE2PPT_IMAGE_MODEL"] = args.model.strip()
    if args.image_backend is not None:
        backend = args.image_backend.strip().lower()
        if backend not in ALLOWED_IMAGE_BACKENDS:
            raise SystemExit(
                "--image-backend must be auto, codex-oauth, or openai-compatible-api"
            )
        values["IMAGE2PPT_IMAGE_BACKEND"] = backend
    if args.image_user_agent is not None:
        values["IMAGE2PPT_IMAGE_USER_AGENT"] = args.image_user_agent.strip()
    if args.clear_image_user_agent:
        values.pop("IMAGE2PPT_IMAGE_USER_AGENT", None)
    if args.paddle_ocr_token:
        values["PADDLE_OCR_TOKEN"] = args.paddle_ocr_token.strip()
    changed = sorted(key for key in ENV_FIELDS if before.get(key) != values.get(key))
    if changed or not config_path(home).exists():
        write_config_file(config_path(home), values)
        state = "updated" if before else "created"
    else:
        state = "unchanged"
    print(f"config={state} path={config_path(home)}")
    print(f"changed={', '.join(changed) if changed else '<none>'}")
    for key in ENV_FIELDS:
        value = str(values.get(key, ""))
        if key in ("OPENAI_API_KEY", "PADDLE_OCR_TOKEN"):
            value = mask_secret(value)
        print(f"{key}={value or '<unset>'}")
    return 0


def module_status() -> dict[str, dict]:
    purposes = {
        "pypdfium2": "PDF input normalization and rendered-slide rasterization",
        "PIL": "image normalization, assets, previews, and offline OCR geometry",
        "openai": "optional image backend",
        "yaml": "local configuration",
        "numpy": "offline ink metrics",
        "requests": "PaddleOCR HTTP client",
    }
    return {
        name: {"available": importlib.util.find_spec(name) is not None, "purpose": purpose}
        for name, purpose in purposes.items()
    }


def renderer_status() -> dict:
    system = platform.system().lower()
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    libreoffice = shutil.which("libreoffice") or shutil.which("soffice")
    powerpoint_candidate = bool(system == "windows" and powershell)
    selection = "powerpoint-com" if powerpoint_candidate else ("libreoffice" if libreoffice else "missing")
    return {
        "platform": system,
        "powerpoint_com_candidate": powerpoint_candidate,
        "powershell": powershell,
        "libreoffice": libreoffice,
        "selection": selection,
        "ready": bool(powerpoint_candidate or libreoffice),
    }


def font_status() -> dict:
    candidates = [
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("C:/Windows/Fonts/msyh.ttc"),
    ]
    existing = [str(path) for path in candidates if path.is_file()]
    fc_match = shutil.which("fc-match")
    matched = ""
    if fc_match:
        try:
            result = subprocess.run(
                [fc_match, "-f", "%{family}|%{file}", "sans-serif"],
                text=True,
                capture_output=True,
                timeout=10,
                check=False,
            )
            if result.returncode == 0:
                matched = result.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            matched = ""
    return {"ready": bool(existing or matched), "fontconfig": fc_match, "matched": matched, "known_files": existing}


def image_processing_status(modules: dict[str, dict]) -> dict:
    imagemagick = shutil.which("magick") or shutil.which("convert")
    return {
        "pillow": modules["PIL"]["available"],
        "imagemagick": imagemagick,
        "ready": modules["PIL"]["available"],
        "note": "Pillow is the primary processor; ImageMagick is used for optional formula/image conversion paths.",
    }


def internal_resource_status() -> dict:
    required = {
        "skill": SKILL_ROOT / "SKILL.md",
        "cli": CLI_ENTRY,
        "runtime_main": Path(__file__).resolve().parent / "main.py",
        "ocr_client": Path(__file__).resolve().parent / "paddle_text_hints.py",
        "offline_ocr": Path(__file__).resolve().parent / "text_hints.py",
        "builder": Path(__file__).resolve().parent / "build_pptx_from_manifest.py",
        "validator": Path(__file__).resolve().parent / "validate_pptx.py",
        "worker_prompt_base": SKILL_ROOT / "prompts" / "page-worker-base.md",
        "worker_prompt_addendum": SKILL_ROOT / "prompts" / "page-worker.md",
        "prompt_builder": SKILL_ROOT / "scripts" / "build_page_worker_prompt.py",
        "page_qa": SKILL_ROOT / "scripts" / "run_image2ppt_qa.py",
        "final_qa": SKILL_ROOT / "scripts" / "run_final_image2ppt_qa.py",
        "renderer": SKILL_ROOT / "scripts" / "render_image2ppt_qa.py",
        "visual_review_evidence": SKILL_ROOT / "scripts" / "visual_review_evidence.py",
        "workflow": SKILL_ROOT / "references" / "workflow.md",
        "manifest_schema": SKILL_ROOT / "references" / "manifest-schema.md",
        "manifest_json_schema": SKILL_ROOT / "schemas" / "page-manifest-v2.schema.json",
        "decision_tree": SKILL_ROOT / "references" / "page-decision-tree.md",
        "cli_contract": SKILL_ROOT / "references" / "cli-helper.md",
        "ocr_contract": SKILL_ROOT / "references" / "ocr-text-hints-contract.md",
        "region_contract": SKILL_ROOT / "references" / "region-decomposition.md",
        "object_routing": SKILL_ROOT / "references" / "object-routing.md",
        "arrow_contract": SKILL_ROOT / "references" / "manifest-arrow-extension.md",
        "qa_contract": SKILL_ROOT / "references" / "qa-contract.md",
        "dependency_contract": SKILL_ROOT / "references" / "runtime-dependencies.md",
        "asset_contract": SKILL_ROOT / "references" / "assets-provenance-contract.md",
    }
    files = {key: {"path": str(path), "exists": path.is_file()} for key, path in required.items()}
    return {"ready": all(item["exists"] for item in files.values()), "files": files}


def collect_status(check_api: bool = False, check_ocr: bool = False) -> dict:
    home = runtime_home()
    active_config = config_path(home)
    config_values = read_config_file(active_config)
    values = dict(config_values)
    for key in ENV_FIELDS:
        if os.getenv(key):
            values[key] = os.environ[key]

    modules = module_status()
    renderer = renderer_status()
    fonts = font_status()
    processing = image_processing_status(modules)
    resources = internal_resource_status()
    api_ready = bool(values.get("OPENAI_API_KEY"))
    codex_ready = codex_oauth_ready()
    selected_backend, cli_fallback_ready = select_image_backend(values, codex_ready, api_ready)
    token = str(values.get("PADDLE_OCR_TOKEN") or "").strip()
    token_source = "environment" if os.getenv("PADDLE_OCR_TOKEN") else ("config" if token else "unset")
    offline_ready = modules["PIL"]["available"] and modules["numpy"]["available"]
    dependency_ready = all(item["available"] for item in modules.values())
    ok = (
        dependency_ready
        and renderer["ready"]
        and fonts["ready"]
        and processing["ready"]
        and resources["ready"]
        and offline_ready
        and (cli_fallback_ready if check_api else True)
        and (bool(token) if check_ocr else True)
    )
    return {
        "schema_version": "image2ppt-doctor-v1",
        "ok": ok,
        "skill_root": str(SKILL_ROOT),
        "local_cli": {"path": str(CLI_ENTRY), "ready": CLI_ENTRY.is_file(), "python": sys.executable},
        "config_home": str(home),
        "config_file": str(active_config),
        "config_scope": config_scope(active_config),
        "config_exists": active_config.exists(),
        "dependencies": modules,
        "internal_resources": resources,
        "rendering": renderer,
        "fonts": fonts,
        "image_processing": processing,
        "ocr": {
            "selection": "paddleocr-vl" if token else "builtin-ink",
            "token": "set" if token else "unset",
            "token_source": token_source,
            "endpoint": PADDLE_ENDPOINT,
            "model": PADDLE_MODEL,
            "network_client_ready": modules["requests"]["available"],
            "network_probe_performed": False,
            "fallback": {"backend": "builtin-ink", "ready": offline_ready, "priority": "network-first-then-local"},
            "apply_url": PADDLE_TOKEN_APPLY_URL,
            "configure_command": "image2ppt config --paddle-ocr-token <token>",
        },
        "image_backend": {
            "agent_builtin": {"checked": False, "ready": None, "tool_name": "image_gen.imagegen"},
            "codex_oauth": {"ready": codex_ready, "auth_file": str(codex_auth_file())},
            "api_fallback": {
                "ready": api_ready,
                "OPENAI_API_KEY": "set" if api_ready else "unset",
                "OPENAI_BASE_URL": values.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                "IMAGE2PPT_IMAGE_MODEL": values.get("IMAGE2PPT_IMAGE_MODEL", DEFAULT_IMAGE_MODEL),
                "IMAGE2PPT_IMAGE_USER_AGENT": values.get("IMAGE2PPT_IMAGE_USER_AGENT", "<default>"),
            },
            "preference": values.get("IMAGE2PPT_IMAGE_BACKEND", DEFAULT_IMAGE_BACKEND),
            "cli_fallback_ready": cli_fallback_ready,
            "selection": selected_backend,
        },
        "checks_requested": {"require_image_api": check_api, "require_network_ocr_token": check_ocr},
        "next": "no action needed" if ok else "inspect failed doctor sections and install/configure only the missing local or system dependency",
    }


def doctor(args: argparse.Namespace) -> int:
    status = collect_status(check_api=args.check_api, check_ocr=args.check_ocr)
    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return 0 if status["ok"] else 1

    print(f"skill root: {status['skill_root']}")
    print(f"local CLI: {'ready' if status['local_cli']['ready'] else 'missing'} ({status['local_cli']['path']})")
    print(f"config: {status['config_file']} ({'exists' if status['config_exists'] else 'missing'})")
    for module, item in status["dependencies"].items():
        print(f"python import {module}: {'ok' if item['available'] else 'missing'}")
    render = status["rendering"]
    print(f"PPTX renderer: {render['selection']} ({'ready' if render['ready'] else 'missing'})")
    print(f"fonts: {'ready' if status['fonts']['ready'] else 'missing'} ({status['fonts']['matched'] or 'known-file scan'})")
    processing = status["image_processing"]
    print(f"image processing: Pillow={'ready' if processing['pillow'] else 'missing'} ImageMagick={processing['imagemagick'] or 'optional/missing'}")
    ocr = status["ocr"]
    print(f"OCR: {ocr['selection']} token={ocr['token']} source={ocr['token_source']}")
    print(f"OCR endpoint: {ocr['endpoint']}")
    print(f"OCR model: {ocr['model']}")
    print(f"OCR fallback: {ocr['fallback']['backend']} ({'ready' if ocr['fallback']['ready'] else 'missing'})")
    backend = status["image_backend"]
    print(f"image CLI fallback: {backend['selection']} ({'ready' if backend['cli_fallback_ready'] else 'not configured'})")
    print(f"internal resources: {'ready' if status['internal_resources']['ready'] else 'missing'}")
    if ocr["token"] == "unset":
        print(f"PaddleOCR token is optional but recommended: apply at {ocr['apply_url']}, then run `{ocr['configure_command']}`.")
    print(f"next: {status['next']}")
    return 0 if status["ok"] else 1


def main() -> None:
    parser = argparse.ArgumentParser(prog="image2ppt", description="Manage Image2PPT configuration and runtime diagnostics")
    sub = parser.add_subparsers(required=True)
    doc = sub.add_parser("doctor", help="Check local runtime, rendering, OCR, image, font, and resource readiness")
    doc.add_argument("--check-api", action="store_true", help="Require Codex OAuth or image API credentials.")
    doc.add_argument("--check-ocr", action="store_true", help="Require a configured PaddleOCR token; no network request is made.")
    doc.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    doc.add_argument("--timeout", type=int, default=30, help="Reserved for opt-in network probes.")
    doc.set_defaults(func=doctor)
    cfg = sub.add_parser("config", help="Write or update the active project/user config.yaml")
    cfg.add_argument("--api-key", help="OpenAI or OpenAI-compatible image API key to store.")
    cfg.add_argument("--base-url", help="OpenAI-compatible base URL.")
    cfg.add_argument("--clear-base-url", action="store_true", help="Remove OPENAI_BASE_URL from the config file.")
    cfg.add_argument("--model", help="Default provider image model id.")
    cfg.add_argument(
        "--image-backend",
        choices=sorted(ALLOWED_IMAGE_BACKENDS),
        help="Default transport backend for image generate/edit calls.",
    )
    cfg.add_argument("--image-user-agent", help="Optional User-Agent for the OpenAI-compatible API only.")
    cfg.add_argument(
        "--clear-image-user-agent",
        action="store_true",
        help="Remove IMAGE2PPT_IMAGE_USER_AGENT from the config file.",
    )
    cfg.add_argument("--paddle-ocr-token", help=f"Baidu AI Studio PaddleOCR token. Apply at {PADDLE_TOKEN_APPLY_URL}.")
    cfg.set_defaults(func=config)
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
