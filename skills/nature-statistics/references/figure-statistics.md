# Figure statistics and legend alignment

Use this file when checking figure panels, legends, star labels, error bars, source data, or statistical annotations.

## Legend information each quantitative panel should provide

For each panel or panel group, check whether the legend states:

- what points, bars, boxes, lines, or shaded regions represent
- the exact definition of `n`
- whether `n` is independent samples, animals, donors, patients, cultures, experiments, simulations, fields, cells, or technical replicates
- summary convention: mean ± s.d., mean ± s.e.m., median with IQR, min-max, confidence interval, or model estimate
- test/model used
- paired/unpaired or repeated-measures status if relevant
- multiple-comparison correction if multiple contrasts are displayed
- exact p values or star thresholds
- whether source data include raw independent values or only summary values

## Plot-type checks

### Bar plots

Risk:
- Bars can hide sample size and distribution.

Fix:
- Prefer showing individual independent data points when feasible.
- If bars remain, require error-bar definition and panel-specific `n`.

### Box plots

Require:
- median line, box bounds, whisker rule, outlier display rule, and `n`.

### Violin plots

Require:
- what points represent, kernel/density caveat if relevant, and independent-unit definition.
- Avoid making dense cell-level violins look like many independent experiments.

### Time courses

Require:
- whether the same units are followed over time.
- Use repeated-measures or mixed models when inference uses all time points from the same unit.

### Heat maps / omics panels

Require:
- normalization, scaling, clustering distance/linkage if used, multiple-testing or FDR treatment for highlighted features, and whether rows/columns are selected post hoc.

### Regression / correlation panels

Require:
- correlation coefficient or model coefficient, uncertainty if available, sample size, independence of points, and whether the fit is descriptive or inferential.

## Star notation

Avoid legends that only say:

```text
*P < 0.05, **P < 0.01, ***P < 0.001
```

Prefer:

```text
Symbols indicate adjusted p values from AUTHOR_INPUT_NEEDED test with AUTHOR_INPUT_NEEDED correction for the comparisons shown: *p < 0.05, **p < 0.01, ***p < 0.001. Exact p values and sample sizes are provided in Source Data. n denotes independent AUTHOR_INPUT_NEEDED.
```

Only use this after the relevant facts are supplied.

## Source-data notes

Ask whether source data should include:

- raw independent-unit values behind summary panels
- exact p values and test statistics
- sample-size table per panel
- excluded-data notes if any
- code or script used to produce the panel, where central to the claims

## Figure audit output mini-format

```text
Figure statistics audit
- Panel:
- Current legend problem:
- Risk:
- Required fix:
- Suggested legend text:
```
