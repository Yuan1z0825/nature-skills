---
name: nature-paper-card
description: "Build a structured deep-reading Paper Card for one scientific paper, analysing methods, experiment-to-claim evidence, limitations, and research ideas. Use for 论文精读卡、方法拆解、证据链分析; not full-paper bilingual translation or formal peer review."
---

# Nature Paper Card - Router

Use this skill to turn one paper into an evidence-grounded research card, not a translated abstract, generic summary, reviewer report, or publication article.

The skill uses:

- a static core under `static/core/` for principles, workflow, and the fixed output contract;
- one paper-type fragment under `static/fragments/paper_type/`;
- on-demand references for evidence labels, the exact card schema, and research-idea checks.

## Routing protocol

Follow these steps every time.

### 1. Load the manifest and core layer

Read [manifest.yaml](manifest.yaml), then read every file under `always_load`. Do not generate the card from this router alone.

### 2. Establish the source boundary

Identify which material is available:

- full paper with figures and tables;
- paper text without reliable layout;
- abstract or metadata only;
- an existing `nature-reader` artifact with stable source IDs.

Prefer an existing `nature-reader` artifact when supplied. Do not repeat full bilingual translation or figure extraction. If only partial material is available, create a visibly partial card and mark every unsupported section `Not assessable from supplied material`.

For a PDF or `nature-reader` source-map JSON, the bundled script is mandatory.

1. Resolve `SKILL_DIR` as the directory containing this loaded `SKILL.md`.
2. Verify `SKILL_DIR/scripts/prepare_paper.py` exists.
3. Run exactly the bundled script by its resolved path:

```text
python "SKILL_DIR/scripts/prepare_paper.py" INPUT \
  --output WORKDIR/source_bundle.json
```

Add `--render-dir WORKDIR/rendered-pages` when visual page review is needed. Inspect the script exit code and the bundle validation block before drafting.

For source-map input, also inspect `locator_summary` and `unlocated_blocks`. Only records under `pages` have verified positive PDF page locators. Missing or invalid page locators remain in `unlocated_blocks` with an explicit status and must be cited structurally, never as page 1.

Never write inline Python, a temporary extraction script, or a replacement script during a Paper Card run. Never patch the bundled scripts during a normal Paper Card run. Modify these scripts only when the user explicitly asks to develop, debug, or improve the skill itself.

Use this fixed locator state machine:

- `page-grounded`: the bundled script succeeds and validates reliable PDF page indices. Use PDF page plus structural locators. Printed page labels are optional metadata.
- `structure-grounded`: page extraction is unreliable, but reliable sections, figures, tables, equations, source blocks, or full text remain available. Do not emit page-number citations.
- `source-limited`: only an abstract, metadata, or user-provided excerpt is reliable. Do not emit page-number citations or infer unseen evidence.

If preparation fails, record the failure. Prefer an existing `nature-reader` source map or the environment PDF/OCR capability, but do not create a replacement script. Then enter the strongest supported fallback mode.

### 3. Classify the paper type

Use the manifest to choose one primary `paper_type` and, only for a genuinely hybrid paper, one secondary contribution lens:

- `methods`
- `discovery`
- `resource`
- `clinical`
- `materials`
- `review`

Load the primary fragment and no more than one secondary fragment. Classify by the paper's argument and evidence structure, not merely its discipline. State both selections before analysis. For example, an algorithm paper that also introduces a substantial dataset may use `methods` as the primary lens and `resource` as the secondary lens.

### 4. Build the evidence base before drafting

Build an internal evidence inventory before drafting. At minimum, enumerate:

- bibliographic metadata and access status;
- research question and claimed contribution;
- method components, assumptions, and data flow;
- every main figure, table, and essential equation with its argumentative role;
- experiments, baselines, metrics, ablations, and reported results;
- author-stated limitations;
- stable source pointers to pages, sections, equations, figures, tables, or `nature-reader` block IDs.

Then build a compact claim-evidence matrix linking each central claim to the evidence that supports it and to any unresolved gap.

Use external search only for Section 04, Section 15, bibliographic verification, or an explicit novelty check. Never present the paper's own related-work narrative as independently verified field history. Record whether the context mode is `paper-only`, `targeted external check`, or `externally verified`.

### 5. Generate the fixed Sections 01-16 Paper Card

Apply, in order:

1. core principles;
2. the selected paper-type fragment;
3. core workflow;
4. output contract.

Read [references/evidence-and-provenance.md](references/evidence-and-provenance.md) before making analytical or externally verified claims. Read [references/card-schema.md](references/card-schema.md) when drafting the final Markdown. Read [references/research-idea-gates.md](references/research-idea-gates.md) before writing Section 16.

Write a real Markdown artifact, defaulting to `paper-card.md`. Keep all 16 numbered sections in order, but write `Not applicable` or `Not assessable` instead of inventing content.

Match the user's language by default. The skill source and schema remain English, but localize the Paper Card headings and prose when the user writes in another language. Preserve canonical technical terms and formulas.

### 6. Run groundedness QA

Before delivery, resolve the bundled auditor from `SKILL_DIR`. In `page-grounded` mode, run:

```text
python "SKILL_DIR/scripts/audit_paper_card.py" \
  --card WORKDIR/paper-card.md \
  --bundle WORKDIR/source_bundle.json \
  --locator-mode page-grounded \
  --report WORKDIR/audit-report.json
```

In either fallback mode, run the same auditor without a bundle:

```text
python "SKILL_DIR/scripts/audit_paper_card.py" \
  --card WORKDIR/paper-card.md \
  --locator-mode structure-grounded-or-source-limited \
  --report WORKDIR/audit-report.json
```

Replace the last value with the actual canonical mode. Treat audit errors as blockers. Review warnings with scientific judgment rather than suppressing them mechanically.

Also verify:

- numerical results match the source;
- the evidence inventory covers every main figure and table;
- every major method, result, boundary, and limitation has a source pointer;
- PDF page pointers distinguish PDF page index from printed page labels;
- author statements are separated from Agent analysis;
- external field-history claims have external citations or are marked unverified;
- proposed ideas are hypotheses, not novelty claims;
- Sections 17 and 18 do not exist;
- no academic-English collection, comprehension quiz, or public-article draft was added.

If the auditor itself cannot run, state that failure and manually apply only its documented checks. Do not write a substitute auditor.

## Script red lines

- Do not resolve bundled scripts relative to the user's current working directory.
- Do not write or execute inline Python as a substitute for either bundled script.
- Do not create `extract_pdf.py`, `parse_paper.py`, or another one-off replacement.
- Do not patch skill code during a normal Paper Card generation request.
- Do not fabricate page numbers when preparation fails.
- Do not remove all grounding in fallback mode; use structural locators or explicit source-scope locators.

## Relationship to adjacent skills

- Use `nature-reader` for full-text bilingual reading artifacts, extraction, and stable source maps.
- Use `nature-academic-search` when external literature is needed to verify field history or knowledge connections.
- Use `nature-reviewer` for formal reviewer-style manuscript assessment.
- Use `nature-literature-pipeline` for batch discovery and lightweight monitoring notes.
- Use `nature-paper2ppt` when the requested end product is a presentation.

Do not silently switch the requested Paper Card into any of these outputs.
