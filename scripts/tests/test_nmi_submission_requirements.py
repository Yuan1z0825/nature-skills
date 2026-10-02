from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = "skills/nature-shared/journal-formats/nature-machine-intelligence.md"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def squash(text: str) -> str:
    return " ".join(text.split())


class NatureMachineIntelligenceSubmissionRequirementsTests(unittest.TestCase):
    def test_shared_contract_is_stage_aware_and_source_dated(self) -> None:
        rules = read(CONTRACT)

        for stage in (
            "initial_submission",
            "revision",
            "accepted_in_principle",
            "proof",
        ):
            self.assertIn(stage, rules)
        self.assertIn("Current pages verified **2026-08-14**", rules)

        for url in (
            "https://www.nature.com/natmachintell/submission-guidelines",
            "https://www.nature.com/natmachintell/content",
            "https://www.nature.com/natmachintell/editorial-policies/reporting-standards",
            "https://www.nature.com/natmachintell/editorial-policies/preprints-conference-proceedings",
            "https://www.nature.com/documents/natmachintell-brief-submission-guide.pdf",
        ):
            self.assertIn(url, rules)

    def test_article_and_analysis_limits_are_exact(self) -> None:
        rules = read(CONTRACT)

        for requirement in (
            "up to **3,500 words**",
            "up to **150 words**, unreferenced",
            "**100–150 words**, unreferenced",
            "up to **6** figures and tables combined",
            "typically up to **50**",
        ):
            self.assertIn(requirement, rules)

        self.assertIn("Introduction, without an `Introduction` heading", rules)
        self.assertIn("Discussion should not", rules)

    def test_initial_package_and_content_type_contract_are_present(self) -> None:
        rules = read(CONTRACT)

        for requirement in (
            "PDF",
            "Microsoft Word",
            "TeX/LaTeX",
            "a **cover letter**",
            "**3,000–4,000 words**",
            "**500–1,000 words**",
            "**1,500–2,000 words**",
            "Reusability Report",
            "does **not** consider presubmission enquiries",
        ):
            self.assertIn(requirement, rules)

    def test_display_data_code_and_overlap_gates_are_present(self) -> None:
        rules = read(CONTRACT)
        normalized = squash(rules)

        for requirement in (
            "no more than **10** Extended Data",
            "after Data Availability and before the references",
            "Software Submission Checklist",
            "available to editors and reviewers",
            "**substantially extends**",
            "300 dpi",
            "180 mm",
            "5–7 pt sans-serif",
        ):
            self.assertIn(requirement, normalized)

    def test_current_limits_and_historical_legend_advisory_are_separate(self) -> None:
        rules = read(CONTRACT)
        normalized = squash(rules)

        self.assertIn("do not publish", rules)
        self.assertIn("a fixed title character or word limit", rules)
        self.assertIn("a separate numeric Methods word limit", rules)
        self.assertIn("a current separate numeric per-figure-legend word limit", rules)
        for requirement in (
            "historical advisory ceiling",
            "below **300 English words**",
            "**150–250 English words**",
            "one whole-figure legend",
            "300 words is not a per-panel allowance",
            "revised 9 July 2018",
        ):
            self.assertIn(requirement, normalized)

    def test_legend_guardrail_reaches_figure_and_text_routes(self) -> None:
        routes = (
            "skills/nature-figure/SKILL.md",
            "skills/nature-figure/references/figure-legend-conventions.md",
            "skills/nature-writing/static/fragments/journal/nat-mach-intell.md",
            "skills/nature-polishing/static/fragments/journal/nat-mach-intell.md",
        )

        for route in routes:
            text = squash(read(route))
            self.assertIn("2018", text)
            self.assertIn("300", text)
            self.assertIn("150–250", text)
            self.assertIn("panel", text)

    def test_writing_and_polishing_have_distinct_nmi_routes(self) -> None:
        writing = read("skills/nature-writing/manifest.yaml")
        polishing = read("skills/nature-polishing/manifest.yaml")

        for manifest in (writing, polishing):
            self.assertIn("nat-mach-intell:", manifest)
            self.assertIn("nature-machine-intelligence.md", manifest)

        self.assertIn("Nature Machine Intelligence or NMI", squash(writing))
        self.assertIn("Nature Machine Intelligence or NMI", squash(polishing))

    def test_cross_skill_routes_and_bilingual_docs_are_complete(self) -> None:
        skill_roots = (
            "nature-writing",
            "nature-polishing",
            "nature-figure",
            "nature-data",
            "nature-statistics",
        )

        for skill in skill_roots:
            manifest = read(f"skills/{skill}/manifest.yaml")
            skill_router = read(f"skills/{skill}/SKILL.md")
            readme_zh = read(f"skills/{skill}/README.md")
            readme_en = read(f"skills/{skill}/README_EN.md")

            self.assertIn("nature-machine-intelligence.md", manifest)
            self.assertIn("nature-machine-intelligence.md", skill_router)
            self.assertIn("Nature Machine Intelligence", readme_zh)
            self.assertIn("Nature Machine Intelligence", readme_en)

        shared = read("skills/nature-shared/manifest.yaml")
        self.assertIn("journal-formats/nature-machine-intelligence.md", shared)

    def test_fragment_relative_paths_resolve(self) -> None:
        routes = (
            (
                "skills/nature-writing/static/fragments/journal/nat-mach-intell.md",
                "../../../../nature-shared/journal-formats/nature-machine-intelligence.md",
            ),
            (
                "skills/nature-writing/static/fragments/task/submission-package.md",
                "../../../../nature-shared/journal-formats/nature-machine-intelligence.md",
            ),
            (
                "skills/nature-polishing/static/fragments/journal/nat-mach-intell.md",
                "../../../../nature-shared/journal-formats/nature-machine-intelligence.md",
            ),
        )

        for source, target in routes:
            resolved = ((ROOT / source).parent / target).resolve()
            self.assertTrue(resolved.is_file(), f"missing routed reference: {resolved}")


if __name__ == "__main__":
    unittest.main()
