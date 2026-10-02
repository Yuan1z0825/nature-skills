# Difficult cases

## Contents

- [Impossible or out-of-scope experiment](#impossible-or-out-of-scope-experiment)
- [Reviewer factual error](#reviewer-factual-error)
- [Conflicting reviewer requests](#conflicting-reviewer-requests)
- [Repeated concerns across reviewers](#repeated-concerns-across-reviewers)
- [Reviewer-requested citation](#reviewer-requested-citation)
- [Major statistical critique](#major-statistical-critique)
- [Ethics, compliance, or data-integrity critique](#ethics-compliance-or-data-integrity-critique)
- [Transfer after review](#transfer-after-review)
- [Appeal-like case](#appeal-like-case)


Use this file when comments cannot be handled with straightforward acceptance and revision.

## Impossible or out-of-scope experiment

Use when the requested work requires a new cohort, long follow-up, new animal model, new clinical
trial, new platform, or different study design.

Strategy:

1. Acknowledge scientific value.
2. Explain the study-design or scope boundary.
3. Offer alternative evidence if supplied.
4. Soften the claim or add a limitation.
5. Avoid time, budget, convenience, or ability excuses.

Template:

```text
We agree that [experiment] would provide an additional test of [claim]. However, the central
conclusion of the present study is based on [existing evidence], and the requested experiment
would require [new system/cohort/longitudinal design] beyond the scope of this revision.
To avoid overstatement, we have revised [location] to acknowledge this limitation and now state
that [revised text or placeholder].
```

## Reviewer factual error

Use when the reviewer appears to have missed existing data or made a factually incorrect statement.

Strategy:

1. Do not accuse the reviewer.
2. Do not say that the answer was already stated or that the reviewer should have found it.
3. Treat the missed point as evidence that the original presentation was not sufficiently clear or visible.
4. Answer the scientific concern directly.
5. Make or propose a small wording, placement, signposting, legend, or cross-reference improvement.
6. Cite the revised manuscript location or use a visible placeholder when the author has not supplied it.

Template:

```text
We appreciate the reviewer raising this point. We agree that the original presentation did not
make [specific point] sufficiently clear. We have therefore revised [location] to state that
[revised text or faithful summary].
```

## Conflicting reviewer requests

Use when two reviewers ask for incompatible changes.

Strategy:

1. Surface the conflict internally in the strategy summary.
2. Prioritize explicit editor instructions if supplied.
3. Find the minimal revision that satisfies both concerns.
4. Avoid making incompatible promises.
5. Draft each reviewer-facing response independently using only that reviewer's concern and the manuscript evidence.
6. Do not tell either reviewer what another reviewer requested, recommended, or received in response.

The internal/editor master may explain the conflict. A reviewer-facing response must not. For
example, do not write "Reviewer 2 requested the opposite" or "as noted in our response to Reviewer
1". Explain the same scientifically coherent manuscript decision separately to each reviewer.

## Repeated concerns across reviewers

Use when two or more reviewers independently raise the same issue.

Strategy:

1. Link the duplicate concerns only in the internal/editor master.
2. Keep one scientifically consistent manuscript action.
3. Give each reviewer a complete standalone explanation of that action.
4. Do not save space by referring one reviewer to another reviewer's response.

## Reviewer-requested citation

Use when a reviewer asks for a specific citation or broader literature coverage.

Strategy:

1. Evaluate relevance.
2. Add only genuinely relevant and verified citations.
3. Do not imply coercion or reviewer self-citation.
4. Use neutral positioning language.
5. If citation metadata is missing, use `AUTHOR_INPUT_NEEDED`.

## Major statistical critique

Treat as high risk or blocking until details are supplied.

Request:

- statistical test name
- replicate unit
- sample size or replicate count
- effect size or estimate when relevant
- confidence interval when relevant
- p-value only when supplied and appropriate
- multiple-testing correction
- software and version if relevant
- Methods and Results locations

Do not invent statistical output.

## Ethics, compliance, or data-integrity critique

Usually `BLOCKING` until author provides exact facts.

Request:

- ethics approval body and approval number
- consent statement
- animal or human-subject reporting details
- competing-interest correction
- image-processing or data-integrity explanation
- data, code, materials, or accession information

Do not write around missing required compliance.

## Transfer after review

Use when a manuscript is transferred with reviewer reports.

Strategy:

1. Identify whether the receiving journal expects a response to transferred reports.
2. Preserve reviewer IDs from the transferred review package when possible.
3. Address comments as normal revision concerns unless the new editor gives different instructions.
4. Flag journal-specific formatting or scope differences.

## Appeal-like case

Appeals are not ordinary revision responses.

Route separately when:

- the user wants to challenge rejection rather than revise;
- the decision letter invites an appeal path;
- the author alleges major factual error, bias, or process failure;
- no revised manuscript is being prepared.

Default action:

```text
This appears to be an appeal-like case rather than a revision response. `nature-response`
can identify the disputed points, but a full appeal letter should be handled as a separate task
with journal-specific appeal rules.
```
