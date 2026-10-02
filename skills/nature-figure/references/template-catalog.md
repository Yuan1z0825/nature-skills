# Validated Plot Template Catalog

Use this catalog after the backend is resolved to Python and after `asset-adaptation.md` confirms that the requested panel matches a template semantically. These templates use only NumPy and Matplotlib, require real CSV input for production, and produce SVG, PDF, 600 dpi TIFF, and a count-based QA JSON record.

Run `python scripts/plot_templates.py <subcommand> --help` for the complete interface.

| Subcommand | Required CSV shape | Main safeguards |
|---|---|---|
| `volcano` | gene, effect-size, adjusted-p columns | positive p-value check, explicit thresholds, all points retained, large-data rasterization |
| `roc` | one FPR column plus one or more TPR columns | range check in `[0,1]`, stable FPR sorting, trapezoidal AUC recorded |
| `dotplot` | row category, column category, size, color | complete category-order validation, no silent category removal |
| `marginal` | x, y, optional group | preserves all observations, separates 2D joint structure from 1D marginal distributions |
| `paired` | pair ID, condition, value | exactly two conditions, rejects duplicate or incomplete pairs unless exclusion is explicit |

## Production examples

```bash
python skills/nature-figure/scripts/plot_templates.py volcano \
  --input results.csv --gene-col gene --effect-col log2fc --p-col padj \
  --output figures/volcano

python skills/nature-figure/scripts/plot_templates.py roc \
  --input roc.csv --fpr-col fpr --tpr-cols model_a,model_b \
  --output figures/roc

python skills/nature-figure/scripts/plot_templates.py dotplot \
  --input markers.csv --row-col cell_type --column-col gene \
  --size-col pct_exp --color-col avg_exp_scaled --output figures/markers
```

Never use `--demo` for a manuscript deliverable. It exists only for explicit smoke tests and is marked in the QA JSON. If required numeric data are missing or non-finite, the default is to stop. `--drop-incomplete` is an explicit exception that records exclusion counts; it is not permission to hide scientifically important missingness.

The templates do not compute hypothesis tests. Add statistics only after defining the replicate unit, test, assumptions, multiplicity correction, and legend reporting contract.
