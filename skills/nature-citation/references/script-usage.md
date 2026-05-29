# Script usage and long-article strategy

Open this reference when running `scripts/nature_citation.py` or when the input is long enough to need batching. It expands step 3 of the workflow.

## Running the script

Start with `scripts/nature_citation.py` when internet access is available:

```bash
python scripts/nature_citation.py \
  --text "PASTE MANUSCRIPT TEXT HERE" \
  --scope cns \
  --outdir /tmp/nature-citation \
  --format enw \
  --with-artifacts
```

### Useful options

- `--text-file manuscript.txt`: read long text from a file.
- `--claim "CLAIM TEXT"` or `--claim-file claims.txt`: treat each claim as a segment.
- `--doi 10.xxxx/xxxxx` or `--doi-file dois.txt`: export known DOI records after screening.
- `--scope nature`: Nature Portfolio-style journals only.
- `--scope flagship`: Nature, Science, and Cell only.
- `--from-year 2018 --to-year 2026`: constrain publication dates.
- `--rows 40`: raise for broad searches; keep top candidates manageable.
- `--per-segment 3`: number of citation candidates to keep per segment.
- `--max-retries 2`: retry transient Crossref failures before skipping a query.
- `--format enw|ris|zotero-rdf`: export format. If omitted and `--output-file` is set, infer from suffix.
- `--mailto you@example.com`: use Crossref's polite pool.
- `--batch-size 10`: process segments in batches of N. Each batch writes an incremental export file.
- `--max-segments 20`: only process the first N segments. Useful for testing or section-by-section workflows.
- `--sleep 0.3`: seconds between Crossref requests. Default is 0.3; raise to 1.0 if rate-limited.

## Long-article strategy

When the input text is longer than roughly 3000 characters (about 10+ segments), switch to a batched workflow to avoid timeout, context overflow, or incomplete results:

1. **Auto-detect length.** Count segments after segmentation. If there are more than 10 segments, switch to batch mode automatically.
2. **Split by section.** Prefer splitting at paragraph double-line breaks or explicit section headings (`Introduction`, `Results`, etc.) so each batch is a coherent unit, not arbitrary sentence groups.
3. **Process each batch independently.** Run the script once per batch using `--batch-size` or `--max-segments`, OR split the text externally and call the script once per chunk. Each call writes its own intermediate export file.
4. **Merge results at the end.** After all batches finish, combine the intermediate files into one final export. Deduplicate by DOI.
5. **Minimize inline analysis.** For long articles, do NOT write detailed support-grade notes for every single segment inline. Instead:
   - Write a compact summary table (segment ID → best candidate → support grade).
   - Point the user to the HTML visualization for full browsing.
   - Only elaborate on segments where no candidate was found or evidence is contradictory.

### Quick guide

| Segments | Strategy |
|---|---|
| 1–10 | Run once, full inline analysis is fine. |
| 11–25 | Use `--batch-size 10`. Write a compact summary table. Point to HTML. |
| 26+ | Split by section. Run script per section with `--batch-size 10`. Compact summary + HTML only. |

For long texts, prefer the HTML browser for review and selection instead of relying only on inline notes.
