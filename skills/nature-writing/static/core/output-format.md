# Output format (writing)

Default output:

1. `Draft:` — the requested prose.
2. `Section outline:` — `3-7` compact bullets when the task involves a full section.
3. `Assumptions or missing inputs:` — only material issues; do not pad with style nits.
4. `Claim-evidence map:` — for major claims, in the form:
   `Claim: ... | Evidence: ... | Status: supported / needs evidence / inferred`
5. `Why this structure:` — `2-4` short bullets on the structural choices made.
6. `To redirect me:` — one line inviting targeted feedback, e.g. "Name the paragraph or claim that is off and I will revise only that, keeping the rest." This sets up the targeted revision loop (workflow step 9) instead of a full rewrite.

For Chinese-author notes, provide polished English first, then brief Chinese notes explaining major structural choices.

For a Results or full-main-text restructuring task, also include a compact
`Main-text discipline audit:` after the prose:

- result allocation: core / necessary support / qualification / SI-bound detail
- relocated, replaced, compressed, or deleted material
- primary statistic retained in the main text and secondary analyses routed to SI
- before/after word count for each revised subsection

Return the full allocation and claim-repetition tables only when the manuscript
is being comprehensively restructured or the user asks for the audit trail.

If essential evidence or boundary is missing, do not invent. Write a placeholder such as `[Evidence needed: comparator group accuracy on test set X]` and list it under `Assumptions or missing inputs:`.

For `task=submission-package`, replace the default manuscript format with:

1. `Submission readiness:`
2. `Deliverable matrix:`
3. `Draft materials:`
4. `AUTHOR_INPUT_NEEDED:`
5. `Cross-file consistency checks:`
6. `Next actions:`
