---
name: nature-image2ppt
description: Convert slide images, screenshots, scanned PDFs, and image-only PPT/PPTX files into high-fidelity object-level editable PowerPoint, including semantic-region mixed reconstruction, measured flowcharts and knowledge graphs, native circle nodes and connectors, single-object thin and filled arrows, speaker-note preservation, and rendered QA. Use for 图片转可编辑PPT、截图还原PPT、扫描PDF恢复、图片型PPTX转换、流程图/知识图谱/复合图形/箭头重建; not for authoring a new deck from notes.
---

# Nature Image2PPT

Use this directory as the complete runtime. Run deterministic actions only through:

```bash
python <image2ppt-root>/cli/image2ppt/cli.py <command> ...
```

Use Python 3.10 or later with `requirements.txt` installed. When a dedicated
environment exists, substitute `<image2ppt-root>/.venv/bin/python` on macOS/Linux
or `<image2ppt-root>/.venv/Scripts/python.exe` on Windows for every `python`
command below. Do not continue after a failed `doctor`; install only the reported
missing dependency, then rerun it.

Do not discover or invoke another Skill, CLI, Prompt, Schema, module, or state machine.

## Read the local contracts progressively

Always read `references/workflow.md`. Read `references/runtime-dependencies.md`
only for setup or `doctor` failures, and read
`references/ocr-text-hints-contract.md` only when choosing or troubleshooting OCR.

Before writing a page manifest, read `references/page-decision-tree.md` and
`references/manifest-schema.md`. Add only the references needed by that page:

- structured or compound page: `references/region-decomposition.md` and
  `references/object-routing.md`;
- arrows: `references/manifest-arrow-extension.md`;
- raster assets or image-backend work: `references/assets-provenance-contract.md`.

Before accepting or delivering output, read `references/qa-contract.md`.

## Preserve the single source of truth

- Treat `page_jobs.json` as the only page-state source.
- Treat each `pages/page_NNN/manifest.json` as the only page-content source.
- Treat `deck_manifest.json` as the final-assembly source.
- Use only `prepare`, `run next/dispatch/record/reset/hints/finalize`, and the
  page commands in the local CLI for stateful lifecycle operations.
- Keep semantic-region evidence in `manifest.json.image2ppt_region_decomposition`.
- Never create a second job file, reconstruction plan, OCR normalizer, page
  controller, packager, or finalize path.
- Let supplemental QA report failures; never let it mutate lifecycle state.

## Keep every write inside its owner directory

- Page build, validation, hints, and QA may read and write only inside that page
  directory. Manifest paths, recorded assets, formulas, reports, previews, and
  `--out` overrides must not use `..`, symlinks, or absolute paths to escape it.
  The sole external-input exception is an explicit image-tool result supplied to
  `image import` or as `process-sheet --asset-sheet-source`; it is copied into the
  page before becoming a build dependency.
- Run-level manifests and final outputs must remain inside the prepared run
  directory. Finalization rebuilds into a same-directory temporary file and
  publishes it atomically only after a successful build.
- Treat any boundary rejection as a hard failure; do not copy the rejected file
  back into scope and present it as runtime output.

## Preserve pre-migration behavior

- Treat self-containment as a path/import/entrypoint migration, not a redesign of
  reconstruction behavior.
- Generate each worker Prompt from the complete local base layer plus the preserved
  Image2PPT profile layer. Do not condense, reinterpret, or replace either layer.
- Prefer the previously validated visual strategy when several routes satisfy the
  contracts. Keep simple measured objects native and retain bounded complex assets
  wherever a native redraw would reduce fidelity.
- Never re-author an accepted baseline page merely to prove runtime independence.

## Run the workflow

### Image backend selection

Use `builtin-imagegen` when the agent runtime exposes `image_gen.imagegen`; it is
the preferred backend because the worker can inspect edit inputs and import the
explicit local result. Use the CLI image contract only when the built-in tool is
unavailable, errors, cannot read an input, or returns no valid local output. A
missing optional argument such as model, mask, size, quality, or output path never
authorizes fallback. Record the actual producer and permitted fallback reason in
`imagegen-jobs.json`.

The CLI image contract is provider-neutral at the transport boundary. Select
`codex-oauth` only for GPT Image model ids. Select `openai-compatible-api` for any
provider-specific model whose endpoint implements the OpenAI Images-compatible
`/images/generations` and/or `/images/edits` schema. Do not infer the image backend
from the task's language model. Use an explicit backend when provenance matters;
`auto` uses Codex OAuth only for compatible GPT Image ids and otherwise selects the
configured API without sending Codex OAuth credentials to third parties.

### 1. Preflight and OCR choice

```bash
python <image2ppt-root>/cli/image2ppt/cli.py doctor --json
```

