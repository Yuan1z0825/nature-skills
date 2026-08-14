---
name: nature-figure
description: >-
  Create, revise, audit, and export submission-grade scientific figures for Nature-family and other high-impact venues in Python (matplotlib/seaborn) or R (ggplot2/patchwork/ComplexHeatmap), including multi-panel plots, figures4papers-style work, and journal-ready SVG/PDF/TIFF outputs. Use for paper or scientific plots, manuscript data visualization, 论文配图、学术写作配图、科研绘图、科研作图、画图、作图、出图、论文图表、可视化. Define the conclusion, evidence logic, data integrity, template compatibility, export needs, and reviewer risks before plotting; honor or persist the Python/R backend choice. Also use the separate OpenRouter GPT Image 2 route for explicit AI-generated graphical abstracts, mechanism diagrams, concept schematics, 论文示意图、机制示意图、图形摘要; this route skips backend choice and treats outputs as drafts. Do not use for interactive dashboards, statistics-only analysis, data cleaning, literature review, code debugging, pure photo editing, or Illustrator/Figma-first infographics without manuscript-figure intent.
---

# Nature Figure Making — Router

This skill is split into two layers:

- A **static layer** under `static/` that holds versioned, reusable content fragments (the figure contract and default stance, plus a per-backend quick-start for Python and R).
- A **dynamic layer** (this file plus `manifest.yaml`) that detects the plotting backend and loads only the fragment needed for the current job. The large design, API, pattern, and QA material lives in on-demand references.

Do not try to apply the figure logic from memory or from this router. Always load fragments from disk as described below.

## Routing protocol

Follow these steps every time the skill is invoked.

### 0. Check for the OpenRouter AI-schematic route

If the user explicitly asks to generate a manuscript schematic, graphical abstract, mechanism diagram, concept illustration, or paper schematic with OpenRouter, GPT Image 2, an image-generation API, or similar wording, do **not** ask "Python or R?". This is a non-plotting AI-schematic route.

For this route:

1. Read [manifest.yaml](manifest.yaml) and the `always_load` files.
2. Read [references/openrouter-image-generation.md](references/openrouter-image-generation.md).
3. Use [scripts/generate_openrouter_schematic.py](scripts/generate_openrouter_schematic.py) when the user wants a real API call or a reproducible payload.
4. Treat output as a draft schematic / graphical abstract, not as a quantitative data panel. Do not invent experimental values, author logos, institutional marks, or unsupported mechanisms.

Only continue to the Python/R backend gate for plotting, charting, data visualization, or manuscript figure assembly tasks that are not explicit OpenRouter AI image-generation requests.

### 1. Load the manifest and the core layer

Read [manifest.yaml](manifest.yaml). It declares the `backend` axis, the allowed values, and the file paths each value maps to.

Also read every file listed under `always_load` (`static/core/contract.md` and `static/core/stance.md`). These hold the figure contract, the backend gate, the missing-runtime rule, the privacy rule, and the default operating stance that apply to every figure job.

### 2. Resolve the backend — a blocking gate

Backend selection blocks plotting tasks, but it should not annoy the same user forever. Decide the `backend` value in this order:

1. If the current request explicitly chooses Python or R, use that backend and save it with `scripts/nature_figure_backend.py set python` or `scripts/nature_figure_backend.py set r`.
2. If the request provides a clearly language-specific input file/workflow, use that backend and save it.
3. Otherwise run `scripts/nature_figure_backend.py get`. If it returns `python` or `r`, use the saved preference.
4. If no saved preference exists, ask exactly one concise question — **Python or R? I will remember this as your default.** — and stop. After the user answers, save the answer before proceeding.

- `python` — matplotlib / seaborn.
- `r` — ggplot2 / patchwork / ComplexHeatmap.

Do not guess or choose a backend by aesthetics alone. Only recommend a backend when the user explicitly asks you to choose; then use `references/backend-selection.md`, state the reason, save the selected backend, and proceed. Once selected, the backend is **exclusive** for all drawing, previewing, exporting, and visual QA (see `core/contract.md`). This gate does not apply to the explicit OpenRouter AI-schematic route above.

### 3. Load the matching backend fragment

After the backend is resolved, Read the mapped fragment (`static/fragments/backend/python.md` or `static/fragments/backend/r.md`). It carries the backend-only execution rule and the publication quick-start (rcParams/theme and export helper). Do **not** load the other backend's fragment.

### 4. Build the figure using the loaded material

Apply the loaded material in this order:

1. Figure contract (`core/contract.md`) — write the core conclusion, map the evidence chain, classify the archetype, set the journal/export contract, before any code.
2. Default stance (`core/stance.md`) — archetype-first composition, hero panel, restrained palette, statistics/integrity as part of the figure.
3. Backend fragment — the exclusive Python or R quick-start and execution rule.
4. Template adaptation — when reusing built-in original examples, licensed external material, or user-provided plotting code, load `references/asset-adaptation.md` before mapping data or changing the script.
5. Delivery preflight — before final delivery, load `references/qa-contract.md`, run `scripts/validate_figure.py` on the plotting source, run `scripts/audit_pdf_text.py` on the exported PDF, then inspect every panel and the complete figure at final physical size. Automated checks do not replace the panel-by-panel uncertainty, salience, spacing, and collision audit.

When the target is the flagship journal Nature, also load
`references/nature-article-requirements.md`. It separates initial-review files
from accepted-in-principle main and Extended Data production contracts and owns
the flagship legend limit.

When the target is Nature Machine Intelligence, instead load
`../nature-shared/journal-formats/nature-machine-intelligence.md`. Apply its
combined six-item main display budget, ten-item Extended Data maximum,
initial-versus-production boundary, 300-dpi/180-mm production checks and source-
data contract. NMI's current live pages do not assign a standalone per-legend
number, but its official 2018 brief guide set a historical advisory ceiling of
fewer than 300 English words per complete figure legend. Count the whole legend,
not each panel; aim for 150–250 words and keep it below 300 unless the live
submission system or editor gives a newer instruction. Do not import flagship
Nature's limit.

The chart serves the scientific logic; aesthetic polish is subordinate to making the core conclusion clear, defensible, and reviewable.

### 5. Reach for references only when needed

The files under `references/` are deep references, not defaults. Open them on demand per the `references.on_demand` table in the manifest — for example `references/figure-contract.md` to build the contract, `references/asset-adaptation.md` to reuse a plotting template safely, `references/template-catalog.md` for validated Python CSV templates, `references/api.md` for the Python palette and numerical/layout safety helpers, `references/r-workflow.md` for R, `references/design-theory.md` for color/typography/export rationale, `references/common-patterns.md` and `references/chart-types.md` for layout/chart recipes, `references/nature-2026-observations.md` for real Nature page archetypes, `references/qa-contract.md` before final delivery, `references/nature-article-requirements.md` for exact flagship Nature stage and upload rules, `../nature-shared/journal-formats/nature-machine-intelligence.md` for exact NMI figure rules, and `references/tutorials.md` / `references/demos.md` for worked examples.

Do not infer flagship Nature or NMI requirements from a Nature Communications
corpus or from the visual-style examples in this skill.

## Why this split

- The static layer is versioned and reviewable. The backend gate is now explicit in the manifest rather than buried in prose.
- The dynamic layer keeps each invocation cheap: only the selected backend's quick-start enters context, and the 2,600+ lines of reference depth load only when a step needs them.
- The router itself is short on purpose. Update fragments and references, not this file, when adding scope.
- This structure mirrors `nature-writing`, `nature-polishing`, `nature-reader`, and `nature-paper2ppt`.
