# `nature-writing` Skill

[中文说明](README.md)

## What It Does

- Drafts, restructures, or plans Nature-style manuscript sections from claims, results, figures, notes, or Chinese drafts.

## When to Use It

- You need to write an abstract, introduction, related work, methods, experiments, discussion, conclusion, or title.
- You need to rebuild the argument rather than only polish finished prose.
- You have results and figures but need a coherent manuscript narrative.

## Copy-Paste Prompts

- `Using these results and figures, draft a Nature-style abstract and introduction.`
- `Rebuild the argument of this introduction around the main scientific gap.`
- `Write a discussion section that links these findings to mechanism, limitation, and implication.`

## Required Inputs

- Claims, results, figure summaries, methods, draft paragraphs, target journal, and audience.
- Evidence constraints and terminology that must be preserved.

## Expected Outputs

- Draft manuscript sections.
- Argument outline and section plan.
- Revision suggestions for evidence flow and narrative logic.

## Dependencies / API Keys / Local Environment

- No special runtime dependency for text-only drafting.

## FAQ

- **How is this different from polishing?** `nature-writing` builds or restructures the argument; `nature-polishing` improves already drafted prose.
- **Can it write from vague ideas?** It can outline questions and missing evidence, but strong drafting needs concrete claims and results.

## Related Skills

- [`nature-polishing`](../nature-polishing/README_EN.md)
- [`nature-reviewer`](../nature-reviewer/README_EN.md)
- [`nature-citation`](../nature-citation/README_EN.md)
