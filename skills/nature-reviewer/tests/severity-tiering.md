# Severity-tiering behavior fixture

## Synthetic input

A complete synthetic manuscript claims that a diagnostic model generalizes across hospitals. The
Results report only a single-hospital internal random split and provide no external-site or temporal
validation. The Discussion repeats the broad generalization claim. In Figure 2, the main text
correctly defines the error bars, but the legend does not repeat that definition. The Abstract uses
the acronym `DHI` before defining it. No page or line numbers are supplied.

## Expected behavior

- Keep exactly three mutually blind anonymous reviewer reports plus a post-review synthesis generated only after the reports are frozen.
- Show separate `Major Concerns` and `Minor Comments` sections in every reviewer report; use
  `None identified from the supplied material` when a reviewer has no grounded item in one tier.
- Classify the unsupported cross-hospital generalization as a Major Concern under
  `clinical-validity`, `experimental-design`, or `claim-moderation`.
- Mark that Major Concern `Blocking Yes` because the supplied evidence does not establish the
  manuscript's central generalization claim. Allow either external/temporal validation or narrowing
  the claim as the resolution test.
- Classify the omitted Figure 2 legend definition and undefined Abstract acronym as Minor Comments
  because the supplied facts make them localized presentation corrections.
- Use uppercase `M` IDs for Major Concerns and lowercase `m` IDs for Minor Comments.
- Include a deduplicated minor-revision checklist in the synthesis and retain source concern IDs.

## Forbidden behavior

- Do not downgrade the unsupported central generalization claim to Minor because claim narrowing
  may be easy to write.
- Do not upgrade the legend or acronym issues to Major merely to make the review sound severe.
- Do not invent additional concerns, external datasets, hospitals, metrics, line numbers, or
  reviewer specialties.
- Do not use hostile or insulting phrasing to signal that a concern is serious.
- Do not list an issue as consensus unless at least two reviewer reports raise the same issue key.
- Do not pass one reviewer's report or concern ledger to another reviewer, and do not rewrite reports after comparison to control overlap.

## Pass/fail checklist

- [ ] Every reviewer visibly has Major and Minor sections.
- [ ] Major IDs use `M`; Minor IDs use `m`.
- [ ] Every Major Concern displays a calibrated Blocking flag.
- [ ] The central generalization gap is Major and Blocking.
- [ ] The two localized reporting issues remain Minor.
- [ ] Empty tiers are explicit and no severity quotas are used.
- [ ] The synthesis separates blocking, other major, and minor-checklist items.
