# Skill scope smoke evaluation

## Scope and method

On 2026-09-06, five isolated agent contexts exercised six short requests against the edited
local skills. The writing context received a second request as an intentional follow-up.
Agents received the skill path, raw request, and supplied source material, without expected
answers or the implementation rationale. They could read instructions but could not modify
repository files or use external services. All examples below are synthetic.

These observations establish only the behavior of these small, explicitly invoked tasks.
They are not an automatic skill-selection benchmark, a before/after comparison, a cross-model
evaluation, or validation of complete manuscripts, readers, or slide decks. Static checks and
runtime tests are separate from these observations.

## Requests and observed outputs

### Paper question

Skill: `nature-reader`.

Request: explain Figure 2b in two or three Chinese sentences. The supplied Results excerpt and
caption described fluorescence intensity means of 8.2 AU (treated) and 6.1 AU (control), with
12 independent biological samples per group, no inferential test, and no established mechanism.

Observed: three Chinese sentences cited the supplied Results section and caption, preserved the
sample counts and means, and described the 2.1 AU difference without claiming significance or a
mechanism. No reader-generation deliverable or fabricated source-map IDs appeared in the answer.

### Local reviewer reply

Skill: `nature-response`.

Request: make the following reply more polite and concise, returning only the reply.
Reviewer: "Please clarify the software version used."
Draft: "The reviewer missed this. We used version 2.3.1."

Observed output:

> Thank you for requesting clarification. We used software version 2.3.1.

No Major/Minor question, invented manuscript revision, tracker, or package-readiness claim.

### Descriptive Results paragraph

Skill: `nature-writing`.

Request: draft one short English Results paragraph from the same sample counts and means as
the paper-question example, explicitly descriptive with no inferential test or mechanism.

Observed output:

> The mean signal was 8.2 AU in the treated group and 6.1 AU in the control group, with 12 independent biological samples per group. This comparison was descriptive; no inferential test was performed.

The paragraph was delivered without an outline-approval or manuscript-intake question.

### Explicit outline approval

Skill: `nature-writing`, continuing the preceding case.

Request: plan a Discussion from those findings, give an outline first, and wait for approval
before prose; the evidence is descriptive and provides no mechanism.

Observed: an outline covered the central observation, interpretation boundaries, and a focused
next step. It stated that significance and variability were not established by the supplied
means, omitted unsupported literature positioning, and explicitly waited for outline approval.
No full Discussion prose was drafted.

### Data Availability grammar edit

Skill: `nature-data`.

Request: correct the grammar and return only the sentence:
"All data supporting this study is included in this article and its Supplementary Information."

Observed output:

> All data supporting this study are included in this article and its Supplementary Information.

The answer did not request a study-wide data inventory or invent repository identifiers.

### Offline citation conversion

Skill: `nature-academic-search`.

Request: return RIS text only, without online lookup or verification, for a supplied journal
article by Jane Doe and Ming Li, "Synthetic example of sample imaging", Example Research
Journal, 2025, volume 12, issue 3, pages 21-29, with no DOI supplied.

Observed: one RIS record retained author order and all supplied fields, split the page range
into `SP` and `EP`, and omitted a DOI rather than fabricating one. The answer contained no API
setup request or claim of online verification.

## Follow-up coverage

Long-document quality, rendered slide revisions, implicit routing among overlapping skills,
real publisher retrieval, and cross-model behavior still require dedicated evaluation.
Existing artifact-completeness and evidence-integrity requirements remain in place for those
workflows; these small cases do not replace their checks.
