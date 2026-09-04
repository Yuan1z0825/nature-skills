# Figure Contract

Use this reference before writing plotting code. The goal is to make the figure
serve the paper's scientific logic.

## Contents

- [Privacy rule](#privacy-rule)
- [Required contract](#required-contract)
- [Core conclusion rules](#core-conclusion-rules)
- [Archetype selection](#archetype-selection)
- [Panel logic](#panel-logic)
- [Aesthetic integration](#aesthetic-integration)
- [Reviewer-risk prompts](#reviewer-risk-prompts)

## Privacy rule

Keep the figure contract user-facing, but keep the working trail private. Do not mention
private paths, source filenames, internal reference documents, template identifiers, or
where a private draft came from unless the user explicitly asks for provenance.

## Required contract

Create a short contract in working notes or in the response:

```text
Core conclusion:
Results-level question:
Figure archetype:
Target journal/output:
Backend: Python or R
Final size:
Panel map:
  a:
  b:
  c:
Evidence hierarchy:
  hero evidence:
  validation evidence:
  controls/robustness:
Statistics needed:
Source data needed:
Image-integrity notes:
Reviewer risk:
```

Do not start from a favorite template. Start from the conclusion, then choose the
minimum set of panels that make the conclusion clear and defensible.

Do not start by mapping each input table to a figure. First group tables, metrics,
and experiments by the scientific claims they can support. Several source tables
may belong in one evidence chain, while one table may support multiple distinct
panels. This claim-first pass prevents redundant figures that restate the same result.

## Core conclusion rules

- The core conclusion should be one sentence with a verb: "Treatment X reduces
  Y by restoring Z", not "Treatment results".
- Every panel must answer a unique question. If covering a panel would not weaken
  the argument, remove or merge it.
- Separate primary evidence from supporting evidence. The primary evidence gets
  the hero panel or the clearest axis; controls and robustness panels should be
  visually quieter.
- If the user provides data but no claim, infer a provisional claim from the data
  request. Confirm only an unresolved interpretive claim that materially changes the final figure; continue independent data checks and layout preparation while waiting. Do not add unsupported causal claims.
- If observations are matched by dataset, subject, seed, task, or specimen, decide
  whether the claim concerns the paired change. Marginal distributions can overlap
  because of between-unit heterogeneity even when paired differences are consistent.

## Archetype selection

| Archetype | Use when | Hero panel | Supporting panels |
|---|---|---|---|
| `quantitative grid` | The claim is mainly numerical comparison | Optional; often a dominant summary metric | Shared axes, aligned scales, compact legends |
| `schematic-led composite` | A workflow, mechanism, device, or experimental design must be understood first | Left or top schematic, 35-60% of area | 2-4 quantitative validation panels |
| `image plate + quant` | Microscopy, imaging, histology, spatial overlays, segmentation, or blots lead the evidence | Image plate or representative image | Scale bars, overlays, crops, quantification |
| `asymmetric mixed-modality figure` | The figure combines schematic, raster images, heatmaps, and quantitative plots | One panel spans rows/columns | Smaller panels ranked by evidence value |

## Panel logic

For a labelled multi-panel manuscript figure, load
`multipanel-evidence-architecture.md`. Use `one figure = one major claim` as a
strong planning default. Panels should be different necessary sentences in the
same visual argument, not parallel mini-stories or the same comparison mirrored
across several metrics.

Use this order unless the manuscript story clearly requires another:

1. Establish the system: sample, method, cohort, device, or experimental design.
2. Show the main effect or primary comparison.
3. Show mechanism or localization.
4. Quantify the representative image or qualitative observation.
5. Add robustness, controls, subgroup analysis, or sensitivity analysis.

For Fig. 1 or a method figure, the first panel often defines the visual vocabulary:
colors, symbols, workflow direction, sample classes, and scale. Reuse that vocabulary
through the whole figure and, where possible, through the manuscript.

## Aesthetic integration

- Use one neutral family, one signal family, and one accent family.
- Keep the same condition/method color across all panels.
- Prefer direct labels for stable line identities, channels, and fixed spatial regions.
- Use a shared legend area when repeated legends would waste space.
- Avoid equal-sized panels when the evidence is not equally important.
- Keep schematic colors and quantitative plot colors related. A schematic-led
  figure should look like one integrated argument, not a pasted collage.

## Reviewer-risk prompts

Before finalizing, ask what a skeptical reviewer would challenge:

- Is the sample size visible in the legend or source data?
- Are error bars, intervals, and statistical tests defined?
- Are the same uncertainty definitions present in every comparable aggregate panel?
- Are axes comparable across panels that invite comparison?
- Would a paired-difference view reveal an effect hidden by overlapping marginal distributions?
- Does each legend label preserve canonical capitalization and match the terminology plan?
- Do data labels clear the upper uncertainty extent at final rendered size?
- Are representative images quantified and traceable to raw files?
- Are image adjustments global and documented?
- Could the same conclusion be made from fewer panels?
