# `nature-paper-card` Tutorial

[中文](nature-paper-card-tutorial.md)

## What It Solves

A conventional abstract summary reports what the authors claim. `nature-paper-card` also examines how the method works, which experiments support each central conclusion, where the conclusion boundaries lie, and which follow-up ideas are worth testing. It produces a reviewable Paper Card with fixed Sections 01–16.

## Prepare the Input

A complete PDF is preferred. A DOI, arXiv page, publisher article, pasted text, or a `nature-reader` source map also works. When only an abstract is supplied, the result automatically uses `source-limited` mode.

Example request:

```text
Use nature-paper-card to deep-read this PDF and generate an English Paper Card.
Focus on:
1. the problem solved by each method module;
2. the experiments that genuinely support the main claims;
3. what the authors did not demonstrate;
4. follow-up research ideas that can be tested.
```

## Run the Workflow

The Agent should first invoke the bundled `scripts/prepare_paper.py` instead of writing a temporary PDF extraction script. After preparation, it selects one locator mode:

| Mode | When It Applies | Locator Policy |
|---|---|---|
| `page-grounded` | PDF page extraction is reliable | Use PDF pages plus section, figure, table, or equation locators |
| `structure-grounded` | Pages are unreliable but document structure remains reliable | Use only sections, figures, tables, equations, or source blocks |
| `source-limited` | Only an abstract, metadata, or excerpt is available | State the source boundary and do not emit page citations |

The Agent then builds an evidence inventory and claim–evidence matrix, drafts the Paper Card, and runs `scripts/audit_paper_card.py` for final QA.

## Inspect the Outputs

A typical output directory contains:

```text
workdir/
├── source_bundle.json
├── paper-card.md
├── audit-report.json
└── rendered-pages/    # only when visual inspection is needed
```

Check `paper-card.md` for the following:

- Sections 01–16 are complete and in order.
- Major methods, results, boundaries, and limitations have source locators.
- Numerical results match the paper.
- Author statements and Agent analysis are clearly separated.
- Unavailable page numbers trigger a correct fallback instead of fabricated citations.
- Research ideas in Section 16 include a hypothesis, mechanism, experiment, and failure criterion.
- Sections 17 and 18 and public-article content are absent.

Errors in `audit-report.json` should be resolved before delivery. Warnings require scientific judgment against the source.

## Partial-Source Example

When only an abstract is available:

```text
Use nature-paper-card to generate a source-limited Paper Card from this abstract.
Do not infer unseen experiments or emit page citations. Mark unsupported sections explicitly.
```

The result keeps the Sections 01–16 structure, but content unsupported by the supplied material is marked `Not assessable from supplied material`.

## Relationship to Adjacent Skills

- For a bilingual full-text reading artifact, use `nature-reader`.
- For external literature search and field-history verification, use `nature-academic-search`.
- For a formal reviewer report, use `nature-reviewer`.
- For batch paper discovery and screening, use `nature-literature-pipeline`.
- For a paper presentation deck, use `nature-paper2ppt`.
