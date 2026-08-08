---
name: nature-statistics
description: >-
  Audit, revise, or draft manuscript statistical reporting for Nature / high-impact journal submissions. Use when the user asks to check statistical analysis sections, p values, confidence intervals, sample size, biological versus technical replicates, randomization, blinding, multiple-comparison correction, model assumptions, figure legends, Results statistics wording, reviewer comments about statistics, or Chinese academic drafts needing publication-ready Statistical analysis text. Also trigger on general paper-statistics requests such as 统计审查、统计分析小节、统计方法、p值、样本量、重复数、多重比较、置信区间、效应量、图注统计、审稿人统计意见.
---

# Nature Statistics Reporting Skill

Use this skill to make manuscript statistics transparent, reproducible, and appropriately bounded. It is a reporting and review skill, not a substitute for a statistician reanalysing raw data unless the user supplies the data and explicitly asks for computation.

## Default stance

- Prioritize design transparency over decorative statistical language.
- Separate three questions: what was measured, what unit was analysed, and what inference was claimed.
- Treat the independent experimental unit as the default `n`; do not silently treat cells, fields of view, repeated readings, spectra, model runs, or technical replicates as independent biological or experimental samples.
- Prefer effect sizes, uncertainty intervals, sample sizes, and exact test definitions over significance-only phrasing.
- State missing information as `AUTHOR_INPUT_NEEDED` instead of inventing sample sizes, tests, software, corrections, exclusion rules, randomization, or blinding.
- If a journal-specific instruction, study-type guideline, or field standard conflicts with this skill, follow the more specific source and mark the source used.

## Accepted inputs

The skill may receive:

- a Statistical analysis / Methods subsection
- Results paragraphs containing test statistics or p values
- figure panels, legends, captions, or source-data notes
- reviewer comments about statistics
- author notes in Chinese or English
- tables of reported comparisons
- raw or summary data, only when the user wants a concrete reanalysis or figure-statistics check

If the input is partial, run a bounded audit and state which parts cannot be assessed.

## Workflow

1. **Classify the task.** Decide whether the user wants audit, rewrite, draft, reviewer-response support, figure-statistics alignment, or data-backed reanalysis.
2. **Extract the design.** Identify groups, treatments, time points, endpoints, blocking factors, repeated measures, randomization, blinding, exclusions, and missing-data handling.
3. **Define `n` and replication.** Separate independent experimental units, biological replicates, technical replicates, repeated measures, cells/fields/subsamples, simulations, and pooled observations.
4. **Map claims to analyses.** For each result claim, record the comparison/model, test family, assumptions, correction strategy, effect estimate, uncertainty, and exact p-value policy.
5. **Check common failure modes.** Use `references/common-failure-modes.md` when the text involves nested data, many comparisons, cell-level measurements, interaction claims, correlations, regression, outliers, small samples, or significance-only reasoning.
6. **Check reporting completeness.** Use `references/statistical-reporting.md` to verify that Methods and Results give enough information for readers and reviewers to understand the analysis.
   If the target is the flagship journal Nature, also use
   `references/nature-article-requirements.md` for its exact tail, `n`, repeat,
   P-value, test-statistic and degrees-of-freedom requirements.
7. **Align figure statistics.** Use `references/figure-statistics.md` when figure legends, panel labels, stars, error bars, box plots, violin plots, source data, or supplementary figure notes are involved.
8. **Draft or revise.** Produce conservative, ready-to-paste text. Keep claims within the supplied design and evidence. Do not upgrade statistical association into mechanism or causality.
9. **Run final QA.** Use `references/reviewer-checklist.md` before final delivery for severity labels, unresolved author questions, and reviewer-facing risk.

## Output format

Unless the user asks for another format, return:

```text
Statistics review scope
- Input reviewed:
- Boundary / missing materials:
- Study design readout:
- Independent unit and replication readout:

Major statistical issues
- [P0/P1/P2] Issue:
  Evidence from supplied text:
  Why it matters:
  Fix:

Ready-to-paste revision
[Rewritten Statistical analysis / Results / figure legend text]

AUTHOR_INPUT_NEEDED
- [short factual questions only]

Reviewer-risk note
- What a statistical reviewer may still challenge:
```

For a clean drafting request with enough information, skip the long issue list and return:

```text
Draft Statistical analysis
[ready-to-paste text]

Reporting notes
- n definition:
- tests/models:
- multiple comparisons:
- software/version:
- unresolved fields:
```

## Red lines

- Do not invent p values, sample sizes, degrees of freedom, confidence intervals, software versions, correction methods, preregistration, exclusion rules, or power calculations.
- Do not recommend a statistical test as final when the unit of analysis or design is unclear.
- Do not accept `n = number of cells/images/measurements` as independent replication without checking the experimental hierarchy.
- Do not use “significant” as a synonym for important, large, causal, or biologically meaningful.
- Do not hide non-significant or weak results by rewriting them into stronger claims.
- Do not give medical, regulatory, or clinical-trial statistical advice beyond reporting checks unless the user provides the relevant protocol and asks for bounded manuscript wording.

## Related files

| File | Open when |
|---|---|
| [references/source-basis.md](references/source-basis.md) | You need the source hierarchy or want to justify why the skill emphasizes transparency, reproducibility, and design reporting |
| [references/nature-article-requirements.md](references/nature-article-requirements.md) | The target is the flagship journal Nature or the user requests its exact statistical submission checklist |
| [references/statistical-reporting.md](references/statistical-reporting.md) | You are drafting or auditing Statistical analysis, Methods, Results, or Supplementary Methods text |
| [references/common-failure-modes.md](references/common-failure-modes.md) | You see nested measurements, many comparisons, interaction claims, correlation/regression, outliers, tiny samples, or overstrong p-value language |
| [references/figure-statistics.md](references/figure-statistics.md) | You are checking figure legends, panel statistics, error bars, stars, box/violin plots, source-data notes, or graphical reporting |
| [references/reviewer-checklist.md](references/reviewer-checklist.md) | You are finalizing an audit or preparing a reviewer-facing risk summary |
| [../nature-shared/core/consistency-sweep.md](../nature-shared/core/consistency-sweep.md) | The same statistic appears in more than one place, or interval terminology is in question: one metric at two precisions across table and text, SD/Std abbreviation drift, `confidence interval` used where `prediction interval` is meant, or overlapping error bars described as outperformance |

## Source hierarchy

Use sources in this order:

1. User-supplied manuscript, data, protocol, statistical analysis plan, reviewer comments, and journal instructions.
2. Nature Portfolio reporting standards and reporting-summary requirements.
3. Nature Methods / Nature Portfolio statistics guidance summarized in `references/source-basis.md`.
4. Study-type reporting guidelines where relevant, for example CONSORT, STROBE, PRISMA, ARRIVE, or field-specific community standards.
5. Conservative statistical reporting practice.

If the supplied material is insufficient for a defensible statistical recommendation, ask for the missing design facts or provide a bounded wording option rather than guessing.
