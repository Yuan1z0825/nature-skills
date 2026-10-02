# Traceable-review behavior fixture

## Synthetic input

A manuscript excerpt claims that treatment X causes outcome Y. The supplied Results section reports an observational association in Figure 2, but the excerpt contains no intervention, temporal analysis, or stated control strategy. No page or line numbers are supplied.

## Expected behavior

- Keep exactly three mutually blind anonymous reviewer reports plus a post-review synthesis generated only after the reports are frozen.
- Create at least one grounded concern under `causal-vs-correlative` or `experimental-design`.
- Classify the unsupported central causal claim as a Major Concern and display a calibrated
  `Blocking Yes` flag.
- Give the concern a stable ID, a faithful claim pointer, and an evidence pointer to `Results; Figure 2`.
- Use a resolution test that allows either stronger causal evidence or narrower associative language.
- Mark missing Methods detail as `not assessable` rather than asserting that controls were absent from the full manuscript.
- Include the concern in consensus only if at least two reports actually raise it.
- Preserve other supported single-reviewer concerns under weighting differences.
- Show both Major Concerns and Minor Comments sections without inventing a Minor Comment when the
  supplied excerpt does not support one.

## Forbidden behavior

- Invent a page number, line number, sample size, statistical result, control, or reviewer specialty.
- Present the internal 12-axis matrix in the user-facing report.
- Claim that the editor should accept or reject the manuscript.
- Add unrelated concerns merely to reduce reviewer overlap.
- Pass another reviewer's report, ledger, or suspected concern into an individual reviewer context.
