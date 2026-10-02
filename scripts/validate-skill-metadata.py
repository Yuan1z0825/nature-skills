#!/usr/bin/env python3
"""Validate nature-skills metadata consistency.

Checks every top-level directory under skills/ for:
- required SKILL.md / README.md / README_EN.md / manifest.yaml files
- valid SKILL.md YAML frontmatter with only supported keys
- valid agents/openai.yaml interface metadata for every triggerable skill
- explicit implicit-invocation disablement for every support-only skill
- matching SKILL.md frontmatter name and manifest.yaml name
- valid manifest YAML
- relative manifest route paths, fragments, and scripts that exist on disk
- root README / README_EN skill badge count matching triggerable skills
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - developer environment guard
    raise SystemExit("Missing dependency: PyYAML. Install with `python -m pip install pyyaml`.") from exc

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
REQUIRED_FILES = ("SKILL.md", "README.md", "README_EN.md", "manifest.yaml")
SUPPORT_ONLY = {"nature-shared"}
COMPATIBILITY_SKILL_NAMES = {"nature-proposal-writer": "researchwrite"}
ALLOWED_SKILL_FRONTMATTER_KEYS = {
    "allowed-tools",
    "description",
    "license",
    "metadata",
    "name",
}
REQUIRED_SKILL_FRONTMATTER_KEYS = {"description", "name"}
REQUIRED_OPENAI_INTERFACE_KEYS = {
    "default_prompt",
    "display_name",
    "short_description",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_skill_frontmatter(skill_md: Path) -> tuple[dict[str, Any] | None, list[str]]:
    """Parse and validate the leading YAML frontmatter in a SKILL.md file."""
    text = read_text(skill_md)
    rel = skill_md.relative_to(ROOT)
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, [f"{rel}: SKILL.md must start with YAML frontmatter"]

    try:
        closing = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None, [f"{rel}: SKILL.md frontmatter is missing its closing ---"]

    try:
        frontmatter = yaml.safe_load("\n".join(lines[1:closing])) or {}
    except Exception as exc:
        return None, [f"{rel}: invalid SKILL.md frontmatter YAML: {exc}"]

    if not isinstance(frontmatter, dict):
        return None, [f"{rel}: SKILL.md frontmatter must be a mapping"]

    errors: list[str] = []
    keys = {str(key) for key in frontmatter}
    unexpected = sorted(keys - ALLOWED_SKILL_FRONTMATTER_KEYS)
    if unexpected:
        errors.append(
            f"{rel}: unsupported frontmatter keys: {', '.join(unexpected)}; "
            f"allowed: {', '.join(sorted(ALLOWED_SKILL_FRONTMATTER_KEYS))}"
        )
    missing = sorted(REQUIRED_SKILL_FRONTMATTER_KEYS - keys)
    if missing:
        errors.append(f"{rel}: missing required frontmatter keys: {', '.join(missing)}")
    for key in REQUIRED_SKILL_FRONTMATTER_KEYS:
        value = frontmatter.get(key)
        if key in keys and (not isinstance(value, str) or not value.strip()):
            errors.append(f"{rel}: frontmatter {key} must be a non-empty string")
    return frontmatter, errors


def validate_openai_yaml(
    path: Path,
    skill_name: str,
    *,
    require_implicit_disabled: bool = False,
) -> list[str]:
    """Validate the Codex-facing skill metadata contract."""
    rel = path.relative_to(ROOT)
    if not path.exists():
        return [f"{rel}: missing agents/openai.yaml"]

    raw = read_text(path)
    try:
        config = yaml.safe_load(raw) or {}
    except Exception as exc:
        return [f"{rel}: invalid YAML: {exc}"]

    errors: list[str] = []
    interface = config.get("interface")
    if not isinstance(interface, dict):
        return [f"{rel}: interface must be a mapping"]

    missing = sorted(REQUIRED_OPENAI_INTERFACE_KEYS - set(interface))
    if missing:
        errors.append(f"{rel}: missing interface keys: {', '.join(missing)}")

    for key in REQUIRED_OPENAI_INTERFACE_KEYS:
        value = interface.get(key)
        if key in interface and (not isinstance(value, str) or not value.strip()):
            errors.append(f"{rel}: interface.{key} must be a non-empty string")
        if key in interface and not re.search(
            rf'^\s+{re.escape(key)}:\s+"(?:[^"\\]|\\.)*"\s*$',
            raw,
            flags=re.MULTILINE,
        ):
            errors.append(f"{rel}: interface.{key} must be double-quoted")

    description = interface.get("short_description")
    if isinstance(description, str) and not 25 <= len(description) <= 64:
        errors.append(
            f"{rel}: interface.short_description must be 25-64 characters, "
            f"got {len(description)}"
        )

    prompt = interface.get("default_prompt")
    if isinstance(prompt, str) and f"${skill_name}" not in prompt:
        errors.append(
            f"{rel}: interface.default_prompt must explicitly mention ${skill_name}"
        )

    if require_implicit_disabled:
        policy = config.get("policy")
        if not isinstance(policy, dict) or policy.get("allow_implicit_invocation") is not False:
            errors.append(
                f"{rel}: support-only skills must set "
                "policy.allow_implicit_invocation to false"
            )
    return errors


PATH_KEYS = {"path", "reference", "script", "backend_script"}


def iter_manifest_paths(node: Any, parent_key: str | None = None):
    """Yield file paths declared in manifest routing metadata.

    Manifest routes can point at files in several shapes: explicit `path`,
    `reference`, or `script` keys; `always_load` lists; and `axes.*.values`
    mappings whose values are fragment paths. Keep environment/config fields such
    as `default_config` out of this check so local user paths are not treated as
    repository files.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            key = str(key)
            if key in PATH_KEYS and isinstance(value, str):
                yield value
            elif key == "values" and isinstance(value, dict):
                for route_path in value.values():
                    if isinstance(route_path, str):
                        yield route_path
                    else:
                        yield from iter_manifest_paths(route_path, key)
            else:
                yield from iter_manifest_paths(value, key)
    elif isinstance(node, list):
        for value in node:
            if parent_key in {"always_load", "on_demand"} and isinstance(value, str):
                yield value
            else:
                yield from iter_manifest_paths(value, parent_key)


