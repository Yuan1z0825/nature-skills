# Flagship Nature Article statistical requirements

Use this checklist only when the target is the flagship journal **Nature** or
the user explicitly asks for a Nature Article submission audit. Keep the
general design checks in `statistical-reporting.md`; this file adds Nature's
current journal-specific minimums.

## Stage and scope

- At initial submission, statistical information must already be complete
  enough for editors and referees to assess the work.
- Production formatting is stage-specific, but missing definitions of `n`,
  replication, tests or error bars are scientific-reporting gaps, not cosmetic
  formatting issues.
- Do not claim that another Nature Portfolio title has the same checklist
  without checking its current instructions.

## Required Methods checks

Confirm that the Methods contain a statistics section that states:

- every statistical test used and the comparison or model it addresses
- whether each applicable test was one-tailed or two-tailed
- the independent experimental unit
- the definition of biological, technical and other replicates
- paired/unpaired or repeated-measures structure where relevant
- inclusion/exclusion criteria, randomization and blinding where applicable
- correction strategy for multiple comparisons

## Required numerical reporting checks

For every reported statistic or applicable figure panel, require:

- an exact `n` value; if `n` varies between experiments, report the individual
  values instead of a range
- a definition of every error bar or interval
- the number of times representative measurements or experiments were repeated
- exact values for statistically significant and non-significant P values where
  relevant
- for ANOVA, the F statistic and degrees of freedom
- for t-tests, the t statistic and degrees of freedom
- the exact comparison, test family and tail direction near the reported result

The general skill may additionally request effect sizes, confidence intervals,
assumption checks and multiplicity details. Those strengthen reporting but
should not be mislabeled as a verbatim Nature requirement unless supported by
the target instruction.

## Reporting Summary gate

Check whether the current Nature Portfolio reporting summary applies:

- life sciences
- behavioural and social sciences
- ecology, evolution and environmental sciences
- covered physical-science areas such as solar cells and claims of lasing

Cross-check the completed form against Methods, Results, legends and Source
Data. Flag contradictory sample sizes, exclusions, randomization, blinding or
software details.

## Audit table

Return one row per analysis or panel:

| Analysis/panel | Test and tail | Exact n and replicate unit | Error/interval | Exact P | Test statistic and df | Repeat count | Status |
|---|---|---|---|---|---|---|---|

Use:

- `pass` when all applicable fields are explicit and consistent
- `AUTHOR_INPUT_NEEDED` when a factual value is absent
- `not applicable` only with a short reason
- `blocked` when the missing information prevents interpretation or exposes
  pseudoreplication, undisclosed exclusions or incompatible analyses

## Official sources

Verified 2026-08-08:

- Nature initial submission, Statistical information:
  <https://www.nature.com/nature/for-authors/initial-submission>
- Nature Portfolio reporting standards:
  <https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards>
