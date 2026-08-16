# `nature-shared/` - shared support package for nature-* skills

This is an installable support package, not a standalone user workflow. It keeps the shared definitions and references used by multiple `nature-*` skills in one place so those sources stay consistent and update together. A complete `npx skills` installation discovers and manages it alongside the user-facing skills.

Sibling skills reference these files through relative paths such as:

```yaml
always_load:
  - ../nature-shared/core/reader-workflow.md
```

## Contents

| File | Consumers |
|---|---|
| `core/reader-workflow.md` | `nature-polishing`, `nature-writing` |
| `core/paper-type-taxonomy.md` | `nature-polishing`, `nature-writing` |
| `core/ethics.md` | `nature-polishing`, `nature-writing` |
| `core/research-compliance.md` | `nature-writing` and skills needing Nature Portfolio specialist compliance checks |
| `core/terminology-ledger.md` | `nature-polishing`, `nature-writing`, `nature-reader`, `nature-paper2ppt` |
| `core/consistency-sweep.md` | `nature-polishing`, `nature-reviewer`, `nature-response`, `nature-statistics` |
| `core/main-text-discipline.md` | `nature-writing`, `nature-polishing`, `nature-response` |
| `journal-formats/nat-comms.md` | `nature-polishing`, `nature-writing` |
| `journal-formats/nature.md` | `nature-writing` and skills needing exact flagship `Nature Article` submission rules |
| `journal-formats/nature-machine-intelligence.md` | Writing, polishing, figure, data, and statistics workflows for NMI submissions |

`scripts/check_consistency.py` provides a mechanical first pass for terminology variants, equal values reported at different precision, and equivalent lengths expressed in different units. Its output is a set of warnings for contextual review, not automatic edits.

## When to Put Files Here

Only place a file here when two or more skills need to reuse the same content. If the content serves only one skill, keep it in that skill's own `static/` or `references/` directory.

## When to Keep Content Local

The shared layer should hold definitions and references only, such as paper-type classifications, reader workflows, ethics rules, or terminology ledgers. Skill-specific diagnosis, drafting, modification, and output logic should remain in each skill's own files.

## Relationship With Other Skills

`nature-shared/` is not a standalone workflow. It is a shared dependency package that other `nature-*` skills read on demand.
