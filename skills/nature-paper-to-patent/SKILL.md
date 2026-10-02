---
name: nature-paper-to-patent
description: "Turn research papers or inventor materials into evidence-grounded Chinese invention patent drafts and technical disclosures. Use for 技术交底书、专利撰写、现有技术对比 and Chinese DOCX patent packages; not general manuscript writing."
---

# Paper to Chinese Patent

Use this file as the router for the patent-drafting workflow. Do not draft the
application directly from the paper abstract or contribution list.

## 1. Load the workflow

Read `manifest.yaml`, then read every file under `always_load`.

Detect these axes from the user's files and request:

- `source_format`: selectable PDF, scanned PDF, pasted text, or mixed project;
- `task_mode`: full draft, claim set, disclosure analysis, technical
  disclosure, disclosure iteration, or paper-patent audit;
- `invention_type`: algorithm/software, apparatus/system, process/material, or mixed.

State the detected values in one short line. Load only the matching fragments
declared in the manifest. Load detailed references only when their condition
applies.

## 2. Preserve source grounding

Create stable source IDs before drafting:

- `P001...` for paper text blocks;
- `E001...` for equations;
- `F001...` for source figures;
- `C001...` for source-code or supplementary evidence.

Every material feature in a formal claim must map to one or more source IDs.
Use only `explicit`, `inherent`, `needs-confirmation`, or `unsupported` as
support states. Exclude `unsupported` features from formal claims.

Never infer inventorship, ownership, unpublished implementation details,
publication dates, prior-art conclusions, or legal sufficiency. Use
`[TO CONFIRM: specific question]` outside formal claims when facts are missing.

## 3. Draft through stage gates

For `full-draft`, `claim-set`, `disclosure-analysis`, and `paper-patent-audit`,
complete the stages in `static/core/workflow.md` in order. Persist the
intermediate artifacts specified there. Do not move to formal claims until the
source map, terminology ledger, inventories, evidence ledger, and invention
concept pass their gates.

For `technical-disclosure`, follow the ordered prompt references in
`static/fragments/task/technical-disclosure.md`. For `disclosure-iteration`,
follow `static/fragments/task/disclosure-iteration.md` and preserve the prior
draft instead of restarting the formal application workflow.

For a full application, draft claims first, then align the specification,
figures, embodiments, and abstract to the claim terminology and step order.

## 4. Produce Chinese formal documents

Agent-facing analysis may use the user's preferred language. Produce formal
Chinese patent deliverables in Chinese when the task is a formal application
package:

- 权利要求书;
- 说明书;
- 说明书摘要;
- 摘要附图;
- figure labels and descriptions.

For `technical-disclosure` and `disclosure-iteration`, produce the Chinese
technical disclosure (`技术交底书`) as timestamped Markdown plus matching DOCX,
with Mermaid system/process diagrams rendered through `scripts/disclosure/`.

For algorithmic inventions, retain source-supported core formulas, define every
symbol, explain each formula's technical operation, and render formulas as
native editable Office Math in DOCX. Do not use plain LaTeX strings as the
visible formula.

Generate the main flowchart from the ordered steps of the principal method
claim. Its final node must name the concrete domain output, such as a defect
detection result, target pose, state estimate, or control instruction. Reuse
the same main figure as the abstract figure and a specification figure.

## 5. Validate before delivery

For formal application packages, populate the structured draft described in
`references/draft-schema.md`, then run:

```bash
python scripts/validate_patent_draft.py draft.json
python scripts/build_patent_package.py draft.json --output-dir outputs --prefix patent
```

Resolve all validation `ERROR` findings. Review every `WARNING` against the
source. Label the result `incomplete draft` when a required quality threshold
in `static/core/output-contract.md` is not met.

For technical disclosures, run the internal checks in
`references/disclosure/disclosure_self_check.md`, render Mermaid/Word outputs
with `scripts/disclosure/mermaid_render.py`, and resolve formula, parameter,
prior-art URL, and chapter-consistency issues before delivery.

The generated package is a drafting aid for inventor and patent-professional
review, not a patentability opinion, infringement opinion, or filing guarantee.
