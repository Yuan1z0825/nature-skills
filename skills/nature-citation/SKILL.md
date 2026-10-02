---
name: nature-citation
description: "Find and verify Nature/CNS-family literature supporting manuscript claims, with claim-to-source mapping and reference-manager export. Use for Nature系列引用、CNS支撑文献、分段补引用 when this journal scope is requested; use broader literature search for unrestricted sources."
metadata:
  author: Yuan1z skill, refactored into static/dynamic layers
---

# Nature Citation — Router

## Routing protocol

For a new task, load the core and matching resources below. Reuse already loaded guidance on follow-ups; load more only when the task needs it.

### 1. Load the manifest and the core layer

Read [manifest.yaml](manifest.yaml). Then read every file listed under `always_load`:

- `static/core/principles.md` — what the skill produces, the strict journal scope, the source hierarchy, and the search-quality rules.
- `static/core/workflow.md` — the seven-step workflow and the final report format.

### 2. No content axis — confirm scope and language inline

Unlike the other nature-* skills, nature-citation has no fragment axis. Its variation is runtime parameters, not different content bodies:

- **journal scope** — `Nature系列` / `CNS` / `CNS及子刊` / flagship-only. Read it from the user's wording (see `core/principles.md`) and pass it to the script as `--scope`.
- **user language** — if the user writes Chinese or requests Chinese guidance, read `static/core/chinese-mode.md` (Chinese notes, English search queries).
- **input length** — if there are more than ~10 segments, switch to the batched long-article strategy in `references/script-usage.md`.

State the detected scope and date limits in one short line before searching.

### 3. Run the workflow

Follow the seven steps in `core/workflow.md`: segment, parse, search, evaluate support conservatively, validate complete structured author metadata, export one reference-manager file, and generate review artifacts when useful. Put the HTML browser path first only when it was generated. Prefer `scripts/nature_citation.py` for the search/export when internet access is available; open `references/script-usage.md` for its full flag list and the long-article batch strategy. When DOI metadata lacks given names, refetch the record by PMID or verify it against the publisher rather than exporting surname-only `AU` fields.

Never present a paper as support merely because its title is related, and never cite a metadata-only candidate without checking the abstract or publisher page. Do not invent missing bibliographic fields.

### 4. Reach for references only when needed

The files under `references/` are deep references, not defaults. Open them on demand per the `references.on_demand` table in the manifest:

- running the script, full flags, long-article batching → `references/script-usage.md`.
- turning a claim into search queries and support grades → `references/search-strategy.md`.
- the exact Nature/CNS journal-family boundary → `references/journal-scope.md`.
- RIS / EndNote / Zotero RDF export details → `references/ris-endnote.md`.
