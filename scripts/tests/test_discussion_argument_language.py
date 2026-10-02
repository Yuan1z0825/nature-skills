from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GUIDANCE = "skills/nature-shared/core/discussion-argument-language.md"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def squash(text: str) -> str:
    return " ".join(text.split())


class DiscussionArgumentLanguageTests(unittest.TestCase):
    def test_reference_is_source_informed_but_not_official_policy(self) -> None:
        guidance = squash(read(GUIDANCE))

        self.assertIn(
            "writing guidance, not an official Nature Portfolio requirement",
            guidance,
        )
        self.assertIn("mp.weixin.qq.com/s/exPlMmjkrDPchE6dCfjINw", guidance)
        self.assertIn("selective, accuracy-checked synthesis", guidance)

    def test_discussion_functions_are_flexible_and_operational(self) -> None:
        guidance = squash(read(GUIDANCE))

        for requirement in (
            "Use the reverse funnel as a direction, not a template",
            "Treat the following as functions, not four mandatory paragraphs",
            "Anchor",
            "Position",
            "Interpret and contribute",
            "Bound and extend",
            "central finding anchor -> cross-Results synthesis",
            "Delete a Discussion sentence when it only repeats",
        ):
            self.assertIn(requirement, guidance)

    def test_modal_ladder_preserves_evidence_boundaries(self) -> None:
        guidance = squash(read(GUIDANCE))

        for safeguard in (
            "Choose the strongest wording the evidence justifies",
            "Supported but not uniquely established",
            "Plausible interpretation or extrapolation",
            "Near-necessity or exclusion",
            "Do not teach spaced `can not` as a routine hedge",
            "Avoid hedge stacking",
            "specific design feature that licenses that strength",
        ):
            self.assertIn(safeguard, guidance)

    def test_limitations_and_future_work_are_claim_specific(self) -> None:
        guidance = squash(read(GUIDANCE))

        for requirement in (
            "claim affected -> untested or constrained condition",
            "what remains supported",
            "the open question",
            "the discriminating experiment, dataset, comparison, or analysis",
            "Label each Discussion sentence with one primary function",
            "Future-work necessity",
        ):
            self.assertIn(requirement, guidance)

    def test_writing_and_polishing_route_to_the_shared_reference(self) -> None:
        routes = (
            "skills/nature-shared/SKILL.md",
            "skills/nature-shared/manifest.yaml",
            "skills/nature-writing/SKILL.md",
            "skills/nature-writing/manifest.yaml",
            "skills/nature-writing/static/fragments/section/discussion.md",
            "skills/nature-polishing/SKILL.md",
            "skills/nature-polishing/manifest.yaml",
            "skills/nature-polishing/static/fragments/section/discussion.md",
        )

        for relative in routes:
            self.assertIn("discussion-argument-language.md", read(relative), relative)

        self.assertIn("version: 1.6.0", read("skills/nature-shared/manifest.yaml"))
        self.assertIn("version: 1.5.0", read("skills/nature-writing/manifest.yaml"))
        self.assertIn("version: 6.6.0", read("skills/nature-polishing/manifest.yaml"))


if __name__ == "__main__":
    unittest.main()
