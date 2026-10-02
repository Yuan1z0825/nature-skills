# Test: mutually blind reviewer responses

## Input

```text
Editor decision: Major revision.

Reviewer 1:
1. Please add an external validation analysis.
2. Please clarify the replicate definition.

Reviewer 2:
1. The replicate definition is unclear.
2. The Discussion should state the limitations of external validation.

Author notes:
- External validation was completed and is reported in Results subsection 3.4.
- The replicate definition was added to Methods subsection 2.2.
- The Discussion now states the validation limitation.
```

## Expected behavior

- Build an internal/editor master tracker containing `R1.1`, `R1.2`, `R2.1`, and `R2.2`.
- Mark the master tracker as not reviewer-facing.
- Produce one standalone response for Reviewer 1 and another for Reviewer 2.
- Use neutral local labels such as `Comment 1` and `Comment 2` in each reviewer-facing file.
- Answer the replicate-definition concern fully in both files.
- Keep manuscript locations and scientific claims consistent across both files.

## Forbidden behavior

- Do not include `R2.*` IDs or Reviewer 2 comments in the Reviewer 1 file.
- Do not include `R1.*` IDs or Reviewer 1 comments in the Reviewer 2 file.
- Do not write "as the other reviewer noted" or "see our response to Reviewer 1".
- Do not disclose another reviewer's recommendation or confidential remarks.
- Do not send the internal/editor master tracker as a reviewer-facing response.

## Pass/fail checklist

- [ ] The master contains all four internal IDs and is clearly restricted to author/editor use.
- [ ] Reviewer 1 receives only Reviewer 1 comments and complete responses.
- [ ] Reviewer 2 receives only Reviewer 2 comments and complete responses.
- [ ] The repeated concern is answered independently in both files.
- [ ] No cross-reviewer phrase, ID, comment, recommendation, or response appears.
- [ ] Both reviewer-specific files describe the same manuscript changes consistently.
