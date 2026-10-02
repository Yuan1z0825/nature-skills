# `nature-response` Skill

[中文说明](README.md)

`nature-response` drafts, audits, and revises revision correspondence, including mutually isolated point-by-point reviewer responses, revision cover letters, red-marked manuscript excerpts, and editable LaTeX templates.

## What To Use It For

- Parse editor decision letters, revision emails, and reviewer reports.
- Confirm whether the decision is Major Revision or Minor Revision before applying the corresponding revision strategy.
- Split comments into stable IDs such as `E.1`, `R1.1`, and `R2.3`.
- Treat different reviewers as mutually blind by default. Keep a master tracker internally while giving each reviewer a standalone response that reveals no other reviewer's comments, IDs, recommendation, or response text.
- Answer repeated concerns fully for each reviewer. Reconcile conflicting requests only in the internal/editor master without telling one reviewer what another requested.
- Build response strategy, manuscript-change actions, and evidence needs for each comment.
- Track response action, task progress, and package readiness separately, with inspectable evidence for completed work.
- Draft formal, restrained, submission-ready English point-by-point responses and cover letters.
- Audit rebuttal drafts for missed replies, defensive tone, unsupported claims, and missing line numbers.
- When a reviewer misses material already present in the manuscript, treat it as a clarity problem and improve the presentation instead of replying that it was already stated.
- Answer the reviewer fully in the letter but keep manuscript changes to what readers need for the central inference; every new main-text sentence triggers a replacement, compression, deletion, or SI-relocation check to prevent revision accretion.
- Mechanically check LaTeX revision packages for quoted-text drift, comment-response count mismatches, and clean-versus-marked manuscript text drift.

## Typical Requests

- "Here is the editor email and reviewer comments; generate a point-by-point response framework."
- "Turn my Chinese revision notes into English reviewer responses."
- "Check whether this rebuttal misses anything, sounds too strong, or lacks evidence."

## What You Need To Provide

- Editor decision letter, reviewer comments, revision requirements, or existing rebuttal draft.
- If the decision letter does not state it, whether this is a Major Revision or Minor Revision.
- Completed or planned experiments, analyses, figures, line numbers, and manuscript-change locations.
- Target journal, manuscript ID, title, and required submission files.

## Outputs

- Response strategy summary.
- Separate point-by-point response letters for each reviewer, a revision cover letter, or a LaTeX response package.
- An author/editor master tracker clearly labelled as not reviewer-facing.
- Manuscript-change checklist, missing-information checklist, and risk notes.
- Per-item tracker with work status, required input, expected output, and finalization-blocking state.
- Optional red-marked manuscript excerpts; manuscript text must come from the author.
- A mechanical package-consistency report; compiled page locations, colors, citations, and references still require final PDF verification.

## Boundaries

- The skill does not invent experiments, analyses, line numbers, figures, statistical results, or editor requirements.
- It does not use cross-reviewer phrases such as "another reviewer also noted" or "see our response to Reviewer 2" in a reviewer-facing response.
- It does not rebuke reviewers with "we already stated this". It answers directly, clarifies the presentation, and identifies the revised location.
- It does not turn the main text into a pre-emptive reviewer response or keep appending non-central robustness and recursive reconciliation prose to Results.
- Information that needs author confirmation is marked in Chinese rather than written as fact.
- For pre-submission simulated review, use `nature-reviewer`.

## Related Skills

- `nature-reviewer`: simulate reviewer comments before submission.
- `nature-polishing`: polish reviewer-response and cover-letter English.
- `nature-statistics`: handle statistical reviewer comments.
- `nature-ref-verifier`: verify reference-error comments.
