# `nature-literature-pipeline` Skill

[中文说明](README.md)

`nature-literature-pipeline` builds a recurring literature-discovery pipeline: multi-source retrieval, six-dimension scoring, deep-reading summaries, delivery, and archiving.

## What To Use It For

- Set up automated literature monitoring for a fixed research topic.
- Collect candidate papers from arXiv, OpenAlex, Crossref, Semantic Scholar, and related sources.
- Score candidates by topic match, methodological value, journal quality, network relation, engineering value, and archive value.
- Turn top papers into Chinese or English deep-reading digests for delivery.
- Maintain DOI, arXiv ID, topic tags, and read status to reduce duplicate reading.

## Relationship With `nature-academic-search`

`nature-academic-search` is for one-off search and citation checks; `nature-literature-pipeline` is for continuous subscription and periodic delivery. The former answers "find papers now"; the latter answers "keep watching this area."

## Typical Requests

- "Track new papers on marine concrete chloride diffusion and machine learning every morning."
- "Create a weekly literature pipeline for this keyword set."
- "Score papers from the last seven days, keep the Top 5, and archive them."

## What You Need To Provide

- Research topic, keywords, exclusion terms, priority journals, or priority authors.
- Delivery frequency, number of candidates per run, and number of deep-read papers.
- Output target, such as Markdown directory, Feishu/Telegram interface, or local archive folder.

## Outputs

- Candidate-paper table and deduplicated Top list.
- Deep-reading card for each key paper: problem, method, key data, limitations, and relation to your project.
- Reusable pipeline configuration, archive index, and failure/degradation notes.

## Boundaries

- Automatic delivery depends on local cron, messaging interfaces, or the user's configured scheduler.
- When full text is unavailable, the output is marked as `Abstract only` or `Metadata only`.
- Scores are not final judgments of paper quality; high-scoring candidates still need human reading.

## Related Skills

- `nature-academic-search`: one-off multi-source search, citation metrics, and strict external-citation audit.
- `nature-reader`: turn candidate papers into full Chinese-English reading materials.
