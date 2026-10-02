#!/usr/bin/env python3
"""Read or write the user's default nature-figure plotting backend."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


VALID_BACKENDS = {"python", "r"}


def config_path() -> Path:
    override = os.environ.get("NATURE_FIGURE_CONFIG")
    if override:
        return Path(override).expanduser()
    return Path("~/.config/nature-skills/nature-figure.json").expanduser()


def read_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid nature-figure config JSON at {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid nature-figure config at {path}: expected object")
    return data


def write_config(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def get_backend(path: Path) -> int:
    backend = read_config(path).get("backend")
    if backend in VALID_BACKENDS:
        print(backend)
        return 0
    return 1


def set_backend(path: Path, backend: str) -> int:
    backend = backend.lower()
    if backend not in VALID_BACKENDS:
        raise SystemExit("backend must be one of: python, r")
    data = read_config(path)
    data["backend"] = backend
    write_config(path, data)
    print(backend)
    return 0


def clear_backend(path: Path) -> int:
    data = read_config(path)
    data.pop("backend", None)
    write_config(path, data)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("get", help="Print the saved backend; exit 1 if unset.")
    set_parser = subparsers.add_parser("set", help="Save the default backend.")
    set_parser.add_argument("backend", choices=sorted(VALID_BACKENDS))
    subparsers.add_parser("clear", help="Remove the saved backend preference.")
    subparsers.add_parser("path", help="Print the config path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = config_path()
    if args.command == "get":
        return get_backend(path)
    if args.command == "set":
        return set_backend(path, args.backend)
    if args.command == "clear":
        return clear_backend(path)
    if args.command == "path":
        print(path)
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
