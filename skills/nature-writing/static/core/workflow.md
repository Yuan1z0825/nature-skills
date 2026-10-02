# Writing workflow

Use these steps for a new section or substantial restructuring. For a title, single paragraph, or follow-up edit, apply only the relevant steps and reuse established framing and terminology. Steps 1-3 are planning, step 3b checks unresolved choices, 4-6 are drafting, 7-8 are checking, and step 9 handles revision.

## 1. Build a one-sentence argument

> In [system/problem], we show [advance] using [approach], supported by [evidence], with [boundary].

Force every section to serve this sentence. If the sentence cannot be written, the paper does not yet have an argument — surface that to the user.

## 1b. Build the Terminology Ledger

On first contact with the material, extract the recurring terms, abbreviations, notation, and proper names into a Terminology Ledger before drafting any prose. Lock the canonical forms and reuse them across every section. See `../../../nature-shared/core/terminology-ledger.md`.

## 2. Choose section architecture

Pick the section structure from the relevant `section/*.md` fragment and, if needed, deeper patterns from `references/article-architecture.md`.

## 3. Map each paragraph to one job

Each paragraph must do exactly one job from: context, gap, approach, result, comparison, mechanism, implication, limitation.

If a paragraph carries two jobs, split it before drafting.

## 3a. Allocate Results evidence before drafting

When the task includes Results, a full manuscript, main-text compression, or
main-versus-SI placement, load
`../../../nature-shared/core/main-text-discipline.md`. Classify each result as
core discovery, necessary support, qualification, robustness, heterogeneity,
provenance detail, alternative inference, or edge case. Build the shortest
sufficient main-text evidence chain and record the destination of everything
else. Do not bury conclusion-changing evidence in SI.

## 3b. Scoped alignment check

Proceed from the supplied material and established task context. For a substantial draft, briefly state the core argument and consequential assumptions so the user can correct them; this update is not an approval gate.

Ask only when an unresolved choice would materially change the core argument, evidence meaning, or requested deliverable and cannot be resolved from context. Explain the choice and pause only the dependent passages. Continue independent work and mark missing facts with explicit placeholders rather than filling them in.

If the user explicitly requested outline approval before prose, deliver the outline and wait. Otherwise complete the requested draft and applicable checks without adding an outline-approval stage. Preserve existing approvals across follow-ups.

When a requested voice cannot be inferred from supplied prose or prior corrections, ask for a short writing sample and calibrate to its style, never its claims or facts.

## 4. Draft from evidence outward

Keep claims near the data that support them. Do not stack claims at the top of a section then leave evidence at the bottom.

## 5. Calibrate verbs to evidence strength

`show` / `demonstrate` need strong direct evidence. `suggest` / `indicate` are for trend-level or indirect evidence. `may` / `could` are for plausible but unverified mechanisms.

## 6. Remove unsupported novelty and universal claims

Sweep for `first`, `unique`, `unprecedented`, `comprehensive`, `complete`, `always`, `never`. Replace with bounded claims or delete.

## 7. Run a paragraph-flow check

- One paragraph, one message.
- The first sentence is the topic / claim.
- Each subsequent sentence has an explicit relation to the previous one (cause, comparison, restriction, example).

For full reverse-outlining, open `references/paragraph-flow.md`.

## 8. Return prose plus notes

Output the draft together with explicit notes on assumptions, missing inputs, and where evidence is needed. See `output-format.md`.

## 9. Revise by targeted edit, not full rewrite

When the user reacts to a draft, "this is not what I meant" is usually local — a wrong claim, a mis-framed paragraph, the wrong result leading. Do not silently re-draft the whole section: a full rewrite breaks the paragraphs that were already right and forces the user to re-check everything.

- Focus on the paragraphs or claims the user flagged; keep unaffected passages verbatim.
- If a requested fix requires changes to adjacent passages for consistency, explain and make the necessary changes within the authorized scope. Confirm only a material change to the argument or scope under step 3b, or when the user explicitly reserved structural approval.
- Keep the Terminology Ledger (step 1b) stable across revisions unless the user changes a term; never let a revision reintroduce a variant of a locked term.
- After revising, re-run only the checks relevant to what changed (steps 5-7), not the whole workflow.
- If the user's redirection changes the original premise, use that correction and revisit step 3b only for choices that remain unresolved.
- Every proposed addition triggers the main-text deletion check: identify the
  new sentence's function, find existing text with the same function, and prefer
  replacement or compression before appending. Re-run the paragraph necessity
  and claim-repetition checks after the edit.
