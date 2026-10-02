# `nature-reviewer` Skill

[中文说明](README.md)

`nature-reviewer` simulates Nature-style pre-submission review from the reviewer perspective, helping authors find risks in novelty, significance, technical soundness, and reader value before submission.

## What To Use It For

- Stress-test a manuscript, abstract, figure set, or result storyline before submission.
- Evaluate originality, scientific importance, interdisciplinary readership, technical soundness, and readability using Nature-style review dimensions.
- Generate three reviewer reports in mutually blind isolated contexts, then create a separate cross-review synthesis only after every report is frozen.
- Mark unsupported claims, technical defects, evidence-chain breaks, and barriers for non-specialist readers.
- Separate comments into `Major Concerns` and `Minor Comments`, marking Major issues that block the central case as `Blocking Yes`.
- Keep severe criticism direct, professional, and evidence-grounded; keep minor comments specific and actionable without inventing issues to fill a quota.
- Avoid dash punctuation and colons throughout the prose when a sentence boundary, comma, semicolon, parentheses, or a short label on a new line is clearer; retain necessary source punctuation and hyphens in stable IDs and compound terms.
- Use an internal 12-axis technical checklist and bind each substantive concern to a claim pointer and verifiable evidence location.
- Cross-check terminology, units, numeric precision, Methods counts, and table support within the manuscript, separating language issues from substantive contradictions that weaken credibility.
- After all reviewer reports are frozen, run a separate forensic consistency audit of arithmetic identities, metric bounds, aggregation levels, prose-table contradictions, duplicate rows, dispersion anomalies, provenance, and reproduction gates. Audit findings are not fed back to reviewers and frozen reports are not edited.
- Do not coordinate or rewrite reviews to reduce duplication; treat an issue as consensus only when at least two reviewers raise it independently in the post-review synthesis.
- Identify which readers would care about the work and why.

## Typical Requests

- "Review this introduction and Figure 1 like a Nature reviewer."
- "Before submission, find the technical issues reviewers are most likely to attack."
- "Give me three reviewer reports and one synthesis, not a rebuttal."

## What You Need To Provide

- Manuscript, abstract, key sections, figures, legends, or author notes.
- Target journal, field, and the review risks you are most worried about.
- Existing supplementary experiments or constraints on adding new experiments.

## Outputs

- Three peer-review style reports.
- Cross-review synthesis: consensus problems, divergent emphases, and editor-level risks.
- Traceable concerns with stable IDs, claim pointers, evidence pointers, and resolution tests.
- Tiered Major/Minor comments, blocking risks, and a deduplicated minor-revision checklist.
- List of experiments, analyses, narrative changes, or figure evidence that must be strengthened.
- Explicit labels for judgments that cannot be made from the supplied evidence.

## Boundaries

- The skill does not invent specific reviewer identities, expert personas, or editorial decisions.
- Reviewers cannot read, cite, agree with, or respond to one another; synthesis begins only after all independent reports are locked.
- It makes conservative simulations only from the provided material and the skill's official review rules.
- For writing responses to real reviewer comments, use `nature-response`.

## Related Skills

- `nature-response`: turn real reviewer comments into a response package.
- `nature-writing`: rebuild manuscript narrative based on review risks.
- `nature-statistics`: deeply audit statistical design and reporting.
