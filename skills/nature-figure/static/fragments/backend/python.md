# Backend: Python (matplotlib / seaborn)

**Python-only execution rule.** When the user has selected Python, do all figure drawing, previewing, exporting, and visual QA in Python. Do not call R/ggplot2, ComplexHeatmap, patchwork, or any R graphics device to create a temporary preview, fallback export, or layout approximation. If Python or required Python plotting packages are missing, pause rendering, continue independent script or data checks, and report the missing dependency. You may still write the Python script, provide `pip`/environment install commands, or ask permission to install dependencies, but do not cross-render the figure in R.

## Python quick-start

```python
import matplotlib as mpl
import matplotlib.pyplot as plt
# Copy audit_panel_alignment.py beside the plotting source or add the skill's
# scripts directory to PYTHONPATH before importing it.
from audit_panel_alignment import require_matplotlib_panel_alignment

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "svg.fonttype": "none",     # editable text in SVG
    "pdf.fonttype": 42,         # editable TrueType text in PDF
    "font.size": 7,             # use 15-24 only for large slide-sized panels
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
})

def save_pub_py(fig, filename, dpi=600):
    # Run after every layout-affecting change, before export. Single-panel
    # figures record NOT APPLICABLE; unresolved multi-panel geometry blocks.
    require_matplotlib_panel_alignment(
        fig,
        json_out=f"{filename}.alignment.json",
        overlay_svg=f"{filename}.alignment.svg",
        tolerance_pt=1.5,
        gutter_tolerance_pt=1.5,
        strict=True,
    )
    fig.savefig(f"{filename}.svg", bbox_inches="tight")
    fig.savefig(f"{filename}.pdf", bbox_inches="tight")
    fig.savefig(f"{filename}.tiff", dpi=dpi, bbox_inches="tight")
```

Use `text.usetex = True` only when LaTeX is installed and math-rich labels are required.

## Going deeper

- `references/api.md` — Python PALETTE, helper function signatures, validation rules.
- `references/template-catalog.md` — validated CSV-driven volcano, ROC, dot-plot, marginal, and paired templates backed by `scripts/plot_templates.py`.
- `references/common-patterns.md` — hero panels, legend-only axes, dark image plates, asymmetric layouts.
- `references/chart-types.md` — radar, 3D sphere, fill_between, scatter patterns.
- `references/tutorials.md` — end-to-end walkthroughs for bars, trends, heatmaps.
- `references/demos.md` — third-party figures4papers demo map, copyright boundary, and original Python reimplementation guidance.
- `scripts/validate_figure.py` — dependency-free source preflight before rendering and visual QA.
- `scripts/audit_pdf_text.py` — dependency-free `Tf` scan of exported PDF text runs; use it to enforce the 5 pt glyph floor after rendering.
- `scripts/audit_panel_alignment.py` — mandatory render-time Matplotlib axes alignment gate for every multi-panel figure; call `require_matplotlib_panel_alignment()` after the final layout draw and before export.
- `scripts/audit_figure_collisions.py` — mandatory PyMuPDF geometry audit after every generated or layout-affecting revision; fix text-text, text-stroke and clipping FAIL findings before delivery.
- `scripts/figure_safety.py` — strict monotone interpolation and annotation placement above uncertainty extents.
