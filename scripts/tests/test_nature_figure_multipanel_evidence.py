from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = "skills/nature-figure/references/multipanel-evidence-architecture.md"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def squash(text: str) -> str:
    return " ".join(text.split())


class NatureFigureMultipanelEvidenceTests(unittest.TestCase):
    def test_guidance_is_corpus_derived_not_official_policy(self) -> None:
        reference = squash(read(REFERENCE))

        self.assertIn(
            "corpus-derived Nature-style guidance, not an official journal requirement",
            reference,
        )
        self.assertIn("author-supplied readings of flagship", reference)
        self.assertIn("Current journal instructions", reference)
        self.assertIn("Panel letters mark reading order", reference)

    def test_one_figure_claim_and_role_diversity_are_operational(self) -> None:
        reference = squash(read(REFERENCE))

        for requirement in (
            "one Results-level scientific question",
            "one figure = one major claim",
            "Panels are independently **necessary**, not independent stories",
            "Prefer role diversity over metric diversity",
            "a: R2 -> b: R2 pairwise tests -> c: MAPE",
            "a: perturbation design -> b: decisive comparison",
            "establish -> compare or control -> stress-test or discriminate",
        ):
            self.assertIn(requirement, reference)

    def test_placement_and_cross_figure_claim_escalation_are_explicit(self) -> None:
        reference = squash(read(REFERENCE))

        for requirement in (
            "Within a figure",
            "Across figures",
            "Main figure:",
            "Extended Data/SI:",
            "Another figure:",
            "Delete or merge:",
            "Does the next figure ask the question created by this figure?",
            "Do not hide a result that changes the conclusion",
        ):
            self.assertIn(requirement, reference)

    def test_corpus_examples_are_preserved_as_reasoning_anchors(self) -> None:
        reference = squash(read(REFERENCE))

        for requirement in (
            "MIRA — validation envelope",
            "consistency, information leakage and adversarial robustness",
            "Centromere architecture — scale to instance",
            "Robin — discovery sequence",
            "TabPFN — capability ladder",
            "aggregate performance, per-dataset generality and tuning-time efficiency",
            "a later figure should normally ask a deeper question",
        ):
            self.assertIn(requirement, reference)

    def test_router_manifest_contract_and_shared_results_are_connected(self) -> None:
        route_files = (
            "skills/nature-figure/SKILL.md",
            "skills/nature-figure/manifest.yaml",
            "skills/nature-figure/static/core/contract.md",
            "skills/nature-figure/references/figure-contract.md",
            "skills/nature-figure/references/design-theory.md",
        )

        for relative in route_files:
            self.assertIn("multipanel-evidence-architecture.md", read(relative), relative)

        skill = read("skills/nature-figure/SKILL.md")
        self.assertIn("../nature-shared/core/nature-results-discussion.md", skill)
        self.assertTrue(
            (ROOT / "skills/nature-shared/core/nature-results-discussion.md").is_file()
        )

    def test_bilingual_docs_and_eval_expose_the_workflow(self) -> None:
        readme_zh = read("skills/nature-figure/README.md")
        readme_en = read("skills/nature-figure/README_EN.md")
        evals = json.loads(read("skills/nature-figure/evals/evals.json"))

        self.assertIn("一张 Figure 回答一个 Results 级科学问题", readme_zh)
        self.assertIn("one figure answers one Results-level scientific question", readme_en)
        for text in (readme_zh, readme_en):
            self.assertIn("multipanel-evidence-architecture.md", text)

        ids = {case["id"] for case in evals["evals"]}
        self.assertIn("multipanel-figure-level-claim-and-role-diversity", ids)


if __name__ == "__main__":
    unittest.main()
