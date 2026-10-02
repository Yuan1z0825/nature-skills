# Output Spec

## Contents

- [Standard bundle](#standard-bundle)
- [Full-text mode](#full-text-mode)
- [source_map.json](#source_mapjson)
- [paper.md](#papermd)
- [reader.html](#readerhtml)
- [Layout rules](#layout-rules)
- [Figure/table card format](#figuretable-card-format)
- [Citation format in the page](#citation-format-in-the-page)


## Standard bundle

Produce these files when possible:

- `paper.md`
- `source_map.json`
- `translation_notes.md`
- `assets/` for extracted images, crops, figure snippets, and equation fallbacks
- `reader.html` only when the user explicitly asks for a browser preview

## Full-text mode

When the source is a full paper, include all pages or all extractable sections in the reader. Do not limit the bundle to selected pages, a teaser excerpt, or the abstract unless the user explicitly requests a preview.

`paper.md` is the primary deliverable. It must expose paragraph-level bilingual alignment:

```markdown
<a id="S001"></a>
**Source:** p.1 S001

**Original:** ...

**中文:** ...
```

For source material that cannot be extracted or translated confidently, keep the source anchor and write a visible uncertainty note instead of dropping the block.

## `source_map.json`

Keep a stable source map so follow-up questions can cite the same anchors.

```json
{
  "paper": {
    "title": "",
    "venue": "",
    "source_type": "pdf|html|doi|arxiv|text",
    "language": "en",
    "source_path": ""
  },
  "blocks": [
    {
      "id": "S001",
      "page": 1,
      "type": "heading|paragraph|caption|table|table_row|equation|note",
      "order": 1,
      "original_text": "",
      "translation": "",
      "bbox": [0, 0, 0, 0],
      "confidence": "high|medium|low",
      "refs": ["F001", "T001"],
      "insert_after": "S001"
    }
  ],
  "pages": [
    {
      "page": 1,
      "block_ids": ["S001", "S002", "S003", "C001"]
    }
  ],
  "figures": [
    {
      "id": "F001",
      "page": 3,
      "caption_id": "C001",
      "image_path": "",
      "bbox": [0, 0, 0, 0],
      "placement_hint": "near_first_mention",
      "placed_after": "S012",
      "alt_text": ""
    }
  ],
  "equations": [
    {
      "id": "E001",
      "page": 4,
      "equation_number": "3",
      "latex": "\\mathcal{L}(\\theta) = \\sum_i ...",
      "bbox": [0, 0, 0, 0],
      "confidence": "high|medium|low",
      "image_path": null
    }
  ],
  "glossary": [
    {
      "term": "",
      "translation": "",
      "note": ""
    }
  ]
}
```

## `paper.md`

The Markdown reader should support:

- stable headings in paper order
- paragraph-level original/Chinese pairs
- source IDs on every substantive block
- figure/table cards near the relevant prose
- rendered display equations with stable `E...` anchors
- an equation index when there are three or more display equations
- English captions and Chinese caption translations
- page navigation for full papers
- terminology notes and uncertainty notes

Use `$...$` for inline math and `$$...$$` for display math. For a low-confidence or image-only equation, show the original crop from `assets/equations/` and label any accompanying LaTeX as a low-confidence transcription. See `references/equation-handling.md` for the exact block shape.

## `reader.html`

The page should support:

- desktop side-by-side original and translation
- mobile stacked layout
- clickable source IDs on every block
- rendered equations and equation-index links that retain the Markdown `E...` anchors
- figure cards near the relevant text
- section navigation
- page navigation for full papers

Do not add a question area unless explicitly requested.

## Layout rules

- Keep paragraph alignment stable.
- Keep captions attached to their figures.
- Show tables where they are explained, not only where they appear in the PDF.
- Prefer semantic proximity over exact visual reconstruction.
- If a figure is referenced across multiple sections, anchor it at the first substantive discussion and link later mentions back to it.
- Crop figures and tables with the tightest valid bounding box.
- Do not use a full-page screenshot when the actual content occupies a smaller region.
- If the exact crop box cannot be verified, label the crop as approximate.
- For full papers, preserve page order and include a page index.
- Keep printed equation numbers outside math delimiters and never invent missing equation numbers.

## Figure/table card format

```markdown
<a id="F001"></a>
### Fig. 1. 中文短标题

**Placed near:** p.3 S012
**Source:** p.4 C001

![Fig. 1](assets/fig1.png)

**Original caption:** ...

**中文图注:** ...

**Reading note:** ...
```

Every image/table asset must have a corresponding card in `paper.md`. Every card must identify the source caption and placement block.

## Citation format in the page

Use short, stable source pointers:

- `p.7 S021`
- `p.8 C003`
- `Fig. 2`
- `Table 1`
- `p.4 E001` or `Eq. (3)`

For follow-up answers, combine page and block ID when available.
