# figures4papers Reference Index

Use this file when a user asks for a `figures4papers` look, cites the older
`scientific-figure-making` skill, or needs a concrete Python/matplotlib reference.

The retained third-party files live under `../assets/figures4papers/`. Before
opening or adapting them, read
`../assets/figures4papers/THIRD_PARTY_NOTICES.md`. These materials are not
automatically covered by the root MIT License, and their inclusion does not grant
additional reuse rights.

## Use boundary

1. Study layout, palette, axes, legends, and export structure as reference patterns.
2. Reimplement with original code and the user's own data whenever the upstream
   license or written permission does not clearly authorize copying or modification.
3. Never reuse manuscript-specific labels, metric values, statistical results, or
   visual assets as placeholders for real evidence.
4. Record the external reference and implementation provenance in the internal QA
   record when it materially influenced the result.
5. Preserve the editable SVG/PDF/TIFF and source-data rules from `api.md` and
   `qa-contract.md`.

## Retained project map

| Project | Open when | Local references |
|---------|-----------|------------------|
| `figure_ImmunoStruct` | Method-comparison and ablation bars | `../assets/figures4papers/figure_ImmunoStruct/` |
| `figure_CellSpliceNet` | Compact benchmark and cross-species bars | `../assets/figures4papers/figure_CellSpliceNet/` |
| `figure_brainteaser` | Category, rewriting, and self-correction panels | `../assets/figures4papers/figure_brainteaser/` |
| `figure_VIGIL` | Radar, trend, ablation, and probability/manifold panels | `../assets/figures4papers/figure_VIGIL/` |
| `figure_ophthal_review` | Time trends and composition heatmaps | `../assets/figures4papers/figure_ophthal_review/` |
| `figure_RNAGenScape` | Heatmaps, optimization, manifold, and sweep plots | `../assets/figures4papers/figure_RNAGenScape/` |
| `figure_Dispersion` | Conceptual sphere and observation panels | `../assets/figures4papers/figure_Dispersion/` |
| `figure_Cflows` | Diffusion, trajectory, comparison, and ablation panels | `../assets/figures4papers/figure_Cflows/` |
| `figure_FPGM` | Frequency-prior or distribution-style motivation | `../assets/figures4papers/figure_FPGM/` |

## Prefer repository-owned implementation paths

When copying is not clearly authorized, route the pattern through the repository's
own material:

| Requested pattern | Open and use |
|-------------------|--------------|
| Grouped bars, ablation bars, shared legends | `tutorials.md`, `common-patterns.md` |
| Radar or polar comparison | `chart-types.md`, then implement with original code |
| Trends, sweeps, and reference baselines | `tutorials.md`, `chart-types.md` |
| Heatmap or annotated matrix | `tutorials.md`, `template-catalog.md` |
| Probability or manifold concept panel | `chart-types.md` |
| Submission typography, palette, and export | `api.md`, `design-theory.md` |
| CSV-driven reproducible plots | `template-catalog.md`, `scripts/plot_templates.py` |

## Upstream source

<https://github.com/ChenLiu-1996/figures4papers>

Check the current upstream license and obtain permission when required before
redistributing, modifying, or publishing derived materials.
