# API Reference — Nature Figure Making

## Contents

- [Constants](#constants)
- [MANDATORY font + SVG rules (always first, no exceptions)](#mandatory-font-svg-rules-always-first-no-exceptions)
- [apply_publication_style()](#apply_publication_style)
- [is_dark(hex_color, threshold=128)](#is_darkhex_color-threshold128)
- [add_panel_label(ax, label, ...)](#add_panel_labelax-label)
- [style_dark_image_ax(ax, ...)](#style_dark_image_axax)
- [make_grouped_bar(ax, categories, series, labels, ...)](#make_grouped_barax-categories-series-labels)
- [make_trend(ax, x, y_series, labels, ...)](#make_trendax-x-y_series-labels)
- [make_forest_plot(ax, labels, estimates, ci_low, ci_high, ...)](#make_forest_plotax-labels-estimates-ci_low-ci_high)
- [make_heatmap(ax, matrix, ...)](#make_heatmapax-matrix)
- [Numerical and annotation safety helpers](#numerical-and-annotation-safety-helpers)
- [require_matplotlib_panel_alignment(fig, ...)](#require_matplotlib_panel_alignmentfig-)
- [finalize_figure(fig, out_path, ...)](#finalize_figurefig-out_path)
- [Validation Rules](#validation-rules)
- [Conventions](#conventions)


Conventions, constants, and reusable code blocks. Implement in your script or adapt as needed.

---

## Constants

### PALETTE

```python
PALETTE = {
    "blue_main":      "#0F4D92",
    "blue_secondary": "#3775BA",
    "green_1": "#DDF3DE",
    "green_2": "#AADCA9",
    "green_3": "#8BCF8B",
    "red_1":   "#F6CFCB",
    "red_2":   "#E9A6A1",
    "red_strong": "#B64342",
    "neutral_light": "#CFCECE",
    "neutral_mid":   "#767676",
    "neutral_dark":  "#4D4D4D",
    "neutral_black": "#272727",
    "gold":   "#FFD700",
    "teal":   "#42949E",
    "violet": "#9A4D8E",
    "magenta":"#EA84DD",
}

DEFAULT_COLORS = [
    PALETTE["blue_main"],
    PALETTE["green_3"],
    PALETTE["red_strong"],
    PALETTE["teal"],
    PALETTE["violet"],
    PALETTE["neutral_light"],
]

PALETTE_NMI_PASTEL = {
    "baseline_dark": "#484878",
    "baseline_mid":  "#7884B4",
    "baseline_soft": "#B4C0E4",
    "ours_tiny":  "#E4E4F0",
    "ours_base":  "#E4CCD8",
    "ours_large": "#F0C0CC",
    "bg_lilac": "#E0E0F0",
    "bg_aqua":  "#E0F0F0",
    "bg_peach": "#F0E0D0",
    "neutral_light": "#D8D8D8",
    "neutral_mid":   "#A8A8A8",
    "neutral_dark":  "#606060",
    "delta_up":   "#2E9E44",
    "delta_down": "#E53935",
}

DEFAULT_COLORS_NMI_PASTEL = [
    PALETTE_NMI_PASTEL["baseline_dark"],
    PALETTE_NMI_PASTEL["baseline_mid"],
    PALETTE_NMI_PASTEL["baseline_soft"],
    PALETTE_NMI_PASTEL["ours_tiny"],
    PALETTE_NMI_PASTEL["ours_base"],
    PALETTE_NMI_PASTEL["ours_large"],
]

PALETTE_NATURE_IMAGING = {
    "bg": "#000000",
    "context": "#B8B8B8",
    "cyan": "#22D7E6",
    "magenta": "#FF2AD4",
    "white": "#FFFFFF",
}

PALETTE_NATURE_MATERIAL = {
    "aqua": "#77D7D1",
    "teal": "#33B5A5",
    "lilac": "#B9A7E8",
    "violet": "#7C6CCF",
    "callout_red": "#E53935",
    "neutral": "#D9D9D9",
}

PALETTE_NATURE_CLINICAL = {
    "baseline": "#272727",
    "week6": "#E28E2C",
    "week13": "#D24B40",
    "week26": "#5B8FD6",
    "year1": "#7BAA5B",
    "year2": "#C45AD6",
    "group_band": "#F2E6D9",
}

PALETTE_NATURE_GENOMICS = {
    "neutral_light": "#D8D8D8",
    "neutral_mid": "#8F8F8F",
    "wave1": "#D9544D",
    "wave2": "#5B7FCA",
    "wave3": "#B89BD9",
    "outline": "#4D4D4D",
}
```

Use `DEFAULT_COLORS` when color itself carries explicit semantic meaning (`hero`, `baseline`, `positive variant`).
Use `DEFAULT_COLORS_NMI_PASTEL` when several compared methods belong to one or two related families and the page
should feel visually unified.

---

## MANDATORY font + SVG rules (always first, no exceptions)

These three lines are **non-negotiable** and must appear at the top of every script,
before any figure is created. They guarantee editable text in SVG output:

```python
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['svg.fonttype'] = 'none'   # keeps text as <text> nodes, not paths
```

**Why `svg.fonttype = 'none'`**: matplotlib's default (`'path'`) converts every
glyph to a bezier path, making text unselectable, unsearchable, and impossible to
re-align in Illustrator / Inkscape. With `'none'`, text stays as SVG `<text>` elements
and font substitution happens at render time.

**Output format**: always save as `.svg` (primary). PNG/PDF are optional secondary
exports. Never use `.png` alone when the figure contains text that may need adjustment.

---

## apply_publication_style()

```python
def apply_publication_style(font_size=16, axes_linewidth=2.5, use_tex=False):
    """Apply Nature-style rcParams. Call once before creating any figures."""
    # ── MANDATORY: editable SVG text ──────────────────────────────────────────
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    plt.rcParams['svg.fonttype'] = 'none'
    # ── Layout & style ────────────────────────────────────────────────────────
    plt.rcParams['font.size'] = font_size
    plt.rcParams['axes.spines.right'] = False
    plt.rcParams['axes.spines.top'] = False
    plt.rcParams['axes.linewidth'] = axes_linewidth
    plt.rcParams['legend.frameon'] = False
    if use_tex:
        plt.rcParams['text.usetex'] = True
```

**Presets:**
- Large bar panels: `apply_publication_style(font_size=24, axes_linewidth=3)`
- Compact figures: `apply_publication_style(font_size=15, axes_linewidth=2)`
- Dense journal-width multi-panels: `apply_publication_style(font_size=8, axes_linewidth=1)`
- LaTeX labels: `apply_publication_style(use_tex=True)`

---

## is_dark(hex_color, threshold=128)

```python
def is_dark(hex_color, threshold=128):
    """Return True if hex color is dark (use white text on it)."""
    c = hex_color.lstrip('#')
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return (0.299*r + 0.587*g + 0.114*b) < threshold
```

---

## add_panel_label(ax, label, ...)

```python
def add_panel_label(ax, label, x=0, y=1, x_offset_pt=-4, y_offset_pt=3,
                    fontsize=8, color='black', fontweight='bold', va='bottom'):
    """Place a panel label with a fixed physical offset from an axes anchor."""
    from matplotlib.transforms import ScaledTranslation
    offset = ScaledTranslation(
        x_offset_pt / 72,
        y_offset_pt / 72,
        ax.figure.dpi_scale_trans,
    )
    ax.text(
        x, y, label,
        transform=ax.transAxes + offset,
        fontsize=fontsize,
        fontweight=fontweight,
        color=color,
        ha='left',
        va=va,
    )
```

The point offset keeps labels aligned when one panel spans two rows and its
neighbouring axes are shorter; a shared axes-fraction offset such as `y=1.02`
would produce different physical displacements. For dark image plates, move
the label inside the panel and switch to white:
`add_panel_label(ax, 'a', x=0.01, y=0.98, x_offset_pt=0, y_offset_pt=0, color='white', va='top')`

---

## style_dark_image_ax(ax, ...)

```python
def style_dark_image_ax(ax, facecolor='black'):
    """Prepare an axes for microscopy / rendering plates."""
    ax.set_facecolor(facecolor)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax
```

---

## make_grouped_bar(ax, categories, series, labels, ...)

```python
def make_grouped_bar(ax, categories, series, labels,
                     ylabel='Value', colors=None,
                     annotate=False, bar_width=0.8,
                     series_spread=None, error_kw=None):
    """
    Grouped bar chart.

    Parameters
    ----------
    ax         : matplotlib Axes
    categories : list[str]  — x-axis category names (length K)
    series     : list[array] — one array per group (each length K)
    labels     : list[str]  — legend label per group
    ylabel     : str
    colors     : list[str] | None  — defaults to DEFAULT_COLORS; override with
                                     DEFAULT_COLORS_NMI_PASTEL for unified-family figures
    annotate   : bool  — print value above each bar
    bar_width  : float — total width for all bars in one category
    error_kw   : dict  — passed to ax.bar as error_kw
    series_spread : list[array] | None — one uncertainty array per series

    Returns
    -------
    list[BarContainer]
    """
    import numpy as np
    if colors is None:
        colors = DEFAULT_COLORS
    if error_kw is None:
        error_kw = {'elinewidth': 2, 'capthick': 2, 'capsize': 10}
    n_groups = len(series)
    n_cats = len(categories)
    w = bar_width / n_groups
    x = np.arange(n_cats)
    flat_values = np.concatenate([np.asarray(values, dtype=float) for values in series])
    label_pad = 0.02 * max(float(np.ptp(flat_values)), float(np.max(np.abs(flat_values))), 1.0)
    containers = []
    for i, (vals, label, color) in enumerate(zip(series, labels, colors)):
        spread = None if series_spread is None else np.asarray(series_spread[i], dtype=float)
        offset = (i - (n_groups - 1) / 2) * w
        bars = ax.bar(x + offset, vals, width=w, label=label,
                      color=color, edgecolor='black', linewidth=1.5,
                      yerr=spread, error_kw=error_kw)
        containers.append(bars)
        if annotate:
            for j, (bar, val) in enumerate(zip(bars, vals)):
                upper = bar.get_height() + (0 if spread is None else spread[j])
                ax.text(bar.get_x() + bar.get_width() / 2,
                        upper + label_pad,
                        f'{val:.2f}', ha='center', va='bottom', fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel(ylabel)
    ax.legend()
    return containers
```

---

## make_trend(ax, x, y_series, labels, ...)

```python
def make_trend(ax, x, y_series, labels,
               colors=None, ylabel=None, xlabel=None,
               show_shadow=True, shadow_alpha=0.15,
               lw=2.5, marker='o', markersize=8):
    """
    Multi-line trend plot.

    Parameters
    ----------
    x        : array-like   — shared x values
    y_series : list[array]  — one 1D array per line
    labels   : list[str]
    show_shadow : bool  — fill_between ± std if y_series contains 2D arrays (rows=runs)
    """
    import numpy as np
    if colors is None:
        colors = DEFAULT_COLORS
    for y, label, color in zip(y_series, labels, colors):
        y = np.asarray(y)
        if y.ndim == 2:
            mean, std = y.mean(0), y.std(0)
        else:
            mean, std = y, None
        ax.plot(x, mean, color=color, lw=lw, marker=marker,
                markersize=markersize, label=label)
        if show_shadow and std is not None:
            ax.fill_between(x, mean - std, mean + std,
                            color=color, alpha=shadow_alpha)
    if ylabel:
        ax.set_ylabel(ylabel)
    if xlabel:
        ax.set_xlabel(xlabel)
    ax.legend()
```

---

## make_forest_plot(ax, labels, estimates, ci_low, ci_high, ...)

```python
def make_forest_plot(ax, labels, estimates, ci_low, ci_high,
                     colors=None, ref=0.0, xlabel=None, xlim=None,
                     marker='o', markersize=5, lw=1.5):
    """
    Minimal forest plot helper for Nature-style clinical/statistical panels.
    """
    import numpy as np
    y = np.arange(len(labels))[::-1]
    if colors is None:
        colors = ['#B64342'] * len(labels)
    for yi, est, lo, hi, color in zip(y, estimates, ci_low, ci_high, colors):
        ax.plot([lo, hi], [yi, yi], color=color, lw=lw)
        ax.plot(est, yi, marker=marker, ms=markersize, color=color)
    ax.axvline(ref, color='#767676', linestyle='--', linewidth=1.2, alpha=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    if xlabel:
        ax.set_xlabel(xlabel)
    if xlim is not None:
        ax.set_xlim(xlim)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
```

Use pale `ax.axhspan(...)` bands behind contiguous label groups when you need the
clinical-triptych look from `Nature`.

---

## make_heatmap(ax, matrix, ...)

```python
def make_heatmap(ax, matrix, x_labels=None, y_labels=None,
                 cmap='magma', cbar_label=None, annotate=False,
                 fmt='{:.2f}', fontsize=12):
    """
    2D heatmap with optional colorbar and cell annotations.
    """
    import numpy as np
    import matplotlib as mpl
    im = ax.imshow(matrix, cmap=cmap, aspect='auto')
    if cbar_label:
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.set_label(cbar_label)
    if x_labels:
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, rotation=30, ha='right', rotation_mode='anchor')
    if y_labels:
        ax.set_yticks(range(len(y_labels)))
        ax.set_yticklabels(y_labels)
    if annotate:
        norm = mpl.colors.Normalize(vmin=matrix.min(), vmax=matrix.max())
        cm_obj = plt.get_cmap(cmap)
        for (i, j), val in np.ndenumerate(matrix):
            r, g, b, _ = cm_obj(norm(val))
            lum = 0.299*r + 0.587*g + 0.114*b
            color = 'white' if lum < 0.5 else 'black'
            ax.text(j, i, fmt.format(val), ha='center', va='center',
                    fontsize=fontsize, color=color)
    ax.set_frame_on(False)
```

---

## Numerical and annotation safety helpers

Copy `scripts/figure_safety.py` beside the plotting script, or add that scripts directory to `PYTHONPATH`. Then import the tested helpers rather than calling `np.interp` directly on a curve whose direction has not been asserted:

```python
from figure_safety import interp_monotone, label_y_above

n_equivalent = interp_monotone(target_error, error_curve, example_counts)
label_y = label_y_above(metric_center, metric_spread)
```

`interp_monotone` accepts strictly increasing or decreasing `xp`, reverses a decreasing grid and its paired values together, and rejects duplicates/direction changes. `label_y_above` places a shared annotation above the upper uncertainty extent rather than relying on a fixed `LABEL_Y`.

For compact mathematical labels, prefer supported Unicode glyphs such as `R²` over `$R^2$` when the meaning is unchanged, then audit the exported PDF:

```bash
python skills/nature-figure/scripts/audit_pdf_text.py figure.pdf --min-pt 5
python skills/nature-figure/scripts/audit_figure_collisions.py figure.pdf \
  --json-out figure.collision-audit.json \
  --overlay-pdf figure.collision-audit.pdf
```

---

## require_matplotlib_panel_alignment(fig, ...)

For every multi-panel figure, measure the final Matplotlib axes positions after
the last `tight_layout`, constrained-layout draw, legend, colorbar or manual
position change and before saving. Copy `scripts/audit_panel_alignment.py`
beside the plotting source or add the skill's scripts directory to
`PYTHONPATH`, then use the blocking helper:

```python
from audit_panel_alignment import require_matplotlib_panel_alignment

alignment = require_matplotlib_panel_alignment(
    fig,
    json_out="figures/figure.alignment.json",
    overlay_svg="figures/figure.alignment.svg",
    tolerance_pt=1.5,
    gutter_tolerance_pt=1.5,
    require_panel_labels=True,
    strict=True,
)
```

The helper calls `fig.canvas.draw()` and converts final axes positions to
physical points. Ordinary `plt.subplots()` and `GridSpec` layouts infer row and
column groups from `SubplotSpec`, then check:

- common top/bottom edges and equal heights within each row;
- equal final widths for three or four same-row panels with equal grid spans;
- common left/right edges and equal widths within each column;
- shared top/bottom or left/right grid boundaries when adjacent panels have
  unequal spans, including `left two + right one` and `left one + right two`;
- repeated horizontal/vertical gutters;
- bold lowercase top-left panel-label anchors when detectable;
- plot-area rectangle overlap.

Ordinary unequal-span `GridSpec` layouts are inferred automatically: a two-row
spanning panel is compared with the appropriate upper and lower small panels at
the shared outer edges, without imposing an invalid equal-height comparison.
For ordinary horizontal `1 × 3` and `1 × 4` grids, equal column spans must also
produce equal final plot-area widths. An intentional unequal `width_ratios`
layout needs a panel-specific `panel-width` exemption with a reason.
For nested or separately created grids, declare intended comparisons instead
of asking the auditor to guess them:

```python
require_matplotlib_panel_alignment(
    fig,
    axes=[ax_a, ax_b, ax_c, ax_d],
    panel_ids=["a", "b", "c", "d"],
    row_groups=[["a", "b"], ["c", "d"]],
    column_groups=[["a", "c"], ["b", "d"]],
    exclude_axes=[colorbar.ax, inset_ax],
    exemptions=[
        {
            "panels": ["a"],
            "checks": ["column", "panel-width"],
            "reason": "hero panel intentionally spans two grid columns",
        }
    ],
    json_out="figures/figure.alignment.json",
    strict=True,
)
```

Every exemption needs panel ids, exact checks and a reason. Prefer omitting a
hero panel, inset, legend-only axis or colorbar from unrelated comparison groups
over globally increasing the `1.5 pt` tolerance. Exit-equivalent failures raise
`PanelAlignmentError`; do not catch and ignore it in a delivery script. A
single-panel figure is outside this gate, while a multi-panel figure without
valid comparable groups is `NOT AUDITABLE`, not a pass.

The optional SVG contains measured rectangles only and is QA-only. Preserve
the JSON with the figure bundle, then run PDF glyph and collision QA on the
exported figure.

---

## finalize_figure(fig, out_path, ...)

```python
def finalize_figure(fig, out_path, formats=None, dpi=300,
                    pad=2, bbox_inches=None, close=True,
                    alignment_options=None):
    """
    Apply tight_layout and save figure. For multi-panel figures, run
    require_matplotlib_panel_alignment() after this layout operation and before
    the save loop; do not close the figure before alignment QA.

    Parameters
    ----------
    out_path : str   — path without extension, or with extension
    formats  : list  — e.g. ['png', 'pdf']. If None, uses extension of out_path.
    dpi      : int   — 300 standard, 600 for dense bar panels
    pad      : float — tight_layout pad (2 default, 1 for compact multi-panel)
    alignment_options : dict | None — explicit groups/exemptions for unusual layouts
    """
    import os
    from pathlib import Path
    base = Path(out_path)
    if formats is None:
        formats = [base.suffix.lstrip('.') or 'png']
        base = base.with_suffix('')
    os.makedirs(base.parent, exist_ok=True)
    fig.tight_layout(pad=pad)
    options = {} if alignment_options is None else dict(alignment_options)
    require_matplotlib_panel_alignment(
        fig,
        json_out=str(base) + ".alignment.json",
        overlay_svg=str(base) + ".alignment.svg",
        strict=True,
        **options,
    )
    saved = []
    for fmt in formats:
        p = str(base) + f'.{fmt}'
        kw = {}
        if bbox_inches is not None:
            kw['bbox_inches'] = bbox_inches
        fig.savefig(p, dpi=dpi, **kw)
        saved.append(p)
    if close:
        plt.close(fig)
    return saved
```

---

## Validation Rules

- `make_grouped_bar`: `len(categories)` must equal length of each array in `series`.
- `make_grouped_bar`: if `series_spread` is supplied, it must mirror `series`; annotations clear `value + spread`.
- `make_trend`: each array in `y_series` must have same length as `x`.
- `make_trend`: 2D run/seed arrays show a standard-deviation band by default; use a different definition only when explicitly justified and documented.
- `make_heatmap`: `matrix` must be 2D; `x_labels` length = `matrix.shape[1]`; `y_labels` length = `matrix.shape[0]`.
- `finalize_figure`: supported formats — `png`, `pdf`, `svg`, `eps`, `jpg`, `tif`.

---

## Conventions

- Save outputs under `./figures/` (or path given by user); `finalize_figure` creates parent dirs.
- In headless / batch runs, set non-interactive backend before importing pyplot:
  ```python
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  ```
- Always `plt.close(fig)` after saving to free memory.
- For multi-panel figures, prefer one baseline family plus one hero family; reserve green/red for delta cues.
- When color roles, resolution, or layout are underspecified and would change the figure, confirm with user before finalizing.
