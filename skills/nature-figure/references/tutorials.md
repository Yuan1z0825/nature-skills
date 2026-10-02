# Tutorials — Nature Figure Making

## Contents

- [Tutorial 1: Grouped bar chart (multi-metric comparison)](#tutorial-1-grouped-bar-chart-multi-metric-comparison)
- [Tutorial 2: Ablation bar chart (alpha-graduated, horizontal)](#tutorial-2-ablation-bar-chart-alpha-graduated-horizontal)
- [Tutorial 3: Multi-panel trend with shared legend](#tutorial-3-multi-panel-trend-with-shared-legend)
- [Tutorial 4: Heatmap with dual colormaps (positive/negative columns)](#tutorial-4-heatmap-with-dual-colormaps-positivenegative-columns)
- [Related files](#related-files)


End-to-end walkthroughs for the most common publication figure types.
All examples use helpers from [api.md](api.md) and patterns from [common-patterns.md](common-patterns.md).
For the retained third-party demo map, copyright boundary, and original reimplementation guidance, open [demos.md](demos.md).

---

## Tutorial 1: Grouped bar chart (multi-metric comparison)

**Goal**: Several methods compared across multiple metrics. Legend in a dedicated panel.
When methods belong to related families, use one coherent baseline family plus one coherent hero family.

```python
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

# --- Style ---
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.size'] = 24
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.linewidth'] = 3

# --- Data ---
methods = ['ResNet1d18', 'ResNet1d34', 'ECGFounder', 'CSFM-Tiny', 'CSFM-Base', 'CSFM-Large']
colors  = ['#484878', '#7884B4', '#B4C0E4', '#E4E4F0', '#E4CCD8', '#F0C0CC']
metrics = ['Metric 1', 'Metric 2', 'Metric 3']
mean = {
    'Metric 1': np.array([0.81, 0.83, 0.86, 0.89, 0.91, 0.92]),
    'Metric 2': np.array([0.63, 0.67, 0.71, 0.74, 0.77, 0.79]),
    'Metric 3': np.array([0.41, 0.45, 0.49, 0.53, 0.56, 0.58]),
}
std  = {k: v * 0.03 for k, v in mean.items()}  # placeholder

# --- Figure ---
fig = plt.figure(figsize=(28, 6))
gs = gridspec.GridSpec(1, len(metrics) + 1)  # +1 for legend panel

handles, labels = None, None
for col, metric in enumerate(metrics):
    ax = fig.add_subplot(gs[col])
    bars = ax.bar(
        range(len(methods)),
        mean[metric],
        yerr=std[metric],
        capsize=5,
        color=colors,
        label=methods,
        error_kw={'elinewidth': 2, 'capthick': 2},
    )
    if col == 0:
        handles, labels = ax.get_legend_handles_labels()
    ax.set_xticks([])
    y_vals = mean[metric]
    margin = (y_vals.max() - y_vals.min()) * 0.15
    ax.set_ylim([y_vals.min() - margin, y_vals.max() + margin])
    ax.set_ylabel(metric, fontsize=32)

# Legend-only panel
ax_leg = fig.add_subplot(gs[-1])
ax_leg.legend(handles, labels, fontsize=28, loc='center', frameon=False)
ax_leg.set_axis_off()

fig.tight_layout(pad=2)
os.makedirs('./figures', exist_ok=True)
fig.savefig('./figures/comparison.png', dpi=300)
fig.savefig('./figures/comparison.pdf', dpi=300)
plt.close(fig)
```

---

## Tutorial 2: Ablation bar chart (alpha-graduated, horizontal)

**Goal**: Same method with components progressively added; alpha encodes completeness.

```python
import os
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.size'] = 24
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.linewidth'] = 3

configs = ['None', '+ Module A', '+ Module B', '+ Module C', 'Full']
values  = np.array([0.72, 0.78, 0.81, 0.84, 0.88])
stds    = np.array([0.02, 0.02, 0.01, 0.01, 0.01])

n = len(configs)
blue_rgb = (0.215686, 0.458824, 0.729412)   # #3775BA
alphas = np.linspace(0.2, 1.0, n)
colors = [(blue_rgb[0], blue_rgb[1], blue_rgb[2], a) for a in alphas]

fig, ax = plt.subplots(figsize=(12, 6))
ax.barh(range(n), values, xerr=stds,
        color=colors, ecolor='k', capsize=5)
ax.set_yticks(range(n))
ax.set_yticklabels(configs)
ax.set_xlim([values.min() - 0.05, values.max() + 0.03])
ax.set_xlabel('Score', fontsize=32)

fig.tight_layout(pad=2)
os.makedirs('./figures', exist_ok=True)
fig.savefig('./figures/ablation.png', dpi=300)
plt.close(fig)
```

---

## Tutorial 3: Multi-panel trend with shared legend

**Goal**: Two trend panels (e.g., train/val curves) and a legend-only third panel.

```python
import os
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.size'] = 15
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.linewidth'] = 2

methods = ['Baseline', 'CSFM-Tiny', 'CSFM-Base', 'CSFM-Large']
colors  = ['#7884B4', '#E4E4F0', '#E4CCD8', '#F0C0CC']
x = np.arange(0, 100, 5)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for panel_idx, (ax, panel_name) in enumerate(zip(axes[:2], ['Training', 'Validation'])):
    for method, color in zip(methods, colors):
        y = 0.48 + 0.42 * (1 - np.exp(-x / 30)) + np.random.randn(len(x)) * 0.01
        if method == 'Baseline':
            y -= 0.03
        elif method == 'CSFM-Tiny':
            y += 0.00
        elif method == 'CSFM-Base':
            y += 0.02
        elif method == 'CSFM-Large':
            y += 0.03
        ax.plot(x, y, color=color, lw=2.5, marker='o', markersize=6, label=method)
    ax.set_title(panel_name, fontsize=18)
    ax.set_xlabel('Epoch', fontsize=16)
    ax.set_ylabel('Loss', fontsize=16)
    if panel_idx == 0:
        handles, labels = ax.get_legend_handles_labels()

# Legend-only panel
axes[2].legend(handles, labels, fontsize=14, loc='center', frameon=False)
axes[2].set_axis_off()

fig.tight_layout(pad=2)
os.makedirs('./figures', exist_ok=True)
fig.savefig('./figures/trends.png', dpi=300)
fig.savefig('./figures/trends.pdf', dpi=300)
plt.close(fig)
```

---

## Tutorial 4: Heatmap with dual colormaps (positive/negative columns)

**Goal**: Score matrix where positive = Reds, negative = Blues_r. Cell text auto-contrasted.

```python
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['font.size'] = 16
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.linewidth'] = 2

# matrix: rows = methods, cols = metrics (alternating positive/negative directions)
methods = ['Method A', 'Method B', 'Method C', 'Method D']
metrics = ['Score (+)', 'Error (-)', 'F1 (+)', 'Loss (-)']
matrix  = np.array([
    [0.88,  0.12,  0.85,  0.20],
    [0.81,  0.18,  0.78,  0.28],
    [0.75,  0.25,  0.72,  0.35],
    [0.70,  0.30,  0.68,  0.40],
])

fig, ax = plt.subplots(figsize=(10, 6))
n_rows, n_cols = matrix.shape
vmin, vmax = matrix.min(0), matrix.max(0)

for j in range(n_cols):
    is_positive = (j % 2 == 0)
    cmap = plt.cm.Reds if is_positive else plt.cm.Blues_r
    cmap = cmap.copy()
    norm = mpl.colors.Normalize(
        vmin=0 if is_positive else vmax[j],
        vmax=vmax[j] if is_positive else 0
    )
    ax.imshow(matrix[:, j:j+1], cmap=cmap, norm=norm,
              aspect='auto', extent=[j-0.5, j+0.5, 0, n_rows], origin='lower')

for (i, j), val in np.ndenumerate(matrix):
    is_positive = (j % 2 == 0)
    cmap = plt.cm.Reds if is_positive else plt.cm.Blues_r
    norm = mpl.colors.Normalize(vmin=0 if is_positive else vmax[j],
                                 vmax=vmax[j] if is_positive else 0)
    r, g, b, _ = cmap(norm(val))
    lum = 0.299*r + 0.587*g + 0.114*b
    color = 'white' if lum < 0.5 else 'black'
    ax.text(j, i + 0.5, f'{val:.2f}', ha='center', va='center',
            fontsize=13, color=color)

ax.set_xlim(-0.5, n_cols - 0.5)
ax.set_xticks(np.arange(n_cols))
ax.set_xticklabels(metrics, rotation=30, ha='right', fontsize=14)
ax.tick_params(axis='x', bottom=False, top=False, length=0)
ax.set_yticks(np.arange(n_rows) + 0.5)
ax.set_yticklabels(methods, fontsize=14)
ax.set_frame_on(False)
ax.invert_yaxis()

fig.tight_layout(pad=2)
os.makedirs('./figures', exist_ok=True)
fig.savefig('./figures/heatmap.png', dpi=300)
plt.close(fig)
```

---

## Related files

- [SKILL.md](../SKILL.md) — When to use this skill
- [api.md](api.md) — Reusable helper implementations
- [common-patterns.md](common-patterns.md) — Layout and encoding patterns used above
- [design-theory.md](design-theory.md) — Why these choices exist
- [chart-types.md](chart-types.md) — Radar, 3D sphere, scatter, fill_between
