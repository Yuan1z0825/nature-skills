---
name: nature-writing
description: Draft, restructure, or plan Nature-style manuscript sections and initial-submission materials from author-provided claims, results, figures, notes, or Chinese drafts. Use for abstracts, introductions, related work, methods, Results or experiments, discussions, conclusions, titles, full manuscript arguments, and first-submission packages such as cover letters, title pages, highlights, author contributions, availability or declaration text, and reviewer suggestions. Also use to classify Results evidence, decide what belongs in main text, captions, Methods or source data, or Supplementary Information, compress Results to the shortest sufficient evidence chain, prevent revision accretion, and audit paragraph necessity or claim repetition. Trigger on drafting a paper or section, structuring a manuscript, academic writing, first submission, 投稿材料、首次投稿、投稿信、标题页、亮点、作者贡献、数据可用性声明、推荐审稿人.
---

# Nature-Style Scientific Writing — Router

This skill is split into two layers:

- A **static layer** under `static/` that holds versioned, reusable content fragments (core stance + workflow, paper-type playbooks, per-section drafting guidance, initial-submission guidance, language-specific rules, per-journal style).
- A **dynamic layer** (this file plus `manifest.yaml`) that detects the request's axes and loads only the fragments needed for the current job.

Do not try to apply the drafting logic from memory or from this router. Always load fragments from disk as described below.

## Routing protocol

Follow these five steps every time the skill is invoked.

### 1. Load the manifest and the core layer

Read [manifest.yaml](manifest.yaml). It declares the axes (`task`, `paper_type`, `section`, `language`, `journal`), the allowed values, and the file paths each value maps to.

Also read every file listed under `always_load`. These hold the default stance, writing workflow, and output format that apply to every drafting job.

### 2. Detect the axis values for this request

For each axis in the manifest, decide the value using the manifest's `detect:` hint and the user's input:

- `task` — manuscript / submission-package. Use `submission-package` for first-submission materials, never for revision correspondence.
- `paper_type` — research / methods / hypothesis / algorithmic / review. Default: research.
- `section` — abstract / intro / related-work / method / experiments / discussion / conclusion / title. May be multiple. Ask the user if it is ambiguous and matters for the draft.
- `language` — en or zh-to-en. Detect from the user's notes themselves.
- `journal` — nature / nature-family / nat-comms / nat-mach-intell / generic.
  Default: generic. Use `nature` only for the flagship journal Nature,
  `nat-comms` for Nature Communications, `nat-mach-intell` for Nature Machine
  Intelligence (NMI), and `nature-family` for other Nature Portfolio titles or
  an unspecified Nature-family request.

State the detected axis values in one short line to the user before drafting, so they can correct you cheaply.

### 3. Load the matching fragments

For each axis value, Read the file mapped in the manifest. Skip the `section` axis when the task is `submission-package` or when the user explicitly asks for a free-floating argument paragraph with no section context.

Do **not** read every fragment in `static/`. Load only what step 2 selected.

### 4. Draft using the loaded material

Apply the loaded fragments in this priority order:

1. Core stance + intake (`core/stance.md`) — surface missing claim / evidence / boundary before drafting.
2. Paper-type playbook — argument chain, drafting order.
3. Section-specific drafting rules and structure.
4. Task-specific submission rules when `task=submission-package`.
5. Journal-specific framing and constraints.
6. Language-specific sentence and paragraph rules (apply last).

For `task=manuscript`, run the workflow in `core/workflow.md` end-to-end. Do not skip planning just because the user asked for prose immediately.

When drafting or restructuring Results, or compressing a full manuscript's main
text, also load `../nature-shared/core/main-text-discipline.md` before building
the paragraph map. Classify every result by function, allocate it across main
text, captions, Methods/source data, and SI, then draft the shortest sufficient
evidence chain. Do not equate a complete analysis record with a complete main
text.

For `task=submission-package`, follow `static/fragments/task/submission-package.md` and `references/submission-package.md` instead. Build the deliverable matrix and readiness audit; do not force manuscript paragraph architecture onto administrative submission materials.

If essential evidence or boundary is missing, write a placeholder and list it under `Assumptions or missing inputs:` instead of inventing content.

### 5. Reach for references only when needed

The files under `references/` are deep references and the example library, not defaults. Open them on demand per the `references.on_demand` table in the manifest. Typical triggers:

- The user asks for a concrete example or template → `references/examples/index.md`.
- A section's draft has structural problems that the section fragment alone does not explain → the matching `references/<section>.md`.
- The user needs a broad-audience `Nature` abstract opening or asks about a `summary paragraph` → `references/nature-summary-paragraph.md`.
- The user asks "does this paragraph flow?" → `references/paragraph-flow.md`.
- The user asks for a self-review or rejection-risk audit → `references/paper-review.md`.
- The user asks what belongs in the main text, captions, or SI; wants a shorter
  Results section; or is adding reviewer-driven explanation →
  `../nature-shared/core/main-text-discipline.md`.
- The user requests a complete first-submission package, templates, or a submission-readiness audit → `references/submission-package.md`.
- The target is the flagship journal Nature and exact submission or formatting
  requirements matter → `../nature-shared/journal-formats/nature.md`.
- The target is Nature Machine Intelligence and exact content-type, submission,
  data/code or production requirements matter →
  `../nature-shared/journal-formats/nature-machine-intelligence.md`.
- The work involves regulated or specialist research compliance →
  `../nature-shared/core/research-compliance.md`.

## Submission boundary

- `nature-writing` owns **initial submission** materials prepared before peer review.
- `nature-response` owns revision cover letters, rebuttals, point-by-point responses, marked manuscripts, appeals, and other post-decision correspondence.
- Route graphical abstracts and TOC graphics to `nature-figure`; route simulated pre-submission peer review to `nature-reviewer`.

## Why this split

- The static layer is versioned and reviewable. Adding a new journal style, paper type, or section is one new file plus one manifest line.
- The dynamic layer keeps each invocation cheap: only the fragments relevant to this draft enter context, instead of the full multi-thousand-line reference set.
- The router itself is short on purpose. Update fragments, not this file, when adding scope.
- This structure mirrors `nature-polishing` so shared content can later be lifted into a `nature-shared/` layer used by both skills.
