# Workflow 4: Citation File Management

**Purpose:** Download and convert citation files.

**Uses:** `scripts/format-converter.py` — multi-source downloader (PubMed/CrossRef/arXiv) with .nbib/.ris/.bib output.

## Procedure

If the user supplied complete citation records and requests only local format conversion, read
[RIS and BibTeX Format](../ris-bibtex-format.md), convert those records, and check record count,
author order, identifiers, and escaping. Do not fetch metadata or run network preflight unless
verification or missing fields require it. The downloader examples below apply to retrieval by
identifier or query; `--input refs.txt` accepts identifier/query lines, not arbitrary citation files.

1. **Identify papers** — by PMID, DOI, arXiv ID, or search query.
2. **Download** via format-converter:
   ```bash
   # PubMed
   python scripts/format-converter.py --pmid 28344011 --format nbib

   # CrossRef
   python scripts/format-converter.py --doi 10.1038/nature14539 --format ris

   # arXiv
   python scripts/format-converter.py --arxiv 1706.03762 --format bib

   # Batch from file
   python scripts/format-converter.py --input refs.txt --format ris
   ```
3. **Convert format** as needed: `.nbib` (MEDLINE), `.ris` (EndNote/Zotero), `.bib` (BibTeX/LaTeX).
   Format specifications: [RIS and BibTeX Format](../ris-bibtex-format.md).
4. Save to `./references/` directory.
5. Verify output count matches input.

## refs.txt Format

```
PMID:28344011
DOI:10.1038/nature14539
ARXIV:1706.03762
QUERY:TB-Profiler AND Bioinformatics[Journal]
AUTHOR:Dheda TITLE:drug-resistant tuberculosis
# Lines starting with # are comments
```

## Error Modes

- **Script failure (2x):** fall back to manual .ris/.bib generation from MCP-fetched metadata.
- **DOI not found in CrossRef:** suggest verifying DOI spelling, trying PMID instead.
- **arXiv ID not found:** check for version suffix (v1, v2), try without it.
