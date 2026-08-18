# `nature-image2ppt` Skill

[中文说明](README.md)

`nature-image2ppt` reconstructs existing slide images, screenshots, scanned PDFs, or image-only PPTX files as object-level editable PowerPoint decks; it restores existing visual pages rather than authoring a new presentation from notes.

## What To Use It For

- Convert one or more slide images into an editable `.pptx` deck.
- Recover text, shapes, and page structure from scanned PDFs, screenshots, or image-only PPTX files.
- Rebuild text boxes, cards, circle nodes, connectors, arrows, formulas, and measurable curves as native objects.
- Preserve complex local visuals as replaceable image assets when a native redraw would be unreliable.
- Preserve speaker notes from source PPTX files and run rendered QA on pages and the final deck.

## Typical Requests

- "Reconstruct these slide screenshots as a PowerPoint with individually editable elements."
- "Convert this scanned PDF into an editable PPTX while preserving the original layout."
- "Repair this image-only deck so its flowchart, knowledge graph, and arrows are editable."

## What You Need To Provide

- Slide images, a scanned PDF, or an image-only PPT/PPTX file.
- Any required page range, language, slide size, or font constraints; omit them when there are no special requirements.
- Whether complex illustrations may remain as separate image assets and whether processing must stay offline.

## Workflow

1. Check the runtime, normalize inputs, and generate OCR text hints.
2. Decompose each page into semantic regions and use mixed native-object and local-image reconstruction.
3. Run structure, arrow, region-decomposition, and rendered checks on each page; visual conclusions require itemized evidence bound to the current source/render hashes rather than a generic approval note.
4. Assemble the final PPTX from structured v2 page manifests, then revalidate rendering and speaker notes.

## Outputs

- An object-level editable PowerPoint file.
- Per-page manifests, text hints, rendered previews, and QA reports.
- Final validation results and a list of complex visuals retained as replaceable image assets.
- Page outputs confined to their owning page directory and atomic final output confined to the prepared run, so a failed build cannot publish a partial deck.

## Runtime and Dependencies

- Use Python 3.10 or later and install `requirements.txt`.
- Copying or synchronizing the skill does not install Python packages; install them in the same Python environment that runs the CLI and require `doctor --json` to pass.
- Use Microsoft PowerPoint on Windows or LibreOffice for rendered checks; follow the result of `python cli/image2ppt/cli.py doctor --json`.
- Online text recognition uses a Baidu AI Studio `PADDLE_OCR_TOKEN`. Copy `config.example.yaml` to the adjacent `config.yaml` and fill the Token there; Git ignores the real configuration and it must never be committed.
- The complete implementation is synchronized from [Paul-Jeo/Image2PPT](https://github.com/Paul-Jeo/Image2PPT), with its MIT License retained in this skill directory.

## Boundaries

- The skill only reconstructs existing pages; use `nature-paper2ppt` to author a new deck from a paper, outline, or notes.
- Photos, complex illustrations, dense knowledge graphs, and visuals that cannot be measured reliably may remain partially image-based.
- Low-resolution inputs, missing fonts, and complex curves limit reconstruction accuracy and require rendered comparison.
- Online OCR sends the current task pages to Baidu services; use offline mode for sensitive material.

## Related Skills

- `nature-paper2ppt`: author a new research-presentation deck from paper content.
- `nature-figure`: generate or redraw publication-quality scientific figures and schematics.
- `nature-reader`: first build full reading material and figure-text alignment for a scanned paper.
