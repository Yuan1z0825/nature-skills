#!/usr/bin/env python3
"""Validate repository-level Nature Skills metadata and README consistency.

This lightweight check intentionally avoids optional runtime dependencies. It is
safe to run locally and in CI to catch stale skill counts, broken README index
links, malformed JSON/TOML configs, and missing per-skill metadata before a
documentation or skill change is merged.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import tomllib
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
README_FILES = (ROOT / "README.md", ROOT / "README_EN.md")
SKILL_LINK_RE = re.compile(r"\[`(nature-[^`]+)`\]\(skills/([^/)]+)/README(?:_EN)?\.md\)")
BADGE_RE = re.compile(r"badge/skills-(\d+)-")
EXCLUDED_INDEX_DIRS = {"nature-shared"}
EXCLUDED_LINK_DIRS = {"nature-shared", "nature-<topic>"}
JSON_FILE_RE = re.compile(r"(^|/)package-lock\.json$|\.json$")
TOML_FILE_RE = re.compile(r"\.toml$")
REFERENCE_CONTENTS_RE = re.compile(
    r"^##\s+(?:Table of Contents|Contents|目录)\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)
MAX_REFERENCE_LINES_WITHOUT_CONTENTS = 100


@dataclass
class ValidationError:
    path: pathlib.Path
    message: str

    def __str__(self) -> str:
        rel = self.path.relative_to(ROOT) if self.path.is_absolute() else self.path
        return f"{rel}: {self.message}"


def skill_dirs() -> list[pathlib.Path]:
    return sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())


def validate_skill_layout(skills: list[pathlib.Path]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    required_files = ("SKILL.md", "README.md", "README_EN.md", "manifest.yaml")
    for skill in skills:
        for filename in required_files:
            if not (skill / filename).is_file():
                errors.append(ValidationError(skill, f"missing required file {filename}"))
    return errors


def validate_structured_configs(skills: list[pathlib.Path]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for skill in skills:
        for path in sorted(skill.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            try:
                if JSON_FILE_RE.search(rel):
                    json.loads(path.read_text(encoding="utf-8"))
                elif TOML_FILE_RE.search(rel):
                    tomllib.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
                errors.append(ValidationError(path, f"invalid structured config: {exc}"))
    return errors


def validate_reference_navigation(skills: list[pathlib.Path]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for skill in skills:
        references = skill / "references"
        if not references.is_dir():
            continue
        for path in sorted(references.rglob("*.md")):
            text = path.read_text(encoding="utf-8", errors="replace")
            if len(text.splitlines()) > MAX_REFERENCE_LINES_WITHOUT_CONTENTS:
                first_lines = "\n".join(text.splitlines()[:40])
                if not REFERENCE_CONTENTS_RE.search(first_lines):
                    errors.append(
                        ValidationError(
                            path,
                            "reference files longer than 100 lines need a Contents section near the top",
                        )
                    )
    return errors


def validate_readme(readme: pathlib.Path, skills: list[pathlib.Path]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    text = readme.read_text(encoding="utf-8")
    expected = {path.name for path in skills if path.name not in EXCLUDED_INDEX_DIRS}
    expected_badge_count = len(expected)

    badges = BADGE_RE.findall(text)
    if not badges:
        errors.append(ValidationError(readme, "missing skills count badge"))
    elif int(badges[0]) != expected_badge_count:
        errors.append(
            ValidationError(
                readme,
                f"skills badge says {badges[0]}, but {expected_badge_count} public skills are indexed",
            )
        )

    linked = {
        match.group(2)
        for match in SKILL_LINK_RE.finditer(text)
        if match.group(2) not in EXCLUDED_LINK_DIRS
    }
    missing = sorted(expected - linked)
    extra = sorted(linked - expected)
    if missing:
        errors.append(ValidationError(readme, "skill index missing: " + ", ".join(missing)))
    if extra:
        errors.append(ValidationError(readme, "skill index references unknown dirs: " + ", ".join(extra)))

    broken = []
    for _label, dirname in SKILL_LINK_RE.findall(text):
        if dirname in EXCLUDED_LINK_DIRS:
            continue
        if not (ROOT / "skills" / dirname / "README.md").is_file():
            broken.append(dirname)
    if broken:
        errors.append(ValidationError(readme, "broken skill README links: " + ", ".join(sorted(set(broken)))))

    return errors


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"ERROR: skills directory not found: {SKILLS_DIR}", file=sys.stderr)
        return 1

    skills = skill_dirs()
    errors = validate_skill_layout(skills)
    errors.extend(validate_structured_configs(skills))
    errors.extend(validate_reference_navigation(skills))
    for readme in README_FILES:
        if readme.is_file():
            errors.extend(validate_readme(readme, skills))
        else:
            errors.append(ValidationError(readme, "README file is missing"))

    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Repository validation passed: {len(skills)} skill directories checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
