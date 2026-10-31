# `nature-paper2word` Skill

[中文说明](README.md)

Compile an academic manuscript or research report from Markdown into journal- or school-compliant Word (`.docx`): declared typography, native editable equations, three-line tables, equation numbering and cross-references, and the common citation styles — with a check before export and a reconciliation pass after it.

## What To Use It For

- Turning a Markdown draft written with `nature-writing` and its siblings into a submission-ready Word file.
- Typesetting to a school or journal specification: fonts, sizes, line spacing, margins, heading levels, three-line tables, page numbers, headers, table of contents.
- Exporting one manuscript in several layouts (thesis version, journal version).
- Extracting styles from actual paragraphs in a formatted reference paper, applying them by role to a manuscript, and checking the result.
- Papers whose equations must stay editable and numbered, rather than images or plain text.

## Typical Requests

- "Export this manuscript as the Word file our graduate school requires."
- "Typeset it to this journal template, number equations per chapter, GB/T 7714 references."
- "Give me a general version first, then the school version of the same paper."
- "Equations and tables must stay editable in Word, not images."
- "Format A.docx like B.docx and check headings, body text, captions and equations."
- "Format this manuscript using the journal's PDF, Word file, screenshots or pasted instructions; automatically recognize image-based requirements and check each rule."

## What You Need To Provide

- **The manuscript**: a Markdown file. If it is plain text, a PDF or an old `.docx`, this skill normalizes it to Markdown first and leaves the original untouched.
- **Format requirements** (optional): journal or school instructions as PDF, Word, images, screenshots, scans, text files or pasted text. The host reads the text, automatically recognizes image/scanned instructions, checks values and units, and prepares the engine settings without requiring a hand-written configuration. Without specific requirements, a built-in preset follows the manuscript's language. See [reading formatting requirements](references/format-requirements.md).
- **Reference paper** (for reference-based formatting): a formatted `.docx`. The host identifies paragraph roles; the helper extracts direct and inherited formatting from selected paragraphs and runs.
- **Material purpose**: distinguish written instructions from an example paper's appearance; combine text, table and image reading within mixed documents. Read or recognize PDF/image examples first; the paragraph-sample helper accepts DOCX only.
- **References** (optional): `.bib` entries. Without them no bibliography is generated; citations can be inserted with a reference manager after export.
- **Context**: Chinese or English, thesis or journal submission, the target journal or school.

## Outputs

- One `.docx`: equations as native Word objects; three-line tables, captions, page numbers, headers, table of contents and the bibliography produced from the requirements file.
- A pre-export check that reports contract violations by line number with the fix, plus numeric-integrity and style reconciliation results after export.
- Several layouts on request, all from the same manuscript.
- Reference-based formatting also supplies the requirements and a role-coverage check, identifying reference samples and unresolved items. See the [reference-paper workflow](references/reference-layout.md).

## Boundaries

- No custom cover pages, merged cells, multi-column text or text-wrapped figures; complete those in Word after export.
- Only equation cross-references are supported; figure and table numbers are typed into the caption.
- TOC page numbers and chapter headers are Word fields; Word asks once whether to update them.
- No PDF, HTML or LaTeX output; no slide decks or grant application forms.
- Existing DOCX files are normalized to Markdown and exported again; compare content and objects before and after conversion. Native-object preservation is not guaranteed. Export checks do not establish complete reference extraction; actual pages need separate inspection.

## Runtime and Dependencies

The export engine is the PyPI package `md-to-word-docx`. The skill's reference-layout helper reuses that package to read actual paragraphs. Confirm the command is available before use:

```bash
md-to-word --version
```

If nothing is printed, run `pip install md-to-word-docx` and check again. The full vocabulary, contract details and limits are in the manual shipped inside the package; `md-to-word --contract` prints its absolute path.

## Related Skills

- `nature-writing`: drafting the manuscript and its section-level argument (input to this one)
- `nature-polishing`: language polishing and academic phrasing (input to this one)
- `nature-citation`: searching for and exporting reference entries (RIS / ENW / Zotero RDF)
- `nature-ref-verifier`: cross-checking reference metadata
- `nature-paper2ppt`: turning the same paper into a presentation deck

## Upstream and Licence

The engine and this documentation come from the open-source project [md-to-word](https://github.com/ls-open/md-to-word) (MIT). Bundled CSL styles come from [Citation Style Language](https://github.com/citation-style-language/styles), under CC BY-SA 3.0.
