from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SKILL = "skills/nature-social-science/SKILL.md"
MANIFEST = "skills/nature-social-science/manifest.yaml"
REFERENCES = [
    "references/01-foundations.md",
    "references/02-workflow-steps1-3.md",
    "references/03-workflow-steps4-5.md",
    "references/04-workflow-steps6-8.md",
    "references/05-prompt-library.md",
    "references/06-worksheets.md",
    "references/07-status-terminology.md",
    "references/08-usage-handoff.md",
    "references/09-academic-expression.md",
]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def squash(text: str) -> str:
    return " ".join(text.split())


class NatureSocialScienceContractTests(unittest.TestCase):
    def test_skill_frontmatter_is_clean(self) -> None:
        text = read(SKILL)
        frontmatter = text.split("---", 2)[1]
        data = yaml.safe_load(frontmatter)

        self.assertEqual(data["name"], "nature-social-science")
        self.assertNotIn("agent_created", data)
        self.assertIn("description", data)

    def test_manifest_references_exist_on_disk(self) -> None:
        manifest = yaml.safe_load(read(MANIFEST))
        self.assertEqual(manifest["name"], "nature-social-science")

        for rel in manifest["always_load"]:
            self.assertTrue((ROOT / "skills/nature-social-science" / rel).is_file(), rel)
        for entry in manifest["references"]["on_demand"]:
            self.assertTrue(
                (ROOT / "skills/nature-social-science" / entry["path"]).is_file(),
                entry["path"],
            )

    def test_all_reference_files_present(self) -> None:
        for rel in REFERENCES:
            path = ROOT / "skills/nature-social-science" / rel
            self.assertTrue(path.is_file(), rel)
            self.assertGreater(len(path.read_text(encoding="utf-8").splitlines()), 50, rel)

    def test_iron_rules_and_fabrication_ban_are_stated(self) -> None:
        skill = squash(read(SKILL))

        # The four iron rules must be visible at router level, not only in references.
        self.assertIn("未知", skill)
        self.assertIn("矛盾、零结果、反向关系和替代解释", skill)
        # Fabrication ban is stated verbatim for every reply.
        self.assertIn("不要编造引文、来源或结果", skill)

    def test_status_systems_are_not_collapsed(self) -> None:
        skill = squash(read(SKILL))
        terminology = squash(read("skills/nature-social-science/references/07-status-terminology.md"))

        for status in (
            "PASS / REVISE / STOP",
            "NAMED / DOCUMENTED / ACCESS-CONFIRMED / TESTED",
            "SURVIVE / REDESIGN / PARK / REJECT",
            "CONFIRMED / RESOLVABLE DEPENDENCY / UNKNOWN / FAIL",
        ):
            self.assertIn(status, skill)

        self.assertIn("UNKNOWN ≠ PASS", terminology)
        self.assertIn("SURVIVE ≠ novel", terminology)

    def test_expression_reference_enforces_claim_ceiling(self) -> None:
        expression = squash(read("skills/nature-social-science/references/09-academic-expression.md"))

        self.assertIn("主张上限", expression)
        self.assertIn("Red flags", expression)
        # Verb-evidence matching must be explicit, not implied.
        self.assertTrue("动词" in expression and "证据" in expression)


if __name__ == "__main__":
    unittest.main()
