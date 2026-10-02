# Paper Card workflow

## 1. Inspect and bound the source

Record the available source, completeness, figure/table availability, supplementary-material availability, extraction confidence, and page-number systems. Resolve DOI or arXiv metadata when possible. Never imply full-paper coverage from an abstract-only input.

For PDF or source-map JSON input, resolve and run the bundled `scripts/prepare_paper.py` before manual analysis. Do not create a replacement script. Inspect the generated metadata, page count, section list, evidence inventory, extraction confidence, and validation block. For source maps, inspect `locator_summary` and `unlocated_blocks`: missing or invalid locators remain structurally usable but have no PDF page. If rendered pages were requested, visually check the pages that contain central figures, tables, equations, or extraction anomalies.

Choose and record exactly one locator mode:

- `page-grounded` when PDF page indices are reliable;
- `structure-grounded` when only section, figure, table, equation, or source-block locators are reliable;
- `source-limited` when only abstract, metadata, or supplied excerpts are reliable.

Printed page labels never determine whether page-grounded mode is available.

## 2. Build an evidence inventory

Before interpreting the paper, inventory:

- every main section;
- every main figure and its argumentative role;
- every main table and its argumentative role;
- every essential equation;
- datasets, populations, or materials;
- baselines, metrics, evaluation settings, and uncertainty;
- explicit author limitation statements;
- supplements that are present or unavailable.

Do not draft the card until the inventory explains where the central method and result evidence lives.

## 3. Build a claim-evidence matrix

Create stable internal records for:

- central claim;
- source pointer;
- evidence type;
- exact result or quotation-free paraphrase;
- supported claim strength;
- unsupported stronger interpretation;
- confidence;
- contradictions or missing support.

In page-grounded mode, use PDF page index plus section, equation, figure, table, appendix, or existing source-block IDs. Printed page labels are optional. In structure-grounded mode, omit all page numbers and use the structural identifiers. In source-limited mode, use only `Abstract`, `Metadata`, or `User-provided excerpt`. Do not invent page or line numbers.

## 4. Reconstruct the paper's argument

Write the chain:

```text
problem
-> limitation of prior approaches
-> core insight
-> design choice
-> evidence required
-> experiment or analysis supplied
-> conclusion actually supported
```

Identify broken, weak, or untested links without turning the output into a reviewer report.

## 5. Analyze method and evidence

For each central component, answer:

- What does it do?
- Why is it needed?
- What are its inputs and outputs?
- What assumption does it introduce?
- Which experiment isolates its contribution?
- What remains unknown if it is removed or changed?

For each central experiment, answer:

- What claim is being tested?
- What is compared under which conditions?
- What metric and uncertainty are reported?
- What result was observed?
- What conclusion is justified?
- What stronger conclusion is not justified?

## 6. Add external context selectively

Use external sources for field history or knowledge connections only when accessible and useful. Cite them. If no external verification is performed, label the development route and novelty position as `paper-framed` or `unverified`.

Record one context mode:

- `paper-only` - no claims beyond the supplied paper are independently verified;
- `targeted external check` - selected metadata, history, or connections are verified;
- `externally verified` - Sections 04 and 15 receive a deliberate multi-source check.

Do not make context verification a prerequisite for a card that the user explicitly wants to remain source-only.

## 7. Separate limitations

Keep two sections distinct:

- Section 12 contains only limitations explicitly acknowledged by the authors.
- Section 13 contains Agent analysis, alternative explanations, missing controls, failure cases, and proposed validation tests.

Do not move Agent criticism into Section 12.

If the paper has no explicit limitations section or statement, say so. Do not promote incidental dataset descriptions, evaluation constraints, or implementation details into author-acknowledged limitations. Related author-noted constraints may be listed under a separately labelled subsection.

## 8. Generate knowledge and ideas

For Sections 14-16:

- extract transferable concepts, methods, formulas, and experimental designs;
- connect them to verified literature, user-provided knowledge, or clearly marked candidate directions;
- derive research ideas from a concrete limitation or unresolved observation;
- specify hypothesis, delta, validation, and failure modes;
- avoid claiming novelty without a dedicated search.

## 9. Write and audit the artifact

Write `paper-card.md` using the exact schema and the user's language. Check internal consistency across terminology, datasets, sample sizes, baselines, metrics, and numbers. Add a short evidence-status summary at the top.

Run the bundled `scripts/audit_paper_card.py` with the selected locator mode. Supply `source_bundle.json` in page-grounded mode. In fallback modes, the bundle is optional and unavailable source-inventory checks become warnings. Correct all errors, assess warnings, and rerun until no audit error remains. The script checks structure and traceability; it does not replace scientific judgment.
