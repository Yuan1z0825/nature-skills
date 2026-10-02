---
name: nature-downloader
description: Use when a user needs lawful academic full text, CNKI institutional access, English OA retrieval, publisher API access, institutional browser fallback, or supporting information downloads.
metadata:
  compatibility: Requires Node.js 22+ and Python 3. CNKI, Web Access, and SI routes additionally require the user's authenticated Chrome session and remote debugging. Uses only lawful OA, publisher API, and user-authorized institutional access.
---

# Nature Literature Downloader

This skill routes literature through lawful open-access, publisher-API, CNKI institutional, and browser-based institutional providers. `scripts/batch_download.mjs` is the orchestration entry point; school configuration, publisher credentials, metadata/OA resolution, provider downloads, content validation, and manifests are separate modules.

Verified routes are examples, not defaults. Every institution should start from the user's actual library resource URL, because resource portals, CAS callbacks, EZproxy, WebVPN, IP-authenticated database pages, and database detail pages reveal the live authorization path more reliably than a school name.

> **SI confirmation gate — do this first.** Before downloading any PDF, CAJ, HTML, XML, archive, or attachment, ask whether the user wants Supporting Information. An explicit request for SI counts as yes; an explicit request for正文 only counts as no. Otherwise ask once for the whole batch. Run the downloader with exactly one of `--si` or `--no-si`. Without either flag the script returns `si_confirmation_required` and does not create the output directory.

> **Main workflow.** Normalize the DOI/title and identify language and publisher before routing. Chinese literature always uses CNKI. For English Elsevier, Springer Nature, and IEEE articles with usable provider credentials, try the publisher API first and do not require an OA determination after a successful API download. If that API attempt fails, automatically check legitimate OA sources. Other English publishers check OA first, then use the institutional Web Access route when OA is unavailable.

```text
规范化 DOI/题名并识别语言、出版商
├─ 中文文献：直接走 CNKI
└─ 英文文献
   ├─ Elsevier / Springer Nature / IEEE，且已配置有效 Key
   │  ├─ 优先通过出版商 API 下载
   │  ├─ API 下载成功：结束，不强制判断 OA
   │  └─ API 下载失败：检查文章级 OA，再走 PMC / Unpaywall / 合法仓储
   └─ 其他出版商
      ├─ 检查文章级 OA
      └─ OA 不可用：走 Web Access 机构授权
```

> **Chinese literature is CNKI-only.** A Chinese title, `zh` metadata language, explicit CNKI source URL, or `--route cnki` must use CNKI even if another OA copy appears to exist. Reuse the user's current Chrome library/CNKI login state and prefer configured `discovery.cnki_url`. Never export cookies or collect the institutional password.

> **Publisher API fallback.** A valid API key does not guarantee full-text entitlement. When an Elsevier, Springer Nature, or IEEE API attempt returns no entitlement or no usable full text, automatically try legitimate OA sources first. Return `api_fallback_confirmation_required` and ask once whether to use Web Access only after both the publisher API and OA routes fail. Do not switch to institutional Web Access automatically.

> **Browser-state principle.** Authorized downloads depend on the exact browser profile where the user is logged in. If a proxy, CDP session, or browser automation tool opens a fresh profile or a different browser with no login state, do not treat the failure as missing library permission. Switch to a control path that reuses the user's active browser session, or ask the user to authenticate in the controlled browser instance.

> **Format principle.** PDF, HTML full text, and database-native formats such as CAJ are different deliverables. If the user asks for PDF only, require a real PDF link or `%PDF` response and report `no_authorized_pdf_found` / `pdf_fetch_failed` when none exists. Do not save CAJ, HTML, or a login page as if it were a PDF.

## Download Intake and First-Run Configuration

For every download request, first establish the paper list and ask:

```text
是否同时下载这些文献的 Supporting Information（SI，补充材料）？
```

Do metadata lookup before this question only when needed to identify the requested papers. Do not download files until the answer is known. Configure a library only when the selected route is CNKI or Web Access. Configure a publisher API only when the selected English article belongs to Elsevier, Springer Nature, or IEEE; an OA determination is not required before trying a configured provider API.

### Paid Library Resource Configuration

Ask for the library resource URL the user actually uses:

