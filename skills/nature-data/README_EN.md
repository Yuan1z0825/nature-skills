# `nature-data` Skill

[中文说明](README.md)

## What It Does

- Prepares Nature-ready Data Availability statements, repository plans, dataset citations, and FAIR metadata checklists.

## When to Use It

- A manuscript needs a Data Availability statement.
- You need to choose a repository or accession strategy.
- The data include sensitive, restricted, proprietary, or third-party materials.

## Copy-Paste Prompts

- `Draft a Nature-ready Data Availability statement for this manuscript.`
- `Choose a repository plan for these datasets and explain what metadata are required.`
- `Audit this data-sharing plan against FAIR expectations.`

## Required Inputs

- Dataset descriptions, file types, repository names, accession numbers, restrictions, and manuscript context.
- Information about source data, supplementary data, code, and third-party datasets.

## Expected Outputs

- Data Availability statement drafts.
- Repository and accession checklists.
- Dataset citation and FAIR metadata guidance.
- Risk notes for restricted or sensitive data.

## Dependencies / API Keys / Local Environment

- No special runtime dependency for text-only drafting.
- Repository-specific validation may require internet access.

## FAQ

- **Can it invent accession numbers?** No. It should use provided accession numbers or leave clear placeholders.
- **Can restricted data still be described?** Yes. It should state access conditions, governance, and request paths clearly.

## Related Skills

- [`nature-writing`](../nature-writing/README_EN.md)
- [`nature-response`](../nature-response/README_EN.md)
- [`nature-reader`](../nature-reader/README_EN.md)
