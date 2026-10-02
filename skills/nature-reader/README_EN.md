# `nature-reader` Skill

[中文说明](README.md)

`nature-reader` converts paper PDFs, DOIs, arXiv links, publisher HTML, or pasted text into traceable full-paper Markdown readers with Chinese-English text, figure/table placement, rendered equations, and a source map.

## What To Use It For

- Create full-paper Chinese-English Markdown readers.
- Insert figures, tables, and translated legends near the first substantive discussion.
- Build page and source anchors for every paragraph, figure, and table.
- Render equations as Markdown math and assign a stable `E...` anchor to every display equation.
- Preserve original equation crops when a scanned or image-only expression cannot be transcribed reliably.
- Extract reviewable reading materials from PDFs, HTML, or preprint text.
- Produce reading notes that can support later writing, presentations, or citation checks.

## Typical Requests

- "Turn this PDF into a full Chinese-English Markdown reader."
- "Translate and explain this paper, placing figures near the relevant text."
- "Use this DOI to get the paper content and generate a reader with a source map."

## What You Need To Provide

- PDF, DOI, arXiv link, publisher HTML, title, or pasted text.
- Output directory and whether image cropping is needed.
- Whether to keep English original text, Chinese translation, figures, tables, and translation notes.

## Outputs

- `paper.md`: full reading material.
- `source_map.json`: mapping for pages, text blocks, and figures/tables.
- `translation_notes.md`: terminology, uncertain content, and translation notes.
- `assets/`: figures, cropped images, and required attachments.
- `assets/equations/`: original crops for low-confidence or image-only equations when needed.

## Boundaries

- The default output is Markdown-centered; it does not generate an interactive Q&A panel by default.
- Scanned PDFs, two-column ordering, or copyright-restricted full text may need additional human checking; image-only equations retain an original crop and an explicit transcription confidence.
- If full text cannot be legally obtained, the skill states the limitation and works from available abstract/metadata.

## Related Skills

- `nature-downloader`: legally obtain PDF or HTML full text first.
- `nature-paper2ppt`: turn reading materials into Chinese presentation slides.
- `nature-citation`: extract claims that need citation support.
