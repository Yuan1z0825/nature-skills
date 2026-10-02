---
name: literature-push-template
description: "Use when building or running a customizable academic literature push workflow: search multiple scholarly sources, filter candidates, summarize top papers, deliver a concise daily/weekly digest, and optionally archive notes. Designed as a generic template for any research field, including LLM research."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, literature, monitoring, papers, digest, cron]
    related_skills: [arxiv, literature-pipeline]
---

# Literature Push Template

## Overview

Generic literature monitoring workflow to copy and customize for a research field such as LLMs, agents, alignment, evaluation, retrieval, multimodal systems, or any other domain.

Workflow: search scholarly sources → build candidate pool → deduplicate → score/filter → summarize top papers → deliver a concise digest → optionally archive raw notes.

This template intentionally contains no private chat IDs, API keys, local vault paths, or user-specific research context.

## Configuration To Customize

```yaml
research_profile:
  field: "LLM research"
  subtopics:
    - "language model agents"
    - "LLM evaluation"
    - "reasoning and planning"
    - "alignment and post-training"
    - "RAG and long-context systems"
    - "efficient inference and serving"

search:
  candidate_pool_size: 30
  final_selection_count: 5
  lookback_days: 7
  sources: [arxiv, openalex, crossref, semantic_scholar_optional]

keywords:
  include:
    - "large language model"
    - "LLM agent"
    - "language model reasoning"
    - "LLM evaluation"
    - "retrieval augmented generation"
    - "long context language model"
    - "post-training language model"
    - "preference optimization"
    - "tool use language model"
    - "multi-agent language models"
  exclude:
    - "CHANGE_ME"

important_authors_or_orgs:
  - "OpenAI"
  - "Anthropic"
  - "Google DeepMind"
  - "Meta AI"
  - "Stanford"
  - "Berkeley"
  - "CMU"
  - "Tsinghua"
  - "Peking University"

delivery:
  target: "CHANGE_ME"   # e.g. feishu:group, telegram, discord:#channel, local
  format: "short_digest"

archive:
  enabled: false
  root: "CHANGE_ME"
  write_wiki: false
```

## Source Priority

Use arXiv, OpenAlex, Crossref, and Semantic Scholar if available. Degrade gracefully if Semantic Scholar has no key or rate-limits.

## Deduplication

Deduplicate by DOI, arXiv ID, OpenAlex ID, then normalized title. Prefer the richer metadata record while preserving all stable links.

## Scoring Rubric

| Dimension | Weight |
|---|---:|
| Topic fit | 35 |
| Novelty / contribution | 20 |
| Method quality | 15 |
| Source / author signal | 10 |
| Practical value | 10 |
| Archive value | 10 |

Rules: no dimension exceeds its weight; total is the sum; display as `⭐ 8.7/10`; never output impossible scores like `11/10`.

## Reading Depth Labels

Every paper must show one of: Full text read, Abstract only, Metadata only, Project page / GitHub read.

## Digest Format

```markdown
📚 Literature Digest | {date} | {research field}
Candidate pool: {M} → selected: {N}

🏅 #{rank} | {title}
{venue/source}, {year} | {authors} | ⭐ {score}/10 | Reading: {reading_depth}
ID: {doi/arxiv/openalex if available}

💡 One-line takeaway: {why this matters}

🔬 What they did: {method, dataset, benchmark, system, or theory}

📊 Key result: {specific result if available; otherwise say what is missing}

🧭 Research value: {how this helps the configured research direction; include limitations}

📎 Link: {best stable link}
```

For LLM papers, note model family/scale, training or post-training method, benchmarks, baselines, code/data/model availability, serving constraints, and evaluation weaknesses or contamination risks.

## Cron Prompt Skeleton

```text
Run the literature-push-template workflow for {FIELD}.

Research focus:
- {SUBTOPICS}

Search:
- Look back {LOOKBACK_DAYS} days.
- Use arXiv, OpenAlex, Crossref, and Semantic Scholar if available.
- Build a candidate pool of up to {CANDIDATE_POOL_SIZE} papers.
- Deduplicate by DOI, arXiv ID, OpenAlex ID, and normalized title.

Filter:
- Score by topic fit 35, novelty 20, method quality 15, source/author signal 10, practical value 10, archive value 10.
- Select up to {FINAL_SELECTION_COUNT} papers.
- If fewer are worth reading, send fewer.

Output:
- Send a concise digest to {DELIVERY_TARGET}.
- Include reading-depth label for each paper.
- Do not modify any curated wiki or knowledge base.
- If archive is enabled, write raw paper notes only to {ARCHIVE_PATH}.
```

## Verification Checklist

- [ ] Research field, keywords, exclusions, and delivery target are configured.
- [ ] Candidates are deduplicated.
- [ ] Scores obey the 100-point rubric.
- [ ] Every paper has a stable link where possible and a reading-depth label.
- [ ] No private paths, chat IDs, API keys, or unrelated personal context are included.
- [ ] No curated wiki was modified unless explicitly requested.
