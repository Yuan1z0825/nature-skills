---
name: nature-paper2word
description: "Compile an academic Markdown manuscript into a journal- or school-compliant Word (.docx): declared typography, native OMML equations, three-line tables, cross-references, per-section page numbers, CSL bibliographies (GB/T 7714, APA, Nature, IEEE), and pre/post-export quality gates. 把学术论文的 Markdown 稿件导出为符合期刊或学位论文规范的 Word：摘要、公式编号、三线表、题注、交叉引用、目录域、参考文献。Use when the user wants a submission-ready .docx — 论文转 Word、学位论文排版、期刊投稿排版、prepare submission docx — or a readable copy of a manuscript. Not for PDF, HTML or LaTeX output, and not for slide decks or grant forms."
license: MIT
---

# Markdown → compliant Word

This file is the router. The engine is deterministic: the same manuscript and the same format
requirements always produce a byte-identical `.docx`. Do not substitute a hand-written
python-docx script; run the installed pipeline.

**Before the first export in a session, confirm the engine is available**: `md-to-word --version`
must print a version. This skill ships documentation only; if the command is missing, install it
with `pip install md-to-word-docx`, then run the check again.

**The full vocabulary lives in the manual inside the package**, not here. `md-to-word --contract`
prints its absolute path (Chinese or English, following the manuscript). Everything below is order
of work; every spelling is looked up in the manual.

## 1. Decide the scenario first

| Scenario | What the user says | What to do |
|---|---|---|
| Journal or school compliance | "format it for Nature / my university" | Get a target `.docx` template or a written spec, then build a requirements file. |
| Existing requirements | "use our lab's spec file" | Pass it with `-r`. |
| Baseline export (no explicit spec) | "turn this into a Word file" | Normalize the manuscript to the contract, then export with the built-in preset. The preset is a complete, valid format, not a provisional default. |

State the chosen preset or requirements path in one line, then proceed. Without `-r` the only file
picked up is one named exactly **`format.txt`** beside the manuscript; no other `.txt` is guessed at
(if one is there, the run names it in a reminder). With no `format.txt`, the preset follows the
**manuscript's language**: `zh-academic` for Chinese, `en-nature` for everything else. The run reports
which one it used.

No path accepts arbitrary Markdown and returns a finished document: a preset supplies formatting,
not missing structure. When the manuscript violates the contract, pre-flight stops with a line
number rather than emitting a document that looks acceptable while its formatting was never mapped.

## 2. Bring the manuscript to the input contract

The source may be pasted text, `.txt`, `.md`, an old `.docx`, or a PDF. Normalize it to Markdown
first; never edit the user's original file in place.

- **Headings**: `#`, `##`, `###`, consecutive and unskipped; a heading that carries its own number
  (`1.`, `2.1`) needs as many `#` as its number has levels.
- **Paragraph styles**: a line starting with `%% ` sets that paragraph's style —
  `%% Abstract …`, `%% Table Caption **Table 1** …`, `%% Image Caption Figure 1 …`.
  One line is one paragraph, ended by a blank line, with no closing fence. Style names come from a
  closed list (manual §3.4) in either language; heading levels are set by `#` only.
- **Title, author, abstract, keywords** are style lines in the body, never YAML — their position on
  the page is the author's decision, and YAML has no position. Pre-flight blocks those keys with the
  exact line to write instead.
- **Paragraphs**: one line is one paragraph; consecutive lines are never joined, so a file of short
  one-sentence paragraphs is already correct. For a break *inside* one paragraph (an address, verse,
  a long title), end the line with a backslash or two spaces — it becomes a line break within the same
  paragraph. Suspected wrapping is reported as a grouped warning with the line numbers.
- **YAML holds only position-independent configuration**: `bibliography:`, `csl:`, `crossref:`,
  `link-citations:`.
- **Equations**: `$$...$$ {#eq-name}` on its own line, referenced as `@eq-name`. Chinese manuscripts
  get 「式/图/表」 prefixes and （1）numbering, English ones get Equation/Figure/Table and (1). Add
  `crossref: chapters: true` for per-chapter numbering. `\tag{}` is blocked.
- **Citations**: `[@key]` parenthetical, `@key` narrative, from `bibliography:` + `csl:`. A `.bib` is
  mandatory once the manuscript cites: handwritten reference lists are not supported, and `[@key]`
  without `bibliography:` would be printed literally.
- **Figures and tables**: `![](path/img.png){width=13cm}` with the caption in its own
  `%% Image Caption` / `%% 图片题注` paragraph; table caption above, note below. Do not put
  `{#fig-...}` labels on images. Column widths follow the separator row's dash lengths.
- **Block markers** (three, each on its own line with blank lines around): `{{< pagebreak >}}`,
  `{{< toc >}}`, `{{< section page_number=lowerRoman start=1 >}}` (Chinese parameters `页码=` `起始=`
  also work). The section marker closes *the section above it*; never add a page break next to it.
