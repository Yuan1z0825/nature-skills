# Workflow and Run Contract

## Contents

- [Ownership map](#ownership-map)
- [Authoritative files](#authoritative-files)
- [Local entrypoint](#local-entrypoint)
- [Sequence](#sequence)
- [Lifecycle invariants](#lifecycle-invariants)
- [Speaker notes and final assembly](#speaker-notes-and-final-assembly)
- [Retry behavior](#retry-behavior)

## Ownership map

| Phase | Authoritative local implementation |
| --- | --- |
| Input normalization | `cli/image2ppt/runtime/_input_normalization.py` and `prepare_deck_run.py` |
| OCR and text hints | `paddle_text_hints.py`, `deck_text_hints.py`, `text_hints.py` |
| Run/page state | `page_jobs.json` through the local CLI `run` commands |
| Page worker Prompt | local base `prompts/page-worker-base.md` plus preserved profile `prompts/page-worker.md`, composed by `scripts/build_page_worker_prompt.py` |
| Page content and build | page `manifest.json` and local `page build` |
| Record/reset/finalize | local `run record/reset/finalize` |
| Semantic regions and compound measurements | in-manifest evidence plus `inspect_region_decomposition.py` |
| Arrow reconstruction | manifest arrow extension plus local postprocessor/inspector |
| Rendering and delivery QA | local page/final QA scripts |

No phase reads another Skill. There is no alternate OCR output, page controller,
reconstruction-plan packager, or deck assembler.

## Authoritative files

- `deck_manifest.json`: prepared input, page order, canvas, image backend, notes,
  and final output contract.
- `page_jobs.json`: only authoritative page status, dispatch lease, and result
  record.
- `run_state.json`: run history written by local lifecycle commands.
- `pages/page_NNN/manifest.json`: only authoritative page build input.
- `pages/page_NNN/validation.json`: page record gate; supplemental QA extends it
  in place under `image2ppt_profile`.
- `pages/page_NNN/page_result.json`: worker return contract.

Every page-owned path resolves inside its page directory; every run/final path
resolves inside the prepared run. Traversal, absolute escapes, and symlink escapes
are invalid state, not alternate output locations.

Forbidden parallel state includes `image2ppt_jobs.json`, a second page plan,
another OCR result schema, an alternate page result, and any second
accepted/recorded/finalized state. Region evidence inside `manifest.json` is build
evidence, not controller state.

## Local entrypoint

Use the source-tree CLI for reproducible execution:

```bash
python <image2ppt-root>/cli/image2ppt/cli.py prepare ...
python <image2ppt-root>/cli/image2ppt/cli.py run next <run> --json
python <image2ppt-root>/cli/image2ppt/cli.py run dispatch <run> ...
python <image2ppt-root>/cli/image2ppt/cli.py run record <run> ...
python <image2ppt-root>/cli/image2ppt/cli.py run reset <run> ...
python <image2ppt-root>/cli/image2ppt/cli.py run hints <run>
python <image2ppt-root>/cli/image2ppt/cli.py run finalize <run>
```

The optional installed `image2ppt` wrapper resolves to the same bundled package.

## Sequence

```text
local prepare
  -> local run next
  -> local worker Prompt builder
  -> local run dispatch
  -> worker writes regions and all objects to manifest.json
  -> local page build
  -> local region inspection + arrow postprocess + page render QA template
  -> source/render inspection + hash-bound structured visual evidence
  -> worker writes page_result.json
  -> local run record
  -> local run finalize
  -> local final arrow postprocess + structure/render QA
```

The Prompt builder preserves the original two-layer order: it renders the complete
local base Prompt, appends the local Image2PPT profile, and substitutes only local
paths and the absolute source-tree CLI invocation. The arrow postprocessor derives target objects from the
same stable `(z_index, manifest order)` mapping used by the local builder and
preserves non-slide package parts.

## Lifecycle invariants

1. `prepare` normalizes inputs, extracts note metadata, creates page requests and
   text hints, initializes `page_jobs.json`, and records the image backend.
2. `run next` reads state only and recommends configuration, dispatch, wait, or
   finalize.
3. `run dispatch` records one active execution lease. Single-page local work uses
   `--local`; multi-page work records the worker id and absolute Prompt path.
4. A dispatched page remains active until explicit completion, failure,
   cancellation, or verified loss. Time elapsed alone is not loss.
5. `run record` validates artifacts, manifest structure, hashes, and top-level
   `validation.json.passed=true` before recording the page.
6. `run reset` is the only supported transition back to pending after a rejected,
   failed, cancelled, or verified-lost execution.
7. `run finalize` accepts only fully recorded pages, rebuilds the deck from page
   manifests in order, validates it, atomically publishes the final PPTX inside
   the run, and updates the existing run/deck state.

Supplemental page/final QA may write report files and extend `validation.json`, but
must never update `page_jobs.json`, `deck_manifest.json`, or `run_state.json`.
Free-text review notes do not close visual review. The required evidence is bound
to the current source/render hashes and covers every page and conditional check.

## Speaker notes and final assembly

`prepare` is the only note-extraction stage. For PPT/PPTX input it reads note-slide
parts, records page mapping, text, hashes, and preserved note XML under
`notes_manifest.json`, and keeps note resources inside the run input area.

Page workers must not receive, translate, summarize, rewrite, or delete speaker
notes. Page manifests describe slide content only.

`run finalize` is the only assembly stage. It reads recorded page manifests in
page order, rebuilds every slide, and restores the corresponding note slide from
the preserved XML when available; otherwise it writes the preserved note text.
It writes the output path and completion metadata to the existing
`deck_manifest.json`/run state.

Final validation compares expected and produced page counts, required text,
asset provenance, and note text hashes. A missing note slide or hash mismatch is a
hard final validation failure. Final Image2PPT QA runs after assembly and must not
alter lifecycle state or note content.

## Retry behavior

Do not hand-edit `page_jobs.json`. Repair a page's authoritative manifest/assets
inside a valid execution lease and rerun the same page gates. If execution failed,
was cancelled, or is verified lost, use local `run reset`, dispatch again, and
record again. Finalization always rebuilds from recorded manifests, so rerun final
QA after every finalize.

If final QA fails, repair the authoritative page manifest through that lifecycle
and finalize again. Do not patch only the final deck or create another assembler.