```text
请发你平时进入图书馆电子资源/数据库的平台链接。
可以是资源门户、数据库列表、Web of Science 入口、某个数据库详情页，
或跳转到统一身份认证的登录链接。
```

Then infer the authorization route from the URL before saving config:

```bash
python3 scripts/configure_school.py infer "https://example.edu/library/resources"
python3 scripts/configure_school.py url "https://example.edu/library/resources"
python3 scripts/configure_school.py show
python3 scripts/configure_school.py health --force
```

The distributed skill contains no school presets. If the user cannot provide a resource URL, ask them to locate their institution's library/database entry instead of guessing a school-specific domain.

The default config path is:

```text
~/.config/lit-dl/school.json
```

For tests or isolated profiles, set:

```bash
LIT_DL_CONFIG_DIR=/path/to/configdir
```

The downloader reads this config automatically. If `discovery.web_of_science_url` is present, `scripts/batch_download.mjs` uses it as the Web of Science entry; otherwise it falls back to `https://www.webofscience.com/wos/woscc/basic-search`.

For Chinese literature, the downloader also reads `discovery.cnki_url` when present. If absent, `scripts/batch_download.mjs --title "<中文题名>"` falls back to `https://kns.cnki.net/kns8s/defaultresult/index`.

### API-First and Open-Access Fallback

For an English article, identify its publisher before deciding when to resolve article-level OA:

1. Collect a DOI, PMID, exact title, article URL, or a definite paper list, then normalize its metadata and publisher.
2. If it belongs to Elsevier, Springer Nature, or IEEE and usable provider credentials are configured, try that publisher API first. On success, record `accessMode: publisher_api` and `oa_status: not_checked_api_first`; do not run OA resolution only to label the article.
3. If the publisher API fails, automatically search legitimate OA sources such as PMC, Unpaywall, publisher OA pages, arXiv, and other lawful repositories or clearly open PDF URLs. Preserve the failed API attempt in the manifest.
4. For all other English publishers, search those legitimate OA sources before Web Access.
5. For an exact title or an explicit OA-only request, prefer:

   ```bash
   node scripts/batch_download.mjs --title "<exact title>" --open-access --no-si --out "<project>"
   ```

   Use `--pdf-url` when the user supplies a known legitimate OA PDF URL.
6. Verify the downloaded file and record the source. Mark a successful PDF as `open_access_downloaded`.
7. If no lawful OA full text is found, mark `oa_not_found`. For a supported publisher whose API already failed, request confirmation before Web Access. For another publisher, continue to Web Access. If `--route open_access` was explicitly requested, stop after the OA result.

### Publisher API Credentials

Configure credentials lazily, only when the route first needs them:

```bash
python3 scripts/configure_credentials.py set elsevier
python3 scripts/configure_credentials.py set springer_nature
python3 scripts/configure_credentials.py set ieee --fulltext-endpoint 'https://issued-endpoint.example/articles/{doi}'
python3 scripts/configure_credentials.py set elsevier --stdin
python3 scripts/configure_credentials.py show
python3 scripts/configure_credentials.py validate <provider>
python3 scripts/configure_credentials.py delete <provider>
python3 scripts/configure_credentials.py contact-email researcher@example.org
```

Give the user the official registration link: Elsevier `https://dev.elsevier.com/`, Springer Nature `https://dev.springernature.com/docs/quick-start/api-access/`, or IEEE `https://developer.ieee.org/member/register`.

Do not proactively ask the user to paste an API key into chat. If the user voluntarily sends a publisher API key, treat that as authorization to save that exact key: do not reject it, ask them to regenerate it, or repeat it back. Pass it to `configure_credentials.py set <provider> --stdin`, keep it out of command-line arguments, logs, replies, and manifests, then report only the masked confirmation and validation status. The local hidden prompt remains the preferred path when the key has not already been provided. IEEE Metadata API access is not paid full-text access; require the issued Full-Text Access endpoint/template before treating IEEE as downloadable through the API. Secrets are stored in `~/.config/lit-dl/credentials.json` with mode `0600`.

## Resource URL Triage

Classify the user-provided URL before choosing an access path:

```text
cas.* / /authserver/login        CAS / SSO login page; inspect service= callback, then return to the service portal
idp/shibboleth / carsi           CARSI / Shibboleth institutional route
ezproxy / libproxy               EZproxy remote-access proxy
webvpn / vpn                     WebVPN route
metaersp / metaauth / uas        Library resource aggregation portal
webofscience / sciencedirect     Database or publisher entry; check whether it was reached through a portal
```

