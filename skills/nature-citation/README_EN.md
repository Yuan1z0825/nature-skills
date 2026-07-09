# `nature-citation` Skill

[中文说明](README.md)

## What It Does

- Adds strict Nature/CNS-style supporting citations to manuscript passages by splitting claims into citable segments and searching within curated high-impact source families.

## When to Use It

- You need supporting references for a manuscript paragraph, abstract, introduction, or discussion.
- You want references constrained to Nature Portfolio, Science-family, or Cell Press sources.
- You need citation exports such as ENW, RIS, or Zotero RDF.

## Copy-Paste Prompts

- `Add Nature/CNS-style supporting citations to this introduction paragraph.`
- `Split this long claim into citable segments and find supporting high-impact references.`
- `Export the selected references as RIS for Zotero.`

## Required Inputs

- Manuscript passage or claim list.
- Optional journal/source constraints and publication-year range.
- Optional export format preference.

## Expected Outputs

- Segmented claim-to-reference mapping.
- Recommended citations with source rationale.
- Reference-manager-ready export files when requested.

## Dependencies / API Keys / Local Environment

- Internet or literature-search access may be required for fresh verification.
- Reference exports depend on the available local scripts and source metadata.

## FAQ

- **Does it cite any paper it finds?** No. It should follow the skill's strict source and relevance filters.
- **Can I use it for non-Nature journals?** Yes, but the default source discipline is Nature/CNS-leaning support, so say when a broader scope is desired.

## Related Skills

- [`nature-academic-search`](../nature-academic-search/README_EN.md)
- [`nature-ref-verifier`](../nature-ref-verifier/README_EN.md)
- [`nature-writing`](../nature-writing/README_EN.md)
