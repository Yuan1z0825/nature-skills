# Source: scanned PDF (OCR required)

The PDF is image-only or has an unreliable text layer. Load the `pdf` skill first for OCR guidance.

- OCR every page; do not assume a usable text layer exists.
- Record a confidence level for each block in the source map, and mark low-confidence blocks explicitly in `translation_notes.md` rather than guessing.
- Preserve the original wording where OCR is confident; flag, do not silently "correct", garbled text.
- Be careful with numerals, units, symbols, gene/protein names, and chemical formulas — OCR errors here change meaning. Cross-check against context and mark uncertainty.
- Treat every display equation as an image-first `E...` block: crop the original formula before attempting math OCR. Show the crop in `paper.md`; include OCR-derived LaTeX only as a visibly low-confidence convenience layer until every symbol is verified.
- Never silently repair or guess a scanned equation from surrounding prose.
- Figures and tables are page regions: crop them per `references/figure-extraction.md`. For low-quality scans, a tight correct crop still beats a wide noisy one.
- If pages are skewed, rotated, or partly cut off, note the affected pages and translate only what is legible.
