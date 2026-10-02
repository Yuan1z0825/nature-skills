# Technical concern taxonomy

Use this reference to build an internal concern ledger after the five source-grounded Nature axes have been assessed. It is a coverage and traceability aid, not an official journal taxonomy, reviewer-persona selector, or historical-frequency model.

## Twelve internal axes

| Axis | Check only when applicable |
|---|---|
| `novelty-significance` | The claimed advance is distinguished from prior work and its importance is supported rather than asserted. |
| `mechanism-evidence` | Mechanistic statements are supported by discriminating evidence rather than a compatible observation alone. |
| `experimental-design` | Comparators, controls, replication units, conditions, sampling, and bias controls support the stated inference. |
| `statistical-rigor` | Estimands, assumptions, uncertainty, multiplicity, power, and model validation are adequate for the claim. |
| `reproducibility` | Methods, code, data, versions, seeds, protocols, and reporting detail permit independent scrutiny or reuse where appropriate. |
| `clinical-validity` | Cohort definition, endpoint choice, external validation, calibration, clinical utility, and generalizability support clinical claims. |
| `ethical-governance` | Human/animal approvals, consent, privacy, dual-use, permissions, and responsible data handling are reported when required. |
| `data-resource-quality` | Dataset completeness, provenance, documentation, quality control, accessibility, and intended reuse are credible. |
| `figures-and-tables` | Visual encodings, labels, denominators, uncertainty, scale bars, legends, and accessibility accurately represent the results. |
| `writing-clarity` | The argument, terminology, abstract/body consistency, and nonspecialist explanation make the evidence chain understandable. |
| `claim-moderation` | Strength, scope, novelty, generality, and translational language do not exceed the supplied evidence. |
| `causal-vs-correlative` | Association, prediction, mediation, intervention, and causation are distinguished according to study design and evidence. |

## Applicability rule

For every axis, record one of:

- `applicable`: the manuscript makes a claim or presents evidence that activates the check;
- `not applicable`: the axis is genuinely outside the manuscript's design or claims;
- `not assessable`: the axis could matter, but the supplied material is insufficient.

Do not turn `not assessable` into a presumed flaw. State the assessment boundary when the missing material affects confidence.

## Concern construction

Emit a concern only when it is supported by the supplied manuscript material. Record:

- `issue_key`: a concise normalized key used to detect overlap;
- `axis`: one primary technical axis;
- `severity`: `major` or `minor` according to effect on the authors' case;
- `blocking`: `yes` or `no`; only a Major Concern may be blocking;
- `severity_rationale`: one sentence explaining the concern's effect on the central case;
- `claim_pointer`: a faithful paraphrase of the challenged claim or affected reporting element;
- `evidence_pointer`: a verified section, figure, table, page, or line location;
- `evidence_status`: `located`, `location_missing`, or `not_assessable`;
- `concern`: why the visible evidence does not yet support the claim or reporting need;
- `resolution_test`: what evidence, analysis, clarification, or claim adjustment would close the concern.

Use `location not provided` when the critique is grounded but the exact location cannot be verified. Never manufacture a location to make the ledger look complete.

## Severity and blocking calibration

Classify impact, not tone, difficulty, cost, or preferred reviewer style.

| Classification | Use when | Typical resolution |
|---|---|---|
| `major`, `blocking: yes` | The current evidence cannot establish a central conclusion, or a validity, ethics, governance, or data-integrity problem prevents a credible scientific case. | Decisive evidence or analysis, correction of the invalid design/reporting, transparent integrity resolution, or narrowing/removal of the unsupported central claim. |
| `major`, `blocking: no` | The issue materially weakens inference, novelty, significance, generalizability, reproducibility, or an important part of the evidence chain, but does not by itself invalidate the entire central case. | Substantive analysis, validation, methodological clarification, structural revision, stronger comparison, or meaningful claim moderation. |
| `minor`, `blocking: no` | The issue is localized and does not change the central conclusion or interpretation of the core evidence. | Precise wording, definition, citation, figure/table/legend correction, localized reporting detail, or limited clarification. |

Calibration rules:

- A missing detail is Major when it prevents evaluation or reproduction of a result central to the
  paper; it is Minor when the result remains interpretable and the correction is localized.
- A figure or statistical issue is not automatically Minor. Misleading uncertainty, denominators,
  scales, tests, or replicate definitions may be Major or blocking when they affect inference.
- A writing issue is Major when ambiguity changes the main claim or scientific interpretation;
  ordinary clarity, terminology, and formatting issues are Minor.
- `not assessable` is an evidence-status label, not a severity. Do not convert absent material into
  a Major Concern unless the supplied package was expected to contain it and the omission itself is
  verifiable.
- Minor Comments must be actionable and manuscript-specific; omit taste-only copyediting.
- Never manufacture concerns to meet a numeric quota. Use `None identified from the supplied
  material` when a severity tier has no grounded item.

## Reviewer-local use

- Keep the visible labels as `Reviewer 1`, `Reviewer 2`, and `Reviewer 3` with preassigned emphasis briefs.
- Apply the taxonomy independently inside each isolated reviewer context. Do not allocate concerns or axes based on another report.
- Do not expose specialist personas such as `Statistics Reviewer` or infer reviewer-selection history.
- Use reviewer-local issue keys while drafting. Map equivalent concerns to synthesis keys only after all reports are frozen.
- Classify Major and Minor concerns according to evidence and emphasis, not fixed counts. A reviewer
  may legitimately have no concern at one severity level.
