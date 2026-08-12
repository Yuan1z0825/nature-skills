---
name: nature-shared
description: Internal shared-reference support package for installed nature-writing, nature-polishing, nature-reader, and nature-paper2ppt skills. Do not invoke it as a standalone user workflow. Load only the specific core or journal-format file requested by another Nature skill.
---

# Nature Shared References

Use this package only as a dependency of another installed Nature skill.

- Load the exact referenced file; do not preload the whole package.
- Treat `core/` and `journal-formats/` as shared definitions, not standalone workflows.
- Use `journal-formats/nature.md` only for the flagship journal Nature and
  `core/research-compliance.md` only when its specialist applicability gate is
  triggered.
- Use `journal-formats/nature-machine-intelligence.md` for exact NMI article
  types, limits, initial-submission files, data/code duties and production
  requirements; do not import flagship Nature or Nature Communications limits.
- Return to the requesting skill for task logic, output format, and final QA.
