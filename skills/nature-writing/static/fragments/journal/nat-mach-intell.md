# Journal: Nature Machine Intelligence — writing

## Read the shared contract first

Open
`../../../../nature-shared/journal-formats/nature-machine-intelligence.md`.
It is the canonical, stage-aware source for NMI content types, word/display
limits, initial files, code/data policy and accepted-in-principle production
rules.

The notes below are the **drafting action layer** on top of those facts.

For Results or Discussion drafting, also open
`../../../../nature-shared/core/nature-results-discussion.md`. It records
corpus-derived Nature-style writing patterns, not official submission
requirements.

For Introduction drafting, also open
`../../../../nature-shared/core/nature-introduction.md`. It records
corpus-derived Nature-style writing patterns, not official submission
requirements.

For abstract drafting, also open
`../../../../nature-shared/core/nature-abstract.md`. It records corpus-derived
Nature-style writing patterns, not official submission requirements.

## Audience and fit

Write for readers across machine learning, robotics, AI applications and the
scientific or societal domain affected by the work. The paper must still be
technically exact, but the title, abstract and opening should explain the
question and consequence without assuming one benchmark community's jargon.

Do not equate a larger model, more compute, a small benchmark gain or an extra
dataset with NMI-level significance. State what scientific, technical or
societal understanding changes and bound transfer claims to the evaluated
settings.

## Article drafting contract

- Budget no more than 3,500 words for Introduction + Results + Discussion;
  Methods, abstract, references and legends are outside this count.
- Keep the unreferenced abstract at no more than 150 words.
- Use at most six figures and tables combined in the main display budget.
- Plan around about 50 references unless the editor permits more.
- Use an unheaded introduction followed by Results, Discussion and Methods.
- Results and Methods may use topical subheadings; Discussion should not.

Suggested starting budget for an Article:

| Section | Suggested budget |
|---|---:|
| Introduction | 550–700 words |
| Results | 2,100–2,350 words |
| Discussion | 500–750 words |
| **Counted main text** | **up to 3,500 words** |

Methods has no fixed public numeric limit. Keep it concise, complete and
reproducible instead of hiding essential details in Supplementary Information.

## Machine-intelligence evidence gates

Before strong novelty, generality or deployment language, ask for:

- genuinely independent test data and leakage controls
- baseline parity in data, supervision, tuning budget and compute
- uncertainty, repeated runs and ablations for the claimed mechanism
- robustness, failure cases and out-of-distribution limits
- compute, hardware, software and environment detail sufficient to reproduce
  the result
- population, setting, human factors and prospective validation for real-world
  or societal claims

New code central to the conclusions requires a separate Code availability
section, reviewer access and the Software Submission Checklist. Plan these
artifacts while drafting Methods rather than after acceptance.

## Results–Discussion action

- Build Results as claim escalation: each subsection should answer a new
  scientific question and add an independent inference.
- Allow a bounded local explanation in Results when it directly resolves the
  experiment just reported; reserve cross-result, literature, and broader
  implications for Discussion.
- Keep robustness in the main text when it establishes or materially bounds a
  claim; route reassurance-only checks to SI.
- Let Discussion briefly anchor the central finding, then synthesize rather
  than replay the Results evidence and statistics.

## Introduction action

- Narrow quickly from the important problem to a specific unresolved
  phenomenon, condition, mechanism, or contradiction.
- State the gap as an exact unknown; do not define it as the absence of the
  author's method.
- Organize literature to construct the known–unknown transition, not to display
  coverage.
- Let the study's answer emerge only after the question is motivated, and use
  the closing paragraph as a compact roadmap of how the study answers it.
- Require every central Introduction question to map to a Results answer and
  every central Results claim to have a motivated question.

## Abstract action

- Treat the abstract as the manuscript's shortest evidence chain, not a
  compressed Introduction or experiment inventory.
- State one sharp gap, the minimum design logic needed to answer it, one main
  discovery, and no more than one or two decisive supports or boundaries.
- Include a number only when it defines, supports, or materially bounds the
  central claim; a decorative numeric result is not required.
- End with what the finding changes or enables within the tested scope, not
  with a claim that the method performs well.

## Submission-package actions

- Treat the cover letter as part of the initial package. State importance,
  NMI readership fit, related manuscripts and prior editor discussions.
- If the manuscript extends a conference paper, identify the substantial new
  results, methodology, analysis, conclusions or implications explicitly.
- For double-anonymized review, move author contact information to the cover
  letter and audit repositories, self-citations, acknowledgements and metadata.
- Do not offer a presubmission enquiry; NMI does not consider them.

## Numeric non-invention rule

The current public NMI pages do not state a fixed title limit, Methods word
limit or current separate per-legend word limit. Do not borrow those numbers
from flagship Nature or Nature Communications. For figure legends, retain the
official 2018 NMI below-300-word instruction only as a historical advisory:
count the complete legend rather than each panel, aim for 150–250 English words,
and follow any newer editor or submission-system instruction.
