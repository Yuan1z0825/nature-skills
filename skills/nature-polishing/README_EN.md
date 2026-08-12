# `nature-polishing` Skill

[中文说明](README.md)

`nature-polishing` polishes, restructures, or translates academic manuscript text into concise Nature-leaning English while preserving author meaning, evidence boundaries, and citation intent.

## What To Use It For

- Translate Chinese academic paragraphs into submission-ready English.
- Shorten long sentences and improve argument order and paragraph movement.
- Adjust abstracts, introductions, results, discussions, or titles using Nature / Nature Communications / Nature Machine Intelligence article patterns.
- Route NMI separately to check its 3,500-word main text, 150-word abstract, six-display budget, code-review duties, and substantial conference-paper extension without importing flagship Nature numbers.
- Distinguish research-paper and methods-paper writing priorities.
- Check AI-like phrasing, exaggerated claims, excessive causal language, and unnatural collocations.
- Sweep full or repeatedly revised manuscripts for terminology, unit, numeric-precision, and internal-claim drift.

## Method Sources

- Writing strategy: hourglass structure, reader workflow, and section roles from academic-writing course notes.
- Published article patterns: section moves from selected Nature and Nature Communications papers.
- Phrase support: expression families from Academic Phrasebank.

## Typical Requests

- "Translate this Chinese Results paragraph into Nature-style English, keeping it conservative."
- "Polish this abstract without changing facts or citation intent."
- "This introduction sounds too AI-written; rebuild its logic and language."

## What You Need To Provide

- Source text, target section, paper type, and terms that must be preserved.
- Facts, data, citations, and specialized expressions that must not change.
- Desired output: rewritten text only, or rewritten text with change notes and risk flags.

## Outputs

- Ready-to-paste English rewrite or Chinese-English paired version.
- Key change notes: logic reordering, tone tightening, terminology alignment, and claim boundaries.
- A manuscript-wide consistency risk list, with mechanical warnings inspected in context before revision.
- Facts or citation intent that require author confirmation.

## Boundaries

- The skill does not add results, mechanisms, statistical significance, or citations not provided by the author.
- It does not exaggerate novelty, causality, or generality to sound more like Nature.
- For building a manuscript section from scratch, use `nature-writing` first.

## Related Skills

- `nature-writing`: section-level drafting and argument rebuilding.
- `nature-response`: reviewer response and cover-letter language.
- `nature-statistics`: statistical text, figure legends, and statistical reviewer responses.
