# Workflow

Run these seven steps for any citation job. For runs with more than ~10 segments, switch to the batched long-article strategy in `references/script-usage.md`.

## 1. Segment the text

- Split long text into citable segments. Prefer paragraph boundaries first, then sentence boundaries.
- Keep each segment focused on one citable idea when possible.
- Preserve original order and stable segment IDs such as `S001`, `S002`, `S003`.
- Skip obvious non-citable connective sentences unless the user asks to cite every sentence.
- For very long text, process in batches but keep a single final mapping table.

Default segmentation rules: use blank lines as paragraph boundaries; if a paragraph is longer than about 700 characters or contains multiple claims, split into sentences; merge very short fragments into neighboring text unless they contain a distinct claim; keep section headings as labels, not as citable segments. If the input has more than about 10 segments, prefer batch mode.

## 2. Parse each segment

For each citable segment:

- Extract the core claim in one sentence.
- Identify claim type: `mechanism`, `association`, `method`, `clinical`, `epidemiology`, `background`, `definition`, or `review-context`.
- Identify entities, intervention/exposure, outcome, population/model, directionality, and boundary.
- Convert the claim into 2-4 English search queries: one precise query with all key terms; one synonym query; one broader background query; one methods or model query if relevant.

If the claim is too broad, split it into citable subclaims rather than searching the whole sentence. For deeper help turning a claim into queries and support grades, open `references/search-strategy.md`.

## 3. Search candidate papers

Prefer `scripts/nature_citation.py` when internet access is available. The full flag list, polite-pool/rate-limit options, and the long-article batch strategy are in `references/script-usage.md`. A minimal run:

```bash
python scripts/nature_citation.py \
  --text "PASTE MANUSCRIPT TEXT HERE" \
  --scope cns \
  --outdir /tmp/nature-citation \
  --format ris \
  --with-artifacts
```

When the topic is biomedical or PubMed-indexed, also search PubMed with journal filters and compare results against Crossref. Use NCBI E-utilities rate limits and include `tool`/`email` parameters if running repeated searches.

## 4. Evaluate whether each paper supports the segment

Use a conservative support scale:

- `strong support`: the paper directly tests the same relationship/mechanism/method and the result supports the segment.
- `partial support`: the paper supports part of the segment, a related model, or a narrower condition.
- `background support`: the paper supports field context, not the specific claim.
- `contradictory/limiting`: the paper conflicts with or narrows the claim.
- `metadata-only candidate`: title/metadata suggest relevance, but abstract/full text has not been checked.

Never cite a `metadata-only candidate` as support without checking the abstract or publisher page. If a paper is a review, label it as review/context and avoid using it as primary evidence for an experimental claim when primary articles are available.

## 5. Export reference-manager file

Default behavior: write one reference-manager file; support publication time filters with `--from-year` and `--to-year`; for long or ambiguous texts, use `--with-artifacts` so the HTML browser is available.

Default file is `references.ris`. Optionally write `references.enw` for EndNote tagged import or `references.rdf` for Zotero RDF. If the user asks to choose the download format, treat `RIS`, `ENW`, and `Zotero RDF` as the supported options and return only one export file unless they explicitly ask for multiple. Do not invent missing fields. If DOI, pages, volume, or issue are missing, leave them absent.

Before writing any reference-manager file, run the author-integrity gate.

- Use the complete ordered author list from structured Crossref, PubMed, or publisher metadata. Never derive `AU` fields from a display citation, an `et al.` string, or a surname-only list.
- Write one `AU` line per person in `Family, Given` form and retain initials, suffixes, particles, and ordering supplied by the source.
- Encode a consortium or institutional author as a corporate author with a trailing comma so EndNote does not invert it.
- If any personal author lacks a family name or given name/initials, stop the export. Refetch by DOI or PMID and compare against the publisher record. Do not label the file EndNote-ready while the author list is incomplete.
- Permit `--allow-incomplete-authors` only as an explicit emergency override, and keep warnings in the exported record.

See `references/ris-endnote.md` for format details and the EndNote import option.

## 6. Optional review artifacts

Generate review artifacts (HTML/TSV/JSON/report) for long or ambiguous runs — they are the primary way the user browses, filters, and selects candidates. Use `--with-artifacts` when the text is long, the query is broad, or the user needs manual curation. Report the HTML visualization path prominently when artifacts are enabled, and generate TSV/JSON/report alongside the HTML.

## 7. Report results

Unless the user asks for a different format, return:

```text
交互式引用浏览器
- [absolute path to citation_visualization.html]  ← 在浏览器中打开此文件，可筛选/选择/下载引用

检索范围
- [Nature Portfolio / Science family / Cell Press / flagship only, plus date limits]

分段引用对应关系
S001: [source segment]
  - [Author, year, title, journal, DOI]
  - 支撑等级: [strong/partial/background/limiting/metadata-only]
  - 插入建议: [e.g. after sentence / after clause]

导出文件
- [absolute path to references.ris / references.enw / references.rdf]

风险和缺口
- [missing full-text check, contradictory evidence, no direct CNS literature, etc.]
```

When HTML review artifacts were generated, put the existing browser path first so the user can browse candidates. Otherwise omit the browser block; do not create extra artifacts or report a nonexistent path merely to fill the template. If no suitable CNS/Nature-series paper exists, say so plainly and suggest the best nearby options from non-CNS literature only if the user wants broader coverage. If the text is long, mention the batch strategy used, especially when you limited the run with `--batch-size` or `--max-segments`.
