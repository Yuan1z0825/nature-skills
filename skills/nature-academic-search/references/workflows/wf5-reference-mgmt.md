# Workflow 5: Reference Management

**Purpose:** Manage and enrich reference collections.

**Uses:** [Dedup Engine](../dedup-engine.md) — for 5a (related papers overlap).

## 5a. Find Related Papers

1. Fetch source paper metadata via `pubmed_fetch_articles`.
2. Discover related articles via `pubmed_find_related`.
3. Filter by relevance, date, or journal.
4. Deduplicate against source using [Dedup Engine](../dedup-engine.md).
5. Present with context notes.

## 5b. BibTeX Generation

1. DOI → `search_crossref` → format as BibTeX.
2. PMID → `pubmed_fetch_articles` → format as BibTeX.
3. Batch: process multiple IDs via `scripts/format-converter.py`.
4. Clean: deduplicate by citation key, sort, validate required fields.
   See [BibTeX Format](../ris-bibtex-format.md#bibtex-format) for field requirements.

## 5c. ID Conversion

1. Accept DOI, PMID, or PMCID (up to 50).
2. Use `pubmed_convert_ids` for conversion.
3. Fetch metadata for newly resolved IDs via `pubmed_fetch_articles`.

## 5d. Citation Formatting

1. Accept PMIDs.
2. Use `pubmed_format_citations` for APA / MLA / BibTeX / RIS output.

## 5e. Full-Text Access

1. `pubmed_fetch_fulltext` for articles with PMC copies (structured JATS).
2. If an open-access article has no PMC copy and built-in fetch returns no usable text, see [Publisher pages and PDF text](../../static/core/routing-and-ops.md#publisher-pages-and-pdf-text-optional).
3. Fall back to `download_paper` for paywalled articles.
4. Report: structured text / PDF-as-text / metadata-only.
