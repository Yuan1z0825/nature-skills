# Read supplied formatting requirements

Accept journal or school instructions as PDF, Word, images, screenshots, scans,
text files or text pasted into the conversation. Several sources may accompany
the manuscript and a reference paper. The host reads them and prepares the
engine's requirements file; users do not need to transcribe or preformat the rules.

## Read by content and file type

| Input | Action |
|---|---|
| PDF with selectable text | Extract text in reading order, including tables and notes; retain page numbers and inspect relevant page images. |
| Word instructions | Read paragraphs, tables, headers, footnotes and embedded images that contain rules; retain paragraph or table locations. |
| Image, screenshot or scanned PDF | Automatically use the host's available image-reading or OCR tools; recognize each relevant page or crop and compare the text with the image. |
| Pasted text or text file | Read the supplied clauses directly, preserving headings, lists, values and exceptions; identify them by clause or paragraph. |
| Mixed document or multiple files | Combine text extraction and image recognition as needed. Keep each rule linked to its source location. |

Distinguish a document stating requirements from a template or example paper.
For example, a Word paragraph saying "body text: 12 pt, double-spaced" defines
those requirements even if that instruction paragraph itself uses 10 pt text.
Use [reference-layout](reference-layout.md) when actual sample layout must also
be learned. Do not pass a PDF or image to the DOCX-only sample helper.

## Extract and reconcile the rules

Record the journal or school, article type, submission stage and source version
when supplied. Extract page size, margins, columns, fonts, sizes, line spacing,
indentation, headings, captions, tables, equations, numbering, references and
running matter. Preserve exceptions and the difference between "must" and
"recommended". Check recognized digits, decimal points, units, ranges, negation
and table row/column associations against the source image. Resolve unclear
text from the surrounding source; identify any remaining unreadable clause.

Explicit journal instructions take precedence over an example paper's appearance
for journal compliance. Record any user-requested departure. Resolve conflicting
instructions by their stated article type, stage and version; if a material
conflict remains, ask about that clause and continue extracting the other rules.

## Build, apply and check

Create a compact list of requirement, source location, engine setting and check
result. Translate supported properties into `format.txt` using the vocabulary
from `md-to-word --contract`; explicit instructions do not need a paragraph map.
Mark any preset values used for missing details as defaults. Retain requirements
outside the engine's scope, such as word limits or unsupported layouts, for a
separate content or page check; do not count them as applied settings.

Use the existing normalization and export workflow. After export, check the
original clauses against the output as well as the generated settings. Inspect
rendered pages for the requirements that need visual verification. Deliver the
editable Word file with concise applied-rule and unresolved-item results.
