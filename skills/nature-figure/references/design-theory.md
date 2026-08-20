# Nature Figure Design Theory

## Contents

- [1) Typography](#1-typography)
- [2) Axes & Spines](#2-axes-spines)
- [3) Color Palette](#3-color-palette)
- [4) Layout and Composition](#4-layout-and-composition)
- [5) Bar Chart Rules](#5-bar-chart-rules)
- [6) Line / Trend Plots](#6-line-trend-plots)
- [7) Heatmap Rules](#7-heatmap-rules)
- [8) Radar / Polar Charts](#8-radar-polar-charts)
- [9) Export Policy](#9-export-policy)
- [10) Multi-Panel Information Architecture](#10-multi-panel-information-architecture)
- [11) Reproduction Checklist](#11-reproduction-checklist)


This file is an original synthesis of publication-figure typography, color,
composition, and export rules. External repositories may be consulted only as
visual references after their license and reuse terms have been verified; see
[demos.md](demos.md).

---

## 1) Typography

### Font stack (priority order)
- **Nature standard**: `font.family = 'sans-serif'`, `font.sans-serif = ['Arial']`
- **Fallback stack**: `['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']`
- **Helvetica** (equivalent) also appears in many scripts as `font.family = 'helvetica'`
- SVG/PDF editable text: always set `svg.fonttype = 'none'`
- LaTeX math labels: `text.usetex = True` only when LaTeX is installed

### Font size hierarchy
| Context | font.size | axes.linewidth |
|---------|-----------|---------------|
| Journal-final dense multi-panel figure at publication width | 7–9 | 0.8–1.2 |
| Large comparison bar panels (figsize > 28in wide) | 24 | 3 |
| Compact subfigures / analytic plots | 15–16 | 2 |
| Axis labels on large panels | 32–54 (override per-label) | — |
| In-bar annotations | 32–36 | — |
| Legend text on large panels | 28–38 | — |
| Tick labels | 20–36 | — |

When targeting the final dimensions of a two-column `Nature` figure page, start smaller than
slide-sized preview figures. The sampled 2026 papers routinely landed in the `7–9 pt` final-text
regime for dense composites.

The submission floor applies to rendered glyphs, not only source-level parent sizes. Mathtext often scales scripts to about `0.7×`; a 7 pt `$R^2$` can therefore contain a 4.9 pt superscript. Prefer a supported Unicode glyph such as `R²` when appropriate, or raise the parent size and verify the exported PDF with `scripts/audit_pdf_text.py`. Also compare each long label's rendered bounding-box width with its allocated slot width in millimetres.

---

## 2) Axes & Spines

```python
plt.rcParams['axes.spines.right'] = False   # always off
plt.rcParams['axes.spines.top'] = False     # always off
plt.rcParams['legend.frameon'] = False      # frameless legends everywhere
```

- Keep only left + bottom spines — minimalist, Nature-approved.
- No grid lines by default; use sparse y-ticks to guide the eye.

---

## 3) Color Palette

Semantic: blue = proposed method, green = positive variants, red/pink = baselines, neutral = reference/background.
For dense multi-panel figures, however, **family consistency beats maximal hue separation**.

```python
PALETTE = {
    # Proposed / key method
    "blue_main":      "#0F4D92",   # deep blue — hero method
    "blue_secondary": "#3775BA",   # medium blue — second author method

    # Positive / improvement shades (light → dark)
    "green_1": "#DDF3DE",
    "green_2": "#AADCA9",
    "green_3": "#8BCF8B",

    # Baseline / contrast shades (light → dark)
    "red_1":      "#F6CFCB",
    "red_2":      "#E9A6A1",
    "red_strong": "#B64342",

    # Neutral support
    "neutral_light": "#CFCECE",
    "neutral_mid":   "#767676",
    "neutral_dark":  "#4D4D4D",
    "neutral_black": "#272727",

    # Accent / callout (use sparingly)
    "gold":   "#FFD700",
    "teal":   "#42949E",
    "violet": "#9A4D8E",
    "magenta":"#EA84DD",
}

DEFAULT_COLOR_ORDER = [
    "#0F4D92",   # blue_main
    "#8BCF8B",   # green_3
    "#B64342",   # red_strong
    "#42949E",   # teal
    "#9A4D8E",   # violet
    "#CFCECE",   # neutral_light
]
```

### Unified-family rule (recommended for NMI-style pages)

Publication figures should read like **one figure**, not six unrelated plots. Prefer one cool family for
baselines and one lilac/rose family for the proposed method line.

```python
PALETTE_NMI_PASTEL = {
    "baseline_dark": "#484878",
    "baseline_mid":  "#7884B4",
    "baseline_soft": "#B4C0E4",
    "ours_tiny":  "#E4E4F0",
    "ours_base":  "#E4CCD8",
    "ours_large": "#F0C0CC",
    "delta_up":   "#2E9E44",
    "delta_down": "#E53935",
}

DEFAULT_COLOR_ORDER_NMI_PASTEL = [
    "#484878",   # baseline_dark
    "#7884B4",   # baseline_mid
    "#B4C0E4",   # baseline_soft
    "#E4E4F0",   # ours_tiny
    "#E4CCD8",   # ours_base
    "#F0C0CC",   # ours_large
]
```

Rules:
1. Keep related baselines in one cool family.
2. Keep `Tiny / Base / Large` or sibling variants in one hero family.
3. Reserve green/red for arrows, gains, drops, thresholds, or signed biological direction.
4. Never remap the same method to a different hue family in another panel.
5. If in doubt, reduce saturation before adding more categories.
6. Validate pairwise separation and white-background contrast, then inspect rendered salience. A neutral baseline must not dominate the hero method merely because it is darker.
7. Sequential light-to-dark scales encode order or magnitude; do not treat their steps as unrelated categories.

### Modality-specific palette discipline from sampled 2026 Nature figures

- **Imaging plates**: grayscale context + 1–2 fluorescent accent channels on black.
- **Schematic/material pages**: derive the palette from the physical objects in the schematic,
  then reuse softened versions of those colors in the support plots.
- **Clinical composites**: dark baseline/reference series, restrained warm/cool follow-up hues,
  pale background bands in forest plots.
- **Genomics / systems pages**: neutral grey scaffolds plus a small number of biologically
  meaningful highlight families, often one red and one blue.

### Ablation alpha encoding
When ablating components of one method, use a **single color with varying alpha**:
```python
color = (0.215686, 0.458824, 0.729412)   # blue_secondary as RGB tuple
alphas = np.linspace(0.2, 1.0, n_variants)
colors = [(color[0], color[1], color[2], a) for a in alphas]
# alpha=1.0 → full method, alpha=0.2 → minimal/ablated variant
```

---

## 4) Layout and Composition

### Figure sizes
| Figure type | Typical figsize |
|-------------|----------------|
| Journal-width composite page / asymmetric multi-panel | (7.0–7.4, 5.5–7.8) |
| Multi-metric bar (3–4 metrics + legend) | (28–45, 6–12) |
| Compact single bar | (9–16, 5–8) |
| Trend / line multi-panel | (14, 4) or (9, 8) |
| Heatmap single | (8–20, 5–9) |
| Radar polar | (12, 10) |
| 3D / illustration multi-panel | (24, 8) |

**Rule**: Width ≈ 3–4× height for comparison bars; prevents vertical crowding and allows left-to-right narrative reading.

### Dedicated legend panel
For multi-axis figures, the **last subplot is legend-only**:
```python
ax_legend = fig.add_subplot(1, n+1, n+1)
ax_legend.legend(handles, labels, fontsize=..., loc='center', frameon=False)
ax_legend.set_axis_off()
```

### Dynamic y-axis scaling
Never use fixed 0–100 when values sit in a narrow band.
Tighten limits to data range: e.g., `ax.set_ylim([data.min() - margin, data.max() + margin])`.

### Nature page archetypes from sampled 2026 papers

`Nature` figures were not uniformly dashboard-like. They repeatedly used a few strong page
archetypes:

| Archetype | Layout signal | Practical rule |
|-----------|---------------|----------------|
| Schematic-led composite | One wide story panel with smaller quant panels below | Give the schematic the visual hierarchy; supporting plots should validate, not compete |
| Dark image plate | Repeated black tiles with fluorescent channels | Use black only inside the image plate region; keep scale bars, gutters, and channel labels high-contrast |
| Clinical triptych | Top longitudinal row, middle forest row, bottom summary row | Reuse the same column logic across outcomes and put the shared legend above the row |
| Asymmetric hero layout | One dominant circular/schematic panel plus small support plots | Let one panel span multiple grid cells; equal panel sizes are not required |

### Panel labels and gutters

- Use small bold lowercase panel letters near the top-left edge.
- Keep gutters tight but real; increase spacing when dark and light modalities touch.
- Leave extra bottom clearance when a dense caption will sit immediately below the figure.
- Avoid decorative panel boxes. Alignment and whitespace should carry the structure.

### Legend economy and direct labelling

- Use direct labels when regions, channels, or line identities are spatially stable.
- Prefer one shared legend strip above a row rather than repeating legends inside several axes.
- Dense categorical area plots often read better with embedded text than with a detached legend.
- If a legend exists, it should usually be frameless and visually quieter than the data.
- Measure legend/panel and legend-row spacing from their rendered tight bounding boxes. Do not infer spacing from a full raster row when the objects occupy different horizontal positions.
- Check long model names at final size against the width allocated to each group. Widen the layout or reduce text size while keeping every PDF glyph at least 5 pt.

### X-tick suppression
When bars represent methods and the legend already names them:
```python
ax.set_xticks([])   # hide x-tick labels; use legend + panel title instead
```

---

## 5) Bar Chart Rules

### Vertical bars (comparison)
```python
bars = ax.bar(
    x_positions,
    values,
    yerr=std_values,
    capsize=5,
    color=colors,
    label=method_names,
    edgecolor='black',      # sharp separation
    linewidth=1.5,
)
```

### Horizontal bars (ablation)
```python
ax.barh(
    y_positions,
    values,
    xerr=std_values,
    color=[(r, g, b, alpha) for alpha in alphas],
    ecolor='k',
    capsize=5,
)
```

### In-bar value annotation
Print exact numbers inside or above bars at 32–36pt for readability without a grid:
```python
for bar, value in zip(bars, values):
    luminance = compute_luminance(bar_color)
    textcolor = 'white' if luminance < 128 else 'black'
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() - 0.10,
            f'{value:.2f}',
            ha='center', va='bottom',
            fontsize=32, color=textcolor)
```

### Hatch encoding for print-safe grayscale
```python
hatches = ['/', '\\', '.', 'x', 'o']
for bar, hatch in zip(bars, hatches):
    bar.set_hatch(hatch)
```

### Error bar styling
```python
error_kw = {
    'elinewidth': 2,
    'capthick': 2,
    'capsize': 15,
}
```

---

## 6) Line / Trend Plots

- Line width: 2–3pt with controlled alpha.
- Marker size: 8–12pt circles.
- For clinical or longitudinal triptychs, place one shared legend above the row rather than repeating it per axis.
- Fading alpha for temporal progression:
  ```python
  from matplotlib.collections import LineCollection
  alphas = np.linspace(0.3, 0.9, n_segments)
  # build LineCollection with per-segment alpha
  ```
- `fill_between` for uncertainty bands (keep alpha low: 0.1–0.2).
- If comparable panels summarize the same seed/fold/split process, show the same spread definition in all of them. After adding uncertainty, remove arrows or brackets that duplicate the same visual gap and collide with the interval geometry.
- Reference baseline as dashed horizontal line: `ax.axhline(y=..., linestyle='--', alpha=0.3, linewidth=4)`.
- No grid; sparse y-ticks guide the eye.

---

## 7) Heatmap Rules

```python
import matplotlib as mpl

# Diverging (positive/negative): use Red + Blue colormaps per column direction
cmap_pos = plt.cm.Reds
cmap_neg = plt.cm.Blues_r

# Masked NaN cells show as white
cmap.set_bad(color='white')

# Normalize per column
norm = mpl.colors.Normalize(vmin=col_min, vmax=col_max)

# Remove frame
ax.set_frame_on(False)

# Remove tick marks, keep labels
ax.tick_params(axis='x', which='both', bottom=False, top=False, length=0)
```

Cell text contrast:
```python
r, g, b, _ = cmap(norm(value))
luminance = 0.299*r + 0.587*g + 0.114*b
text_color = 'white' if luminance < 0.5 else 'black'
```

---

## 8) Radar / Polar Charts

- Project: `fig.add_subplot(projection='polar')`.
- Remove default grid and spines; draw custom spokes and contour polygons.
- Normalize per-spoke to display range (e.g., 45–90) using per-benchmark tick lists.
- Use `ax.set_theta_zero_location('N')` to start at top.
- Legend: `bbox_to_anchor=(1.40, 0.05)` outside right edge.

---

## 9) Export Policy

### SVG is the required primary format

SVG preserves editable text (when `svg.fonttype = 'none'`), supports lossless scaling,
and is required for any figure where text labels may need post-hoc alignment in
Illustrator or Inkscape. Always save SVG first.

```python
import os
os.makedirs('./figures/', exist_ok=True)
fig.tight_layout(pad=2)   # default; use pad=1 for compact multi-panel

# ── PRIMARY ── editable vector, text as <text> nodes ─────────────────────────
fig.savefig('./figures/name.svg', bbox_inches='tight')

# ── SECONDARY ── raster for quick preview / submission portals ────────────────
fig.savefig('./figures/name.png', dpi=300, bbox_inches='tight')

plt.close(fig)   # always close to free memory
```

**DPI guide (PNG only)**:
- `dpi=300` — standard for all figure types.
- `dpi=600` — dense bar panels with many methods.

**Never** use `svg.fonttype = 'path'` (matplotlib default): it converts glyphs to bezier
curves, breaking text editability. The mandatory three rcParams lines (see api.md) must
be set before any `savefig` call.

---

## 10) Multi-Panel Information Architecture

### Rule: Every panel must answer a unique scientific question

In a multi-panel figure, each panel should be independently necessary but need
not tell an independent story. Covering one panel must remove a distinct
inferential step that cannot be recovered from the others. For figure-level
claim design, evidence-role selection, placement decisions and manuscript
figure progression, load `multipanel-evidence-architecture.md`.

**Recommended three-level progression**:

| Level | Question answered | Typical encoding |
|-------|------------------|-----------------|
| Overview | "What is the landscape?" | Stacked bar, composition |
| Deviation | "What is distinctive per group?" | Z-score heatmap (diverging cmap) |
| Relationship | "How do variables co-vary?" | Scatter / bubble plot |

### Anti-redundancy checklist

Before finalising:

- [ ] Panel b does **not** re-display the same data as panel a in a different visual form
- [ ] Panel c adds a dimension absent from a and b (e.g., correlation, biological relationship)
- [ ] Each panel has its own axis-label vocabulary (different x/y quantities)

### Common redundancy traps

| Trap | Example | Fix |
|------|---------|-----|
| Absolute + absolute | Stacked bar (%) + heatmap of same % | Replace heatmap with z-score deviation |
| Subset of parent | Tumor-only ranked bar is just one column of the stacked bar | Swap for scatter: tumor % vs. immune % |
| Two rankings | Two ranked bars on related metrics | Replace one with scatter / bubble |
| Different chart, same data slice | Pie + stacked bar | Merge or replace one with a relationship plot |

### Z-score deviation heatmap (complement to a composition bar)

When panel a shows absolute composition, panel b should show **what is atypical** per group:

```python
# heat: DataFrame (cohorts × cell-type categories), values in %
z = (heat - heat.mean(axis=0)) / heat.std(axis=0)
im = ax.imshow(z.values, cmap="RdBu_r", aspect="auto", vmin=-2.5, vmax=2.5)
# colorbar label:
cbar.set_label("Z-score vs pan-cohort mean")
```

Use `RdBu_r` (red = enriched above average, blue = depleted). This diverging view is orthogonal to the absolute-percentage view in panel a.

### Bubble scatter (complement to both)

When a = composition, b = deviation, panel c should reveal **biological co-variation**:

```python
# x: dominant compartment (e.g., tumor %)
# y: functional readout (e.g., immune-cell %)
# size: third variable (e.g., stroma %)
ax.scatter(x, y, s=stroma * scale, c=colors,
           edgecolors="white", linewidth=0.8, alpha=0.9)
# Quadrant reference lines at median x and median y
ax.axvline(np.median(x), lw=1.2, ls="--", color="#767676", alpha=0.6)
ax.axhline(np.median(y), lw=1.2, ls="--", color="#767676", alpha=0.6)
```

Label quadrants ("Immune-hot / low tumor", "Immune-desert / high tumor", …) with small grey text.

---

## 11) Reproduction Checklist

To match Nature publication standards:

- [ ] **MANDATORY first lines**: `font.family='sans-serif'`, `font.sans-serif=['Arial','DejaVu Sans','Liberation Sans']`, `svg.fonttype='none'`
- [ ] **Save as SVG** (primary). PNG dpi=300 as optional raster preview.
- [ ] Top and right spines off; frameless legend
- [ ] Figure architecture chosen intentionally: grid, schematic-led composite, image plate, or asymmetric hero layout
- [ ] Journal-final source fonts usually 7–9 pt, and every exported PDF glyph including scripts is ≥ 5 pt
- [ ] Colors from blue-green-red-neutral semantic palette
- [ ] Rendered salience hierarchy matches the evidence hierarchy; neutral baselines do not dominate hero evidence
- [ ] Black background used only for imaging plates, not for ordinary plots
- [ ] Legends omitted or shared when direct labels or one legend strip read better
- [ ] Y-limits tightened to data range (not 0–100 when values are 80–95)
- [ ] X-ticks hidden when methods are named in legend
- [ ] Legend in dedicated panel or `frameon=False`
- [ ] Every comparable stochastic aggregate panel has the intended uncertainty definition
- [ ] Rotated text uses anchor placement; labels clear data and uncertainty without opaque masks
- [ ] `tight_layout(pad=2)` before save
- [ ] `plt.close(fig)` after save
