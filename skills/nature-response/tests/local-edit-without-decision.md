# Test: local reply edit without an editorial decision

## Input

```text
Please make this reply more polite and concise. Only return the revised reply.

Reviewer: Please clarify the software version used.
Draft reply: The reviewer missed this. We used version 2.3.1.
```

## Expected behavior

- Return a polite revised reply preserving version `2.3.1`.
- Do not require a Major/Minor Revision label for this wording edit.
- Do not claim that the manuscript has been revised or invent its location.
- Respect the requested output: no master tracker, cover letter, or package-readiness verdict.

## Follow-up

```text
Now list what information is missing from this response before I edit the manuscript.
```

- Perform bounded comment-level triage using the existing reply and reviewer comment.
- Identify missing manuscript-location or change evidence without inventing it.
- Continue without asking for the editorial decision unless the user expands the task to a decision-dependent package strategy.

## Evaluation boundary

This is a behavioral fixture for manual or agent evaluation, not an executed model benchmark.
Evaluate the produced response, questions, and scope, not matching phrases or headings.
