# `nature-proposal-writer` Skill

[中文说明](README.md)

`nature-proposal-writer` is a proposal-first research-writing workflow for turning topics, ideas, drafts, or sections into academic text with argument structure, evidence boundaries, and quality gates.

## What To Use It For

- Build a research canon, problem chain, and section contracts from a rough research direction.
- Revise existing paragraphs so argument order, contribution boundaries, and evidence support are clearer.
- Expand existing drafts into proposals, manuscript sections, review frameworks, or project narratives.
- Run content, language, citation, and formatting QA after drafting.

## Three Modes

| Mode | Input | Best For |
|------|-------|----------|
| `compose` | Topic, direction, rough idea | Build argument and sections from scratch |
| `revise` | Existing paragraph or section | Gap analysis, reordering, and polishing |
| `hybrid` | Draft plus expansion target | Preserve existing text while filling structure |

## Typical Requests

- "I have a grant title; first break down the scientific questions and research content, do not write prose yet."
- "This introduction is scattered; rebuild it with the proposal-first workflow."
- "Expand this draft into a proposal framework and mark evidence gaps."

## What You Need To Provide

- Research topic, target reader, submission/application type, and available materials.
- Confirmed facts, data, figures, references, or wording that must not change.
- Desired length, language, and file format.

## Outputs

- Argument architecture, section contracts, and writing order.
- Ready-to-paste draft text or revised text.
- QA results: content gaps, language risks, citation/numbering issues, and facts that need author confirmation.

## Boundaries

- The skill does not invent experimental results, references, collaboration basis, or feasibility evidence.
- Missing facts are marked as `AUTHOR_INPUT_NEEDED` rather than hidden under fluent prose.
- For sentence-level English polishing only, use `nature-polishing`.

## Complete Reference Set

The skill includes 20 references that are loaded on demand, covering:

- the complete `compose`, `revise`, and `hybrid` workflows;
- foundation files, project state, scope control, and writing within an approved proposal;
- dynamic expert dispatch, scoring, stopping rules, and automated validation;
- Chinese research-writing cleanup, review architecture, and critical synthesis;
- citation renumbering, revision handoffs, export and archival workflows, and a completed example.

See the [reference index and loading conditions](SKILL.md#reference-文件索引) in `SKILL.md`. Load only the references required by the current task rather than injecting the entire set into context.

## Related Skills

- `nature-writing`: Nature-style manuscript-section drafting.
- `nature-polishing`: English manuscript polishing, restructuring, and translation.
- `nsfc-proposal`: dedicated National Natural Science Foundation of China proposal writing.
