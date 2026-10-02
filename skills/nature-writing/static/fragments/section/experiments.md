# Section: Experiments / Results (writing)

## Default evidence ladder

`establish the phenomenon -> stress-test it -> rule out alternatives -> broaden it -> interpret it -> bound it`

Each subsection has a claim-first opening, then data support.

Depending on the paper, instantiate this as a discovery loop, a core-capability
plus validation envelope, or a capability ladder. Load
`../../../../nature-shared/core/nature-results-discussion.md` for the three
archetypes and the same-level-repetition test.

## Drafting rules

- Load `../../../../nature-shared/core/main-text-discipline.md` before deciding
  which analyses enter the main text. Classify results by their function in the
  paper and build the shortest sufficient evidence chain.
- Stay mainly in past tense.
- Report what was observed, under what conditions, with what quantitative support.
- Use statistics correctly and sparingly. Every test needs a stated hypothesis.
- Keep core discovery and necessary support in the main text. Route robustness,
  non-central heterogeneity, provenance detail, alternative inference, and edge
  cases to SI unless they change the central interpretation.
- **Each major claim needs adequate evidence across the manuscript and SI.** Do
  not force every comparison, ablation, or stress test into the main text; if
  adequate evidence is absent from the full record, mark it for follow-up rather
  than drafting around it.
- Normally report the descriptive quantity and primary inferential statistic in
  the main text. Put secondary inference and diagnostics in SI unless required
  or conclusion-changing.

## Results syntax (vs Discussion)

Results sentences usually report:

- `was detected` / `increased` / `showed` / `enabled` / `achieved`

Close each coherent evidence unit with the bounded inference it supports.
Calibrated interpretation (`suggests`, `indicates`, `likely because`) may remain
in Results when it directly answers the current experiment and the supporting
evidence is visible there. Move literature synthesis, broad implications, and
extended mechanistic reconciliation to Discussion.

## Common failure modes when drafting

- Mixing observation with an interpretation that is not supported by the
  current experiment, or allowing local interpretation to expand into a broad
  Discussion.
- Citing supplementary data when the result should be in the main text.
- Appending robustness or reviewer-defense prose until the central evidence chain
  disappears.
- Repeating the same effects, intervals, and P values in Results and captions.
- Vague comparisons (`higher than control`) without effect size, sample size, or test.
- Per-paragraph claims without per-paragraph evidence.
- Reusing an earlier baseline or control as the centre of a later subsection
  and restating the same claim, instead of making the new perturbation,
  falsification, stronger comparator, or boundary the decisive evidence.

## Deeper reference

For ML/conference-style experiment sections — baselines, ablations, metrics, tables, figures — open `references/experiments.md`.
