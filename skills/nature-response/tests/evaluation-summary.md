# Evaluation summary

`nature-response` is evaluated with synthetic Markdown fixtures. These tests are not executable
unit tests; they are behavior contracts for manual and agent review.

## Status rationale

Recommended status: `Beta`.

Rationale:

- The core rules are defined in `SKILL.md` and modular references.
- The skill has synthetic fixtures covering package-level decision-type intake, local edits without a decision label, minor revision, major
  revision with missing evidence, impossible experiment, defensive draft audit, conflicting
  reviewers, mutually blind reviewer-response separation, and per-task status tracking.
- Each fixture includes expected behavior, forbidden behavior, and pass/fail criteria.
- The examples show expected output shape without using real confidential reviewer comments.
- The skill has not yet been validated on real anonymized revision packages, so `Stable` would be premature.

## Fixture coverage

| Fixture | Coverage | Key failure prevented |
|---|---|---|
| `unclear-decision-type.md` | package-level Major/Minor intake gate | guessing the revision type or drafting with the wrong package strategy |
| `local-edit-without-decision.md` | local wording edits and bounded triage | blocking an independent edit or expanding it into a full package |
| `minor-revision.md` | stable IDs, minor comments, missing citation metadata | fabricated citation or line numbers |
| `major-revision-missing-evidence.md` | validation request, statistical details, missing evidence | invented results or p-values |
| `impossible-experiment.md` | out-of-scope longitudinal evidence | time/funding excuse or fabricated survival data |
| `defensive-draft-audit.md` | hostile draft language, missed existing text, vague compliance | accusatory wording or an impolite "we already stated this" reply |
| `conflicting-reviewers.md` | editor priority, incompatible reviewer requests, and reviewer isolation | contradictory promises or cross-reviewer disclosure |
| `reviewer-visibility.md` | separate outward-facing responses for mutually blind reviewers | leaked comments, IDs, recommendations, or cross-review references |
| `task-status-tracking.md` | action/status separation, verification evidence, expected output, blocking state | false completion and premature submission readiness |

## Manual evaluation checklist

- [x] Every fixture has input, expected behavior, forbidden behavior, and pass/fail checklist.
- [x] No fixture uses real reviewer comments.
- [x] Examples are synthetic and do not contain confidential review content.
- [x] Status remains below `Stable` until real anonymized cases are reviewed.

## Promotion path to Stable

Promote from `Beta` to `Stable` only after:

- at least two real anonymized revision packages are tested with author permission;
- no fabricated actions, line numbers, statistics, or citations are observed;
- Chinese-note workflows produce usable English response drafts and Chinese confirmation notes;
- edge cases such as conflicting reviewers and impossible experiments remain traceable.
