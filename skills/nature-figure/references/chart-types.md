# Chart Types — Nature Figure Making

## Contents

- [Radar / Polar Chart](#radar-polar-chart)
- [3D Sphere / Conceptual Illustration](#3d-sphere-conceptual-illustration)
- [Scatter Plot with Color-Coded Clusters](#scatter-plot-with-color-coded-clusters)
- [Probability + Manifold Concept Panel](#probability-manifold-concept-panel)
- [Ablation Line Panel with Reference Baselines](#ablation-line-panel-with-reference-baselines)
- [Fill-Between Area Chart (Stacked trend)](#fill-between-area-chart-stacked-trend)
- [Log-Scale Bar Chart](#log-scale-bar-chart)
- [GridSpec Multi-Panel Layout](#gridspec-multi-panel-layout)
- [Scientific Notation on Y-Axis](#scientific-notation-on-y-axis)
- [Custom Spine Positioning](#custom-spine-positioning)
- [Related files](#related-files)


Specialized chart patterns beyond basic bars and trends.
Each section includes the key code pattern extracted from production scripts.

---

## Radar / Polar Chart

Used when comparing multiple methods across many benchmarks simultaneously.

```python
import numpy as np
import matplotlib.pyplot as plt

def plot_radar(methods, colors, subtask_names, value_matrix,
               benchmark_radii, display_range=(45, 90)):
    """
    Parameters
    ----------
    methods        : list[str]    — one curve per method
    colors         : list[str]
    subtask_names  : list[str]    — one spoke per subtask (may contain '\\n')
    value_matrix   : np.ndarray  — shape (n_subtasks, n_methods)
    benchmark_radii: dict         — {benchmark_name: [tick1, tick2, ...]} for normalization
    display_range  : (r_min, r_max) — polar radial display window
    """
    r_lo, r_hi = display_range
    n_subtasks = len(subtask_names)
    n_methods  = len(methods)

    fig = plt.figure(figsize=(12, 10))
    ax  = fig.add_subplot(111, projection='polar')

    # Evenly spaced angles, clockwise from top
    angles = np.linspace(2 * np.pi, 0, n_subtasks, endpoint=False)
    angles_closed = np.append(angles, angles[0])

    def _normalize(val, bench):
        radii_list = benchmark_radii.get(bench, [0, 100])
        span = max(radii_list) - min(radii_list)
        if span <= 0:
            return (r_lo + r_hi) / 2
        frac = np.clip((val - min(radii_list)) / span, 0, 1)
        return r_lo + (r_hi - r_lo) * frac

    subtask_benchmarks = [s.split('\\n', 1)[-1] if '\\n' in s else s
                          for s in subtask_names]

    # Draw data polygons
    for m in range(n_methods):
        norm_vals = np.array([_normalize(value_matrix[i, m], subtask_benchmarks[i])
                              for i in range(n_subtasks)])
        closed = np.append(norm_vals, norm_vals[0])
        ax.plot(angles_closed, closed, color=colors[m], lw=2, label=methods[m])
        ax.fill(angles_closed, closed, color=colors[m], alpha=0.05)
        ax.scatter(angles, norm_vals, color=colors[m], s=18, zorder=5)

    # Style
    ax.set_ylim(r_lo, r_hi)
    ax.set_theta_zero_location('N')
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)

    # Outer boundary ring
    ax.plot(angles_closed, np.full_like(angles_closed, r_hi),
            color='k', lw=0.8, zorder=4)

    # Radial spokes
    for a in angles:
        ax.plot([a, a], [r_lo, r_hi], color='gray', lw=0.5, zorder=4)

    # Benchmark-level contour polygons
    max_levels = max(len(v) for v in benchmark_radii.values())
    for k in range(max_levels):
        disp = np.array([_normalize(benchmark_radii.get(b, [0,100])[
                            min(k, len(benchmark_radii.get(b,[0,100]))-1)], b)
                         for b in subtask_benchmarks])
        ax.plot(angles_closed, np.append(disp, disp[0]),
                color='k', lw=0.6, zorder=4)

    ax.set_yticks([r_hi])
    ax.set_yticklabels([])
    ax.set_xticks(angles)
    ax.set_xticklabels([])

    # Spoke labels (outside outer ring)
    for angle, label in zip(angles, subtask_names):
        r_label = r_hi + 8 + 10 * abs(np.sin(angle))
        ax.text(angle, r_label, label, fontsize=14,
                ha='center', va='center',
                transform=ax.transData, clip_on=False)

    ax.legend(loc='upper right', bbox_to_anchor=(1.40, 0.05),
              fontsize=15, frameon=False)
    return fig, ax
```

**Key settings:**
- `ax.set_theta_zero_location('N')` — top-start convention
- Remove all default spines/grid; draw custom spokes + contour polygons manually
- Normalize each spoke independently using per-benchmark tick lists
- Legend placed **outside** the plot at `bbox_to_anchor=(1.40, 0.05)`

---

## 3D Sphere / Conceptual Illustration

Used for geometric conceptual diagrams (e.g., embedding space visualization).

```python
import numpy as np
import matplotlib.pyplot as plt

def draw_shaded_sphere(ax, light_dir=(-0.5, 0.5, 0.8),
                       resolution=512, alpha=1.0,
                       extent=(-1, 1, -1, 1)):
    """Draw a 2D shaded disk that mimics a 3D sphere using ray-casting."""
    xs = np.linspace(extent[0], extent[1], resolution)
    ys = np.linspace(extent[2], extent[3], resolution)
    x, y = np.meshgrid(xs, ys)
    r2 = x**2 + y**2
    mask = r2 <= 1.0

    z = np.zeros_like(x)
    z[mask] = np.sqrt(1.0 - r2[mask])

    # Surface normals
    nx, ny, nz = x.copy(), y.copy(), z.copy()
    nrm = np.sqrt(nx**2 + ny**2 + nz**2) + 1e-6
    nx, ny, nz = nx/nrm, ny/nrm, nz/nrm

    # Lambertian shading
    ld = np.array(light_dir, dtype=float)
    ld /= np.linalg.norm(ld)
    intensity = np.maximum(0, nx*ld[0] + ny*ld[1] + nz*ld[2])

    img = np.ones_like(x)
    img[mask] = np.clip(0.2 + 0.9 * intensity[mask], 0, 1)

    ax.imshow(img, cmap='gray',
              extent=list(extent),
              vmin=0, vmax=1, alpha=alpha)
    ax.set_axis_off()
    return ax


def plot_3d_scatter_with_arrows(ax, points, grad_vectors,
                                point_color='#0c2458', arrow_color='#b64342'):
    """3D scatter plot with gradient arrow annotations."""
    from mpl_toolkits.mplot3d import proj3d
    from matplotlib.patches import FancyArrowPatch

    class Arrow3D(FancyArrowPatch):
        def __init__(self, xs, ys, zs, *args, **kwargs):
            super().__init__((0,0), (0,0), *args, **kwargs)
            self._verts3d = xs, ys, zs
        def do_3d_projection(self, renderer=None):
            xs, ys, zs = proj3d.proj_transform(*self._verts3d, self.axes.get_proj())
            self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
            return np.min(zs)

    ax.scatter(points[:, 0], points[:, 1], points[:, 2],
               s=80, color=point_color, alpha=0.5)
    for p, g in zip(points, grad_vectors):
        arrow = Arrow3D([p[0], p[0]+g[0]], [p[1], p[1]+g[1]], [p[2], p[2]+g[2]],
                        mutation_scale=16, lw=4, arrowstyle='->',
                        color=arrow_color, alpha=0.8)
        ax.add_artist(arrow)

    # Clean 3D axes
    ax.grid(False)
    ax.xaxis.pane.set_visible(False)
    ax.yaxis.pane.set_visible(False)
    ax.zaxis.pane.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
```

---

## Scatter Plot with Color-Coded Clusters

```python
def make_scatter(ax, x, y, labels_or_colors,
                 size=50, alpha=0.7, edgecolors='none'):
    """Single or multi-cluster scatter."""
    import numpy as np
    ax.scatter(x, y, c=labels_or_colors, s=size,
               alpha=alpha, edgecolors=edgecolors)
    ax.set_axis_off()   # for conceptual diagrams; remove for data plots
```

---

## Probability + Manifold Concept Panel

Use when a manuscript needs a conceptual mechanism panel that links a probability
shift to a geometric or latent-space explanation. Build the pair from the
original pattern below: a 1D probability-density panel beside a contour/scatter
manifold panel.

**Pattern:**
- Left panel: draw 2-3 probability curves with transparent fills; use one vertical
  reference line and a single double-headed arrow to define the conceptual gap.
- Right panel: sample points around smooth center curves, show low-alpha clouds,
  contour density bands, and a small number of highlighted trajectory markers.
- Keep axes only where they carry meaning. The manifold panel can be axis-free if
  labels and arrows carry the explanation.
- All math labels and manifold names must map to real manuscript concepts. Do not
  reuse demo labels such as `VIG` or `DPO` unless they are the user's actual terms.

```python
fig, (ax_prob, ax_manifold) = plt.subplots(1, 2, figsize=(24, 6))
plot_distribution(ax_prob)  # probability curves + conceptual gap arrow
plot_manifold(ax_manifold)  # density contours + trajectory markers
fig.tight_layout(pad=0.5)
```

---

## Ablation Line Panel with Reference Baselines

Use when an ablation compares data fraction, hyperparameters, or coupled metrics
across a small set of methods. A robust original layout uses three horizontal
panels: data fraction, one hyperparameter sweep, and a dual-axis coupled metric
sweep.

**Pattern:**
- Use a dashed horizontal baseline for the simple/reference model.
- Use a dotted horizontal line for a meaningful operating point, e.g. "ours at
  25% data", only when that comparison is called out in the text.
- Use `twinx()` sparingly. If two y-axes are needed, color each y label to match
  the corresponding series and keep tick ranges narrow.
- Put legends inside low-density regions of each panel; avoid one giant legend
  if panel-specific series differ.

```python
fig, axes = plt.subplots(1, 3, figsize=(27, 6),
                         gridspec_kw={"width_ratios": [1.1, 1, 1]})
axes[0].plot(x, baseline, color="black", alpha=0.3, lw=4, ls="--")
axes[0].plot(x, reference, color=hero_color, lw=3, ls=":")
ax2 = axes[2].twinx()
```

---

## Fill-Between Area Chart (Stacked trend)

Used for cumulative publication counts, stacked contributions, etc.

```python
# Filled area (stacked) with hatch for print safety
ax.fill_between(x, 0, y_bottom,
                color='#ffa8a6', label='Category A')
ax.fill_between(x, 0, y_top,
                color='#9BC8FA',
                hatch='///',               # hatch for grayscale print
                edgecolor='black',
                label='Category B')
# Erase border artifacts
ax.fill_between(x, 0, y_top,
                facecolor='none',
                edgecolor='white',
                linewidth=2)

# Overlay the trend line for exact values
ax.plot(x, y_top, lw=3, color='#13457E')
ax.plot(x, y_bottom, lw=3, color='#850c0a')
```

---

## Log-Scale Bar Chart

```python
ax.set_yscale('log')
ymin, ymax = ax.get_ylim()
ax.set_ylim(ymin, ymax * 20)   # expand top for annotations

# Annotate values above bars
for i, val in enumerate(values):
    ax.text(i, val * 1.1, f'{val:.3f}',
            ha='center', va='bottom', fontsize=16)
```

---

## GridSpec Multi-Panel Layout

```python
from matplotlib import gridspec

# 2-row, 4-column layout
fig = plt.figure(figsize=(36, 12))
gs = gridspec.GridSpec(2, 4)

ax_top_left  = fig.add_subplot(gs[0, 0])
ax_top_right = fig.add_subplot(gs[0, 1:3])   # span columns 1-2
ax_legend    = fig.add_subplot(gs[0, 3])     # legend panel
ax_bottom    = fig.add_subplot(gs[1, :])     # full-width bottom
```

---

## Scientific Notation on Y-Axis

```python
ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
```

---

## Custom Spine Positioning

```python
# Move bottom spine to y=0 (for negative values)
ax.spines['bottom'].set_position(('data', 0))
ax.xaxis.set_ticks_position('bottom')
ax.spines['left'].set_bounds(0, y_max)
```

---

## Related files

- [SKILL.md](../SKILL.md) — When to use this skill
- [api.md](api.md) — PALETTE and core helper signatures
- [common-patterns.md](common-patterns.md) — Bar, trend, and layout patterns
- [design-theory.md](design-theory.md) — Rationale and color theory
- [tutorials.md](tutorials.md) — Full end-to-end walkthroughs
