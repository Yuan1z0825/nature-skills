# FAIR Metadata Checklist

## Contents

- [Quick FAIR test](#quick-fair-test)
- [DataCite core fields](#datacite-core-fields)
- [Dataset README template](#dataset-readme-template)
- [Summary](#summary)
- [Files](#files)
- [Variables and units](#variables-and-units)
- [Methods and provenance](#methods-and-provenance)
- [Software and environment](#software-and-environment)
- [Access and licence](#access-and-licence)
- [Citation](#citation)
- [File organization](#file-organization)
- [Provenance prompts](#provenance-prompts)
- [Licence guidance](#licence-guidance)
- [Final audit](#final-audit)


Use this file to audit whether a dataset deposit is findable, accessible, interoperable, and
reusable enough for a Nature-style submission.

## Quick FAIR test

| Principle | Practical check |
|---|---|
| Findable | Dataset has a persistent identifier, rich title/abstract/keywords, searchable repository record, and metadata that names the data identifier. |
| Accessible | Identifier resolves through a standard protocol; access conditions are explicit; metadata stay public even if data are restricted. |
| Interoperable | Files use community formats where possible; metadata use shared vocabulary, units, identifiers, and qualified links to related data/code/publication. |
| Reusable | Licence, provenance, methods, variables, quality-control notes, version, and community-standard metadata are clear enough for reuse. |

## DataCite core fields

Mandatory fields commonly expected for DOI-style dataset records:

- Identifier
- Creator
- Title
- Publisher / repository
- Publication year
- Resource type

Strongly recommended when available:

- contributor and role
- description / abstract
- subject keywords
- funding reference
- related identifiers: manuscript preprint/article, code repository, protocol, previous dataset
- version
- licence / rights
- geolocation or temporal coverage for spatial/temporal data
- language

## Dataset README template

```text
# [Dataset title]

## Summary
[One-paragraph description of what the dataset contains and which manuscript results it supports.]

## Files
- [filename]: [contents, format, size, related figure/table]

## Variables and units
[Column/field name] | [definition] | [unit] | [allowed values/missing-value code]

## Methods and provenance
[How data were generated, collected, transformed, filtered, normalised, or aggregated.]

## Software and environment
[Software, package versions, scripts, notebooks, operating system or instrument software when relevant.]

## Access and licence
[Licence, access restrictions, data-use agreement, embargo, or controlled-access process.]

## Citation
[Preferred dataset citation.]
```

## File organization

- Use stable, descriptive filenames instead of local shorthand.
- Keep raw and processed data separate.
- Include a manifest for archives or large multi-file deposits.
- Map source data to exact figure panels and table numbers.
- Preserve units in column names or data dictionaries, not only in manuscript captions.
- Record missing-value codes and filtering decisions.
- Include checksums for large or critical files when the repository does not generate them.

## Provenance prompts

Ask the author:

- What instrument, survey, simulation, database, or processing pipeline produced each file?
- Which script or notebook converts raw data into each figure or statistical table?
- Which samples, time points, conditions, or participants were excluded, and why?
- What version of each third-party dataset was used?
- Are there licences, consent forms, data-use agreements, or ethics approvals that limit reuse?
- Has any data been transformed in a way that prevents reconstruction of the raw values?

## Licence guidance

- Prefer a standard open licence when data can be public.
- Use the repository's licence field rather than only writing licence text in the manuscript.
- Use CC0 or CC-BY-style terms only when appropriate for the data and institution.
- Do not apply an open licence to third-party or participant data unless the authors hold the right
  to do so.
- For code, use a software licence and archive a release when possible.

## Final audit

Block submission until these are resolved:

- no Data Availability statement for original research
- no identifier or stable access route for data supporting central conclusions
- sensitive data restriction without access procedure
- third-party data with no source or permission route
- public dataset with no licence or README
- claim that data are in the paper when figure source data are absent
- mismatch between manuscript statement, repository record, and supplementary files
