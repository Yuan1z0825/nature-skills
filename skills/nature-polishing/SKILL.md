---
name: nature-polishing
description: Polish, restructure, or translate academic prose into Nature-leaning English using writing-strategy principles, curated Nature/Nature Communications article patterns, and phrase-level support from Academic Phrasebank. Use whenever the user asks to polish a manuscript paragraph, abstract, introduction, results, discussion, conclusion, title, methods section, or Chinese academic draft for publication-quality English. Also covers LaTeX layout/typesetting (排版) fixes — loose or sparse pages, stranded section headings, figures that don't fill the page or split across pages, "Float too large", multi-panel figure arrangement, and Supplementary Information that looks empty — via references/latex-layout.md. Also trigger on general academic/scientific writing requests even without the word "Nature", including academic writing, scientific writing, SCI/paper writing, English manuscript polishing, language editing, proofreading, and Chinese phrasings such as 学术写作、科研写作、论文润色、写paper、SCI写作、英文论文润色、语言润色、润色、改写、学术英语、英文写作.
version: 6.1.0
author: Yuan1z skill, refactored into static/dynamic layers
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
- `journal` — nature / nat-comms / generic. Default: generic. If the user names a Nature subjournal, treat it as `nature`.

State the detected axis values in one short line to the user before proceeding, so they can correct you cheaply.

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

### 5. Reach for references only when needed

The files under `references/` are deep references, not defaults. Open them on demand per the `references.on_demand` table in the manifest, for example when the user explicitly asks for phrasebank-style alternatives or a stricter style audit.

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
