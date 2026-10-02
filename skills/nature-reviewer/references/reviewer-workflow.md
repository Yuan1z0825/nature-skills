# Reviewer workflow

## Contents

- [Default execution order](#default-execution-order)
- [Input handling](#input-handling)
- [Immutable review-packet checklist](#immutable-review-packet-checklist)
- [Concern-ledger fields](#concern-ledger-fields)
- [Forensic consistency audit](#forensic-consistency-audit)
- [Cross-review generation rule](#cross-review-generation-rule)
- [Failure-safe behaviour](#failure-safe-behaviour)


## Default execution order

1. Identify the input package.
   - Determine whether the user supplied a full manuscript, abstract-only draft, selected sections, figures, notes, or a pre-submission concept summary.
2. Build an immutable review packet.
   - Include the supplied manuscript/source, verified source anchors, assessment boundary, and common journal criteria.
   - Do not include suspected concerns, a shared interpretation, another report, or a draft synthesis.
3. Define all reviewer emphasis briefs before review begins.
   - Keep the source packet and report skeleton identical; vary only the declared emphasis.
4. Generate each reviewer report in an isolated context.
   - Give the reviewer only the immutable packet, common rules, report skeleton, and its own emphasis brief.
   - Within that context, independently extract the central claim, key evidence, stated significance, implied audience, visible limitations, and missing material.
   - Independently apply `originality`, `scientific importance`, `interdisciplinary interest`, `technical soundness`, and `readability for nonspecialists`.
5. Build one private concern ledger per reviewer.
   - Load `technical-concern-taxonomy.md` and mark each axis `applicable`, `not applicable`, or `not assessable` without access to any other reviewer's ledger.
   - Give every supported concern a reviewer-local issue key, `major` or `minor` severity, a blocking flag for Major Concerns, severity rationale, `claim_pointer`, `evidence_pointer`, and resolution test.
   - Keep the ledger private to that reviewer; expose only the fields needed to make emitted concerns traceable.
6. Freeze all reviewer reports.
   - Do not let reviewers read, cite, agree with, answer, or anticipate one another.
   - Do not redistribute, add, remove, or rephrase concerns after comparison merely to change overlap.
   - Render separate `Major Concerns` and `Minor Comments` sections. If a tier has no grounded item, write `None identified from the supplied material` rather than filling a quota.
7. Run the forensic consistency audit in a separate editorial pass after all reports are frozen.
   - Use `forensic-consistency-audit.md` to test arithmetic, metric bounds, aggregation level, prose-table ordering, duplicated displays, dispersion anomalies, provenance, leakage, and reproducibility gates.
   - Classify every result as confirmed internal error, aggregation ambiguity, provenance gap, suspected duplication, unresolved input needed, not assessable, or passed.
   - Do not feed audit findings into reviewer contexts or edit frozen reports after comparison.
8. Generate a post-review synthesis in a separate context.
   - Summarize consensus blocking concerns, other major concerns, forensic consistency findings, the minor-revision checklist, points of emphasis divergence, and the most decision-relevant technical and significance risks.
   - Reconcile reviewer-local issue keys only now. Treat an issue as consensus only when at least two frozen reports independently raise the same underlying concern.
   - Keep audit findings separate from reviewer consensus.
9. Run final QA.
   - Check context isolation, locked-report status, evidence anchors, post hoc overlap mapping, groundedness, consistency, coverage, non-invention, and forensic consistency.

## Input handling

- Acceptable inputs include:
  - manuscript draft
  - abstract or summary paragraph
  - introduction, results, discussion, or methods excerpts
  - figure legends or selected figures
  - author notes describing the claimed contribution
- If the input is thin, the skill should still provide a bounded review, but it must clearly state the assessment boundary.

## Immutable review-packet checklist

- Put only these common inputs into every isolated reviewer context:
  - supplied manuscript/source material
  - verified section, figure, table, equation, page, or block anchors
  - assessment boundary and missing-file inventory
  - common journal criteria and report skeleton
  - that reviewer's preassigned emphasis brief
- Do not put these into the shared packet:
  - extracted concerns or visible technical gaps
  - a shared claim-evidence interpretation
  - another reviewer report or ledger
  - overlap targets, consensus labels, or synthesis notes

## Concern-ledger fields

Use this internal shape before drafting reviewer prose:

```yaml
issue_key: experimental-design-control-selection
axis: experimental-design
applicability: applicable
severity: major
blocking: yes
severity_rationale: The missing control prevents the supplied comparison from isolating the central treatment effect.
claim_pointer: The treatment effect is attributed to the intervention.
evidence_pointer: Results, "Primary outcome"; Figure 2
evidence_status: located
concern: The supplied comparison does not isolate the intervention effect.
resolution_test: Show an appropriate control or narrow the causal claim.
reviewer_id: Reviewer 1
```

- Use section headings and supplied figure/table identifiers before page or line numbers.
- Use `location not provided` or `not assessable from supplied material` when an exact pointer cannot be verified.
- Never infer an absent figure, analysis, control, or manuscript location.
- Use `blocking: yes` only for a grounded Major Concern that prevents the current manuscript from
  establishing its central case. Minor Comments always use `blocking: no` internally and do not
  need to display the field in the final report.

## Forensic consistency audit

Run this audit only after every reviewer report is frozen. It is a deterministic editorial pass, not a fourth review and not a consensus ledger.

Required checks:

- Arithmetic, subgroup totals, percentages, deltas, ranges, and precision consistency.
- Metric bounds and identities under the stated aggregation level.
- Macro, micro, tile, region, event, cluster, and paired-unit definitions.
- Prose claims against table and figure ordering or values.
- Duplicate rows, identical intervals, or suspiciously repeated outputs.
- Dispersion anomalies and influential groups.
- Training, validation, test, continuation, placebo, support, query, and exclusion provenance.
- Spatial, temporal, hierarchical, or subject leakage.
- Reproduction of existing headline numbers before interpreting new experiments.

Record each finding with `audit_id`, status, location, claim pointer, evidence pointer, check, result, impact, resolution test, and reviewer overlap. Classify status exactly as one of:

- `confirmed_internal_error`
- `aggregation_ambiguity`
- `provenance_gap`
- `suspected_duplication`
- `unresolved_input_needed`
- `not_assessable`
- `passed`

Confirmed or unresolved central findings belong in the synthesis and `Risk / unsupported claims`. Do not call them reviewer consensus unless at least two frozen reports independently raised the same underlying concern.

## Cross-review generation rule

- Run synthesis only after all individual reports are final and locked.
- Treat the synthesis as editor/author-facing; never send it back into any reviewer context.
- The cross-review synthesis should consolidate, not average away, reviewer differences.
- A consensus item must map post hoc to equivalent concerns raised by at least two reviewer reports.
- Preserve consequential single-reviewer concerns under weighting differences; do not drop them merely because they lack consensus.
- It must separate:
  - shared strengths
  - consensus blocking concerns
  - other shared major concerns
  - minor revision checklist
  - differences in significance weighting
  - differences in readership/readability judgment

## Failure-safe behaviour

- If isolated contexts are unavailable, produce one reviewer report per invocation or disclose that mutual blindness cannot be guaranteed. Do not silently simulate independence inside a shared drafting context.
- When evidence is absent, say the case is not yet established from the supplied material.
- When significance is unclear, distinguish `potentially interesting` from `demonstrated broad importance`.
- When readability is weak, describe the barrier to nonspecialist comprehension instead of rewriting the manuscript unless asked.
