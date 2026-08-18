# Manifest Schema

This document describes the responsibilities, owners, and current field contracts for `image2ppt` run/page JSON files. All key state is advanced by `image2ppt` commands; page reconstructors write only page-local files.

## Contents

- `deck_manifest.json`
- `page_jobs.json`
- `page_request.json`
- `page_result.json`
- `pages/page_NNN/validation.json`
- `pages/page_NNN/manifest.json`
- `pages/page_NNN/imagegen-jobs.json`
- `notes_manifest.json`

## `deck_manifest.json`

Owner: created by `image2ppt prepare`; `image2ppt run backend` may update the image backend; `image2ppt run finalize` reads it and writes completion time.

Purpose:

- Input type.
- Page order.
- Page manifest paths.
- Notes manifest path.
- Final output path.
- Run-level image backend contract.
- Original user request.

Key fields:

```json
{
  "schema_version": 1,
  "run_id": "job-id",
  "input_type": "image|images|pdf|pptx",
  "max_concurrent_pages": 6,
  "image_backend": {
    "backend_id": "builtin-imagegen",
    "tool_name": "image_gen.imagegen",
    "required_parameters": {
      "generate": ["prompt"],
      "edit": ["prompt", "referenced_image_paths"]
    },
    "input_context_policy": "generate with prompt; before editing, view_image each input, then use prompt plus absolute local referenced_image_paths",
    "save_path_policy": "use only an explicit valid local result/output_hint path, then image2ppt image import; never scan for a newest file",
    "fallback_command": "image2ppt image generate/edit",
    "fallback_order": ["codex-oauth", "openai-compatible-api"],
    "fallback_policy": {
      "on": [
        "tool-unavailable",
        "tool-error",
        "input-unreadable",
        "no-valid-local-output"
      ],
      "missing_optional_parameters": false
    }
  },
  "pages": [],
  "notes_manifest": "notes_manifest.json",
  "output": "final/origin_edited.pptx"
}
```

`image_backend` is written by `image2ppt prepare` and may be overwritten by `image2ppt run backend` when needed. Parent-level backend selection policy lives in `SKILL.md` under "Image backend selection".

For `backend_id: "builtin-imagegen"`, these fields are required and have fixed meanings:

- `tool_name`: `image_gen.imagegen`, an agent tool rather than a Python or shell API.
- `required_parameters`: the complete required argument sets. Generation needs `prompt`; editing needs `prompt` plus absolute local paths in `referenced_image_paths`.
- `input_context_policy`: requires `view_image` on every edit input before the built-in call; generation has no image input.
- `save_path_policy`: permits only an explicit valid local result path, including `output_hint`, followed by `image2ppt image import`; newest-file directory scanning is forbidden.
- `fallback_command`: the CLI surface used only after the fallback policy matches.
- `fallback_order`: the CLI's internal order, Codex OAuth before a configured OpenAI-compatible API.
- `fallback_policy.on`: the only events that permit leaving the built-in tool: it is unavailable/not callable, its call errors, an edit input is unreadable, or it returns no valid local image.
- `fallback_policy.missing_optional_parameters`: always `false`; absent optional controls never authorize fallback.

Other backend metadata may describe model labels, runtime homes, or handoff text, but it does not change this order. Parent-level tool selection and user-interaction policy live in `SKILL.md` under "Image backend selection"; page reconstructors execute the copied contract above.

## `page_jobs.json`

Owner: created by `image2ppt prepare`, updated by `image2ppt run` commands.

Purpose:

- Source of truth for page state.
- Dispatch records.
- Result records.

Structure:

```json
{
  "schema_version": 1,
  "run_id": "job-id",
  "max_concurrent_pages": 6,
  "pages": [
    {
      "page_id": "page_001",
      "status": "pending",
      "page_dir": "pages/page_001",
      "page_request": "pages/page_001/page_request.json",
      "source": "pages/page_001/source.png",
      "dispatch": null,
      "result": null
    }
  ]
}
```

`dispatch` is written by `image2ppt run dispatch`. It includes `execution_mode`: `"worker"` for normal page-worker dispatch and `"local"` for the parent agent's single-page local claim; older dispatch records without this field are treated as `"worker"`. A page with status `dispatched` is an active execution lease until explicit completion, failure, cancellation, or lost-worker verification; elapsed time alone does not make it lost. `result` is written by `image2ppt run record`. `accepted` is written by `image2ppt run finalize`.

## `page_request.json`

Owner: `image2ppt prepare`.

Purpose: task boundary for the page worker.

Includes:

- page id
- page directory
- source image
- slide size
- content box
- max concurrent pages
- allowed write scope
- required outputs
- user constraints
- image backend contract

Must not include:

- page type prediction
- `imagegen_required` prediction
- object-level decisions

If the run uses an image backend, `page_request.json` must contain the same `image_backend` object without weakening or reordering its `fallback_policy` or `fallback_order`.

`slide` and `content_box` are computed automatically by `image2ppt prepare`. Inputs close to 16:9 use the standard widescreen canvas; other inputs use a custom canvas converted from the source image pixel dimensions. The agent must copy these two fields into the page `manifest.json` and must not compress, stretch, or recalculate the canvas.

## `page_result.json`

Owner: created by the page reconstructor, validated by `image2ppt run record`.

Includes:

- manifest path
- imagegen jobs path
- page pptx path
- preview path
- contact sheet path
- validation path
- page-local output hashes, which may be supplemented by `image2ppt run record`

Minimal required shape (paths are relative to the page directory):

```json
{
  "page_manifest": "manifest.json",
  "imagegen_jobs": "imagegen-jobs.json",
  "page_pptx": "page.pptx",
  "preview": "preview.png",
  "contact_sheet": "split_assets_contact.png",
  "validation": "validation.json",
  "page_result": "page_result.json"
}
```

Every path in this object must resolve inside the owning page directory. Absolute
paths, `..` traversal, and symlink escapes are rejected even if the target exists.

The `manifest` artifact is the authoritative page source for final assembly. `image2ppt run finalize` rebuilds the final deck from recorded page manifests in page order. The `page_pptx` artifact remains a page-level deliverability artifact and is validated by `image2ppt run record`, but it is not the final assembly input.

## `pages/page_NNN/validation.json`

Owner: created by the page reconstructor, read by `image2ppt run record`.

Purpose: page-level deliverability conclusion.

Must contain at top level:

```json
{
  "passed": true
}
```

`passed` must be a boolean. `image2ppt run record` only reads top-level `passed` to decide whether the page can enter final assembly. `status: "pass"`, `runtime_validation.passed`, or other nested fields may remain as supplemental information, but they cannot replace top-level `passed`.

## `pages/page_NNN/manifest.json`

Owner: page reconstructor. New manifests use `schema_version: 2`; schema version 1
remains readable for existing runs. The machine-readable v2 contract is
`schemas/page-manifest-v2.schema.json`.

Purpose: source of truth for page-level PPTX construction.

The manifest is not a summary of a separately authored `page.pptx`. It is the build contract for both page-level validation and final deck assembly. A page may not pass validation if the page PPTX can only be reproduced by custom page-local code while the manifest lacks object positions.

Must contain:

- `schema_version: 2`
- `slide`
- `content_box`
- `source`
- `text_inventory`
- `visual_inventory`
- `background_strategy`
- `quality_checks`
- `quality_evidence`
- `text_boxes`
- `shapes`
- `images`
- `asset_provenance`
- page strategy

All paths referenced by the manifest, including `source`, `images`, provenance
sources, formula files, reports, and build overrides, must resolve inside the page
directory. Page build output is staged in the same directory and published
atomically; a failed build must not leave a new partial PPTX at the requested path.

`slide`, `content_box`, and `source.width_px/source.height_px` must come from `page_request.json`. All `box_px`, `points_px`, and `polygon_px` values use `source.png` pixel coordinates; the runtime maps these coordinates into `content_box` instead of stretching them to the whole slide. Coordinate layouts:

- `box_px: [x, y, width, height]`
- `points_px: [x1, y1, x2, y2]`
- `bezier_px`: one or more contiguous cubic segments, each encoded as
  `[x1, y1, c1x, c1y, c2x, c2y, x2, y2]` in source pixels. Use
  `type: "bezier"` plus `box_px` to create one editable PowerPoint freeform
  curve; do not approximate a smooth chart curve with many straight shapes.

Positioned build object requirements:

- Every `text_boxes[]` item must have `box_px`. Text in `text_inventory` does not create a positioned text box.
- Every `images[]` item must have `box_px`.
- Every non-line `shapes[]` item must have `box_px`.
- Every line shape must have `points_px`.
- Every Bézier shape must have `box_px` and at least one valid `bezier_px`
  segment. Consecutive segments should share endpoints so the rendered path has
  continuous geometry.

`text_inventory` and `visual_inventory` are only inventories; they do not substitute for positioned `text_boxes`, `images`, and `shapes`. The manifest must be sufficient to rebuild the page without reading any custom page script.

In schema v2, every `visual_inventory` item is structured:

```json
{
  "id": "company-mark",
  "kind": "foreground-asset",
  "representation": "asset-sheet-separated",
  "path": "assets/company-mark.png",
  "description": "Source-faithful mark separated on the reviewed asset sheet"
}
```

Allowed `kind` values are `background`, `foreground-asset`,
`native-structure`, and `formula`. Allowed `representation` values are `native`,
`asset-sheet-separated`, `source-preserving-local-cleanup`, `imagegen`, and
`latex-rendered-formula`. Valid pairs are:

- background: `native`, `source-preserving-local-cleanup`, or `imagegen`;
- foreground-asset: `asset-sheet-separated` with a path and matching provenance;
- native-structure: `native`;
- formula: `latex-rendered-formula`.

Every structured formula item must match a `formula_inventory` entry by id or
rendered image path; merely classifying a visual as a formula does not prove it was
rendered or explicitly approved for omission.

These fields, rather than substring matches in prose, determine the object-source
contract. This avoids false matches such as `benchmark` containing `mark`, and it
prevents a foreground icon from being excused merely because its description also
contains the word `background`.

Missing coordinates are page-contract violations. The runtime must reject them during `image2ppt run record` and deck validation because otherwise missing values fall back to default positions such as the top-left corner.

Text-size fitting:

- `text_boxes[].font_size` is treated as the requested font size. The deterministic builder may clamp it downward during normalization when the requested size is too large for the resolved source-pixel box.
- Keep default fitting enabled for first drafts. Set `fit_text: false` only when the page author has manually calibrated the box and font size.
- `text_boxes[].box_px` should describe the source text bounds plus modest padding. Do not use an entire card, chart, table cell group, or unrelated container as the text box, because the fitter can only infer size from the box it receives.
- Optional tuning fields are `min_font_size`, `max_font_size`, `text_fit_safety`, and `line_height`.

Text alignment:

- `text_boxes[].align` accepts `left`, `center`, or `right` (default `left`). The equivalent DrawingML tokens `l`, `ctr`, and `r` are also accepted.
- `text_boxes[].valign` accepts `top`, `middle`, or `bottom` (default `top`); `center` is an alias for `middle`. The equivalent DrawingML tokens `t`, `ctr`, and `b` are also accepted.
- The deterministic builder translates these manifest values to valid DrawingML enum tokens. Unsupported values are page-contract violations instead of silently falling back to an application default.

`text_inventory` may be a list of strings or a list of structured objects. In structured objects, the fields used for exact text validation are `text`, `required_text`, `items`, or `texts`; fields such as `id`, `decision`, `description`, and `note` are only records and are not used for exact text matching. Example:

```json
[
  {"id": "title", "text": "Market Overview", "decision": "native-text"},
  {"id": "metrics", "required_text": ["Annual recurring revenue", "42.8M"]}
]
```

`quality_checks` must include at least:

```json
{
  "font_size_calibrated": true,
  "visual_inventory_matched": true,
  "background_strategy_checked": true,
  "shape_corner_geometry_checked": true
}
```

Schema v2 also requires matching `quality_evidence`. Every required check has an
object with a concrete `observation` of at least 12 characters and may identify the
inspected `artifact`:

```json
{
  "font_size_calibrated": {
    "observation": "Title and body levels match the source without clipping",
    "artifact": "preview.png"
  },
  "visual_inventory_matched": {
    "observation": "All five source visuals appear once in the reconstructed page"
  },
  "background_strategy_checked": {
    "observation": "Background geometry and palette remain aligned with source.png"
  },
  "shape_corner_geometry_checked": {
    "observation": "Card radii and straight table corners match the enlarged source"
  }
}
```

`background_strategy` must explain at least:

- `mode`: `native-or-script`, `source-preserving-local-cleanup`, `imagegen-full-clean-base`, or similar.
- `source_consistency_contract`: which composition, perspective, object positions, colors, lighting, and key details are preserved.
- `removed_foreground`: which foreground objects were removed from the background and rebuilt later.
- `comparison_note`: the background consistency conclusion after comparing the preview against the source.

`asset_provenance` requirements — every path referenced in `images[]` must have a matching entry:

- `path`: the image path as referenced in `images[]`.
- `source`: the file the asset was produced from (for separated assets and clean bases this is typically `source.png` or the recorded asset sheet; for formulas the `.tex` file). The referenced file must exist.
- `source_type`: exactly one of `asset-sheet-separated`, `imagegen`, `latex-rendered-formula`, `user-provided`, `user-approved-rasterization`. No other value passes validation.
- `provenance_note`: a non-empty explanation of how the asset was produced.