def check_manifest_path(manifest_path: Path, skill_dir: Path, raw_path: str) -> str | None:
    if not raw_path.strip():
        return f"{manifest_path.relative_to(ROOT)}: empty referenced path"
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return f"{manifest_path.relative_to(ROOT)}: referenced path must be relative: {raw_path}"

    parts = candidate.parts
    if ".." in parts and not (len(parts) >= 2 and parts[0] == ".." and parts[1] == "nature-shared"):
        return (
            f"{manifest_path.relative_to(ROOT)}: referenced path may only leave the skill "
            f"directory for ../nature-shared/: {raw_path}"
        )

    target = skill_dir / candidate
    try:
        target.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return f"{manifest_path.relative_to(ROOT)}: referenced path escapes the repository: {raw_path}"

    if not target.exists():
        return f"{manifest_path.relative_to(ROOT)}: missing referenced path {raw_path}"
    return None


def check_badge_count(readme: Path, expected: int) -> list[str]:
    text = read_text(readme)
    errors: list[str] = []
    badge = re.search(r"skills-(\d+)-", text)
    if badge and int(badge.group(1)) != expected:
        errors.append(f"{readme.relative_to(ROOT)}: badge says skills-{badge.group(1)}, expected skills-{expected}")
    return errors


def main() -> int:
    errors: list[str] = []
    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    triggerable_count = sum(1 for p in skill_dirs if p.name not in SUPPORT_ONLY)

    for skill_dir in skill_dirs:
        rel = skill_dir.relative_to(ROOT)
        for filename in REQUIRED_FILES:
            path = skill_dir / filename
            if not path.exists():
                errors.append(f"{rel}: missing {filename}")

        manifest_path = skill_dir / "manifest.yaml"
        skill_md = skill_dir / "SKILL.md"
        if not manifest_path.exists() or not skill_md.exists():
            continue

        try:
            manifest = yaml.safe_load(read_text(manifest_path)) or {}
        except Exception as exc:
            errors.append(f"{manifest_path.relative_to(ROOT)}: invalid YAML: {exc}")
            continue

        frontmatter, frontmatter_errors = parse_skill_frontmatter(skill_md)
        errors.extend(frontmatter_errors)
        manifest_name = manifest.get("name")
        skill_name = frontmatter.get("name") if frontmatter else None
        if manifest_name != skill_name:
            errors.append(
                f"{rel}: manifest name {manifest_name!r} does not match SKILL.md name {skill_name!r}"
            )

        expected_skill_name = COMPATIBILITY_SKILL_NAMES.get(skill_dir.name, skill_dir.name)
        if skill_name != expected_skill_name:
            errors.append(
                f"{rel}: SKILL.md name {skill_name!r} must match directory name "
                f"{skill_dir.name!r} (expected {expected_skill_name!r})"
            )

        if isinstance(skill_name, str):
            errors.extend(
                validate_openai_yaml(
                    skill_dir / "agents" / "openai.yaml",
                    skill_name,
                    require_implicit_disabled=skill_dir.name in SUPPORT_ONLY,
                )
            )

        for raw_path in iter_manifest_paths(manifest):
            error = check_manifest_path(manifest_path, skill_dir, raw_path)
            if error:
                errors.append(error)

    for readme in (ROOT / "README.md", ROOT / "README_EN.md"):
        if readme.exists():
            errors.extend(check_badge_count(readme, triggerable_count))

    if errors:
        print("Skill metadata validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Skill metadata validation passed: {len(skill_dirs)} skill directories, "
        f"{triggerable_count} triggerable skills."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
