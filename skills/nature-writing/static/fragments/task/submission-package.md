# Initial submission package

Use this task only before the first editorial decision. Read `references/submission-package.md` for the full intake contract, templates, and readiness checklist.

## Core workflow

1. Identify the target journal, article type, manuscript title, corresponding author, and requested deliverables.
2. Check the journal's current author instructions when exact requirements matter. Treat journal-specific instructions as authoritative.
3. Record the submission stage. Do not apply accepted-in-principle production
   rules as initial-submission blockers.
4. For the flagship journal Nature, load
   `../../../../nature-shared/journal-formats/nature.md`; load the conditional
   research-compliance reference when its applicability gate is triggered.
   For Nature Machine Intelligence, load
   `../../../../nature-shared/journal-formats/nature-machine-intelligence.md`
   and treat the cover letter, availability statements and central-code review
   access as initial-package checks.
5. Build a deliverable matrix: required, optional, not applicable, or author input needed.
6. Draft only from author-supplied facts. Never invent author identities, affiliations, ORCIDs, funding numbers, ethics approvals, repository links, accession numbers, conflicts, reviewer identities, or permissions.
7. Keep the initial cover letter concise and editor-facing: what the study shows, what is new, why it fits the journal/readership, and any required declarations.
8. Keep each declaration internally consistent with the manuscript and title page.
9. Return a readiness state: `ready`, `ready_with_author_checks`, or `blocked`.

## Default deliverables

- Initial-submission cover letter when required or useful. For the flagship
  journal Nature it is optional and must not be treated as a blocker.
- Title-page metadata checklist or draft.
- Three to five highlights when the journal accepts them.
- CRediT-style author-contribution statement.
- Data and code availability statements.
- Competing-interests, funding, acknowledgements, and ethics statements.
- Suggested/opposed reviewer table when requested.
- Related-manuscript, preprint, originality, permissions, and reporting-checklist prompts.
- Submission completeness matrix.
- Stage-specific file preflight: initial submission versus revision versus
  accepted-in-principle production files.
- Filled LaTeX deliverables from `templates/submission/` when the user requests `.tex` files.

Graphical abstracts and TOC graphics belong to `nature-figure`. Revision cover letters and rebuttals belong to `nature-response`.
