# QA Contract

## Contents

- [Current official references to verify](#current-official-references-to-verify)
- [Pre-submission checklist](#pre-submission-checklist)
- [Statistics legend minimum](#statistics-legend-minimum)
- [Image-integrity minimum](#image-integrity-minimum)
- [Automated source preflight](#automated-source-preflight)
- [Rendered panel-by-panel audit](#rendered-panel-by-panel-audit)
- [Typography and PDF glyph floor](#typography-and-pdf-glyph-floor)
- [Uncertainty consistency](#uncertainty-consistency)
- [Geometry and annotation placement](#geometry-and-annotation-placement)
- [Color separation and salience](#color-separation-and-salience)
- [Transformation and paired-effect checks](#transformation-and-paired-effect-checks)
- [Export checks](#export-checks)


Use this before final delivery, before a revision package, and whenever the figure
contains microscopy, blots, gels, clinical subgroup analysis, or statistical claims.
Journal rules change, so verify the latest target journal author guide for final
submission. The values below are conservative defaults for Nature-family style work.
For the flagship journal Nature, load `nature-article-requirements.md` and use
its stage-specific main-figure, Extended Data and legend contracts.

## Current official references to verify

- Nature research figure guide: `https://research-figure-guide.nature.com/`
- Nature building/exporting panels: `https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/`
- Nature preparing figures/specifications: `https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/`
- Nature initial submission and statistics guidance: `https://www.nature.com/nature/for-authors/initial-submission`
- Nature formatting guide: `https://www.nature.com/nature/for-authors/formatting-guide`
- Journal of Cell Biology figure/video guidelines for microscopy-oriented image QA: `https://rupress.org/jcb/pages/fig-vid-guidelines`
- Elsevier/Cell-family image-manipulation baseline: `https://www.sciencedirect.com/journal/the-cell-surface/publish/guide-for-authors`

## Pre-submission checklist

| Check | Pass condition |
|---|---|
| Core conclusion | One-sentence claim exists and every panel maps to it |
| Archetype | Figure has a declared archetype and panel hierarchy |
| Backend exclusivity | The selected backend produced all plotting, previews, exports, and visual QA renders |
| Final size | Single-column about 89 mm or double-column about 183 mm, height not above target journal limit |
| Text size | Body/tick/legend text is readable at final size, usually 5-7 pt for dense journal figures |
| Rendered glyph floor | Every PDF text run, including math superscripts/subscripts, is at least 5 pt |
| Panel labels | Lowercase, bold, near top-left, typically 8 pt at final size |
| Editable text | SVG/PDF text remains editable; no outlined text unless unavoidable for special symbols |
| Font | Arial/Helvetica/sans-serif fallback is used consistently |
| Color | No rainbow color maps; red/green is not the only encoding; grayscale print remains interpretable |
| Legend strategy | Shared or direct labels where possible; no repeated redundant legends |
| Display terminology | Legend labels use display-style initial capitalization and preserve canonical model names |
| Statistics | `n`, biological/technical repeat definition, center, spread, test, correction, and exact comparison are documented |
| Comparable uncertainty | Every comparable seed/fold/split aggregate panel shows the same variability definition or documents an exemption |
| Annotation clearance | Labels clear points, curves, bars, and uncertainty extents at final size without opaque masking |
| Visual hierarchy | Hero evidence remains more salient than neutral baselines after rendering |
| Numerical transforms | Interpolation/normalization direction and monotonicity assumptions are asserted in code |
| Source data | Quantitative panels can be traced to a clean CSV/TSV/XLSX or script output |
| Raster resolution | Photos/microscopy are high-resolution enough for final size; line art uses vector where possible |
| Microscopy scale | Scale bar is present, calibrated, and not only a magnification factor |
| Image integrity | Crop, contrast, pseudo-color, stitching, reuse, and raw-file provenance are recorded |
| Export bundle | Script, source data, SVG, PDF, TIFF/PNG preview, and QA notes are delivered together when requested; previews are not mislabeled as accepted main-figure upload formats |

## Statistics legend minimum

For each quantitative panel, capture:

```text
n definition:
biological replicates:
technical replicates:
center statistic:
spread/interval:
test:
multiple-comparison correction:
p-value display:
source-data file:
```

For machine-learning/model figures, also capture:

```text
train/validation/test split:
number of seeds or folds:
metric definition:
confidence interval or variability definition:
baseline definition:
```

## Image-integrity minimum

For each image panel, capture:

```text
raw file:
processed file:
crop:
brightness/contrast/gamma:
pseudo-color:
scale calibration:
stitching:
reuse in other figures:
quantification link:
```

Global adjustments are generally safer than local selective edits. If an adjustment
changes the visibility of relevant background or bands, flag it instead of silently
normalizing it away.

## Automated source preflight

Run the dependency-free validator on the final plotting source before rendering the delivery bundle:

```bash
# Python source
python skills/nature-figure/scripts/validate_figure.py path/to/figure.py

# R, R Markdown, or Quarto source
python skills/nature-figure/scripts/validate_figure.py path/to/figure.R

# Machine-readable report or stricter warning gate
python skills/nature-figure/scripts/validate_figure.py path/to/figure.py --json
python skills/nature-figure/scripts/validate_figure.py path/to/figure.py --strict

# Exported-PDF glyph-size audit
python skills/nature-figure/scripts/audit_pdf_text.py path/to/figure.pdf --min-pt 5
python skills/nature-figure/scripts/audit_pdf_text.py path/to/figure.pdf --min-pt 5 --json
```

The source preflight checks syntax, font configuration and size floor, mathtext shrinkage risk, literal legend-label capitalization, unsafe color maps, editable-text settings, vector/raster exports, DPI, common journal widths, potential sampling or unreported missing-data exclusion, simulated-data leakage, log guards, interpolation monotonicity, stochastic uncertainty encoding, rotated-text anchoring, risky annotation workarounds, and obvious cross-backend plotting references. The PDF audit scans supported content streams for actual `Tf` font-size operators and catches reduced script glyphs that source-level `fontsize` checks miss.

Treat the result as a deterministic source audit, not as evidence that the analysis or rendered figure is correct. Resolve all `FAIL` findings before delivery. Review every `WARN`, then run the selected backend and inspect the actual SVG/PDF/TIFF/PNG outputs at final size. A warning may be acceptable only when the QA notes state the reason.

## Rendered panel-by-panel audit

Do not approve a figure from a whole-page glance. Inspect each panel at final physical size, then inspect the assembled figure. Record one row per panel:

| Panel | Unique claim | Center/summary | Spread/interval | Replicate unit | Labels/legend | Collision check | Pass |
|---|---|---|---|---|---|---|---|
| a | What question only this panel answers | mean/median/raw | SD/SE/CI/none + reason | seeds/folds/subjects/etc. | exact display labels | data + error extent + text bbox | yes/no |

Cover each panel mentally. If the figure's argument remains complete, merge or remove that panel. Compare repeated panels side by side for consistent terminology, uncertainty, axes, and color mapping. After adding error bars or uncertainty bands, remove arrows, brackets, or fills that encode the same gap and occupy the same geometry.

## Typography and PDF glyph floor

- The 5 pt floor applies to every rendered glyph, not only the parent `fontsize` in source code.
- Matplotlib mathtext commonly scales superscripts/subscripts to about 0.7 of the parent. A 7 pt `$R^2$` can therefore contain a 4.9 pt glyph. Prefer a Unicode glyph such as `R²` when it preserves the intended notation, or increase the parent size and confirm the PDF audit.
- Measure long labels against their allocated group width at final size. Compare rendered text bounding-box width in millimetres with the available slot; do not rely on the source font number alone.
- Keep canonical capitalization such as `XGBoost`, `DeepSeek`, `GPT-5.2`, and `RF`. Legend labels start with display-style capitalization, while prose follows normal sentence grammar. Do not use blind string title-casing.

## Uncertainty consistency

- If a line or bar is a mean/median across random seeds, folds, splits, subjects, or repeated experiments, encode the requested spread in every comparable panel.
- State the exact definition, for example `median ± one seed SD`, in the legend or panel notes. Do not infer or invent it.
- Presence of one `fill_between`, `errorbar`, `yerr`, or `geom_errorbar` call does not prove coverage. Use the panel audit table to verify every comparable panel.
- Recompute label clearance from the upper uncertainty extent after error bars are added.

## Geometry and annotation placement

- Measure spacing between the actual objects being compared. Use rendered/tight bounding boxes for panel-to-legend or legend-row gaps; scanning an entire raster row can mix unrelated objects at different horizontal positions.
- Derive label positions from data and uncertainty bounds, for example `max(center + spread) + margin`, rather than a fixed `LABEL_Y`.
- For rotated Matplotlib text, use `rotation_mode="anchor"` and verify the final bounding box.
- If a curve crosses a label, reposition the label beyond the local data envelope. Avoid opaque white `bbox` masks that cut a conspicuous hole in a line.
- Equal pixel y-coordinates can still look uneven when bar heights create unequal whitespace. Diagnose the perceived gap before moving already aligned labels.

## Color separation and salience

- Pairwise ΔE and white-background contrast are necessary checks, not a complete design test.
- Verify hierarchy after rendering: neutral baselines should not appear stronger than the proposed method or primary evidence.
- Do not repurpose a sequential light-to-dark palette as unrelated categorical colors merely because the hues look attractive.
- Check grayscale and color-vision robustness, then inspect the actual figure because metrics do not encode which series should dominate attention.

## Transformation and paired-effect checks

- `numpy.interp` requires increasing `xp`. Use `scripts/figure_safety.py::interp_monotone`, or explicitly assert monotonicity and reverse/sort `xp` and `fp` together. Plausible-looking output is not evidence of correctness.
- Do not plan one figure per source table. Group panels by the distinct claims they support.
- When repeated units are matched, inspect paired differences. Broad between-dataset or between-subject heterogeneity can make four marginal distributions overlap even when the within-unit effect is strong; use a paired-difference view when the scientific claim is paired.

## Export checks

Run only the export block for the selected backend. If that backend is unavailable,
stop and report the missing runtime/package instead of producing a substitute export
with the other language.

### Python

```python
import matplotlib as mpl
mpl.rcParams["svg.fonttype"] = "none"
mpl.rcParams["pdf.fonttype"] = 42
fig.savefig("figure.svg", bbox_inches="tight")
fig.savefig("figure.pdf", bbox_inches="tight")
fig.savefig("figure.tiff", dpi=600, bbox_inches="tight")
```

### R

```r
svglite::svglite("figure.svg", width = width_mm / 25.4, height = height_mm / 25.4)
print(plot)
dev.off()

grDevices::cairo_pdf("figure.pdf", width = width_mm / 25.4, height = height_mm / 25.4, family = "Arial")
print(plot)
dev.off()

ragg::agg_tiff("figure.tiff", width = width_mm / 25.4, height = height_mm / 25.4, units = "in", res = 600)
print(plot)
dev.off()
```

Open the SVG/PDF after export and verify that text can be selected, labels do not
overlap, and the figure still reads at final printed size.
