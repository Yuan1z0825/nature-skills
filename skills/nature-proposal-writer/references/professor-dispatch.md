# Professor dispatch

`professor` is a dynamic specialist generator, not a fixed expert pool. Select reviewers from the current failure mode instead of reusing a generic panel.

## Contents

- [Dispatch contract](#dispatch-contract)
- [Expert count](#expert-count)
- [Selection and permanence rules](#selection-and-permanence-rules)
- [Example 1: Focused claim review](#example-1-focused-claim-review)
- [Example 2: Foundation review](#example-2-foundation-review)
- [Example 3: Language-only work](#example-3-language-only-work)
- [Example 4: Full-proposal QA](#example-4-full-proposal-qa)

## Dispatch contract

Provide:

```text
task_context
current_mode
text_type
research_domain
current_failure_mode
needed_review_depth
canon/evidence/draft summary
```

Request:

```text
selected_experts
expert_reviews
conflict_summary
recommendation
permanence_candidate
```

Every expert review must distinguish:

- evidence-backed findings;
- plausible but unverified interpretations;
- missing information that requires author input;
- recommendations that would change scope or scientific commitments.

## Expert count

- Default: 1-2 specialists.
- Complex proposal: 2-4 specialists.
- Final review or major direction decision: up to 5 specialists.
- More than 5 requires an explicit rationale.

When independent review capability is available, run non-overlapping specialists in parallel. Otherwise, perform clearly separated expert passes and preserve each pass in the QA log.

## Selection and permanence rules

Select specialist classes that map directly to the failure mode. Examples include a domain-mechanism expert, methods expert, statistics expert, feasibility reviewer, doctoral-proposal reviewer, academic-style reviewer, adversarial reviewer, or supervisor-perspective reviewer.

Do not request a broad domain expert when the failure is narrow. A vague mechanistic claim needs a mechanism specialist; an overloaded work plan needs a feasibility reviewer.

If the same specialist class is invoked at least three times, or the user explicitly asks to retain it, propose creating a reusable long-term reviewer. Do not create one without approval.

## Example 1: Focused claim review

**Context**: Revise mode identified a mechanism claim that uses “may affect” without specifying a plausible pathway or the evidence supporting it.

**Dispatch input**:

```text
task_context: "Revising the background section of a materials proposal."
current_mode: revise
text_type: doctoral_proposal
research_domain: high-temperature materials chemistry
current_failure_mode: >
  The draft says additive A may change degradation pathways, but it does not
  identify a reaction, phase, transport process, or supporting source.
needed_review_depth: medium
canon/evidence/draft summary:
  - Study 1 reports a change in product phase under condition X.
  - Study 2 reports suppression of a precursor reaction under condition Y.
  - Neither study directly measures the proposed pathway under the target condition.
```

**Expected response**:

```text
selected_experts:
  - reaction-mechanism specialist
  - evidence-calibration reviewer
expert_reviews: [specific assessment from each reviewer]
conflict_summary: [agreement or the exact disputed point]
recommendation:
  - retain claims directly supported by the cited studies
  - label the target-condition pathway as a hypothesis
  - state which measurement would discriminate competing explanations
permanence_candidate: none
```

## Example 2: Foundation review

**Context**: Compose mode has produced the canon, evidence table, and argument map. Review is required before section contracts.

```text
task_context: "Review foundation files for Part 1 of a materials-science project."
current_mode: compose
text_type: doctoral_proposal_foundation
research_domain: materials processing and durability
current_failure_mode: >
  The argument map may overemphasize a performance benefit while treating a
  route-limiting compatibility constraint as a secondary issue.
needed_review_depth: medium
canon/evidence/draft summary:
  - 7 literature facts
  - 2 supervisor constraints
  - 12 claim-evidence mappings
  - 1 central question, 3 supporting arguments, 1 counterargument
```

Select a proposal-structure reviewer and a domain feasibility expert. Ask whether the central tension is evidence-backed, whether the question can be answered by the proposed methods, and whether any supporting argument must be downgraded before drafting.

## Example 3: Language-only work

If the user explicitly requests language-only review and the diagnosis finds no content-level risk, skip professor dispatch. Load `references/research-anti-slop.md`, run the language scan, and produce a focused revision brief. Do not manufacture a scientific review stage when it cannot change the result.

## Example 4: Full-proposal QA

For a completed proposal, separate technical and argument reviews:

```text
Specialist A: domain methods and feasibility
  focus: scientific assumptions, controls, operating window, failure criteria,
         reproducibility, evidence gaps, and fallback routes

Specialist B: proposal structure and doctoral fit
  focus: argument chain, testable objectives, workload, risk boundaries,
         concrete novelty, section integrity, and language quality

Both receive:
  - scope and task brief
  - research canon and evidence table
  - complete draft
  - section contracts

Both return:
  - P0/P1/P2 findings with locations
  - dimension scores with reasons
  - the single most consequential revision
```

Reconcile the reviews explicitly. If they conflict, identify whether the disagreement comes from evidence interpretation, feasibility assumptions, or scope. The author or a qualified domain owner retains final scientific judgment.
