from pathlib import Path


ROOT = Path(__file__).parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_severity_and_blocking_contract_is_present() -> None:
    router = read("SKILL.md")

    assert "Major Concerns" in router
    assert "Minor Comments" in router
    assert "Blocking Yes" in router
    assert "Minor Comments are never blocking" in router
    assert "Do not impose a concern quota" in router


def test_reviewers_are_isolated_before_synthesis() -> None:
    router = read("SKILL.md")

    assert "genuinely separate context" in router
    assert "Freeze each individual report before comparing" in router
    assert "not shown to reviewers" in router
    assert "Do not let one reviewer read" in router


def test_traceability_and_non_invention_are_required() -> None:
    router = read("SKILL.md")

    assert "claim_pointer" in router
    assert "evidence_pointer" in router
    assert "Do not invent experiments" in router


def test_punctuation_guard_is_part_of_the_reviewer_contract() -> None:
    router = read("SKILL.md")

    assert "Avoid em dashes, en dashes, and colons" in router
    assert "Do not use dash punctuation or colons" in router

def test_forensic_consistency_audit_is_required_after_freezing() -> None:
    router = read("SKILL.md")
    workflow = read("references/reviewer-workflow.md")
    qa = read("references/qa-checklist.md")
    audit = read("references/forensic-consistency-audit.md")

    assert "forensic consistency audit" in router
    assert "confirmed internal error" in router
    assert "Never feed audit findings back into reviewer contexts" in router
    assert "Run the forensic consistency audit in a separate editorial pass" in workflow
    assert "Forensic consistency checks" in qa
    assert "aggregation_ambiguity" in audit
    assert "provenance_gap" in audit
    assert "Existing code and artifacts must reproduce existing headline numbers" in audit
