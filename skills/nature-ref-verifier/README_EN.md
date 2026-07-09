# `nature-ref-verifier` Skill

[中文说明](README.md)

## What It Does

- Verifies reference lists across multiple sources and flags bibliographic inconsistencies such as author, title, year, volume, issue, page, and DOI mismatches.

## When to Use It

- You need to check whether a reference list contains fabricated, inconsistent, or malformed entries.
- You want a field-by-field verification table before submission.
- You need to distinguish minor formatting issues from serious metadata conflicts.

## Copy-Paste Prompts

- `Verify this reference list and flag author, title, year, volume, issue, page, and DOI problems.`
- `Check whether these references are real and return corrected metadata candidates.`
- `Audit these references before journal submission.`

## Required Inputs

- Reference list, BibTeX, RIS, DOI list, manuscript bibliography, or pasted citations.
- Optional target journal citation style.

## Expected Outputs

- Verification table with per-field comparisons.
- Severity labels for fabricated, conflicting, missing, or formatting-only issues.
- Corrected metadata candidates and source links when available.

## Dependencies / API Keys / Local Environment

- Internet or bibliographic-source access may be required for fresh verification.
- Some databases may require credentials.

## FAQ

- **Does it rewrite the bibliography automatically?** It should first report verified corrections; rewriting can be requested after review.
- **Can it prove a citation is fabricated?** It can flag strong evidence of non-existence or conflict, but should report source coverage and uncertainty.

## Related Skills

- [`nature-academic-search`](../nature-academic-search/README_EN.md)
- [`nature-citation`](../nature-citation/README_EN.md)
