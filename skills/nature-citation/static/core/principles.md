# Core principles (citation)

Use this skill to turn manuscript text into a defensible citation export:

- segmented text with citation candidates for each segment
- a reference-manager import file in `.enw`, `.ris`, or Zotero `.rdf`
- conservative evidence notes explaining whether each candidate truly supports the segment

## Default scope

Interpret journal scope from the user's wording, but keep the filter strict:

- `Nature系列`: search Nature Portfolio first. Include `Nature`, `Nature [field]`, `Nature Communications`, `Communications [field]`, `Scientific Reports`, and `npj` journals.
- `CNS`: search `Cell`, `Nature`, and `Science` plus their major sister journals.
- `CNS及其子刊` or `CNS/sister journals`: search only accepted flagship and subjournal titles in Nature Portfolio, the AAAS Science family, and Cell Press.
- `只要Nature/Science/Cell正刊`: restrict to the flagship journals `Nature`, `Science`, and `Cell`.

Do not treat merely related journals as in-scope. A title is valid only if it is in the accepted publisher-family whitelist or clearly matches the official naming pattern for that family. If the user needs an exhaustive or submission-critical boundary, verify current official journal pages before finalizing because journal portfolios change. The exact boundary and official source notes are in `references/journal-scope.md`.

## Source hierarchy

Use sources in this order:

1. Structured bibliographic metadata: Crossref, PubMed/NCBI E-utilities, DOI metadata.
2. Publisher pages: `nature.com`, `science.org`, `cell.com`, and official journal pages.
3. Full text or abstract pages, if accessible.
4. Secondary databases such as Google Scholar, Semantic Scholar, Web of Science, or Scopus only as discovery aids, not as the sole support basis.

Prefer structured APIs for metadata and publisher pages for claim verification. If metadata and publisher page disagree, preserve the DOI and journal-page facts and flag the discrepancy.

## Search quality rules

- Prefer precision over volume. A useful answer is usually 3-8 candidates, not 50 loosely related papers.
- Use exact phrase searches only for distinctive terms; otherwise use concept terms and synonyms.
- Check journal identity. Many journals contain the word "nature" but are not Nature Portfolio journals.
- Treat citation count as a tie-breaker, not evidence of support.
- Capture retractions, corrections, and expressions of concern when visible in Crossref or publisher metadata.
- Date-sensitive topics require current searching and an explicit search date.
- For medical, clinical, or safety claims, search current literature and state that citations do not replace clinical guidance or systematic review.

## Source notes

This skill is based on public bibliographic APIs and official publisher/import documentation: Crossref REST API and filters, NCBI E-utilities, EndNote RIS import options, Nature Portfolio, AAAS Science journals, and Cell Press portfolio descriptions. Verify pages at use time when exact journal coverage or current import behavior matters.
