---
name: nature-reviewer
description: >-
  Simulate a Nature-style reviewer assessment from the referee perspective rather than
  an author rebuttal. Use when the user wants a pre-submission review, reviewer report,
  peer-review style critique, novelty/significance/technical soundness assessment,
  reviewer-style manuscript evaluation, 审稿人视角评估, 预审稿意见, or Nature reviewer
  report. Return 3 reviewer reports plus a cross-review synthesis, grounded only in the
  local Nature reviewer source basis.
  Also trigger on general pre-submission review requests during academic writing even without the
  word "Nature", such as getting a mock peer review for any journal, critiquing a draft as a
  reviewer would, assessing novelty/rigor before submission, and Chinese phrasings like
  审稿人视角、模拟审稿、预审、帮我审一下论文、投稿前自审、审稿意见模拟、找论文问题.
version: 0.1.0
status: Draft
---

# Nature Reviewer Assessment Skill

Use this skill to simulate a `Nature`-style reviewer assessment package from the referee
side.

This skill is for reviewer-style manuscript evaluation, not for drafting the authors'
response. If the user wants rebuttal writing, route to `nature-response`.

## Default stance

- Ground the review only in the local source basis plus manuscript facts supplied by the user.
- Evaluate the manuscript against source-grounded axes: `originality`, `scientific importance`, `interdisciplinary readership`, `technical soundness`, and `readability for nonspecialists`.
- Return exactly `3 reviewer reports + 1 cross-review synthesis` unless the user explicitly asks for another structure.
- The three reviewers may differ only in `emphasis`; do not invent reviewer identities, specialties, institutions, or biographies.
- Identify who would be interested in the results and why.
- Identify technical failings that must be addressed before the authors' case is established.
- Distinguish clearly between what is supported, what is weak, and what is not assessable from the provided material.
- Do not claim the editor's final decision or certainty about fit to `Nature`.

## Accepted inputs

The skill may receive:

- full manuscript draft
- abstract, summary paragraph, or cover-summary style text
- introduction, results, discussion, or methods excerpts
- figure legends, selected figures, or result notes
- author notes in Chinese or English describing the claimed contribution
- pre-submission positioning notes

If the provided material is partial, perform a bounded review and mark the assessment boundary explicitly.

## Workflow

1. Identify the input scope and whether the job is a reviewer-style assessment rather than rebuttal drafting.
2. Extract a shared manuscript fact base: main claim, visible evidence, claimed significance, likely readership, and visible limitations.
3. Check readiness and label missing evidence or missing sections instead of inventing them.
4. Assess the manuscript using the source-grounded axes.
5. Generate `Reviewer 1`, `Reviewer 2`, and `Reviewer 3` using shared facts but different emphasis.
6. Generate a `Cross-review synthesis` that captures consensus and weighting differences.
7. Run QA for groundedness, coverage, role boundaries, and non-invention.

## Output format

Unless the user asks for another format, return:

```text
Review setup
- Input scope:
- Assessment boundary:
- Shared manuscript claim summary:
- Visible evidence base:
- Missing materials affecting confidence:

Reviewer 1
- Overall assessment:
- Who would be interested in the results, and why:
- Major strengths:
- Major concerns:
- Technical failings that need to be addressed before the case is established:
- Assessment against Nature-style criteria:
- Recommendation posture:

Reviewer 2
[Same structure]

Reviewer 3
[Same structure]

Cross-review synthesis
- Consensus strengths:
- Consensus technical risks:
- Where emphasis differs across reviewers:
- Broad-interest / significance readout:
- Most important issues to resolve before a strong Nature-style case is established:

Risk / unsupported claims
- [specific unsupported or not-assessable items]
```

## Red lines

- Do not invent reviewer identities, specialty roles, or selection history.
- Do not invent experiments, validations, controls, citations, figure details, line numbers, or prior-work distinctions not present in the input.
- Do not silently turn reviewer assessment into author rebuttal drafting.
- Do not present the review as an editorial decision letter.
- Do not state that the manuscript belongs in `Nature` as a settled fact.
- Do not omit technical failings when the provided evidence does not establish the authors' case.

## Related files

| File | Open when |
|---|---|
| [references/source-basis.md](references/source-basis.md) | You need source provenance, local rule summaries, or source-vs-implementation boundaries |
| [references/reviewer-workflow.md](references/reviewer-workflow.md) | You need the invocation order, fact-base extraction flow, or synthesis rules |
| [references/review-axes.md](references/review-axes.md) | You need the evaluation axes or reviewer weighting logic |
| [references/report-structure.md](references/report-structure.md) | You need the default output contract or section anatomy |
| [references/role-boundaries.md](references/role-boundaries.md) | You need constraints on reviewer differences and editor-versus-reviewer boundaries |
| [references/qa-checklist.md](references/qa-checklist.md) | You are finalizing an output and need groundedness / non-invention checks |
| [references/editorial criteria and processes.md](references/editorial criteria and processes.md) | You need the primary local Nature source text |

## Source hierarchy

Use sources in this order:

1. `references/editorial criteria and processes.md`
2. manuscript facts supplied by the user
3. conservative local implementation rules documented in `references/source-basis.md`

If a user asks for policy-level certainty beyond this local source, state the limit instead of improvising broader journal policy.
