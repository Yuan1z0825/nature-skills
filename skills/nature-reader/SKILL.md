---
name: nature-reader
description: "Create source-grounded Chinese-English paper readers with aligned text, figures, tables, and equations. Use for 全文翻译、中英文对照、论文精读 or source-linked questions about a paper; respect a requested excerpt or question without generating a full reader."
metadata:
  version: "2.1.1"
  author: Community contribution, refactored into static/dynamic layers
---

# Full-Paper Markdown Reader — Router

## Routing protocol

First distinguish creating a reader from answering a question or translating an excerpt.
For a source-linked question, read `references/grounding-rules.md` and inspect only the relevant
source material; reuse existing source-map IDs when available. Do not regenerate the reader or
require a full source map before answering. For an explicit excerpt request, apply extraction,
translation, and grounding rules to that excerpt. The full-artifact workflow below applies when
the user requests a reader or full-paper translation.

For a new task, load the core and matching resources below. Reuse already loaded guidance on follow-ups; load more only when the task needs it.

### 1. Load the manifest and the core layer

Read [manifest.yaml](manifest.yaml). It declares the `source_format` axis, the allowed values, and the file paths each value maps to.

Also read every file listed under `always_load`. These hold the core principles, the reading workflow, and the output contract that apply to every reading job, plus the shared Terminology Ledger used to build the recurring-term table.

### 2. Detect the source format

Decide the `source_format` value using the manifest's `detect:` hint and the user's input:

- `pdf-text` — selectable-text PDF. Default.
- `scanned-pdf` — image-only or OCR-required PDF.
- `html` — publisher or preprint HTML page.
- `doi-arxiv` — a bare DOI or arXiv link that must be resolved first.
- `pasted-text` — pasted prose or notes with no retrievable original layout.

State the detected value in one short line to the user before processing, so they can correct you cheaply. A source may map to more than one value (for example a DOI that resolves to a PDF); load the resolution fragment first, then the fragment for the resolved artifact.

### 3. Load the matching fragment(s)

Read the file mapped for the detected `source_format`. Do **not** read every fragment in `static/`. Load only what step 2 selected.

### 4. Build the reader using the loaded material

Apply the loaded fragments in this priority order:

1. Core principles (`core/principles.md`) — bilingual reader by default, translate for meaning, never degrade to a summary, copyright caution.
2. Source-format fragment — how to extract text, figures, and tables for this input.
3. Reading workflow (`core/workflow.md`) — the six-step source-map-first process.
4. Output contract (`core/output-contract.md`) — required files and the pre-response verification checklist.

Build the Terminology Ledger as you translate (`../nature-shared/core/terminology-ledger.md`); it becomes the `paper.md` recurring-term table and the `source_map.json` glossary.

If constraints prevent full processing, still create a draft reader and label missing pages, figures, or low-confidence crops in `translation_notes.md`. Do not switch to summary mode.

### 5. Reach for references only when needed

The files under `references/` are deep references, not defaults. Open them on demand per the `references.on_demand` table in the manifest:

- detailed figure/table cropping and placement → `references/figure-extraction.md`.
- exact field schema for `paper.md` / `source_map.json` → `references/output-spec.md`.
- equations, mathematical expressions, chemical formulae, or image-only formulae → `references/equation-handling.md`.
- answering follow-up questions with source citations → `references/grounding-rules.md`.
