from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from support import SKILL_ROOT


class ProjectMetadataTests(unittest.TestCase):
    def test_versions_are_unified(self) -> None:
        manifest = (SKILL_ROOT / "manifest.yaml").read_text(encoding="utf-8")
        pyproject = (SKILL_ROOT / "cli" / "pyproject.toml").read_text(encoding="utf-8")
        package = (SKILL_ROOT / "cli" / "image2ppt" / "__init__.py").read_text(encoding="utf-8")
        skill_version = re.search(r"(?m)^version:\s*([^\s]+)$", manifest).group(1)
        project_version = re.search(r'(?m)^version\s*=\s*"([^"]+)"$', pyproject).group(1)
        package_version = re.search(r'(?m)^__version__\s*=\s*"([^"]+)"$', package).group(1)
        self.assertEqual(skill_version, project_version)
        self.assertEqual(skill_version, package_version)

    def test_requirements_match_package_dependencies(self) -> None:
        requirements = (SKILL_ROOT / "requirements.txt").read_text(encoding="utf-8")
        pyproject = (SKILL_ROOT / "cli" / "pyproject.toml").read_text(encoding="utf-8")

        def package_name(spec: str) -> str:
            return re.split(r"[<>=!~\[]", spec.strip(), maxsplit=1)[0].lower().replace("_", "-")

        requirement_names = {
            package_name(line)
            for line in requirements.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        dependency_block = re.search(r"(?s)dependencies\s*=\s*\[(.*?)\]", pyproject).group(1)
        dependency_names = {
            package_name(spec) for spec in re.findall(r'"([^"]+)"', dependency_block)
        }
        self.assertEqual(requirement_names, dependency_names)

    def test_readmes_are_mirrored_without_excluded_preview_assets(self) -> None:
        readme_cn = (SKILL_ROOT / "README.md").read_text(encoding="utf-8")
        readme_en = (SKILL_ROOT / "README_EN.md").read_text(encoding="utf-8")
        self.assertIn("[English](README_EN.md)", readme_cn)
        self.assertIn("[中文说明](README.md)", readme_en)
        for readme in (readme_cn, readme_en):
            self.assertIn("https://github.com/Paul-Jeo/Image2PPT", readme)
            self.assertIn("config.example.yaml", readme)
            self.assertIn("config.yaml", readme)
            self.assertNotIn("assets/readme/", readme)
        self.assertEqual(
            len(re.findall(r"^## ", readme_cn, flags=re.MULTILINE)),
            len(re.findall(r"^## ", readme_en, flags=re.MULTILINE)),
        )

    def test_public_config_template_contains_no_secret(self) -> None:
        yaml_template = (SKILL_ROOT / "config.example.yaml").read_text(encoding="utf-8")
        self.assertRegex(yaml_template, r'(?m)^PADDLE_OCR_TOKEN:\s*""\s*$')
        self.assertNotIn("sk-", yaml_template)
        self.assertFalse((SKILL_ROOT / ".env.example").exists())

    def test_secret_files_and_generated_runs_are_ignored(self) -> None:
        ignore = (SKILL_ROOT / ".gitignore").read_text(encoding="utf-8")
        patterns = (".env", "config.yaml", "output/", "runs/", "__pycache__/", "assets/readme/", ".github/")
        for pattern in patterns:
            self.assertIn(pattern, ignore)

    def test_openai_metadata_has_required_user_facing_fields(self) -> None:
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Nature Image2PPT"', metadata)
        self.assertIn("$nature-image2ppt", metadata)
        match = re.search(r'^\s*short_description:\s*"([^"]+)"', metadata, flags=re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertGreaterEqual(len(match.group(1)), 25)
        self.assertLessEqual(len(match.group(1)), 64)

    def test_page_manifest_v2_json_schema_is_valid_json(self) -> None:
        schema = (SKILL_ROOT / "schemas" / "page-manifest-v2.schema.json")
        payload = json.loads(schema.read_text(encoding="utf-8"))
        self.assertEqual(payload["properties"]["schema_version"]["const"], 2)
        self.assertIn("quality_evidence", payload["required"])

    def test_markdown_references_current_skill_sections(self) -> None:
        markdown = "\n".join(
            path.read_text(encoding="utf-8")
            for root in (SKILL_ROOT / "references", SKILL_ROOT / "prompts")
            for path in sorted(root.glob("*.md"))
        )
        for stale_reference in (
            "SKILL.md Entry Contract",
            "SKILL.md Phase 1",
            "SKILL.md Phase 3",
            "SKILL.md Phase 4",
            'SKILL.md subsection "Image Backend Selection"',
            "State Principles section of `SKILL.md`",
        ):
            self.assertNotIn(stale_reference, markdown)


if __name__ == "__main__":
    unittest.main()
