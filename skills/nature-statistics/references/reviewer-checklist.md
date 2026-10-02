# Reviewer checklist for statistical reporting

Use this file before final delivery. It converts the audit into reviewer-facing risk and concrete author actions.

## Severity labels

### P0 — must fix before submission or resubmission

Use P0 when the current statistical reporting or analysis logic could invalidate a central claim.

Examples:
- independent unit is wrong or undefined for a central claim
- paired/repeated/nested structure is ignored
- many comparisons are made without any correction or family definition
- interaction is inferred incorrectly
- exclusion/missing-data handling could change the result but is not disclosed
- analysis cannot be understood from Methods and legends

### P1 — important revision strongly recommended

Use P1 when the claim may be defensible but reporting is too weak for review.

Examples:
- exact sample sizes are missing
- error bars or box-plot conventions are undefined
- effect sizes or uncertainty are absent for key results
- software/package/version is missing
- p-value thresholds are used without exact values or clear correction status
- small-sample limitation is not acknowledged

### P2 — clarity or polish improvement

Use P2 when the issue is unlikely to change the conclusion but could frustrate reviewers.

Examples:
- inconsistent terminology for replicates
- figure legends repeat methods but omit panel-specific `n`
- `ns` labels are unclear
- statistical text is scattered between Methods, legends and supplementary notes

## Final QA questions

Before sending the answer, check:

1. Did we define the independent unit?
2. Did we distinguish biological and technical replicates?
3. Did we avoid inventing p values, tests, software, sample size, randomization, or blinding?
4. Did every central result claim map to a test/model or to a clear descriptive statement?
5. Did we identify whether multiple-comparison correction is needed or missing?
6. Did we state which issues are not assessable from the supplied material?
7. Did the proposed wording avoid causal or mechanistic overclaiming?
8. Did we include short `AUTHOR_INPUT_NEEDED` questions rather than broad requests?

## Reviewer-risk phrasing

Use neutral phrasing:

- `A reviewer may challenge whether the analysis treats the correct independent unit as n.`
- `The current legend does not make clear whether the plotted points are biological replicates or technical subsamples.`
- `The claim is stronger than the statistical evidence currently reported.`
- `The comparison family is not defined, so the correction status is unclear.`

Avoid accusatory phrasing:

- `This is fake significance.`
- `The authors manipulated p values.`
- `The analysis is wrong.`

Unless raw data and full design are supplied, prefer:

- `not assessable from the supplied material`
- `potential risk`
- `requires author confirmation`
- `should be clarified before submission`

## Response to reviewer support

When helping draft a response to statistical reviewer comments, use this structure:

```text
Reviewer concern
- [quote or short paraphrase]

Author-side action needed
- [analysis/text/figure/source data change]

Draft response
- We thank the reviewer for raising this point. We have revised the Statistical analysis section to define AUTHOR_INPUT_NEEDED and have updated Fig. AUTHOR_INPUT_NEEDED legend to report AUTHOR_INPUT_NEEDED. The revised text now states: "AUTHOR_INPUT_NEEDED".

Manuscript change
- Section / figure:
- Replacement text:
```

Do not claim that a new analysis was performed unless the user supplies the result or asks you to run it on data.
