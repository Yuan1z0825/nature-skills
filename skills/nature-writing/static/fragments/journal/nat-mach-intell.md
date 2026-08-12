# Journal: Nature Machine Intelligence — writing

## Read the shared contract first

Open
`../../../../nature-shared/journal-formats/nature-machine-intelligence.md`.
It is the canonical, stage-aware source for NMI content types, word/display
limits, initial files, code/data policy and accepted-in-principle production
rules.

The notes below are the **drafting action layer** on top of those facts.

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
limit or separate per-legend word limit. Do not borrow those numbers from
flagship Nature or Nature Communications.
