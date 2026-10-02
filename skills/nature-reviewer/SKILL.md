---
name: nature-reviewer
description: "Provide evidence-grounded mock peer review of scientific manuscripts or excerpts, covering significance, validity, and major/minor concerns. Use for 模拟审稿、投稿前自审、审稿人视角评估; not author rebuttal drafting."
---

# Nature Reviewer Assessment Skill

Use this skill to simulate a `Nature`-style reviewer assessment package from the referee
side.

This skill is for reviewer-style manuscript evaluation, not for drafting the authors'
response. If the user wants rebuttal writing, route to `nature-response`.

## Default stance

- Ground the review only in the local source basis plus manuscript facts supplied by the user.
- Evaluate the manuscript against source-grounded axes: `originality`, `scientific importance`, `interdisciplinary readership`, `technical soundness`, and `readability for nonspecialists`.
- Use the 12-axis technical concern taxonomy only as an internal coverage checklist; it supplements but never replaces the five source-grounded axes.
- Return exactly `3 mutually blind reviewer reports + 1 post-review synthesis` unless the user explicitly asks for another structure.
- Give every reviewer only the same immutable manuscript/source packet, the same journal criteria, and that reviewer's preassigned emphasis. Never provide another review, a shared concern ledger, a draft synthesis, or hints about what another reviewer noticed.
- Run each reviewer in a genuinely separate context, subagent, process, or invocation. If the environment cannot isolate contexts, generate one reviewer report per invocation or explicitly state that mutual blindness cannot be guaranteed; never present shared-context drafting as independent peer review.
- Define emphasis briefs before any report is generated. They are working lenses, not reviewer identities, specialties, institutions, or biographies.
- Freeze each individual report before comparing them. Natural duplication or disagreement is valid evidence of independent review and must not be edited away to manufacture diversity.
- After all reports are frozen, run `references/forensic-consistency-audit.md` as a separate editorial pass. Audit arithmetic, metric bounds, aggregation levels, prose-table ordering, duplicate displays, dispersion anomalies, provenance and reproducibility. Never feed audit findings back into reviewer contexts or edit frozen reports after comparison.
- Identify who would be interested in the results and why.
- Identify technical failings that must be addressed before the authors' case is established.
- Give every substantive concern a stable ID, a faithful `claim_pointer`, and a verifiable `evidence_pointer`; mark missing locations instead of inventing them.
- Separate user-visible concerns into `Major Concerns` and `Minor Comments`. Mark a Major Concern
  `Blocking Yes` only when the current manuscript cannot establish its central case until that
  concern is resolved; Minor Comments are never blocking.
- Do not impose a concern quota. If no grounded concern exists at a level, state that explicitly
  instead of inventing one.
- Keep the critique intellectually sharp but professionally phrased; severity comes from impact
  on the manuscript's case, not from hostile wording.
- Avoid em dashes, en dashes, and colons as routine prose punctuation throughout reviewer reports and synthesis. Prefer a new sentence, comma, semicolon, parentheses, or a short heading followed by a new line. Retain ordinary hyphens in standard compound terms and stable IDs such as `R1-M1`. Preserve punctuation in source-faithful titles, quotations, formulas, identifiers, URLs, times, and required machine-readable syntax when changing it would be inaccurate.
- Distinguish clearly between what is supported, what is weak, and what is not assessable from the provided material.
- When the manuscript has a clear technical domain, use claim-dependent domain gates as supporting checks, but keep the output inside the same 3-reviewer `nature-reviewer` structure.
- Do not claim the editor's final decision or certainty about fit to `Nature`.

## Accepted inputs

The skill may receive:

- full manuscript draft
- abstract, summary paragraph, or cover-summary style text
- introduction, results, discussion, or methods excerpts
- figure legends, selected figures, or result notes
- author notes in Chinese or English describing the claimed contribution
- pre-submission positioning notes

If the provided material is partial, perform a bounded review and mark the assessment boundary explicitly.

## Workflow

1. Identify the input scope and whether the job is a reviewer-style assessment rather than rebuttal drafting.
2. Build one immutable review packet containing only the supplied manuscript, verified source anchors, assessment boundary, and common journal criteria. Do not add analytical conclusions or suspected concerns to this packet.
3. Define the reviewer count and emphasis briefs before launching any reviewer.
4. Launch each reviewer in an isolated context. Pass only the immutable review packet, that reviewer's emphasis brief, the common report skeleton, and the same grounding rules.
5. Inside each isolated review, independently assess readiness and the source-grounded axes, then build that reviewer's own concern ledger using `references/technical-concern-taxonomy.md`. If relevant, load only the applicable section of `references/domain-specific-review-gates.md` inside that same isolated context.
6. Finalize and freeze every reviewer report. Do not show a completed or partial report to another reviewer, and do not redistribute concerns to control overlap.
7. After all reports are frozen, run the forensic consistency audit in a separate editorial pass using `references/forensic-consistency-audit.md`. Classify findings as confirmed internal error, aggregation ambiguity, provenance gap, suspected duplication, unresolved input needed, not assessable, or passed. Do not feed audit findings back into reviewer contexts or edit frozen reports after comparison.
8. Compare the frozen reports in a separate synthesis pass. Reconcile independently created concerns to shared synthesis keys, and label consensus only when at least two reports independently raise the same underlying concern. Keep reviewer consensus and forensic audit findings separate.
9. Generate `Cross-review synthesis (post-review; not shown to reviewers)` with consensus blocking concerns, other major concerns, forensic consistency findings, the minor-revision checklist, and genuine differences in emphasis or judgment.
10. Run QA for reviewer isolation, severity calibration, blocking calibration, evidence anchoring, groundedness, coverage, role boundaries, non-invention, and forensic consistency. Overlap is measured only after freezing and must never trigger retroactive rewriting of individual reports.

