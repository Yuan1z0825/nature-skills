# AI-Assisted Graphical Abstract Workflow

Use this reference whenever a task involves planning, generating, revising, or
auditing a graphical abstract with AI assistance. Apply it before any
provider-specific image-generation instructions.

## Contents

- [Authority boundary and policy gate](#authority-boundary-and-policy-gate)
- [1. Define the communication target](#1-define-the-communication-target)
- [2. Build a visual brief](#2-build-a-visual-brief)
- [3. Assign AI a bounded role](#3-assign-ai-a-bounded-role)
- [4. Write the prompt as a figure contract](#4-write-the-prompt-as-a-figure-contract)
- [5. Run human scientific and publication QA](#5-run-human-scientific-and-publication-qa)
- [Sources and status](#sources-and-status)

## Authority boundary and policy gate

- Treat Ananya Thakur's 22 July 2026 *Nature* Careers column as practitioner
  guidance, not as a Nature Portfolio submission policy or blanket permission
  to publish AI-generated artwork.
- Before generating a submission candidate, verify the target journal's current
  graphical-abstract, artificial-intelligence, image-integrity, copyright, and
  disclosure rules on official pages. Record the journal, URL, and access date.
- For a Nature Portfolio target, apply the current risk-assessment framework:
  assistive use can support expression or organization; interpretive or
  generative use requires human oversight, verification, and transparent
  disclosure; opaque, unverifiable, confidentiality-breaching, or
  judgement-replacing use is not permitted. A journal may impose stricter
  rules.
- If journal clearance is unknown, label the output **internal design draft —
  submission eligibility unverified**. Do not call it submission-ready.
- Keep two decisions separate: whether a draft is useful internally and whether
  the final asset is eligible for submission.

## 1. Define the communication target

Before choosing a tool or visual style, write down:

1. the single sentence the reader should remember
2. the figure type: mechanism, process, experimental setup, workflow,
   comparison, timeline, cycle, or branching decision
3. the intended audience and its expected vocabulary
4. the evidence boundary: what the study demonstrates, what is contextual, and
   what must not be implied
5. the details to omit because they do not support the central message

Do not ask an image model to summarize an entire manuscript into a final image
without this brief.

## 2. Build a visual brief

- Inspect graphical abstracts from comparable papers for information density,
  reading order, and composition. Learn the visual grammar; do not copy
  protected artwork, icons, or distinctive layouts.
- Choose an explicit reading path: left-to-right, top-to-bottom, cycle, split
  comparison, or fork. Use arrows and grouping only when they clarify that path.
- Use a limited, consistent, high-contrast, color-accessible palette. Assign
  color by scientific meaning, not decoration, and do not rely on color alone.
- Reserve the strongest accent for the central causal step or principal result.
  Keep labels short and plan their placement before generating artwork.
- Prefer one representative pathway over an exhaustive interaction network when
  the fuller network would obscure the central claim. Preserve necessary caveats
  in the legend or manuscript.

## 3. Assign AI a bounded role

Use AI to assist with tasks such as:

- distilling author-provided claims into candidate one-sentence messages
- comparing audience-specific levels of terminology and detail
- proposing several compositions or label placements
- checking palette contrast and color accessibility
- turning an author-owned sketch into a draft layout or vectorization plan
- brainstorming pictorial metaphors that will be scientifically reviewed

Do not let AI invent measurements, mechanisms, structures, clinical effects,
citations, labels, or evidence. Do not upload confidential manuscripts, peer
review material, sensitive data, or unpublished images to an unsecured or public
AI service without explicit authorization.

## 4. Write the prompt as a figure contract

Include these fields in a provider-neutral prompt:

- **Purpose and audience**
- **One-sentence message**
- **Figure type and reading order**
- **Required entities and relationships**
- **Evidence boundary and forbidden implications**
- **Composition and focal element**
- **Palette, contrast, and accessibility constraints**
- **Exact short labels**
- **Elements to exclude**, including fabricated numbers, logos, and decorative
  scientific objects
- **Output role**, explicitly stating `concept draft` when generative AI is used

Generate layout alternatives before polishing a single composition. Correct
scientific structure first, then typography, color, and visual finish. Redraw
critical text, arrows, chemical structures, and quantitative marks with
deterministic or editable tools whenever possible.

## 5. Run human scientific and publication QA

Before delivery, check every visual element against the manuscript and source
data:

- scientific entities, directions, causal links, scale, anatomy, and chronology
- all labels, abbreviations, spelling, units, and symbol definitions
- absence of invented data, unsupported effects, misleading realism, or
  decorative evidence
- readable hierarchy at final size and a color-blindness-safe reading path
- originality, licenses, permissions, attribution, and resemblance to source art
- target-journal eligibility, disclosure wording, and figure-legend treatment

Retain a provenance bundle containing the prompt, model/provider and version,
generation date, reference-image rights, generated candidates, selected output,
and a log of manual corrections. Human authors remain accountable for the final
asset.

## Sources and status

- Practitioner workflow: Ananya Thakur, “How to use AI to make a graphical
  abstract in minutes,” *Nature* Careers, 22 July 2026,
  <https://doi.org/10.1038/d41586-026-02072-9>.
- Governing portfolio policy: Nature Portfolio, “Artificial Intelligence (AI),”
  <https://www.nature.com/nature-portfolio/editorial-policies/ai>, verified
  15 August 2026. Recheck before each submission because the policy is reviewed
  periodically.
