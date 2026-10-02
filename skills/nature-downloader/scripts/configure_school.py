#!/usr/bin/env python3
"""Command line helper for literature-downloader school configuration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from config import CONFIG_FILE, config_exists, load_config, save_config, validate  # noqa: E402
from health_check import health_check  # noqa: E402
from schools_loader import list_school_names  # noqa: E402
from wizard import Wizard, infer_access_from_url  # noqa: E402


def cmd_preset(args: argparse.Namespace) -> int:
    result = Wizard().configure_from_preset(args.school)
    cfg = result["config"]
    print(json.dumps({"ok": True, "path": result["path"], "school": cfg["school"]["name"]}, ensure_ascii=False))
    return 0


def cmd_url(args: argparse.Namespace) -> int:
    result = Wizard().configure_from_resource_url(args.url)
    cfg = result["config"]
    inferred = result["inferred"]
    print(
        json.dumps(
            {
                "ok": True,
                "path": result["path"],
                "school": cfg["school"]["name"],
                "entry_type": inferred["entry_type"],
                "auth_type": inferred["auth_type"],
                "sso_domain": inferred["sso_domain"],
                "resource_entry": inferred["resource_entry"],
            },
            ensure_ascii=False,
        )
    )
    return 0


def cmd_infer(args: argparse.Namespace) -> int:
    print(json.dumps(infer_access_from_url(args.url), ensure_ascii=False, indent=2))
    return 0


def cmd_show(_: argparse.Namespace) -> int:
    cfg = load_config()
    if cfg is None:
        print(f"尚未配置，配置文件路径：{CONFIG_FILE}")
        return 2
    errors = validate(cfg)
    print(json.dumps({"ok": not errors, "path": str(CONFIG_FILE), "errors": errors, "config": cfg}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def cmd_cnki_url(args: argparse.Namespace) -> int:
    cfg = load_config()
    if cfg is None:
        print(f"尚未配置，配置文件路径：{CONFIG_FILE}")
        return 2
    cfg.setdefault("discovery", {})["cnki_url"] = args.url
    path = save_config(cfg)
    print(json.dumps({"ok": True, "path": str(path), "cnki_url": args.url}, ensure_ascii=False))
    return 0


def cmd_health(args: argparse.Namespace) -> int:
    result = health_check(force=args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


def cmd_list(_: argparse.Namespace) -> int:
    for name in list_school_names():
        print(name)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Configure school access for nature-downloader.")
    sub = parser.add_subparsers(dest="command", required=True)

    preset = sub.add_parser("preset", help="Configure from bundled school preset.")
    preset.add_argument("school", help="Optional user-maintained preset name. The distributed skill contains no institution presets.")
    preset.set_defaults(func=cmd_preset)

    url = sub.add_parser("url", help="Configure from a library resource portal or authentication URL.")
    url.add_argument("url", help="Library resource/database portal URL.")
    url.set_defaults(func=cmd_url)

    infer = sub.add_parser("infer", help="Infer access route from a library resource URL without saving.")
    infer.add_argument("url", help="Library resource/database portal URL.")
    infer.set_defaults(func=cmd_infer)

    show = sub.add_parser("show", help="Show current configuration.")
    show.set_defaults(func=cmd_show)

    cnki_url = sub.add_parser("cnki-url", help="Save the CNKI entry URL for Chinese literature downloads.")
    cnki_url.add_argument("url", help="CNKI entry URL from the library portal, or the public CNKI search entry.")
    cnki_url.set_defaults(func=cmd_cnki_url)

    health = sub.add_parser("health", help="Run connectivity health check.")
    health.add_argument("--force", action="store_true", help="Ignore cached health result.")
    health.set_defaults(func=cmd_health)

    list_cmd = sub.add_parser("list", help="List bundled school presets.")
    list_cmd.set_defaults(func=cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
