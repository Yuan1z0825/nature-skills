# Table Style

## Default Word table style

- Times New Roman
- 9 or 10 pt tables
- no vertical borders
- top border, header bottom border, bottom border
- compact rows
- clear footnote

## Default values

Continuous variables:

```text
mean ± SEMᵃ
```

Ordinal/score variables:

```text
median (IQR)ᵃ
```

P-value formatting:

- p < 0.001 shown as `≤0.001`
- otherwise 3 decimal places by default

Letter display:

- different letters indicate significant pairwise differences at p < 0.05
- identical letters indicate no significant difference
- if overall p >= 0.05, all groups may be shown with `a` or letters may be omitted according to configuration; default is all `a` for clarity in multi-group tables.
