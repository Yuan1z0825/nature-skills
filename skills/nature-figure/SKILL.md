---
name: nature-figure
description: >-
  Submission-grade Nature/high-impact journal figure workflow for Python or R. Use whenever the user asks to create, revise, audit, or polish manuscript figures, multi-panel scientific plots, figures4papers-style matplotlib plots, or journal-ready SVG/PDF/TIFF outputs, especially for Nature-family or other high-impact journals. Before plotting, define the figure's conclusion, evidence logic, export needs, and review risks. If the user has not chosen Python or R, ask "Python or R?" and stop. Use only the selected backend for figure generation, previewing, exporting, and QA. Supports matplotlib/seaborn and ggplot2/patchwork/ComplexHeatmap. Not for dashboards or Illustrator/Figma-first infographics. Also trigger on general academic-writing figure needs even without the word "Nature", such as making figures/plots for a paper, scientific/academic plotting, data visualization for a manuscript, and Chinese phrasings like 论文配图、学术写作配图、科研绘图、科研作图、画图、作图、出图、论文图表、可视化.
version: 2.0.0
author: Community contribution, refactored into static/dynamic layers
---

# Nature Figure Making — Router

This skill is split into two layers:

- A **static layer** under `static/` that holds versioned, reusable content fragments (the figure contract and default stance, plus a per-backend quick-start for Python and R).
- A **dynamic layer** (this file plus `manifest.yaml`) that detects the plotting backend and loads only the fragment needed for the current job. The large design, API, pattern, and QA material lives in on-demand references.

Do not try to apply the figure logic from memory or from this router. Always load fragments from disk as described below.

## Routing protocol

Follow these five steps every time the skill is invoked.

### 1. Load the manifest and the core layer

Read [manifest.yaml](manifest.yaml). It declares the `backend` axis, the allowed values, and the file paths each value maps to.

Also read every file listed under `always_load` (`static/core/contract.md` and `static/core/stance.md`). These hold the figure contract, the backend gate, the missing-runtime rule, the privacy rule, and the default operating stance that apply to every figure job.

### 2. Resolve the backend — a blocking gate

Backend selection blocks everything else. Decide the `backend` value only from an explicit user choice or a clearly language-specific input file/workflow:

- `python` — matplotlib / seaborn.
- `r` — ggplot2 / patchwork / ComplexHeatmap.

If the user has **not** explicitly chosen, ask exactly one concise question — **Python or R?** — and stop. Do not default, guess, generate mock data, or write scripts before the answer. Only recommend a backend when the user explicitly asks you to choose; then use `references/backend-selection.md`, state the reason, and proceed. Once selected, the backend is **exclusive** for all drawing, previewing, exporting, and visual QA (see `core/contract.md`).

### 3. Load the matching backend fragment

After the backend is resolved, Read the mapped fragment (`static/fragments/backend/python.md` or `static/fragments/backend/r.md`). It carries the backend-only execution rule and the publication quick-start (rcParams/theme and export helper). Do **not** load the other backend's fragment.

### 4. Build the figure using the loaded material

Apply the loaded material in this order:

1. Figure contract (`core/contract.md`) — write the core conclusion, map the evidence chain, classify the archetype, set the journal/export contract, before any code.
2. Default stance (`core/stance.md`) — archetype-first composition, hero panel, restrained palette, statistics/integrity as part of the figure.
3. Backend fragment — the exclusive Python or R quick-start and execution rule.

The chart serves the scientific logic; aesthetic polish is subordinate to making the core conclusion clear, defensible, and reviewable.

### 5. Reach for references only when needed

The files under `references/` are deep references, not defaults. Open them on demand per the `references.on_demand` table in the manifest — for example `references/figure-contract.md` to build the contract, `references/api.md` for the Python palette and helpers, `references/r-workflow.md` for R, `references/design-theory.md` for color/typography/export rationale, `references/common-patterns.md` and `references/chart-types.md` for layout/chart recipes, `references/nature-2026-observations.md` for real Nature page archetypes, `references/qa-contract.md` before final delivery, and `references/tutorials.md` / `references/demos.md` for worked examples.

## Why this split

- The static layer is versioned and reviewable. The backend gate is now explicit in the manifest rather than buried in prose.
- The dynamic layer keeps each invocation cheap: only the selected backend's quick-start enters context, and the 2,600+ lines of reference depth load only when a step needs them.
- The router itself is short on purpose. Update fragments and references, not this file, when adding scope.
- This structure mirrors `nature-writing`, `nature-polishing`, `nature-reader`, and `nature-paper2ppt`.
