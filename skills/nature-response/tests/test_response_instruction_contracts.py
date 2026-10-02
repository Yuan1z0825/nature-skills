from pathlib import Path


ROOT = Path(__file__).parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_decision_type_gate_is_part_of_the_runtime_contract() -> None:
    router = read("SKILL.md")
    workflow = read("static/core/workflow.md")

    assert "Major Revision" in router and "Minor Revision" in router
    assert "pause and ask the user" in workflow
    assert "do not draft a generic response" in workflow


def test_reviewer_isolation_is_required_in_core_and_qa() -> None:
    stance = read("static/core/stance.md")
    qa = read("references/qa-checklist.md")

    assert "mutually blind by default" in stance
    assert "must not reveal another reviewer's" in stance
    assert "Each reviewer-facing file contains only one reviewer's comments" in qa
    assert "complete standalone answer" in qa


def test_missed_existing_text_is_treated_as_a_clarity_problem() -> None:
    stance = read("static/core/stance.md")
    qa = read("references/qa-checklist.md")

    assert "not sufficiently visible or clear" in stance
    assert 'No response says "we already stated this"' in qa


def test_punctuation_guard_is_present_in_core_and_qa() -> None:
    stance = read("static/core/stance.md")
    qa = read("references/qa-checklist.md")

    assert "Avoid em dashes, en dashes, and colons" in stance
    assert "No avoidable em dash, en dash, or colon" in qa
