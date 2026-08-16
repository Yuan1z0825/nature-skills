# Main-Text Discipline for Scientific Papers

Use this shared contract when drafting, restructuring, compressing, or revising
the main text of a scientific manuscript, especially Results. It operationalizes
an author-supplied writing discipline; it is not a journal policy. Current
journal instructions and field-specific reporting standards override it when
they require information in the main text.

## Contents

- [1. Separate evidence completeness from main-text completeness](#1-separate-evidence-completeness-from-main-text-completeness)
- [2. Classify every result before placement](#2-classify-every-result-before-placement)
- [3. Build the shortest sufficient evidence chain](#3-build-the-shortest-sufficient-evidence-chain)
- [4. Prevent revision accretion](#4-prevent-revision-accretion)
- [5. Separate main text, captions, and SI](#5-separate-main-text-captions-and-si)
- [6. Apply statistical reporting discipline](#6-apply-statistical-reporting-discipline)
- [7. Run the paragraph necessity test](#7-run-the-paragraph-necessity-test)
- [8. Stop explanatory recursion](#8-stop-explanatory-recursion)
- [9. Audit claim repetition](#9-audit-claim-repetition)
- [10. Return an auditable compression record](#10-return-an-auditable-compression-record)
- [Non-negotiable exceptions](#non-negotiable-exceptions)

## 1. Separate evidence completeness from main-text completeness

Preserve the complete evidential record across the manuscript, figures, tables,
Methods, source data, and Supplementary Information (SI). Do not force that full
record into the main text. Reserve main-text space for evidence that establishes,
advances, or materially bounds the central claim.

Do not use compression to hide inconvenient evidence. If an observation changes
the direction, magnitude, scope, or credibility of the central conclusion, keep
it visible in the main text even if it is nominally a robustness or subgroup
analysis.

## 2. Classify every result before placement

Build a result-allocation table before drafting or restructuring Results:

| Class | Decision test | Default destination |
|---|---|---|
| `core_discovery` | Does it advance the paper's central conclusion? | Main text, with adequate evidence |
| `necessary_support` | Must the reader see it to accept the core discovery? | Main text briefly |
| `qualification` | Does it materially bound or alter the central interpretation? | Main text if yes; otherwise SI |
| `robustness` | Does it show the result survives an alternative specification, estimator, seed, threshold, or inference procedure without changing the conclusion? | SI, with a concise pointer when useful |
| `heterogeneity` | Is variation across groups, settings, tasks, or models itself part of the central claim? | Main text if central; otherwise SI |
| `provenance_detail` | Does it document traceability, preprocessing, implementation, or audit detail without advancing the conclusion? | Methods, Source Data, repository, or SI |
| `alternative_inference` | Does it test the same claim using a secondary inferential route? | SI unless it changes acceptance of the claim |
| `edge_case` | Does it define a failure boundary that changes how the claim must be read? | Main text if interpretation changes; otherwise SI |

Classify by function in this paper, not by analysis name. An ablation can be a
core discovery in a mechanism paper; heterogeneity can be the headline result;
a confidence interval can be the primary inferential evidence.

## 3. Build the shortest sufficient evidence chain

After classification, write the minimum ordered chain that lets the reader:

1. understand the central observation
2. see the decisive comparison or mechanism evidence
3. judge the primary uncertainty or inference
4. understand any boundary that changes the conclusion

Do not reproduce the chronological record of analyses. Route supporting checks
to SI with stable pointers. Draft the final Results narrative only after the
analysis and result-allocation table are stable.

## 4. Prevent revision accretion

Every requested addition triggers a deletion check across the whole affected
paragraph:

1. State what new function the proposed sentence serves.
2. Find existing sentences that already serve that function.
3. Prefer replacement, combination, or compression before appending.
4. Re-read the paragraph after the edit and delete any sentence made redundant.
5. Re-run the paragraph necessity test and claim-repetition audit below.

For reviewer-driven edits, ask:

> Does this sentence tell the reader what was discovered, or does it mainly tell
> a reviewer why an objection does not overturn the result?

Keep the first in the main text when necessary. Route the second to SI or the
response letter unless the objection is essential to the central inference.
Answer every reviewer fully in the response letter even when the manuscript
change is deliberately short.

## 5. Separate main text, captions, and SI

- **Main text:** what was found, the decisive support, and what it means for the
  central claim.
- **Figure or table caption:** what is shown and how to read it, including
  definitions needed to interpret the display.
- **SI:** why the conclusion survives deeper scrutiny, including secondary
  analyses, robustness, implementation detail, extended diagnostics, and
  non-central edge cases.

Do not repeat a full set of effect sizes, confidence intervals, and P values in
both the main text and caption. Choose one authoritative location for the full
numeric report and use the other location for the minimum narrative or reading
cue. Preserve journal-mandated caption content.

## 6. Apply statistical reporting discipline

Compute and retain every analysis required by the design, protocol, reporting
standard, and integrity audit. In the main text, normally report:

- the descriptive quantity needed to understand the effect
- the primary inferential statistic or interval needed to support the claim

Route secondary intervals, alternative estimators or inference procedures,
multiplicity checks, sensitivity analyses, and model-level heterogeneity to SI
unless they change the conclusion or are required in the main text. Never select
only the most favorable statistic. Record the complete analysis family and the
reason for each reporting location.

## 7. Run the paragraph necessity test

For every Results paragraph, ask:

> If this paragraph were removed, would the reader still understand and have
> adequate evidence for the paper's central claim?

- **No:** keep it.
- **Yes, but a reviewer might ask for it:** route it to SI or the response letter.
- **Yes, and the point appears elsewhere:** delete it.

When only one sentence is necessary, keep that sentence and relocate the rest.
Do not preserve an unnecessary paragraph merely because one clause matters.

## 8. Stop explanatory recursion

Do not explain an explanation in the main text. If a statistical or graphical
detail needs several sentences to reconcile it with the main result, state the
result and any conclusion-changing boundary simply, then move the extended
reconciliation to SI. Keep the longer explanation in the main text only when the
reconciliation itself is part of the discovery.

## 9. Audit claim repetition

A major claim may be introduced, demonstrated, and synthesized, but each
appearance must perform a different function. Build a claim-location map across
the heading, transition, figure/table caption, Results paragraph, Discussion,
and closing sentence. For each occurrence, mark `introduce`, `demonstrate`,
`interpret`, `synthesize`, `shorten`, or `delete`.

Delete or compress restatements that add no new evidence, boundary, or
interpretation. Do not force the same full claim into every rhetorical slot.

## 10. Return an auditable compression record

For a Results or full-manuscript restructuring task, return or maintain:

1. **Result-allocation table:** result, class, effect on central interpretation,
   destination, and SI/caption pointer.
2. **Shortest evidence chain:** ordered main-text claims and their decisive
   evidence.
3. **Deletion log:** appended, replaced, compressed, relocated, or deleted text,
   with a short reason.
4. **Statistics-location record:** primary main-text report and secondary SI
   analyses.
5. **Claim-repetition map:** retained rhetorical function at each location.
6. **Word-count delta:** before and after for every revised Results subsection.

The prose remains the deliverable. Keep the audit compact unless the user asks
for the full table.

## Non-negotiable exceptions

- Do not move information required for reproducibility, research integrity,
  participant safety, ethics, or a mandatory reporting checklist merely to save
  words.
- Do not bury contradictory or conclusion-changing evidence in SI.
- Do not strip a qualification that prevents a misleading causal, clinical,
  societal, or generalization claim.
- Do not remove statistics required by the target journal, study design, or
  field standard.
- When the user or editor explicitly requires a point in the main text, comply
  but still replace or compress neighboring redundancy before appending.
