#!/usr/bin/env python3
"""Insert compact H2 navigation lists into long skill reference files."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills"
MIN_LINES = 100
CONTENTS_RE = re.compile(r"^##\s+(?:Table of Contents|Contents|目录)\s*$", re.IGNORECASE)
H1_RE = re.compile(r"^\ufeff?#\s+\S")
H2_RE = re.compile(r"^##\s+(.+?)\s*$")


def clean_heading(text: str) -> str:
    text = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.replace("`", "").replace("*", "").strip()


def github_anchor(text: str, seen: dict[str, int]) -> str:
    slug = clean_heading(text).casefold()
    slug = re.sub(r"[^\w\s-]", "", slug, flags=re.UNICODE)
    slug = re.sub(r"[\s-]+", "-", slug).strip("-") or "section"
    duplicate = seen.get(slug, 0)
    seen[slug] = duplicate + 1
    return slug if duplicate == 0 else f"{slug}-{duplicate}"


def add_contents(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) <= MIN_LINES or any(CONTENTS_RE.match(line) for line in lines[:40]):
        return False

    headings = [match.group(1) for line in lines if (match := H2_RE.match(line))]
    if not headings:
        return False

    try:
        insertion = next(index for index, line in enumerate(lines) if H1_RE.match(line)) + 1
    except StopIteration:
        return False

    seen: dict[str, int] = {}
    contents = ["", "## Contents", ""]
    for heading in headings:
        label = clean_heading(heading)
        contents.append(f"- [{label}](#{github_anchor(heading, seen)})")
    contents.append("")
    lines[insertion:insertion] = contents
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def main() -> int:
    updated = []
    for path in sorted(REFERENCES.glob("*/references/**/*.md")):
        if add_contents(path):
            updated.append(path.relative_to(ROOT))
    for path in updated:
        print(path)
    print(f"Updated {len(updated)} reference files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
