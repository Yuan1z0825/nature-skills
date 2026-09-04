---
name: nature-polishing
description: Polish, restructure, or translate academic prose into concise Nature-leaning English while preserving facts, evidence boundaries, terminology, and citation intent. Use for manuscript paragraphs, abstracts, introductions, Results, discussions, conclusions, titles, Methods, Chinese drafts, proofreading, language editing, and general academic or scientific writing. Also use to shorten bloated Results, allocate evidence across main text, captions, and Supplementary Information, prevent reviewer-driven revision accretion, reduce repeated statistics or claims, and apply paragraph-necessity checks. Covers LaTeX layout or typesetting fixes such as sparse pages, stranded headings, oversized or split figures, float errors, multi-panel arrangement, and sparse Supplementary Information via references/latex-layout.md. Trigger on 学术写作、科研写作、论文润色、SCI写作、英文论文润色、语言润色、润色、改写、学术英语、排版.
---

# Nature-Style Academic Polishing — Router

This skill is split into two layers:

- A **static layer** under `static/` that holds versioned, reusable content fragments (core principles, paper-type playbooks, per-section guidance, language-specific rules, per-journal style).
- A **dynamic layer** (this file plus `manifest.yaml`) that detects the request's axes and loads only the fragments needed for the current job.

Do not try to apply the polishing logic from memory or from this router. Always load fragments from disk as described below.

## Routing protocol

Follow these five steps every time the skill is invoked.

### 1. Load the manifest and the core layer

Read [manifest.yaml](manifest.yaml). It declares the axes (`paper_type`, `section`, `language`, `journal`), the allowed values, and the file paths each value maps to.

Also read every file listed under `always_load`. These hold the default stance, failure-mode diagnosis, ethics, and output format that apply to every polish job.

### 2. Detect the axis values for this request

For each axis in the manifest, decide the value using the manifest's `detect:` hint and the user's input:

- `paper_type` — research / methods / hypothesis / algorithmic / review. Default: research.
- `section` — abstract / intro / results / discussion / conclusion / title / methods. May be multiple. Ask the user if it is ambiguous and matters for the polish.
- `language` — en or zh-to-en. Detect from the draft itself.
- `journal` — nature / nat-comms / nat-mach-intell / generic. Default:
  generic. Use `nature` only for flagship Nature, `nat-comms` for Nature
  Communications and `nat-mach-intell` for Nature Machine Intelligence (NMI).
  Do not route another Nature Portfolio title through flagship Nature rules.

State the detected axis values in one short line to the user before proceeding, so they can correct you cheaply. This is a progress update, not an approval gate; continue unless a necessary decision remains unresolved.

### 3. Load the matching fragments

For each axis value, Read the file mapped in the manifest. Skip the `section` axis only if the user has supplied free-floating prose with no section context.

Do **not** read every fragment in `static/`. Load only what step 2 selected.

### 4. Polish using the loaded material

Apply the loaded fragments in this priority order, matching the `paper type -> section job -> paragraph logic -> claim/evidence/boundary -> sentence polish` rule from `core/failure-modes.md`:

1. Paper-type playbook (architecture, writing order).
2. Section-specific job and failure modes.
3. Journal-specific framing and constraints.
4. Language-specific sentence and paragraph rules (apply last).
5. Core stance and ethics throughout.

If a paragraph's structural problem cannot be fixed without inventing content, flag it instead of papering over it.

For Results, full-main-text compression, main-versus-SI allocation, or prose
added during revision, load `../nature-shared/core/main-text-discipline.md`
before sentence polishing. Classify each result, retain the shortest sufficient
evidence chain, and require every addition to trigger a deletion or replacement
check across the affected paragraph.

For flagship Nature, Nature Communications, Nature Machine Intelligence, or
another Nature Portfolio title, load the matching shared Nature-style corpus
guidance:

- Results or Discussion →
  `../nature-shared/core/nature-results-discussion.md`
- Introduction or whole-manuscript narrative →
  `../nature-shared/core/nature-introduction.md`
- Abstract → `../nature-shared/core/nature-abstract.md`

Preserve claim escalation, the fast question funnel, Introduction–Results
alignment, discovery-centred abstract compression, evidence-bound local
interpretation, and cross-Results synthesis. These defaults were initially
distilled from published NMI papers; treat them as corpus-derived guidance, not
official policy, and obey the target journal's current rules when they differ.

For any Discussion polish or restructuring job, also load
`../nature-shared/core/discussion-argument-language.md`. Use its function labels
to remove Results replay, repair the movement from specific findings to bounded
implications, calibrate modal and reporting verbs to evidence strength, and make
limitations and future work resolve named claim boundaries. Treat it as general
writing guidance, not journal policy.

### 5. Reach for references only when needed

The files under `references/` are deep references, not defaults. Open them on demand per the `references.on_demand` table in the manifest, for example when the user explicitly asks for phrasebank-style alternatives or a stricter style audit.

When the target is Nature Machine Intelligence and exact limits, availability
sections, conference-extension disclosure or production checks affect the
revision, load
`../nature-shared/journal-formats/nature-machine-intelligence.md`.

When the job is a whole manuscript rather than a passage, or the text has already been through more than one round of editing, also load `../nature-shared/core/consistency-sweep.md`. Polishing passage by passage cannot see accumulated drift: one experimental factor under several names, the same quantity in two units, a metric at two precisions, or a superlative the paper's own table contradicts. Sweep for those before working on sentences, and repeat the sweep until a pass finds nothing new.

**Layout/typesetting (排版) requests are different.** If the user asks to fix
*placement* rather than wording — loose/sparse pages, stranded headings, figures
that don't fill the page or split across pages, "Float too large", multi-panel
arrangement, sparse Supplementary Information — skip the prose axes (paper_type,
section, language, journal) and load `references/latex-layout.md` directly. That
file is self-contained: it carries the diagnosis workflow (render → contact-sheet →
read the log), the float-glue and `[H]`/`\clearpage`/`placeins` patterns, and the
"regenerate wide figures taller at the source" rule. Always compile and visually
inspect rendered pages before and after — never judge layout from the `.tex` alone.

## Why this split

- The static layer is versioned and reviewable. Adding a new journal style or paper type is one new file plus one manifest line.
- The dynamic layer keeps each invocation cheap: only the fragments relevant to this draft enter context, instead of the full 1000-line monolith.
- The router itself is short on purpose. Update fragments, not this file, when adding scope.
