# Workflow 6: Strict Other-Citation Impact Audit

## Contents

- [Definitions](#definitions)
- [Procedure](#procedure)
- [Article Summary Table Mode](#article-summary-table-mode)
- [Output Format](#output-format)
- [Red Lines](#red-lines)


**Purpose:** Audit who cites a target paper, distinguish strict independent
other-citations from self/team citations, build article-level citation metric
tables, identify high-profile independent citers, and extract how those citers
discuss the target paper.

**Use when the user asks:** `严格他引`, `他引判定`, `排除自引`,
`谁引用了我的文章`, `引用我的文章的人有没有大牛`, `院士引用`,
`杰青引用`, `长江学者引用`, `Fellow citation`, `influential citer`,
`citation context`, `文章引用表`, `指定文章引用数`, `严格他引数`,
`整理成表格`, or similar citation-impact questions.

**Uses:**
- [Search Strategy](../search-strategy.md) — construct title/DOI/cited-by queries.
- [Dedup Engine](../dedup-engine.md) — deduplicate citing records across sources.
- [Source Tiers](../source-tiers.md) — report source coverage and confidence limits.

## Definitions

Use conservative labels. Do not upgrade a citation to strict independent status
unless the evidence supports it.

| Label | Meaning |
|---|---|
| `confirmed_strict_other_citation` | The citing paper cites the target paper; no target-paper author overlap; no obvious same lab/team/institution conflict; no discoverable recent coauthorship tie with target authors in the checked sources. |
| `probable_external_citation` | No author overlap is visible, but affiliation, ORCID, coauthor-network, or full metadata is incomplete. |
| `self_or_team_citation` | At least one target-paper author appears on the citing paper, or the citing authors are clearly from the same lab/team/project group. |
| `collaborator_or_affiliation_overlap` | No direct author overlap, but there is a same-institution, same-center, advisor/student, project, or recent coauthorship tie strong enough to make strict independence doubtful. |
| `unknown_metadata` | Metadata is insufficient to classify independence. |

For `严格他引`, the default bar is stricter than a simple non-self-citation:
exclude direct self-citations, same-team citations, and obvious close
collaboration-network citations. If the user wants a looser bibliometric
definition, state the changed rule explicitly.

## Procedure

1. **Identify the target paper.**
   - Resolve title, DOI, PMID/arXiv ID if any, publication year, journal, author
     list, corresponding authors, affiliations, and author identifiers
     (ORCID/Scopus Author ID/Semantic Scholar author ID when available).
   - If the target is ambiguous, list the candidate records and ask for the DOI
     or exact title before auditing.

2. **Retrieve citing papers with source coverage stated.**
   - Prefer citation-graph sources when available: Scopus, Web of Science,
     Semantic Scholar, OpenAlex, CrossRef cited-by, publisher cited-by pages.
   - Use multiple sources when possible, then deduplicate with
     [Dedup Engine](../dedup-engine.md).
   - Report which sources were checked and which were unavailable. Do not imply
     an exhaustive citation count when only partial sources were available.

3. **Classify strict other-citation status.**
   - Compare citing-paper authors against target-paper authors by normalized
     name plus ORCID/author IDs when available.
   - Check affiliations, lab/center names, corresponding-author groups, and
     recent coauthorship ties when source metadata allows.
   - Classify each citing paper using the labels above. Include the specific
     evidence for exclusions, such as shared author, shared lab, shared center,
     or missing metadata.

4. **Extract citation context.**
   - Prefer full text: PubMed Central JATS, ScienceDirect metadata/full text,
     publisher HTML, or legally available PDF text.
   - Locate the target reference in the bibliography, map it to in-text citation
     markers (numeric or author-year), then extract the citing sentence plus one
     adjacent sentence before/after when available.
   - If only abstract/metadata is available, set `citation_context:
     unavailable` and do not infer wording from title similarity.
   - Preserve exact citation-context snippets only when short; otherwise
     paraphrase and identify where the citation appeared.

5. **Identify high-profile independent citers.**
   - Run this step only on `confirmed_strict_other_citation` and
     `probable_external_citation` papers unless the user asks for all citing
     papers.
   - Check identity evidence in this order:
     1. official university, academy, government, funding-agency, or learned
        society pages;
     2. official fellow/member lists, talent-program lists, editorial-board
        pages, or institutional appointment announcements;
     3. stable researcher profiles such as ORCID, Scopus, Semantic Scholar, or
        Google Scholar;
     4. news, personal pages, or third-party biographies only as secondary
        support.
   - Recognized profile signals include academy member / 院士, university
     president or vice president, dean or department chair, national talent
     awards such as 杰青 / 长江学者 / 优青, society fellow status such as IEEE
     Fellow / AAAS Fellow / RSC Fellow / ASCE Fellow, highly cited researcher
     status, major editor roles, or clearly field-leading citation/profile
     evidence.
   - Disambiguate names using affiliation, field, ORCID/author IDs, coauthors,
     and publication topics. If the evidence does not identify the same person,
     mark the profile `unverified`.

6. **Assess how the target paper was cited.**
   - Classify citation function as one or more of:
     `background_support`, `method_used`, `data_or_code_used`,
     `benchmark_or_comparison`, `direct_extension`, `replication_or_validation`,
     `limitation_or_critique`, `review_summary`, or `incidental_mention`.
   - Classify stance as `positive`, `neutral`, `critical`, `mixed`, or
     `not_assessable`.
   - Explain the classification from the citation context. Do not infer praise
     merely from the fact that the paper was cited.

7. **Generate the audit report.**
   - Start with coverage and limitations.
   - Separate high-profile independent citers from ordinary citing papers.
   - Keep every identity claim tied to evidence. Unsupported "大牛" labels are
     not allowed.

## Article Summary Table Mode

Use this compact mode when the user asks to organize one or more specified
papers into a table, especially when they ask for fields such as article title,
publication date, authors, affiliations, citation count, strict other-citation
count, and DOI.

### Required fields

For each specified paper, return a table with these columns unless the user asks
for a different schema:

| Column | Required handling |
|---|---|
| `Article title` | Use the resolved title from DOI/PMID/arXiv/publisher metadata. If multiple records match, ask for confirmation before counting citations. |
| `Publication date` | Prefer full date (`YYYY-MM-DD`); otherwise use year/month or year and mark the precision. |
| `Authors` | List all authors when the list is short; for long author lists, list first 6 + `et al.` and state that the full author list is available. |
| `Author affiliations` | Preserve author-affiliation mapping when metadata provides it. If only institution-level metadata is available, summarize distinct affiliations and mark mapping precision. |
| `Citation count` | Use the best available citation-count source and name it in an evidence note. Do not merge counts from different databases as if they are identical. |
| `Strict other-citation count` | Count only records classified as `confirmed_strict_other_citation`. Optionally report `probable_external_citation` separately in a note, not inside the strict count. |
| `DOI` | Normalize DOI casing/prefix; use `not_found` only after checking title and ID-based lookup routes. |

### Counting rules

1. Resolve the target paper first; do not count citations against an ambiguous
   title match.
2. Retrieve citing records as in the main procedure, deduplicate them, then
   classify strict other-citation status.
3. Set `Citation count` to one source-specific count, preferably Scopus, Web of
   Science, Semantic Scholar, OpenAlex, or publisher/CrossRef in that order when
   available. If multiple counts are available, include them in `Evidence /
   notes` instead of collapsing them.
4. Set `Strict other-citation count` to the number of deduplicated citing papers
   with label `confirmed_strict_other_citation`.
5. If the audit cannot inspect enough metadata to classify strict independence,
   use `not_assessable` for the strict count and state the missing sources.
6. For batches, keep one row per target paper and put source limitations in a
   short notes column or a separate evidence section.

### Table format

```markdown
| Article title | Publication date | Authors | Author affiliations | Citation count | Strict other-citation count | DOI | Evidence / notes |
|---|---|---|---|---:|---:|---|---|
|  |  |  |  |  |  |  |  |
```

For Chinese outputs, use this header:

```markdown
| 文章名 | 发表时间 | 作者名 | 作者机构 | 引用数 | 严格他引数 | DOI | 证据 / 备注 |
|---|---|---|---|---:|---:|---|---|
|  |  |  |  |  |  |  |  |
```

Always include a short source note after the table:

```text
计数来源：
- 引用数来源：
- 严格他引判定来源：
- 未覆盖或无法访问的来源：
```

## Output Format

```text
Strict other-citation impact audit

Target paper
- Title:
- DOI / PMID / arXiv:
- Year / venue:
- Target authors checked:

Coverage
- Citation sources checked:
- Full-text sources checked:
- Identity sources checked:
- Known limitations:

Citation classification summary
- total citing records retrieved:
- deduplicated citing papers:
- confirmed strict other-citations:
- probable external citations:
- self/team citations:
- collaborator or affiliation-overlap citations:
- unknown metadata:

High-profile independent citers
1. [Name]
- Citing paper:
- Strict other-citation status:
- Profile signals:
- Identity evidence:
- Citation context:
- How they used the target paper:
- Stance:
- Confidence:

All citing-paper classifications
| Citing paper | Year | Citer(s) flagged | Strict-status label | Citation context available | Citation function | Notes |
|---|---:|---|---|---|---|---|

Evidence gaps / next checks
- [missing source, paywalled full text, ambiguous author identity, incomplete affiliation metadata]
```

## Red Lines

- Do not call someone an academy member, fellow, dean, president, 杰青, 长江学者,
  or similar without evidence for the same person.
- Do not treat same-name matches as identity matches without affiliation or
  author-ID support.
- Do not treat citation count or h-index alone as proof that the citer is a
  "大牛"; present it as bibliometric context only.
- Do not infer citation context from abstracts, titles, or reference-list
  presence when full text is unavailable.
- Do not hide source coverage limits. If Scopus/WoS/Semantic Scholar/OpenAlex
  are unavailable or incomplete, say so before reporting counts.
