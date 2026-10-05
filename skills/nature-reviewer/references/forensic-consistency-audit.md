# Forensic consistency and numerical audit

## Contents

- [Purpose](#purpose)
- [Isolation rule](#isolation-rule)
- [Evidence statuses](#evidence-statuses)
- [Audit layers](#audit-layers)
- [Required audit record](#required-audit-record)
- [Synthesis handling](#synthesis-handling)
- [Avoid](#avoid)

## Purpose

Use this reference after all individual reviewer reports are frozen and before the synthesis is written. Its role is to catch deterministic internal failures that independent reviewers may miss during claim-level assessment.

This audit is not a fourth reviewer report and does not create a consensus concern. Treat its findings as an editorial consistency layer. Include confirmed findings in the synthesis and risk section, label them as audit findings, and never feed them back into reviewer contexts.

## Isolation rule

- Run the audit in a separate main-agent or editor-facing pass.
- Do not show audit results to reviewers.
- Do not edit frozen reviewer reports after the audit.
- Do not call an audit finding a consensus finding unless at least two frozen reviewer reports independently raised the same issue.
- When an audit finds a blocking error that no reviewer identified, preserve it as an editor-facing audit finding rather than pretending it was reviewer consensus.

## Evidence statuses

Classify every audit result as one of:

- `confirmed_internal_error`: arithmetic, ordering, bounds, unit, or direct contradiction is proved from supplied material.
- `aggregation_ambiguity`: numbers may be valid under another aggregation level, but the manuscript does not define it.
- `provenance_gap`: a number, sample count, experimental unit, configuration, or selection rule lacks a traceable source.
- `suspected_duplication`: repeated rows, values, or text patterns are implausible but not yet proved to be copy errors.
- `unresolved_input_needed`: a raw-data or author fact is required before the finding can be classified.
- `not_assessable`: supplied material cannot support the check.
- `passed`: the check was run and no inconsistency was found.

Never upgrade a suspected anomaly to a confirmed error without arithmetic proof or source data.

## Audit layers

### 1. Arithmetic and identities

Check deterministic relations using only supplied values.

- Sums of subgroup counts, tiles, patients, sites, events, or samples.
- Percentages, retention ratios, rates, fold changes, and weighted means.
- Mean minus baseline equals reported delta.
- Paired differences equal the compared quantities.
- Ranges contain all reported values.
- Standard deviations, standard errors, confidence intervals, and test statistics are internally plausible.
- Percentages remain within 0 to 100 and probabilities within 0 to 1.
- Counts remain integers where required.
- Subgroup totals reconcile with full-cohort totals and exclusions.

Record enough intermediate arithmetic that another reader can reproduce the check.

### 2. Metric bounds and identities

Identify the exact metric definition, aggregation level, denominator, positive class, and empty-mask rule before checking bounds.

Check applicable relations such as:

- IoU and Dice bounds.
- Balanced accuracy, balanced IoU, and per-class recall identities.
- Precision-recall-IoU relationships under a stated denominator.
- MCC bounds and zero-denominator behavior.
- Calibration and Brier-score bounds.
- Boundary metrics, Hausdorff distances, and unit conventions.
- Prevalence-sensitive metrics at extreme foreground fractions.
- Whether a reported value is impossible under one aggregation interpretation but possible under another.

If a metric is undefined in the manuscript, classify the issue as `aggregation_ambiguity` or `provenance_gap`, not as a numerical error.

### 3. Prose, tables, and figures

Compare narrative claims directly with their displays.

- Highest, lowest, best, worst, monotonic, always, only, and every-threshold statements.
- Rank ordering and any claim that two methods exchange order.
- Every headline number in Abstract, Results, Discussion, and Conclusion.
- Same quantity at different precision.
- Percentages, sample counts, and retention values across sections.
- Table and figure calls resolving to the intended object.
- Captions matching visible columns, rows, units, and aggregation.
- Duplicate rows, identical deltas, or identical intervals to the displayed precision.
- Error bars and intervals using compatible variance definitions.
- Figure examples matching the regime they are claimed to illustrate.

### 4. Aggregation and inferential unit

State the unit at every level.

- Observation, pixel, tile, image, patient, site, region, event, or cluster.
- Training, validation, test, support, query, and held-out roles.
- Macro versus micro aggregation.
- Equal-region, equal-tile, equal-pixel, or prevalence-weighted means.
- Pairing and nesting across treatment, seed, group, and cluster.
- Whether bootstrap or resampling treats the inferential unit at the correct level.
- Whether overlapping or near-duplicate units make an interval too narrow.

A numerical value is only auditable after its aggregation level is defined.

### 5. Experimental provenance and leakage

Check whether every central comparison can be reconstructed.

- Exact training, validation, test, continuation, placebo, and evaluation sets.
- Source-domain membership and sampling weights.
- Group, site, event, or subject exclusions.
- Target data participation in training or selection.
- Checkpoint-selection rules.
- Spatial, temporal, or hierarchical independence.
- Duplicate and near-duplicate audits, with thresholds and sensitivity.
- Pilot runs and configuration differences.
- Compute cost, hardware, run count, and wall-clock time when needed for comparative claims.

### 6. Dispersion and sensitivity anomalies

Flag but do not overclaim when:

- One group has near-zero variance while a comparable group has large variance.
- Standard deviation exceeds or approaches the mean for a bounded metric.
- Replicate counts differ silently.
- One influential group changes an aggregate interval or sign.
- A suspiciously uniform result appears across independent runs.
- A robustness check reuses one seed or initialization while claiming broad robustness.
- Identical rows appear after a filtering step that should remove more cases.

Require per-seed, per-unit, or raw values before declaring an error.

### 7. Reproducibility gate

When the user plans new experiments, distinguish audit findings from new-experiment feasibility.

- Existing code and artifacts must reproduce existing headline numbers before new experiments are used to support the paper.
- If reproduction fails, report the paper as not yet reproducible and stop interpreting new runs.
- Record tolerance, expected value, reproduced value, and run path.
- A failed or unavailable gate is a reproducibility finding, not a minor formatting issue.

## Required audit record

Use this shape for each finding:

```yaml
audit_id: AUD-01
status: confirmed_internal_error
location: Table 3; Results 4.11
claim_pointer: Method A has the lowest score at every threshold.
evidence_pointer: Table 3 values at thresholds 0.6 and 0.7.
check: Recomputed the rank order at all tested thresholds.
result: Method B is lower than Method A at two thresholds.
impact: The narrative claim contradicts the table.
resolution_test: Correct the ranking statement and recheck all downstream interpretations.
reviewer_overlap: none identified
```

## Synthesis handling

- Place confirmed internal errors, aggregation ambiguities, provenance gaps, and reproducibility blockers in the synthesis.
- Keep reviewer consensus and audit findings separate.
- Add confirmed or unresolved central audit findings to `Risk / unsupported claims`.
- Do not rewrite reviewer reports to incorporate audit findings.
- If an audit finding changes the interpretation of a reviewer concern, state the change in the synthesis as an audit-driven reconciliation.

## Avoid

- Domain-habit arithmetic with no supplied values.
- Treating an undefined aggregation level as proof that a number is wrong.
- Calling a suspicious dispersion pattern a data-integrity violation without evidence.
- Replacing reviewer independence with a shared audit.
- Adding audit findings only to an appendix while leaving the headline unsupported.
- Hiding confirmed arithmetic contradictions because no reviewer raised them.
- Treating a failed reproducibility check as a presentation issue.
