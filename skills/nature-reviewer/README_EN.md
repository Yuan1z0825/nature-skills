# `nature-reviewer` Skill

[中文说明](README.md)

## What It Does

- Simulates Nature-style peer review from the reviewer perspective and returns multiple reviewer reports plus a synthesis.

## When to Use It

- You want a pre-submission critique before journal submission.
- You need novelty, significance, technical soundness, evidence, and presentation assessed from reviewer perspectives.
- You want likely reviewer objections and revision priorities.

## Copy-Paste Prompts

- `Evaluate this manuscript from a Nature reviewer perspective and produce three reviewer reports.`
- `Give me a pre-submission review focused on novelty, significance, and technical soundness.`
- `Identify the strongest reasons this paper could be rejected and how to fix them.`

## Required Inputs

- Manuscript, abstract, figures, methods, results, or paper draft.
- Optional target journal and field context.

## Expected Outputs

- Three reviewer-style reports.
- Synthesis of major risks and recommendation.
- Prioritized revision checklist.

## Dependencies / API Keys / Local Environment

- No special runtime dependency for text-only review.
- Literature comparison may require search access if novelty claims need verification.

## FAQ

- **Is this a rebuttal skill?** No. It critiques from the reviewer perspective. Use `nature-response` for rebuttal and revision replies.
- **Can it replace real peer review?** No. It is a pre-submission stress test.

## Related Skills

- [`nature-response`](../nature-response/README_EN.md)
- [`nature-writing`](../nature-writing/README_EN.md)
- [`nature-polishing`](../nature-polishing/README_EN.md)
