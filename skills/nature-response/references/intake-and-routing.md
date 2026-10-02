# Intake and routing

## Contents

- [Decision-type gate for package-level work](#decision-type-gate-for-package-level-work)
- [Task modes](#task-modes)
- [Readiness states](#readiness-states)
- [Editor instruction handling](#editor-instruction-handling)
- [Pasted editorial email handling](#pasted-editorial-email-handling)
- [Minimum information by output type](#minimum-information-by-output-type)
- [Clarifying question rules](#clarifying-question-rules)
- [Routing shortcuts](#routing-shortcuts)


Use this file before splitting comments or drafting prose. Its job is to decide what task the
user is asking for, whether the supplied information is enough, and what output state is honest.

## Decision-type gate for package-level work

Identify the editorial decision before selecting a new package-level revision strategy or
drafting a complete response package. Task mode alone does not make the decision a blocker:
local wording edits, audits of existing replies, and comment-level triage can proceed with the
decision marked unknown. Return the requested passage or findings without inventing a decision,
expanding to a full package, or claiming submission readiness.

- If an editor letter explicitly says `Major Revision` or `Minor Revision`, use that value and do
  not ask a redundant question.
- If the user explicitly says 大修、小修, major review, minor review, major revision, or minor
  revision, normalize it to the corresponding revision type.
- If neither source resolves it and the requested work depends on it, ask in the user's language
  and pause only decision-dependent work. Continue independent inspection. Chinese default:
  `这是 Major Revision（大修）还是 Minor Revision（小修）？如果决定信没有明确写，请把决定信发给我，我帮你判断。`
  English default: `Is this a Major Revision or a Minor Revision? If the decision letter does
  not state it clearly, please send it and I can help classify the decision.`
- Never guess from the number or apparent difficulty of reviewer comments. Reviewer requests and
  editor instructions can be serious even when the package is labelled Minor Revision.
- `revise-and-resubmit` and `transfer after review` remain distinct decision types; do not force
  either into Major or Minor Revision. Follow the explicit editor instructions for those routes.

Once resolved, apply the Major/Minor strategy in `static/core/workflow.md` when package-level
strategy is requested and record the decision type in that strategy summary. Reuse a decision
already established in the task without asking again.

## Task modes

| Mode | Use when | Minimum useful input | Default output |
|---|---|---|---|
| `draft` | User wants a new point-by-point response package | Reviewer comments plus any author actions or manuscript-change notes | Internal/editor master plus separate reviewer-specific responses with placeholders where needed |
| `audit` | User provides an existing response draft and asks whether it is good enough | Response draft; reviewer comments when available | Findings first, then revised or annotated response sections |
| `revise` | User wants a draft rewritten for tone, traceability, or Nature-style response | Existing draft plus target change request | Revised response text plus changed-risk notes |
| `triage-only` | User wants strategy, action list, or missing inputs before writing prose | Reviewer comments or editor letter | Tracker, action map, missing-input list, no final letter |
| `cover-letter` | User asks for a revision cover letter only | Manuscript metadata plus revision summary or change notes | Concise editor-facing cover letter |
| `revision-package` | User asks for a complete revision package or pastes a decision email and wants the agent to begin | Decision email or reviewer/editor comments plus available author actions | Internal/editor master, reviewer-separated response files, cover letter when useful, change checklist, and placeholders |
| `latex-template` | User asks for LaTeX templates or filled `.tex` files | Desired output type; manuscript metadata if filling templates | Template paths or filled `.tex` content |
| `appeal-like` | User wants to challenge rejection or process rather than revise | Decision letter and disputed points | Route out of default workflow and explain separate appeal handling |

If the mode is unclear, infer the safest useful mode. Prefer `triage-only` when drafting would
require many unsupported facts.

## Readiness states

Use one readiness state for each comment and one package-level state:

| State | Meaning | Allowed output |
|---|---|---|
| `ready_to_submit` | Direct answer, supplied action, and traceable manuscript location are all present | Final response wording without unresolved placeholders |
| `draft_with_placeholders` | A useful draft can be written, but visible placeholders remain | Draft wording with bracketed placeholders and risk flags |
| `needs_author_input` | Final text would require facts the user has not supplied | Tracker, questions, partial draft only if placeholders are explicit |
| `blocked` | Ethics, compliance, data integrity, missing central evidence, or appeal-like routing prevents credible revision response | Blocking issue first; do not produce confident final wording |

Do not call a package `ready_to_submit` if any comment remains `draft_with_placeholders`,
`needs_author_input`, or `blocked`.

## Editor instruction handling

When editor instructions are supplied:

- Assign editor-level IDs before reviewer IDs: `E.1`, `E.2`, `E.3`.
- Address editor instructions before Reviewer 1, Reviewer 2, etc.
- If editor instructions conflict with reviewer suggestions, surface the conflict in the strategy summary.
- Treat explicit editor constraints as higher priority than reviewer-level preference.

Example:

```text
E.1: Focus on clarifying the central claim without substantial manuscript expansion.
R1.1: Make the causal claim stronger.
R2.1: Soften unsupported causal language.
```

The response strategy should explain that the editor's constraint and the observational design
support claim softening rather than stronger causal language.

## Pasted editorial email handling

When the user pastes an editorial decision email or revision invitation, do not ask them to
separate the email manually. Start by extracting:

- journal name;
- manuscript title and manuscript ID;
- decision type and revision deadline;
- required files, such as clean manuscript, marked manuscript, response to reviewers, cover letter, graphical abstract, data availability update, or supplementary files;
- editor instructions and portal-specific constraints;
- reviewer-report boundaries and comment numbering.
- reviewer-visibility rules and whether the portal accepts separate reviewer-response files.

Ignore boilerplate only after checking it for required files, deadlines, formatting constraints,
and resubmission instructions. If the email contains reviewer reports, enter `revision-package`
or `draft` mode automatically depending on whether the user requested a full package or only a
response letter. If reviewer boundaries are ambiguous, keep the original ordering visible in the
internal package and flag the ambiguity instead of inventing identities. Do not create outward-facing
reviewer files until their boundaries can be separated safely.

## Minimum information by output type

### Full draft response

Requires:

- reviewer comments or editor comments;
- enough author notes to know which actions were taken;
- manuscript locations or placeholders for claimed changes.

If locations are missing, use section names or bracketed placeholders. Do not invent line numbers.

### Final submission-ready response

Requires:

- all reviewer and editor comments identified;
- all claimed actions supplied by the author;
- traceable locations for every manuscript change;
- real details for experiments, analyses, statistics, citations, figures, tables, supplements, ethics, and data availability.

If any required fact is missing, the output is not `ready_to_submit`.

### Audit

Requires:

- user draft;
- reviewer comments when available.

If reviewer comments are absent, audit only the visible draft and flag that completeness cannot be verified.

## Clarifying question rules

Subject to the package-level decision-type gate above, usually proceed with placeholders and risk
flags. Ask concise questions only when:

- the requested package strategy depends on Major/Minor Revision status that is not supplied and cannot be extracted from the decision letter or task context;
- the user explicitly asks for final submission-ready text and required facts are missing;
- the draft would otherwise fabricate data, locations, approvals, statistics, citations, or figure panels;
- reviewer boundaries are too ambiguous to assign stable IDs;
- the case appears appeal-like or outside normal revision response.

When asking, keep questions specific. Ask the decision-type question first when it blocks the requested work;
after that, group only the remaining facts that genuinely block the requested output:

```text
I need three facts before final wording: the validation result summary, the Methods/Results location,
and whether Fig. 5 is a main or supplementary figure.
```

## Routing shortcuts

- Vague author note such as "we fixed it" -> `needs_author_input`.
- Existing response with hostile language -> `audit` or `revise`.
- Reviewer asks for impossible new work -> normal revision mode with `PARTIAL` or `OUT_OF_SCOPE`, not appeal.
- Rejection challenge -> `appeal-like`.
- User asks only "what should we do?" -> `triage-only`.
- Pasted decision/revision email with reviewer reports -> auto-parse the email and begin `draft` or `revision-package`; do not wait for the user to reformat the email.
