# Common Patterns — Nature Figure Making

## Contents

- [Pattern 1: Ultra-wide multi-metric bar panel](#pattern-1-ultra-wide-multi-metric-bar-panel)
- [Pattern 2: Dedicated legend panel](#pattern-2-dedicated-legend-panel)
- [Pattern 3: Categorical bars without x-tick labels](#pattern-3-categorical-bars-without-x-tick-labels)
- [Pattern 4: Dynamic y-axis tightening](#pattern-4-dynamic-y-axis-tightening)
- [Pattern 5: Alpha-graduated ablation bars (same color, varying opacity)](#pattern-5-alpha-graduated-ablation-bars-same-color-varying-opacity)
- [Pattern 6: Hatch encoding for print-safe grayscale](#pattern-6-hatch-encoding-for-print-safe-grayscale)
- [Pattern 7: Semantic or family color mapping](#pattern-7-semantic-or-family-color-mapping)
- [Pattern 8: In-bar text with luminance-aware color](#pattern-8-in-bar-text-with-luminance-aware-color)
- [Pattern 9: Fill-between trend with hatch (print-safe)](#pattern-9-fill-between-trend-with-hatch-print-safe)
- [Pattern 10: Annotate events on trend lines](#pattern-10-annotate-events-on-trend-lines)
- [Pattern 11: Grouped bars across multiple datasets (grouped-within-grouped)](#pattern-11-grouped-bars-across-multiple-datasets-grouped-within-grouped)
- [Pattern 12: Schematic hero panel with supporting quant row](#pattern-12-schematic-hero-panel-with-supporting-quant-row)
- [Pattern 13: Dark image plate with repeated views](#pattern-13-dark-image-plate-with-repeated-views)
- [Pattern 14: Clinical triptych](#pattern-14-clinical-triptych)
- [Pattern 15: Asymmetric hero panel](#pattern-15-asymmetric-hero-panel)
- [Pattern 16: Direct labels inside filled regions](#pattern-16-direct-labels-inside-filled-regions)
- [Related files](#related-files)


Reusable layout and encoding patterns used across publication-grade scripts.

---

## Pattern 1: Ultra-wide multi-metric bar panel

For 3–4 metrics compared across many methods, use a wide canvas so bars and labels don't crowd.

```python
fig = plt.figure(figsize=(45, 12))   # or (28, 6) for fewer metrics
gs = gridspec.GridSpec(1, n_metrics)

for i, metric in enumerate(metrics):
    ax = fig.add_subplot(gs[i])
    ax.bar(x, values[metric], color=colors, ...)
    ax.set_ylabel(metric, fontsize=54, labelpad=12)
    ax.set_xticks([])

# Last panel: legend only
ax_leg = fig.add_subplot(gs[-1])
ax_leg.legend(handles, labels, fontsize=38, loc='center', frameon=False)
ax_leg.set_axis_off()

fig.tight_layout(pad=2)
```

**Rule**: Width often 3–4× height. Allows left-to-right narrative scanning.

---

## Pattern 2: Dedicated legend panel

When the legend is large, give it its own axis so data panels stay clean.

```python
fig, axes = plt.subplots(1, n_data + 1, figsize=(...))

for i, ax in enumerate(axes[:-1]):
    bars = ax.bar(...)
    if i == 0:
        handles, labels = ax.get_legend_handles_labels()

# Legend-only panel
axes[-1].legend(handles, labels, fontsize=28, loc='center', frameon=False)
axes[-1].set_axis_off()
```

---

## Pattern 3: Categorical bars without x-tick labels

When methods are named in the legend, hide x-ticks entirely.

```python
ax.set_xticks([])        # removes ticks and labels
# Alternatively:
ax.set_xticklabels([])   # keeps tick marks, removes labels
```

---

## Pattern 4: Dynamic y-axis tightening

Never use 0–100 when all values are in 80–95.

```python
margin = (values.max() - values.min()) * 0.1   # 10% padding
ax.set_ylim([values.min() - margin, values.max() + margin])

# Manual ticks at clean round numbers
ax.set_yticks([0.75, 0.80, 0.85, 0.90])
ax.tick_params(axis='y', labelsize=36, length=10, width=2)
```

---

## Pattern 5: Alpha-graduated ablation bars (same color, varying opacity)

```python
import numpy as np

blue_rgb = (0.215686, 0.458824, 0.729412)   # #3775BA as float tuple
n_ablations = len(ablation_configs)
alphas = np.linspace(0.2, 1.0, n_ablations)
colors = [(blue_rgb[0], blue_rgb[1], blue_rgb[2], a) for a in alphas]
# Full method → alpha=1.0, most ablated → alpha=0.2
```

---

## Pattern 6: Hatch encoding for print-safe grayscale

Add hatching so bars remain distinct when printed in black-and-white.

```python
hatches = ['/', '\\\\', '.', 'x', 'o', '+']
for bar_container, hatch in zip(grouped_bars, hatches):
    for patch in bar_container:
        patch.set_hatch(hatch)
        patch.set_edgecolor('black')
        patch.set_linewidth(1.5)
```

---

## Pattern 7: Semantic or family color mapping

Always map colors consistently across all panels in a figure:

```python
method_colors = {
    'ResNet1d18': '#484878',   # baseline_dark
    'ResNet1d34': '#7884B4',   # baseline_mid
    'ECGFounder': '#B4C0E4',   # baseline_soft
    'CSFM-Tiny':  '#E4E4F0',   # ours_tiny
    'CSFM-Base':  '#E4CCD8',   # ours_base
    'CSFM-Large': '#F0C0CC',   # ours_large
}
colors = [method_colors[m] for m in methods]
```

Prefer coherent hue families over alternating saturated blue/green/red just because categories differ.
Green and red should usually be reserved for **directional annotations**, not primary series identity:

```python
ax.scatter(x_gain, y_gain, marker='^', color='#2E9E44', s=90, zorder=6)  # improvement
ax.scatter(x_drop, y_drop, marker='v', color='#E53935', s=90, zorder=6)  # degradation
```

---

## Pattern 8: In-bar text with luminance-aware color

```python
def annotate_bars(ax, bars, colors, fmt='{:.2f}', fontsize=32, offset=-0.10):
    for bar, color in zip(bars, colors):
        c = color.lstrip('#')
        r, g, b = int(c[0:2],16)/255, int(c[2:4],16)/255, int(c[4:6],16)/255
        lum = 0.299*r + 0.587*g + 0.114*b
        textcolor = 'white' if lum < 0.5 else 'black'
        value = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2,
                value + offset,
                fmt.format(value),
                ha='center', va='bottom',
                fontsize=fontsize, color=textcolor)
```

---

## Pattern 9: Fill-between trend with hatch (print-safe)

```python
ax.fill_between(x, 0, cumsum_series,
                color=fill_color,
                hatch='\\\\\\',   # triple backslash for dense hatch
                edgecolor='black',
                label=label_name)
# Visually erase the border artifacts:
ax.fill_between(x, 0, cumsum_series,
                facecolor='none',
                edgecolor='white',
                linewidth=2)
```

---

## Pattern 10: Annotate events on trend lines

```python
def mark_events(ax, x_labels, y_cumsum, events_dict, dy_fraction=0.1):
    """Add labeled arrows at event dates on a trend line."""
    x_index = {label: i for i, label in enumerate(x_labels)}
    y_lo, y_hi = ax.get_ylim()
    dy = dy_fraction * (y_hi - y_lo)
    for date, label in events_dict.items():
        if date not in x_index:
            continue
        i = x_index[date]
        stars = label.count('*')
        clean_label = label.replace('*', '')
        y_data = y_cumsum[i]
        ax.annotate(
            clean_label,
            xy=(i, y_data),
            xytext=(i, y_data + (1 + 0.8 * stars) * dy),
            ha='center', va='bottom', fontsize=11,
            arrowprops=dict(arrowstyle='-|>', lw=1.3, color='black',
                            shrinkA=0, shrinkB=0, mutation_scale=15)
        )
```

---

## Pattern 11: Grouped bars across multiple datasets (grouped-within-grouped)

```python
num_methods = len(methods)
xtick_positions = []

for dataset_idx, dataset_name in enumerate(datasets):
    x_start = dataset_idx * (num_methods + 1)   # gap of 1 between groups
    ax.bar(
        np.arange(num_methods) + x_start,
        values[dataset_name],
        color=method_colors,
        label=methods if dataset_idx == 0 else ['_nolegend_'] * num_methods,
    )
    xtick_positions.append(np.mean(np.arange(num_methods)) + x_start)

ax.set_xticks(xtick_positions)
ax.set_xticklabels(datasets)
```

---

## Pattern 12: Schematic hero panel with supporting quant row

Use when one mechanism or fabrication story needs to lead, with 2–4 smaller evidence plots below.

```python
fig = plt.figure(figsize=(7.2, 6.2))
gs = fig.add_gridspec(
    2, 4,
    height_ratios=[2.2, 1.0],
    hspace=0.18, wspace=0.28,
)

ax_top = fig.add_subplot(gs[0, :])    # hero schematic
ax_b = fig.add_subplot(gs[1, 0])
ax_c = fig.add_subplot(gs[1, 1:3])
ax_d = fig.add_subplot(gs[1, 3])

# top panel should carry the main palette and the main visual narrative
```

Rules:

- Allocate `45–60%` of total height to the hero schematic.
- Reuse softened versions of the same colors in the lower plots.
- Keep support plots quieter than the hero panel.

---

## Pattern 13: Dark image plate with repeated views

Use for microscopy, volume rendering, or fluorescence-heavy panels.

```python
fig = plt.figure(figsize=(7.2, 6.5))
gs = fig.add_gridspec(3, 5, hspace=0.08, wspace=0.04)

for r in range(3):
    for c in range(5):
        ax = fig.add_subplot(gs[r, c])
        ax.set_facecolor('black')
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
```

Rules:

- Use black only within the image plate cells.
- Put channel labels, scale bars and small crop guides directly on the plate.
- Keep crop geometry and scale-bar placement consistent across the grid.

---

## Pattern 14: Clinical triptych

Use for outcome-over-time figures that combine trajectories, effect sizes, and summary proportions.

```python
fig = plt.figure(figsize=(7.2, 6.8))
gs = fig.add_gridspec(
    3, 3,
    height_ratios=[1.0, 1.35, 0.8],
    hspace=0.28, wspace=0.32,
)

axes_top = [fig.add_subplot(gs[0, i]) for i in range(3)]
axes_mid = [fig.add_subplot(gs[1, i]) for i in range(3)]
axes_bot = [fig.add_subplot(gs[2, i]) for i in range(3)]

# Put one shared legend strip above axes_top rather than repeating legends.
```

Rules:

- Keep the three columns semantically parallel.
- Use a dashed vertical reference line in the forest-plot row.
- Group shading in the forest-plot row should be pale and subordinate.

---

## Pattern 15: Asymmetric hero panel

Use when one panel is conceptually central and should dominate.

```python
fig = plt.figure(figsize=(7.2, 5.8))
gs = fig.add_gridspec(3, 4, hspace=0.25, wspace=0.28)

ax_a = fig.add_subplot(gs[0, :2])
ax_b = fig.add_subplot(gs[0, 2])
ax_c = fig.add_subplot(gs[1, :2])
ax_d = fig.add_subplot(gs[1, 2])
ax_e = fig.add_subplot(gs[:, 3])      # hero panel spans all rows
ax_f = fig.add_subplot(gs[2, :2])
```

Rule: do not normalize every subplot to the same size if the science does not have equal importance.

---

## Pattern 16: Direct labels inside filled regions

Use when the same categorical structure repeats and a legend would become too large.

```python
for x_text, y_text, text, color in label_specs:
    ax.text(
        x_text, y_text, text,
        color=color,
        ha='center', va='center',
        fontsize=9, fontweight='bold',
    )
```

Rules:

- Keep labels inside stable, visually large regions.
- Use a small white or black stroke if the fill varies strongly underneath.
- Prefer direct labels over a mega-legend for repeated stacked-area or phase diagrams.

---

## Related files

- [SKILL.md](../SKILL.md) — When to use this skill
- [api.md](api.md) — Helper function signatures and PALETTE
- [design-theory.md](design-theory.md) — Rationale behind every pattern above
- [nature-2026-observations.md](nature-2026-observations.md) — Real Nature page archetypes behind these patterns
- [tutorials.md](tutorials.md) — End-to-end walkthroughs
- [chart-types.md](chart-types.md) — Radar, 3D, scatter patterns
- [demos.md](demos.md) — Third-party demo map, copyright-aware reference use, and original reimplementation guidance
