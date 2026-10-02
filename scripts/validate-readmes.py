#!/usr/bin/env python3
"""Validate repository README and skill README consistency."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
TOP_READMES = (ROOT / "README.md", ROOT / "README_EN.md")


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"missing {path.relative_to(ROOT)}")


def count_skill_index_rows(text: str) -> int:
    try:
        section = text.split("## 6.", 1)[1].split("## 7.", 1)[0]
    except IndexError:
        fail("README is missing the section 6 skill index or section 7 boundary")
    return len(re.findall(r"^\| \[`nature-[^`]+`\]\(", section, flags=re.MULTILINE))


def validate_top_readmes(triggerable_skill_count: int) -> None:
    for path in TOP_READMES:
        text = read(path)
        match = re.search(r"skills-(\d+)-0ea5e9", text)
        if not match:
            fail(f"{path.name} is missing the skills-count badge")
        badge_count = int(match.group(1))
        if badge_count != triggerable_skill_count:
            fail(
                f"{path.name} badge says {badge_count}, "
                f"expected {triggerable_skill_count} triggerable skills"
            )
        index_rows = count_skill_index_rows(text)
        if index_rows != triggerable_skill_count:
            fail(
                f"{path.name} skill index has {index_rows} rows, "
                f"expected {triggerable_skill_count}"
            )
        print(f"ok: {path.name} badge and index count = {triggerable_skill_count}")


def validate_skill_readmes(skill_dirs: list[Path]) -> None:
    for skill_dir in skill_dirs:
        name = skill_dir.name
        manifest = skill_dir / "manifest.yaml"
        readme = skill_dir / "README.md"
        readme_en = skill_dir / "README_EN.md"
        if not manifest.is_file():
            fail(f"{name} is missing manifest.yaml")
        if not readme.is_file():
            fail(f"{name} is missing README.md")
        if not readme_en.is_file():
            fail(f"{name} is missing README_EN.md")
        print(f"ok: {name} includes manifest.yaml, README.md, and README_EN.md")


def main() -> int:
    if not SKILLS_DIR.is_dir():
        fail("skills/ directory not found")

    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    triggerable_skill_dirs = [path for path in skill_dirs if path.name != "nature-shared"]
    validate_top_readmes(len(triggerable_skill_dirs))
    validate_skill_readmes(skill_dirs)
    print("README validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
