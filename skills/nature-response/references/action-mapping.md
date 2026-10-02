# Action mapping

## Contents

- [Action labels](#action-labels)
- [Internal tracker fields](#internal-tracker-fields)
- [Work status](#work-status)
- [Task-control fields](#task-control-fields)
- [Readiness state](#readiness-state)
- [Risk level](#risk-level)
- [Mapping rules](#mapping-rules)


Use this file to map every reviewer concern to a concrete response action.

## Action labels

| Action label | Meaning | Use when |
|---|---|---|
| `ACCEPT_TEXT` | Revised wording, structure, title, abstract, Methods detail, Discussion, or legend | The author supplied or can supply a text change |
| `ACCEPT_ANALYSIS` | Added or revised analysis | The response depends on real analysis output |
| `ACCEPT_EXPERIMENT` | Added experimental data | The author performed a real experiment and supplied enough detail |
| `ACCEPT_FIGURE` | Added or modified figure, table, panel, legend, or supplement | A visual or tabular item addresses the concern |
| `CLARIFY_EXISTING` | Existing data already address the concern, but manuscript presentation needed clarification | The evidence exists and location can be cited |
| `ADD_CITATION` | Added verified citation | The citation is genuinely relevant and metadata is supplied or flagged |
| `SOFTEN_CLAIM` | Reduced claim strength or added boundary | The original claim was too broad, causal, novel, clinical, or mechanistic |
| `PARTIAL` | Partly addressed with explicit remaining limitation | A valid concern cannot be fully resolved in the revision |
| `DISAGREE` | Respectfully disagree with evidence or scope-based reasoning | The reviewer interpretation is not supported by the manuscript facts |
| `OUT_OF_SCOPE` | Valid suggestion but outside current manuscript scope | The request requires a new cohort, system, longitudinal design, or different study |
| `AUTHOR_INPUT_NEEDED` | Cannot draft final answer without real details | The author note is vague, missing, or unsupported |
| `BLOCKING` | Revision cannot be credible until author action occurs | Missing ethics, compliance, central evidence, integrity explanation, or required data |

## Internal tracker fields

Use this shape internally when organizing a response:

```yaml
comment_id: R1.3
reviewer: Reviewer 1
severity: major
category: methodological
action: ACCEPT_ANALYSIS
work_status: TODO_ANALYSIS
required_input: Analysis specification and result output
expected_output: Updated Results text and Supplementary Table S2
verification_evidence: null
blocks_finalization: true
package_readiness: needs_author_input
risk_level: high
manuscript_location: Methods; Results; Supplementary Fig. S2
```

Keep these dimensions separate:

- `action`: the scientific or editorial response approach;
- `work_status`: how far the concrete task has progressed and whether completion is verified;
- `package_readiness`: whether the complete response package can be submitted safely.

The IDs in this tracker belong to the internal/editor master. In each reviewer-facing response,
map only that reviewer's IDs to neutral local labels such as `Comment 1`. Never expose another
reviewer's IDs in the outward-facing file.

## Work status

| Status | Meaning | Minimum evidence |
|---|---|---|
| `VERIFIED_DONE` | The requested change or justified response is complete and independently traceable | Supplied revised text, analysis output, figure/table, repository record, approval, or other inspectable artifact |
| `REPORTED_DONE_UNVERIFIED` | The author reports completion, but the revised artifact was not supplied or cannot be matched | Explicit author statement only |
| `TODO_TEXT` | Manuscript or response wording still needs to be written or revised | Clear target section and requested change |
| `TODO_ANALYSIS` | A computational, statistical, or data-analysis task remains | Analysis specification and required inputs |
| `TODO_EXPERIMENT` | Experimental, clinical, field, or validation work remains | Study task and required design details |
| `TODO_AUTHOR_CONFIRM` | The proposed action requires an author decision or missing factual confirmation | A concrete author question |
| `NOT_FEASIBLE` | The requested work cannot reasonably be completed within the study design or revision | Scientific, ethical, scope, or data-based rationale plus an alternative response |
| `PROPOSED_DISAGREEMENT` | A disagreement is recommended but not yet approved and evidenced | Draft reasoning, supporting evidence, and author confirmation request |

Status rules:

- A drafted reply is not proof that the manuscript was changed.
- Use `VERIFIED_DONE` only after matching the claimed action to an inspectable artifact and record it in `verification_evidence`.
- Use `REPORTED_DONE_UNVERIFIED` when the author explicitly says the work was completed but does not supply the revised artifact.
- `NOT_FEASIBLE` is not automatically submission-ready; the response still needs a defensible rationale, an appropriate limitation or claim adjustment, and author approval.
- After the author approves an evidence-backed disagreement, record the response action as `DISAGREE`; use `VERIFIED_DONE` only when the final response and any manuscript clarification are inspectable.

## Task-control fields

- `required_input`: the next concrete fact, file, decision, or result needed; use `None` only when genuinely complete.
- `expected_output`: the artifact that will demonstrate completion, such as revised Methods text, a robustness-analysis table, a new figure panel, or a finalized disagreement paragraph.
- `verification_evidence`: the supplied location or artifact used to justify `VERIFIED_DONE`.
- `blocks_finalization`: `true` when the unresolved item prevents a credible final response or submission-ready package.

## Readiness state

| State | Meaning |
|---|---|
| `ready_to_submit` | No item blocks finalization, every claimed completed change is verified, and no unresolved placeholder remains |
| `draft_with_placeholders` | Draft can proceed, but placeholders must remain visible |
| `needs_author_input` | Do not draft final wording until author supplies facts |
| `blocked` | Revision response would be misleading or non-credible without author action |

Derive package readiness conservatively:

- Use `ready_to_submit` only when no item blocks finalization, no unresolved placeholder remains, and every claimed completed change is `VERIFIED_DONE`.
- Use `draft_with_placeholders` when usable prose exists but one or more non-final artifacts or locations remain unresolved.
- Use `needs_author_input` when at least one item is `TODO_AUTHOR_CONFIRM`, `REPORTED_DONE_UNVERIFIED`, or otherwise depends on missing facts.
- Use `blocked` when a central-evidence, integrity, ethics, compliance, or essential revision task prevents credible finalization.

## Risk level

| Risk | Use when |
|---|---|
| `low` | Wording, format, or straightforward clarification |
| `medium` | Citation, figure, method detail, or presentation issue requiring verification |
| `high` | Evidence, statistics, validation, claim strength, or out-of-scope request |
| `blocking` | Ethics, compliance, data integrity, missing central evidence, or unsupported response |

## Mapping rules

- If the author says only "we revised it", use `AUTHOR_INPUT_NEEDED` until the location and nature of the revision are known.
- If the author explicitly reports a completed change without providing the revised artifact, use `REPORTED_DONE_UNVERIFIED`, never `VERIFIED_DONE`.
- If the author says "we added an experiment", request experiment name, condition, sample size or replicate unit, result summary, and figure/table location.
- If the author says "we added a citation", request verified bibliographic detail unless already supplied.
- If a reviewer asks for impossible or out-of-scope work, use `PARTIAL` or `OUT_OF_SCOPE` plus claim softening or limitation.
- If a reviewer missed information already present in the manuscript, use `CLARIFY_EXISTING` with a small presentation improvement. Do not reply that the information was already stated or imply that the reviewer failed to read carefully.
- If a central claim remains unsupported, use `SOFTEN_CLAIM` or `BLOCKING`, not confident compliance language.
