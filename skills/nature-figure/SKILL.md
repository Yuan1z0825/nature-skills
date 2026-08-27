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

### 0. Check for graphical-abstract and AI-schematic routes

For every graphical-abstract planning, generation, revision, or audit task that
uses AI, read
[references/ai-graphical-abstract-workflow.md](references/ai-graphical-abstract-workflow.md)
first. It owns the message/audience brief, composition and palette workflow,
policy gate, human scientific review, disclosure boundary, and provenance
requirements. A Nature Careers article is practitioner advice, not submission
clearance; verify the current official policy for the exact target journal.

If the request is planning or auditing only, do not ask for Python or R unless
the user also asks to render or revise a data-driven figure.

If the user explicitly asks to generate a manuscript schematic, graphical abstract, mechanism diagram, concept illustration, or paper schematic with OpenRouter, GPT Image 2, an image-generation API, or similar wording, do **not** ask "Python or R?". This is a non-plotting AI-schematic route.

For this route:

1. Read [manifest.yaml](manifest.yaml) and the `always_load` files.
2. Read [references/ai-graphical-abstract-workflow.md](references/ai-graphical-abstract-workflow.md).
3. Read [references/openrouter-image-generation.md](references/openrouter-image-generation.md).
4. Use [scripts/generate_openrouter_schematic.py](scripts/generate_openrouter_schematic.py) when the user wants a real API call or a reproducible payload.
5. Treat output as a draft schematic / graphical abstract, not as a quantitative data panel. Do not invent experimental values, author logos, institutional marks, or unsupported mechanisms. Keep internal usefulness separate from submission eligibility.

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
2. Multi-panel evidence architecture — when planning, restructuring, or auditing a labelled multi-panel figure, load `references/multipanel-evidence-architecture.md`. Make the figure answer one Results-level scientific question; assign panels different inferential roles, not merely different metrics. When figure order must follow the manuscript argument, also load `../nature-shared/core/nature-results-discussion.md`.
3. Default stance (`core/stance.md`) — archetype-first composition, hero panel, restrained palette, statistics/integrity as part of the figure.
4. Backend fragment — the exclusive Python or R quick-start and execution rule.
5. Template adaptation — when reusing built-in original examples, licensed external material, or user-provided plotting code, load `references/asset-adaptation.md` before mapping data or changing the script.
6. Rendered QA and delivery preflight — load `references/qa-contract.md`, run the render-time panel-alignment gate for every multi-panel figure, `scripts/validate_figure.py` on the plotting source, `scripts/audit_pdf_text.py` on the exported PDF, and `scripts/audit_figure_collisions.py` on the same final PDF. Then inspect every panel and the complete figure at final physical size. Automated checks do not replace the panel-by-panel uncertainty, salience, spacing, and ambiguity audit.

For every figure containing two or more comparable panels, measure the **final
rendered plot-area rectangles** before export and preserve the alignment JSON.
Python figures must call `require_matplotlib_panel_alignment()` from
`scripts/audit_panel_alignment.py` after the final layout draw. R/patchwork
figures must source `scripts/panel_alignment.R`, write the patchwork layout
manifest at the final export dimensions, and run the same backend-neutral JSON
auditor. Use a default physical tolerance of `1.5 pt` for shared edges, widths,
heights, panel-label anchors and repeated gutters. `FIX BEFORE DELIVERY` or exit
code `1` blocks export; `NOT AUDITABLE` or exit code `2` blocks any claim that
alignment passed. A horizontal row of three or four equal-grid-span panels must
have equal final plot-area widths as well as equal heights and gutters; an
intentional unequal-width design requires a recorded `panel-width` exemption.
Structured unequal-span grids—including two stacked panels
beside one panel spanning both rows, in either column—must be inferred from
shared grid start/stop boundaries and checked automatically. Nested grids,
free-positioned hero panels, insets and colorbars may be excluded only through
explicit comparable groups or a recorded exemption with a reason. Do not
weaken the global tolerance to hide one intentional exception.

After every generated or revised Python/R scientific figure, export the final
PDF and run the collision audit again; this is mandatory after any change to
data geometry, text, fonts, legends, annotations, axes, error bars, panel size
or layout, not only at final submission. Use:

```bash
python skills/nature-figure/scripts/audit_figure_collisions.py figure.pdf \
  --json-out figure.collision-audit.json \
  --overlay-pdf figure.collision-audit.pdf
```

- `FIX BEFORE DELIVERY` or exit code `1`: repair the figure, re-export with the
  selected plotting backend, and rerun all rendered QA.
- `REVIEW REQUIRED`: inspect every WARN at final physical size; record why an
  intentional overlay is acceptable. Use `--strict` when WARN must block.
- `NOT AUDITABLE` or exit code `2`: report the dependency/PDF blocker and do not
  claim collision validation. Install `requirements.txt` when PyMuPDF is absent.

The collision audit reads PDF geometry for both Python and R output. It does not redraw
the scientific figure or authorize cross-backend plotting. Its optional marked
PDF is a QA-only diagnostic artifact and must never replace the selected
backend's source or submission files.

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

The files under `references/` are deep references, not defaults. Open them on demand per the `references.on_demand` table in the manifest — for example `references/figure-contract.md` to build the contract, `references/multipanel-evidence-architecture.md` to turn one Results-level question into complementary panel roles and a claim-escalating figure sequence, `references/asset-adaptation.md` to reuse a plotting template safely, `references/template-catalog.md` for validated Python CSV templates, `references/api.md` for the Python palette and numerical/layout safety helpers, `references/r-workflow.md` for R, `references/design-theory.md` for color/typography/export rationale, `references/common-patterns.md` and `references/chart-types.md` for layout/chart recipes, `references/nature-2026-observations.md` for real Nature page archetypes, `references/qa-contract.md` before final delivery, `references/nature-article-requirements.md` for exact flagship Nature stage and upload rules, `../nature-shared/journal-formats/nature-machine-intelligence.md` for exact NMI figure rules, `references/ai-graphical-abstract-workflow.md` for AI-assisted graphical-abstract planning, policy gating, human verification, and provenance, and `references/tutorials.md` / `references/demos.md` for worked examples.

Do not infer flagship Nature or NMI requirements from a Nature Communications
corpus or from the visual-style examples in this skill.

## Why this split

- The static layer is versioned and reviewable. The backend gate is now explicit in the manifest rather than buried in prose.
- The dynamic layer keeps each invocation cheap: only the selected backend's quick-start enters context, and the 2,600+ lines of reference depth load only when a step needs them.
- The router itself is short on purpose. Update fragments and references, not this file, when adding scope.
- This structure mirrors `nature-writing`, `nature-polishing`, `nature-reader`, and `nature-paper2ppt`.