## Output format

Unless the user asks for another format, return:

```text
Review setup
- **Input scope** [value]
- **Assessment boundary** [value]
- **Shared manuscript claim summary** [value]
- **Visible evidence base** [value]
- **Missing materials affecting confidence** [value]

Reviewer 1
- **Overall assessment** [text]
- **Who would be interested in the results, and why** [text]
- **Major strengths** [text]
- **Major Concerns** [items]
- **Minor Comments** [items]
- **Technical failings that need to be addressed before the case is established** [IDs or summary]
- **Assessment against Nature-style criteria** [text]
- **Recommendation posture** [text]

For each Major Concern
- **Concern ID** R1-M1
- **Severity** Major
- **Blocking** Yes / No
- **Axis** [value]
- **Claim pointer** [value]
- **Evidence pointer** [value]
- **Concern** [text]
- **Why it matters** [text]
- **Resolution test** [text]

For each Minor Comment
- **Concern ID** R1-m1
- **Severity** Minor
- **Axis** [value]
- **Affected element** [value]
- **Evidence pointer** [value]
- **Issue** [text]
- **Required correction** [text]

Reviewer 2
[Same structure]

Reviewer 3
[Same structure]

Cross-review synthesis (post-review; not shown to reviewers)
- **Consensus strengths** [text]
- **Consensus blocking concerns** [items]
- **Other consensus major concerns** [items]
- **Where emphasis differs across reviewers** [text]
- **Forensic consistency findings** [confirmed errors, aggregation ambiguities, provenance gaps, suspected duplication, unresolved author input]
- **Minor revision checklist** [items]
- **Broad-interest / significance readout** [text]
- **Most important issues to resolve before a strong Nature-style case is established** [items]

Risk / unsupported claims
- [specific unsupported or not-assessable items]
```

## Red lines

- Do not invent reviewer identities, specialty roles, or selection history.
- Do not let one reviewer read, cite, anticipate, agree with, or respond to another review.
- Do not build or distribute a shared concern ledger before individual reports are frozen.
- Do not rewrite independent reports after comparison merely to reduce duplication or create artificial disagreement.
- Do not call reports mutually blind when they were generated in a shared context without an explicit limitation notice.
- Do not use dash punctuation or colons as habitual sentence connectors when clearer punctuation, headings, or sentence boundaries work.
- Do not invent experiments, validations, controls, citations, figure details, line numbers, or prior-work distinctions not present in the input.
- Do not silently turn reviewer assessment into author rebuttal drafting.
- Do not present the review as an editorial decision letter.
- Do not state that the manuscript belongs in `Nature` as a settled fact.
- Do not omit technical failings when the provided evidence does not establish the authors' case.
- Do not create Major or Minor concerns merely to fill a quota or make reviewer reports look balanced.
- Do not downgrade a core evidence, validity, ethics, or integrity problem to Minor because it is
  easy to describe, and do not upgrade a local presentation issue merely to sound severe.
- Do not label a numerical anomaly a confirmed error without arithmetic proof or source data.
- Do not hide confirmed internal contradictions merely because no reviewer identified them.
- Do not present an audit finding as reviewer consensus unless at least two frozen reports independently raised the same underlying concern.

## Related files

| File | Open when |
|---|---|
| [references/source-basis.md](references/source-basis.md) | You need source provenance, local rule summaries, or source-vs-implementation boundaries |
| [references/reviewer-workflow.md](references/reviewer-workflow.md) | You need the invocation order, fact-base extraction flow, or synthesis rules |
| [references/review-axes.md](references/review-axes.md) | You need the evaluation axes or reviewer weighting logic |
| [references/technical-concern-taxonomy.md](references/technical-concern-taxonomy.md) | You need the internal 12-axis coverage check, concern ledger, or claim/evidence-pointer rules |
| [references/domain-specific-review-gates.md](references/domain-specific-review-gates.md) | The manuscript has clear chemistry, engineering, materials, atmospheric, climate-ecology, hydrology, or remote-sensing evidence chains |
| [references/report-structure.md](references/report-structure.md) | You need the default output contract or section anatomy |
| [references/role-boundaries.md](references/role-boundaries.md) | You need constraints on reviewer differences and editor-versus-reviewer boundaries |
| [references/qa-checklist.md](references/qa-checklist.md) | You are finalizing an output and need groundedness / non-invention checks |
| [references/forensic-consistency-audit.md](references/forensic-consistency-audit.md) | You need the mandatory post-review audit of arithmetic, metric bounds, aggregation level, prose-table consistency, provenance, dispersion anomalies, or reproducibility gates |
| [../nature-shared/core/consistency-sweep.md](../nature-shared/core/consistency-sweep.md) | You are checking the manuscript against itself: headline counts that do not reconcile with the Methods, one metric at two precisions, a superlative contradicted by the paper's own table, overlapping error bars presented as an advantage, or internal summaries that disagree |
| [references/editorial criteria and processes.md](<references/editorial criteria and processes.md>) | You need the primary local Nature source text |

## Source hierarchy

Use sources in this order:

1. `references/editorial criteria and processes.md`
2. manuscript facts supplied by the user
3. conservative local implementation rules documented in `references/source-basis.md`
4. domain-specific supporting gates in `references/domain-specific-review-gates.md`

If a user asks for policy-level certainty beyond this local source, state the limit instead of improvising broader journal policy.
