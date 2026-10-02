# Source: selectable-text PDF

The PDF has an extractable text layer. Load the `pdf` skill first for extraction guidance.

- Extract the text layer directly; do not OCR text that is already selectable.
- Process the whole document, not just the first pages. Build the source map (step 2) across every page.
- Watch for multi-column layouts: recover natural reading order rather than top-to-bottom raw stream order.
- Keep ligatures, hyphenated line breaks, superscripts, subscripts, and math intact; rejoin words split across line breaks.
- Detect display equations as independent `E...` blocks. Plain-text extraction often destroys fractions, matrices, alignment, and symbol placement, so verify each equation against the rendered PDF page before writing LaTeX.
- Use native math objects or embedded LaTeX when available. If visual verification still leaves ambiguity, crop the original equation and use the low-confidence fallback in `references/equation-handling.md`.
- Figures and tables are images embedded in the page — crop them per `references/figure-extraction.md`; do not paste the page text of a table where the table image belongs.
- If some pages have a text layer and others are scanned, treat the scanned pages with the `scanned-pdf` rules and mark them with a confidence note.
