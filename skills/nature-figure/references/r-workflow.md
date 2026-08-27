# R Workflow

## Contents

- [R-only execution rule](#r-only-execution-rule)
- [Required packages by task](#required-packages-by-task)
- [Contract scaffold](#contract-scaffold)
- [Panel labels in R](#panel-labels-in-r)
- [Patchwork layout patterns](#patchwork-layout-patterns)
- [Patchwork panel-alignment gate](#patchwork-panel-alignment-gate)
- [ComplexHeatmap export](#complexheatmap-export)
- [Template reuse rule](#template-reuse-rule)


Use this when the user chooses R, brings R data/scripts, or asks to reuse the local
R plotting templates. The R track should still follow the same figure contract:
claim first, evidence hierarchy second, plotting code third.

## R-only execution rule

When the user has selected R, do all figure drawing, previewing, exporting, and
visual QA in R. Do not call Python/matplotlib/seaborn/plotly to create a temporary
preview, fallback export, or layout approximation. If R, `Rscript`, or required R
packages are missing, stop before rendering and report the missing dependency. You
may still write the R script, provide `install.packages()` commands, or ask permission
to install dependencies, but do not cross-render the figure in another language.

Allowed non-R utilities are limited to non-visual tasks such as shell file inspection,
CSV line counts, checksums, archive extraction, or text search. They must not create
image/vector outputs or alter visual layout.

## Required packages by task

| Task | Preferred packages |
|---|---|
| Bars, boxplots, violins, dot plots, lines, volcano plots | `ggplot2`, `ggrepel`, `dplyr`, `tidyr` |
| Multi-panel assembly and alignment QA | `patchwork`, `grid`, `jsonlite`; use `cowplot` only when inset alignment requires it |
| Rich omics heatmaps | `ComplexHeatmap`, `circlize`, `grid` |
| Survival and clinical subgroup plots | `survival`, `survminer`, `forestplot`, `ggplot2` |
| Circular/genome plots | `circlize`, `ggtree`, `gggenes`, domain-specific packages |
| Export | `svglite`, `grDevices::cairo_pdf`, `ragg` |

## Contract scaffold

```r
library(ggplot2)
library(patchwork)
source("skills/nature-figure/scripts/panel_alignment.R")

palette_contract <- c(
  neutral_dark = "#272727",
  neutral_mid = "#767676",
  neutral_light = "#D8D8D8",
  signal_blue = "#3182BD",
  signal_teal = "#33B5A5",
  accent_red = "#D24B40",
  accent_orange = "#E28E2C"
)

theme_nature_contract <- function(base_size = 6.5, base_family = "Arial") {
  theme_classic(base_size = base_size, base_family = base_family) +
    theme(
      axis.line = element_line(linewidth = 0.35, colour = "black"),
      axis.ticks = element_line(linewidth = 0.35, colour = "black"),
      axis.title = element_text(size = base_size),
      axis.text = element_text(size = base_size - 0.5),
      legend.title = element_text(size = base_size - 0.3),
      legend.text = element_text(size = base_size - 0.7),
      strip.text = element_text(size = base_size - 0.3, face = "bold"),
      plot.title = element_text(size = base_size + 0.5, face = "bold"),
      panel.grid = element_blank()
    )
}

theme_set(theme_nature_contract())

save_pub_r <- function(plot, filename, width_mm = 183, height_mm = 120, dpi = 600) {
  w <- width_mm / 25.4
  h <- height_mm / 25.4

  if (inherits(plot, "patchwork")) {
    require_patchwork_panel_alignment(
      plot,
      manifest_path = paste0(filename, ".alignment-layout.json"),
      report_path = paste0(filename, ".alignment.json"),
      overlay_svg = paste0(filename, ".alignment.svg"),
      width_in = w,
      height_in = h,
      tolerance_pt = 1.5,
      gutter_tolerance_pt = 1.5,
      strict = TRUE
    )
  }

  svglite::svglite(paste0(filename, ".svg"), width = w, height = h)
  print(plot)
  dev.off()

  grDevices::cairo_pdf(paste0(filename, ".pdf"), width = w, height = h, family = "Arial")
  print(plot)
  dev.off()

  ragg::agg_tiff(paste0(filename, ".tiff"), width = w, height = h, units = "in", res = dpi)
  print(plot)
  dev.off()
}
```

## Panel labels in R

Use patchwork tags for most multi-panel figures:

```r
fig <- (p_a | p_b) / (p_c | p_d) +
  plot_annotation(tag_levels = "a") &
  theme(plot.tag = element_text(size = 8, face = "bold"))
```

Use manual labels only when dark image plates or inset geometry make patchwork tags
misalign.

## Patchwork layout patterns

### Quantitative grid

```r
fig <- (p_a | p_b | guide_area()) /
       (p_c | p_d | p_e) +
  plot_layout(guides = "collect", widths = c(1, 1, 0.45)) &
  theme(legend.position = "right")
```

### Schematic-led composite

```r
design <- "
AAAA
BBCD
"
fig <- p_schematic + p_b + p_c + p_d +
  plot_layout(design = design, heights = c(1.8, 1))
```

### Image plate plus quant

Keep black backgrounds inside image panels only. Put scale bars on the image, then
place quantification next to or below the representative image.

```r
p_img <- ggplot(img_df, aes(x, y, fill = intensity)) +
  geom_raster() +
  scale_fill_gradient(low = "black", high = "white") +
  coord_fixed(expand = FALSE) +
  annotate("segment", x = 10, xend = 40, y = 10, yend = 10,
           linewidth = 0.6, colour = "white") +
  theme_void() +
  theme(legend.position = "none", plot.background = element_rect(fill = "black", colour = NA))
```

## Patchwork panel-alignment gate

`panel_alignment.R` converts the final patchwork gtable cells to physical-point
rectangles on a temporary R graphics device with the same dimensions as the
real export. It then invokes the backend-neutral
`audit_panel_alignment.py` JSON auditor. Python does not render or modify the R
figure.

Simple patchwork grids infer row/column groups from gtable cells. Structured
unequal-span designs are also automatic: two stacked panels in the left column
beside one two-row panel in the right column, and the mirrored arrangement,
receive shared top/bottom boundary checks without an invalid equal-height
comparison. Horizontal groups of three or four equal gtable spans must also
have equal final widths; intentional unequal widths require a reasoned
`panel-width` exemption. For nested or manually composed figures, declare the intended
comparisons explicitly:

```r
require_patchwork_panel_alignment(
  fig,
  manifest_path = "figures/fig2.alignment-layout.json",
  report_path = "figures/fig2.alignment.json",
  overlay_svg = "figures/fig2.alignment.svg",
  width_in = 183 / 25.4,
  height_in = 120 / 25.4,
  panel_ids = c("a", "b", "c", "d"),
  row_groups = list(c("a", "b"), c("c", "d")),
  column_groups = list(c("a", "c"), c("b", "d")),
  exemptions = list(
    list(
      panels = c("a"),
      checks = c("column", "panel-width"),
      reason = "hero panel intentionally spans the evidence columns"
    )
  ),
  tolerance_pt = 1.5,
  gutter_tolerance_pt = 1.5,
  strict = TRUE
)
```

Every exemption must name the panel, the exact check and the reason. Do not
increase the global tolerance to hide an inset, colorbar, legend-only cell or
hero panel. A non-zero audit status stops the R delivery script. Preserve both
the measured layout manifest and audit JSON; the alignment SVG is QA-only.

## ComplexHeatmap export

`ComplexHeatmap` objects are grid objects, not ggplot objects. Export them by opening
the graphics device, drawing, then closing it.

```r
library(ComplexHeatmap)
library(circlize)

pdf("heatmap.pdf", width = 7.2, height = 4.8, family = "Arial")
draw(ht, heatmap_legend_side = "right", annotation_legend_side = "right")
dev.off()

svglite::svglite("heatmap.svg", width = 7.2, height = 4.8)
draw(ht, heatmap_legend_side = "right", annotation_legend_side = "right")
dev.off()
```

## Template reuse rule

The local R materials are examples, not final style. When reusing them:

1. Inspect only the nearest template folder.
2. Keep useful data wrangling, statistics, and geoms.
3. Replace ad hoc colors, oversized fonts, dense legends, and PNG-only export.
4. Rebuild the final script around `theme_nature_contract()` and `save_pub_r()`.
5. Add source-data output if the figure is manuscript-facing.

Open `references/r-template-index.md` for the local template atlas.
