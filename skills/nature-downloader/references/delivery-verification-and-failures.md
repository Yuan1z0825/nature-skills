# Delivery, Verification, and Failure Handling

## Contents

- [Supporting Information](#supporting-information)
- [Verification and Reading](#verification-and-reading)
- [Zotero](#zotero)
- [Naming Convention](#naming-convention)
- [Failure Handling](#failure-handling)
- [To Confirm With The User on First Run](#to-confirm-with-the-user-on-first-run)


Load this reference when the user requests Supporting Information, when files are ready for
verification and delivery, or when an access attempt reaches a typed failure or retry state.

## Supporting Information

**Always confirm SI before file download.** Fetch SI only when the user explicitly chooses it (e.g. "连补充材料一起下", "include SI", "download supplementary", "把补充材料也下了"). When the user chooses no, pass `--no-si` and do not perform extra attachment navigation.

When the user does ask for supporting information, use this method:

1. Open the article landing page, not only the PDF page.
2. Extract all links with text or href matching:
   - `Supporting Information`
   - `Supplementary`
   - `Supplemental`
   - `/doi/suppl/`
   - `/suppl_file/`
   - `_si_`
   - `mmc1`, `mmc2` (Elsevier/ScienceDirect supplement pattern)
3. Download every PDF/DOCX/XLSX/video/data file that is clearly a legitimate supplement, using the browser context if needed.

For the WoS batch route, an explicit SI request maps to `--si`. When an exact title is known, pass it as both `--topic` and `--title` with `--count 1`. WoS + `--si` must:

- keep each paper in its own readable-title folder;
- place only the verified main PDF and clearly labelled SI files in that folder;
- preserve original attachment names when available;
- follow a supplementary landing page at most one level deep;
- exclude external repository links such as GitHub, Zenodo, Figshare, Dryad, and OSF;
- keep the main PDF and report `si.status = not_found` when no SI exists;
- report `partial` when some SI files fail without treating the main PDF as failed.

Do not apply the clean per-article folder behavior to CNKI, `--open-access`, bare `--pdf-url`, or direct `--dois` routes.

ACS fallback pattern, only after verifying the DOI and article page:

```text
https://pubs.acs.org/doi/suppl/<DOI>/suppl_file/<journal-code>_si_001.pdf
```

Do not invent supplement URLs as facts. If a guessed URL returns 404, record "not found" and inspect the article page.

## Verification and Reading

After downloading, verify every file.

For PDFs:

```powershell
$env:PYTHONUTF8='1'
python -X utf8 "$env:USERPROFILE\.claude\skills\nature-downloader\scripts\extract_pdf_text.py" `
  --pdf "D:\path\paper.pdf" `
  --pages 3
```

This should report page count and extracted text. The script also reconfigures stdout/stderr to UTF-8 internally to reduce Windows GBK failures. If extraction fails but the PDF is valid, try PyMuPDF, OCR, or the local `pdf` skill.

Minimum verification checklist:

- File exists and size is plausible.
- First bytes are `%PDF` for PDF files.
- Page count is nonzero.
- Extracted text includes the article title, abstract, or supporting information title.
- For HTML full text, saved HTML/text includes the article title or DOI, and the user-facing reply states that no valid PDF was available.
- Save a small manifest with DOI, title, source URL, download date, and supplement status when doing more than one paper.

## Zotero

Zotero import is useful for metadata, DOI, citation keys, and library organization, but it does not replace local PDF verification. If Zotero imports a paper, still check whether the PDF attachment is present and readable. If the user wants a project folder with full text, save PDFs explicitly to that folder.

## Naming Convention

Use readable filenames:

```text
FirstAuthor_Year_Journal_short-title.pdf
FirstAuthor_Year_Journal_short-title_SI.pdf
```

For project work, keep a folder like:

```text
文献自动下载/
  manifest.tsv
  PDFs/
  SupportingInformation/
  extracted_text/
```

## Failure Handling

If direct publisher navigation triggers ScienceDirect "Are you a robot?", Cloudflare, CAPTCHA, or another bot challenge:

- First, attempt automatic verification via `scripts/lib/anti-bot.mjs`.
- If auto-verification succeeds, continue the download normally.
- If auto-verification fails, record `verification_auto_failed` or `sciencedirect_robot_check`.
- Ask the user to solve it in Chrome.
- Then continue once from the same now-open page.
- If the same challenge immediately reappears, mark `do_not_auto_retry` and move on.

If shell `Invoke-WebRequest` or `curl` returns 403 but the PDF opens in Chrome:

- Use `browser_pdf_downloader.mjs`; this is the normal institutional-access case.

If a page shows publisher bot verification, CAPTCHA, Cloudflare, QR login, SMS/OTP, or another security challenge:

- Do not ask for or accept institutional credentials in chat. Publisher API keys follow the separate save-on-receipt rule in `../SKILL.md`.
- Pause and ask the user to complete the verification in Chrome.
- Record `publisher_verification_waiting_user` in `publisher_verification.tsv`, or `sciencedirect_robot_check` for ScienceDirect.
- Continue only after the user says the browser step is complete.

If a page shows institutional SSO, CAS, CARSI/Shibboleth, OpenAthens, SAML, federation/WAYF/机构选择, database login, or IP-login options:

- Do not ask for or accept institutional credentials in chat. Publisher API keys follow the separate save-on-receipt rule in `../SKILL.md`.
- If the user has explicitly authorized it and the browser has already filled credentials, click the visible login/confirm button once.
- Otherwise pause and ask the user to complete the login in the browser.
- Record `carsi_waiting_user` or `carsi_resolved_retry_needed` in `carsi_retry.tsv` as appropriate.

If the aggregation entry shows no full-text link:

- Try the publisher's own `Institutional login` / `机构登录` / CARSI/Shibboleth/OpenAthens route and select the user's institution when authorized.
- Try the DOI on the publisher page once an institutional session exists.
- Check open-access copies only from legitimate sources.
- Record `no_authorized_pdf_found` rather than seeking unauthorized mirrors.

If a page opens as `about:blank`:

- Treat it as a URL-fragment/encoding problem first, especially when the original URL contains `#` or `#!`.
- Reopen through `scripts/cdp_open_url.mjs --url "<full URL>" --wait`.
- Do not paste fragment-heavy URLs unquoted into shell commands or manually concatenate them into `/new?url=...` without URL encoding.

If `curl` is unavailable:

- Use PowerShell `Invoke-WebRequest` for simple proxy checks.
- Prefer the bundled Node.js helper scripts for CDP proxy actions because Node's `URLSearchParams` preserves nested URL fragments correctly.

If the session expires:

- Ask the user to re-authenticate through their institution/library route in the same browser, then reopen the publisher/database entry.

## To Confirm With The User on First Run

These items depend on the user's live institution/library session and should be confirmed once per deployment or institution profile:

1. The exact institutional login, federation, proxy, WebVPN, or database hosts that appear in the address bar.
2. The base URL / link pattern of the library aggregation or database entries the user actually uses.
3. Whether a federation/WAYF/机构选择, IP-login, or database-login step appears, and whether the user authorizes selecting the unambiguous institution/login option.
