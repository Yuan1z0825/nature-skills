# Common statistical failure modes

## Contents

- [P0: likely to undermine the result](#p0-likely-to-undermine-the-result)
- [P1: important reporting or interpretation risk](#p1-important-reporting-or-interpretation-risk)
- [P2: clarity and presentation risk](#p2-clarity-and-presentation-risk)


Use this file to identify reviewer-risk patterns. Do not accuse the authors; state the risk and the fix.

## P0: likely to undermine the result

### Pseudoreplication

Signal:
- `n` is reported as cells, images, fields, spectra, droplets, reads, technical wells, or repeated readings.
- The independent experimental unit is likely animal, patient, culture, donor, batch, plot, device, or experiment.

Risk:
- The test may overstate precision and produce artificially small p values.

Fix:
- Analyse independent units, aggregate technical subsamples, or use a hierarchical / mixed-effects model when justified.
- Show subsample-level spread visually without treating every subsample as independent.

### Uncorrected multiple comparisons

Signal:
- Many genes, proteins, time points, panels, groups, pairwise contrasts, or exploratory endpoints are tested.
- The manuscript reports selected significant comparisons only.

Risk:
- False-positive rate is inflated or the comparison family is unclear.

Fix:
- Define the family of tests and use an appropriate correction or distinguish prespecified primary comparisons from exploratory analyses.

### Wrong interaction inference

Signal:
- Authors say two effects differ because one comparison is significant and the other is not.

Risk:
- Difference in significance is not evidence of a significant difference between effects.

Fix:
- Test the interaction or directly compare effect sizes.

### Analysis unit mismatch

Signal:
- Design is paired, matched, blocked, longitudinal, nested, or repeated-measures, but analysis uses independent tests.

Risk:
- Dependence structure is ignored.

Fix:
- Use paired tests, repeated-measures analysis, mixed-effects models, blocking, or cluster-robust methods as appropriate.

## P1: important reporting or interpretation risk

### Significance-only conclusion

Signal:
- Result is described mainly by stars or p thresholds.

Risk:
- Readers cannot judge magnitude, uncertainty, or practical importance.

Fix:
- Add effect estimates, confidence/credible intervals, raw distributions, and exact p values where possible.

### Small-sample overclaim

Signal:
- Very small `n`, unstable estimates, or no uncertainty interval, but strong language.

Risk:
- Effect size and direction may be imprecise.

Fix:
- Use cautious wording and report the limitation directly.

### Normality or equal-variance assumption not supportable

Signal:
- Parametric tests are used on small or skewed samples with no rationale.

Risk:
- Assumptions may be unverifiable or violated.

Fix:
- Add assumption checks, use robust/nonparametric alternatives, or describe the limitation.

### Outlier handling is unclear

Signal:
- Points disappear, exclusions are mentioned vaguely, or outlier tests are named without prespecified rules.

Risk:
- Post-hoc exclusion may bias results.

Fix:
- State exclusion criteria, timing, number removed, and whether conclusions are robust to inclusion.

### Correlation or regression overclaim

Signal:
- Association is written as mechanism, prediction, or causality without design support.

Risk:
- Confounding, non-independence, and model extrapolation may be ignored.

Fix:
- Reword as association unless experimental or causal identification supports stronger claims.

## P2: clarity and presentation risk

### Error bars are undefined

Fix:
- State s.d., s.e.m., confidence interval, interquartile range, or other convention.

### `n` varies across panels but is not panel-specific

Fix:
- Give panel-specific `n` and define what `n` represents.

### Star notation is not defined

Fix:
- Define thresholds, correction status, and exact p values if available.

### Software is missing

Fix:
- Add software/package and version if supplied by the user.

### `ns` hides the result

Fix:
- Provide exact p value or state the reporting threshold and avoid interpreting lack of significance as proof of no effect.
