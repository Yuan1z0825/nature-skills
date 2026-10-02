# Six-Dimension Scoring System

Used in the coarse-filtering stage (30 → 5 papers). Each paper is scored 0-100 across six weighted dimensions.

## Dimensions

| # | Dimension | Weight | What It Measures |
|---|-----------|:------:|------------------|
| 1 | Topic Match | 35 | How closely the paper aligns with core research questions |
| 2 | Methodological Value | 20 | Quality and applicability of methods (experimental design, analysis techniques) |
| 3 | Journal/Source Quality | 15 | Venue prestige, citation impact, credibility |
| 4 | Research Network Relevance | 10 | Connections to tracked authors, institutions, or active collaborations |
| 5 | Applied/Engineering Value | 10 | Practical utility: protocols, datasets, benchmarks, engineering insights |
| 6 | Archival Value | 10 | Long-term reference value: review potential, foundational status, teaching utility |

## Scoring Rules

1. Each dimension is capped at its weight — no overshooting
2. Total score must equal the sum of all six dimensions — recalculate, don't trust subagent arithmetic
3. Dimension 1 is the gate: papers scoring <10 on Topic Match are auto-rejected regardless of other scores

## Subagent Prompt Template

```
Score each of the following 30 papers on six dimensions (0-100 total):

1. Topic Match (max 35): [insert your research questions]
2. Methodological Value (max 20)
3. Journal Quality (max 15)
4. Network Relevance (max 10): [insert tracked authors/institutions]
5. Applied Value (max 10)
6. Archival Value (max 10)

For each paper, output:
{
  "title": "...",
  "scores": {"topic": X, "method": X, "journal": X, "network": X, "applied": X, "archival": X},
  "total": X,
  "rationale": "one sentence"
}

Return the top 5 papers by total score, sorted descending.
```

## Common Pitfalls

- Subagents may inflate Dimension 1 scores for well-known papers that aren't actually relevant — always verify
- Papers from prestigious journals can score high on Dimension 3 but be irrelevant (low Dimension 1) — the gate rule catches this
- The "Network Relevance" dimension is NOT about fame — it's about specific tracked authors/institutions the user cares about

## Calibration

After 2-3 pipeline runs, review the score distribution with the user:
- If top papers consistently score 90+, the rubric is too loose
- If no paper breaks 60, keywords may be too narrow or the field is sparse
- Adjust weights based on user feedback (e.g., if applied value matters more than journal prestige for their work)
