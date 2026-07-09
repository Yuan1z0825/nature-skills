# `nature-paper2ppt` Skill

[中文说明](README.md)

## What It Does

- Builds Chinese PPTX journal-club or paper-presentation decks from scientific papers, with figure-crop QA, alignment checks, and de-template Chinese academic expression rules.

## When to Use It

- You need a group-meeting, journal-club, thesis-seminar, or department-report deck from a paper.
- You want key figures, source labels, and narrative structure preserved.
- You need a draft deck plus QA warnings rather than a purely decorative summary.

## Copy-Paste Prompts

- `Create a Chinese journal-club PPT from this paper, keeping key figures and source labels.`
- `Audit this generated PPT for incomplete figure crops, alignment problems, and AI-template wording.`
- `Revise this deck so the figures are complete and the Chinese academic expression is less templated.`

## Required Inputs

- PDF, article text, DOI, abstract, figure legends, or reading notes.
- Audience, presentation duration, slide count, and preferred emphasis.
- Optional source figures or existing PPTX to audit.

## Expected Outputs

- PPTX deck and related assets.
- Slide-level notes, source labels, and figure attributions.
- Quality-audit findings for crop completeness, alignment, text density, and template-like wording.

## Dependencies / API Keys / Local Environment

- PPTX generation and XML-level QA scripts may require Python packages available in the local environment.
- Visual verification is recommended before using the deck directly in a talk.

## FAQ

- **Can the output be used directly for a talk?** Treat it as a strong draft unless visual QA passes and the scientific content has been checked.
- **What was recently improved?** The workflow now emphasizes complete figure crops, alignment stability, and less templated Chinese academic phrasing.

## Related Skills

- [`nature-reader`](../nature-reader/README_EN.md)
- [`nature-figure`](../nature-figure/README_EN.md)
- [`nature-polishing`](../nature-polishing/README_EN.md)
