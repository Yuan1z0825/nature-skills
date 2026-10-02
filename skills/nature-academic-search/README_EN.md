# `nature-academic-search` Skill

[中文说明](README.md)

`nature-academic-search` supports multi-source scholarly search, bibliographic metadata checks, citation formatting, strict external-citation audits, and influential-citer analysis.

## What To Use It For

- Search papers across CrossRef, PubMed, arXiv, Scopus, ScienceDirect, and related scholarly sources.
- Retrieve structured paper details by DOI, PMID, or arXiv ID.
- Generate Nature, APA, IEEE, Vancouver, and other citation styles.
- Build MeSH-assisted PubMed search strategies for biomedical topics.
- Audit strict external citations for a target paper while excluding self-citations, team citations, and obvious collaboration-network citations.
- Identify how academy members, Fellows, highly cited scholars, institutional leaders, or field experts cited a target paper.

## Typical Requests

- "Check the strict external citations for this paper and list influential citers."
- "Find 20 recent Nature/Science/Cell-related papers on this topic."
- "Convert these DOIs into Nature-style references and export RIS."
- "Add MeSH terms and synonyms to this PubMed query."

## What You Need To Provide

- Search topic, keywords, time range, journal scope, or target DOI.
- Whether Scopus / ScienceDirect or other locally configured sources may be used.
- The exclusion rule for strict external citations, such as whether to exclude same-institution, coauthor, or lab-network citations.

## Outputs

- Deduplicated paper table with title, authors, year, journal, DOI, and source.
- Formatted citation text or `.ris`, `.bib`, `.nbib`, `.enw` reference-management files.
- Strict external-citation table and citation-context summary.
- Search strategy, source notes, and records that could not be verified.

## Runtime and Dependencies

- PubMed search needs `PUBMED_EMAIL` or `mcp-server/config.toml`.
- Scopus / ScienceDirect depend on local `pybliometrics` configuration, normally read from `~/.config/pybliometrics.cfg`.
- Do not write Elsevier API keys into repository files; keep them in local secure configuration.

## Boundaries

- Secondary scholarly indexes are discovery aids; key fields should be verified through DOI records, PubMed, publisher pages, or authoritative databases.
- Strict external-citation analysis needs a clear exclusion rule; missing author or affiliation metadata is marked as uncertain.
- Restricted databases are not bypassed; the skill reports missing sources or asks for user login when needed.

## Related Skills

- `nature-citation`: match Nature/CNS/Cell supporting citations for manuscript claims.
- `nature-literature-pipeline`: turn one-off search into ongoing literature monitoring.
- `nature-ref-verifier`: verify reference-list metadata field by field.
