from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = "skills/nature-shared/core/main-text-discipline.md"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def squash(text: str) -> str:
    return " ".join(text.split())


class MainTextDisciplineTests(unittest.TestCase):
    def test_contract_classifies_results_before_placement(self) -> None:
        contract = squash(read(CONTRACT))

        for result_class in (
            "core_discovery",
            "necessary_support",
            "qualification",
            "robustness",
            "heterogeneity",
            "provenance_detail",
            "alternative_inference",
            "edge_case",
        ):
            self.assertIn(result_class, contract)

        self.assertIn("Classify by function in this paper", contract)
        self.assertIn("shortest sufficient evidence chain", contract)

    def test_contract_prevents_accretion_duplication_and_recursion(self) -> None:
        contract = squash(read(CONTRACT))

        for requirement in (
            "Every requested addition triggers a deletion check",
            "Prefer replacement, combination, or compression before appending",
            "Figure or table caption",
            "Do not repeat a full set of effect sizes, confidence intervals, and P values",
            "paragraph necessity test",
            "Do not explain an explanation in the main text",
            "Build a claim-location map",
            "Word-count delta",
        ):
            self.assertIn(requirement, contract)

    def test_contract_preserves_integrity_and_required_reporting(self) -> None:
        contract = squash(read(CONTRACT))

        for safeguard in (
            "Do not use compression to hide inconvenient evidence",
            "Never select only the most favorable statistic",
            "Do not bury contradictory or conclusion-changing evidence in SI",
            "Do not remove statistics required by the target journal",
            "research integrity",
        ):
            self.assertIn(safeguard, contract)

    def test_writing_and_polishing_routes_apply_the_contract(self) -> None:
        files = (
            "skills/nature-writing/SKILL.md",
            "skills/nature-writing/manifest.yaml",
            "skills/nature-writing/static/core/workflow.md",
            "skills/nature-writing/static/fragments/section/experiments.md",
            "skills/nature-polishing/SKILL.md",
            "skills/nature-polishing/manifest.yaml",
            "skills/nature-polishing/static/core/failure-modes.md",
            "skills/nature-polishing/static/fragments/section/results.md",
        )

        for relative in files:
            self.assertIn("main-text-discipline.md", read(relative), relative)

        self.assertIn("version: 1.5.0", read("skills/nature-writing/manifest.yaml"))
        self.assertIn("version: 6.6.0", read("skills/nature-polishing/manifest.yaml"))

    def test_response_route_prevents_reviewer_driven_main_text_bloat(self) -> None:
        files = (
            "skills/nature-response/SKILL.md",
            "skills/nature-response/manifest.yaml",
            "skills/nature-response/static/core/workflow.md",
        )

        for relative in files:
            self.assertIn("main-text-discipline.md", read(relative), relative)

        stance = squash(read("skills/nature-response/static/core/stance.md"))
        self.assertIn("response letter complete but the manuscript change minimal", stance)
        self.assertIn("pre-emptive reviewer response", stance)
        self.assertIn("version: 1.7.0", read("skills/nature-response/manifest.yaml"))
        self.assertIn(
            "Main-text discipline audit",
            read("skills/nature-response/static/core/workflow.md"),
        )

    def test_shared_registry_docs_and_output_contracts_are_complete(self) -> None:
        shared_manifest = read("skills/nature-shared/manifest.yaml")
        self.assertIn("version: 1.6.0", shared_manifest)
        self.assertIn("core/main-text-discipline.md", shared_manifest)

        for relative in (
            "skills/nature-shared/README.md",
            "skills/nature-shared/README_EN.md",
            "skills/nature-writing/README.md",
            "skills/nature-writing/README_EN.md",
            "skills/nature-polishing/README.md",
            "skills/nature-polishing/README_EN.md",
            "skills/nature-response/README.md",
            "skills/nature-response/README_EN.md",
        ):
            text = read(relative)
            self.assertTrue(
                "main-text-discipline.md" in text
                or "主文" in text
                or "main text" in text,
                relative,
            )

        for relative in (
            "skills/nature-writing/static/core/output-format.md",
            "skills/nature-polishing/static/core/output-format.md",
        ):
            output = read(relative)
            self.assertIn("Main-text discipline audit", output)
            self.assertIn("before/after word count", output)


if __name__ == "__main__":
    unittest.main()
