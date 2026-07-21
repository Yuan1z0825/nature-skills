#!/usr/bin/env python3
"""Verify declared Nature Skills Python distributions and imports.

The installer passes one or more simple requirements.txt files.  This checker
intentionally supports the repository's direct requirement format rather than
acting as a full pip requirements parser.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import os
import re
import sys
from pathlib import Path

try:
    from packaging.requirements import InvalidRequirement, Requirement
except ImportError:  # A fresh venv exposes packaging through pip's vendored copy.
    from pip._vendor.packaging.requirements import InvalidRequirement, Requirement


IMPORT_OVERRIDES = {
    "pillow": "PIL",
    "pyyaml": "yaml",
    "python-dateutil": "dateutil",
    "python-docx": "docx",
    "python-pptx": "pptx",
}


def normalize_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_requirements(path: Path) -> list[Requirement]:
    requirements: list[Requirement] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith(("-", "http://", "https://", "git+")):
            raise ValueError(f"{path}:{line_number}: unsupported requirement syntax: {line}")
        try:
            requirement = Requirement(line)
        except InvalidRequirement as exc:
            raise ValueError(f"{path}:{line_number}: cannot parse requirement: {line}") from exc
        if requirement.url is not None:
            raise ValueError(f"{path}:{line_number}: direct URLs are not supported")
        if requirement.marker is None or requirement.marker.evaluate():
            requirements.append(requirement)
    return requirements


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--playwright-chromium",
        action="store_true",
        help="also verify that the Playwright Chromium executable is present",
    )
    parser.add_argument("requirements", nargs="+", type=Path)
    args = parser.parse_args()

    distributions: dict[str, list[Requirement]] = {}
    try:
        for requirement_file in args.requirements:
            if not requirement_file.is_file():
                print(f"MISSING requirements file: {requirement_file}", file=sys.stderr)
                return 1
            for requirement in parse_requirements(requirement_file):
                distributions.setdefault(normalize_name(requirement.name), []).append(requirement)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1

    failed = False
    for normalized, requirements in sorted(distributions.items()):
        distribution_name = requirements[0].name
        import_name = IMPORT_OVERRIDES.get(normalized, distribution_name.replace("-", "_"))
        try:
            version = importlib.metadata.version(distribution_name)
        except importlib.metadata.PackageNotFoundError:
            print(f"MISSING {distribution_name}")
            failed = True
            continue
        unsatisfied = [str(req.specifier) for req in requirements if version not in req.specifier]
        if unsatisfied:
            constraints = ", ".join(unsatisfied)
            print(f"WRONG   {distribution_name}=={version}: requires {constraints}")
            failed = True
            continue
        try:
            importlib.import_module(import_name)
        except Exception as exc:  # Import failures can include broken binary wheels.
            print(f"BROKEN  {distribution_name}=={version}: import {import_name}: {exc}")
            failed = True
            continue
        print(f"OK      {distribution_name}=={version} (import {import_name})")

    if "matplotlib" in distributions:
        matplotlib_cache = os.environ.get("MPLCONFIGDIR")
        if not matplotlib_cache:
            print("BROKEN  Matplotlib cache: MPLCONFIGDIR is not configured")
            failed = True
        else:
            cache_path = Path(matplotlib_cache)
            if not cache_path.is_dir() or not os.access(cache_path, os.W_OK):
                print(f"BROKEN  Matplotlib cache is not writable: {cache_path}")
                failed = True
            else:
                print(f"OK      Matplotlib cache ({cache_path})")

    if args.playwright_chromium:
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as playwright:
                chromium_path = Path(playwright.chromium.executable_path)
            if not chromium_path.is_file():
                print(f"MISSING Playwright Chromium executable: {chromium_path}")
                failed = True
            else:
                print(f"OK      Playwright Chromium ({chromium_path})")
        except Exception as exc:
            print(f"BROKEN  Playwright Chromium check: {exc}")
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
