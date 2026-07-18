# `nature-figure` Skill

[中文说明](README.md)

`nature-figure` designs, generates, and audits submission-grade scientific figures for Nature-series papers, high-impact journals, manuscript panels, mechanism schematics, and graphical-abstract drafts.

## What To Use It For

- Generate Python / R plotting scripts and editable figures from data, legends, or manuscript claims.
- Redraw existing figures into clearer multi-panel manuscript figures.
- Plan Figure 1, mechanism diagrams, workflows, graphical abstracts, or supplementary figures.
- Check panel labels, color, typography, statistical annotations, source data, and export formats.
- When explicitly requested, call `openai/gpt-image-2` through the OpenRouter Images API to draft AI concept schematics.

## Workflow

Start with a figure contract rather than a template:

- Core conclusion: what the figure must demonstrate.
- Evidence hierarchy: which panels are primary evidence and which are explanatory.
- Figure prototype: scatter, box plot, heatmap, mechanism diagram, workflow, multi-panel composition, and so on.
- Backend choice: Python or R; the first choice can be reused as the default preference.
- Data integrity: preserve all observations and requested variables by default, and record every exclusion rule with before/after counts.
- Template compatibility: compare scientific meaning, data shape, and transform constraints before exact reuse, structural adaptation, or style-only inheritance.
- Submission constraints: size, typography, color, resolution, vector format, and source-data traceability.

## Typical Requests

- "Make a Nature-style multi-panel figure from this dataset, preferably in Python."
- "Use the figures4papers Nature Machine Intelligence layout as a reference and add a method-comparison figure."
- "Redraw this mechanism schematic, export SVG/PDF, and give me the source-data table."
- "Use OpenRouter to draft a graphical abstract, but do not treat it as a quantitative data figure."

## Example Preview

| Direction | Preview | Reusable Pattern |
|-----------|---------|------------------|
| Multi-panel manuscript figure | <a href="assets/gallery/fig1-material-mechanism-rich.png"><img src="assets/gallery/fig1-material-mechanism-rich.png" width="220" alt="Material design and physical validation"></a> | Mechanism schematic, image panels, quantitative results, and correlation in one evidence chain |
| Chart-type atlas | <a href="assets/chart-atlas/atlas-03-heatmaps.png"><img src="assets/chart-atlas/atlas-03-heatmaps.png" width="220" alt="Heatmap atlas"></a> | Heatmaps, annotation matrices, cluster blocks, and diverging color scales |
| figures4papers demo | <a href="assets/figures4papers/figure_VIGIL/figures/comparison_radar.png"><img src="assets/figures4papers/figure_VIGIL/figures/comparison_radar.png" width="220" alt="VIGIL comparison radar"></a> | Layout, legend, and multi-metric comparison grammar from real paper scripts |

## What You Need To Provide

- Raw data, existing figure, legend, manuscript claim, or intended mechanism.
- Target journal, single-column / double-column size, output format, and whether source data is required.
- Python / R preference; if absent, the skill asks or reuses the local preference.

## Outputs

- Runnable Python or R plotting script.
- SVG/PDF/TIFF/PNG figure files, with editable vector output preferred.
- Panel notes, source-data mapping, exclusion counts, and a pre-submission QA record.
- For AI-schematic tasks, a concept draft and a list of elements that need human redrawing or verification.

## Built-In References

- `references/api.md`: Python palette, style, and plotting-helper conventions.
- `references/asset-adaptation.md`: semantic matching, field mapping, and data-integrity rules for templates.
- `references/template-catalog.md`: validated Python CSV templates for volcano, ROC, marker dot plot, marginal, and paired figures.
- `references/chart-types.md`: chart selection and visual rules.
- `references/demos.md`: `figures4papers` demos and reusable patterns.
- `references/qa-contract.md`: export QA, source-data constraints, and static-preflight entry points.
- `scripts/validate_figure.py`: reproducible static QA for Python and R plotting source.
- `assets/figures4papers/`: packaged demo scripts and previews.

## Boundaries

- AI-generated images are not treated as real experimental results or quantitative data panels.
- The skill does not invent statistical tests, sample sizes, error-bar meanings, or experiment conditions.
- The skill does not silently sample for rendering convenience, ignore requested variables, or remove incomplete observations.
- Private templates can be used locally, but user-facing outputs should not expose private paths, filenames, or sources.

## Related Skills

- `nature-statistics`: check statistical annotations, n definitions, and p-value wording.
- `nature-writing`: align figure conclusions with manuscript narrative.
- `nature-paper2ppt`: turn manuscript figures into presentation slides.

## Relationship With Other Skills

- If the core task is statistical interpretation, sample-size definition, or significance wording, let `nature-statistics` audit the text before returning to `nature-figure`.
- If the figure is finished but the user needs the claim written into an abstract, introduction, or results section, hand off to `nature-writing`.
- If the figure should become a lab meeting deck or presentation slide, hand off to `nature-paper2ppt`.
- `nature-figure` is responsible for the figure itself; it does not replace statistical review or manuscript narration.
