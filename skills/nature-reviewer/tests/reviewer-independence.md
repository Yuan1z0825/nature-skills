# Reviewer-independence behavior fixture

## Synthetic request

The user supplies one complete manuscript and asks for three reviewer reports plus a synthesis. Reviewer 1 identifies a missing control. Reviewer 2 could independently identify the same issue or focus elsewhere. Reviewer 3 receives no special evidence. The execution environment supports isolated reviewer contexts.

## Expected behavior

- Fix all three emphasis briefs before generating any report.
- Give every reviewer the same immutable manuscript/source packet, common criteria, report skeleton, and only its own emphasis brief.
- Run Reviewer 1, Reviewer 2, and Reviewer 3 in separate contexts, subagents, processes, or invocations.
- Let every reviewer build its own fact assessment and private concern ledger.
- Freeze all three reports before comparing concern IDs or drafting synthesis.
- Allow natural duplication: if Reviewer 2 independently finds the missing control, preserve it in both reports.
- Generate `Cross-review synthesis (post-review; not shown to reviewers)` only after the reports are locked.
- Label the missing-control issue consensus only if at least two frozen reports independently raised it.
- Keep post-review deduplication inside the synthesis; preserve the original reviewer-local IDs.

## Forbidden behavior

- Do not pass Reviewer 1's report, notes, concern ledger, recommendation, or suspected concerns to Reviewer 2 or Reviewer 3.
- Do not tell a reviewer what another reviewer noticed or failed to notice.
- Do not write `as another reviewer noted`, `I agree with Reviewer 1`, or equivalent cross-review language inside an individual report.
- Do not use a shared concern ledger to assign issues across reviewers before drafting.
- Do not rewrite, suppress, add, or redistribute concerns after comparison to meet a duplication target or manufacture distinct personalities.
- Do not feed the synthesis back into any reviewer context.
- Do not claim mutual blindness if all reports were drafted in one shared context without an explicit limitation notice.

## Fallback when isolation is unavailable

- Produce one reviewer report per invocation, or clearly state before output that technical mutual blindness cannot be guaranteed.
- Never hide this limitation behind reviewer numbering or different writing styles.

## Pass/fail checklist

- [ ] Reviewer inputs contain no other reviewer output or analytical hints.
- [ ] Reviewer contexts are isolated.
- [ ] Reports are frozen before comparison.
- [ ] Individual reports contain no cross-review references.
- [ ] Natural overlap remains unchanged.
- [ ] Synthesis is clearly post-review and not shown to reviewers.
- [ ] Consensus is derived only from independently raised concerns.
