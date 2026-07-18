# `nature-downloader` Skill

[中文说明](README.md)

`nature-downloader` obtains paper full text, PDFs, HTML/XML full text, or auditable download status through publisher APIs, lawful open-access routes, CNKI, or the user's own institution-authorized access.

## Workflow

1. First identify the paper language, publisher, and whether supplementary information is needed.
2. Prefer lawful publisher APIs when they are available; fall back to OA, repository, or institution-authorized access only when needed.
3. Record the access path, failure reason, and reusable configuration so batch jobs remain auditable.
4. Never bypass paywalls, DRM, CAPTCHAs, or two-factor verification, and never read or export browser cookies, passwords, localStorage, or session files.

## What To Use It For

- Configure a school library, CARSI, EZproxy, WebVPN, or resource-portal entry point for first use.
- Prefer configured Elsevier, Springer Nature, or IEEE full-text APIs, then automatically try lawful OA sources when an API attempt fails.
- Reuse the user's logged-in Chrome institutional session to download legally accessible PDFs.
- Try to obtain full text from DOI, title, publisher page, PubMed page, or CNKI Chinese title.
- When explicitly requested, use `--si` with an exact WoS title to download supplementary files into a clean per-article folder.
- Save HTML/text or explain access status when no PDF is available.
- Report why access failed: no permission, user login required, CAPTCHA, human verification, or missing holdings.

## Typical Requests

- "Configure my university library entry point so future paper downloads can reuse it."
- "Use my logged-in Chrome session to download PDFs for these DOIs into the current project."
- "Use the authorized CNKI route for this Chinese paper; save it if possible and explain why if not."

## What You Need To Provide

- DOI, title, paper page link, or Chinese paper title.
- Library database entry point or logged-in Chrome session.
- Target output directory and naming preference.
- Whether Supporting Information should also be downloaded; it is off by default.

## Outputs

- Local PDF, HTML, or text file.
- Access path, OA/API fallback history, save path, integrity hash, and failure reason for each paper in `manifest.json`.
- Reusable school-entry configuration, usually at `~/.config/lit-dl/school.json`.

## Runtime and Dependencies

- First-time setup can use `scripts/configure_school.py` to identify and save resource entry points.
- Publisher API keys are configured with `scripts/configure_credentials.py`, stored separately with owner-only permissions, and never written to manifests.
- Real downloading depends on local browser login state and available web-access / CDP control.
- Chinese papers default to the user's authorized CNKI or library CNKI entry point.

## Boundaries

- The skill does not bypass paywalls, use mirror sites, or read/export cookies, passwords, localStorage, or session files.
- For a visible slider, checkbox, robot check, or simple verification button, it first makes at most two bounded attempts in the same authenticated browser tab and continues when the page confirms success.
- User action is required only after those attempts fail or for image selection, QR approval, SMS/OTP, passkeys, hardware keys, or two-factor authentication.
- Without legal access, the skill only reports status and possible alternatives.

## Related Skills

- `nature-reader`: turn obtained PDF/HTML into a full-paper reader.
- `nature-academic-search`: find target papers from title, DOI, or topic.
