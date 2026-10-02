from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def squash(text: str) -> str:
    return " ".join(text.split())


class FlagshipNatureSubmissionRequirementsTests(unittest.TestCase):
    def test_cross_skill_reference_paths_resolve(self) -> None:
        routes = (
            (
                "skills/nature-writing/static/fragments/journal/nature.md",
                "../../../../nature-shared/journal-formats/nature.md",
            ),
            (
                "skills/nature-writing/static/fragments/task/submission-package.md",
                "../../../../nature-shared/journal-formats/nature.md",
            ),
            (
                "skills/nature-figure/references/nature-article-requirements.md",
                "../../nature-shared/core/research-compliance.md",
            ),
        )

        for source, target in routes:
            resolved = ((ROOT / source).parent / target).resolve()
            self.assertTrue(resolved.is_file(), f"missing routed reference: {resolved}")

    def test_flagship_and_family_routes_are_separate(self) -> None:
        manifest = read("skills/nature-writing/manifest.yaml")
        flagship = read("skills/nature-writing/static/fragments/journal/nature.md")
        family = read("skills/nature-writing/static/fragments/journal/nature-family.md")

        self.assertIn("nature-family:", manifest)
        self.assertIn("Journal: flagship Nature", flagship)
        self.assertIn("Do not import flagship Nature's", family)

    def test_shared_article_contract_is_stage_aware_and_contains_exact_limits(self) -> None:
        rules = read("skills/nature-shared/journal-formats/nature.md")

        for stage in ("initial_submission", "revision", "accepted_in_principle", "proof"):
            self.assertIn(stage, rules)
        for requirement in (
            "75 characters",
            "2,500 words",
            "4,300 words",
            "40 characters",
            "3,000 words",
            "up to 30 MB",
            "no more than ten",
            "below 250 words",
            "use double spacing",
            "640 × 480 pixels",
        ):
            self.assertIn(requirement, rules)

    def test_figure_legend_uses_flagship_limit_not_legacy_generic_limit(self) -> None:
        legend = read("skills/nature-figure/references/figure-legend-conventions.md")
        nature = read("skills/nature-figure/references/nature-article-requirements.md")

        self.assertNotIn("`<= 300`", legend)
        self.assertIn("below 250 words", legend)
        self.assertIn("below 250 words", nature)
        self.assertIn("Main-figure production files", nature)
        self.assertIn("Extended Data production files", nature)

    def test_nature_statistics_contract_contains_official_fields(self) -> None:
        rules = read("skills/nature-statistics/references/nature-article-requirements.md")

        for requirement in (
            "one-tailed or two-tailed",
            "exact `n` value",
            "non-significant P values",
            "F statistic and degrees of freedom",
            "t statistic and degrees of freedom",
            "number of times representative",
        ):
            self.assertIn(requirement, rules)

    def test_ai_gate_contains_authorship_disclosure_and_confidentiality(self) -> None:
        ethics = read("skills/nature-shared/core/ethics.md")

        self.assertIn("do not satisfy authorship criteria", ethics)
        self.assertIn("document LLM use in Methods", ethics)
        self.assertIn("unsecured or public AI system", ethics)
        self.assertIn("Amber", ethics)

    def test_conditional_compliance_contract_covers_major_routes(self) -> None:
        rules = read("skills/nature-shared/core/research-compliance.md")

        normalized = squash(rules)
        for requirement in (
            "ethics committee's name and reference number",
            "ARRIVE 2.0",
            "before enrolment of the first participant",
            "CONSORT 2025",
            "CheckCIF",
            "LSIDs from",
            "unprocessed original gel",
        ):
            self.assertIn(requirement, normalized)

    def test_data_contract_covers_review_access_and_separate_code_statement(self) -> None:
        rules = read("skills/nature-data/references/nature-article-requirements.md")

        self.assertIn("separate headed `Code Availability` statement", rules)
        self.assertIn("editors and referees on request", rules)
        self.assertIn("Mandatory and specialist deposition gate", rules)
        self.assertIn("Structure-data submission files", rules)


if __name__ == "__main__":
    unittest.main()
