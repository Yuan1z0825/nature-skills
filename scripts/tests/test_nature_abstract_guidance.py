from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GUIDANCE = "skills/nature-shared/core/nature-abstract.md"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def squash(text: str) -> str:
    return " ".join(text.split())


class NatureAbstractGuidanceTests(unittest.TestCase):
    def test_guidance_is_corpus_derived_not_official_policy(self) -> None:
        guidance = squash(read(GUIDANCE))

        self.assertIn(
            "corpus-derived writing guidance, not official journal requirements",
            guidance,
        )
        self.assertIn("Current target-journal instructions", guidance)

    def test_guidance_centres_the_discovery_evidence_chain(self) -> None:
        guidance = squash(read(GUIDANCE))

        for requirement in (
            "shortest evidence chain",
            "compressed Introduction",
            "Use a discovery-centred architecture",
            "Choose one central claim",
            "one or two critical supporting findings or boundaries",
            "The abstract is not a Methods summary",
            "Experimental scale is a credibility cue, not the protagonist",
        ):
            self.assertIn(requirement, guidance)

    def test_numeric_and_payoff_rules_are_selective(self) -> None:
        guidance = squash(read(GUIDANCE))

        for requirement in (
            "Use numbers by necessity",
            "do not require a numeric result merely to appear empirical",
            "defines the strength or threshold of the main discovery",
            "End with the conceptual payoff",
            "Do not end with",
            "Run the Nature abstract audit",
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
            self.assertIn("nature-abstract.md", read(relative), relative)

    def test_section_fragments_do_not_require_decorative_numbers(self) -> None:
        files = (
            "skills/nature-writing/static/fragments/section/abstract.md",
            "skills/nature-polishing/static/fragments/section/abstract.md",
        )
        combined = squash("\n".join(read(relative) for relative in files))

        for requirement in (
            "shortest evidence chain",
            "one main claim",
            "number is optional",
            "numeric reporting is not mandatory",
        ):
            self.assertIn(requirement, combined)


if __name__ == "__main__":
    unittest.main()
