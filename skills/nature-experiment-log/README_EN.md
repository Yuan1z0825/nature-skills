# `nature-experiment-log` Skill

[中文说明](README.md)

## What It Does

- Standardizes experiment images, voice notes, and text into structured Obsidian-compatible experiment logs with YAML frontmatter and archived source materials.

## When to Use It

- You need to turn raw experiment notes into a durable lab log.
- You want consistent metadata, file naming, and source-material archiving.
- You are collecting field, lab, or group-chat experiment evidence.

## Copy-Paste Prompts

- `Turn these photos and notes into a structured experiment log entry.`
- `Archive these raw materials and create an Obsidian experiment note with YAML frontmatter.`
- `Summarize today's experiment from these voice notes and images.`

## Required Inputs

- Images, voice transcripts, text notes, dates, project names, experiment IDs, and operator/context information.
- Optional Obsidian vault or archive path.

## Expected Outputs

- Markdown experiment log with YAML frontmatter.
- Archived source-material references.
- Clean summaries, observations, and follow-up action items.

## Dependencies / API Keys / Local Environment

- Obsidian is optional but useful for vault workflows.
- Messaging or Feishu integration may require local credentials and bot setup.

## FAQ

- **Does it replace a formal lab notebook?** No. It helps structure and archive notes; institutional record requirements still apply.
- **Can it handle images without text?** Yes, but it should mark visual interpretation uncertainty.

## Related Skills

- [`nature-literature-pipeline`](../nature-literature-pipeline/README_EN.md)
- [`nature-data`](../nature-data/README_EN.md)
