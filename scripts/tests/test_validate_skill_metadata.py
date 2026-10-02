from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "validate-skill-metadata.py"
SPEC = importlib.util.spec_from_file_location("validate_skill_metadata", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class SkillFrontmatterTests(unittest.TestCase):
    def parse(self, content: str):
        original_root = VALIDATOR.ROOT
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                skill = root / "skills" / "demo" / "SKILL.md"
                skill.parent.mkdir(parents=True)
                skill.write_text(content, encoding="utf-8")
                VALIDATOR.ROOT = root
                return VALIDATOR.parse_skill_frontmatter(skill)
        finally:
            VALIDATOR.ROOT = original_root

    def test_supported_metadata_is_valid(self) -> None:
        frontmatter, errors = self.parse(
            """---
name: demo
description: Demonstrate valid metadata.
license: MIT
metadata:
  author: Example Author
---
"""
        )

        self.assertEqual([], errors)
        self.assertEqual("demo", frontmatter["name"])

    def test_legacy_version_and_author_are_rejected(self) -> None:
        _frontmatter, errors = self.parse(
            """---
name: demo
description: Demonstrate invalid metadata.
version: 1.0.0
author: Example Author
---
"""
        )

        self.assertTrue(any("author, version" in error for error in errors), errors)

    def test_required_fields_must_be_non_empty(self) -> None:
        _frontmatter, errors = self.parse(
            """---
name: ""
metadata:
  author: Example Author
---
"""
        )

        self.assertTrue(any("missing required" in error for error in errors), errors)
        self.assertTrue(any("name must be a non-empty string" in error for error in errors), errors)

    def test_frontmatter_requires_a_closing_fence(self) -> None:
        _frontmatter, errors = self.parse(
            """---
name: demo
description: Missing closing fence.
"""
        )

        self.assertTrue(any("missing its closing" in error for error in errors), errors)


class OpenAIYamlTests(unittest.TestCase):
    def validate(self, content: str, skill_name: str = "demo") -> list[str]:
        original_root = VALIDATOR.ROOT
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path = root / "skills" / skill_name / "agents" / "openai.yaml"
                path.parent.mkdir(parents=True)
                path.write_text(content, encoding="utf-8")
                VALIDATOR.ROOT = root
                return VALIDATOR.validate_openai_yaml(path, skill_name)
        finally:
            VALIDATOR.ROOT = original_root

    def test_complete_quoted_interface_is_valid(self) -> None:
        errors = self.validate(
            '''interface:
  display_name: "Demo Skill"
  short_description: "Help with demonstrative skill workflows"
  default_prompt: "Use $demo to complete this demonstrative task."
'''
        )
        self.assertEqual([], errors)

    def test_default_prompt_must_name_the_skill(self) -> None:
        errors = self.validate(
            '''interface:
  display_name: "Demo Skill"
  short_description: "Help with demonstrative skill workflows"
  default_prompt: "Help me complete this demonstrative task."
'''
        )
        self.assertTrue(any("must explicitly mention $demo" in error for error in errors))

    def test_interface_strings_must_be_quoted(self) -> None:
        errors = self.validate(
            '''interface:
  display_name: Demo Skill
  short_description: "Help with demonstrative skill workflows"
  default_prompt: "Use $demo to complete this demonstrative task."
'''
        )
        self.assertTrue(any("display_name must be double-quoted" in error for error in errors))

    def test_support_only_skill_must_disable_implicit_invocation(self) -> None:
        content = '''interface:
  display_name: "Shared Support"
  short_description: "Shared references for dependent skills only"
  default_prompt: "Use $demo only as support for another skill."
'''
        errors = self.validate(content)
        self.assertEqual([], errors)

        original_root = VALIDATOR.ROOT
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path = root / "skills" / "demo" / "agents" / "openai.yaml"
                path.parent.mkdir(parents=True)
                path.write_text(content, encoding="utf-8")
                VALIDATOR.ROOT = root
                errors = VALIDATOR.validate_openai_yaml(
                    path,
                    "demo",
                    require_implicit_disabled=True,
                )
        finally:
            VALIDATOR.ROOT = original_root

        self.assertTrue(any("allow_implicit_invocation" in error for error in errors))

    def test_support_only_skill_accepts_explicit_disablement(self) -> None:
        content = '''interface:
  display_name: "Shared Support"
  short_description: "Shared references for dependent skills only"
  default_prompt: "Use $demo only as support for another skill."
policy:
  allow_implicit_invocation: false
'''
        original_root = VALIDATOR.ROOT
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path = root / "skills" / "demo" / "agents" / "openai.yaml"
                path.parent.mkdir(parents=True)
                path.write_text(content, encoding="utf-8")
                VALIDATOR.ROOT = root
                errors = VALIDATOR.validate_openai_yaml(
                    path,
                    "demo",
                    require_implicit_disabled=True,
                )
        finally:
            VALIDATOR.ROOT = original_root

        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