If the URL is a login page with a `service=` parameter, treat the callback host as the resource service and do not make the login page the whole workflow. For example, `https://login.university.example/authserver/login?service=https://resources.university.example/callback` means the identity service returns to the user's resource portal after authentication.

## Institution-Specific Domains

Confirm against what actually appears in the user's address bar; correct these for each institution instead of assuming a preset is complete.

```text
Library home / aggregation:  library.example.edu, resources.example.edu
Discovery/database entry:    webofscience.com, clarivate.com, cnki.net, sciencedirect.com, provider.example.com
Unified identity / SSO:      sso.example.edu, cas.example.edu, idp.example.edu
Federation / WAYF:           ds.carsi.edu.cn, wayf.example.org, shibboleth/openathens hosts
Proxy / WebVPN:              ezproxy.example.edu, webvpn.example.edu
```

Treat configured institutional login, federation, proxy, and database-login hosts as sign-in stages. Do not treat reaching them as a final failure.

## Boundaries

Use only the user's legitimate institutional access. Do not bypass paywalls, DRM, or two-factor authentication.

**Verification-first rule:** When a visible slider, checkbox, robot check, or simple verification control appears in the user's authenticated Chrome session, attempt it in the browser before asking the user to intervene. Keep the attempt bounded (at most two attempts on one tab), verify that the challenge disappeared, and continue from that same tab when successful.

- Slider/drag challenges (including CNKI puzzle sliders): estimate the visible travel distance and simulate a gradual drag.
- ScienceDirect robot checks, managed Turnstile, and reCAPTCHA checkbox stages: try the visible checkbox once.
- Simple `Continue`, `Verify`, or equivalent visible controls: click once, then re-check the page state.

**User handoff:** Ask the user only after the bounded attempt fails, or immediately when the page requires secret or identity-bearing input such as an image-selection answer, QR approval, SMS/OTP, passkey, hardware key, or two-factor authentication. Keep the challenged tab open and never ask the user to paste credentials or codes into chat.

Avoid unbounded or indiscriminate downloading. Process only the definite paper list confirmed by the user, apply provider-friendly pacing, and leave a clear audit trail of what was downloaded, from where, and whether supporting information was found.

Do not ask the user to paste institutional passwords, database passwords, OTP codes, recovery codes, or session tokens into chat or terminal. If the user offers one of those identity-bearing secrets, decline and use the handoff-login workflow instead. Publisher API keys follow the separate save-on-receipt rule above.

Exception for saved institutional login pages: if the user explicitly says that the browser has already filled credentials and authorizes clicking the visible login/confirm button, the agent may click that button once on the expected institutional SSO / CAS / CARSI / Shibboleth page without reading, copying, or typing any credential. This exception does not apply to CAPTCHA, QR login, SMS/OTP, publisher bot checks, consent/security warnings, or any page outside the expected institutional login flow.

Do not inspect or export cookies, passwords, local storage, browser profiles, or session files. Use the browser's already-authenticated page context only.

## Preconditions

Before attempting downloads, confirm the conditions that apply to the selected access branch.

For the OA-only branch, confirm the target paper identifier/list, output folder, Node.js 22+, and Python 3 when PDF verification needs it. Do not require a library configuration or institutional browser login.

For the paid-library branch, confirm these conditions:

1. The browser that holds the user's library/database login state is open on the user's machine.
2. The school configuration exists and is valid.
   - Run `python3 scripts/configure_school.py show`.
   - If missing, run `python3 scripts/configure_school.py preset "<school name>"` or guide the user through `src/wizard.py`.
3. The user has personally logged in to their institution/library route in that same browser, and can reach the library aggregation service, target database, or discovery entry.
4. The browser-control path can reuse that same logged-in browser profile.
   - For Chrome CDP, ask the user to open `chrome://inspect/#remote-debugging` and enable remote debugging for the current browser instance.
   - If CDP attaches to a stale browser, a temporary profile, or a different browser, use a browser-control channel that can reuse the user's active session instead of launching a new profile.
5. The environment can run Node.js 22+.
   - Try `node --version`.
   - If `node` is not on PATH in Codex Desktop, try `%LOCALAPPDATA%\OpenAI\Codex\bin\node.exe`.
