# Nature Introduction Corpus Guidance

Use this reference when drafting, restructuring, or polishing an Introduction
for flagship **Nature**, **Nature Communications**, **Nature Machine
Intelligence**, or another **Nature Portfolio** title. The patterns were
initially distilled from an author-supplied reading set of published NMI papers
and are generalized here as Nature-style defaults. They are **corpus-derived
writing guidance, not official journal requirements**. Current target-journal
instructions, article-type rules, reporting standards, and the paper's actual
evidence always take precedence.

## Contents

- [Make the Introduction converge](#make-the-introduction-converge)
- [State an exact knowledge gap](#state-an-exact-knowledge-gap)
- [Use literature to construct the gap](#use-literature-to-construct-the-gap)
- [Frame a scientific question](#frame-a-scientific-question)
- [Let the answer emerge late](#let-the-answer-emerge-late)
- [End with a compact research route](#end-with-a-compact-research-route)
- [Align Introduction, Results, and Discussion](#align-introduction-results-and-discussion)
- [Run the Nature Introduction audit](#run-the-nature-introduction-audit)

## Make the Introduction converge

Build a narrowing argument rather than an extended topic overview:

`important problem -> specific phenomenon or difficulty -> what existing approaches establish -> unresolved limitation or tension -> exact unknown -> research question or hypothesis -> what this study does`

Move quickly. Assume the target journal's readers understand the broad field's
importance; use only enough context to make the specific unresolved problem
intelligible. By the end of the opening paragraph, expose the concrete
phenomenon, contradiction, failure condition, or bottleneck whenever the
material permits it.

Delete or compress background that neither narrows the problem nor makes the
eventual question necessary. A history of the field is not a substitute for a
problem funnel.

## State an exact knowledge gap

Express the gap as something genuinely unknown, disputed, or untested. Prefer:

- what causes an observed advantage or failure
- under what conditions a claimed benefit appears or disappears
- which mechanism, information source, or design choice is necessary
- why two credible bodies of evidence disagree
- whether a proposed representation or signal adds information beyond the
  current baseline

Avoid `existing methods have limitations` unless the next clause names the
specific limitation and why resolving it matters. The reader should be able to
complete the sentence:

> It remains unclear whether, why, or under what conditions ______.

Do not define the gap as the absence of the author's method. `No one has used
our architecture for this task` is not yet a scientific unknown.

## Use literature to construct the gap

Organize citations by argumentative function, not as an author-by-author
catalogue:

1. establish the known capability, phenomenon, or prevailing explanation
2. show what prior work has already resolved
3. expose the unresolved condition, boundary, or contradiction
4. make the present research question unavoidable

When the literature contains tension, state both sides fairly and use the
tension to motivate a discriminating question. Avoid generic transitions such
as `substantial progress has been made, but challenges remain` when the cited
work supports a more exact conflict or boundary.

Every literature paragraph must earn its place by narrowing the question. Move
material that only demonstrates breadth to Related Work, Methods context, or a
shorter citation cluster.

## Frame a scientific question

Prefer a question about a phenomenon, condition, mechanism, or boundary over a
method-demand claim:

- weak: `Existing methods are limited; therefore, a new method is needed.`
- stronger: `Performance improves in some settings but deteriorates in others;
  which condition determines whether the proposed mechanism is beneficial?`

Let novelty arise from the unanswered question and the study design capable of
answering it. Remove unsupported novelty adjectives such as `novel`,
`groundbreaking`, `unprecedented`, or `innovative` when the question,
controlled comparison, or diagnostic perturbation already demonstrates the
advance.

## Let the answer emerge late

Do not force the paper's preferred concept, mechanism, or framework into the
opening before the problem logic has motivated it. First establish the
phenomenon, limitation, and exact unknown; then introduce the study's conceptual
move as the natural way to resolve that unknown.

Use transitions such as `To address this question`, `To test this possibility`,
or `To this end` only after the question is explicit. Do not use the transition
to conceal a missing gap.

## End with a compact research route

Prefer one connected closing paragraph over a ceremonial contribution list for
a Nature Portfolio research article, unless the target journal, article type,
editor, or user requires another structure. The paragraph should state:

`research question -> study design or conceptual move -> decisive evaluation route -> principal scope of inference`

Preview the logic of the Results without replaying all findings, metrics, or
figure-level detail. A restrained result-level statement is acceptable when it
clarifies the paper's answer, but do not turn the final paragraph into an
abstract or Discussion.

The route should tell the reader why the chosen comparisons, perturbations,
decompositions, or boundary tests can answer the stated question. Method names
alone do not provide that logic.

## Align Introduction, Results, and Discussion

Treat the three sections as one story at different levels:

- **Introduction:** establish why each central question must be asked.
- **Results:** answer the questions through an escalating evidence chain.
- **Discussion:** synthesize what those answers mean together.

Draft backward from the paper's actual Results claims. For every central
Results subsection, identify the question that the Introduction must motivate.
For every question or hypothesis introduced, identify the Results subsection
that answers it. Do not create parallel stories.

A useful alignment pattern is:

`Introduction: phenomenon -> unresolved source -> necessary-condition question -> decomposition question`

`Results: establish phenomenon -> identify source -> perturb or test necessity -> decompose contributions -> establish boundaries`

`Discussion: synthesize the answers -> relate to theory and prior work -> state implications and limits`

## Run the Nature Introduction audit

First state the paper's exact unknown in one sentence. If that sentence is
vague, repair the gap before polishing prose.

Then build this reverse-outline table:

| Introduction unit | Narrowing move | Literature function | Question motivated | Results answer |
|---|---|---|---|---|
| Paragraph or sentence block | What becomes more specific here? | Establish, resolve, contrast, or expose gap | Which exact question follows? | Which Results subsection answers it? |

Flag and revise any unit that:

- adds field background without narrowing the problem
- lists studies without constructing a known–unknown transition
- introduces the solution before the reader can see why it is needed
- claims novelty mainly through adjectives
- previews a Results claim for which no question has been motivated
- motivates a question that the Results never answer

Before finalizing, run a deletion test: if removing a paragraph leaves the
exact gap, research question, and Results roadmap intact, compress, relocate, or
delete that paragraph.