- **Unsupported Markdown is blocked with a replacement**, never printed literally: HTML tags, `---`
  rules, `====` headings, definition lists, `- [ ]` boxes, tables without outer pipes, nested block
  quotes, full-width `％％`, four-space code blocks, a second paragraph inside a
  list item, `==highlight==`, `[text]{.class}` (except `.underline`), `\(...\)` inline math, and a
  percentage image width (`{width=60%}` — write an absolute length).

## 3. Choose or build the format requirements

0. **Starting from nothing** — `md-to-word init` writes a complete preset copy plus a one-page
   manuscript that exports as-is.
1. **Built-in preset** — `zh-academic` or `en-nature`. Use as-is when the user gave no detailed spec.
2. **Copy and edit a preset** — change only the lines the user mentioned. Field order is fixed:
   font, size, bold, italic, alignment, line spacing, space before, space after, indent. Every style
   line must be complete; missing fields are errors.
3. **Reverse-engineer a target `.docx`** — `md-to-word-template target.docx -o format.txt`, then
   review the "to confirm" list at the end of the draft.

Each property has exactly one accepted spelling (two in total: the canonical Chinese and English
forms); anything else is a hard error with a line number. Full table: manual §3.1. Style names:
§3.4. Presets are the reference examples — `md-to-word --contract` prints their paths.

Throughout this file, `format.txt` means *the format requirements file* — any path works, `-r` takes
it.

Citation style comes from `csl:` with a bundled file name (manual §7) or a path to the user's own
CSL. Without `csl:`, Chinese manuscripts get GB/T 7714 numeric, others APA 7th. A user-supplied CSL
is normalized on export so that one requirements file always produces one layout.

## 4. Export

Run the installed command from the manuscript's directory:

```bash
md-to-word manuscript.md -o manuscript.docx
md-to-word manuscript.md -r format.txt -o manuscript.docx
md-to-word --contract          # contract + paths to the manual and presets
```

The pipeline runs: pre-flight validation → style template generation → manuscript model → OOXML
writing → number-integrity check → line-by-line audit against the requirements file.

## 5. How to read the gates

Two levels, split by "would the mistake be visible afterwards":

- **Blocking** — silently wrong later: dropped content, syntax printed literally, formatting never
  mapped, a title in YAML, a caption inside an image's brackets. Fix the reported line; do not reach
  for `--no-check`, which turns off the blocking gates too.
- **Warning** — visible but non-compliant: an image wider than the text block (it gets clamped), a
  caption far from its figure, a skipped heading level, a page break after a section marker,
  suspected line wrapping. Warnings of one kind arrive as a single line (up to eight line numbers,
  then a count).

Add `--json` when the result has to be read back programmatically: stdout then carries one JSON
object — `ok`, `returncode`, `input`, `output`, `pdf`, `lang`, `messages`, `errors` — with progress
and reminders on stderr. The keys are fixed; the sentences inside them follow the manuscript's
language, and the reminders are in `messages`.

Exit codes: `0` every gate passed; `1` manuscript, gate or dependency problem; `2` a usage error
(bad flags or a missing argument); `3` the `.docx` was written but the optional `--pdf` proof was
skipped (non-macOS). Messages follow the manuscript's language. Add `--verbose` when a format does
not seem to take effect.

## 6. Verify before delivery

- Confirm the `.docx` exists and the command exited `0`.
- Report the applied preset or requirements file, the citation style, and anything the run warned
  about.
- Say plainly that the layout still needs a manual check in Word. The engine verifies text and
  structure; row heights, column widths and where equations and captions settle are only visible in
  a real renderer.
- When the document has a TOC, `{style-title}` headers or per-section page numbers, run once with
  `--pdf` (macOS with Word) — that is the only way fields are expanded — and spot-check the first
  page, the widest table, an equation-heavy page and the references.

## 7. Boundaries

- No custom cover pages, merged cells, multi-column text, inline text colour, or text-wrapped
  figures. Export the body, then complete those in Word.
- Only equation cross-references are supported (`{#eq-x}` + `@eq-x`); figure and table numbers are
  typed into the caption.
- Sum and integral limits stay on the right of the symbol in numbered equations (Word stacks limits
  only in display math). Content and symbols are correct; only the arrangement differs.
- TOC page numbers and chapter headers are Word fields; Word asks once whether to update them.
Full statements: manual §6 (limits) and §8 (symptom → fix).

## 8. Related skills

This skill compiles the manuscript; these cover the steps around it. Hand off rather than
re-implement:

| Skill | What it covers |
|---|---|
| `nature-writing` | Drafting the manuscript and its section-level argument (input to this one) |
| `nature-polishing` | Language polishing and academic phrasing (input to this one) |
| `nature-citation` | Searching for and exporting reference entries (RIS / ENW / Zotero RDF); export BibTeX from the reference manager for the `.bib` this skill consumes |
| `nature-ref-verifier` | Cross-checking reference metadata before submission |
| `nature-paper2ppt` | Turning the same manuscript into a presentation deck |

Upstream engine, the general-purpose pip package, and the changelog:
[md-to-word](https://github.com/ls-open/md-to-word).
