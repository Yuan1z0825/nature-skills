# Page Decision Tree

This file is the single source of truth for page object decisions. Field contracts live in `manifest-schema.md`; command syntax lives in `cli-helper.md`.

Every `source.png` is judged in three steps, in this order:

1. Background recognition and repair.
2. Foreground asset separation.
3. PPT native element reconstruction.

The order exists because steps 1-2 decide object sources and step 3 consumes those decisions. Nativizing text and layout first locks in wrong choices: text that belongs to a logo, a UI screenshot, or a to-be-separated asset must not become a native text box, and which text needs clean-base removal depends on the background decision. Define the boundaries between background, foreground, and native structure first; then write the manifest. Submit image jobs serially through `page_request.json.image_backend`; its field contract lives in `manifest-schema.md`, and fallback CLI syntax lives in `cli-helper.md`. Do not parallelize page-local image jobs through a batch interface because concurrent asset-sheet calls make rate limits, retries, and reconciliation failures harder to diagnose.

## Contents

- [Common Failure Mode: False Progress](#common-failure-mode-false-progress)
- [Pre-Decision: Page Inventory](#pre-decision-page-inventory)
- [1. Background Recognition and Repair](#1-background-recognition-and-repair)
- [2. Foreground Asset Separation](#2-foreground-asset-separation)
- [3. PPT Native Element Reconstruction](#3-ppt-native-element-reconstruction)
- [Final Self-Check](#final-self-check)
- [Fix versus Warning](#fix-versus-warning)

## Common Failure Mode: False Progress

Do not create a "good enough" editable draft by rebuilding text and layout while cropping or approximating foreground assets. This is false progress: it may pass deterministic validation but it fails the object-source contract. Deterministic validation is a structure gate, not a waiver — `validation.json.passed=true` never makes a forbidden foreground fallback acceptable.

When a page has complex foreground visuals, first prove the foreground asset workflow is feasible. If it is not, stop with a page failure before building `manifest.json`. Do not convert the missing workflow into a warning, a direct source crop, a native-shape approximation, an emoji/text-symbol substitute, or any other fallback.

## Pre-Decision: Page Inventory

Build a complete inventory before deciding anything, so that no object's source is chosen ad hoc later:

- Page size and page type.
- All readable text, with source glyph height, container height, line spacing, and density for each text level.
- Background type — solid color, gradient, regular texture, photo, illustration, dashboard, spatial/product image, complex graphic background — and whether it is occluded by text, icons, labels, stickers, hand-drawn marks, or other foreground objects that will be rebuilt later.
- Foreground visual objects: icons, pictograms, logo-like marks, foreground photos, screenshots, image blocks, textures, illustrations, people, plants, devices, hand-drawn marks, stickers, decorative lines, badges.
- PPT native element candidates: text, text boxes, cards, panels, tables, axes, lines, flow boxes, dividers, simple arrows.
- Formula candidates: objective functions, constraints, matrices, fractions, roots, cases, multiline equation groups, ordinary math expressions. List formulas separately; never group them with ordinary text.
- Corner geometry for every rectangle/card/table outline: straight, slight radius, obvious radius, pill.

Record the inventory in `visual_inventory`, and the decisions of the next three sections in `background_strategy` and `quality_checks` (field contracts in `manifest-schema.md`; all four `quality_checks` flags must end up `true`).

## 1. Background Recognition and Repair

Step 1 decides only the background; do not process foreground assets or text yet. Record the outcome in `background_strategy` (field contract in `manifest-schema.md`), including a `comparison_note` written after comparing the result against the source.

### 1.1 Backgrounds That Do Not Need Image Tools

Rebuild these directly with PPT structural objects or the deterministic runtime — calling the image backend for them wastes a generation and risks drift:

- Solid-color backgrounds.
- Simple gradients.
- Ordinary cards, panels, and container fills.
- Table lines, axes, gridlines, chart frames.
- Regular repeated textures, regular divider bands, simple shadows.
- Blank background regions not occluded by foreground.

Record this kind of background as `background_strategy.mode: native-or-script` or an equivalent mode.

### 1.2 Reusable Background Regions

An existing background region may be reused as-is only when all of these hold:

- It contains no text, labels, icons, stickers, hand-drawn marks, or other foreground objects that need removal.
- Reusing it will not create a duplicate "one copy in the background, another copy as editable objects" problem.
- It is not a full-page `source.png` with native text overlaid.
- It is a background/illustration area within the page — not a whole card, whole table, or whole chart screenshot used to bypass editability.

### 1.3 Backgrounds That Need Image Tool Repair

Use the image-edit path selected by `page_request.json.image_backend` for background repair or clean bases when:

- Complex photos, spaces, real product images, complex dashboards, or complex illustrated backgrounds are occluded by foreground text or icons.
- Occluded areas need completion after removing text, labels, icons, stickers, or hand-drawn marks.
- Background and foreground are stuck together and native shapes cannot preserve source identity.

The clean base target is the same background with the to-be-rebuilt foreground removed — not a new image with a similar theme. The edit prompt must treat the source as both the edit target and strict visual reference, and must state:

- Preserve: original aspect ratio, composition, perspective, object positions, colors, lighting, materials, textures, depth of field, and background identity.
- Remove: readable text, labels, numbers, icons, stickers, badges, hand-drawn marks, and decorative objects that will be rebuilt later.
- Forbid: new rooms, new dashboards, new products, new camera angles, new object positions, different lighting, pseudo-text, watermarks, blurry patches, or smear artifacts.

If the occlusion is small, prefer local completion or a small patch rather than letting the image backend reimagine the whole background.

### 1.4 Dashboard Is Not Background by Default

A dashboard is not background, and it is not a single image block to screenshot wholesale. Dashboard titles, numbers, tables, axes, legends, ordinary chart elements, metric cards, filters, and labels are decomposed in step 3 into native text and structural objects.

Only these areas may be handled as background or image regions:

- Maps and heatmaps.
- Complex screenshot base images.
- Complex chart image regions whose data cannot be reliably restored.
- Complex textures or base imagery that function as visual background and will not be duplicated by later native objects.

Never screenshot a whole dashboard, whole table, whole card, or whole chart to skip editable structure.

## 2. Foreground Asset Separation

Step 2 decides only the source of non-text foreground visual objects. Every foreground object enters `visual_inventory` before its source is chosen.

### 2.1 Foreground Assets Must Use Image Edit Separation

Every non-text foreground visual object must be separated through the image-edit asset-sheet workflow selected by `page_request.json.image_backend`, including:

- Foreground photos, foreground screenshots, video covers, foreground image blocks, map fragments, chart-image fragments, and rectangular illustrations.
- Icons, pictograms, symbols, logo-like marks.
- Badges, stickers, tapes, stamps, corner tags.
- Hand-drawn marks, hand-drawn arrows, decorative underlines, circles, checkmarks, crosses.
- Complex arrows, icon-like nodes, objects with texture or shadow.
- Semantic small icons, trend icons, warning symbols, and status symbols in dashboards or charts.
- Leaves, plants, people, animals, computers, phones, devices, scene illustrations, and any other non-text object that carries page style.

Do not approximate these with native primitives, even when one appears to be made of circles, lines, rectangles, or ellipses — the criterion is not "can it be drawn" but whether it is a foreground visual asset rather than a layout primitive. Do not substitute direct source-image snippets for source-faithful separation. Do not hand-draw or assemble foreground visual objects with local Python/Pillow/SVG/HTML/CSS code; deterministic tools are only for normalization, recording, background removal, splitting, formula rendering, building, validation, and QA.

There is no fallback path. If asset-sheet separation cannot produce a compliant asset, the page is blocked until the asset workflow is fixed or the user explicitly changes the requirements for that exact object. Do not downgrade the missing separation to a warning; do not record, finalize, or deliver the fallback.

### 2.2 Asset Sheet Prompt Principles

An asset sheet is source-faithful separation, not redraw. The generation prompt must require:

- Separate existing objects from the source.
- Preserve original shapes, strokes, colors, proportions, internal spacing, texture, and visual identity.
- Use a flat chroma-key background; choose the key color based on the subject colors in `visual_inventory`.
- Put as many icons and foreground visual objects as practical onto one sparse asset sheet. Create multiple asset sheets only when a single sheet cannot fit all required objects with clear separation.
- Every object complete, not touching or overlapping other objects, with generous empty space between neighboring objects and sufficient outer padding so `process-sheet` can split each icon/object cleanly.
- Object count and order match `visual_inventory`.
- No readable text, labels, pseudo-text, or watermarks.
- No whole cards, whole panels, whole charts, or full-page fragments.
- No redrawing, beautifying, simplifying, synonym-symbol replacement, or "cleaner" substitute icons.

Key color: any high-saturation pure color (cyan, green, magenta, red, orange, ...) that does not appear in the assets and is far from all subject, stroke, shadow, and highlight colors — green subjects must not use `#00ff00`, blue/purple subjects must not use cyan/blue families, purple/magenta subjects must not use `#ff00ff`, white subjects must not use white or light gray. If `process-sheet` background removal fades the subject, cuts edges, or leaves key-color remnants, regenerate the sheet with a different key color first; only then consider tuning removal parameters.

### 2.3 Asset Sheet Reconciliation

After a sheet is generated and split, reconcile it against `visual_inventory`:

- Split asset count covers all required objects, and every asset name corresponds to the inventory.
- Missing objects, wrong symbols, missing strokes, severe deformation, background attachment, text contamination, or synonymous substitution must be regenerated or fixed before use.

What may ship as a recorded warning after compliant separation is defined in "Fix versus Warning" at the end of this file.

## 3. PPT Native Element Reconstruction

Step 3 rebuilds everything carried by native PowerPoint structure, plus formula assets. Enter it only after the step-1/2 decisions are recorded.

### 3.1 Text and Text Boxes

All readable text defaults to native PPT text boxes. Never use generated images to carry editable text, and never use hidden text, transparent text, 1 pt text, or off-canvas text to satisfy the text inventory. (Formulas are not ordinary text — see 3.2.)

Exceptions — text that is part of brand or background identity rather than editable content:

- Logo wordmarks, brand symbols, and trademark text.
- Brand text on product packaging.
- Place names on map base imagery.
- Small text inside UI screenshots that is not required to be editable.
- Signage in photo backgrounds.
- Textures such as newspapers, book pages, or code.
- Tiny text with very low OCR confidence that does not affect main meaning.

Explain each exception in `visual_inventory` or `asset_provenance`. Never disguise main titles, subtitles, body text, table text, legends, axis labels, numbers, tags, or button text as exceptions.

Do not guess font sizes or positions by eye — `image2ppt prepare` already measured them. Every page dir contains `text_hints.json` (each detected line's source-pixel `box_px`, glyph height, and derived font sizes; the `backend` field records which detector produced them) and `text_hints.png`, the source image with every detected line framed and labeled. If missing, regenerate with `image2ppt page hints <page_dir>`. Use the hints like this:

- Match each detected line in the overlay image to the text you read in the source.
- Copy the measured `box_px` and the matching font size column (`font_pt_if_cjk` for CJK text, `font_pt_if_latin` for Latin) into the corresponding `text_boxes` item.
- Add `"font_size_source": "measured"` to every box sized this way — the deterministic builder then trusts the measured size instead of applying its conservative shrink, which otherwise makes text systematically smaller than the source.
- Hints are advisory and incomplete by design. Fill lines the detector missed and correct lines it merged with a graphic or labeled implausibly (a box sitting on an icon or photo) from your own reading of the source — a missed hint never means the text can be dropped.
- Same-level text uses exactly one font size: lines sharing a `size_group` get the same size, hand-added text joins the size group of its level, and the final page keeps same-level text identical even where individual measurements disagree slightly.
- Keep deterministic runtime fitting (`fit_text`) enabled as the overflow guard; tuning fields and when to disable it are in `manifest-schema.md`.
- After building a preview, compare text by level against the source; do not enlarge titles, body text, or labels by default. If any level looks larger, heavier, more crowded, or wraps more than the source, fix the font size or box before continuing.

Record completed calibration with `quality_checks.font_size_calibrated=true`.

### 3.2 Formula Handling

Transcribe each formula from the source into LaTeX, then render it with the local
CLI into an image asset written inside the page directory (prefer SVG; use PNG
when SVG preview/PowerPoint compatibility is unstable):

```bash
python <image2ppt-root>/cli/image2ppt/cli.py formula render-latex <page_dir> \
  --tex "\\sum_{i \\in N} p_{ij} x_{ij} \\ge a_j u_j" \
  --out assets/formula_c2_1.svg \
  --box 105,392,390,90 \
  --id formula_c2_1 \
  --fragment assets/formula_c2_1.fragment.json
```

Merge the fragment's `images`, `asset_provenance`, and `formula_inventory` into `manifest.json`; the required provenance fields are in `manifest-schema.md`. Never assemble formulas from Unicode subscripts/superscripts or many hand-written text boxes, and never use source-image formula snippets.

If the machine lacks a TeX engine or converter, or compilation fails, keep
`validation.json.passed=false` and record the formula id, LaTeX source, exact CLI
error, and required repair. Do not replace the formula with a full-page screenshot.
Delivery may proceed only when the user explicitly approves omission of that exact
formula; record `user_approved_exception: true` and a concrete `approval_note` in
its `formula_inventory` entry.

### 3.3 Structural Primitives and Layout Objects

These may use native PPT shapes or structural objects:

- Straight lines, dashed lines, polylines.
- Rectangles, rounded rectangles, circles, ellipses.
- Ordinary arrows and connectors.
- Solid-color cards, panels, dividers, borders.
- Tables, table lines, axes, gridlines.
- Simple bar charts, progress bars, status color blocks.
- Simple callouts.
- Basic flow boxes and containers without style-specific details.

Native shapes carry only layout structure, never semantic icons or visual identity: a DNA mark, lock, network node, target, magnifier, or checkmark inside a circular icon is not a structural primitive — separate it in step 2.

### 3.4 Corner Geometry

Corner decisions are conservative because over-rounding is a common, visible failure:

- Classify the source corner first: `straight`, `small-radius`, `large-radius`, or `pill`.
- Use `rect` for `straight`; use `roundRect` for the rest and estimate `source_corner_radius_px`.
- Corner radius is an object-level property, not a boolean: an 8-12 px slight radius on a large panel must not become a 70 px pill.
- If uncertain, zoom into the source corner; if still uncertain, record the basis and prefer the smaller radius.
- Every `roundRect` records `source_corner_radius_px`; `corner_reason` is supplemental and never replaces the radius.
- Never round ordinary rectangles out of design preference.

### 3.5 Text Strokes and Decoration Splitting

A readable character stroke belongs only to its native text box — never draw the same stroke again as a shape. Independent decorative lines, dividers, and button underlines may be shapes, but only after confirming they are not part of text. If the preview shows an extra dash, dot, or repeated symbol, inspect the source to decide whether it is a text stroke or an independent decoration, then remove the duplicate.

### 3.6 Grouping and Layering

Preserve grouping relationships (icon + circular base, badge + number, speech bubble + text, hand-drawn arrow + annotation, card background + title + chart + labels).

For native text centered inside a badge or circular base, reuse the base shape's exact `box_px` for the text box and use the centered horizontal and vertical alignment defined in `manifest-schema.md` under "Text alignment." A separate tight ink box drifts as font metrics change and is not a stable grouping relationship.

Recommended z-index:

- clean background/base: 0
- native structural shapes: 10-20
- separated foreground assets: 30
- native editable text: 40+
- circles, stickers, or hand-drawn marks that must sit above text: 50+

The background must not cover text, foreground assets must sit on the right layer, and the same text, icon, or decoration must never appear both in an image layer and as a native object.

## Final Self-Check

Whoever rebuilds the page checks it once against this list — deterministic validation is necessary but not sufficient, and the parent agent does not repeat this check. Record the evidence in structured manifest fields, `validation.json`, and the hash-bound visual-review evidence defined in `qa-contract.md`. Deck-level structural QA follows "Finalize and revalidate the rebuilt deck" in `SKILL.md`.

Structure and artifacts:

- `page.pptx` builds from `manifest.json` and opens; `preview.png` exists; `split_assets_contact.png` exists and shows an origin-versus-preview comparison.
- Every final raster asset has provenance.

Background:

- The clean base contains no readable text and no foreground object that will be rebuilt later.
- Repaired regions show no ghosts, blur blocks, smear patches, or pseudo-text.
- A complex-background clean base is the same background as the source — composition, perspective, object positions, colors, lighting, and key details have not drifted. A related-theme lookalike is a current-page fix even if deterministic validation passes.
- No image-backend call was wasted on solid or regular backgrounds.

Assets:

- `visual_inventory` covers all non-text visual objects; each has an independent representation unless explicitly recorded as background; no required object is missing or stood in by a low-quality placeholder.
- Every source decision follows sections 1-3: nothing marked for separation was replaced with a similar-but-different symbol, approximated with native primitives, or substituted with a source-image snippet.
- Split assets have no fused objects, missing edges, wrong names, fragments, or cross-object shadows; alpha edges have no chroma-key remnants.

Text:

- `text_inventory` covers all readable text; every editable item is a real, visible native text box (no hidden, transparent, 1 pt, or off-canvas text).
- Font sizes and positions are calibrated per 3.1: no clipping, wrong wrapping, or container overflow, and no level visibly larger, heavier, or more crowded than the source.
- CJK previews show no boxes or mojibake; use a stable CJK font when needed.
- No text, icon, or decoration appears both in an image layer and as a native object.

Shapes and layers:

- Corners follow 3.4; large container corners, table borders, and card borders align with the source. Corner misclassification is a current-page fix, not a low-risk warning.
- No text stroke is redrawn as a decorative shape (3.5).
- Dashboards, tables, cards, and charts are decomposed per 1.4, never screenshotted wholesale.
- Badge and circular-number groups follow the shared-box centering rule in 3.6.
- z-index follows 3.6; no text or key object is covered.

## Fix versus Warning

Every failed self-check item above is a current-page fix, owned by the page author, before the page returns. These structural conditions are also hard failures, never warnings:

- The input cannot be normalized.
- The page lacks a buildable `manifest.json`/`page.pptx`, or the PPTX cannot be opened.
- Text font size or position visibly deviates from the source and causes crowding, overflow, or occlusion.
- A formula cannot be rendered and lacks an explicit user-approved exception for
  that exact formula.

May ship as recorded warnings with the current PPT — but only after the required object-source workflow has succeeded:

- Minor line-width, antialiasing, proportion, shadow, or detail differences in separated assets.
- Minor visual drift in non-critical decorations.
- Recorded low-risk font differences.

Warnings never hide a failure to follow the three-step decision process: an object-source violation is always a current-page fix.
