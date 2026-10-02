# Supplemental QA Contract

Local deterministic validation remains mandatory. Image2PPT adds region/compound-diagram evidence, arrow atomicity, and render-based visual review.

## Contents

- [Page gate](#page-gate)
- [Arrow inspection](#arrow-inspection)
- [Region and compound-diagram inspection](#region-and-compound-diagram-inspection)
- [Rendered review](#rendered-review)
- [Final gate](#final-gate)

## Page gate

Required standard artifacts are exactly those in the local manifest schema:

- `manifest.json`
- `imagegen-jobs.json`
- `page.pptx`
- `preview.png`
- `split_assets_contact.png`
- `validation.json`
- `page_result.json`

Supplemental evidence is:

- `arrow_postprocess_report.json`
- `arrow_inspection_report.json`
- `region_decomposition_report.json`
- `render/rendered.png`
- `render_report.json`
- `image2ppt_qa.json`
- `visual-review-evidence.template.json`
- `visual-review-evidence.json` after human/agent visual inspection

`run_image2ppt_qa.py` must be the last validation command before writing standard `page_result.json`. It reruns local page validation after modifying the PPTX, then sets:

```json
{
  "passed": true,
  "image2ppt_profile": {
    "passed": true,
    "visual_review_status": "reviewed"
  }
}
```

at the relevant locations in standard `validation.json`. Do not replace `validation.json` with a profile-specific result file.

## Arrow inspection

For every profiled manifest arrow:

- `shapes[].id` resolves to exactly one PowerPoint object on the corresponding slide;
- a connector is one `p:cxnSp` with the expected straight/elbow/curve preset;
- start/end arrowheads are children of that connector's own line properties;
- a filled arrow is one `p:sp` with the expected Arrow AutoShape preset;
- `text`, when specified on a filled arrow, exists in that same object's text body;
- no duplicate object name creates an ambiguous mapping.

Machine inspection proves object structure, not visual fidelity.

## Region and compound-diagram inspection

`inspect_region_decomposition.py` validates the in-manifest
`image2ppt_region_decomposition` block against standard object ids and source
coordinates. It rejects:

- a structured page without 3-5 semantic regions;
- region references to missing manifest objects;
- manifest objects that were never assigned to a semantic region;
- a high-risk region without protected visual anchors;
- a compound diagram flattened as one region asset;
- an incomplete or unreviewed compound-object inventory;
- node centers/sizes or edge endpoints that do not match the reviewed source measurements;
- a declared circle implemented as a distorted ellipse;
- a missing direction arrowhead or dashed relationship style;
- a compound node/edge without a protected anchor.

Machine inspection proves internal measurement consistency. Source-versus-render review still determines whether the measurements themselves are correct.

## Rendered review

Compare `source.png` with the actual PowerPoint/LibreOffice render at matching aspect ratio. Check:

- arrow direction, bend, curvature, thickness, head type/size, and z-order;
- semantic region boundaries and composition;
- compound diagram node count, centers, sizes, circle geometry, connector endpoints, direction, dash rhythm, labels, and z-order;
- filled-arrow silhouette and embedded-label centering;
- composition, text hierarchy, line breaks, font fallback, assets, formula rendering, missing objects, and duplicate source text;
- no full-slide source image or source reuse masquerades as a render.

Specific structured observations are mandatory. A generic phrase such as "looks
good" is not sufficient evidence.

The evidence must be machine-checkable as well as specific. The first QA run
writes `visual-review-evidence.template.json`, binding every page to the SHA-256
hash of its current source and render. Copy it to `visual-review-evidence.json`,
set each page's `reviewed` field to `true`, and fill every listed check with a
concrete observation of at least 12 characters. Baseline checks cover composition,
text, object completeness, and render integrity; arrows, raster assets, formulas,
and compound diagrams add conditional checks. Missing pages, stale hashes, empty
checks, or generic notes fail the gate. `--visual-review-notes` is supplemental
only and never substitutes for this file.

Run the reviewed page gate with:

```bash
python <image2ppt-root>/scripts/run_image2ppt_qa.py <page-dir> \
  --visual-review-status reviewed \
  --visual-review-evidence <page-dir>/visual-review-evidence.json
```

## Final gate

After every local `image2ppt run finalize`, run `run_final_image2ppt_qa.py`. It must report:

- local deck validation still passes;
- page count and render count match;
- speaker-note hashes still match through the local validator;
- all profiled arrows pass one-object inspection in the rebuilt final deck;
- every manifest passes region/compound-diagram inspection;
- every rendered slide was compared with its source;
- `final/visual-review-evidence.json` covers the current hash of every source and
  final render with all required structured checks;
- `final/image2ppt_qa.json.passed` is true.

The final QA command follows the same two-pass template/evidence flow and uses
`--visual-review-evidence <run-dir>/final/visual-review-evidence.json`.

If final QA fails, fix the authoritative page manifest through the same local lifecycle and finalize again. Do not patch the final deck manually as the only fix.
