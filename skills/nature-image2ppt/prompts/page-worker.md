# Image2PPT profile addendum

This addendum extends the complete local page-reconstructor prompt above. It does not replace that prompt, its required reading, its object-source decisions, its OCR/text-hint behavior, its ownership boundary, or its standard artifacts.

Image2PPT root: {{SKILL_ROOT}}
Run directory: {{RUN_DIR}}
Page id: {{PAGE_ID}}
Page directory: {{PAGE_DIR}}
Source image: {{SOURCE_IMAGE}}

Before authoring the page, read these profile files in full:

- `{{SKILL_ROOT}}/references/region-decomposition.md`
- `{{SKILL_ROOT}}/references/object-routing.md`
- `{{SKILL_ROOT}}/references/manifest-arrow-extension.md`
- `{{SKILL_ROOT}}/references/qa-contract.md`

Additional hard rules:

1. Keep `manifest.json` as the only page build source. Use schema version 2 with structured `visual_inventory` and `quality_evidence`. Add arrow fields directly to standard `shapes[]`; do not create an Image2PPT plan, OCR copy, review manifest, or controller state.
2. Before choosing individual objects, divide a structured page into 3-5 semantic regions (1-2 only for a genuinely simple page). Inventory and route each region with the region/mixed-reconstruction contract, then express the result only through standard manifest objects.
3. Add `image2ppt_region_decomposition` directly to `manifest.json`. For compound diagrams, record every node center/size and every edge endpoint/direction in source pixels, map each to a stable manifest id, and protect every node/edge as a visual anchor. This extension is evidence, not a second build plan.
4. Regular circles, nodes, cards, straight lines, dashed relationships, and ordinary connectors that can be measured accurately must remain native objects. Use bounded source-faithful/textless assets only for the complex local subparts that would visibly drift; never flatten a whole knowledge graph or compound region into one bitmap.
5. A simple arrow is exactly one manifest shape and one PowerPoint object. Use one line item with native start/end arrowhead fields, or one filled-arrow preset with optional embedded text. Never use a line plus triangle, Unicode arrow glyph, or grouped arrow fragments.
6. The local page-decision-tree remains authoritative for OCR ownership, text hints, background/image-edit provenance, formulas, and asset generation. Region routing changes page decomposition and mixed reconstruction, not those upstream ownership rules.
7. Stable unique ids are required for all `shapes[]`, `text_boxes[]`, and `images[]` referenced by a region. Connector captions outside the line remain ordinary `text_boxes[]`; centered labels inside a filled arrow use that same arrow shape's `text` field.
8. Every page artifact, manifest path, asset, formula, report, and output override must resolve inside `{{PAGE_DIR}}`. A rejected path escape is a hard page failure.
9. Formula rendering failure is a hard page failure unless the user explicitly approved that exact exception and `formula_inventory` records `user_approved_exception: true` plus a concrete `approval_note`.

Replace only the base prompt's final page build/validate sequence with this extended sequence:

1. Finish the standard `manifest.json` and `imagegen-jobs.json` exactly as required by the base prompt, including `image2ppt_region_decomposition` inside the manifest.
2. Run `{{CLI}} page build {{PAGE_DIR}}`.
3. Run `python {{SKILL_ROOT}}/scripts/run_image2ppt_qa.py {{PAGE_DIR}}`. A return code of 2 with only pending visual review is expected on the first pass.
4. Inspect `{{SOURCE_IMAGE}}` and `{{PAGE_DIR}}/render/rendered.png` at useful detail, region by region. For compound diagrams check node count, center, size, circle geometry, edge endpoints, direction, dash style, document nodes, label anchors, and z-order. Also check every arrow's bend, head size, thickness, object count, and embedded label plus all base visual checks.
5. The first QA run writes `{{PAGE_DIR}}/visual-review-evidence.template.json`. Fix `manifest.json` or assets, rebuild, and repeat until the render matches. Copy the current template to `visual-review-evidence.json`, set `reviewed` to true, and fill every required check with a specific source-versus-render observation. Then run:

   `python {{SKILL_ROOT}}/scripts/run_image2ppt_qa.py {{PAGE_DIR}} --visual-review-status reviewed --visual-review-evidence {{PAGE_DIR}}/visual-review-evidence.json`

   Generic notes such as "looks good" never satisfy this evidence contract. Supplemental `--visual-review-notes` may explain context but cannot replace the evidence file.
6. Run `{{CLI}} page contact-sheet {{PAGE_DIR}}` after the accepted build. Confirm standard `validation.json` still contains top-level `passed: true` and its `image2ppt_profile.passed` is true.
7. Write the standard `page_result.json` shape required by the local manifest schema. Do not add an alternative result file.

In addition to the base-required files, leave these supplemental reports in the page directory:

- `arrow_postprocess_report.json`
- `arrow_inspection_report.json`
- `region_decomposition_report.json`
- `render/rendered.png`
- `render_report.json`
- `image2ppt_qa.json`
- `visual-review-evidence.json`

Return exactly the standard paths requested in the base prompt.
