# Figure and table assets

Open this reference for steps 4-5: selecting figures as evidence, extracting and preparing assets, and the figure-crop self-check.

## Step 4 detail — select figures as evidence, not decoration

Inspect the source for: graphical abstracts or summary models; study design and workflow diagrams; central result figures; microscopy or imaging panels; heatmaps, dimensionality reduction, networks, maps, or spatial plots; survival curves, forest plots, calibration curves, or statistical result plots; materials characterization and performance plots; model architecture, benchmark, ablation, or error analysis figures; key tables; validation or control figures.

Prioritize figures that carry the paper's argument:

1. design/workflow,
2. main evidence,
3. validation or robustness,
4. mechanism/model/synthesis,
5. practical or conceptual implication.

Prefer a few readable key panels over many unreadable full figures.

## Step 5 detail — extract and prepare figure assets

When the source contains usable figures:

- extract original images from the PDF or source package when possible, but only for selected figures,
- render high-resolution page images only for pages containing selected figures or tables,
- crop relevant panels when full figures are too dense,
- keep original data visuals unchanged,
- save images under `output/assets/figures/`,
- use clear filenames such as `fig1_workflow.png`, `fig2b_main_result.png`, or `fig4ef_validation.png`,
- record source page, figure number, panel, crop status, and intended slide in `output/asset_manifest.md`.

For a standard 10-14 slide journal-club deck, usually select 4-8 figure/table assets. Add more only when they directly support distinct evidence slides.

For tables and simple quantitative comparisons, prefer editable PPT-native tables/charts when values are explicit in the paper text or table. Use table screenshots only when recreating the table would risk transcription errors or when layout/formatting itself is the evidence.

If extraction fails, use the best available fallback:

- rendered page screenshot with careful crop,
- recreated editable table only when values are explicitly available,
- clearly labeled placeholder only when the visual is unavailable.

## Figure crop self-check before slide insertion

Before building the final PPTX, create a quick contact sheet or inspect selected crops directly. This is a cheap way to catch the most common deck defects before they become slide defects.

Check every selected figure/table asset for:

- clipped titles, axis labels, legends, panel letters, or source figure labels,
- irrelevant surrounding paper text or captions included in the crop,
- too little margin around the crop, especially at the top and left edges,
- unreadable small text after the planned slide scaling,
- dense multi-panel figures that should be split into separate slides or cropped to key panels,
- low-resolution or blurry rendering.

Revise the crop before placing it in the PPTX when any scientific context is cut off. A figure crop that loses a title, y-axis label, legend, or panel label is a defect, not an acceptable tradeoff.

## Crop QA hard gate

Treat figure crops as evidence, not decoration. A crop is not acceptable until it passes all applicable checks below:

- panel letters are present when the slide refers to a panel letter,
- x/y axes, axis titles, tick labels, color bars, legends, scale bars, and table headers are preserved when they are needed to read the evidence,
- method labels, condition names, group labels, and sample labels remain visible,
- the crop has a small safety margin around the scientific content rather than cutting exactly at the ink boundary,
- the planned slide placement still leaves the figure readable without asking the audience to zoom,
- no caption, source note, or callout covers original scientific labels.

If any item fails, fix the asset before authoring the slide. Use one of these repairs:

1. expand the crop rectangle,
2. split the source figure across two slides,
3. use a full-width hero figure slide,
4. recreate a simple table/chart natively when values are explicit,
5. replace the crop with a higher-resolution source image.

Record the pass/fail result in `output/asset_manifest.md`. Use compact fields such as:

```text
asset: fig2b_main_result.png
source: Fig. 2b, p. 5
slide: 7
method: pdf page render at 300 dpi, manual crop
crop_qa: pass
preserved: panel label, axes, legend, colorbar
notes: split from Fig. 2 because full figure was unreadable at slide scale
```

If the crop is a deliberate partial crop, state exactly what was omitted and why it is not needed for the slide's claim.
