# Figure contract before plotting

A publication-quality scientific figure is a visual argument, not an isolated pretty plot. Every figure starts from a claim, an evidence hierarchy, and a review-risk check before code or aesthetics. Before generating or editing code, establish the contract below.

## Backend selection uses a saved preference

For plotting tasks, first honor an explicit Python/R choice in the current request or a clearly language-specific input file/workflow. Save that backend as the user's default with `scripts/nature_figure_backend.py set python` or `scripts/nature_figure_backend.py set r`.

If the current request does not specify a backend, check the saved preference with `scripts/nature_figure_backend.py get`. If it returns `python` or `r`, use that backend without asking again.

If no saved preference exists, ask one concise question: **Python or R? I will remember this as your default.** Then stop and wait for the user's answer. Do not generate mock data, write scripts, create figures, or choose Python/R by default before this first preference is established. After the user answers, save it and proceed.

Only recommend a backend when the user explicitly asks you to choose or recommend one. In that case, use `references/backend-selection.md`, state the reason, save the selected backend, and then proceed with the recommended backend.

## The selected backend is exclusive

Once Python or R is selected, every plotting script, preview image, SVG/PDF/TIFF/PNG export, QA render, and visual workaround must be produced by that same backend. Do not use Python to draw a preview for an R figure, and do not use R to draw a preview for a Python figure, even if the selected runtime or packages are missing locally. The non-selected language may only be used for non-visual file inspection or data conversion when it does not open a graphics device, import plotting libraries, create image/vector files, or change the final visual appearance.

The backend-neutral `audit_panel_alignment.py`, `audit_pdf_text.py` and
`audit_figure_collisions.py` tools may inspect a layout manifest or final PDF
from either backend. They do not redraw the scientific content. The selected
backend must measure its own final axes/grob geometry before the alignment JSON
is audited. Alignment and collision overlays are QA-only, not previews,
substitute exports or submission assets; keep the original selected-backend
figure authoritative.

## Missing runtime/package rule

After the backend is selected, check the selected runtime early (`Rscript`/R for R; Python and required plotting packages for Python). If the selected runtime or required packages are unavailable, stop before rendering and report the exact blocker. You may provide a selected-backend script and installation commands, or ask permission to install dependencies, but you must not fall back to the other language to make a substitute figure.

## Data-integrity gate

Use all user-provided observations and requested variables unless an exclusion has a scientific or statistical justification or the user explicitly requests a subset. Never reduce data merely to make a plot easier or faster to render. For large point clouds, prefer rasterized marks, hexbin/density representations, aggregation with a stated rule, or another backend-native rendering strategy.

If any row, column, replicate, image, or category is excluded, record the before/after counts, the exact rule, and the reason in the QA notes. Preserve the unmodified source data and never silently select convenient columns to satisfy a template.

Plan figures by scientific claims, not by source tables. Do not turn each table into a separate figure when several tables answer the same question. If an effect is defined within matched datasets, subjects, seeds, or tasks, inspect and visualize paired differences rather than relying only on overlapping marginal distributions; large between-unit heterogeneity can hide a strong paired effect.

## The five-point contract

1. **Core conclusion**: write the one-sentence claim the figure must defend and the Results-level scientific question it answers.
2. **Evidence chain**: map each planned panel to one distinct inferential role in that claim, and drop, merge, or demote panels that only redraw another panel's evidence or repeat it under a secondary metric.
3. **Archetype**: classify the figure as `quantitative grid`, `schematic-led composite`, `image plate + quant`, or `asymmetric mixed-modality figure`.
4. **Backend**: use the explicit or saved Python/R track exclusively for all figure drawing, previewing, exporting, and visual QA. Do not cross-render with the other language.
5. **Journal/export contract**: set final dimensions, a 5 pt floor for every rendered glyph, editable text, source data, statistics, image-integrity notes, export formats, a blocking multi-panel alignment gate, and automatic rendered collision QA before styling.

The highest-priority rule is: **the chart serves the scientific logic**. Aesthetic polish, template matching, and complex layout are subordinate to making the core conclusion clear, defensible, and reviewable.

For the full method to convert a request into core conclusion, evidence hierarchy, panel map, and review-risk checks, open `references/figure-contract.md`.
For a labelled multi-panel figure or a manuscript-level figure sequence, also
open `references/multipanel-evidence-architecture.md`: use one figure-level
claim as the planning default, give panels complementary evidence roles, and
align successive figures with the Results claim escalation.
