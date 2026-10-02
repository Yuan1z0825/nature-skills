from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = "skills/nature-figure/references/ai-graphical-abstract-workflow.md"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def squash(text: str) -> str:
    return " ".join(text.split())


class NatureFigureAIGraphicalAbstractTests(unittest.TestCase):
    def test_reference_separates_practitioner_advice_from_policy(self) -> None:
        reference = read(REFERENCE)
        normalized = squash(reference)

        self.assertIn("practitioner guidance", normalized)
        self.assertIn("not as a Nature Portfolio submission policy", normalized)
        self.assertIn("internal design draft", normalized)
        self.assertIn("submission eligibility", normalized)
        self.assertIn("verified 15 August 2026", normalized)

        for url in (
            "https://doi.org/10.1038/d41586-026-02072-9",
            "https://www.nature.com/nature-portfolio/editorial-policies/ai",
        ):
            self.assertIn(url, reference)

    def test_workflow_covers_message_design_accountability_and_provenance(self) -> None:
        reference = read(REFERENCE)

        for requirement in (
            "single sentence",
            "intended audience",
            "evidence boundary",
            "left-to-right",
            "color-accessible palette",
            "Do not let AI invent measurements",
            "Retain a provenance bundle",
            "Human authors remain accountable",
        ):
            self.assertIn(requirement, reference)

    def test_router_manifest_and_provider_route_load_the_workflow(self) -> None:
        skill = read("skills/nature-figure/SKILL.md")
        manifest = read("skills/nature-figure/manifest.yaml")
        provider = read("skills/nature-figure/references/openrouter-image-generation.md")

        for text in (skill, manifest, provider):
            self.assertIn("ai-graphical-abstract-workflow.md", text)

        self.assertIn("version: 2.8.0", manifest)
        self.assertIn("planning or auditing only", skill)
        self.assertIn("internal design use and submission eligibility", provider)

    def test_bilingual_readmes_and_eval_cover_the_new_contract(self) -> None:
        readme_zh = read("skills/nature-figure/README.md")
        readme_en = read("skills/nature-figure/README_EN.md")
        evals = json.loads(read("skills/nature-figure/evals/evals.json"))

        for text in (readme_zh, readme_en):
            self.assertIn("ai-graphical-abstract-workflow.md", text)
            self.assertIn("Nature Careers", text)

        ids = {case["id"] for case in evals["evals"]}
        self.assertIn("ai-graphical-abstract-policy-and-accountability-gate", ids)


if __name__ == "__main__":
    unittest.main()
