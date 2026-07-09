# `nature-downloader` Skill

[中文说明](README.md)

## What It Does

- Helps legally obtain academic full text and PDFs through library access, browser login state, institutional routes, and open-access sources.

## When to Use It

- You have a title, DOI, publisher URL, or database record and need the accessible full text.
- You need to use CARSI, Web of Science, library proxy, or an existing browser login state.
- You want an auditable path for how a PDF was obtained.

## Copy-Paste Prompts

- `Download the PDF for this DOI using legal library or open-access routes.`
- `Use my logged-in browser state to obtain this paper from Web of Science or the publisher page.`
- `Find the open-access version of this paper and save the PDF with metadata.`

## Required Inputs

- Paper title, DOI, publisher URL, or database link.
- Optional institution/library route and browser profile information.
- Target output directory and naming preference.

## Expected Outputs

- Downloaded PDF or access-status report.
- Source URL, access route, and metadata notes.
- Failure reason when access is unavailable.

## Dependencies / API Keys / Local Environment

- Library access or browser login may be required.
- Chrome or another supported browser may be needed for login-state workflows.
- The workflow must respect copyright, license, and institutional access rules.

## FAQ

- **Does it bypass paywalls?** No. It uses legal access paths such as library subscriptions, author manuscripts, and open-access copies.
- **What if no PDF is available?** It should return the best legal access route and explain the blocker.

## Related Skills

- [`nature-reader`](../nature-reader/README_EN.md)
- [`nature-academic-search`](../nature-academic-search/README_EN.md)
