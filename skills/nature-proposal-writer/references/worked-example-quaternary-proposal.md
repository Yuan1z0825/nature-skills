# Worked example: materials proposal revise-mode evaluation

This fictionalized example shows the expected depth of a revise-mode assessment without relying on a real project, person, or file path.

- **Mode**: revise
- **Text type**: doctoral proposal, first stage
- **Domain**: multicomponent high-temperature materials system

## Pipeline flow applied

1. Classify text → background and literature review, objectives, methodology, expected outcomes, and references.
2. Extract claims → scan each paragraph for scientific and feasibility claims.
3. Compare with canon → check every claim against literature, model boundaries, and supervisor constraints.
4. Diagnose structure → identify the strongest argument chain and sections overloaded with conditional outcomes.
5. Run anti-slop scan → check structural and language anti-patterns.
6. Score → assess all eight rubric dimensions independently.
7. Write revision brief → separate P0, P1, and P2 changes and state what should remain unchanged.

## Illustrative scoring

| Dimension | Score | Evidence-based reason |
|---|:---:|---|
| Research-question clarity | 7 | The question is identifiable but buried in the background. |
| Scientific tension | 8 | A real trade-off between performance and compatibility drives the project. |
| Evidence alignment | 6 | Model outputs are reported with more precision than the source figure supports. |
| Logic chain | 8 | The sequence from system limitation to candidate intervention is coherent. |
| Method feasibility | 6 | Atmosphere control and transition steps are underspecified. |
| Novelty | 6 | The contribution is implicit and not yet distinguished from the closest work. |
| Risk boundaries | 7 | Conditional outcomes are present, but the all-candidates-fail route is missing. |
| Language quality | 7 | No major template language, but the outcomes section is repetitive. |

Overall score: **6.9/10**. The draft is suitable for supervisor discussion after P0 fixes, but not ready for formal submission.

## Constraint checklist

Before revising prose, verify every project constraint explicitly:

- candidate selection is traceable to evidence or a declared model;
- environment and exposure controls are specified;
- material or sample categories match the approved scope;
- experimental flows are distinguishable and reproducible;
- later-stage platform work remains deferred;
- model outputs are labeled as predictions rather than measurements.

## What to watch for

### Unverifiable embedded figures

If a figure cannot be inspected, do not infer its content from the caption alone. Extract it with an appropriate document workflow, or report that figure-level verification remains incomplete.

### Precision inflation

Flag model or plot-derived values reported to more significant figures than the source supports. Prefer an approximate value, range, or uncertainty statement.

### Transition-step gaps

A flow such as “cool → sample → insert specimen → reheat” must specify environment control during every intermediate step. Transition steps often contain the highest contamination and reproducibility risk.

## Revision brief format

```markdown
## Revision Brief

### P0 — must fix
1. [Location] — [Problem] — [Required change] — [Acceptance criterion]

### P1 — strongly recommended
...

### P2 — optional optimization
...

### Preserve
- [Elements that already work and should not be rewritten]
```

Each item must identify a location, explain why the issue matters, prescribe a concrete change, and define how the revised text will be checked.
