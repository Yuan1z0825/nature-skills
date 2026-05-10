# Output Contract

## Required outputs

```text
analysis_results.xlsx
three_line_tables.docx
methods_results.docx
logs/
```

## Excel workbook sheets

- Run info
- Column audit
- Numeric coercion log
- Data audit
- Descriptive statistics
- Group comparisons
- Three-line table data
- Paired comparisons
- ANCOVA
- Factorial ANOVA
- GLM
- Mixed models
- Skipped analyses

Optional when requested:

- Post hoc tests

## Word documents

### three_line_tables.docx

Publication-style tables using:

- variable names in rows
- groups in columns
- p-value column
- method column optional
- `mean ± SEM` for continuous variables
- `median (IQR)` for ordinal/score variables
- `a/b/c` letters for >=3 groups

### methods_results.docx

Includes:

- statistical methods paragraph
- data audit summary
- concise results narrative
- interpretation caution
