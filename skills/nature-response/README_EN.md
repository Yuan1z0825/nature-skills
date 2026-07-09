# `nature-response` Skill

[中文说明](README.md)

## What It Does

- Drafts, audits, and revises point-by-point reviewer response letters, revision cover letters, red-marked manuscript plans, and LaTeX response templates.

## When to Use It

- You receive a major or minor revision decision.
- You need to parse editor and reviewer comments into actionable response items.
- You need a cover letter, reviewer-by-reviewer replies, redline guidance, or LaTeX template.

## Copy-Paste Prompts

- `Use this revision email to draft point-by-point replies and a cover letter.`
- `Revise this response letter so each reviewer comment is answered clearly and politely.`
- `Create a LaTeX response template where each reviewer starts on a new page and quoted manuscript text is italicized.`

## Required Inputs

- Decision letter, reviewer comments, manuscript changes, response draft, and target journal constraints.
- Optional original manuscript, revised manuscript, or change log.

## Expected Outputs

- Point-by-point response letter.
- Revision cover letter.
- Redline/change-location plan for the manuscript.
- LaTeX templates and formatting guidance when requested.

## Dependencies / API Keys / Local Environment

- LaTeX is optional and only needed for compiling templates.
- Manuscript redlining may require document tooling depending on file format.

## FAQ

- **Should quoted revised manuscript text be formatted specially?** Yes. The current convention is to answer the comment, then paste revised manuscript text in italics.
- **Should reviewer sections start on new pages?** Yes, when producing formal reviewer-response letters.
- **Can it start from an email?** Yes. The workflow should parse the email and begin the response plan automatically.

## Related Skills

- [`nature-reviewer`](../nature-reviewer/README_EN.md)
- [`nature-polishing`](../nature-polishing/README_EN.md)
- [`nature-writing`](../nature-writing/README_EN.md)
