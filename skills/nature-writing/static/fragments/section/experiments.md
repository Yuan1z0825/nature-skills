# Section: Experiments / Results (writing)

## Default evidence ladder

`system / workflow validation -> main result -> baseline comparison -> ablation / mechanism analysis -> application or generalization -> stress tests / failure modes`

Each subsection has a claim-first opening, then data support.

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

Do not drift into Discussion syntax (`may reflect`, `suggests`, `is likely due to`) unless the transition is intentional.

## Common failure modes when drafting

- Mixing observation and interpretation in the same paragraph.
- Citing supplementary data when the result should be in the main text.
- Appending robustness or reviewer-defense prose until the central evidence chain
  disappears.
- Repeating the same effects, intervals, and P values in Results and captions.
- Vague comparisons (`higher than control`) without effect size, sample size, or test.
- Per-paragraph claims without per-paragraph evidence.

## Deeper reference

For ML/conference-style experiment sections — baselines, ablations, metrics, tables, figures — open `references/experiments.md`.
