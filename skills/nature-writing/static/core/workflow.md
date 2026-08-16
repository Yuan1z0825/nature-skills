# Writing workflow

Run these steps for any drafting or restructuring task. Steps 1-3 are planning, step 3b is an alignment gate, 4-6 are drafting, 7-8 are checking, step 9 is the revision loop.

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

## 3b. Confirmation gate — align before drafting

Drafting a full section on a wrong assumed premise wastes the whole draft and is the main reason output "does not match what I meant". Before writing full prose, show the user a short alignment block and **stop for confirmation**:

- **One-sentence argument** (from step 1) — the single most important thing to get right. Echo it back in plain language.
- **Plan**: detected paper type, section(s), journal / word limit, and the paragraph map from step 3 as a short bullet list.
- **Key terminology**: the canonical forms locked in the Terminology Ledger (step 1b) for the main methods, models, datasets, and metrics. Surface them here so the user can fix a wrong canonical term before it propagates through every section.
- **Primary reader**: who the draft is optimized for, and which of the five reader questions it leads with (relevance / novelty / trust / reuse / meaning — see `../../../nature-shared/core/reader-workflow.md`). Getting the lead question wrong is a common silent cause of "this is not what I meant".
- **Key assumptions**: anything else you inferred rather than were told — especially what the core contribution is and which result to lead with. Mark each clearly as an assumption.
- **At most 2–3 targeted questions**, only on genuinely ambiguous, high-leverage points (how to frame the core contribution, target audience / journal, which result leads). Do not ask about things the user already made clear, and do not pad the list to reach three.

Then wait for the user to confirm or correct before drafting the full section.

Shortcuts:

- **Skip the gate** when the core claim, evidence, and boundary are all clearly given and there is no real ambiguity in framing. In that case just state the one-sentence argument in a single line (per the router) and proceed.
- **Depth dial**: for a full section or a major rewrite, offer to deliver the outline first (the paragraph map from step 3) and expand to full prose only after the user approves it. Reacting to an outline is far cheaper than reacting to full prose. Skip this for short or single-paragraph requests.
- **Style, not substance**: if the user says the voice or style "is not mine", do not keep guessing — ask for one short sample of their own writing, then calibrate to it. From the sample, match: typical sentence length and rhythm, hedging level (`demonstrate` vs `may` / `could`), preferred connectives and transitions, person (first-person `we` vs passive), and terminology / abbreviation choices. Match the voice, not the content — never reuse the sample's claims or facts.

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

- Change **only** the paragraphs or claims the user flagged; keep the rest verbatim.
- If a requested fix genuinely forces a structural change (reordering sections, moving a claim across paragraphs), say so and confirm the new structure before applying it, rather than restructuring silently.
- Keep the Terminology Ledger (step 1b) stable across revisions unless the user changes a term; never let a revision reintroduce a variant of a locked term.
- After revising, re-run only the checks relevant to what changed (steps 5-7), not the whole workflow.
- If the user's redirection reveals the original premise was wrong, return to the confirmation gate (step 3b) instead of patching prose on a broken premise.
- Every proposed addition triggers the main-text deletion check: identify the
  new sentence's function, find existing text with the same function, and prefer
  replacement or compression before appending. Re-run the paragraph necessity
  and claim-repetition checks after the edit.
