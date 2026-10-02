# Assets and Provenance Contract

## Separate image production from page assembly

The agent image tool or the bundled `image generate/edit` backend produces image
files. The deterministic local CLI imports, validates, records, chroma-cleans, and
splits those outputs. Never infer a generated result by scanning for the newest
file; import only the explicit returned path.

Use an image only for a clean background, a bounded style-bearing foreground
object, a complex local diagram subpart, a user-provided visual, an approved
rasterization, or a rendered formula. Do not use a full-slide screenshot as a
hidden base and do not flatten a measurable knowledge graph.

## `imagegen-jobs.json`

`prepare` creates one page-local job ledger. `image import` records the actual
producer, selected file, destination, hash, role, and fallback reason. `image
process-sheet` records chroma cleanup and split artifacts. These are asset records,
not a second page state machine.

Every recorded source, destination, split artifact, and provenance path must
resolve inside the owning page directory. An absolute path may be used as the
input to `image import` or as the explicit `process-sheet --asset-sheet-source`
only long enough to copy a selected image-tool result into the page; it must never
be recorded as the page asset path or reused as a build dependency. Relative
inputs remain page-confined and may not use `..` traversal.

Valid producer identifiers are `builtin-imagegen`, `codex-oauth`, and
`openai-compatible-api`. A fallback reason is allowed only when it matches the
run/page image-backend contract. Record the exact provider model id with
`image2ppt image import --model` when it is known; provider-specific model ids do
not create new producer identifiers because the producer boundary is the transport
backend plus the recorded model.

## `manifest.json.asset_provenance`

Every `images[].path` requires one matching provenance item with:

- `path`: the exact path referenced by the page image object;
- `source`: an existing source, asset sheet, or formula source file;
- `source_type`: `asset-sheet-separated`, `imagegen`,
  `latex-rendered-formula`, `user-provided`, or
  `user-approved-rasterization`;
- `provenance_note`: a non-empty production explanation;
- `approval_note`: additionally required for user-approved rasterization.

Record foreground visuals as source-faithful image-edit/asset-sheet separation.
Native structural circles, lines, cards, and connectors should be described as
native structure, not as image assets. Keep every complex asset bounded to its
actual source region and give it useful alt text.

## Security and network boundary

Online OCR and image services receive only the task-local pages, prompts, masks,
and references necessary for the requested conversion. Request required network
approval before sending sensitive material. Keep API keys and OAuth files outside
the Skill and run directories; diagnostic output must expose only set/unset status.
