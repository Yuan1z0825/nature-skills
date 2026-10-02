# `nature-ref-verifier` Skill

[中文说明](README.md)

`nature-ref-verifier` performs multi-source cross-verification of references, comparing authors, title, year, volume, issue, pages, DOI, and publication status, then outputs a structured fixable report.

## What To Use It For

- Check an entire manuscript reference list before submission.
- Verify a few citations raised in reviewer comments.
- Clean incorrect metadata in a Zotero / BibTeX library.
- Flag volume-year conflicts, author-order problems, page mismatches, title differences, and wrong DOI targets.
- Verify Chinese references through CNKI or Chinese-language sources for author names, journal names, and pages.

## Typical Requests

- "Check these 50 references one by one and mark the ones that must be fixed."
- "These DOIs may be wrong; find the real titles and page ranges."
- "Turn the incorrect fields in this BibTeX file into patch suggestions."

## What You Need To Provide

- Reference list, single citation, BibTeX, RIS, Zotero item key, or manuscript bibliography page.
- Allowed sources such as Crossref, PubMed, IEEE, CNKI, publisher pages, or Zotero.
- Whether a directly importable correction file is needed.

## Outputs

- Field-level verification table: original value, trusted-source value, difference, and evidence link.
- Severity labels: must fix, check suggested, reference only, or unverifiable.
- Optional BibTeX patch, Zotero update suggestion, or Markdown review report.
- Human-check checklist for uncertain records.

## Boundaries

- A single search result is not treated as final truth; key fields are verified against DOI records, publishers, or authoritative databases.
- DOI year, volume year, and online-publication year conflicts are explained rather than force-merged.
- Inaccessible databases or Chinese sources are marked as unverified.

## Related Skills

- `nature-academic-search`: retrieve paper metadata and citation indicators.
- `nature-citation`: choose candidate citations for manuscript claims.
- `nature-response`: respond to reviewer comments about reference errors.
