# Workflow and output format

## Accepted inputs

The skill may receive: pasted editorial decision or revision-invitation email; editor decision letter; reviewer comments; previous response draft; manuscript change notes; tracked-change summary; line or page numbers; figure, table, and supplement list; author notes in Chinese or English; journal name and article type; manuscript title; author list; manuscript ID; original manuscript text or LaTeX source; requested cover-letter or LaTeX output format; journal or portal instructions governing who can see each response file.

If reviewer boundaries or comment segmentation are ambiguous, flag the ambiguity instead of inventing reviewer structure.

## Decision-type gate and revision strategy

For normal revision-response work, determine the editorial decision before drafting the response
strategy or response prose:

1. Use an explicit label in the editor decision letter or revision invitation when supplied.
2. Normalize informal author wording such as `major review` and `minor review` to `Major Revision`
   and `Minor Revision` when the meaning is unambiguous.
3. If the decision remains unclear, ask one concise question in the user's language and pause:
   `这是 Major Revision（大修）还是 Minor Revision（小修）？如果决定信没有明确写，请把决定信发给我，我帮你判断。`
   English default: `Is this a Major Revision or a Minor Revision? If the decision letter does
   not state it clearly, please send it and I can help classify the decision.`
4. Do not infer the decision type from comment count, reviewer tone, requested workload, or the
   apparent severity of individual comments.

After the gate is resolved, use the corresponding default strategy:

| Decision type | Default revision strategy |
|---|---|
| `Major Revision` | Build an evidence-first work plan. Prioritize central-claim support, experiments or analyses, methods and statistics, validation, figures, limitations, and any structural rewriting. Treat unresolved central evidence or integrity/compliance items as finalization blockers. Responses should explain both the action and the evidence that resolves each concern. |
| `Minor Revision` | Use a bounded correction plan. Prioritize precise wording, definitions, citations, reporting details, figure/table presentation, and localized clarifications. Keep replies concise and avoid unnecessary redesign of the study or expansion of claims unless an editor or reviewer request genuinely requires it. |

The decision label sets the package-level posture, not the severity of every comment. A substantive
evidence, statistics, ethics, or data-integrity concern remains major or blocking even inside a
Minor Revision. Journal instructions and explicit editor directions override these defaults.

## Workflow

1. Identify task mode and input readiness: `draft`, `audit`, `revise`, `triage-only`, `cover-letter`, `revision-package`, `latex-template`, or `appeal-like`.
2. If the input is a pasted journal email, automatically extract manuscript title, manuscript ID, journal, decision type, editor instructions, reviewer-report boundaries, required revision files, deadline, reviewer-visibility rules, and portal-specific constraints before drafting.
3. Pass the decision-type gate. For normal revision modes, pause and ask the user when the decision remains unclear; do not draft a generic response that silently treats Major and Minor Revision as equivalent.
4. Select the decision-specific package strategy while preserving item-level severity.
5. Extract editor instructions first and assign IDs such as `E.1`, then split reviewer comments with IDs such as `R1.1`, `R1.2`, and `R2.1`.
6. Classify each item by category, severity, action label, work status, required input, expected output, finalization-blocking state, package readiness, and risk.
7. Create an internal/editor master strategy and tracker before drafting prose. It may record duplicates and conflicts across reviewers, but label it clearly as not reviewer-facing.
8. Treat reviewer reports as mutually blind by default. For each reviewer, draft a standalone privacy-filtered response containing only that reviewer's comments and the author responses to them. Use neutral local labels such as `Comment 1` in outward-facing files. Do not expose another reviewer's IDs, comments, recommendation, identity, response wording, or conflicting request.
9. When reviewers repeat the same concern, answer it fully in every relevant reviewer-specific file. When their requests conflict, reconcile the scientific and manuscript action in the master strategy, then explain the chosen revision independently to each reviewer using only that reviewer's concern and the manuscript evidence.
10. When a reviewer asks about material that already existed in the submitted manuscript, use `CLARIFY_EXISTING` and treat the missed point as a presentation problem. Answer directly, acknowledge that the original wording or placement did not make the point sufficiently clear, make or propose a small clarification, and cite the revised location. Do not say that the reviewer should have seen it or that it was already stated.
11. If explicit current journal or portal instructions require one combined response document, follow that submission requirement and flag its visibility implications. Otherwise default to an editor/internal master plus separate reviewer-specific files. Never silently treat the master tracker as reviewer-facing.
12. For `cover-letter` or `revision-package`, draft a concise editor-facing cover letter that summarizes revision scope and points to the point-by-point responses without duplicating them.
13. Map each claimed change to manuscript location, figure, table, supplement, citation, or explicit placeholder. For every main-text edit, load `../../../nature-shared/core/main-text-discipline.md`, classify the result or explanation, and decide whether it belongs in the main text, caption, Methods/source data, SI, or response letter. Answer the reviewer fully in the letter while keeping the manuscript change to the shortest reader-facing text that preserves the central inference. Every addition triggers a deletion check across the affected paragraph; prefer replacement or compression before appending.
14. If editing manuscript text, create or instruct use of a backed-up manuscript copy and mark changed text in red. For LaTeX, use `\revised{...}` from `templates/revised-manuscript-redline.tex`.
15. If pasting revised manuscript text after a response, format it in italics. For LaTeX response files, use `\RevisedExcerpt{...}` from `templates/response-to-reviewers.tex`.
16. If the user requests LaTeX, create one filled copy of `templates/response-to-reviewers.tex` per reviewer and use `templates/cover-letter.tex` and/or `templates/revised-manuscript-redline.tex` as needed. Preserve visible placeholders for missing facts.
17. Mark a claimed change `VERIFIED_DONE` only after matching it to supplied revised manuscript text, analysis output, figure/table content, or another inspectable artifact. Treat an unsupported author report as `REPORTED_DONE_UNVERIFIED`.
18. Flag missing author input rather than fabricating details.
19. Run QA for completeness, decision-strategy consistency, reviewer isolation, per-item status calibration, blocking-state consistency, traceability, factuality, tone, unresolved risk, red-marked changes, italic revised excerpts, and LaTeX placeholder visibility.
20. Derive package readiness from the item statuses and return one of: `ready_to_submit`, `draft_with_placeholders`, `needs_author_input`, or `blocked`.

## Output format

Unless the user asks for another format, return:

```text
Response strategy summary
- Decision type:
- Task mode:
- Overall posture:
- Major risks:
- Parsed email metadata:
- Suggested ordering:
- Package readiness:

Internal/editor master tracker (not reviewer-facing)
| ID | Reviewer concern | Type | Severity | Proposed action | Work status | Required input | Expected output | Blocks finalization? |
|---|---|---|---|---|---|---|---|---|

Reviewer-specific response files
- Reviewer 1: [standalone response containing Reviewer 1 comments only]
- Reviewer 2: [standalone response containing Reviewer 2 comments only]

Draft revision cover letter
[only when requested or when returning a revision package]

Marked manuscript changes
- [red-marked changed passages or path to marked backup copy]

LaTeX files
- cover letter: [path or template-filled text when requested]
- response to Reviewer 1: [path or template-filled text when requested]
- response to Reviewer 2: [path or template-filled text when requested]
- red-marked manuscript: [path or template-filled text when requested]

Manuscript change checklist
- [specific manuscript changes or placeholders]
- Main-text discipline audit: [result/explanation class; destination; appended,
  replaced, compressed, relocated, or deleted; before/after paragraph word count]

Missing information / risk flags
- [specific unresolved items or "None"]

中文核对
- [when the user writes in Chinese; otherwise omit unless useful]
```
