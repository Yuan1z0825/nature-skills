# Region Decomposition and Mixed Reconstruction

This local contract defines semantic-region routing, measured compound diagrams,
and protected visual anchors. The local `page_jobs.json` remains the only page
state, and the page `manifest.json` remains the only build source.

## Contents

- [Two-level routing](#two-level-routing)
- [Compound diagrams](#compound-diagrams)
- [Protected visual anchors](#protected-visual-anchors)
- [Manifest extension](#manifest-extension)
- [Review gate](#review-gate)

## Two-level routing

Do not route a whole page object-by-object without first understanding its
semantic modules.

1. Divide a structured page into 3-5 semantic regions.  A genuinely simple
   page may use 1-2 regions.
2. Inventory every meaningful object inside each region before authoring it.
3. Route the region and its objects:
   - native text for readable content;
   - measured native shapes for simple circles, cards, boxes, rules, and dots;
   - one native connector for each simple straight/elbow/curved relationship;
   - a bounded source-faithful or textless asset for complex, dense,
     style-bearing visual material that would drift when redrawn;
   - mixed reconstruction when a complex local visual needs native editable
     text or simple measured objects above or around it.
4. Write the chosen objects to the normal `text_boxes[]`, `shapes[]`, and
   `images[]` arrays.  Do not create `source_reconstruction_plan.json` or a
   second assembly path.

Region planning changes reconstruction reasoning, not lifecycle ownership.

## Compound diagrams

Knowledge graphs, node-link diagrams, workflows, matrices, and other compound
regions require an object inventory in source-pixel coordinates.

For a knowledge graph, record at least:

- every circle/node center and measured width/height;
- whether it is a true circle, ellipse, document node, or complex pictogram;
- every relationship's measured endpoints, direction, line style, and
  arrowhead ownership;
- labels and their anchor objects;
- z-order and overlap ownership;
- the exact manifest id that implements every native node and relationship.

Do not infer a node layout from an attractive graph template.  Measure each
node independently from the source.  A repeated row or column is useful as a
cross-check, never as a substitute for measurements.

Simple regular graph objects remain native and editable when they can be
measured accurately.  Do not replace an entire knowledge-graph region with one
bitmap merely because the region is dense.  Use a local asset only for the
specific complex or style-bearing subpart that cannot be represented faithfully
with normal shapes/connectors.

## Protected visual anchors

Preserve and review non-text structure explicitly:

- circles, rings, node boundaries, and document-node boundaries;
- line endpoints, route lines, arrowheads, bends, and junctions;
- dashed relationships and their dash rhythm;
- card edges, dividers, markers, icons, and label anchors.

Every node and edge in a compound diagram must appear in
`protected_visual_anchors`.  Textless cleanup must not erase, clip, shift, or
duplicate these anchors.

## Manifest extension

Add this evidence directly to the standard `manifest.json`.  The deterministic
builder may ignore the extension, while Image2PPT QA validates it against the
normal manifest objects.

```json
{
  "image2ppt_region_decomposition": {
    "schema_version": "image2ppt-region-decomposition-v1",
    "page_complexity": "structured",
    "source_size_px": [1672, 941],
    "regions": [
      {
        "id": "supplementary-kg",
        "label": "Supplementary Knowledge Graph Context",
        "source_bbox_px": [904, 373, 391, 370],
        "risk_level": "high",
        "strategy": "native-object-decomposition",
        "reason": "Regular circles and simple relationships are individually measurable.",
        "manifest_ids": {
          "shapes": ["node_concept", "edge_concept_threshold"],
          "text_boxes": ["label_concept"],
          "images": ["kg_doc_core"]
        },
        "protected_visual_anchors": [
          {
            "id": "anchor-node-concept",
            "kind": "circle-node",
            "manifest_id": "node_concept",
            "source_bbox_px": [1051, 467, 25, 25]
          },
          {
            "id": "anchor-edge-concept-threshold",
            "kind": "directed-connector",
            "manifest_id": "edge_concept_threshold",
            "source_points_px": [1063, 492, 1063, 535]
          }
        ],
        "compound_diagram": {
          "kind": "knowledge-graph",
          "object_inventory_complete": true,
          "measurement_reviewed": true,
          "native_object_policy": "measured-simple-objects-native",
          "nodes": [
            {
              "id": "concept",
              "manifest_id": "node_concept",
              "geometry": "circle",
              "source_center_px": [1063.5, 479.5],
              "source_size_px": [25, 25],
              "position_tolerance_px": 2,
              "size_tolerance_px": 2
            }
          ],
          "edges": [
            {
              "id": "concept-to-threshold",
              "manifest_id": "edge_concept_threshold",
              "source_points_px": [1063, 492, 1063, 535],
              "line_style": "solid",
              "direction": "end"
            }
          ]
        }
      }
    ]
  }
}
```

Allowed region strategies are:

- `native-object-decomposition` for accurately measurable structure;
- `mixed-reconstruction` for native objects plus bounded local assets;
- `bounded-local-asset` for a complex non-compound visual region;
- `native-text-layout` for a simple text/layout region.

A compound diagram may not use `bounded-local-asset` as its whole-region
strategy.  In a mixed compound diagram, retain every measurable simple node and
connector as native objects and bound each asset to its actual subpart.

`source_bbox_px` uses `[x, y, width, height]` in the unchanged source-image
coordinate system.  `source_points_px` uses `[x1, y1, x2, y2]`.  Manifest
`box_px` and `points_px` must match the reviewed measurements within the stated
tolerance.

## Review gate

Before page acceptance:

1. Run `inspect_region_decomposition.py` through the Image2PPT page QA.
2. Compare the source and render at useful zoom, region by region.
3. For compound diagrams, check node count, node centers, node sizes, edge
   endpoints, direction, dash style, label anchors, and z-order.
4. Correct the standard manifest and rebuild.  Do not patch a separate plan.

The supplemental report is evidence only.  It is not controller state and is
never consumed as an alternative build source.
