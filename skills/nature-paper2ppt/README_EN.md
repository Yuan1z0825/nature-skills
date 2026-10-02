# `nature-paper2ppt` Skill

[中文说明](README.md)

`nature-paper2ppt` converts scientific papers, preprints, PDFs, figure legends, or reading notes into Chinese PowerPoint decks for group meetings, journal clubs, paper sharing, and pre-defense preparation.

## What To Use It For

- Reorganize a paper into a 10-16 slide Chinese presentation instead of copying the article structure.
- Extract the research question, key claims, core evidence, limitations, and reusable value.
- Select figures and tables that support the narrative, cropping or splitting dense plates when needed.
- Generate editable `.pptx`, speaker notes, and lightweight QA reports.
- Translate Nature-style evidence narrative into short slide text and live-presentation structure.

## Typical Requests

- "Turn this Nature Communications paper into a 12-slide Chinese group-meeting PPT."
- "Use the abstract and figure legends to make a first paper-presentation draft; keep it concise."
- "Make this machine-learning paper into a deck with clear method, results, and limitations."

## What You Need To Provide

- Paper PDF, DOI, arXiv link, publisher page, abstract plus figure legends, or reading notes.
- Presentation duration, audience background, slide-count range, and whether speaker notes are needed.
- Whether original figures must be preserved and whether cropping or redrawing schematics is allowed.

## Outputs

- Editable PowerPoint file.
- Figure-asset manifest and crop/source notes.
- Slide titles, bullets, takeaways, and speaker notes.
- Package checks for embedded media, slide count, notes, and layout risks.

## Boundaries

- The skill does not turn paper content into generic, untraceable summaries.
- If image quality is poor, the PDF is scanned, or figures cannot be extracted, the limitation and alternative are stated.
- For full translation or paragraph-level reading, use `nature-reader` first.

## Related Skills

- `nature-reader`: build full Chinese-English reading material and a figure source map first.
- `nature-figure`: redraw mechanism or method diagrams for the deck.
- `presentations`: further edit the generated PPTX layout.
