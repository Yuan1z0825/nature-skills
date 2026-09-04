# Backend: R (ggplot2 / patchwork / ComplexHeatmap)

**R-only execution rule.** When the user has selected R, do all figure drawing, previewing, exporting, and visual QA in R. Do not call matplotlib/seaborn or any Python graphics device to create a temporary preview, fallback export, or layout approximation. If `Rscript`/R or required R packages are missing, pause rendering, continue independent script or data checks, and report the exact blocker. You may still write the R script, provide install commands (for example `install.packages(...)`), or ask permission to install dependencies, but do not cross-render the figure in Python.

## R quick-start

```r
library(ggplot2)
library(patchwork)
source("skills/nature-figure/scripts/panel_alignment.R")

theme_set(
  theme_classic(base_size = 6.5, base_family = "Arial") +
    theme(
      axis.line = element_line(linewidth = 0.35, colour = "black"),
      axis.ticks = element_line(linewidth = 0.35, colour = "black"),
      legend.title = element_text(size = 6.2),
      legend.text = element_text(size = 5.8),
      strip.text = element_text(size = 6.2, face = "bold"),
      plot.title = element_text(size = 7, face = "bold"),
      panel.grid = element_blank()
    )
)

save_pub_r <- function(plot, filename, width_mm = 183, height_mm = 120, dpi = 600) {
  w <- width_mm / 25.4
  h <- height_mm / 25.4
  if (inherits(plot, "patchwork")) {
    # Run after every layout-affecting change, before export.
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

## Going deeper

- `references/r-workflow.md` — the R plotting workflow when the user provides R scripts, templates, or data.
- `references/r-template-index.md` — adapt a user-provided or private R template collection without exposing source paths.
- `references/design-theory.md` — typography, color theory, layout rationale, export policy (backend-agnostic).
- `references/nature-2026-observations.md` — real Nature page archetypes to match before choosing layout.
- `scripts/validate_figure.py` — dependency-free static R source preflight before running R and inspecting the rendered outputs.
- `scripts/audit_pdf_text.py` — inspect the final R-generated PDF's rendered glyph floor without redrawing it.
- `scripts/panel_alignment.R` plus `scripts/audit_panel_alignment.py` — mandatory render-time patchwork/gtable alignment gate for every multi-panel figure; declare comparable groups explicitly for asymmetric layouts.
- `scripts/audit_figure_collisions.py` — mandatory backend-neutral geometry audit after every generated or layout-affecting revision; its optional marked PDF is QA-only and does not replace the R export.
