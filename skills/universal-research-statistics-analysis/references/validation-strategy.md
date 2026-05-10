# Validation Strategy

Recommended validation before release:

1. Oracle numerical checks against SciPy/statsmodels/R.
2. Method-router tests for normal, non-normal, ordinal, paired, and grouped data.
3. Monte Carlo simulations for false-positive behavior under null data.
4. Metamorphic tests:
   - row order invariance,
   - group label order invariance,
   - constant shift invariance for p-values,
   - scale invariance for t-test/ANOVA p-values.
5. End-to-end CLI tests confirming Excel, Word, logs, and figures are generated.
6. Visual rendering checks for Word tables.