6. The environment can run Python 3 for configuration and PDF text verification.
   - Try `python3 --version`.
   - Install Python helpers with `pip install -r requirements.txt` when needed.
7. The web-access CDP proxy is available or can be started.
   - Typical Claude Code path: `%USERPROFILE%\.claude\skills\web-access-main\scripts\check-deps.mjs`.
   - Typical shared agent path: `%USERPROFILE%\.agents\skills\web-access-main\scripts\check-deps.mjs`.
   - In Codex-only setups also check `%USERPROFILE%\.codex\skills\web-access-main\scripts\check-deps.mjs`.
8. The user has approved the target output folder.

If Claude Code says this skill is not installed, install or copy it to:

```powershell
$env:USERPROFILE\.claude\skills\nature-downloader
```

Codex and other agent setups may instead use `.codex\skills` or `.agents\skills`; treat the three locations as install targets, not as different skill versions.

## Batch Scope

Definite DOI/title/PMID lists are supported without a fixed per-batch paper-count recommendation.

Operational safeguards:

- pace requests appropriately for each provider and maintain the manifest throughout the batch
- attempt visible verification controls first; stop after at most two failed attempts, on institutional login expiry, or when an unusual/security-sensitive prompt appears

Do not turn a broad keyword search into unlimited automatic downloading. Do not download whole journal issues, volumes, or large result sets.

## Status Categories

Classify every paper into one of these statuses, and keep the status in the manifest:

```text
downloaded
downloaded_with_si
open_access_downloaded
full_text_html_available
available_not_downloaded
native_fulltext_downloaded
si_confirmation_required
credentials_missing
credentials_invalid
api_not_entitled
api_fulltext_unavailable
api_fallback_confirmation_required
oa_not_found
oa_resolution_inconclusive
metadata_ambiguous
carsi_waiting_user
carsi_resolved_retry_needed
publisher_verification_waiting_user
sciencedirect_robot_check
retry_after_user_verification
verification_auto_passed
verification_auto_failed
do_not_auto_retry
url_needs_repair
library_no_permission
no_full_text_link
publisher_blocked_waiting_user
no_authorized_pdf_found
failed_after_retry
```

Use `verification_auto_passed` when an automatic CAPTCHA/slider/robot check was successfully solved by the skill, and the download then proceeded normally.

Use `verification_auto_failed` when auto-verification was attempted but could not pass the challenge. This is a user-handoff status, not a final failure.

Use `carsi_waiting_user` only when the browser is visibly at an institutional SSO / CAS / CARSI-Shibboleth / OpenAthens / database authentication page. Do not treat this as a final failure.

Use `publisher_verification_waiting_user` or `sciencedirect_robot_check` when a publisher page shows a verification challenge but no automatic interaction was possible. When a bounded automatic attempt was made and failed, use `verification_auto_failed` instead. None of these is a final download failure.

Use `open_access_downloaded` when a legitimate open-access route such as PMC, the publisher's OA PDF, arXiv, or another lawful open PDF source provides the downloaded PDF without institutional authorization.

For a successful API-first download, record `oa_status: not_checked_api_first`; this means OA resolution was intentionally skipped, not that the article is non-OA. Use `api_fallback_confirmation_required` only after a supported publisher API attempt and its automatic OA fallback both fail.

Use `full_text_html_available` when the library/full-text resolver grants access to a readable HTML full text but no valid PDF link or `%PDF` response is available. This is a successful full-text access result, not a PDF download. Save the HTML/text if the user asked for the article, and explicitly tell the user that the PDF was not available through the current authorized route.

Use `library_no_permission` when the library portal, SFX/OpenURL resolver, database, or publisher page clearly says the user's institution has no full-text entitlement for the paper. Tell the user plainly that the current library resources do not have permission for this article. Do not retry direct publisher access as if it were a temporary network problem.

## Start Browser Control

Use the web-access CDP proxy when it can attach to the same logged-in browser instance the user is using. If the task depends on existing login state and CDP opens a blank/new profile, prefer a browser-control channel that reuses the user's active browser session.

On Windows PowerShell:

