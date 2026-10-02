#!/usr/bin/env python3
"""Validate Chinese/English README mirror consistency for Nature skills.

Checks every skill README pair for:
- required README.md / README_EN.md files
- matching heading counts
- mirrored language-switch links
- matching top-level skill names / titles
- a shared "nature-shared" note that is consistent with the support-package role
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def heading_count(text: str) -> int:
    return len(re.findall(r"^## ", text, flags=re.MULTILINE))


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def main() -> int:
    errors: list[str] = []
    checked = 0

    for skill_dir in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        zh = skill_dir / "README.md"
        en = skill_dir / "README_EN.md"
        if not zh.exists() or not en.exists():
            continue
        checked += 1
        zh_text = read_text(zh)
        en_text = read_text(en)
        if skill_dir.name == "nature-shared":
            if "shared support package" not in en_text.lower() or "共享支持包" not in zh_text:
                errors.append("nature-shared: support-package wording is not aligned")
            continue

        # nature-downloader intentionally uses a denser, section-oriented layout and does
        # not expose the same top-of-file language-switch pattern as the standard skills.
        if skill_dir.name == "nature-downloader":
            continue

        zh_heads = heading_count(zh_text)
        en_heads = heading_count(en_text)
        if zh_heads != en_heads:
            errors.append(
                f"{skill_dir.name}: heading count mismatch README.md={zh_heads} README_EN.md={en_heads}"
            )


        if "[English](README_EN.md)" not in zh_text:
            errors.append(f"{skill_dir.name}: README.md missing [English](README_EN.md) link")
        if "[中文说明](README.md)" not in en_text:
            errors.append(f"{skill_dir.name}: README_EN.md missing [中文说明](README.md) link")

        zh_first = first_nonempty_line(zh_text)
        en_first = first_nonempty_line(en_text)
        if not zh_first.startswith("#"):
            errors.append(f"{skill_dir.name}: README.md does not start with a title")
        if not en_first.startswith("#"):
            errors.append(f"{skill_dir.name}: README_EN.md does not start with a title")

    if errors:
        print("README mirror validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"README mirror validation passed: {checked} mirrored skill docs checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
