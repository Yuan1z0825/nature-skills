#!/usr/bin/env python3
"""Configure publisher API credentials without echoing secrets."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REGISTRY_FILE = Path(__file__).resolve().parents[1] / "data" / "publishers.json"
PROVIDER_REGISTRY = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
PROVIDERS = tuple(PROVIDER_REGISTRY)
CONFIG_DIR = Path(os.environ.get("LIT_DL_CONFIG_DIR", Path.home() / ".config" / "lit-dl"))
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save(path: Path, value: dict, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temp_name = tempfile.mkstemp(prefix=path.name, dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.chmod(temp_name, mode)
        os.replace(temp_name, path)
        os.chmod(path, mode)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _mask(value: str) -> str:
    return "*" * max(0, len(value) - 4) + value[-4:]


def cmd_set(args: argparse.Namespace) -> int:
    if args.stdin:
        api_key = sys.stdin.readline().strip()
    else:
        api_key = args.api_key or os.environ.get("LIT_DL_API_KEY") or getpass.getpass("API key: ")
    if not api_key:
        raise SystemExit("API key 不能为空")
    values = {"api_key": api_key.strip()}
    if args.insttoken:
        values["insttoken"] = args.insttoken.strip()
    if args.authtoken:
        values["authtoken"] = args.authtoken.strip()
    if args.fulltext_endpoint:
        values["fulltext_endpoint"] = args.fulltext_endpoint.strip()
    all_credentials = _load(CREDENTIALS_FILE)
    all_credentials[args.provider] = values
    _save(CREDENTIALS_FILE, all_credentials)
    print(json.dumps({"ok": True, "provider": args.provider, "path": str(CREDENTIALS_FILE), "api_key": _mask(values["api_key"])}, ensure_ascii=False))
    return 0


def cmd_show(_: argparse.Namespace) -> int:
    credentials = _load(CREDENTIALS_FILE)
    masked = {provider: {key: _mask(str(value)) for key, value in values.items()} for provider, values in credentials.items()}
    print(json.dumps({"path": str(CREDENTIALS_FILE), "credentials": masked, "settings": _load(SETTINGS_FILE)}, ensure_ascii=False, indent=2))
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    credentials = _load(CREDENTIALS_FILE)
    credentials.pop(args.provider, None)
    _save(CREDENTIALS_FILE, credentials)
    print(json.dumps({"ok": True, "provider": args.provider}, ensure_ascii=False))
    return 0


def _validation_request(provider: str, values: dict) -> urllib.request.Request:
    key = values["api_key"]
    if provider == "elsevier":
        url = "https://api.elsevier.com/content/article/doi/10.1016/S0140-6736(20)30183-5?view=META"
        headers = {"X-ELS-APIKey": key, "Accept": "application/json"}
        if values.get("insttoken"):
            headers["X-ELS-Insttoken"] = values["insttoken"]
        return urllib.request.Request(url, headers=headers)
    if provider == "springer_nature":
        url = "https://api.springernature.com/meta/v2/json?" + urllib.parse.urlencode({"q": "keyword:test", "api_key": key, "p": 1})
        return urllib.request.Request(url, headers={"Accept": "application/json"})
    url = "https://ieeexploreapi.ieee.org/api/v1/search/articles?" + urllib.parse.urlencode({"apikey": key, "querytext": "test", "max_records": 1})
    return urllib.request.Request(url, headers={"Accept": "application/json"})


def cmd_validate(args: argparse.Namespace) -> int:
    values = _load(CREDENTIALS_FILE).get(args.provider)
    if not values or not values.get("api_key"):
        print(json.dumps({"ok": False, "provider": args.provider, "status": "credentials_missing"}, ensure_ascii=False))
        return 2
    try:
        with urllib.request.urlopen(_validation_request(args.provider, values), timeout=30) as response:
            status = response.status
    except urllib.error.HTTPError as error:
        status = error.code
    except OSError as error:
        print(json.dumps({"ok": False, "provider": args.provider, "status": "validation_failed", "error": str(error)}, ensure_ascii=False))
        return 1
    valid = status not in (401, 403)
    print(json.dumps({"ok": valid, "provider": args.provider, "http_status": status, "status": "configured" if valid else "credentials_invalid"}, ensure_ascii=False))
    return 0 if valid else 1


def cmd_contact_email(args: argparse.Namespace) -> int:
    settings = _load(SETTINGS_FILE)
    settings.setdefault("open_access", {})["contact_email"] = args.email
    _save(SETTINGS_FILE, settings)
    print(json.dumps({"ok": True, "path": str(SETTINGS_FILE), "contact_email": args.email}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Configure nature-downloader publisher API credentials.")
    sub = parser.add_subparsers(dest="command", required=True)
    set_cmd = sub.add_parser("set")
    set_cmd.add_argument("provider", choices=PROVIDERS)
    set_cmd.add_argument("--api-key", help="Prefer the hidden prompt or LIT_DL_API_KEY over command-line secrets.")
    set_cmd.add_argument("--stdin", action="store_true", help="Read the API key from stdin without placing it in process arguments or output.")
    set_cmd.add_argument("--insttoken", help="Elsevier institutional token, if issued.")
    set_cmd.add_argument("--authtoken", help="Elsevier authentication token, if issued.")
    set_cmd.add_argument("--fulltext-endpoint", help="IEEE paid Full-Text Access API endpoint template issued for your product; use {doi} as the placeholder.")
    set_cmd.set_defaults(func=cmd_set)
    show = sub.add_parser("show")
    show.set_defaults(func=cmd_show)
    delete = sub.add_parser("delete")
    delete.add_argument("provider", choices=PROVIDERS)
    delete.set_defaults(func=cmd_delete)
    validate = sub.add_parser("validate")
    validate.add_argument("provider", choices=PROVIDERS)
    validate.set_defaults(func=cmd_validate)
    email = sub.add_parser("contact-email")
    email.add_argument("email")
    email.set_defaults(func=cmd_contact_email)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
