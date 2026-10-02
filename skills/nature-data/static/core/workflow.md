# Workflow and output format

## Workflow

Use the complete workflow for a new data-sharing plan, full statement, or submission audit.
For a local wording edit or bounded statement audit, apply only relevant checks to the supplied
dataset identifiers, access conditions, and claims. Do not infer that the whole study is FAIR
or submission-ready from checking one statement.

1. Identify the target journal and article type. If journal-specific instructions conflict with this skill, follow the journal.
2. Inventory every dataset needed to support the main and supplementary results: generated raw data, processed data, figure source data, secondary data, software outputs, models, tables, images, and files underlying statistical analysis.
3. Classify each dataset into one access route: `public repository`, `controlled access repository`, `within paper or supplement`, `reused public source`, `third-party restricted`, `available on justified request`, or `not applicable`.
4. Choose repository and identifier strategy before drafting text. Prefer DOI, accession number, Handle, ARK, or stable repository record over personal websites and temporary cloud links.
5. Draft the Data Availability statement using explicit dataset-to-location mapping.
6. Add formal dataset citations for public data that support conclusions.
7. Run the FAIR and metadata audit before finalizing.
8. Return ready-to-paste statement text plus any unresolved fields the author must confirm.

## Output format

Unless the user asks for another format, return:

```text
Data Availability
[ready-to-paste statement]

Repository and citation actions
- [specific actions or "None"]

Missing information / risk flags
- [specific flags or "None"]

中文核对
- [用中文列出作者需要确认的字段或 "无"]
```

When auditing an existing statement, lead with blocking issues first, then provide a revised version.
