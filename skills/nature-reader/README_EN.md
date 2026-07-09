# `nature-reader` Skill

[中文说明](README.md)

## What It Does

- Creates source-grounded full-paper Markdown readers with Chinese-English side-by-side translation, figure/table awareness, and source anchors.

## When to Use It

- You want to read or translate a complete paper rather than only summarize it.
- You need figures and tables placed near relevant text.
- You want source-grounded notes that preserve structure and citations.

## Copy-Paste Prompts

- `Turn this PDF into a figure-aware Chinese-English Markdown reader.`
- `Create a full-paper Markdown reading note with figures placed near the relevant sections.`
- `Translate this paper with original text, Chinese translation, and source anchors.`

## Required Inputs

- PDF, DOI, arXiv link, publisher HTML, pasted article text, or extracted figures/tables.
- Optional output path and language preferences.

## Expected Outputs

- Full Markdown reader.
- Chinese-English side-by-side sections.
- Figure/table placement notes and source anchors.
- Uncertainty notes when extraction is incomplete.

## Dependencies / API Keys / Local Environment

- PDF extraction or rendering tools may be required for scanned or layout-heavy papers.
- Internet access may be needed for DOI or publisher retrieval.

## FAQ

- **Does it summarize or translate?** It focuses on full-paper reading and translation, with summaries included only when helpful.
- **Can it handle scanned PDFs?** Only if OCR or visual extraction is available; otherwise it should report the limitation.

## Related Skills

- [`nature-paper2ppt`](../nature-paper2ppt/README_EN.md)
- [`nature-academic-search`](../nature-academic-search/README_EN.md)
- [`nature-polishing`](../nature-polishing/README_EN.md)
