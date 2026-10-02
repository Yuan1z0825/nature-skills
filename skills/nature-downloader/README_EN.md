# `nature-downloader` Skill

[中文说明](README.md)

`nature-downloader` obtains paper full text, PDFs, HTML/XML full text, or auditable download status through publisher APIs, lawful open-access routes, CNKI, or the user's own institution-authorized access.

## Workflow

1. First identify the paper language, publisher, and whether supplementary information is needed.
2. Prefer lawful publisher APIs when they are available; fall back to OA, repository, or institution-authorized access only when needed.
3. Record the access path, failure reason, and reusable configuration so batch jobs remain auditable.
4. Never bypass paywalls, DRM, CAPTCHAs, or two-factor verification, and never read or export browser cookies, passwords, localStorage, or session files.

## Supporting Information Confirmation

Every download command must choose one SI mode explicitly:

```bash
--no-si  # download the main text only
--si     # download the main text and available Supporting Information
```

If neither option is provided, the CLI returns `si_confirmation_required` and does not create output directories or download files. Passing both options fails argument validation. In batch jobs, the choice applies to the whole batch.

## Configuration

### Library and CNKI

Save the resource portal that the user actually uses:

```bash
python3 scripts/configure_school.py infer "https://example.edu/library/resources"
python3 scripts/configure_school.py url "https://example.edu/library/resources"
python3 scripts/configure_school.py show
python3 scripts/configure_school.py health --force
```

Regular school configuration is stored in `~/.config/lit-dl/school.json`.

### Publisher APIs

Configure publisher APIs only when non-OA English papers match those publishers:

- Elsevier: [Developer Portal](https://dev.elsevier.com/)
- Springer Nature: [API Access](https://dev.springernature.com/docs/quick-start/api-access/)
- IEEE: [Developer Registration](https://developer.ieee.org/member/register)

Store API keys through hidden input:

```bash
python3 scripts/configure_credentials.py set elsevier
python3 scripts/configure_credentials.py set springer_nature
python3 scripts/configure_credentials.py set ieee --fulltext-endpoint 'https://issued-endpoint.example/articles/{doi}'
python3 scripts/configure_credentials.py show
python3 scripts/configure_credentials.py validate elsevier
python3 scripts/configure_credentials.py delete elsevier
```

When the user has already provided a publisher API key in the conversation, the agent should save it through standard input without echoing it in commands, replies, or manifests:

```bash
python3 scripts/configure_credentials.py set elsevier --stdin
```

Otherwise prefer local hidden input. Institutional passwords, OTP codes, cookies, and session tokens are not handled by this rule. Secrets are stored in `~/.config/lit-dl/credentials.json` with owner-only permissions and are displayed only by their last four characters.

Unpaywall needs a compliant contact email:

```bash
python3 scripts/configure_credentials.py contact-email researcher@example.org
```

The email is stored as non-secret settings in `~/.config/lit-dl/settings.json`.

## Download Examples

Download main PDFs by DOI:

```bash
node scripts/batch_download.mjs \
  --dois "10.1007/s00122-021-03957-1,10.1111/pbi.14066" \
  --no-si \
  --out "./literature-downloads"
```

Chinese titles use the CNKI route only:

```bash
node scripts/batch_download.mjs \
  --title "乡村振兴背景下数字治理研究" \
  --no-si \
  --out "./literature-downloads"
```

For an exact English OA title:

```bash
node scripts/batch_download.mjs \
  --title "Attention Is All You Need" \
  --open-access \
  --no-si \
  --out "./literature-downloads"
```

Search by topic and download SI:

```bash
node scripts/batch_download.mjs \
  --topic "rice blast resistance gene" \
  --count 10 \
  --si \
  --out "./literature-downloads"
```

For a known lawful full-text URL:

```bash
node scripts/batch_download.mjs \
  --pdf-url "https://arxiv.org/pdf/1706.03762" \
  --title "Attention Is All You Need" \
  --no-si \
  --out "./literature-downloads"
```

Use `--language zh|en` or `--route cnki|open_access|elsevier|springer_nature|ieee|web_access` to override ambiguous metadata. A `--source-url` pointing to CNKI forces the Chinese CNKI route.

## API Failure and Web Access Fallback

When Elsevier, Springer Nature, or IEEE APIs return no entitlement or no full text, the downloader tries PMC, Unpaywall, publisher OA, and lawful repositories first. Only when API and OA routes fail does it return `api_fallback_confirmation_required`; after confirmation, rerun with the publisher-specific choice:

```bash
--api-fallback-web-for elsevier
--no-api-fallback-web-for springer_nature
```

For the whole batch, use `--api-fallback-web` or `--no-api-fallback-web`. Web Access reuses the user's logged-in Chrome institutional session; login, QR approval, OTP, and complex verification remain user actions.

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
