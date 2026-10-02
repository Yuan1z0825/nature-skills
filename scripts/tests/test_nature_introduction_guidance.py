from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GUIDANCE = "skills/nature-shared/core/nature-introduction.md"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def squash(text: str) -> str:
    return " ".join(text.split())


class NatureIntroductionGuidanceTests(unittest.TestCase):
    def test_guidance_is_corpus_derived_not_official_policy(self) -> None:
        guidance = squash(read(GUIDANCE))

        self.assertIn(
            "corpus-derived writing guidance, not official journal requirements",
            guidance,
        )
        self.assertIn("Current target-journal instructions", guidance)

    def test_guidance_builds_an_exact_question_funnel(self) -> None:
        guidance = squash(read(GUIDANCE))

        for requirement in (
            "Make the Introduction converge",
            "exact unknown",
            "It remains unclear whether, why, or under what conditions",
            "Do not define the gap as the absence of the author's method",
            "Organize citations by argumentative function",
            "Prefer a question about a phenomenon, condition, mechanism, or boundary",
            "Let the answer emerge late",
        ):
            self.assertIn(requirement, guidance)

    def test_guidance_aligns_introduction_results_and_discussion(self) -> None:
        guidance = squash(read(GUIDANCE))

        for requirement in (
            "End with a compact research route",
            "Align Introduction, Results, and Discussion",
            "establish why each central question must be asked",
            "answer the questions through an escalating evidence chain",
            "synthesize what those answers mean together",
            "Run the Nature Introduction audit",
            "Results answer",
        ):
            self.assertIn(requirement, guidance)

    def test_writing_and_polishing_routes_load_shared_guidance(self) -> None:
        routes = (
            "skills/nature-shared/SKILL.md",
            "skills/nature-shared/manifest.yaml",
            "skills/nature-writing/SKILL.md",
            "skills/nature-writing/manifest.yaml",
            "skills/nature-writing/static/fragments/journal/nat-mach-intell.md",
            "skills/nature-polishing/SKILL.md",
            "skills/nature-polishing/manifest.yaml",
            "skills/nature-polishing/static/fragments/journal/nat-mach-intell.md",
        )

        for relative in routes:
            self.assertIn("nature-introduction.md", read(relative), relative)

    def test_section_fragments_enforce_question_answer_alignment(self) -> None:
        files = (
            "skills/nature-writing/static/fragments/section/intro.md",
            "skills/nature-polishing/static/fragments/section/intro.md",
        )
        combined = squash("\n".join(read(relative) for relative in files))

        for requirement in (
            "exact unresolved gap",
            "known–unknown transition",
            "absence of the author's method",
            "question answered in Results",
        ):
            self.assertIn(requirement, combined)


if __name__ == "__main__":
    unittest.main()