```powershell
$node = "node"
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  $node = "$env:LOCALAPPDATA\OpenAI\Codex\bin\node.exe"
}
$checkDepsCandidates = @(
  "$env:USERPROFILE\.claude\skills\web-access-main\scripts\check-deps.mjs",
  "$env:USERPROFILE\.agents\skills\web-access-main\scripts\check-deps.mjs",
  "$env:USERPROFILE\.codex\skills\web-access-main\scripts\check-deps.mjs"
)
$checkDeps = $checkDepsCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $checkDeps) { throw "web-access-main/scripts/check-deps.mjs not found" }
& $node $checkDeps
```

Then test:

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:3456/targets" -TimeoutSec 10
```

If this hangs or fails:

- Ask the user to confirm the remote debugging checkbox.
- Check `%TEMP%\cdp-proxy.log`.
- If targets appear but the database/library page is unauthenticated, suspect a stale CDP endpoint, wrong browser, or fresh browser profile before suspecting missing library permission.
- Do not attempt to read Chrome session files.

## Fast Batch Path (default for 2+ papers — fast & token-efficient)

For anything beyond a single paper, run `scripts/batch_download.mjs` instead of driving the browser step-by-step. OA and publisher APIs run without CDP; CNKI, Web Access, and requested SI lazily attach to the authenticated browser. Large DOMs and file bytes remain inside the scripts.

The script reads `~/.config/lit-dl/school.json` automatically. When the config contains `discovery.web_of_science_url`, that URL is used as the Web of Science entry; otherwise the script falls back to its compiled default Web of Science URL.

```bash
# by topic (collects N records from Web of Science Core Collection):
node scripts/batch_download.mjs --topic "rice blast resistance gene" --count 10 --no-si --out "<project>"
# by explicit DOIs:
node scripts/batch_download.mjs --dois "10.1007/s00122-021-03957-1,10.1111/pbi.14066" --no-si --out "<project>"
# by exact open-access title (arXiv fallback, useful for DOI-less papers):
node scripts/batch_download.mjs --title "Attention Is All You Need" --open-access --no-si --out "<project>"
# by Chinese exact title (default CNKI route):
node scripts/batch_download.mjs --title "乡村振兴背景下数字治理研究" --no-si --out "<project>"
# by Chinese exact title, PDF only:
node scripts/batch_download.mjs --title "乡村振兴背景下数字治理研究" --cnki-format pdf --no-si --out "<project>"
# by Chinese exact title with a library-provided CNKI entry:
node scripts/batch_download.mjs --title "乡村振兴背景下数字治理研究" --cnki-url "https://kns.cnki.net/kns8s/defaultresult/index" --no-si --out "<project>"
# by known PDF URL:
node scripts/batch_download.mjs --pdf-url "https://arxiv.org/pdf/1706.03762" --title "Attention Is All You Need" --no-si --out "<project>"
# replace --no-si with --si only after the user explicitly requests SI
```

Output includes `{ summary, manifest, results }`. The script writes `<project>/manifest.json` with route, OA evidence, access mode, format, MIME, bytes, SHA-256, SI choice, and typed failures; secret-looking fields are removed recursively. PDFs go under `PDFs/`, native HTML/XML under `FullText/`, CAJ under `CNKI/`, and supplements under `SupportingInformation/`.

**Token discipline (applies to all paths):** never `eval` a whole page DOM, search result, or PDF/SI bytes back into the agent context. Keep large data inside Node/`scripts/*.mjs` and surface only compact status. Reserve interactive `/eval` + `cdp_open_url.mjs` for the single-paper route below or for diagnosing one stuck paper after the batch run.

## Advanced Browser and Delivery Routes

Keep this router compact and load the detailed operational references only when their conditions
apply:

- Load [references/institutional-browser-workflow.md](references/institutional-browser-workflow.md)
  when legitimate OA and applicable publisher-API routes are exhausted and the task needs Web of
  Science, an institution-authorized browser session, publisher verification, an authentication
  handoff, or browser-context PDF transfer.
- Load
  [references/delivery-verification-and-failures.md](references/delivery-verification-and-failures.md)
  when the user requests Supporting Information, downloaded files need final verification and
  naming, or an access attempt reaches a typed failure or retry state.

The boundaries, SI confirmation gate, browser-state principle, status semantics, and token
discipline in this router remain mandatory when either reference is loaded. Do not treat the
references as permission to bypass access controls or to expose credentials, cookies, or session
data.
