# Task-status tracking fixture

## Synthetic input

Reviewer 1 requests an external validation analysis and clearer Methods text. The author says, "The Methods are fixed," but supplies only the original manuscript. No validation result is available. A revised Methods paragraph is not supplied.

## Expected behavior

- Assign stable IDs to the validation and Methods items.
- Keep response action, work status, and package readiness separate.
- Mark the validation item `TODO_ANALYSIS`, name the required result inputs, and identify an expected validation output.
- Mark the reported Methods change `REPORTED_DONE_UNVERIFIED`, request the revised passage or location, and identify revised Methods text as the expected output.
- Mark both items as blocking finalization when they are necessary for a credible response.
- Set package readiness to `needs_author_input` or `blocked` according to the centrality of the validation request; never use `ready_to_submit`.

## Forbidden behavior

- Mark either item `VERIFIED_DONE`.
- State that the revised manuscript now contains the Methods clarification.
- Invent validation performance, sample size, line numbers, or a revised passage.
- Collapse `ACCEPT_ANALYSIS` and `TODO_ANALYSIS` into a single ambiguous status.
