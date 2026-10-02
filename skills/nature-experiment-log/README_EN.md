# `nature-experiment-log` Skill

[中文说明](README.md)

`nature-experiment-log` turns experiment images, voice notes, text, and scattered observations into traceable structured experiment logs for Obsidian or plain Markdown workflows.

## Ways To Use It

- Upload images, audio, voice transcripts, or text directly in the current session.
- Provide a local file or folder path for the agent to read and organize.
- Optionally use `feishu-cli-integration` to retrieve messages and attachments from a Feishu group.
- Save the output to a normal local folder or an Obsidian vault; when no target directory is provided, return save-ready Markdown first.

## What To Use It For

- Turn a day's experiment record into a standard log with YAML frontmatter.
- Extract experiment elements from photos, microscopy images, weighing notes, instrument screenshots, or voice transcripts.
- Link samples, conditions, observations, anomalies, next actions, and raw attachments.
- Archive raw materials from Feishu, chat records, or CLI input into the same experiment-log format.

## Typical Requests

- "Record an experiment: 316L chloride-salt corrosion at 500°C for 300 h in Ar, mass loss 0.0032 g."
- "Turn these experiment photos into today's Obsidian lab log."
- "Use this voice transcript to create a standard experiment record and list missing information."

## What You Need To Provide

- Experiment date, sample, conditions, steps, observations, or raw attachments.
- Target vault / output directory; if not specified, the skill generates Markdown that can be saved.
- Required naming rules, project IDs, or sample IDs.

## Outputs

- Experiment log with YAML frontmatter.
- Attachment index for source images, audio, tables, or chat records.
- Missing-field checklist and suggested next experiment actions.

## Boundaries

- The skill does not invent temperature, duration, recipe, device model, or results.
- Unconfirmed information is preserved as `AUTHOR_INPUT_NEEDED` or Chinese confirmation items.
- The core workflow does not require Feishu or Obsidian. Their CLI, bot permissions, or vault access are needed only when those optional integrations are used.

## Related Skills

- `nature-data`: turn experiment data into Data Availability and FAIR checklists.
- `nature-figure`: turn experiment data or images into submission-grade figures.
