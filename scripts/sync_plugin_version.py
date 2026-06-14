#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    (ROOT / ".claude-plugin" / "plugin.json", (("version",),)),
    (
        ROOT / ".claude-plugin" / "marketplace.json",
        (("version",), ("plugins", 0, "version")),
    ),
    (
        ROOT / "plugins" / "nature-skills" / ".codex-plugin" / "plugin.json",
        (("version",),),
    ),
)


def git_output(*args: str) -> str:
    result = subprocess.run(
        ("git", *args),
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def commit_version(ref: str) -> str:
    return git_output("rev-parse", "--short=12", ref)


def read_json(path: Path) -> OrderedDict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=OrderedDict)


def value_at(data: Any, path: tuple[str | int, ...]) -> Any:
    node = data
    for part in path:
        node = node[part]
    return node


def set_value(data: Any, path: tuple[str | int, ...], value: str) -> None:
    node = data
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = value


def write_json(path: Path, data: OrderedDict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize plugin manifest versions with the repository commit.",
    )
    parser.add_argument(
        "--version",
        help="Use an explicit version instead of the current short Git commit.",
    )
    parser.add_argument(
        "--ref",
        default="HEAD",
        help="Use the short Git commit for this ref when --version is not set.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only verify that all plugin manifest versions already match.",
    )
    args = parser.parse_args()

    version = (args.version or commit_version(args.ref)).strip()
    if not version:
        print("error: version cannot be empty", file=sys.stderr)
        return 2

    mismatches: list[str] = []
    changed: list[Path] = []

    for path, fields in TARGETS:
        data = read_json(path)
        local_changed = False
        for field in fields:
            old_value = value_at(data, field)
            if old_value != version:
                if args.check:
                    field_name = ".".join(str(part) for part in field)
                    mismatches.append(f"{path.relative_to(ROOT)}:{field_name}={old_value}")
                else:
                    set_value(data, field, version)
                    local_changed = True
        if local_changed:
            write_json(path, data)
            changed.append(path.relative_to(ROOT))

    if args.check:
        if mismatches:
            print(f"expected version: {version}")
            print("mismatched fields:")
            for mismatch in mismatches:
                print(f"  {mismatch}")
            return 1
        print(f"all plugin manifest versions match {version}")
        return 0

    if changed:
        print(f"plugin manifest version set to {version}")
        for path in changed:
            print(f"  updated {path}")
    else:
        print(f"plugin manifest version already set to {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
