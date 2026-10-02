# nature-response test rubric

Use this rubric to manually evaluate `nature-response` outputs against the Markdown fixtures.

## Decision routing

Pass when:

- The decision type is extracted from an explicit editor letter or user statement.
- When it remains unclear, the skill asks before decision-dependent package strategy or complete-package drafting, while continuing independent inspection.
- Local wording edits, audits of existing replies, and comment-level triage proceed without requiring a decision label or expanding into a full package.
- Major Revision receives an evidence-first, potentially structural work plan.
- Minor Revision receives a bounded correction plan without downgrading any genuinely major or blocking concern.

Fail when:

- The skill guesses the decision type from reviewer tone, comment count, or apparent workload.
- It blocks a local edit solely because Major/Minor Revision status is unknown.
- It drafts the same undifferentiated strategy for Major and Minor Revision.
- It treats the Minor Revision label as permission to minimize an evidence, statistics, ethics, or integrity concern.

## Completeness

Pass when:

- Every reviewer comment receives a stable ID.
- Every master ID maps to the correct reviewer-specific response and local comment number.
- Repeated concerns are answered fully in every relevant reviewer-specific file rather than cross-referenced across reviewers.
- Ambiguous reviewer boundaries are flagged.

Fail when:

- A comment is skipped.
- Two concerns are merged without traceability.
- A major concern receives only a polite acknowledgement.

## Reviewer isolation

Pass when:

- The internal/editor master is clearly marked as not reviewer-facing.
- Each reviewer-facing file contains only one reviewer's comments and corresponding responses.
- Repeated concerns receive a complete standalone answer in each relevant file.
- Conflicting requests are coordinated only in the master and explained independently to each reviewer.
- All reviewer-specific files remain consistent with the same manuscript revision.

Fail when:

- A reviewer-facing response mentions another reviewer, another reviewer ID, or another recommendation.
- The response says "see our response to Reviewer 2" or uses an equivalent cross-reviewer reference.
- One reviewer is told that another reviewer requested an incompatible change.
- The master tracker is presented as if it were safe to send to every reviewer.

## Traceability

Pass when:

- Every claimed manuscript change has a section, page, line, figure, table, supplement, or explicit placeholder.
- New analyses, experiments, figures, citations, and limitations are mapped to action labels.
- Missing locations are flagged rather than invented.

Fail when:

- The response claims a change without location or evidence.
- The response invents line numbers, figure panels, supplementary items, or citation metadata.

## Factuality

Pass when:

- Missing evidence is marked `AUTHOR_INPUT_NEEDED`.
- Quantitative details are used only when supplied by the author.
- Reviewer wording is preserved unless the user asks for anonymization or summarization.

Fail when:

- The response invents data, p-values, confidence intervals, sample sizes, accession details, reviewer identities, or editor instructions.
- The response overstates unsupported causal or clinical claims.

## Tone

Pass when:

- The response is cooperative, concise, and evidence-forward.
- Disagreement is respectful and scientifically justified.
- Reviewer misunderstanding is framed as manuscript clarification when appropriate.
- A reviewer who missed existing material receives a direct answer, a clearer manuscript presentation, and a final location or visible placeholder.

Fail when:

- The response accuses the reviewer of error, incompetence, or misunderstanding.
- The response says "we already stated this", "as clearly described in the manuscript", or otherwise implies that the reviewer failed to read carefully.
- The response is excessively apologetic, defensive, or repetitive.
- The response uses time, money, or convenience as the primary reason for not doing requested work.

## Actionability

Pass when:

- The author can see what to change in the manuscript.
- Missing information is listed as concrete author questions.
- Blocking or high-risk issues are visible before the draft letter.
- If manuscript text is edited, changes are shown in red on a backed-up/copy version of the original manuscript.
- If revised manuscript text is pasted after a response, that excerpt is italic.
- LaTeX or print-oriented output uses one separate response file per mutually blind reviewer unless explicit journal instructions require a combined file.
- Every tracker row distinguishes proposed action from work status.
- Required input, expected output, and finalization-blocking state are explicit.
- `VERIFIED_DONE` rows identify the supplied artifact used for verification.

Fail when:

- The output only produces prose and no action checklist.
- The author cannot identify what evidence is still needed.
- The output overwrites the clean manuscript without a marked backup/copy.
- The response letter pastes revised manuscript text as plain non-italic body text.
- Multiple mutually blind reviewer reports are combined in one outward-facing LaTeX or print file without an explicit journal requirement.
- An author-reported but uninspected change is labelled `VERIFIED_DONE`.
- Package readiness is `ready_to_submit` while a blocking, unverified, or `TODO_*` item remains.

## Nature-fit

Pass when:

- The output is organized as editor-readable point-by-point response material.
- All referee criticisms are seriously addressed, justified, or flagged.
- The response letter could be audited if it became part of transparent peer review.

Fail when:

- The output reads like generic language polishing.
- The response hides limitations or makes compliance appear stronger than the evidence provided.
