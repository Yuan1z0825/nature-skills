# Output contract

Prefer these outputs:

- `paper.md` for the full-paper Markdown artifact
- `source_map.json` for stable source anchors
- `translation_notes.md` for terminology, uncertainty, and layout notes
- `assets/` for extracted figures, tables, and equation crops when needed
- `reader.html` only when the user explicitly wants a browser preview

Do not hide missing information. If the source is incomplete, label the output as draft mode.

## Pre-response verification

Before final response, verify:

- `paper.md` contains `**Original:**` and `**中文:**` block pairs
- every image/table link used in `paper.md` exists under `assets/`
- every figure/table in `assets/` has a corresponding Markdown block and source pointer
- display equations render inside `$$...$$` (or a fenced `math` block), and inline equations render inside `$...$`
- mathematical content is unchanged across the bilingual explanation: only prose is translated, each display equation is shown once, and Chinese text never uses `(I_0)`-style pseudo-math
- no bare LaTeX commands such as `\\frac`, `\\sum`, or `\\begin{...}` appear as ordinary prose
- every display equation has an `E...` anchor and a matching equation entry in `source_map.json`
- every low-confidence or image-only equation points to an existing file under `assets/equations/`
- `source_map.json` parses as JSON and includes source block IDs
- `translation_notes.md` records skipped, uncertain, or draft-mode content

Run the deterministic math check before delivery:

```bash
python scripts/validate_reader_math.py paper.md --source-map source_map.json
```

Add `--strict` for a published or reusable artifact. The command checks delimiters, bare LaTeX, equation IDs, source-map linkage, and equation fallback paths.

## Tooling guidance

- If the input is a PDF, load the `pdf` skill first for extraction and OCR guidance.
- If the user asks for a richer browser view, use `web-artifacts-builder` or `frontend-design` only as a preview layer on top of the Markdown workflow.
- If the user wants citation-level grounding to original text, keep the source map explicit and do not lose the page or block IDs.
