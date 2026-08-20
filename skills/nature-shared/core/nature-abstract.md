# Nature Abstract Corpus Guidance

Use this reference when drafting, restructuring, or polishing an abstract for
flagship **Nature**, **Nature Communications**, **Nature Machine Intelligence**,
or another **Nature Portfolio** title. The patterns were initially distilled
from an author-supplied reading set of published NMI papers and are generalized
here as Nature-style defaults. They are **corpus-derived writing guidance, not
official journal requirements**. Current target-journal instructions,
article-type rules, reporting standards, and the paper's actual evidence always
take precedence.

## Contents

- [Treat the abstract as the shortest evidence chain](#treat-the-abstract-as-the-shortest-evidence-chain)
- [Use a discovery-centred architecture](#use-a-discovery-centred-architecture)
- [Make the gap sharp and brief](#make-the-gap-sharp-and-brief)
- [Keep only answer-enabling method logic](#keep-only-answer-enabling-method-logic)
- [Select one main claim](#select-one-main-claim)
- [Use numbers by necessity](#use-numbers-by-necessity)
- [End with the conceptual payoff](#end-with-the-conceptual-payoff)
- [Align the abstract with the manuscript](#align-the-abstract-with-the-manuscript)
- [Run the Nature abstract audit](#run-the-nature-abstract-audit)

## Treat the abstract as the shortest evidence chain

Do not write the abstract as a compressed Introduction or a catalogue of
sections. Compress the entire paper into the shortest chain that makes the
central discovery understandable, credible, and consequential:

`precise problem or gap -> what the study does to resolve it -> main discovery -> decisive support or boundary -> what the discovery establishes -> why it matters`

Draft the abstract after the Introduction question, Results evidence chain,
and Discussion synthesis are stable. The abstract should reveal the paper's
argument, not the chronology of the research process.

## Use a discovery-centred architecture

Use this default move order for a Nature Portfolio research article:

1. known phenomenon or important problem
2. precise unresolved question
3. study design or conceptual move used to answer it
4. main discovery
5. one or two critical supporting findings or boundaries
6. conceptual, technical, or field-level implication

Move rapidly into the present study. Spend only enough background to make the
gap intelligible. The centre of gravity must be `we found X`, not `we evaluated
many models and datasets` or `we propose a framework`.

This move order is rhetorical guidance, not a requirement for six sentences.
Combine moves when needed to satisfy the current target-journal abstract limit.

## Make the gap sharp and brief

Use one sentence, or at most the minimum needed, to join the known phenomenon
to the exact unknown. Prefer:

`X is increasingly used or observed, but whether, why, or under what conditions Y remains unclear.`

Do not spend abstract space proving that the whole field is important,
summarizing several generations of prior work, or rehearsing the Introduction
funnel. Avoid generic gaps such as `existing methods still face challenges`
when the paper addresses a precise source, condition, mechanism, or boundary.

## Keep only answer-enabling method logic

Describe the method at the minimum level needed to understand why the design
can answer the stated question. Include, when central:

- the controlled factor or contrast that identifies the claim
- the perturbation, intervention, or decomposition that tests the proposed
  source or mechanism
- the scope needed to judge generalization
- the theoretical property needed to understand the contribution

Omit learning rates, hardware, routine data splits, implementation modules,
and dataset-by-dataset detail unless one of them defines the discovery or its
boundary. The abstract is not a Methods summary.

## Select one main claim

Choose one central claim and at most one or two supporting claims. Compress the
remaining Results into evidence categories or omit them.

Use this hierarchy:

| Role | Abstract decision |
|---|---|
| Main claim | State explicitly and give it the most space |
| Decisive support | Keep when needed to make the main claim credible |
| Boundary | Keep when it materially changes how the claim must be read |
| Scope credential | Mention briefly only when breadth itself supports the inference |
| Secondary analysis | Omit or reserve for the main text/SI |

Do not give every Results subsection one sentence. Experimental scale is a
credibility cue, not the protagonist: use `across ... settings` only when that
scope is necessary to understand generality or confidence.

## Use numbers by necessity

Nature Portfolio abstracts do not require a numeric result merely to appear
empirical.
Include a number only when it performs one of these functions:

- defines the strength or threshold of the main discovery
- is itself the paper's principal law, prediction, or selection result
- makes a decisive comparison interpretable
- establishes a boundary that qualitative wording would obscure

Omit numbers when the conceptual or mechanistic claim is the contribution and
the number would displace the evidence logic. Comparative wording may be
adequate when the exact effect size is not the headline claim.

If several numbers compete for space, keep the one that most changes the
reader's understanding of the central claim. Do not report sample counts,
benchmarks, models, metrics, and multiple effect sizes simply because they are
available.

## End with the conceptual payoff

Use the final sentence to state what the findings change, enable, connect, or
make predictable. Prefer a bounded field-level payoff over self-evaluation:

- a mechanism or principle becomes identifiable
- a design or architecture choice becomes predictable
- a method becomes applicable to a previously inaccessible regime
- two areas become conceptually connected
- a practical decision gains a quantitative or mechanistic basis

Do not end with `the proposed method achieves superior performance` or a broad
promise unsupported by the tested scope.

## Align the abstract with the manuscript

Treat the four sections as different compressions of the same central claim:

- **Abstract:** the manuscript's shortest claim–evidence–implication chain
- **Introduction:** why the exact question must be asked
- **Results:** the full escalating evidence chain that answers it
- **Discussion:** what the answers mean together

Every abstract claim must map to visible Results evidence. The final implication
must match the Discussion synthesis without exceeding its boundaries. Do not
introduce a claim, mechanism, or application in the abstract that the main text
does not establish.

## Run the Nature abstract audit

Build this compact map before sentence polishing:

| Abstract move | Content | Manuscript support | Keep test |
|---|---|---|---|
| Gap | Exact unresolved question | Introduction | Can it be stated in one sharp sentence? |
| Design | Answer-enabling logic | Methods/Results | Does it explain why the question is answerable? |
| Main discovery | One central claim | Results | Is this the paper's real advance? |
| Support/boundary | One or two decisive findings | Results | Does each materially strengthen or bound the claim? |
| Payoff | What the finding changes | Discussion | Is it important and scope-calibrated? |

Then delete or compress:

- background already implied by the title
- implementation detail that does not explain identification or inference
- experiment inventory presented instead of a discovery
- secondary Results included only for completeness
- numbers that do not define, support, or bound the main claim
- a final sentence that merely says the method performs well

Read the abstract once with all method and dataset names hidden. If the central
discovery and why it matters are no longer clear, the abstract is organized
around implementation rather than insight.
