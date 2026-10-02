# QA checklist

## Contents

- [Completeness](#completeness)
- [Status calibration](#status-calibration)
- [Traceability](#traceability)
- [Revision formatting](#revision-formatting)
- [Reviewer isolation](#reviewer-isolation)
- [Factuality](#factuality)
- [Tone](#tone)
- [Actionability](#actionability)
- [Final output gate](#final-output-gate)
- [Readiness gate](#readiness-gate)


Use this checklist before finalizing a response package or when auditing an existing draft.

## Completeness

- Every reviewer comment has a stable ID.
- Every ID has a response or an explicit unresolved flag.
- No reviewer comment is paraphrased in a way that changes meaning.
- Repeated concerns are answered fully in every relevant reviewer-specific response rather than cross-referenced across reviewers.
- No major concern is answered only with thanks.
- Editor-specific instructions are addressed before reviewer comments when supplied.
- Every editor/reviewer item has an action, work status, required input, expected output, and finalization-blocking state.

## Status calibration

- `VERIFIED_DONE` is supported by an inspectable revised manuscript passage, result, figure/table, repository record, approval, or equivalent supplied artifact.
- An author statement without the corresponding artifact is `REPORTED_DONE_UNVERIFIED`.
- A drafted response paragraph alone never proves that a manuscript change, analysis, or experiment was completed.
- `NOT_FEASIBLE` includes a scientific, ethical, scope, or data-based rationale and an appropriate alternative such as claim moderation or a limitation.
- `PROPOSED_DISAGREEMENT` includes evidence and awaits author confirmation; it is not silently treated as an approved final response.
- Required inputs and expected outputs are concrete enough for the author to act on and verify.
- `Blocks finalization?` agrees with severity, missing evidence, and package readiness.

## Traceability

- Every claimed revision has a manuscript location or visible placeholder.
- Every new figure, table, panel, supplement, or citation is named only if supplied.
- Every new experiment or analysis has enough supplied description to be credible.
- Line numbers are not invented; use section names if line numbers are unavailable.
- Reviewer comments and response IDs match throughout tracker, letter, and checklist.

## Revision formatting

- If manuscript text is edited, the changed text is marked in red on a backed-up/copy version of the original manuscript, with a clean copy kept separate when needed.
- In LaTeX marked manuscripts, changed text uses `\revised{...}` or an equivalent visible red-text macro.
- If revised manuscript text is pasted into the response letter after the answer, that pasted text is italic.
- In LaTeX response letters, pasted revised manuscript excerpts use `\RevisedExcerpt{...}` or another visible italic excerpt style.
- One LaTeX or print-oriented response file is created per mutually blind reviewer unless explicit journal instructions require a combined file.
- Cover letters summarize the revision for the editor and do not replace the point-by-point response.

## Reviewer isolation

- The internal/editor master is clearly labelled as not reviewer-facing.
- Each reviewer-facing file contains only one reviewer's comments and the author responses to those comments.
- Reviewer-facing files use neutral local numbering such as `Comment 1` and contain no IDs belonging to another reviewer.
- No reviewer-facing text says "as another reviewer noted", "see our response to Reviewer 2", "the other reviewer requested", or equivalent wording.
- Repeated concerns receive a complete standalone answer in each relevant reviewer-specific file.
- Conflicting requests are reconciled in the internal/editor strategy, then explained independently to each reviewer without revealing the conflict or the other request.
- Reviewer recommendations, identities, and confidential remarks are never copied into another reviewer's response.
- All reviewer-specific responses describe manuscript changes consistently.
- Explicit journal or portal visibility instructions are followed and any forced combined-file constraint is flagged.

## Factuality

- No invented data.
- No invented p-values, confidence intervals, effect sizes, sample sizes, or replicate counts.
- No invented DOI, citation metadata, accession number, repository record, or figure panel.
- No invented reviewer identity or editor instruction.
- No unsupported claim that an experiment, analysis, or manuscript revision was performed.
- Unsupported claims are softened or flagged.

## Tone

- No avoidable em dash, en dash, or colon is used as a routine sentence connector. Source-faithful
  reviewer quotations and required identifiers or syntax are unchanged.
- No accusations of reviewer incompetence, bias, or misunderstanding unless the user is explicitly preparing an appeal and supplies evidence.
- No excessive apologies.
- No repetitive empty thanks.
- Disagreement is evidence-based and narrow.
- Study limitations are acknowledged cleanly.
- Time, money, convenience, or ability is not the primary stated reason for not doing requested work.
- A missed existing passage is treated as a clarity or visibility problem, not as a reviewer failure.
- No response says "we already stated this", "this was already explained", "as clearly described", or an equivalent rebuke.
- When existing material answers the concern, the response gives a direct answer, a supported clarification, and the final manuscript location or a visible placeholder.

## Actionability

- Missing author inputs are concrete.
- High-risk and blocking items appear before the final letter or in a visible risk section.
- The manuscript change checklist tells the author which section, figure, table, supplement, or claim needs attention.
- Partial responses state what was addressed and what remains unresolved.

## Final output gate

Before returning final text, ask:

- Can an editor verify every response against a manuscript change, supplied evidence, or explicit limitation?
- Would the response remain professional if included in a transparent peer review file?
- Are all placeholders visible enough that the author cannot accidentally submit fabricated compliance?
- Is the package readiness honestly labelled as `ready_to_submit`, `draft_with_placeholders`, `needs_author_input`, or `blocked`?
- If any item is `draft_with_placeholders`, `needs_author_input`, or `blocked`, the package must not be labelled `ready_to_submit`.
- Does every `VERIFIED_DONE` item cite its verification evidence?
- Has each reviewer-facing deliverable passed the isolation checks without relying on another reviewer's response?
- Does `ready_to_submit` have no blocking item, no unresolved placeholder, and no claimed change left at `REPORTED_DONE_UNVERIFIED` or `TODO_*`?

## Readiness gate

Use these labels consistently:

- `ready_to_submit`: all comments are answered, no item blocks finalization, every claimed completed change is verified against supplied evidence, and no placeholder remains.
- `draft_with_placeholders`: draft text exists, but visible placeholders or missing locations remain.
- `needs_author_input`: the author must provide facts before final response wording is credible.
- `blocked`: a compliance, integrity, central-evidence, or appeal-like issue prevents normal final response drafting.
