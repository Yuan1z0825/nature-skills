# Statistical reporting checklist

Use this file when drafting or auditing a Statistical analysis, Methods, Results, or Supplementary Methods section.

## Minimum information to extract

For each major analysis, identify:

- endpoint or response variable
- experimental groups / conditions
- independent experimental unit
- biological replicates and technical replicates
- repeated measures, paired observations, blocks, batches, sites, donors, animals, patients, plots, or model runs
- inclusion / exclusion criteria
- missing-data handling
- randomization and blinding, if applicable
- transformation or normalization
- test or model name
- assumptions checked or rationale for robust / nonparametric approach
- multiple-comparison correction or planned-comparison rationale
- reported estimate, uncertainty interval, p value, and sample size
- software, package, and version when available

## Statistical analysis paragraph structure

A clean manuscript paragraph usually follows this order:

1. **Software and environment**
   - Name software and packages when supplied.
   - Do not invent versions.

2. **Data summary convention**
   - State whether values are mean ± s.d., mean ± s.e.m., median with interquartile range, box-plot convention, or another summary.

3. **Sample-size and replication definition**
   - Define `n` for each experiment class.
   - Distinguish independent samples from technical readings or submeasurements.

4. **Test/model choice**
   - State which comparisons used which tests or models.
   - Explain paired vs unpaired, parametric vs nonparametric, repeated-measures or mixed-effects models where relevant.

5. **Multiplicity strategy**
   - State the family of comparisons and correction method, or explain that tests were prespecified and limited.

6. **Thresholds and exact reporting**
   - Use exact p values where possible.
   - If thresholds are used, define them and avoid star-only reporting.

7. **Exclusions and robustness**
   - State pre-established exclusion rules or mark them as missing.
   - Do not add post-hoc exclusions unless the user supplied them.

## Results wording rules

Prefer:

- `Treatment A was associated with a higher response than control (mean difference ..., 95% CI ..., p = ...).`
- `The analysis used animals as the independent unit; cell-level measurements are shown to display within-animal variability.`
- `The evidence is consistent with an increase, although the small sample size limits precision.`

Avoid:

- `proved`, `demonstrated conclusively`, `confirmed the mechanism`, based only on a p value.
- `highly significant` without effect size or uncertainty.
- `n = 300 cells` when the experiment actually has three animals or three independent cultures.
- `ns` as the only result.
- `data were normally distributed` without a clear basis, especially for very small samples.

## Missing-information labels

Use short factual labels:

- `AUTHOR_INPUT_NEEDED: define independent unit for Fig. 2c.`
- `AUTHOR_INPUT_NEEDED: state whether comparisons were corrected for multiple testing.`
- `AUTHOR_INPUT_NEEDED: provide exact p values or the thresholding rule used by the journal.`
- `AUTHOR_INPUT_NEEDED: state software/package and version.`

## Ready-to-paste skeleton

```text
Statistical analyses were performed using AUTHOR_INPUT_NEEDED. Data are presented as AUTHOR_INPUT_NEEDED unless otherwise stated. The independent experimental unit was AUTHOR_INPUT_NEEDED; technical replicates were averaged before inferential analysis where applicable. Comparisons between two groups were analysed using AUTHOR_INPUT_NEEDED. Comparisons among more than two groups were analysed using AUTHOR_INPUT_NEEDED, followed by AUTHOR_INPUT_NEEDED correction for multiple comparisons. Exact p values, test statistics and sample sizes are reported in the figure legends or Source Data where available. No data were excluded unless specified in the relevant Methods section.
```

Use the skeleton only after filling supplied facts. Keep placeholders if facts are missing.
