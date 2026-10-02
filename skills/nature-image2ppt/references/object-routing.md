# Object Routing Addendum

The local `references/page-decision-tree.md` is authoritative for background recognition/repair, foreground asset separation, formulas, native text, provenance, and fix-versus-warning decisions. This file adds semantic regions, mixed reconstruction, measured compound diagrams, protected visual anchors, and the arrow branch.

## Region decision order

1. Divide a structured page into 3-5 semantic regions before authoring objects.
2. Identify compound diagrams and position-sensitive modules.
3. Inventory and measure the simple objects in each region in source pixels.
4. Choose `native-object-decomposition`, `mixed-reconstruction`, `bounded-local-asset`, or `native-text-layout` for the region.
5. Write all resulting objects to standard `manifest.json` arrays and write the region evidence to `image2ppt_region_decomposition` in that same manifest.
6. Validate the region evidence against manifest ids before accepting the page.

For knowledge graphs and node-link diagrams, accurate native circles and simple connectors are preferred over either an approximate template redraw or a whole-region bitmap. Complex pictograms or source-specific dense paths may remain bounded local assets. Read `region-decomposition.md` for the required measurements and anchor contract.

## Arrow decision order

1. Decide whether the source mark is an ordinary structural arrow or a style-bearing foreground visual.
2. For an ordinary arrow, choose exactly one native representation.
3. Decide label ownership: inside a filled arrow, beside a connector, or part of a complex visual asset.
4. Record the one native arrow directly in standard `manifest.json.shapes[]`.

| Source arrow | Standard manifest strategy | PPT object count |
| --- | --- | --- |
| Straight thin arrow | one `type: line`, `connector: straight`, native arrowhead | 1 `p:cxnSp` |
| Elbow thin arrow | one `type: line`, `connector: elbow`, native arrowhead | 1 `p:cxnSp` |
| Simple curved thin arrow | one `type: line`, `connector: curve`, native arrowhead | 1 `p:cxnSp` |
| Filled directional arrow | one `preset: rightArrow/leftArrow/...` | 1 `p:sp` AutoShape |
| Chevron/process arrow | one `preset: chevron` | 1 `p:sp` AutoShape |
| Centered label inside filled arrow | `text` on the same filled-arrow shape | still 1 arrow object |
| Hand-drawn, textured, gradient, illustrated, or otherwise style-bearing arrow | foreground asset through the local asset-sheet workflow | 1 separated picture asset |

Do not reinterpret the foreground-asset rule as permission to use direct source crops. Complex arrows follow the same source-faithful image-edit separation contract as other foreground visuals.

## Fragmentation failures

These are always failures for an ordinary arrow:

- shaft plus a separate triangle/chevron head;
- outline, fill, head, and shadow as separate objects;
- a Unicode arrow glyph used as the visual arrow;
- multiple line segments grouped to imitate a simple elbow or curve;
- a bitmap used for an ordinary arrow without reclassifying it as a genuine style-bearing asset.

Connector captions may be separate native text boxes because they are labels, not arrow fragments. A centered filled-arrow label belongs in the same AutoShape.

## Other objects

After region routing and arrow classification, use the local decision tree for OCR/text ownership, image-edit separation, formulas, provenance, and packaging. Do not add another OCR selection, OCR normalization, icon substitution, controller state, or packaging rule.
