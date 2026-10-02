# Review axes

## Core axes derived from the source

- `originality`
  - Ask whether the work appears to report original scientific research and whether the main results or conclusions seem genuinely new from the provided material.
  - Flag when novelty is asserted but not well distinguished from prior work.
- `scientific importance / significance`
  - Ask whether the work appears to be of outstanding scientific importance.
  - Distinguish field-local usefulness from broader scientific importance.
- `interdisciplinary readership interest`
  - Ask whether the conclusion appears interesting beyond the immediate specialty.
  - Note whether the implications feel immediate and far-reaching versus narrow and incremental.
- `technical soundness / technical failings`
  - Ask whether the authors' case is technically established from the evidence shown.
  - Identify concrete technical failings that must be addressed before the case is established.
- `readability for nonspecialists`
  - Ask whether a nonspecialist reader could understand the basic background, what was done, and how the results affect the field.
  - Use this axis especially for highly technical manuscripts.

## Axis-specific prompts

- For `originality`:
  - What is the claimed advance?
  - Is the distinction from prior work explicit and credible in the supplied manuscript?
- For `scientific importance / significance`:
  - Does the manuscript support a case for outstanding importance, or only competent incremental progress?
  - Are the implications immediate and far-reaching, or mainly field-internal?
- For `interdisciplinary readership interest`:
  - Who outside the immediate area would care, and why?
  - Is the conclusion framed in a way that broad scientific readers can grasp?
- For `technical soundness / technical failings`:
  - Which parts of the causal or evidentiary chain are under-supported?
  - What missing controls, analyses, validations, or logic gaps currently weaken the authors' case?
- For `readability for nonspecialists`:
  - Is the summary logic accessible?
  - Does the manuscript rely on unexplained jargon, compressed context, or unclear field impact?

## Weighting guidance for the three reports

- Assign these emphasis briefs before any reviewer receives the manuscript, and do not change them in response to another report.
- `Reviewer 1` should usually foreground `technical soundness / technical failings`.
- `Reviewer 2` should usually foreground `originality` plus `scientific importance / significance`.
- `Reviewer 3` should usually foreground `interdisciplinary readership interest` plus `readability for nonspecialists`.
- All three reviewers should still cover all axes briefly; the difference is weight, not scope omission.

## Missing-evidence handling

- If the manuscript text or figures are incomplete, do not infer absent validations or prior-work distinctions.
- Use explicit markers such as:
  - `Not assessable from provided material`
  - `AUTHOR_INPUT_NEEDED`
  - `Evidence not shown in the supplied manuscript excerpt`

## Things this axis set must not do

- Do not replace source-grounded axes with generic peer-review checklists unrelated to the local source.
- Do not force exhaustive domain-specific methodological critique when the provided material does not support it.
- Do not convert readability comments into copyediting line edits unless the user explicitly asks for that level of intervention.
