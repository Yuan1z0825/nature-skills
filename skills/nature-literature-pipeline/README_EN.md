# `nature-literature-pipeline` Skill

[中文说明](README.md)

## What It Does

- Runs an automated literature-discovery pipeline with multi-source retrieval, scoring, deep-reading delivery, and local archiving.

## When to Use It

- You want daily or scheduled literature discovery for a topic.
- You need ranked papers, summaries, and archive-ready notes.
- You want a pipeline rather than a one-off literature search.

## Copy-Paste Prompts

- `Set up a daily literature push for this research topic.`
- `Run the literature pipeline for these keywords and rank papers by novelty and relevance.`
- `Archive today's top papers with summaries and source links.`

## Required Inputs

- Topic, keywords, sources, schedule, scoring preferences, and delivery target.
- Optional chat, Feishu, Obsidian, or local archive path configuration.

## Expected Outputs

- Ranked literature digest.
- Deep-reading notes and local archive records.
- Scheduled-task configuration guidance when supported.

## Dependencies / API Keys / Local Environment

- Search providers or MCP tools may require credentials.
- Hermes cron is local; the machine or profile must be running for scheduled tasks.
- Messaging integrations require local bot credentials.

## FAQ

- **Is this the same as nature-academic-search?** No. `nature-academic-search` is a search and verification skill; this is a recurring pipeline around discovery, scoring, and delivery.
- **Can it run in the cloud automatically?** Only if the selected agent/runtime is deployed there; local Hermes cron is not a cloud service by itself.

## Related Skills

- [`nature-academic-search`](../nature-academic-search/README_EN.md)
- [`nature-reader`](../nature-reader/README_EN.md)
- [`nature-experiment-log`](../nature-experiment-log/README_EN.md)
