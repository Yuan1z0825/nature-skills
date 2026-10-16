# nature-paper-trans

[中文说明](README.md)

Translate a full English research-paper PDF or selected pages into a Simplified Chinese, image-based PDF while preserving each source page's size, orientation, and layout as closely as possible. The only deliverable is the Chinese PDF.

![nature-paper-trans · Paper PDF translation](assets/banner.png)

## What To Use It For

- Translate a full paper or a consecutive or nonconsecutive selection of pages.
- Read a Chinese version that retains the main visual layout of the source.
- Apply supplied terminology or confirmed translations; later update only pages explicitly selected by the user.

## Typical Requests

> Use $nature-paper-trans to translate this entire English paper into a Chinese PDF.

> Use $nature-paper-trans to translate pages 1–3 and 5, following the terminology list I supplied.

> Use $nature-paper-trans to update original PDF page 3 in the previous translation, focusing on the right column's text footprint, and merge a new version.

## What You Need To Provide

An English research-paper PDF and, optionally, page ranges, a glossary, a do-not-translate list, or confirmed translations. Page numbers refer to the **physical PDF page order**, starting at 1, rather than printed page numbers. With no range specified, the whole PDF is processed.

The source PDF must be clear, readable, and unencrypted; an extractable text layer is not required. To update an existing result, provide the original task materials and explicitly select source page numbers and update requirements.

## Output

Deliver only one Chinese PDF: image-based, in source-page order. By default, preserve each source page's size, orientation, and aspect ratio, centering the translated image proportionally within its corresponding page. Convert all pages to A4 only when the user explicitly requests it. Do not generate or deliver a page-review Markdown file.

## Workflow

**Split the source PDF → generate each translated page once → compare and record review → merge in source order.**

All pages use one prompt. The image model reads, translates, and adapts the layout. Each page gets one generation attempt per user task, with no automatic retry after failure or an unknown outcome. Compare each generated page with its source for body coverage, figures, equations, numbers and units, and record actual observations in the task ledger before assembly. Review does not grant another generation attempt or trigger automatic repair. No review Markdown is delivered. Disclose source page numbers with recorded issues or uncertainty beside the PDF link; the user may explicitly request selected page updates.

Up to 10 requests may be outstanding; actual parallel execution and timing depend on the host tool and service. Interrupted tasks can resume using saved pages. A later, explicit user page selection starts a new update task.

## Runtime and Dependencies

Requires Codex with the built-in `image_gen` tool, Python 3.9+, PyMuPDF, and Pillow. The helper supports macOS, Linux, WSL2, and native Windows; use PowerShell on native Windows and Bash in WSL2. See [requirements.txt](requirements.txt).

In Windows PowerShell, replace `$PYTHON` in examples with `python` or `py -3`, and quote Windows paths. The workflow and file formats stay the same; native Windows needs no extra POSIX file-lock package.

The Python helper handles source-page rendering, attempt/review records, image storage, and PDF assembly. It does not call an image-generation service or judge translation accuracy. `--pdf-only` omits the review sidecar while still requiring review records for newly generated images. This skill runs independently of other Nature Skills skills.

## Boundaries

- Outputs have no OCR text layer and are neither editable Word documents nor searchable-text PDFs.
- Pixel-perfect reproduction and word-by-word accuracy are not guaranteed. Generated pages may contain translation errors, omissions, changed equations or figures, or layout differences. Basic comparison is not a full textual audit; verify critical data and conclusions against the source.
- Once missing pages are confirmed, a partial PDF identifies the source pages actually included. If no usable pages exist, no PDF is delivered.
- Failed page updates retain existing usable results. Source PDFs and existing deliverables are not overwritten.

See [SKILL.md](SKILL.md) for execution rules and the [shared prompt](references/image-translation-prompt.md) for translation and layout requirements.

## Related Skills

- [nature-reader](https://github.com/Yuan1z0825/nature-skills/tree/main/skills/nature-reader): for full-paper Markdown, bilingual comparison, and source anchors.
- [nature-paper2ppt](https://github.com/Yuan1z0825/nature-skills/tree/main/skills/nature-paper2ppt): for Chinese paper-presentation PPTX decks.
