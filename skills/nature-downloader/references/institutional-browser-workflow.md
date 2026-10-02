# Institutional Browser Workflow

## Contents

- [Recommended Web Access Workflow](#recommended-web-access-workflow)
- [Publisher Verification and ScienceDirect](#publisher-verification-and-sciencedirect)
- [Institutional Authentication Handoff and Retry](#institutional-authentication-handoff-and-retry)
- [Download PDF From Browser Context](#download-pdf-from-browser-context)


Load this reference only when lawful open-access sources are unavailable and the selected route
requires the user's institution-authorized browser session. It covers Web of Science discovery,
publisher verification, institutional authentication handoff, and PDF transfer from the browser
context.

## Recommended Web Access Workflow

Use this section only after legitimate OA sources are unavailable: directly for English publishers outside Elsevier/Springer Nature/IEEE, or after the user explicitly accepts Web Access fallback when both a supported publisher API and the OA fallback failed. Start from Web of Science or the configured library portal and reuse the user's authenticated browser session.

Before using the library route, check for legitimate open-access availability when the article metadata suggests OA or the user provides an OA/open journal paper. Use PMC, publisher OA links, arXiv, DOI landing pages with clear open PDF access, or a known lawful PDF URL. If an OA PDF is available, download and verify it directly, mark `open_access_downloaded`, and record the OA source in the manifest. Do not require institutional login for an article that is already openly available.

Important distinction: `--topic` is a Web of Science topic search, not an exact-title resolver. For a known exact title, especially conference/arXiv papers without DOI, prefer `--title "<exact title>" --open-access` or `--pdf-url` when the legitimate PDF URL is known. In testing, `--topic "Attention Is All You Need"` matched an unrelated HBR article first, while `--title "Attention Is All You Need" --open-access` correctly downloaded arXiv `1706.03762v7`.

Web of Science hosts to recognize: `webofscience.clarivate.cn`, `www.webofscience.com`, `*.webofknowledge.com`, `*.clarivate.com`. Note: WoS renders records inside **shadow DOM with a virtualized list** — when scraping manually you must pierce shadow roots and scroll to load more rows (the batch script already does this).

1. **Authenticate once**: open Web of Science via the library aggregation / institutional entry. If Web of Science or another database shows authentication choices such as institutional login, Shibboleth/OpenAthens/CARSI, CAS/SSO, or IP login, use the route the user normally uses. If credentials, QR, CAPTCHA, SMS/OTP, or unclear consent appears, follow **Institutional Authentication Handoff** below.
2. Confirm you are on the authenticated Web of Science search page (institutional name visible, search box present).
3. Search the paper by **DOI** when available, otherwise by **exact title**:
   - Set the search field to `DOI` or `Title`, paste the value, run the search.
   - Read the results page with `/eval` and pick the record that matches title + year + authors.
4. Open the matching record and read it with `/eval`.
5. Click the full-text route, in this order of preference:
   - `Free Full Text` / `Open Access` if present
   - library resolver links: `Find it at`, `SFX`, `OpenURL`, `Full Text Links`, `查看全文`, `Full Text available via`, database/provider names such as Ovid
   - publisher full-text link: `View Full Text`, the publisher name, or `View PDF`
   - The full-text link should inherit the institutional session, so the publisher often grants access without a second login. If a second institutional handoff appears, complete it once.
6. On the publisher page, find the PDF link (`PDF`, `View PDF`, `Download PDF`, `pdfft`, `/doi/pdf/`) and save it with `scripts/browser_pdf_downloader.mjs`.
7. If the full-text resolver opens readable HTML full text but no valid PDF is exposed, save the HTML/text, mark `full_text_html_available`, and tell the user plainly: "已获取 HTML 全文，但当前授权路径没有可下载 PDF." Do not mislabel an HTML page as a PDF; if a PDF probe returns HTML, move it to diagnostics and explain that no valid PDF was downloaded.
8. If the resolver/provider explicitly says the institution has no entitlement, mark `library_no_permission` and tell the user: "当前图书馆资源没有该文献全文权限." Do not hide this behind `failed_after_retry`.
9. **Do not download Supporting Information by default.** Only fetch SI if the user explicitly asked; otherwise just note whether SI exists (see `delivery-verification-and-failures.md`).
10. Record the route taken (OA source or WoS → SFX/OpenURL/full-text provider → publisher/database) in the manifest.

If Web of Science returns no record, or the record has no accessible full-text link, mark the paper `no_full_text_link` and tell the user. If the library route is found but denies entitlement, mark `library_no_permission`. Do not silently fall back to direct publisher navigation as if it were the same authorized route.

## Publisher Verification and ScienceDirect

ScienceDirect and some publisher platforms may show "Are you a robot?", CAPTCHA, Cloudflare, bot verification, or similar checks after repeated direct DOI navigation or automated tab opening. These pages are security and anti-automation challenges, not ordinary login confirmations.

Reduce the chance of triggering them by using a conservative access pattern:

1. Prefer the library aggregation / CARSI entry before direct `doi.org -> publisher` navigation.
2. Process ScienceDirect and other sensitive publishers one article at a time.
3. Keep a visible audit trail in the manifest; do not open many publisher tabs in parallel.
4. Wait for each page to settle before looking for `Download PDF`, `View PDF`, or `PDF`.
5. Reuse the same tab after the user completes a verification step instead of opening repeated new tabs.
6. Avoid retry loops. Use one attempt by default and no more than two attempts on the same tab before handing the page to the user.

When a publisher verification page appears:

1. First, **attempt automatic verification** via the built-in anti-bot module (`scripts/lib/anti-bot.mjs`). The module tries: simple click challenges, ScienceDirect robot check, Cloudflare Turnstile, slider CAPTCHA (including CNKI Geetest-style), and reCAPTCHA checkbox.
2. If auto-verification succeeds, continue the download from the resolved page.
3. If auto-verification fails:
   a. Stop automated actions on that tab.
   b. Record the paper with status `verification_auto_failed`. Use `sciencedirect_robot_check` only when no automatic interaction was possible.
   c. Tell the user which paper and tab need manual attention.
   d. After the user says the verification is complete, continue from the same tab and try the visible article/PDF route once.
   e. If verification immediately reappears, mark `do_not_auto_retry` and move on.

Create or update `publisher_verification.tsv` when publisher checks interrupt a batch. Use this header:

```text
id	project	title	doi	year	venue	publisher	status	source_url	current_url	next_action	notes
```

Suggested `next_action` values:

```text
user_complete_publisher_verification
retry_same_tab_after_user_confirms
try_aggregation_entry_route
try_authorized_oa_route
mark_do_not_auto_retry
```

## Institutional Authentication Handoff and Retry

Publishers and databases routed through CAS/SSO, CARSI/Shibboleth, OpenAthens, EZproxy, WebVPN, or IP authorization may redirect to an institutional login or database login page for the first authenticated access. This is expected and is not a reason to ask for the user's password.

When a page reaches an institutional login page, federation/WAYF selector, database login page, or IP-login prompt:

1. Stop automated actions on that tab.
2. Record the paper in `carsi_retry.tsv` with status `carsi_waiting_user`.
3. Tell the user exactly which tab/page needs attention, for example: "This page is at your institution/database login. If the browser has already filled credentials, I can click the visible login/confirm button once with your authorization; otherwise please complete it in the browser." If a federation/WAYF page asks which institution to use, ask the user to pick their institution, or do it only when the choice is unambiguous and credential-free and the user authorized it.
4. Do not read, store, or request the password, QR result, OTP, SMS code, CAPTCHA, cookie, or local/session storage.
5. If the user explicitly authorizes clicking because credentials are already filled, click only the visible login/confirm/continue button once. Do not type into fields or inspect hidden credential values. For credential-free options such as "IP login", click only when the user authorizes that route or has just completed it manually.
6. If QR login, SMS/OTP, CAPTCHA, Cloudflare, or publisher bot verification appears, stop and let the user complete it manually.
7. After the login/confirm step completes, refresh or continue from the same tab.
8. Re-detect whether the page is now a publisher article page, a PDF viewer, or another institutional handoff.
9. If resolved, download and verify the PDF/SI, then update the manifest status to `downloaded` or `downloaded_with_si`.
10. If it loops back to the same institutional/database login after a completed user login, record `failed_after_retry` with the observed reason and move on.

### Safe Institutional Auto-Confirm

The agent may click a saved-login confirmation button only when all conditions are true:

```text
1. The page is on an expected institutional, library, federation, or database domain for the user's configured route.
2. The user has explicitly authorized this action in the current conversation, for example: "可以点这个机构登录确认按钮".
3. The visible action is clearly a login/confirm/continue button, such as 登录, 登 录, 确认登录, 继续登录, Continue, Proceed, or Sign in.
4. There is no visible QR-only login, SMS/OTP field, push-approval prompt, password reset prompt, consent-to-share-new-data prompt, or account/security warning. (Slider CAPTCHAs and simple robot checks are now auto-attemptable — see Boundaries in `../SKILL.md`.)
5. The agent does not read, reveal, copy, store, type, or modify credentials.
```

A federation/WAYF/机构选择 page carries no credentials and may be selected when the institution is unambiguous and the user has authorized it. If any condition is unclear, pause and ask the user to handle that tab. Do not repeatedly click login; one click is enough to test whether the saved-login state works.

Create or update `carsi_retry.tsv` whenever institutional authentication blocks a batch. Use this header:

```text
id	project	title	doi	year	venue	publisher	failure_stage	status	source_url	current_url	next_action	notes
```

Suggested `next_action` values:

```text
user_complete_institution_login_in_chrome
select_institution_in_federation_wayf
retry_same_tab_after_user_confirms
repair_url_by_doi
try_aggregation_entry_route
mark_no_authorized_pdf
```

For a CARSI retry batch, process one or a few tabs at a time. Do not open many login tabs in parallel; it can confuse the user's session and increase publisher or SSO risk.

## Download PDF From Browser Context

Use the bundled script when a PDF URL opens in Chrome but direct shell download returns `403`, `401`, Cloudflare HTML, or a login page.

```powershell
$node = "$env:LOCALAPPDATA\OpenAI\Codex\bin\node.exe"
& $node "$env:USERPROFILE\.agents\skills\nature-downloader\scripts\browser_pdf_downloader.mjs" `
  --url "https://www.sciencedirect.com/science/article/pii/SXXXXXXXXXXXXXXXX/pdfft" `
  --out "D:\path\paper.pdf"
```

The script:

- Opens the URL in the user's controlled Chrome session unless `--target` is provided.
- Runs `fetch(location.href, { credentials: "include" })` inside the page.
- Transfers bytes in chunks through the local CDP proxy.
- Writes the binary file to disk.
- Verifies the `%PDF` signature by default.

Useful options:

```text
--url <url>          PDF URL to open and save
--target <targetId>  Existing Chrome target/tab id to use
--out <path>         Output PDF path
--proxy <url>        CDP proxy URL, default http://127.0.0.1:3456
--close              Close the tab after download if the script opened it
--allow-non-pdf      Save even when content does not start with %PDF
```
