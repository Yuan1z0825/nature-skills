from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GUIDANCE = "skills/nature-shared/core/nature-results-discussion.md"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def squash(text: str) -> str:
    return " ".join(text.split())


class NatureResultsDiscussionGuidanceTests(unittest.TestCase):
    def test_guidance_is_corpus_derived_not_official_policy(self) -> None:
        guidance = squash(read(GUIDANCE))

        self.assertIn(
            "corpus-derived writing guidance, not official journal requirements",
            guidance,
        )
        self.assertIn("Current target-journal instructions", guidance)
        self.assertIn("corpus variation", guidance)

    def test_results_claim_escalation_and_local_interpretation_are_operational(self) -> None:
        guidance = squash(read(GUIDANCE))

        for requirement in (
            "establish and advance the paper's scientific claims",
            "observation -> unresolved question -> targeted experiment",
            "phenomenon -> source -> necessary condition or mechanism",
            "association -> targeted disruption -> predicted degradation",
            "Apply the local-interpretation gate",
            "rules out a central alternative",
            "reassurance that the same conclusion survives",
        ):
            self.assertIn(requirement, guidance)

    def test_mixed_nature_corpus_supports_evidence_chain_archetypes(self) -> None:
        guidance = squash(read(GUIDANCE))

        for requirement in (
            "author-supplied NMI reading set",
            "flagship Nature papers",
            "Discovery loop",
            "Core capability and validation envelope",
            "Capability ladder",
            "establish the phenomenon -> stress-test it -> rule out alternatives",
            "necessary comparators",
            "content versus correct correspondence",
            "If two adjacent subsections can both be summarized as `X helps`",
        ):
            self.assertIn(requirement, guidance)

    def test_discussion_synthesizes_without_redemonstrating(self) -> None:
        guidance = squash(read(GUIDANCE))

        for requirement in (
            "Write Discussion as synthesis, not re-demonstration",
            "necessary recap / anchor",
            "redundant re-demonstration",
            "Scientific question",
            "New claim",
            "Inference gain",
            "Evidence-chain role",
            "Open by redefining the paper's central discovery",
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
            self.assertIn("nature-results-discussion.md", read(relative), relative)

    def test_routes_cover_all_nature_portfolio_targets(self) -> None:
        manifests = (
            "skills/nature-shared/manifest.yaml",
            "skills/nature-writing/manifest.yaml",
            "skills/nature-polishing/manifest.yaml",
        )

        for relative in manifests:
            route = squash(read(relative))
            for target in (
                "flagship Nature",
                "Nature Communications",
                "Nature Machine Intelligence",
                "another Nature Portfolio title",
            ):
                self.assertIn(target, route, relative)

    def test_old_facts_only_split_is_not_enforced(self) -> None:
        files = (
            "skills/nature-writing/static/fragments/section/experiments.md",
            "skills/nature-writing/static/fragments/section/discussion.md",
            "skills/nature-polishing/static/fragments/section/results.md",
            "skills/nature-polishing/static/fragments/section/discussion.md",
        )

        combined = squash("\n".join(read(relative) for relative in files))
        self.assertNotIn("Results = what we observed", combined)
        self.assertNotIn("Results should answer what happened", combined)
        self.assertIn("evidence chain that establishes and advances", combined)
        self.assertIn("synthesizes across", combined)


if __name__ == "__main__":
    unittest.main()
