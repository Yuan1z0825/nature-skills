# Core principles (paper2ppt)

## Purpose

Transform a scientific paper or paper-derived notes into a complete Chinese, figure-integrated PPTX presentation package with a Nature-style reporting logic.

When the user requests a deck, deliver a real `.pptx` rather than stopping at an outline or script. If the user explicitly requests only an outline, explanation, or approval stage, honor that scope. Keep supporting files minimal unless the user asks for more traceability.

Use this skill for papers across scientific fields, including life sciences and medicine; chemistry and materials science; environmental and earth sciences; physics and engineering; computational biology, AI, and methods papers; interdisciplinary Nature-family style research; and reviews, perspectives, resources, datasets, and benchmark papers.

## Core principle

Use the paper's scientific argument as the presentation spine. The default slide logic should help the audience answer, in order:

1. Why does this problem matter?
2. What gap or bottleneck does the paper address?
3. What did the authors do?
4. What is the key evidence?
5. Why should we trust the result?
6. What is new, reusable, or broadly meaningful?
7. Where are the boundaries and open questions?

This is more important than copying the paper section order.

## Lean operating mode

Default to the lowest-overhead workflow that still produces a usable PPTX.

Do:
- read only the source material needed to understand the paper's argument,
- extract only figures/tables that will actually appear in the deck,
- create the PPTX as the primary deliverable,
- design slides with varied, evidence-led composition rather than rigid AI-looking card templates,
- prevent text overflow by writing shorter on-slide copy, using larger text boxes, and splitting slides when needed,
- run at least one self-audit and correction pass on the generated PPTX,
- run lightweight structural checks on the PPTX package after revision,
- write a short QA report.

Avoid by default:
- exhaustive extraction of every figure, page, image, table, or supplement,
- full OCR unless normal text extraction fails or the PDF is scanned,
- saving full raw extracted paper text unless it is needed for debugging or reuse,
- installing new dependencies when an existing tool can complete the task,
- launching GUI apps or desktop automation just to render previews,
- generating long markdown scripts when the user only needs a deck,
- rendering every slide when no reliable headless renderer is available.

## Accepted inputs

The skill may receive: a full paper PDF; supplementary figures or tables; Word or markdown converted paper text; abstract + results + figure legends; structured reading notes; manually pasted article content; an `input/source.md` file; or a user-provided PPTX template.

Default output language is simplified Chinese unless the user requests otherwise. Preserve important technical terms, abbreviations, gene/protein names, model names, dataset names, equations, and statistical terms in English when needed, and keep them consistent via the Terminology Ledger.
