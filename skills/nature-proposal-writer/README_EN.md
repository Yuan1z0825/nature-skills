# `nature-proposal-writer` Skill

[中文说明](README.md)

## What It Does

- A proposal-first research-writing state machine that establishes evidence, argument, and section contracts before drafting or reviewing proposal text.

## When to Use It

- You need to draft a proposal, opening report, research plan, or structured research-writing document.
- You want a QA pass that checks evidence, argument, feasibility, and section logic.
- You need to move from rough notes to a coherent proposal skeleton.

## Copy-Paste Prompts

- `Build a proposal outline from these notes and identify missing evidence.`
- `Review this research plan for argument gaps, feasibility, and section logic.`
- `Draft the opening-report background and research objectives from these materials.`

## Required Inputs

- Research topic, background notes, preliminary evidence, target format, constraints, and review criteria.
- Optional existing draft for QA or rewrite.

## Expected Outputs

- Proposal outline, section contract, and evidence map.
- Drafted or revised proposal sections.
- QA findings and next-step checklist.

## Dependencies / API Keys / Local Environment

- May integrate with Hermes or Claude Code workflows depending on the local setup.
- No special dependency for plain text drafting.

## FAQ

- **Is this only for grant proposals?** No. It also fits opening reports, research plans, and proposal-like academic documents.
- **Does it write before checking evidence?** The intended workflow is evidence and argument first, drafting second.

## Related Skills

- [`nature-writing`](../nature-writing/README_EN.md)
- [`nature-polishing`](../nature-polishing/README_EN.md)
- [`nature-reviewer`](../nature-reviewer/README_EN.md)
