# Flagship Nature Article figure requirements

Use this reference for figures submitted to the flagship journal **Nature**.
Keep initial-review files separate from accepted-in-principle production files,
and do not apply these formats automatically to Nature Portfolio subjournals.

## Contents

1. Stage gate
2. Initial-submission figures
3. Legend contract
4. Production dimensions and typography
5. Main-figure production files
6. Extended Data production files
7. Accessibility and image integrity
8. Delivery audit
9. Official sources

## 1. Stage gate

Record one stage before auditing:

- `initial_submission`: figures may be embedded in the Word/PDF manuscript;
  production-quality files are not required
- `revision`: follow both the public guide and the editor's instructions
- `accepted_in_principle`: supply production-quality main figures and Extended
  Data using their different file contracts

Do not fail an initial submission solely because it lacks separate editable
production artwork. Do fail it when the displayed data are unreadable,
misrepresented, incomplete or impossible for referees to assess.

## 2. Initial-submission figures

- Prefer figures embedded with manuscript text in one Word or PDF file.
- Put each figure legend on the same page as its figure.
- Use enough resolution for referees to evaluate the data.
- If embedding is impractical, supply separate files or an accessible
  repository route and confirm every figure is cited.
- Run the statistics, source-data and image-integrity checks even though final
  artwork formatting is deferred.

## 3. Legend contract

For every flagship Nature figure legend:

- keep the complete legend below 250 words
- begin with a brief title sentence for the whole figure
- follow with a concise description of what each panel depicts
- do not use the legend to narrate results or duplicate Methods
- include definitions needed to understand the figure in isolation
- state exact `n`, replicate definition, center/spread, error bars, test,
  correction and P-value display where applicable
- identify adaptations and permissions when third-party material is used

Table legends begin with a short title sentence; explanatory detail may go in
footnotes.

## 4. Production dimensions and typography

For accepted-in-principle main figures:

- use 89 mm for a single-column figure or 183 mm for a double-column figure
- do not exceed 170 mm height, leaving room for the legend
- keep ordinary figure text between 5 pt and 7 pt at final size
- label multi-panel figures with 8 pt bold upright lowercase `a`, `b`, `c`, etc.
- use a consistent sans-serif typeface, preferably Arial or Helvetica
- use Courier or another monospaced font for amino-acid sequences
- keep all text editable, do not outline it, and embed TrueType 2 or 42 fonts
- arrange panels alphabetically where practical and minimize unused space

## 5. Main-figure production files

Main figures require vector artwork with editable layers.

Preferred:

- `.ai`
- `.eps`
- editable `.pdf`

Also accepted by the current research figure guide when properly prepared:

- layered Photoshop artwork
- PowerPoint converted to PDF
- plain `.svg`
- Excel
- `.ps`

Do not submit flattened `.jpeg`, `.tiff` or `.png` as the final main-figure
production file merely because the workflow also creates those formats for QA
or preview. Keep all components embedded rather than externally linked and aim
to keep each file below 50 MB.

## 6. Extended Data production files

Extended Data has a different production contract:

- save in RGB
- use no more than 300 dpi
- keep each file at or below 10 MB
- use `.jpeg` preferably, or `.tiff`/`.eps`
- fit each item on one page with room for its legend or footnotes
- use the journal's required filename pattern based on the corresponding
  author's surname and the ED figure/table number

Do not send a main figure through the Extended Data file route or vice versa.

## 7. Accessibility and image integrity

- include axis lines and tick marks
- label every axis and place units in parentheses
- avoid background gridlines, drop shadows, decorative icons, patterns,
  overlapping labels and coloured text
- use an accessible palette; do not rely on red/green or rainbow scales
- supply artwork in RGB; photographic images need at least 300 dpi, with
  450 dpi preferred for the highest online-proof resolution
- keep scale bars and their labels editable rather than flattened into images
- use scale bars instead of magnification factors

For microscopy, gels, blots or other processed images, load the image-integrity
section of `../../nature-shared/core/research-compliance.md`. Record raw-file
provenance, crop, contrast, gamma, pseudocolour, stitching, lane rearrangement
and processing software.

## 8. Delivery audit

Return:

| Item | Stage | Required contract | Current file/evidence | Status | Action |
|---|---|---|---|---|---|

Before approval:

- run `scripts/validate_figure.py` on plotting source
- run `scripts/audit_pdf_text.py` on exported PDF text
- inspect every panel and the assembled figure at final physical size
- verify that preview/export bundles are not mislabeled as the journal's final
  accepted upload formats

## 9. Official sources

Verified 2026-08-08:

- Nature initial submission: <https://www.nature.com/nature/for-authors/initial-submission>
- Preparing figures: <https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/>
- Building and exporting figure panels: <https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/>
- Image integrity: <https://www.nature.com/nature-portfolio/editorial-policies/image-integrity>
