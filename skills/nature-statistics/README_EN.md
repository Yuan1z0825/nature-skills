# `nature-statistics` Skill

[中文说明](README.md)

## What It Does

`nature-statistics` audits, revises, or drafts statistical reporting for Nature
and other high-impact journal manuscripts. It focuses on whether statistical
information is transparent, checkable, and aligned with the study design, rather
than reducing statistical quality to whether a p value is significant.

## When to Use It

- Before submission, to check a Statistical analysis / Methods section.
- When reviewers say the statistical analysis is unclear or insufficient.
- When figure legends need consistent reporting of error bars, n definitions,
  statistical tests, exact p values, and source-data notes.
- When Chinese author notes need to be converted into conservative English
  statistical reporting.
- When a result may involve pseudoreplication, multiple comparisons, nested
  data, repeated measures, or overinterpretation of significance.

## Copy-Paste Prompts

```text
Use nature-statistics to audit this Statistical analysis section and list missing information before submission.
```

```text
Rewrite these figure-legend statistics in conservative Nature-style English, and mark anything that still needs author confirmation.
```

```text
Use nature-statistics to answer this reviewer comment about unclear statistical analysis.
```

## Required Inputs

- The Statistical analysis / Methods text, Results text, figure legends, or
  reviewer comments to check.
- Sample size, replicate type, independent analysis unit, statistical tests,
  p-value handling, and software information when available.
- Any known design details such as paired data, repeated measures, nesting,
  randomization, blinding, or exclusion rules.

## Expected Outputs

- `Statistics review scope`
- `Major statistical issues`
- `Ready-to-paste revision`
- `AUTHOR_INPUT_NEEDED`
- `Reviewer-risk note`

For drafting-only requests, the skill can return a shorter `Draft Statistical
analysis` plus `Reporting notes`.

## Dependencies / API Keys / Local Environment

No external API key is required by default. Statistical software names, package
versions, exact p values, sample sizes, exclusion rules, and power-analysis
details must come from the author or project materials.

## FAQ

**Can this skill invent missing p values or sample sizes?**  
No. Missing facts are marked as `AUTHOR_INPUT_NEEDED`.

**Does it perform statistical tests from raw data?**  
It is primarily a reporting and review skill. If raw-data analysis is required,
provide the data and requested analysis separately.

**Does significance prove mechanism or causality?**  
No. The skill keeps statistical language conservative and separates statistical
evidence from mechanism, causality, and biological importance.

## Related Skills

- [`nature-figure`](../nature-figure/README_EN.md)
- [`nature-response`](../nature-response/README_EN.md)
- [`nature-reviewer`](../nature-reviewer/README_EN.md)
- [`nature-writing`](../nature-writing/README_EN.md)
