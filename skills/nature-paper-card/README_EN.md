# `nature-paper-card` Skill

[中文说明](README.md)

`nature-paper-card` deeply reads one scientific paper and produces a source-grounded, reviewable Sections 01–16 Paper Card. It focuses on the research question, method logic, experiment-to-claim evidence, conclusion boundaries, critical analysis, and testable research ideas instead of translating the abstract.

## What To Use It For

- Deep-read one paper through a consistent structure rather than produce only a summary.
- Trace central conclusions to figures, tables, equations, experiments, and ablations.
- Separate author statements, external facts, Agent analysis, and research hypotheses.
- Examine conclusion boundaries, author-stated limitations, and unresolved questions.
- Derive falsifiable and actionable candidate research ideas from the evidence chain.

## Typical Requests

- "Use `nature-paper-card` to deep-read this PDF and generate a complete Paper Card."
- "Analyze the method modules, essential equations, and experiment-to-claim evidence chain."
- "What does this paper actually demonstrate, and what does it not demonstrate?"
- "Propose testable follow-up directions based on the paper's limitations."

## What You Need To Provide

- A paper PDF, DOI, arXiv page, publisher article, pasted text, or an existing `nature-reader` source map.
- When relevant, the output language, output directory, and questions that need special attention.
- The skill can work from an abstract or partial material, but it will explicitly mark sections that cannot be assessed.

## Workflow

1. Run the bundled `prepare_paper.py` to prepare source material instead of writing a temporary PDF extraction script.
2. Select `page-grounded`, `structure-grounded`, or `source-limited` mode according to evidence reliability.
3. Select a methods, discovery, resource, clinical, materials, or review lens from the paper's argument structure.
4. Build an evidence inventory and claim–evidence matrix before drafting the fixed Sections 01–16.
5. Run the bundled `audit_paper_card.py` to check structure, locators, and evidence grounding.

## Outputs

- `paper-card.md`: the fixed Sections 01–16 deep-reading Paper Card.
- `source_bundle.json`: normalized source material from a PDF or source map.
- `audit-report.json`: structure, locator, and evidence-grounding audit results.
- Optional `rendered-pages/`: rendered PDF pages for visual inspection.

## Runtime and Dependencies

- Python 3 is required.
- PDF processing uses the bundled scripts and PDF libraries available in the current environment.
- When PDF page indices are reliable, the card uses both PDF-page and structural locators. If page extraction fails, it falls back to structural locators without inventing page numbers.
- Missing or invalid source-map page locators remain explicitly unlocated with a warning; they are never assigned to PDF page 1.
- External search is limited to field-history checks, knowledge connections, bibliographic verification, or an explicitly requested novelty check.

## Tutorial

See the complete [English tutorial](../../docs/nature-paper-card-tutorial_EN.md) for copyable prompts, inputs, the three locator modes, output files, and acceptance checks.

Minimal invocation:

```text
Use nature-paper-card to deep-read this paper and generate an English Paper Card.
Focus on the method modules, decisive experiments, conclusion boundaries,
and testable follow-up ideas.
```

## Boundaries

- Process one paper at a time; do not perform batch literature monitoring.
- Do not produce full-text bilingual translation; use `nature-reader` for that output.
- Do not produce a formal peer-review report; use `nature-reviewer` for reviewer-style assessment.
- Do not turn the Paper Card into a public article or add Sections 17 and 18.
- When source material is insufficient, write `Not assessable` rather than invent unseen experiments or page numbers.

## Related Skills

- `nature-reader`: generate bilingual full-text Markdown, figure-text alignment, and a stable source map.
- `nature-academic-search`: verify field history, external knowledge connections, or related work.
- `nature-reviewer`: produce a formal reviewer-style assessment.
- `nature-literature-pipeline`: discover, screen, and deliver papers in batches.
- `nature-paper2ppt`: convert paper content into presentation slides.
