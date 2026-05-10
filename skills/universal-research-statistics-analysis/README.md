# Universal Research Statistics Analysis

This Skill analyzes common research datasets from CSV/XLSX files and automatically generates:

- Excel workbook with audit trails and statistical results
- Word three-line tables
- Word Methods + Results draft
- optional PNG/PDF figures

It is deliberately domain-neutral. Domain-specific skills can wrap this core and add variable dictionaries, preferred table grouping, and field-specific interpretation language.

## Minimal command

```bash
python scripts/analyze_research_data.py --input data.csv --outdir results --group-col Group
```

## Recommended data structure

Each row should represent one observation. Typical columns:

```text
SubjectID, Group, Time, Period, Sequence, Sex, Age, Outcome1, Outcome2, ...
```

Only `Group` and at least one numeric outcome are required for independent group comparisons.
