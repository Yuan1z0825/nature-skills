# `nature-academic-search` Skill

[中文说明](README.md)

## What It Does

- Coordinates multi-source academic search, citation verification, strict external-citation audits, influential-citer profiling, and reference-management exports.
- It is the right entry point when a task needs evidence from scholarly databases rather than a single ad hoc search.

## When to Use It

- Search papers across multiple sources for a topic, DOI, author, or manuscript claim.
- Verify bibliographic metadata or DOI accuracy.
- Build a table of a paper's title, publication date, authors, affiliations, citation count, strict external-citation count, and DOI.
- Check whether major scholars, academy members, presidents, deans, distinguished young scholars, Changjiang Scholars, or Fellows have cited a paper, and summarize how they cited it.

## Copy-Paste Prompts

- `Search recent high-impact papers about chloride-induced corrosion prediction and return a ranked table.`
- `Verify this reference list and flag fabricated authors, wrong years, page mismatches, and DOI conflicts.`
- `Create a table for this paper with title, publication date, authors, affiliations, citation count, strict external-citation count, and DOI.`
- `Check whether influential scholars or Fellows cited this paper, and summarize the citing context.`

## Required Inputs

- Research topic, paper title, DOI, author name, reference list, or manuscript passage.
- Optional source preferences such as PubMed, CrossRef, arXiv, Scopus, ScienceDirect, or publisher pages.
- Optional definition of self-citation or strict external citation for the target field.

## Expected Outputs

- Ranked search tables with source links and metadata.
- Reference-verification reports and corrected citation candidates.
- Strict external-citation audit tables.
- Influential-citer profiles with cited-context summaries and uncertainty notes.
- BibTeX, RIS, NBIB, or other reference-manager-ready exports when supported by the workflow.

## Dependencies / API Keys / Local Environment

- Some providers require local credentials or API access.
- PubMed workflows require a configured `PUBMED_EMAIL`.
- Scopus, ScienceDirect, and other optional providers require credentials configured outside the repository.
- Never commit API keys or provider credentials to the repository.

## FAQ

- **Can it guarantee exact citation counts?** No. Citation counts differ by database and update time; the report should name the source and timestamp when counts matter.
- **What is strict external citation?** It excludes citations by overlapping authors or institutions according to the task's stated rule, then reports the rule used.
- **Can it identify influential citers automatically?** It can profile candidates from affiliation, title, honors, and public scholarly signals, but uncertain cases should be marked rather than overstated.

## Related Skills

- [`nature-citation`](../nature-citation/README_EN.md)
- [`nature-ref-verifier`](../nature-ref-verifier/README_EN.md)
- [`nature-reader`](../nature-reader/README_EN.md)