Legacy schema-v1 manifests use conservative free-text checks for backward
compatibility. Schema-v2 manifests use the structured fields above and do not use
substring classification. In legacy manifests:

- An item whose description names a foreground object (icon, photo, logo, screenshot, badge, 图标, 照片, ...) must state its separation method in its text — include a term like "asset-sheet separated" / "image edit" / "分离" — unless the text marks it as background, formula, or native structure. Matching is substring-level, so words like "benchmark" or "trademark" also trigger the foreground check ("mark"); give native structural items an explicit "native structural" / "结构" marker in their description to exempt them.
- Terms naming forbidden fallbacks — "crop", "approximation", "fallback", "emoji", "裁剪", "近似", "降级", and similar — fail validation wherever they appear in these texts, even inside negations such as "no crop". Describe what was done ("asset-sheet separated from source"), not what was avoided.

`roundRect` shapes must record `source_corner_radius_px`; they may also record `corner_reason`. If the source is a straight-corner rectangle, use `rect`.

Recommended record:

```json
{
  "type": "roundRect",
  "box_px": [64, 169, 472, 187],
  "source_corner_radius_px": 12,
  "corner_category": "small-radius",
  "corner_reason": "source card corners are lightly rounded"
}
```

Allowed `corner_category` values: `straight`, `small-radius`, `large-radius`, `pill`. `straight` should not use `roundRect`.

`latex-rendered-formula` formula assets must record:

```json
{
  "images": [
    {
      "id": "formula_c2_1",
      "path": "assets/formula_c2_1.svg",
      "box_px": [105, 392, 390, 90],
      "alt": "LaTeX rendered formula formula_c2_1",
      "z_index": 220
    }
  ],
  "asset_provenance": [
    {
      "path": "assets/formula_c2_1.svg",
      "source": "assets/formula_c2_1.tex",
      "source_type": "latex-rendered-formula",
      "provenance_note": "Rendered from LaTeX by image2ppt formula render-latex; visual fidelity is prioritized over formula editability."
    }
  ],
  "formula_inventory": [
    {
      "id": "formula_c2_1",
      "decision": "latex-rendered-image",
      "editable": false,
      "image": "assets/formula_c2_1.svg",
      "tex_source": "assets/formula_c2_1.tex"
    }
  ]
}
```

Formula images must be generated by `image2ppt formula render-latex`. Do not use source-image formula snippets, and do not assemble complex formulas from hand-written native text boxes.

Every `formula_inventory` item is a hard validation contract. A formula marked
`failed`, `missing`, or `blocked`, or one without a rendered image/provenance pair,
fails the page. The only exception is explicit approval from the user for that
exact formula, recorded as:

```json
{
  "id": "formula_c2_1",
  "status": "blocked",
  "user_approved_exception": true,
  "approval_note": "User approved delivery without formula_c2_1 on 2026-08-18"
}
```

An internal decision, generic warning, or `validation.json.passed=true` cannot
create this exception.

## `pages/page_NNN/imagegen-jobs.json`

Owner: created by `image2ppt prepare`, updated by `image2ppt image import` and `image2ppt image process-sheet` (`generate`/`edit` do not write it — importing the selected output is what records the job).

Purpose: record the generation and processing process for clean bases, asset sheets, and selected bitmap assets.

Each imported job records at least the selected output and the backend that actually produced it:

```json
{
  "schema_version": 1,
  "jobs": [
    {
      "job_id": "icon-sheet",
      "role": "asset_sheet",
      "status": "recorded",
      "source_image": "/absolute/path/from/tool-output.png",
      "output": "assets/icon-sheet.png",
      "output_sha256": "...",
      "backend": "builtin-imagegen",
      "fallback_reason": null
    }
  ]
}
```

`backend` is the actual producer: `builtin-imagegen`, `codex-oauth`, or `openai-compatible-api`; `unknown` is reserved for legacy page directories that have no `image_backend` contract. `image2ppt image import` requires an explicit producer, rejects files that are not readable images, and checks `backend`/`fallback_reason` against the page contract. `fallback_reason` is `null` when the preferred backend succeeded or the run selected a CLI contract directly; when a built-in contract enters its CLI fallback, it records the matching event from `image_backend.fallback_policy.on`.

State and provenance record rules are described under "Preserve the single source
of truth" in `SKILL.md` and in the asset processing examples in `cli-helper.md`.

## `notes_manifest.json`

Owner: created by `image2ppt prepare`, read by `image2ppt run finalize`.

Purpose:

- Original PPT/PPTX speaker notes.
- Notes hashes.
- Page mapping.

Notes are not handed to page workers, translated, summarized, or rewritten.
