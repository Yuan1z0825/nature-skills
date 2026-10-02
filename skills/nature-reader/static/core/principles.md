# Core principles (reader)

Use this skill to turn a research paper into a complete Markdown reading artifact. The default output should read like a bilingual paper companion, not a summary dump:

- keep the extractable prose, paragraph structure, and section flow
- show original text and Chinese translation together at block level
- extract figures and tables as assets and place them at the first substantive mention or interpretation point
- render equations as Markdown math with stable equation anchors; never expose bare LaTeX commands as ordinary prose
- keep captions attached to figures/tables with English caption text and Chinese caption translation
- preserve stable page and block anchors for traceability
- write a complete `paper.md` by default, plus `source_map.json`, `translation_notes.md`, and `assets/`

This skill is for papers, preprints, and conference proceedings across disciplines. It is not limited to Nature-family journals. Honor an explicit request for a summary, excerpt, or source-linked answer at that scope; no separate summarization skill is required. Citation-only searches belong to the appropriate citation workflow.

## Non-negotiable defaults

When the user requests a reader, `中英文对照`, `原文对照`, `全文翻译`, or invokes `nature-reader` without a narrower deliverable, produce a paragraph-level bilingual reader by default. An explicit question, summary, or excerpt request takes precedence; do not expand it into full-paper processing.

Do not replace the reader with:

- a Chinese-only summary
- a paper review without original/translation alignment
- figure captions without figure/table crops
- a list of key points detached from source locations
- only the abstract, introduction, or selected highlights

If constraints prevent full processing, still create a draft reader and clearly label missing pages, missing figures/tables, untranslated blocks, or low-confidence OCR/crops in `translation_notes.md`.

## Core principle

Translate for meaning, not for style. Preserve the paper's structure, evidence, hedging, terminology, equations, units, and citation markers. Keep the output in prose paragraphs unless the source itself is tabular or list-like. Do not collapse the paper into keyword bullets or slide-style notes.

Equations are first-class source blocks. Give every display equation an `E001`, `E002`, ... anchor and put valid inline math inside `$...$` or display math inside `$$...$$`. If the expression cannot be transcribed confidently, crop the original formula into `assets/equations/`, show that image in `paper.md`, and label any best-effort LaTeX as low confidence. Never guess missing symbols or leave commands such as `\\frac` and `\\sum` outside a math delimiter.

The reading file should help a reader move between:

- original text
- translated text
- source location
- figure or table evidence

Each substantive source block should have a stable anchor and a visible bilingual pair:

```markdown
<a id="S001"></a>
**Source:** p.1 S001

**Original:** [source paragraph]

**中文:** [faithful Chinese translation]
```

## Copyright caution

For copyrighted publisher PDFs, keep chat responses short and point to the local artifact. In local `paper.md`, include the bilingual reader only for the user-provided source file or clearly lawful open-access content; avoid reproducing large copyrighted text directly in chat.

## Quality bar

Good output feels like a paper reader, not a machine translation dump. It should let a reader:

- read the paper in two languages
- see where a claim came from
- inspect the nearby figure or table
- read equations directly in the Markdown viewer or inspect the original crop when transcription is uncertain
- move through a complete Markdown file without losing source traceability
