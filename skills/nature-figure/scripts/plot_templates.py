#!/usr/bin/env python3
"""Validated Python templates for five common manuscript-figure families.

Subcommands: volcano, roc, dotplot, marginal, and paired. Production runs
require a CSV input. Simulated data is available only through the explicit
--demo flag and is marked as such in the generated QA record.

The template families and adaptation safeguards were informed by the
Apache-2.0 academic-figure-skill asset collection. This implementation is
portable, path-independent, and designed for the nature-figure contract.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable


DEFAULT_WIDTH_MM = 183.0
DEFAULT_HEIGHT_MM = 120.0
MM_PER_INCH = 25.4
PALETTE = ["#2166AC", "#B2182B", "#1B7837", "#F1A340", "#762A83", "#666666"]
DEPENDENCY_ERROR: Exception | None = None

try:
    import numpy as np
    import matplotlib as mpl

    mpl.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.lines import Line2D
except ImportError as exc:  # Keep --help usable in a minimal environment.
    DEPENDENCY_ERROR = exc


def require_dependencies() -> None:
    if DEPENDENCY_ERROR is not None:
        raise RuntimeError(
            "plot_templates.py requires numpy and matplotlib in the selected Python environment"
        ) from DEPENDENCY_ERROR


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"],
            "font.size": 7,
            "axes.labelsize": 7,
            "axes.titlesize": 8,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "legend.fontsize": 6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.6,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "legend.frameon": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
        }
    )


def normalize_prefix(raw: Path) -> Path:
    if raw.suffix.lower() in {".svg", ".pdf", ".tif", ".tiff", ".png"}:
        raw = raw.with_suffix("")
    raw.parent.mkdir(parents=True, exist_ok=True)
    return raw


def save_bundle(fig: Any, output: Path) -> dict[str, str]:
    output = normalize_prefix(output)
    paths = {
        "svg": str(output.with_suffix(".svg")),
        "pdf": str(output.with_suffix(".pdf")),
        "tiff": str(output.with_suffix(".tiff")),
    }
    fig.savefig(paths["svg"], bbox_inches="tight", facecolor="white")
    fig.savefig(paths["pdf"], bbox_inches="tight", facecolor="white")
    fig.savefig(paths["tiff"], dpi=600, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return paths


def write_qa(output: Path, qa: dict[str, Any]) -> Path:
    path = normalize_prefix(output).with_suffix(".qa.json")
    path.write_text(json.dumps(qa, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def read_csv_rows(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        rows = [dict(row) for row in reader]
        return rows, list(reader.fieldnames)


def require_columns(fieldnames: Iterable[str], required: Iterable[str]) -> None:
    available = set(fieldnames)
    missing = [name for name in required if name not in available]
    if missing:
        raise ValueError(f"missing required CSV columns: {', '.join(missing)}")


def coerce_numeric_rows(
    rows: list[dict[str, Any]],
    columns: Iterable[str],
    drop_incomplete: bool,
) -> tuple[list[dict[str, Any]], list[int]]:
    columns = list(columns)
    valid: list[dict[str, Any]] = []
    invalid: list[int] = []
    for row_number, row in enumerate(rows, start=2):
        converted = dict(row)
        try:
            for column in columns:
                value = float(row[column])
                if not math.isfinite(value):
                    raise ValueError
                converted[column] = value
        except (KeyError, TypeError, ValueError):
            invalid.append(row_number)
            continue
        valid.append(converted)
    if invalid and not drop_incomplete:
        shown = ", ".join(str(value) for value in invalid[:10])
        suffix = " ..." if len(invalid) > 10 else ""
        raise ValueError(
            f"non-finite or missing numeric values at CSV rows {shown}{suffix}; "
            "fix the data or rerun with explicit --drop-incomplete"
        )
    if not valid:
        raise ValueError("no valid observations remain")
    return valid, invalid


def first_seen(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def parse_order(raw: str | None, observed: Iterable[str], label: str) -> list[str]:
    observed_order = first_seen(str(value) for value in observed)
    if not raw:
        return observed_order
    requested = [value.strip() for value in raw.split(",") if value.strip()]
    missing = [value for value in observed_order if value not in requested]
    extra = [value for value in requested if value not in observed_order]
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing observed {label}: {missing}")
        if extra:
            details.append(f"unknown {label}: {extra}")
        raise ValueError("; ".join(details))
    return requested


def nice_reference_values(maximum: float) -> list[float]:
    if maximum <= 0:
        return []
    magnitude = 10 ** math.floor(math.log10(maximum))
    quantum = magnitude / 2
    values = [round((maximum * fraction) / quantum) * quantum for fraction in (0.25, 0.5, 1.0)]
    return sorted({value for value in values if value > 0})


def base_qa(args: argparse.Namespace, kind: str, rows_input: int) -> dict[str, Any]:
    return {
        "template": kind,
        "backend": "python",
        "demo": bool(args.demo),
        "input": "<explicit-demo-data>" if args.demo else args.input.name,
        "output_prefix": normalize_prefix(args.output).name,
        "rows_input": rows_input,
        "rows_plotted": rows_input,
        "excluded_rows": 0,
        "excluded_entities": 0,
        "mapping": {},
        "parameters": {},
        "notes": [
            "All supplied observations are used unless excluded through explicit --drop-incomplete.",
            "The QA record stores input basenames rather than private absolute paths.",
        ],
    }


def load_rows(args: argparse.Namespace, kind: str) -> tuple[list[dict[str, Any]], list[str]]:
    if args.demo:
        rows = demo_rows(kind)
        return rows, list(rows[0])
    if args.input is None:
        raise ValueError("production runs require --input CSV; use --demo only for an explicit example")
    return read_csv_rows(args.input)


def demo_rows(kind: str) -> list[dict[str, Any]]:
    rng = np.random.default_rng(20260715)
    if kind == "volcano":
        rows = []
        for index in range(1200):
            effect = float(rng.normal(0, 0.65))
            pvalue = float(rng.uniform(0.02, 1.0))
            if index < 55:
                effect = float(rng.choice([-1, 1]) * rng.uniform(1.2, 3.2))
                pvalue = float(10 ** (-rng.uniform(2, 9)))
            rows.append({"gene": f"Gene_{index + 1}", "log2fc": effect, "padj": pvalue})
        return rows
    if kind == "roc":
        rows = []
        for fpr in np.linspace(0, 1, 101):
            rows.append(
                {
                    "fpr": float(fpr),
                    "model_a": float(np.clip(fpr ** 0.42, 0, 1)),
                    "model_b": float(np.clip(fpr ** 0.58, 0, 1)),
                    "model_c": float(np.clip(fpr ** 0.72, 0, 1)),
                }
            )
        return rows
    if kind == "dotplot":
        rows = []
        row_names = ["VCT", "EVT", "SCT", "FB", "T", "dNK"]
        column_names = ["TP63", "HLA-G", "ERVW-1", "VIM", "ACTA2", "CD3D", "GNLY", "NKG7"]
        for row_index, row_name in enumerate(row_names):
            for col_index, column_name in enumerate(column_names):
                distance = abs((row_index * 1.3) - (col_index * 0.7))
                rows.append(
                    {
                        "cell_type": row_name,
                        "gene": column_name,
                        "pct_exp": float(np.clip(70 - 14 * distance + rng.normal(0, 5), 1, 90)),
                        "avg_exp_scaled": float(np.clip(1 - distance / 6 + rng.normal(0, 0.08), 0, 1)),
                    }
                )
        return rows
    if kind == "marginal":
        rows = []
        for group_index, group in enumerate(("Control", "Treatment A", "Treatment B")):
            x = rng.normal(group_index * 0.7, 0.85, 220)
            y = 0.65 * x + rng.normal(group_index * 0.35, 0.65, 220)
            rows.extend({"x": float(a), "y": float(b), "group": group} for a, b in zip(x, y))
        return rows
    if kind == "paired":
        rows = []
        for index in range(28):
            before = float(rng.normal(1.0, 0.18))
            after = float(before + rng.normal(0.20, 0.10))
            rows.extend(
                [
                    {"subject": f"S{index + 1:02d}", "condition": "Before", "value": before},
                    {"subject": f"S{index + 1:02d}", "condition": "After", "value": after},
                ]
            )
        return rows
    raise ValueError(f"unknown demo kind: {kind}")


def plot_volcano(args: argparse.Namespace) -> tuple[dict[str, str], dict[str, Any]]:
    rows, fields = load_rows(args, "volcano")
    required = [args.gene_col, args.effect_col, args.p_col]
    require_columns(fields, required)
    rows, invalid = coerce_numeric_rows(rows, [args.effect_col, args.p_col], args.drop_incomplete)
    bad_p = [index for index, row in enumerate(rows, start=1) if not 0 < row[args.p_col] <= 1]
    if bad_p:
        raise ValueError("adjusted p values must be strictly positive and no greater than 1")

    effects = np.asarray([row[args.effect_col] for row in rows], dtype=float)
    pvalues = np.asarray([row[args.p_col] for row in rows], dtype=float)
    genes = [str(row[args.gene_col]) for row in rows]
    scores = -np.log10(pvalues)
    up = (pvalues < args.p_threshold) & (effects >= args.effect_threshold)
    down = (pvalues < args.p_threshold) & (effects <= -args.effect_threshold)
    neutral = ~(up | down)

    fig, ax = plt.subplots(figsize=(args.width_mm / MM_PER_INCH, args.height_mm / MM_PER_INCH))
    rasterized = len(rows) > 50000
    ax.scatter(effects[neutral], scores[neutral], s=5, color="#B3B3B3", alpha=0.45, edgecolors="none", rasterized=rasterized, label=f"Not significant ({neutral.sum()})")
    ax.scatter(effects[down], scores[down], s=7, color="#2166AC", alpha=0.72, edgecolors="none", rasterized=rasterized, label=f"Down ({down.sum()})")
    ax.scatter(effects[up], scores[up], s=7, color="#B2182B", alpha=0.72, edgecolors="none", rasterized=rasterized, label=f"Up ({up.sum()})")
    ax.axhline(-math.log10(args.p_threshold), color="#666666", linestyle="--", linewidth=0.6)
    ax.axvline(-args.effect_threshold, color="#666666", linestyle="--", linewidth=0.6)
    ax.axvline(args.effect_threshold, color="#666666", linestyle="--", linewidth=0.6)
    significant = np.flatnonzero(up | down)
    if args.top_labels > 0 and len(significant):
        selected = significant[np.argsort(pvalues[significant])[: args.top_labels]]
        for is_positive in (False, True):
            side = [index for index in selected if (effects[index] >= 0) == is_positive]
            last_label_y = -math.inf
            for index in sorted(side, key=lambda value: scores[value]):
                label_y = max(float(scores[index]) + 0.12, last_label_y + 0.30)
                last_label_y = label_y
                direction = 1 if is_positive else -1
                ax.annotate(
                    genes[index],
                    (effects[index], scores[index]),
                    xytext=(effects[index] + 0.07 * direction, label_y),
                    textcoords="data",
                    ha="left" if is_positive else "right",
                    va="bottom",
                    fontsize=5,
                    color="#333333",
                    arrowprops={"arrowstyle": "-", "color": "#777777", "linewidth": 0.3},
                )
    ax.set_xlabel(args.effect_label)
    # Keep the subscript as Unicode so the rendered glyph does not shrink below
    # the journal's 5 pt floor when the surrounding label is already compact.
    ax.set_ylabel("−log₁₀(adjusted p value)")
    if args.title:
        ax.set_title(args.title)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.19), ncol=3)
    paths = save_bundle(fig, args.output)

    qa = base_qa(args, "volcano", len(rows) + len(invalid))
    qa.update({"rows_plotted": len(rows), "excluded_rows": len(invalid)})
    qa["mapping"] = {"gene": args.gene_col, "effect": args.effect_col, "adjusted_p": args.p_col}
    qa["parameters"] = {"p_threshold": args.p_threshold, "effect_threshold": args.effect_threshold, "top_labels": args.top_labels, "rasterized_marks": rasterized, "category_counts": {"up": int(up.sum()), "down": int(down.sum()), "neutral": int(neutral.sum())}}
    return paths, qa


def plot_roc(args: argparse.Namespace) -> tuple[dict[str, str], dict[str, Any]]:
    rows, fields = load_rows(args, "roc")
    tpr_columns = [value.strip() for value in args.tpr_cols.split(",") if value.strip()] if args.tpr_cols else [field for field in fields if field != args.fpr_col]
    if not tpr_columns:
        raise ValueError("no TPR columns selected")
    require_columns(fields, [args.fpr_col, *tpr_columns])
    rows, invalid = coerce_numeric_rows(rows, [args.fpr_col, *tpr_columns], args.drop_incomplete)
    for row in rows:
        values = [row[args.fpr_col], *(row[column] for column in tpr_columns)]
        if any(value < 0 or value > 1 for value in values):
            raise ValueError("FPR and TPR values must stay within [0, 1]")

    fpr = np.asarray([row[args.fpr_col] for row in rows], dtype=float)
    order = np.argsort(fpr, kind="stable")
    sorted_input = bool(np.all(order == np.arange(len(fpr))))
    fig, ax = plt.subplots(figsize=(args.width_mm / MM_PER_INCH, args.height_mm / MM_PER_INCH))
    aucs: dict[str, float] = {}
    for index, column in enumerate(tpr_columns):
        tpr = np.asarray([row[column] for row in rows], dtype=float)[order]
        auc = float(np.trapezoid(tpr, fpr[order]))
        aucs[column] = auc
        ax.plot(fpr[order], tpr, color=PALETTE[index % len(PALETTE)], linewidth=1.3, label=f"{column} (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], color="#888888", linestyle="--", linewidth=0.7, label="Chance")
    ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="False-positive rate", ylabel="True-positive rate")
    ax.set_aspect("equal", adjustable="box")
    if args.title:
        ax.set_title(args.title)
    ax.legend(loc="lower right")
    paths = save_bundle(fig, args.output)

    qa = base_qa(args, "roc", len(rows) + len(invalid))
    qa.update({"rows_plotted": len(rows), "excluded_rows": len(invalid)})
    qa["mapping"] = {"fpr": args.fpr_col, "tpr_series": tpr_columns}
    qa["parameters"] = {"auc_method": "trapezoidal", "auc": aucs, "input_already_sorted_by_fpr": sorted_input}
    return paths, qa


def plot_dotplot(args: argparse.Namespace) -> tuple[dict[str, str], dict[str, Any]]:
    rows, fields = load_rows(args, "dotplot")
    required = [args.row_col, args.column_col, args.size_col, args.color_col]
    require_columns(fields, required)
    rows, invalid = coerce_numeric_rows(rows, [args.size_col, args.color_col], args.drop_incomplete)
    if any(row[args.size_col] < 0 for row in rows):
        raise ValueError("dot size values must be non-negative")
    row_order = parse_order(args.row_order, (str(row[args.row_col]) for row in rows), "row categories")
    column_order = parse_order(args.column_order, (str(row[args.column_col]) for row in rows), "column categories")
    row_map = {value: index for index, value in enumerate(row_order)}
    column_map = {value: index for index, value in enumerate(column_order)}

    size_values = np.asarray([row[args.size_col] for row in rows], dtype=float)
    color_values = np.asarray([row[args.color_col] for row in rows], dtype=float)
    size_max = float(size_values.max())
    sizes = np.full_like(size_values, 30.0) if size_max == 0 else 12 + 160 * np.sqrt(size_values / size_max)
    color_min = float(color_values.min())
    color_max = float(color_values.max())
    color_norm = np.full_like(color_values, 0.5) if color_max == color_min else (color_values - color_min) / (color_max - color_min)
    xs = np.asarray([column_map[str(row[args.column_col])] for row in rows])
    ys = np.asarray([row_map[str(row[args.row_col])] for row in rows])
    cmap = LinearSegmentedColormap.from_list("nature_expression", ["#2166AC", "#F7F7F7", "#B2182B"])

    fig, ax = plt.subplots(figsize=(args.width_mm / MM_PER_INCH, args.height_mm / MM_PER_INCH))
    scatter = ax.scatter(xs, ys, s=sizes, c=color_norm, cmap=cmap, vmin=0, vmax=1, edgecolors="#666666", linewidths=0.35)
    ax.set_xticks(
        range(len(column_order)),
        column_order,
        rotation=90,
        rotation_mode="anchor",
        ha="right",
    )
    ax.set_yticks(range(len(row_order)), row_order)
    ax.set_xlim(-0.7, len(column_order) - 0.3)
    ax.set_ylim(-0.7, len(row_order) - 0.3)
    ax.invert_yaxis()
    ax.spines["top"].set_visible(True)
    ax.spines["right"].set_visible(True)
    ax.grid(color="#E6E6E6", linewidth=0.35)
    ax.set_axisbelow(True)
    colorbar = fig.colorbar(scatter, ax=ax, fraction=0.025, pad=0.02)
    colorbar.set_label(args.color_label)
    reference_values = nice_reference_values(size_max)
    handles = [Line2D([], [], marker="o", linestyle="", markerfacecolor="#999999", markeredgecolor="#666666", markersize=math.sqrt(12 + 160 * math.sqrt(value / size_max))) for value in reference_values]
    if handles:
        ax.legend(handles, [f"{value:g}" for value in reference_values], title=args.size_label, bbox_to_anchor=(1.18, 1), loc="upper left")
    if args.title:
        ax.set_title(args.title)
    paths = save_bundle(fig, args.output)

    qa = base_qa(args, "dotplot", len(rows) + len(invalid))
    qa.update({"rows_plotted": len(rows), "excluded_rows": len(invalid)})
    qa["mapping"] = {"row_category": args.row_col, "column_category": args.column_col, "dot_size": args.size_col, "dot_color": args.color_col}
    qa["parameters"] = {"row_order": row_order, "column_order": column_order, "size_range": [float(size_values.min()), size_max], "color_range": [color_min, color_max]}
    return paths, qa


def plot_marginal(args: argparse.Namespace) -> tuple[dict[str, str], dict[str, Any]]:
    rows, fields = load_rows(args, "marginal")
    required = [args.x_col, args.y_col] + ([args.group_col] if args.group_col else [])
    require_columns(fields, required)
    rows, invalid = coerce_numeric_rows(rows, [args.x_col, args.y_col], args.drop_incomplete)
    groups = [str(row[args.group_col]) if args.group_col else "All observations" for row in rows]
    group_order = parse_order(args.group_order, groups, "groups")

    fig = plt.figure(figsize=(args.width_mm / MM_PER_INCH, args.height_mm / MM_PER_INCH))
    grid = fig.add_gridspec(4, 4, hspace=0.05, wspace=0.05)
    ax_joint = fig.add_subplot(grid[1:, :3])
    ax_top = fig.add_subplot(grid[0, :3], sharex=ax_joint)
    ax_right = fig.add_subplot(grid[1:, 3], sharey=ax_joint)
    counts: dict[str, int] = {}
    for index, group in enumerate(group_order):
        mask = np.asarray([value == group for value in groups])
        x = np.asarray([row[args.x_col] for row in rows], dtype=float)[mask]
        y = np.asarray([row[args.y_col] for row in rows], dtype=float)[mask]
        counts[group] = len(x)
        color = PALETTE[index % len(PALETTE)]
        ax_joint.scatter(x, y, s=8, alpha=0.42, color=color, edgecolors="none", rasterized=len(rows) > 50000, label=f"{group} (n={len(x)})")
        ax_top.hist(x, bins=args.bins, density=True, histtype="stepfilled", alpha=0.20, color=color)
        ax_top.hist(x, bins=args.bins, density=True, histtype="step", linewidth=0.8, color=color)
        ax_right.hist(y, bins=args.bins, density=True, orientation="horizontal", histtype="stepfilled", alpha=0.20, color=color)
        ax_right.hist(y, bins=args.bins, density=True, orientation="horizontal", histtype="step", linewidth=0.8, color=color)
    ax_joint.set_xlabel(args.x_label or args.x_col)
    ax_joint.set_ylabel(args.y_label or args.y_col)
    ax_joint.legend(loc="best")
    ax_top.tick_params(labelbottom=False)
    ax_right.tick_params(labelleft=False)
    ax_top.set_ylabel("Density")
    ax_right.set_xlabel("Density")
    if args.title:
        ax_top.set_title(args.title)
    paths = save_bundle(fig, args.output)

    qa = base_qa(args, "marginal", len(rows) + len(invalid))
    qa.update({"rows_plotted": len(rows), "excluded_rows": len(invalid)})
    qa["mapping"] = {"x": args.x_col, "y": args.y_col, "group": args.group_col}
    qa["parameters"] = {"group_order": group_order, "group_counts": counts, "histogram_bins": args.bins, "rasterized_marks": len(rows) > 50000}
    return paths, qa


def plot_paired(args: argparse.Namespace) -> tuple[dict[str, str], dict[str, Any]]:
    rows, fields = load_rows(args, "paired")
    required = [args.id_col, args.condition_col, args.value_col]
    require_columns(fields, required)
    rows, invalid = coerce_numeric_rows(rows, [args.value_col], args.drop_incomplete)
    condition_order = parse_order(args.condition_order, (str(row[args.condition_col]) for row in rows), "conditions")
    if len(condition_order) != 2:
        raise ValueError(f"paired template requires exactly two conditions, found {len(condition_order)}")

    subjects: dict[str, dict[str, list[float]]] = {}
    for row in rows:
        subject = str(row[args.id_col])
        condition = str(row[args.condition_col])
        subjects.setdefault(subject, {}).setdefault(condition, []).append(float(row[args.value_col]))
    duplicates = [subject for subject, values in subjects.items() if any(len(values.get(condition, [])) > 1 for condition in condition_order)]
    if duplicates:
        raise ValueError("multiple values per subject-condition pair found; aggregate only with an explicit scientific rule before plotting")
    incomplete = [subject for subject, values in subjects.items() if any(condition not in values for condition in condition_order)]
    if incomplete and not args.drop_incomplete:
        raise ValueError(f"{len(incomplete)} incomplete subject pairs found; fix the data or rerun with explicit --drop-incomplete")
    complete = [subject for subject in subjects if subject not in incomplete]
    if not complete:
        raise ValueError("no complete subject pairs remain")
    values_a = np.asarray([subjects[subject][condition_order[0]][0] for subject in complete])
    values_b = np.asarray([subjects[subject][condition_order[1]][0] for subject in complete])

    fig, ax = plt.subplots(figsize=(args.width_mm / MM_PER_INCH, args.height_mm / MM_PER_INCH))
    for value_a, value_b in zip(values_a, values_b):
        ax.plot([0, 1], [value_a, value_b], color="#B0B0B0", linewidth=0.55, alpha=0.65, zorder=1)
    boxes = ax.boxplot([values_a, values_b], positions=[0, 1], widths=0.34, patch_artist=True, showfliers=False, medianprops={"color": "#222222", "linewidth": 1.0}, whiskerprops={"linewidth": 0.7}, capprops={"linewidth": 0.7})
    for patch, color in zip(boxes["boxes"], ("#9ECAE1", "#FC9272")):
        patch.set(facecolor=color, edgecolor="#555555", alpha=0.55, linewidth=0.7)
    ax.scatter(np.zeros_like(values_a), values_a, s=13, color="#2166AC", edgecolors="white", linewidths=0.35, zorder=3)
    ax.scatter(np.ones_like(values_b), values_b, s=13, color="#B2182B", edgecolors="white", linewidths=0.35, zorder=3)
    ax.set_xticks([0, 1], condition_order)
    ax.set_ylabel(args.value_label or args.value_col)
    if args.title:
        ax.set_title(args.title)
    paths = save_bundle(fig, args.output)

    qa = base_qa(args, "paired", len(rows) + len(invalid))
    qa.update({"rows_plotted": len(complete) * 2, "excluded_rows": len(invalid), "excluded_entities": len(incomplete)})
    qa["mapping"] = {"pair_id": args.id_col, "condition": args.condition_col, "value": args.value_col}
    qa["parameters"] = {"condition_order": condition_order, "complete_pairs": len(complete), "incomplete_pairs_excluded": len(incomplete), "statistical_test": None}
    qa["notes"].append("No inferential test is computed; add one only after choosing a justified paired analysis.")
    return paths, qa


def add_common_arguments(parser: argparse.ArgumentParser, width_mm: float, height_mm: float) -> None:
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--input", type=Path, help="production CSV input")
    source.add_argument("--demo", action="store_true", help="render explicit deterministic demo data")
    parser.add_argument("--output", type=Path, required=True, help="output prefix for SVG/PDF/TIFF/QA JSON")
    parser.add_argument("--width-mm", type=float, default=width_mm)
    parser.add_argument("--height-mm", type=float, default=height_mm)
    parser.add_argument("--title")
    parser.add_argument("--drop-incomplete", action="store_true", help="explicitly exclude rows with missing/non-finite required values and record counts")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    volcano = subparsers.add_parser("volcano", help="effect size versus adjusted p value")
    add_common_arguments(volcano, 89.0, 82.0)
    volcano.add_argument("--gene-col", default="gene")
    volcano.add_argument("--effect-col", default="log2fc")
    volcano.add_argument("--p-col", default="padj")
    volcano.add_argument("--effect-label", default="log₂(fold change)")
    volcano.add_argument("--p-threshold", type=float, default=0.05)
    volcano.add_argument("--effect-threshold", type=float, default=1.0)
    volcano.add_argument("--top-labels", type=int, default=10)
    volcano.set_defaults(plotter=plot_volcano)

    roc = subparsers.add_parser("roc", help="one FPR column and one or more TPR columns")
    add_common_arguments(roc, 89.0, 89.0)
    roc.add_argument("--fpr-col", default="fpr")
    roc.add_argument("--tpr-cols", help="comma-separated TPR columns; defaults to every non-FPR column")
    roc.set_defaults(plotter=plot_roc)

    dotplot = subparsers.add_parser("dotplot", help="marker-gene or other size/color matrix dot plot")
    add_common_arguments(dotplot, 183.0, 105.0)
    dotplot.add_argument("--row-col", default="cell_type")
    dotplot.add_argument("--column-col", default="gene")
    dotplot.add_argument("--size-col", default="pct_exp")
    dotplot.add_argument("--color-col", default="avg_exp_scaled")
    dotplot.add_argument("--row-order", help="comma-separated complete row order")
    dotplot.add_argument("--column-order", help="comma-separated complete column order")
    dotplot.add_argument("--size-label", default="Fraction (%)")
    dotplot.add_argument("--color-label", default="Mean expression")
    dotplot.set_defaults(plotter=plot_dotplot)

    marginal = subparsers.add_parser("marginal", help="2D scatter with marginal distributions")
    add_common_arguments(marginal, 120.0, 105.0)
    marginal.add_argument("--x-col", default="x")
    marginal.add_argument("--y-col", default="y")
    marginal.add_argument("--group-col", default="group")
    marginal.add_argument("--group-order", help="comma-separated complete group order")
    marginal.add_argument("--x-label")
    marginal.add_argument("--y-label")
    marginal.add_argument("--bins", type=int, default=24)
    marginal.set_defaults(plotter=plot_marginal)

    paired = subparsers.add_parser("paired", help="paired box-and-point plot for exactly two conditions")
    add_common_arguments(paired, 89.0, 86.0)
    paired.add_argument("--id-col", default="subject")
    paired.add_argument("--condition-col", default="condition")
    paired.add_argument("--value-col", default="value")
    paired.add_argument("--condition-order", help="comma-separated two-condition order")
    paired.add_argument("--value-label")
    paired.set_defaults(plotter=plot_paired)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        require_dependencies()
        configure_style()
        paths, qa = args.plotter(args)
        qa_path = write_qa(args.output, qa)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"outputs": paths, "qa": str(qa_path)}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
