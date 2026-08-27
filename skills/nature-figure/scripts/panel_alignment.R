# Render-time panel-alignment helper for R patchwork figures.
#
# Source this file from the selected R plotting script. It measures patchwork's
# final panel cells on a device with the same physical dimensions as the export,
# writes the backend-neutral JSON manifest consumed by audit_panel_alignment.py,
# and can run the blocking audit in one call.

.nature_alignment_groups <- function(groups) {
  if (is.null(groups)) {
    return(NULL)
  }
  lapply(groups, function(group) as.character(unlist(group, use.names = FALSE)))
}

.nature_alignment_panel_rows <- function(grob) {
  rows <- grob$layout[grepl("^panel(?:-[0-9]+)?$", grob$layout$name, perl = TRUE), , drop = FALSE]
  if (nrow(rows) < 2) {
    stop("At least two patchwork panel cells are required for alignment QA", call. = FALSE)
  }
  rows[order(rows$t, rows$l), , drop = FALSE]
}

write_patchwork_panel_layout <- function(
  plot,
  manifest_path,
  width_in,
  height_in,
  panel_ids = NULL,
  row_groups = NULL,
  column_groups = NULL,
  exemptions = list()
) {
  for (package in c("patchwork", "grid", "jsonlite")) {
    if (!requireNamespace(package, quietly = TRUE)) {
      stop(sprintf("Package '%s' is required for patchwork alignment QA", package), call. = FALSE)
    }
  }
  if (!is.numeric(width_in) || length(width_in) != 1 || !is.finite(width_in) || width_in <= 0 ||
      !is.numeric(height_in) || length(height_in) != 1 || !is.finite(height_in) || height_in <= 0) {
    stop("width_in and height_in must be positive finite numbers", call. = FALSE)
  }

  grob <- patchwork::patchworkGrob(plot)
  panel_rows <- .nature_alignment_panel_rows(grob)
  if (is.null(panel_ids)) {
    panel_ids <- vapply(
      seq_len(nrow(panel_rows)),
      function(index) if (index <= length(letters)) letters[index] else paste0("panel-", index),
      character(1)
    )
  }
  panel_ids <- as.character(panel_ids)
  if (length(panel_ids) != nrow(panel_rows) || anyDuplicated(panel_ids) || any(!nzchar(panel_ids))) {
    stop("panel_ids must be unique, non-empty, and match the measured patchwork panels", call. = FALSE)
  }

  probe_path <- tempfile(fileext = ".pdf")
  grDevices::pdf(probe_path, width = width_in, height = height_in, useDingbats = FALSE)
  device_open <- TRUE
  on.exit({
    if (device_open) {
      grDevices::dev.off()
    }
    unlink(probe_path)
  }, add = TRUE)
  grid::grid.newpage()
  grid::grid.draw(grob)
  grid::grid.force()

  widths_pt <- grid::convertWidth(grob$widths, "pt", valueOnly = TRUE)
  heights_pt <- grid::convertHeight(grob$heights, "pt", valueOnly = TRUE)
  if (any(!is.finite(widths_pt)) || any(!is.finite(heights_pt))) {
    stop("Patchwork panel dimensions could not be converted to physical points", call. = FALSE)
  }
  x_edges <- c(0, cumsum(widths_pt))
  top_edges <- c(0, cumsum(heights_pt))
  total_height_pt <- sum(heights_pt)

  panels <- lapply(seq_len(nrow(panel_rows)), function(index) {
    row <- panel_rows[index, ]
    left <- x_edges[row$l]
    right <- x_edges[row$r + 1]
    top <- total_height_pt - top_edges[row$t]
    bottom <- total_height_pt - top_edges[row$b + 1]
    list(
      id = panel_ids[index],
      bbox_pt = unname(c(left, bottom, right, top)),
      grid_id = "patchwork-grid-1",
      row_start = as.integer(row$t - 1),
      row_stop = as.integer(row$b),
      col_start = as.integer(row$l - 1),
      col_stop = as.integer(row$r)
    )
  })

  manifest <- list(
    schema_version = 1L,
    backend = "r-patchwork",
    figure = list(width_pt = width_in * 72, height_pt = height_in * 72),
    panels = panels,
    exemptions = exemptions
  )
  normalized_rows <- .nature_alignment_groups(row_groups)
  normalized_columns <- .nature_alignment_groups(column_groups)
  if (!is.null(normalized_rows)) {
    manifest$row_groups <- normalized_rows
  }
  if (!is.null(normalized_columns)) {
    manifest$column_groups <- normalized_columns
  }

  dir.create(dirname(manifest_path), recursive = TRUE, showWarnings = FALSE)
  temporary_path <- tempfile(pattern = ".panel-layout-", tmpdir = dirname(manifest_path), fileext = ".json")
  jsonlite::write_json(manifest, temporary_path, auto_unbox = TRUE, pretty = TRUE, digits = NA)
  if (!file.rename(temporary_path, manifest_path)) {
    unlink(temporary_path)
    stop("Could not activate the patchwork alignment manifest atomically", call. = FALSE)
  }

  grDevices::dev.off()
  device_open <- FALSE
  unlink(probe_path)
  invisible(manifest)
}

require_patchwork_panel_alignment <- function(
  plot,
  manifest_path,
  report_path,
  width_in,
  height_in,
  panel_ids = NULL,
  row_groups = NULL,
  column_groups = NULL,
  exemptions = list(),
  audit_script = "skills/nature-figure/scripts/audit_panel_alignment.py",
  python = Sys.which("python"),
  overlay_svg = NULL,
  tolerance_pt = 1.5,
  gutter_tolerance_pt = 1.5,
  strict = TRUE
) {
  if (!nzchar(python)) {
    stop("Python is required for the backend-neutral panel-alignment JSON audit", call. = FALSE)
  }
  if (!file.exists(audit_script)) {
    stop(sprintf("Panel-alignment audit script not found: %s", audit_script), call. = FALSE)
  }
  write_patchwork_panel_layout(
    plot = plot,
    manifest_path = manifest_path,
    width_in = width_in,
    height_in = height_in,
    panel_ids = panel_ids,
    row_groups = row_groups,
    column_groups = column_groups,
    exemptions = exemptions
  )

  args <- c(
    shQuote(audit_script),
    shQuote(manifest_path),
    "--json-out", shQuote(report_path),
    "--tolerance-pt", format(tolerance_pt, scientific = FALSE),
    "--gutter-tolerance-pt", format(gutter_tolerance_pt, scientific = FALSE)
  )
  if (!is.null(overlay_svg)) {
    args <- c(args, "--overlay-svg", shQuote(overlay_svg))
  }
  if (isTRUE(strict)) {
    args <- c(args, "--strict")
  }
  output <- suppressWarnings(system2(python, args = args, stdout = TRUE, stderr = TRUE))
  status <- attr(output, "status")
  if (is.null(status)) {
    status <- 0L
  }
  if (length(output)) {
    message(paste(output, collapse = "\n"))
  }
  if (status != 0L) {
    stop(
      sprintf("Panel alignment gate failed with exit code %d; inspect %s", status, report_path),
      call. = FALSE
    )
  }
  invisible(jsonlite::read_json(report_path, simplifyVector = TRUE))
}
