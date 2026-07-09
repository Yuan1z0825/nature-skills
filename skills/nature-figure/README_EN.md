# `nature-figure` Skill

[中文说明](README.md)

## What It Does

- Creates, revises, and audits submission-grade scientific figures for Nature and other high-impact journals using Python or R workflows, with optional OpenRouter GPT Image 2 schematic drafting.

## When to Use It

- You need publication-quality plots, multi-panel figures, graphical abstracts, or manuscript schematics.
- You want to convert rough analysis into editable SVG/PDF/TIFF figure outputs.
- You need a figure QA pass for typography, labels, color, panel logic, and journal constraints.

## Copy-Paste Prompts

- `Create a Nature-style multi-panel figure from this dataset and methods description.`
- `Polish this matplotlib figure for submission and export editable SVG plus high-resolution TIFF.`
- `Use OpenRouter GPT Image 2 to draft a manuscript schematic from this mechanism description.`
- `Audit this figure for Nature-style readability, color, labels, and panel layout.`

## Required Inputs

- Data files, analysis code, sketch, figure goal, target journal, panel plan, and preferred backend.
- Optional Python/R preference. The skill can persist the first backend choice for future use.
- Optional OpenRouter API key for GPT Image 2 schematic drafting.

## Expected Outputs

- Editable figure files such as SVG/PDF and high-resolution raster exports when requested.
- Plotting scripts and reproducibility notes.
- Schematic-generation prompts or image drafts.
- Figure QA checklist and revision suggestions.

## Dependencies / API Keys / Local Environment

- Python or R plotting environment depending on the selected backend.
- Optional OpenRouter credentials for GPT Image 2 image generation.
- Some outputs may require fonts, vector-export support, or image-conversion tools.

## FAQ

- **Should I choose Python or R every time?** No. The workflow should ask the first time if needed and reuse the stored preference later.
- **Can GPT Image 2 generate final publication figures?** Treat generated schematics as drafts; scientific accuracy and editable redraw should still be verified.
- **What is the preferred output format?** Editable vector output is preferred for manuscript figures, with journal-required raster exports generated as needed.

## Related Skills

- [`nature-paper2ppt`](../nature-paper2ppt/README_EN.md)
- [`nature-writing`](../nature-writing/README_EN.md)
- [`nature-response`](../nature-response/README_EN.md)
