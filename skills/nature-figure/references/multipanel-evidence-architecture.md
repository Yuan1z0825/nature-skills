# Multi-panel evidence architecture

Use this reference when planning, restructuring, or auditing a manuscript
figure with several labelled panels, or when mapping a Results evidence chain
onto a sequence of figures. Read it together with the
[Nature Results–Discussion corpus guidance](../../nature-shared/core/nature-results-discussion.md)
when figure order must mirror the manuscript's claim escalation.

## Contents

- [Status and scope](#status-and-scope)
- [Start from the figure-level claim](#start-from-the-figure-level-claim)
- [Give panels different inferential roles](#give-panels-different-inferential-roles)
- [Choose an evidence-chain archetype](#choose-an-evidence-chain-archetype)
- [Corpus pattern anchors](#corpus-pattern-anchors)
- [Align figure order with Results claim escalation](#align-figure-order-with-results-claim-escalation)
- [Assign visual hierarchy from evidence hierarchy](#assign-visual-hierarchy-from-evidence-hierarchy)
- [Decide whether a panel belongs in the main figure](#decide-whether-a-panel-belongs-in-the-main-figure)
- [Run the multi-panel audit](#run-the-multi-panel-audit)

## Status and scope

This is **corpus-derived Nature-style guidance, not an official journal
requirement**. It was distilled from author-supplied readings of flagship
*Nature* papers on MIRA (`s41586-026-10675-5`), centromere architecture
(`s41586-026-10841-9`), Robin (`s41586-026-10652-y`) and TabPFN
(`s41586-024-08328-6`), then generalized for Nature Portfolio manuscript
figures. Current journal instructions, article-type rules, the actual evidence
and the scientific question always take precedence.

Do not copy a published paper's panel count or letter order as a template. The
stable pattern is inferential: a figure usually answers one Results-level
scientific question, while its panels perform different jobs in the evidence
chain needed to answer it.

## Start from the figure-level claim

Before choosing plots, write:

```text
Results-level question:
Figure-level claim:
What could overturn that claim?
Decisive evidence:
Panel sequence:
  a — question | evidence role | necessary comparison
  b — question | evidence role | necessary comparison
  c — question | evidence role | necessary comparison
Destination of displaced material: main figure | another figure | Extended Data/SI
```

Treat `one figure = one major claim` as a strong planning default, not a rigid
counting rule. A figure may contain several subordinate findings when all are
necessary to establish, qualify or bound the same higher-level claim. If a
panel establishes a separate major claim, give it another figure or Results
unit. If a panel can disappear without weakening or changing the figure-level
inference, merge it, move it to Extended Data/SI, or delete it.

Panel letters mark reading order; they do not assign universal functions.
Panel `a` need not always be a schematic, and panel `d` need not always be a
stress test. Choose roles from the scientific logic.

## Give panels different inferential roles

Select the smallest sufficient set. A figure does not need every role.

| Evidence role | Question it answers |
|---|---|
| Setup or schematic | What system, intervention, workflow or contrast is being tested? |
| Representative example | What does the phenomenon look like in a concrete case? |
| Primary quantitative evidence | Does the central effect or capability exist? |
| Baseline or control | Does it exceed a credible alternative or survive the relevant control? |
| Decomposition | Which components, strata or variables account for the effect? |
| Stratification | Does the conclusion hold across scientifically meaningful conditions? |
| Orthogonal validation | Is the conclusion recovered with another assay, measure or evidence type? |
| Perturbation or stress test | Does the claim survive an attack, or fail as predicted when a necessary relation is disrupted? |
| Boundary or failure case | Where does the effect weaken, reverse or stop generalizing? |
| Mechanistic evidence | What bounded explanation is supported for why the effect occurs? |

Panels are independently **necessary**, not independent stories. Covering one
panel should remove a distinct inferential step that the other panels cannot
recover. Prefer role diversity over metric diversity.

Weak mirror layout:

`a: R2 -> b: R2 pairwise tests -> c: MAPE -> d: MAPE pairwise tests`

This contains four panels but often only two inferential roles: overall
performance and pairwise evidence. A secondary metric can be useful, but it
does not earn a main panel merely by being another metric.

Stronger claim-driven layout:

`a: perturbation design -> b: decisive comparison -> c: full distribution or residual -> d: decomposition or boundary`

This progresses from what was changed, to what happened, to which alternative
was rejected, to what explains or limits the remaining effect.

## Choose an evidence-chain archetype

### Validation envelope

Use when the figure asks whether one system, simulator, intervention or model
capability is credible:

`define the capability -> establish it -> test distinct failure modes -> attack the claim -> bound it`

Consistency, leakage, safety, bias and adversarial robustness can belong in one
figure when they are different ways the same credibility claim could fail. Do
not present them as unrelated metric panels.

### Scale-to-instance chain

Use when a population-level pattern needs biological, clinical or physical
interpretation:

`global map or distribution -> quantity -> spatial relation or scale -> internal structure -> representative exception or instance`

The representative example should explain, localize or challenge the aggregate
pattern; it should not be a decorative anecdote.

### Discovery sequence

Use when each result changes the next scientific question:

`hypothesis -> decisive experiment -> analysis -> refined hypothesis -> next test -> mechanism validation`

At manuscript level, the figure sequence can carry this discovery loop. Keep
only steps that alter the claim or motivate the next test; do not reproduce a
chronological laboratory notebook.

### Capability ladder

Use when a method paper makes progressively stronger claims:

`what it is -> what behaviour it learned -> whether it outperforms alternatives -> whether the gain survives harder conditions -> what broader ability follows`

Within a benchmark figure, combine complementary support such as aggregate
performance, per-dataset generality and efficiency. In the following figure,
move to a stronger question such as robustness, confounding or broader
capability instead of redrawing the same ranking.

Across these archetypes, a reusable Figure-level chain is:

`establish -> compare or control -> stress-test or discriminate -> broaden -> bound`

Use only the moves the claim needs.

## Corpus pattern anchors

Use these author-supplied readings as reasoning examples, not layouts to copy:

- **MIRA — validation envelope.** One figure asks whether the patient agent is
  a credible evaluation environment, with panels probing consistency,
  information leakage and adversarial robustness as different failure modes.
  Later figures ask separate higher-level questions about intervention
  capability, medication, admission decisions and bias robustness. The metrics
  are grouped by the claim they can overturn, not by data type.
- **Centromere architecture — scale to instance.** A resource/map figure first
  defines the study object. A later variation figure moves through count,
  spatial relation, scale and internal structure before showing informative
  examples. The panels collectively explain which dimensions constitute the
  variation rather than announcing five unrelated discoveries.
- **Robin — discovery sequence.** The figure progression follows hypothesis
  generation, wet-lab testing, analysis and refined mechanism or hypothesis.
  The sequence preserves the scientific discovery loop because each result
  changes what is tested next.
- **TabPFN — capability ladder.** Early figures explain the system and learned
  behaviour; a benchmark figure combines aggregate performance, per-dataset
  generality and tuning-time efficiency; a later figure asks whether that
  performance claim survives uninformative features, outliers, reduced data
  and stronger competitors. The later figure escalates the claim instead of
  repeating that performance is good.

These examples support three portable distinctions:

1. several attacks on one claim can belong in one figure
2. population summaries and representative cases can be complementary steps
   in one figure
3. a later figure should normally ask a deeper question than the preceding
   figure

## Align figure order with Results claim escalation

The relationship works at two scales:

- **Within a figure:** panels are different sentences in one compact Results
  argument.
- **Across figures:** each figure should make a stronger or different claim
  that creates the next scientific question.

For example:

`Fig. 1: What is it? -> Fig. 2: Is the evaluation or resource credible? -> Fig. 3: Does the phenomenon exist? -> Fig. 4: Does it beat alternatives? -> Fig. 5: Does the claim survive harder conditions? -> Fig. 6: What mechanism, generality or boundary follows?`

This is an archetype, not a mandatory six-figure template. Apply the
claim-escalation audit from the shared Results–Discussion guidance. If two
figures can both be summarized as `X performs well`, merge them, demote the
weaker evidence, or revise the later figure around a deeper discriminator.

## Assign visual hierarchy from evidence hierarchy

- Give the decisive evidence the hero position or largest visual area.
- Keep controls and robustness panels quieter, but large enough to judge.
- Use one condition, cohort or method mapping consistently across panels.
- Do not force equal panel sizes when inferential importance differs.
- Use a setup schematic only when readers need it to interpret the evidence;
  do not add a decorative panel `a` by habit.
- Make the attack, negative result or failure boundary visible when it changes
  the figure-level claim.
- Keep axes, uncertainty definitions, sample definitions and comparator labels
  consistent whenever panels invite direct comparison. Disclose any change in
  `n`, denominator, cohort, estimator or scale.

## Decide whether a panel belongs in the main figure

Use the necessity test:

1. What unique inference disappears if this panel is removed?
2. Does that inference establish, advance, qualify or bound the figure-level
   claim?
3. Is it a distinct evidence role, or the same result under another metric,
   estimator, seed, threshold or visual encoding?

Then route it:

- **Main figure:** decisive evidence, a necessary control, a central
  falsification, or a conclusion-changing boundary.
- **Extended Data/SI:** reassurance, provenance detail, secondary metrics,
  alternative estimators, expanded subgroup views or robustness that does not
  change the central interpretation.
- **Another figure:** a genuinely separate major claim or the next rung of the
  manuscript's claim escalation.
- **Delete or merge:** a repeated view with no independent inference gain.

Do not hide a result that changes the conclusion merely because it is negative
or complicates the layout.

## Run the multi-panel audit

Complete this table before drawing and again after the final render:

| Panel | Scientific question | Evidence role | Decisive comparison | Unique inference gain | Claim dependency | Destination |
|---|---|---|---|---|---|---|
| a |  |  |  |  |  |  |
| b |  |  |  |  |  |  |
| c |  |  |  |  |  |  |

Audit the full figure:

- Can the figure-level claim be stated in one sentence with a verb?
- Do the panels collectively answer one Results-level question?
- Does every panel add a distinct inferential role rather than only a new
  metric or chart type?
- Does the panel order form a readable chain rather than a dashboard grid?
- Is the strongest evidence visually dominant?
- Are central controls, attacks and failure boundaries present?
- Would a moved panel fit Extended Data/SI without weakening the main claim?
- Does the next figure ask the question created by this figure?
- Can the caption explain what is shown and how to read it without replaying
  the full Results argument?
- At final physical size, are dependencies, shared encodings, uncertainty and
  panel transitions still legible?

The final design rule is: **do not begin with the number of datasets, metrics
or panels available. Begin with the one sentence the figure must establish,
then choose the few different evidence roles a skeptical reader needs to
believe it.**
