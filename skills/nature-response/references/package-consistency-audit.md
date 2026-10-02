# Package consistency audit

## Contents

1. [The coupling rule](#1-the-coupling-rule)
2. [Red marking must have a baseline](#2-red-marking-must-have-a-baseline)
3. [Deletions ripple](#3-deletions-ripple)
4. [Counting statements go stale](#4-counting-statements-go-stale)
5. [Location references are volatile](#5-location-references-are-volatile)
6. [Manuscript self-consistency and terminology drift](#6-manuscript-self-consistency-and-terminology-drift)
7. [Etiquette failures that survive editing](#7-etiquette-failures-that-survive-editing)
8. [Delivery gate](#8-delivery-gate)

Use this file when a revision package is being finalized, re-edited after an earlier draft, or
audited before submission. It covers the failures that are **mechanically verifiable** and that
survive an editorial read: the manuscript and the response letter drifting apart, red marking that
misrepresents what changed, numbers that do not reconcile, and terminology that fragments across
rounds.

`qa-checklist.md` asks whether the response is complete, honest, and well-toned. This file asks
whether the shipped files actually agree with each other. Run both.

The core rule: **a revision package is three coupled artifacts** — the marked manuscript, the clean
manuscript, and the response letter. An edit to any one of them can silently invalidate the others.
Never edit the manuscript without re-running the checks below.

## 1. The coupling rule

Response letters quote manuscript text. Every quote is a promise that the manuscript reads exactly
that way. Any later edit to a quoted passage must be mirrored in the letter, or a reviewer
comparing the two finds a mismatch and starts doubting everything else.

Checks:

- Every quoted passage in the letter appears **verbatim** in the expanded manuscript source,
  including statically named `\\input{...}` and `\\include{...}` files.
- Editing a quoted manuscript sentence triggers a letter update in the same commit, not later.
- Whitespace, hyphenation, and unit changes count — `4.5 cm` in the letter against `45 mm` in the
  manuscript is a mismatch.
- Where the letter resolves a cross-reference for readability (`Table \ref{tab:x}` printed as
  `Table 1`), record that substitution with a repeated `--substitution SOURCE=RENDERED` argument so
  the automated check does not flag it every round.

Script the check rather than eyeballing it. Resolve the script relative to this skill directory,
then pass the actual package paths:

```bash
python scripts/check_package_consistency.py \
  --manuscript main.tex \
  --response response.tex \
  --clean main-clean.tex \
  --marked main-marked.tex \
  --substitution 'Table \ref{tab:x}=Table 1'
```

The checker expands existing statically named `\\input` and `\\include` files, normalizes LaTeX and
whitespace, checks the arguments of `\\RevisedExcerpt`, `\\revtext`, and `\\oldtext` against the
manuscript, compares the number of `\\ReviewerComment` and `\\AuthorResponse` blocks, removes
`\\deletedtext` / `\\deleted` passages from the marked copy, and confirms that clean and marked
sources otherwise have the same text after revision markup is removed. Use repeated
`--quote-macro NAME` arguments when a project defines a different quote macro and repeated
`--substitution SOURCE=RENDERED` arguments for deliberate rendered substitutions. Use `--json` for
machine-readable findings. A non-zero exit status means the package still contains a mechanical
mismatch.

Re-run it after **every** manuscript edit. It does not replace compiled-PDF page checks, color
inspection, citation/reference diagnostics, or editorial judgement. Those remain manual gates in
the sections below.

## 2. Red marking must have a baseline

Red means "changed in this revision". The baseline is the **archived original submission**, not
what feels new.

- Keep the submitted version on disk (`main_R0_backup.tex` or equivalent) and diff against it.
- Marking unchanged text red inflates the apparent revision and is caught the moment a reviewer
  opens the marked manuscript.
- Leaving genuinely new text unmarked hides work the reviewer asked for.
- Sentences reworded from the original are a judgement call; be consistent within a package and
  lean toward marking substantive rewording, not cosmetic edits.

When the letter reproduces **existing** manuscript text for the reviewer's convenience, give it a
visually distinct, non-red style (plain italic) and state in the letter preamble that plain italic
means unchanged text. Reproducing unchanged text in the same red italic used for new text is a
misrepresentation even when the surrounding prose is honest.

## 3. Deletions ripple

Removing content is more dangerous than adding it, because the letter keeps describing what is no
longer there. After any deletion, grep the letter for prose that describes the deleted item.

Failure patterns seen in practice:

- A table row is dropped, but the letter still says "the table reports all four factors named by the
  reviewer". Fix the sentence, or point to wherever the fourth factor now lives.
- A citation group is trimmed, and the reference list shrinks in a round where reviewers asked for
  **more** references. Decide whether to explain the net change in the letter.
- A sentence is deleted from the manuscript, but the letter still quotes it and still claims it was
  added in response to a comment.
- A quantity is deleted from a table, but the letter's prose still cites that table as the source.
- Deleting a sentence can orphan the sentence that introduced it — check that the surviving opening
  still refers to something present ("This decomposition is actionable" after the only sentence
  about the decomposition was cut).

## 4. Counting statements go stale

Do not write "two sentences have been added", "three new references", or "the four summary items".
Splitting one sentence into three, or dropping an item, silently falsifies the count, and a reviewer
who counts finds the discrepancy.

Prefer "a short passage", "a dedicated item", "the sentences quoted below". If a count must appear,
verify it against the manuscript at the end of every round.

## 5. Location references are volatile

Page numbers change whenever the manuscript reflows, including from edits far away in the document.
Adding a reference can add a page to the bibliography; shortening a paragraph can pull a section back
a page.

- Re-verify **every** page and section reference in the letter after **every** recompile, not once
  at the end.
- Verify by extracting text per page from the compiled PDF and asserting that the quoted phrase
  actually falls on the claimed page, rather than trusting the number written earlier.
- Section numbers are more stable than page numbers; prefer them when the journal allows.
- Never invent line numbers.

```bash
pdftotext -f 8 -l 8 main.pdf - | grep -c "phrase the letter places on page 8"
```

## 6. Manuscript self-consistency and terminology drift

A revision round is when manuscript-internal drift is both introduced and catchable. Run the full
sweep from `nature-shared/core/consistency-sweep.md`: headline counts that do not reconcile with the
Methods, one metric reported at two precisions, superlatives contradicted by the paper's own tables,
over- and under-claiming, terminology and unit variants accumulated across rounds, and tense
parallelism inside the conclusion items.

Two points are specific to a revision package:

- **Every fix that lands inside red-marked text must be mirrored in the letter's quotes** (section 1).
  A terminology sweep is exactly the kind of low-attention edit that desynchronizes a package,
  because the edits feel too small to be worth re-checking.
- **The letter must not promise text the manuscript lacks.** If the letter says "this point is now
  also stated in the Abstract" and quotes a sentence, that sentence must exist in the abstract. This
  is the single most damaging failure in a response package: it is trivially checkable, and it reads
  as fabricated compliance rather than as an oversight.

A related trap: prose added in response to a comment often restates what the neighbouring sentence
already said, or repeats numbers already given in a table quoted right below it in the letter. After
drafting a response, re-read the manuscript passage in place and cut the restatement.

## 7. Etiquette failures that survive editing

Two wording patterns pass a normal read and still damage the response:

- **"Already" constructions.** "The tested configuration is already specified in Section 2" tells the
  reviewer they failed to read. Reframe as author-side work: "To make these boundaries concrete, we
  reproduce below the sentences of Section 2 that define the tested configuration." See
  `tone-and-stance.md`.
- **Cross-reviewer references.** "This comment coincides with Comment 4 of Reviewer 1 and is
  addressed by the sentences quoted above" breaks isolation. Each reviewer's section must stand
  alone, which means **repeating** the quoted manuscript passage in full under both reviewers. The
  duplication is correct, not redundant. See `difficult-cases.md`.

## 8. Compile and delivery gate

- The marked and clean manuscripts must differ **only** in color. Verify with a full text diff of the
  two PDFs, not by inspection.
- Generate the clean copy by toggling the mark-up macro, never by hand-deleting markers.
- Colored table or figure environments need their color removed separately from the mark-up macro.
- Confirm the clean copy actually has no colored text by rendering the page with the most red and
  checking it, since a text diff cannot see color.
- Compile both files with the project's own engine; do not silently substitute one.
- Zero compile errors, zero undefined citations, zero undefined references.
- Bibliography entry count matches expectations after any citation change.
- Every reviewer comment has exactly one response — assert the counts match per reviewer.

## 9. Audit order

Run in this order; later steps depend on earlier ones being stable.

1. Manuscript self-consistency and terminology sweep (section 6, and the shared sweep it points to) — fix content before formatting, and repeat until a pass finds nothing new.
2. Sync every letter quote affected by step 1 (section 1).
3. Recompile.
4. Re-verify page and section references (section 5).
5. Re-run the verbatim quote check (section 1).
6. Etiquette and isolation pass (section 7).
7. Generate the clean copy and run the delivery gate (section 8).
8. Package.

Steps 3 to 5 repeat after every subsequent edit, however small. An edit that removes one sentence
changes pagination, which invalidates the page references verified in the previous round.
