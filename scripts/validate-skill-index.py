#!/usr/bin/env python3
"""Validate the main README skill index against the skills/ directory.

Checks:
- the number of listed triggerable skills matches the skill index count
- every non-support skill appears in the README and README_EN tables
- every index entry points to an existing skill README
- nature-shared stays excluded from the triggerable skill count
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
SUPPORT_ONLY = {"nature-shared"}
INDEX_RE = re.compile(r"^\| \[`([^`]+)`\]\((skills/[^)]+/README(?:_EN)?\.md)\) \|", re.M)
PLACEHOLDER_SKILL = "nature-<topic>"


def filter_entries(entries):
    return [item for item in entries if item[0] != PLACEHOLDER_SKILL]

def expected_skill_list(skills):
    return [s for s in skills if s not in SUPPORT_ONLY]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_index(text: str):
    return INDEX_RE.findall(text)


def main() -> int:
    errors: list[str] = []
    skills = sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir())
    triggerable = [s for s in skills if s not in SUPPORT_ONLY]

    zh = read_text(ROOT / "README.md")
    en = read_text(ROOT / "README_EN.md")
    zh_entries = parse_index(zh)
    en_entries = parse_index(en)
    zh_index = filter_entries(zh_entries)
    en_index = filter_entries(en_entries)

    if len(zh_index) != len(triggerable):
        errors.append(
            f"README.md index count {len(zh_index)} does not match triggerable skills {len(triggerable)}"
        )
    if len(en_index) != len(triggerable):
        errors.append(
            f"README_EN.md index count {len(en_index)} does not match triggerable skills {len(triggerable)}"
        )

    zh_names = [name for name, _ in zh_index]
    en_names = [name for name, _ in en_index]

    if zh_names != en_names:
        errors.append("README.md and README_EN.md index skill order differs")

    expected = expected_skill_list(skills)
    if zh_names != expected:
        missing = [s for s in expected if s not in zh_names]
        extra = [s for s in zh_names if s not in expected]
        if missing:
            errors.append(f"README skill index missing: {missing}")
        if extra:
            errors.append(f"README skill index has unexpected entries: {extra}")

    for name, rel in zh_index + en_index:
        target = ROOT / rel
        if not target.exists():
            errors.append(f"Missing index target: {rel} for {name}")

    if "nature-shared" in zh_names or "nature-shared" in en_names:
        errors.append("nature-shared must not appear in the triggerable skill index")

    if errors:
        print("Skill index validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Skill index validation passed: {len(triggerable)} triggerable skills, "
        f"{len(zh_entries)} listed entries."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
