# QA checklist

## Reviewer-isolation checks

- Reviewer emphasis briefs were fixed before any report was generated.
- Each reviewer received only the immutable manuscript/source packet, common criteria, report skeleton, and its own emphasis brief.
- Each reviewer ran in a separate context, subagent, process, or invocation and received no other review, ledger, synthesis, consensus hint, or overlap target.
- Every individual report was finalized and locked before comparison began.
- No individual report cites, agrees with, answers, anticipates, or refers to another reviewer.
- Cross-review synthesis was generated afterward in a separate editor/author-facing pass and was not fed back to reviewers.
- If technical isolation was unavailable, the output explicitly says mutual blindness was not guaranteed or provides only one reviewer report for the invocation.

## Grounding checks

- Every substantive evaluation should be traceable to either:
  - `references/editorial criteria and processes.md`, or
  - manuscript facts explicitly supplied by the user.
- No reviewer persona detail should appear beyond allowed `emphasis` labels.
- No technical failing should be invented from domain habit alone when the supplied material does not show it.
- Every substantive concern has a stable concern ID, `claim_pointer`, and `evidence_pointer`.
- Page, line, figure, and table identifiers are supplied or directly verified; otherwise the pointer says `location not provided` or `not assessable from supplied material`.

## Technical coverage checks

- The internal 12-axis matrix was considered without being dumped into the final report.
- Each axis is marked internally as `applicable`, `not applicable`, or `not assessable`; absence of evidence is not silently treated as a defect.
- The technical taxonomy supplements the five source-grounded Nature axes and does not create policy claims or severity statistics.

## Forensic consistency checks

- Run the forensic audit only after reviewer reports are frozen.
- Confirm arithmetic identities, subgroup totals, percentages, deltas, ranges, and precision consistency.
- Confirm metric bounds after identifying the exact metric and aggregation level.
- Compare prose superlatives and rankings directly with table and figure values.
- Flag duplicate rows, identical intervals, or repeated outputs that require explanation.
- Check dispersion anomalies and influential groups without calling them errors before proof.
- Verify training, validation, test, continuation, placebo, support, query, and exclusion provenance.
- Check spatial, temporal, hierarchical, subject, or target leakage.
- Require existing headline numbers to reproduce before interpreting new experiments.
- Classify every audit result as `confirmed_internal_error`, `aggregation_ambiguity`, `provenance_gap`, `suspected_duplication`, `unresolved_input_needed`, `not_assessable`, or `passed`.
- Keep audit findings separate from reviewer consensus and add central findings to synthesis and risk.

## Severity and blocking checks

- Every emitted concern is classified as Major or Minor from its impact on the manuscript's case,
  not from tone, difficulty, cost, or a desired quota.
- Every Major Concern displays `Blocking Yes` or `Blocking No` and gives a rationale consistent
  with the concern and resolution test.
- `Blocking Yes` is used only when the current manuscript cannot establish its central case until
  the concern is resolved.
- No Minor Comment is blocking, and no core evidence, validity, ethics, or integrity problem is
  downgraded to Minor merely because it can be described briefly.
- Localized presentation, terminology, citation, and reporting issues remain Minor unless they
  materially affect inference or reproducibility.
- Empty tiers say `None identified from the supplied material`; concerns are never invented to fill
  Major/Minor sections or equalize reviewer counts.

## Coverage checks

- Confirm all three reviewer reports exist.
- Confirm all reviewers received the same source packet and criteria, with only their preassigned emphasis briefs differing; no invented identity or unequal evidence access explains their conclusions.
- Confirm each reviewer still addresses all core axes, even if briefly.
- Confirm each reviewer visibly contains both `Major Concerns` and `Minor Comments` sections.
- Confirm a `Cross-review synthesis (post-review; not shown to reviewers)` section exists.
- Confirm a `Risk / unsupported claims` section exists.

## Boundary checks

- Confirm the output stays in reviewer-assessment mode, not author-response mode.
- Confirm the output does not claim a final editorial decision.
- Confirm broad-interest judgment is expressed cautiously, because the source assigns that final judgment to editors.

## Style checks

- Reviewer reports and synthesis avoid em dashes, en dashes, and colons as routine prose punctuation when a sentence boundary, comma, semicolon, parentheses, or a short label followed by a new line would be clearer.
- Necessary hyphens in compound terms and stable IDs such as `R1-M1` remain intact.
- Source-faithful titles, quotations, formulas, identifiers, URLs, times, and required machine-readable syntax are not altered merely to remove punctuation.

## Non-invention checks

- No invented reviewer identity, specialty, institution, or selection history.
- No invented experiments, controls, analyses, line numbers, citations, prior-work details, or figure-specific content absent from the input.
- If evidence is partial, mark `AUTHOR_INPUT_NEEDED` or `Not assessable from provided material`.

## Consistency checks

- Verifiable manuscript facts should stay consistent across all three reviewers even though their analyses were independent.
- Divergence may reflect weighting or interpretation of the same evidence, not access to different or invented facts.
- Technical failings listed in the synthesis should match issues already raised in at least one individual report.
- Consensus issues were raised by at least two reviewer reports and map to the same underlying issue key.
- Consensus blocking and other consensus major concerns preserve the original severity and
  blocking status of the source concerns.
- The minor-revision checklist contains only supported Minor Comments and cross-references their IDs.
- Preserve important single-reviewer concerns as weighting differences instead of deleting them.

## Overlap checks

- Normalize concerns to synthesis keys only after all individual reports are frozen.
- Measure pairwise overlap descriptively as `shared synthesis keys / smaller report issue count` when useful.
- Do not revise, redistribute, suppress, or add concerns to hit an overlap target. High overlap can be legitimate independent consensus; low overlap can be legitimate difference in judgment.
- Deduplicate only inside the post-review synthesis and preserve links to the original reviewer-local concern IDs.

## Final release rule

- If the skill cannot produce a grounded three-reviewer package without major invention, it should return a bounded draft review with explicit missing-information flags rather than pretending certainty.
- If the skill cannot isolate reviewer contexts, it must not label a multi-reviewer package mutually blind; use separate invocations or state the technical limitation.
- Do not release the report when Major/Minor labels or Blocking flags conflict with their stated
  rationale, manuscript impact, or resolution test.
- Do not release habitual dash-heavy or colon-heavy prose without first rewriting it with clearer sentence structure.
- Do not release a report that omits a confirmed central arithmetic, bounds, aggregation, provenance, or reproduction contradiction found by the forensic audit.
- Do not report an audit anomaly as a confirmed error unless arithmetic proof or source data supports it.