Use Baidu AI Studio `PADDLE_OCR_TOKEN` when configured. If it is absent, tell the
user once that the local `builtin-ink` fallback measures text geometry but does
not recognize characters; offer the configuration path in
`references/ocr-text-hints-contract.md`. Respect an offline-only choice.

### 2. Prepare one run

```bash
python <image2ppt-root>/cli/image2ppt/cli.py prepare <input...> \
  --out-root output/image2ppt --image-backend builtin-imagegen
```

To pin a configured third-party provider/model for auditable provenance, prepare
with `--image-backend openai-compatible-api`. The run contract records the exact
`IMAGE2PPT_IMAGE_MODEL` from the active project config or environment; it does not
substitute a GPT Image default merely because no `--model` flag was passed.

Use `--no-text-hints` only when OCR processing is intentionally disabled. Regenerate
hints without creating a new run when needed:

```bash
python <image2ppt-root>/cli/image2ppt/cli.py run hints <run-dir>
```

### 3. Advance and claim pages

```bash
python <image2ppt-root>/cli/image2ppt/cli.py run next <run-dir> --json
python <image2ppt-root>/scripts/build_page_worker_prompt.py \
  <run-dir> --page <page-id> --out <absolute-page-dir>/worker-prompt.md
python <image2ppt-root>/cli/image2ppt/cli.py run dispatch \
  <run-dir> --page <page-id> --agent-id <id> --prompt-file <absolute-prompt>
```

For exactly one page, claim it with `--local` and reconstruct it in the current
agent. For multiple pages, dispatch independent page workers up to the capacity in
`page_jobs.json`. Do not reset a live worker merely because it is slow.

### 4. Reconstruct and gate each page

Plan a structured page as 3–5 semantic regions and route each region independently.
Use measured compound diagrams: measure every node, relation, and protected anchor. Keep measurable
circles, cards, straight/dashed relations, and simple connectors native. Use bounded
transparent assets only for complex local subparts.

Represent a thin arrow as one connector with its arrowhead on the same object.
Represent a filled arrow as one Arrow AutoShape, with centered label text inside the
same object. Never construct an ordinary arrow from a line plus triangle and never
flatten a whole knowledge graph into one image.

Write new page manifests with `schema_version: 2`. Use structured
`visual_inventory` items with explicit `kind` and `representation` values, and
write a concrete `quality_evidence` observation for every required quality check.
Formula rendering is a hard gate: a missing engine, converter, or failed compile
must keep the page failed unless the user explicitly approves that exact formula
exception and the manifest records both `user_approved_exception: true` and a
concrete `approval_note`.

The worker Prompt performs the deterministic sequence. Its final gates are:

```bash
python <image2ppt-root>/cli/image2ppt/cli.py page build <page-dir>
python <image2ppt-root>/scripts/run_image2ppt_qa.py <page-dir>
# The first run writes visual-review-evidence.template.json and remains pending.
# Inspect source.png against render/rendered.png, copy and complete the template
# as visual-review-evidence.json, repair if needed, then:
python <image2ppt-root>/scripts/run_image2ppt_qa.py <page-dir> \
  --visual-review-status reviewed \
  --visual-review-evidence <page-dir>/visual-review-evidence.json
python <image2ppt-root>/cli/image2ppt/cli.py page contact-sheet <page-dir>
```

The evidence file must cover the current source/render hashes and every required
check with a specific observation. `--visual-review-notes` is optional context and
cannot substitute for the evidence file.

Record only after standard validation and the Image2PPT region, arrow, and rendered
gates pass:

```bash
python <image2ppt-root>/cli/image2ppt/cli.py run record \
  <run-dir> --page <page-id> --agent-id <id>
```

Use the same `run reset` → dispatch → record lifecycle to repair rejected pages.

### 5. Finalize and revalidate the rebuilt deck

When `run next` reports `finalize`, run:

```bash
python <image2ppt-root>/cli/image2ppt/cli.py run finalize <run-dir>
python <image2ppt-root>/scripts/run_final_image2ppt_qa.py <run-dir>
# The first run writes final/visual-review-evidence.template.json and remains pending.
# Inspect every rendered slide, complete final/visual-review-evidence.json, then:
python <image2ppt-root>/scripts/run_final_image2ppt_qa.py <run-dir> \
  --visual-review-status reviewed \
  --visual-review-evidence <run-dir>/final/visual-review-evidence.json
```

Finalize rebuilds from page manifests, preserves source speaker notes, validates the
package, and writes the output recorded by `deck_manifest.json`. Final QA reapplies
manifest arrows, verifies arrow atomicity and compound structure, renders every
slide, checks speaker-note integrity, and writes `final/image2ppt_qa.json`.

## Deliver

Return the final PPTX path, standard final validation, and
`final/image2ppt_qa.json`. Report which complex visuals remain replaceable bitmap
assets. Do not call the deck complete while any page/final gate is pending or failed.
