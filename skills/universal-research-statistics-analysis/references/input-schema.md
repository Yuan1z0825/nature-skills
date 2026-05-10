# Input Schema

## Supported file formats

- `.csv`
- `.xlsx`

## Recommended columns

| Role | Example names | Required? |
|---|---|---|
| Group/treatment | Group, Treatment, Arm, Diet | Required for group comparisons |
| Subject ID | SubjectID, AnimalID, ParticipantID, ID | Required for paired/mixed/repeated models |
| Time | Time, Visit, Day, Week | Required for timepoint models |
| Period | Period | Optional crossover model |
| Sequence | Sequence | Optional crossover model |
| Carryover | Carryover | Optional crossover sensitivity |
| Baseline | Baseline, Pre, Day0 | Optional ANCOVA |
| Endpoint | Final, Post, Endpoint | Optional ANCOVA |

## Partial data policy

The Skill must analyze whatever valid modules are present. Missing modules are skipped without error and recorded in `Skipped analyses` or logs.

## Numeric coercion policy

- Convert fully numeric strings, including comma decimals (`70,25` → `70.25`).
- Convert threshold-like strings (`<0.001`, `≤0.001`) to their numeric boundary for audit fields.
- Do **not** convert categorical labels containing letters and digits (`A30`, `P40`, `T1`, `Dose2`) to numbers.
