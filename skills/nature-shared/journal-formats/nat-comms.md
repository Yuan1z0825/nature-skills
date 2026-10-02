# Nature Communications — formatting facts

Authoritative facts about Nature Communications formatting requirements. Used by both `nature-polishing` and `nature-writing` when `journal=nat-comms`. This file holds the **facts**; each skill's `static/fragments/journal/nat-comms.md` adds the **action layer**.

> Always verify against the journal's current guidelines before final submission. Limits change. The numbers below are accurate as of early 2026.

## Article types and limits

| Article type | Body words | Abstract | References | Display items | Methods placement |
|---|---|---|---|---|---|
| **Article** | ~5,000 (incl. Methods) | 150 words | ~60 | up to 10 (figures + tables combined) | within main text |
| **Brief Communication** | ~2,000 (incl. Methods) | 100 words | ~20 | up to 4 | within main text |
| **Review** | ~6,000 | 200 words | ~100 | flexible | N/A |
| **Perspective** | ~4,000 | 150 words | ~50 | flexible | N/A |
| **Correspondence** | ~500 | none | ~10 | 1 | within main text |

### Critical word-count quirk (Articles)

The ~5,000-word limit **includes Methods**. This is the single biggest practical difference from *Nature* (where Methods sits after references with its own ~3,000-word allowance).

Budget upfront, e.g.:
- ~3,500 words for Introduction + Results + Discussion
- ~1,500 words for Methods

A paper with 4,800 words of Intro/Results/Discussion plus 1,500 words of Methods is **30% over the limit**.

## Abstract

- 150 words maximum
- Unstructured single paragraph
- No citations
- Spell out abbreviations at first use
- Keywords are assigned by editorial staff, not submitted
- Include quantitative results where possible (`94% conversion with 99% selectivity`, not `significant improvement`)
- Lead with the finding, not the background — editors triage on the abstract

## Figures and display items

- **Up to 10 display items** in the main article (figures + tables combined)
- **No Extended Data tier** (unlike *Nature*). Items beyond 10 go into Supplementary Information (downloadable, but still peer-reviewed)

### Resolution and format

| Parameter | Requirement |
|---|---|
| Line art resolution | 1,200 dpi minimum |
| Halftone / photo resolution | 300 dpi minimum |
| Combination (line + halftone) | 600 dpi minimum |
| File formats | TIFF, EPS, PDF, or JPEG |
| Color mode | RGB (online-only journal) |
| Single-column width | 89 mm |
| Double-column width | 183 mm |
| In-figure font | Arial / Helvetica / sans-serif, 5–7 pt |
| Panel labels | Lowercase bold letters (`a`, `b`, `c`, …) |

Online-only publication means: color is free, no CMYK requirement, design for screen reading (sufficient contrast, colorblind-friendly palettes, clear labels).

### Multi-panel figures

Common and accepted. A single figure with panels `a`–`l` is normal. No formal panel cap, but readability is enforced informally — if panel labels need magnification, the figure has too many panels.

## References

- **Style**: standard Nature reference style
- **In-text**: superscript numbers, sequential by first appearance. Multiple: `^1,2`. Ranges: `^3–7`.
- **Cap**: ~60 for Articles (more generous than *Nature*'s ~30)
- **Format example**:
  ```
  1. Smith, A. B., Johnson, C. D. & Williams, E. F. Title of article. Nat. Commun. 16, 1234 (2025).
  ```
- Author names: `Last, Initials` (no periods on initials)
- `&` before the last author
- Journal names abbreviated per ISO 4
- Volume in **bold**
- **Article number** (e.g., `1234`), not page range — Nature Communications is online-only
- Year in parentheses
- DOIs encouraged
- Reference list appears **before** the Methods section in the published article, even though Methods is part of the main text in the manuscript

## Supplementary Information

- Single PDF or multiple files; peer-reviewed
- Organize with a table of contents if it exceeds 10 pages
- Labels: `Supplementary Fig. 1`, `Supplementary Table 1`, `Supplementary Note 1`, `Supplementary Methods`
- Large tables → separate Excel files

## Mandatory statements

- **Data Availability statement** — required. Must specify repositories, accession numbers, DOIs. Enforced at production stage; **invalid or pre-publication accession numbers block publication**.
- **Code Availability statement** — required if custom code was used. Must include repository URL and DOI (e.g., via Zenodo).
- **Author contributions** — in the manuscript after the main text
- **Competing interests** — in the manuscript
- **Reporting Summary** — Nature Portfolio Reporting Summary required (Life Sciences Reporting Summary for life sciences). Sent to reviewers; not a checkbox exercise.

## Cover page elements

- **Title**: concise, informative, no abbreviations; recommended ≤ 15 words
- Author names with superscript affiliation numbers
- Affiliations with full institutional addresses
- Corresponding author(s) with email
- ORCID iDs required for corresponding author, encouraged for all

## Cover letter (separate upload)

Editors use the cover letter for triage. Do not waste it on generic statements like "broad interest." State explicitly:

1. What the finding is (one sentence)
2. What makes it new (one sentence)
3. Why it matters across multiple scientific disciplines (one sentence)

## Open access and licensing

- Fully open access — APC applies (verify current rate; substantial)
- Default license: **CC BY 4.0**
- Some funders (e.g., UKRI) require CC BY; others allow CC BY-NC — check funder requirements

## Transparent peer review

- **Default since November 2022**: reviewer reports and author responses published alongside accepted articles
- Authors may opt out during submission — opt-out must be deliberate
- Consider opt-out if reviewer exchanges contain content not suitable for public record

## Manuscript formats

- Initial submission: single PDF preferred (Word- or LaTeX-generated), figures embedded
- Revision: Springer Nature Word template **or** LaTeX `sn-jnl` class with `nature` option
- BibTeX: `sn-nature.bst`
- Both formats equally acceptable; no editorial preference

## Common desk-rejection / production-hold patterns

1. **Methods word count not budgeted** — most common formatting error, especially for authors transferring from *Nature*
2. **Reporting Summary completed as checkbox** — vague `N/A` responses, no explanation for outlier exclusions, missing blinding info, weak power calculations → generates specific revision requests
3. **Data availability statement with unresolved accession numbers** — production verifies all accessions before publication; invalid IDs block release
4. **Generic cover letter** — fails to establish cross-disciplinary significance; signals authors haven't considered scope fit

## Transfer from Nature

Manuscripts rejected from *Nature* can transfer with reviews intact. Editors may decide on existing reviews or send for additional review. **Formatting differences (Methods placement, word limit including Methods, no Extended Data tier) are handled at revision, not at transfer**.
