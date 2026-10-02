# Initial submission package

Use this reference for first-submission materials before peer review. Journal instructions override these defaults.

## Contents

1. Intake and routing
2. Deliverable matrix
3. Initial cover letter
4. Title page
5. Highlights and editorial summary
6. Declarations
7. Reviewer suggestions
8. Completeness audit
9. LaTeX templates
10. Output format

## 1. Intake and routing

Collect or mark as missing:

- Target journal, article type, submission stage, manuscript title, short title,
  abstract, and keywords.
- Author names, order, affiliations, corresponding-author details, email, and ORCID.
- One-sentence claim, strongest evidence, novelty boundary, significance, and journal fit.
- Funding identifiers, acknowledgements, conflicts, ethics approvals, consent, and permissions.
- Data/code repository links, accession numbers, license, embargo, and access conditions.
- Preprint, conference version, related manuscripts, prior submission, or concurrent-submission facts.
- Suggested/opposed reviewers with affiliation, email, expertise, relationship/conflict check, and rationale.
- Journal-specific items such as highlights, graphical abstract, reporting summary, checklist, or author declaration.

Do not infer unknown administrative facts. Use `[AUTHOR_INPUT_NEEDED: ...]`.

## 2. Deliverable matrix

Return a compact table:

| Item | Status | Source or missing input | Draft/output |
|---|---|---|---|
| Main manuscript | required / optional / N/A | path or note | filename/status |
| Anonymous manuscript | required / optional / N/A | journal rule | filename/status |
| Title page | required / optional / N/A | author metadata | draft/status |
| Cover letter | required / optional / N/A | claim + fit | draft/status |
| Highlights | required / optional / N/A | key findings | draft/status |
| Graphical abstract | required / optional / N/A | route to nature-figure | status |
| Supplementary information | required / optional / N/A | supplied files | status |
| Reporting checklist | required / optional / N/A | study design | status |
| Declarations | required / optional / N/A | author facts | draft/status |
| Reviewer suggestions | required / optional / N/A | author candidates | draft/status |

## 3. Initial cover letter

This is not a revision cover letter.

Recommended anatomy:

```text
Dear [Editor name / Editors],

Please consider our manuscript, "[Title]," for publication as a [Article type] in [Journal].

[What the study addresses and the principal finding, in 1-2 sentences.]
[What is specifically new and which evidence supports it, in 1-2 sentences.]
[Why the result matters to this journal's readership, in 1 sentence.]

[Required declarations: originality, author approval, related manuscripts/preprint, conflicts, or other journal-specific statements.]

Thank you for your consideration.

Sincerely,
[Corresponding author]
[Affiliation and contact details]
```

Rules:

- First classify the cover letter as required, optional, or not accepted. Do not
  infer that every journal requires one.
- Usually 250-400 words unless the journal specifies otherwise.
- Do not repeat the abstract.
- Do not use unsupported priority claims such as "the first" or "unprecedented".
- Do not name-drop editors, reviewers, or famous researchers as persuasion.
- Do not claim journal fit without connecting the finding to the journal's scope and readers.

## 4. Title page

Draft or audit:

- Full title and short/running title.
- Author names in final order.
- Affiliation mapping and present addresses.
- Corresponding author(s), email, postal address when required, and ORCID.
- Equal-contribution and senior-author notes.
- Word count, figure/table count, keywords, and article type when required.
- Funding, acknowledgements, conflicts, data/code availability, ethics, consent, and author contributions when the journal places them on the title page.

For double-anonymous review, keep identifying details out of the anonymous manuscript.

## 5. Highlights and editorial summary

Highlights:

- Three to five bullets.
- One finding per bullet.
- Prefer concrete results over generic importance claims.
- Respect the journal's character limit.

Editorial summary or significance statement:

- Problem and audience.
- Main advance.
- Why the evidence changes understanding or practice.
- Scope and limitation.

## 6. Declarations

Prepare separate, fact-grounded blocks as applicable:

- CRediT author contributions.
- Competing interests.
- Funding.
- Acknowledgements.
- Data availability.
- Code availability.
- Ethics approval and consent to participate.
- Consent for publication.
- Materials availability.
- Preprint and related-manuscript disclosure.
- Originality and all-author approval.
- Third-party permissions.
- AI/LLM use disclosure when required by the journal and applicable to the work.

Never convert "available on request" into a public repository claim. Never invent contribution roles, grant numbers, approval IDs, accession numbers, or licenses.

## 7. Reviewer suggestions

When requested, return:

| Name | Institution | Email | Expertise fit | Conflict check | Rationale |
|---|---|---|---|---|---|

Require the author to confirm:

- No recent coauthorship, same institution, close collaboration, supervisory relationship, personal conflict, or other journal-defined conflict.
- Institutional email and current affiliation are accurate.
- The candidate has topic/method expertise relevant to the manuscript.

For opposed reviewers, give a short factual reason without attacking competence or character.

## 8. Completeness audit

Check:

- Journal instructions and article type are confirmed.
- All author names, order, affiliations, and corresponding-author details match every file.
- Title, abstract, keywords, declarations, repository links, and manuscript metadata are consistent.
- Anonymous and identified files are separated correctly.
- Figures, tables, supplements, permissions, and checklists are present and cited.
- Initial-submission and accepted-in-principle requirements have not been
  conflated.
- Data/code statements point to real destinations and access conditions.
- Cover letter matches the manuscript's actual claims and does not overstate novelty.
- Suggested reviewers pass conflict checks.
- Required placeholders are resolved.
- Related manuscripts that the journal requires for assessment are attached as
  clearly marked separate files, not only named in the cover letter.

Readiness:

- `ready`: all required facts and files are present and cross-checked.
- `ready_with_author_checks`: drafts are complete but administrative facts need confirmation.
- `blocked`: required ethics, authorship, permissions, integrity, or journal-rule information is missing.

## 9. LaTeX templates

Use these only for initial submission:

| Template | Purpose |
|---|---|
| `templates/submission/initial-cover-letter.tex` | Initial editor-facing cover letter |
| `templates/submission/title-page.tex` | Identified title page and declarations |
| `templates/submission/highlights-and-summary.tex` | Highlights and editorial/significance summary |
| `templates/submission/declarations-and-reviewers.tex` | Submission declarations and reviewer suggestions |

When producing LaTeX:

- Copy only the requested templates into the user's delivery folder.
- Replace placeholders only with author-confirmed facts.
- Keep unresolved facts visibly marked as `AUTHOR_INPUT_NEEDED`.
- Check journal instructions before deciding which declarations belong on the title page or in separate files.
- Compile when a LaTeX engine is available and report any missing package or compilation error.
- Never reuse `nature-response/templates/cover-letter.tex`; that template is explicitly for a revised manuscript.

## 10. Output format

Return:

1. `Submission readiness:`
2. `Deliverable matrix:`
3. `Draft materials:` with clear headings for each requested item.
4. `AUTHOR_INPUT_NEEDED:` as a consolidated checklist.
5. `Cross-file consistency checks:`
6. `Next actions:` ordered by blocking priority.
