# `nature-paper2word` Skill

[中文说明](README.md)

Compile an academic manuscript or research report from Markdown into journal- or school-compliant Word (`.docx`): declared typography, native editable equations, three-line tables, equation numbering and cross-references, and the common citation styles — with a check before export and a reconciliation pass after it.

## What To Use It For

- Turning a Markdown draft written with `nature-writing` and its siblings into a submission-ready Word file.
- Typesetting to a school or journal specification: fonts, sizes, line spacing, margins, heading levels, three-line tables, page numbers, headers, table of contents.
- Exporting one manuscript in several layouts (thesis version, journal version).
- Papers whose equations must stay editable and numbered, rather than images or plain text.

## Typical Requests

- "Export this manuscript as the Word file our graduate school requires."
- "Typeset it to this journal template, number equations per chapter, GB/T 7714 references."
- "Give me a general version first, then the school version of the same paper."
- "Equations and tables must stay editable in Word, not images."

## What You Need To Provide

- **The manuscript**: a Markdown file. If it is plain text, a PDF or an old `.docx`, this skill normalizes it to Markdown first and leaves the original untouched.
- **Format requirements** (optional): a text file, one style per line. Without it, a built-in preset is chosen by the manuscript's language.
- **References** (optional): `.bib` entries. Without them no bibliography is generated; citations can be inserted with a reference manager after export.
- **Context**: Chinese or English, thesis or journal submission, the target journal or school.

## Outputs

- One `.docx`: equations as native Word objects; three-line tables, captions, page numbers, headers, table of contents and the bibliography produced from the requirements file.
- A pre-export check that reports contract violations by line number with the fix, plus numeric-integrity and style reconciliation results after export.
- Several layouts on request, all from the same manuscript.

## Boundaries

- No custom cover pages, merged cells, multi-column text or text-wrapped figures; complete those in Word after export.
- Only equation cross-references are supported; figure and table numbers are typed into the caption.
- TOC page numbers and chapter headers are Word fields; Word asks once whether to update them.
- No PDF, HTML or LaTeX output; no slide decks or grant application forms.

## Runtime and Dependencies

This skill is documentation only. The engine is the PyPI package `md-to-word-docx`; install it once, and the skill files never change with the engine version. Confirm the command is available before use:

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
