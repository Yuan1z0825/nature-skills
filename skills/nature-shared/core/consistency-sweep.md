# Consistency Sweep

A retrospective audit of a manuscript that already exists. `terminology-ledger.md` is preventive:
it fixes the vocabulary before drafting. This file is detective: it finds the drift that a
manuscript has already accumulated, which is what happens to every manuscript that has been revised
more than once.

Use it when polishing or proofreading a full manuscript, self-reviewing before submission, or
auditing cross-document consistency. For a local edit, check the affected terms, numbers, and
claims first; expand to the full sweep when discrepancies suggest wider drift or the user asks
for it. Do not use it as a substitute for building a ledger on a fresh draft.

Two facts drive the method:

- **Multi-round editing fragments a manuscript.** Each round produces wording that fits its local
  context and diverges from the rest. Nobody notices, because nobody re-reads the whole document
  after each small edit.
- **Reviewers verify arithmetic and cross-check tables.** Numbers that do not reconcile and claims
  that contradict the paper's own data are the cheapest possible findings for a referee, and they
  cast doubt on everything that is harder to check.

## 1. Sweep, then inspect

Count variants mechanically first, then read the contexts before changing anything. Raw counts
over-report: Title Case in captions and headings, sentence-initial capitals, first-use acronym
expansions, and grammatically required inflections are legitimate variation.

For each axis, count every variant, then open the contexts of the minority forms. A term used 33
times one way and once another way is almost always a real slip; a term split 5/4 usually means two
different concepts are being conflated.

Start the mechanical pass with the bundled checker, resolving it relative to the
`nature-shared` package directory:

```bash
python scripts/check_consistency.py manuscript.tex tables.tex \
  --term-group 'test-object=specimen|sample|test article' \
  --term-group 'method-name=GraphNet|Graph Net'
```

The checker reports built-in self-reference and standard-deviation variants, user-supplied term
groups, equal numeric values printed at different precision, and equivalent lengths written in
different units. Use `--json` for machine-readable results or `--fail-on-findings` in a local
quality gate. Findings are warnings, not automatic corrections: identical numbers may denote
different quantities, and two terms may represent a real conceptual distinction. Inspect every
reported context before editing. This first pass does not replace the claim, tense, acronym,
cross-reference, or redundancy checks below.

## 2. Axes

| Axis | What to look for | Typical real finding |
| --- | --- | --- |
| Experimental factors | Every name used for one variable | One factor under four names, while a fifth name denotes a *different* concept |
| Physical objects | One word denoting two things | `specimen` meaning both a physical test article and a row in the test set |
| Acronyms | Definition site vs first use | Abbreviation used pages before it is defined; defined twice; never expanded |
| Model and method names | Expansion and capitalization at each mention | `Multi-Layer Perceptron` vs `Multilayer Perceptron`; `Extreme` vs `eXtreme Gradient Boosting` |
| Units | The **same quantity** in two units | `35 mm` cover in one section, `3.5 cm` cover in another |
| Statistical terms | Abbreviation and technical precision | `SD` in one table, `Std` in another; `confidence interval` where `prediction interval` is meant |
| Number formatting | Decimal places per metric; percent spacing | `8.26` in a table against `8.258` in the text |
| Self-reference | `this study` / `this paper` / `this work` / `this article` | One stray variant among many |
| Tense | Parallelism inside a list | Three conclusion items in past tense, one in present |
| Hyphenation | Compound modifiers | Genuine distinction: `residual-capacity check` (modifier) vs `the residual capacity` (noun) |
| Spelling variety | `-ise`/`-yse` vs `-ize`/`-yze`, `-our` vs `-or` | New text in British spelling inside a US-spelling manuscript |
| Cross-references | Non-breaking space before the number | `Figure~\ref` vs `Figure \ref` mixed |

Two axes are technical errors rather than style, and reviewers treat them as competence signals:

- **Interval terminology.** A confidence interval covers a parameter; a prediction interval covers a
  future observation. A paper reporting per-observation uncertainty must say *prediction interval*.
  `confidence level` for the alpha level is a different, correct term — do not "fix" it.
- **Same quantity, two units.** Converting for local readability forces the reader to verify that the
  two numbers match, and invites the suspicion that they do not.

Run several passes. Each pass surfaces axes the previous one did not, because fixing one axis makes
the next one visible. In practice a heavily revised manuscript yields findings on at least three
successive passes before converging.

## 3. Numeric self-consistency

- **Headline counts must be derivable from the Methods.** A design described as "640 samples covering
  32 states, four positions and four orientations" invites the reader to compute 512. If the real
  design is 32 x 4 positions x 5 signals (four orientations plus an averaged waveform), say so in
  the abstract and conclusion, not only in the Methods.
- **One metric, one precision, everywhere.** Cross-check every number that appears in more than one
  place — abstract, results prose, tables, conclusion — mechanically, not from memory.
- **Reused numbers must denote the same thing.** When two different quantities happen to share a
  value, label them distinctly; the same integer meaning "design combinations" in one section and
  "test-set size" in another will be read as one quantity.

## 4. Claims versus the paper's own data

Check every superlative against the table behind it.

- "Consistently highest across all three methods" fails if one column shows another item higher.
  State what the data supports and name the exception explicitly. A reviewer who finds the exception
  unaided assumes nothing else was checked either.
- Overlapping error bars do not support "outperformed". Use "statistically indistinguishable".
- Check for **under**claiming too. A conclusion saying "matched the best conventional model" when the
  results section reports first place on every metric throws away a real result.
- Internal summaries must agree with each other. If the results section concludes that features A and
  B are jointly dominant, the abstract and conclusion cannot credit only A.

## 5. Redundancy between prose and displays

Prose that restates a table's numbers adds length without information. Keep in the text only what the
display cannot show: the interpretation, the comparison, the reason a value matters.

The same applies within a paragraph — a sentence that re-states the immediately preceding sentence in
different words is padding, and it is easy to introduce when adding material in response to a
comment. After any insertion, re-read the neighbouring sentences and check that the new text is not
saying what the old text already said.

## 6. Order of operations

1. Numeric self-consistency and claims-versus-data (sections 3 and 4). Fix content before wording.
2. Terminology sweep (sections 1 and 2). After correcting a discrepancy, recheck affected occurrences and related claims; repeat a broader sweep only when changes or new findings warrant it.
3. Redundancy pass (section 5).
4. Recompile and re-verify anything that depends on pagination.

Content fixes change wording, and wording fixes change pagination, so this order avoids redoing work.
Any downstream artifact that quotes the manuscript — a response letter, a cover letter, a slide deck
— must be re-synchronized after every change; see `nature-response/references/package-consistency-audit.md`
when a revision package is involved.
