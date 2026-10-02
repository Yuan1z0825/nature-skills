# Test: defensive draft audit

## Input

```text
Mode requested: audit and revise this draft response.

Reviewer 1:
1. The method description is unclear and does not explain how model calibration was performed.
2. The authors should report the software version.

Author draft:
The reviewer clearly misunderstood our method. We already explained the calibration in the paper.
We have revised accordingly. The software version is now included.

Author notes:
- Calibration is described in Methods, but the exact paragraph may not be clear.
- Software version: v2.3.1.
- No line numbers are available yet.
```

## Expected behavior

- Detect task mode as `audit` or `revise`.
- Proceed with the bounded draft audit even though the editorial decision is not supplied; do not select a Major/Minor package strategy.
- Assign stable IDs `R1.1` and `R1.2`.
- Flag the author draft as defensive and insufficiently traceable.
- Rewrite the misunderstanding sentence as manuscript-clarity framing.
- Remove "We already explained the calibration in the paper" as impolite reviewer-facing language.
- Treat `R1.1` as `CLARIFY_EXISTING` plus possible `ACCEPT_TEXT`.
- Treat `R1.2` as `ACCEPT_TEXT` with supplied version `v2.3.1`.
- Use section names rather than invented line numbers.
- Mark package readiness as `draft_with_placeholders` or `needs_author_input` until exact Methods location or revised text is supplied.

## Forbidden behavior

- Do not retain "The reviewer clearly misunderstood our method."
- Do not retain "We already explained the calibration in the paper" or replace it with equivalent wording such as "as clearly stated in the manuscript".
- Do not retain bare "We have revised accordingly."
- Do not invent line numbers or a Methods paragraph.
- Do not claim the calibration explanation was already sufficient without clarifying the manuscript.
- Do not remove the supplied software version.

## Pass/fail checklist

- [ ] Defensive language is removed.
- [ ] The response does not tell the reviewer that the point was already present or should have been noticed.
- [ ] Each reviewer comment receives its own ID.
- [ ] Revised response includes manuscript-clarity framing.
- [ ] The response directly explains the calibration point and proposes or cites a clearer Methods presentation.
- [ ] `v2.3.1` is preserved exactly.
- [ ] Missing location details remain visible.
