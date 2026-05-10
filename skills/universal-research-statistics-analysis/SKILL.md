---
name: universal-research-statistics-analysis
description: Use this Skill when a user provides CSV/XLSX research data and wants statistically defensible analysis, Excel results, Word three-line tables, Methods/Results text, optional figures, or help choosing an appropriate common statistical test. The Skill is domain-agnostic and suitable for typical experimental, observational, pre/post, repeated-measures, and small-to-moderate tabular datasets.
---

# Universal Research Statistics Analysis Skill

## Purpose

Convert tabular research data into a transparent analysis package:

- `analysis_results.xlsx`
- `three_line_tables.docx`
- `methods_results.docx`
- optional `figures/*.png` and `figures/*.pdf`
- logs documenting method routing, skipped tests, and warnings

## Default reporting policy

1. Use **p-values only** by default.
2. Do **not** output q-values or FDR q-values by default.
3. Use two-sided tests unless the user explicitly requests otherwise.
4. For three or more groups, generate a compact letter display (`a/b/c`) for Word tables by running the necessary background pairwise comparisons. Do not show the detailed pairwise table unless the user asks for it or passes `--include-posthoc`.
5. Word tables use `mean ± SEM` by default for continuous variables.
6. Ordinal or score-like outcomes use `median (IQR)` and non-parametric tests by default.
7. Excel retains complete audit statistics: `n`, `mean`, `SD`, `SEM`, `median`, `Q1`, `Q3`, p-value, method, letters, and skip reasons.
8. Never infer causality from non-randomized or cross-sectional data. Use cautious language.

## Trigger examples

Use this Skill when the user says:

- “Analyze this CSV and make Excel and Word tables.”
- “I have two/three/four treatment groups; choose the correct test.”
- “Generate three-line tables.”
- “Run ANCOVA / factorial ANOVA / GLM / mixed model.”
- “Create Methods and Results text from my statistical output.”
- “My data only contains some variables; analyze whatever is available.”

## Method router summary

See `references/method-router.md` for detailed routing.

Default route:

- two independent groups: Welch t-test or Mann–Whitney U
- three or more independent groups: one-way ANOVA or Kruskal–Wallis
- paired two-timepoint data: paired t-test or Wilcoxon signed-rank
- baseline/final data: ANCOVA when baseline and endpoint are supplied
- factorial designs: OLS factorial model with ANOVA table
- binary outcome: logistic GLM
- count outcome: Poisson or negative binomial GLM
- repeated/clustered data: optional random-intercept mixed model

## Command-line use

```bash
python scripts/analyze_research_data.py \
  --input your_data.csv \
  --outdir results \
  --group-col Group \
  --make-figures
```

Optional modules:

```bash
# Detailed pairwise results sheet
--include-posthoc

# Baseline-adjusted model
--baseline-col Baseline --endpoint-col Final

# Factorial ANOVA
--factor-cols FactorA FactorB

# GLM screening
--run-glm

# Mixed model / repeated measures
--subject-col SubjectID --period-col Period --sequence-col Sequence --run-mixed-models
```

## Output discipline

- If a variable lacks enough valid data, skip it and record the reason.
- If a model fails to converge, report the failure; do not present it as a valid result.
- If only a subset of expected data is present, analyze only the available modules.
- Maintain original column names in outputs whenever possible while also recording canonicalized names.

## Limitations

This Skill is not a substitute for regulatory statistical software, a preregistered clinical trial SAP, survival analysis, complex causal inference, high-dimensional omics models, advanced GLMM, or Bayesian modelling. For these, use the Skill to audit and prepare data, then consult specialist methods.
