# Method Router

## Core principles

1. Choose a method based on design first, then data distribution.
2. Use p-values only by default.
3. Treat ordinal/score outcomes as non-parametric unless the user overrides.
4. Do not run a test when sample size, variance, or model assumptions make the result invalid.

## Independent groups

| Design | Default method |
|---|---|
| 2 groups, approximately normal, n>=3 per group | Welch t-test |
| 2 groups, non-normal/ordinal/small n | Mann–Whitney U |
| >=3 groups, approximately normal, n>=3 per group | One-way ANOVA |
| >=3 groups, non-normal/ordinal/small n | Kruskal–Wallis |

For >=3 groups, compact letters are generated for table display. Detailed post hoc tables are hidden unless requested.

## Paired data

| Design | Default method |
|---|---|
| 2 paired timepoints, approximately normal difference | Paired t-test |
| 2 paired timepoints, non-normal/ordinal | Wilcoxon signed-rank |

## ANCOVA

Use when baseline and endpoint are supplied:

```text
Endpoint ~ C(Group) + Baseline
```

## Factorial ANOVA

Use when two or more categorical factors are supplied:

```text
Outcome ~ C(FactorA) * C(FactorB)
```

## GLM

| Outcome type | Model |
|---|---|
| Binary 0/1 | Logistic GLM |
| Count, variance approximately mean | Poisson GLM |
| Count, overdispersed | Negative binomial GLM |

## Mixed model

Run only when explicitly enabled:

```text
Outcome ~ C(Group) + optional C(Period) + optional C(Sequence) + optional Carryover + (1 | SubjectID)
```

Always report convergence status and warnings.
