#!/usr/bin/env node
// Institution-neutral literature downloader.
//
// Runs the whole chain inside Node + the web-access CDP proxy, so large data
// (search DOMs, PDF bytes) never enters the agent's context. Only compact
// per-paper status is printed. This is the token-efficient fast path.
//
// Usage:
//   Every download requires exactly one of --si / --no-si.
//   node batch_download.mjs --topic "<query>" --count 10 --out <dir> --no-si
//   node batch_download.mjs --dois 10.x/a,10.y/b --out <dir> --si
//   node batch_download.mjs --title "<exact title>" --out <dir> --no-si
//   node batch_download.mjs --pdf-url "https://..." --title "<title>" --out <dir> --no-si
//   options: [--proxy http://127.0.0.1:3456] [--debug] [--legacy-status]
//
// Boundaries: uses only the user's already-authenticated browser session.
// Stops at institutional SSO / CARSI pages and never handles credentials. For visible
// verification widgets it makes a bounded attempt before reporting a handoff.
// Main PDF only by default; --si also fetches supplements.

import fs from "node:fs";
import crypto from "node:crypto";
import path from "node:path";
import { pathToFileURL } from "node:url";
import {
  DEFAULT_PROXY,
  healthCheck,
  evalJs,
  newTab,
  navigate,
  closeTab,
  listTargets,
  click,
  scroll,
  waitForComplete,
  proxyGet,
} from "./lib/cdp-utils.mjs";
import { classifyWall, STATUS, isSuccess } from "./lib/status-codes.mjs";
import { fetchToFile, fetchAnyToFile } from "./lib/pdf-utils.mjs";
import { handleVerification } from "./lib/anti-bot.mjs";
import {
  DEFAULT_DISCOVERY_URL,
  discoveryUrlFromConfig,
  loadSchoolConfig,
  schoolSummary,
} from "./lib/school-config.mjs";
import { findArxivByTitle } from "./lib/open-access.mjs";
import {
  articleBundleDirectory,
  downloadWosSupportingInformation,
  exactArticleTitleMatch,
  safeArticleTitle,
  shouldUseCleanWosBundle,
  wosSearchQuery,
} from "./lib/wos-supporting-information.mjs";
import {
  DEFAULT_CNKI_URL,
  createCnkiTransport,
  downloadCnkiDirectUrl,
  downloadCnkiTitle,
  looksChinese,
} from "./lib/cnki.mjs";
import {
  classifyPublisher,
  chooseDirectUrlRoute,
  hasUsablePublisherCredentials,
  parseSiChoice,
  chooseRoute,
  isChineseLiterature,
} from "./lib/routing.mjs";
import { fetchCrossrefByDoi, findCrossrefByTitle } from "./lib/metadata.mjs";
import { downloadOpenAccessArticle } from "./lib/open-access-provider.mjs";
import { downloadPublisherArticle } from "./lib/publisher-providers.mjs";
import { providerCredentials } from "./lib/credentials.mjs";
import { loadSettings } from "./lib/settings.mjs";
import { saveFullTextResponse } from "./lib/direct-download.mjs";
import { writeManifest } from "./lib/manifest.mjs";

// Core Collection only: journal articles that carry DOIs (avoids Derwent/patent records).
const WOS = DEFAULT_DISCOVERY_URL;

export function parseArgs(argv) {
  const a = { out: ".", si: false, noSi: false, proxy: DEFAULT_PROXY, debug: false, legacyStatus: false };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    if (k === "--topic") a.topic = argv[++i];
    else if (k === "--title") a.title = argv[++i];
    else if (k === "--pdf-url") a.pdfUrl = argv[++i];
    else if (k === "--open-access") a.openAccess = true;
    else if (k === "--cnki-url") a.cnkiUrl = argv[++i];
    else if (k === "--cnki-format") a.cnkiFormat = argv[++i];
    else if (k === "--dois") a.dois = argv[++i].split(",").map((s) => s.trim()).filter(Boolean);
    else if (k === "--count") a.count = Number(argv[++i]);
    else if (k === "--out") a.out = argv[++i];
    else if (k === "--si") a.si = true;
    else if (k === "--no-si") a.noSi = true;
    else if (k === "--language") a.language = argv[++i];
    else if (k === "--route") a.route = argv[++i];
    else if (k === "--unpaywall-email") a.unpaywallEmail = argv[++i];
    else if (k === "--source-url") a.sourceUrl = argv[++i];
    else if (k === "--api-fallback-web") a.apiFallbackWeb = true;
    else if (k === "--no-api-fallback-web") a.apiFallbackWeb = false;
    else if (k === "--api-fallback-web-for") a.apiFallbackWebFor = argv[++i].split(",").map((s) => s.trim()).filter(Boolean);
    else if (k === "--no-api-fallback-web-for") a.noApiFallbackWebFor = argv[++i].split(",").map((s) => s.trim()).filter(Boolean);
    else if (k === "--proxy") a.proxy = argv[++i].replace(/\/$/, "");
    else if (k === "--debug") a.debug = true;
    else if (k === "--legacy-status") a.legacyStatus = true;
    else throw new Error("unknown arg " + k);
  }
  const primaryModes = [a.topic, a.pdfUrl, a.dois?.length].filter(Boolean).length;
  if (primaryModes > 1 || (a.title && a.dois?.length)) {
    throw new Error("--topic, --pdf-url, and --dois are mutually exclusive; --title may accompany --topic or --pdf-url");
  }
  if (a.cnkiFormat && !["pdf", "any"].includes(a.cnkiFormat)) {
    throw new Error("--cnki-format must be pdf or any");
  }
  if (a.route && !["cnki", "open_access", "elsevier", "springer_nature", "ieee", "web_access"].includes(a.route)) {
    throw new Error("--route must be cnki, open_access, elsevier, springer_nature, ieee, or web_access");
  }
  parseSiChoice(a);
  if (!a.topic && !a.title && !a.pdfUrl && !a.dois?.length) throw new Error("one of --topic, --title, --pdf-url, or --dois is required");
  if (a.topic && a.count === undefined) a.count = 10;
  return a;
}

export function selectBatchDois(dois = [], count) {
  const unique = [...new Set(dois)];
  return count === undefined ? unique : unique.slice(0, count);
}

function cnkiUrlFromConfig(config, argUrl) {
  return (
    argUrl ||
    config?.discovery?.cnki_url ||
    config?.discovery?.cnki ||
    DEFAULT_CNKI_URL
  );
}

async function handleWosAuthPreference(proxy, target) {
  const info = await proxyGet(proxy, "/info", { target }, 8000).catch(() => ({}));
  const marker = `${info.url || ""} ${info.title || ""}`;
  if (!/AUTH_PREFERENCE_ERROR|身份验证首选项|Authentication Preference/i.test(marker)) {
    return false;
  }
  const clicked = await evalJs(
    proxy,
    target,
    `(()=>{const r=document.querySelector('#radio-shibboleth,input[value="shibboleth"]');if(r)r.click();const b=[...document.querySelectorAll('button,a,input[type=button],input[type=submit]')].find(e=>/(继续|Continue)/i.test(e.innerText||e.value||''));if(b)b.click();return !!b;})()`
  ).catch(() => false);
  if (clicked) {
    await new Promise((r) => setTimeout(r, 3000));
    await waitForComplete(proxy, target);
  }
  return Boolean(clicked);
}

// --- WoS: search a topic, return the first N full-record URLs ---
async function wosRecordUrls(proxy, topic, count, debug, discoveryUrl = WOS) {
  const tabs = await listTargets(proxy);
  let target = (tabs.find((t) => /webofscience\./i.test(t.url || "")) || {}).targetId;
  if (target) await navigate(proxy, target, discoveryUrl);
  else target = (await newTab(proxy, discoveryUrl)).targetId;
  await waitForComplete(proxy, target);
  await handleWosAuthPreference(proxy, target);
  await new Promise((r) => setTimeout(r, 1500));
  await evalJs(
    proxy,
    target,
    `(()=>{const a=document.querySelector('#onetrust-accept-btn-handler');if(a)a.click();return 1;})()`
  ).catch(() => {});
  await evalJs(
    proxy,
    target,
    `(()=>{const i=document.querySelector('#search-option-0');if(!i)return 0;const s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;s.call(i,${JSON.stringify(topic)});i.dispatchEvent(new Event('input',{bubbles:true}));return 1;})()`
  );
  await click(proxy, target, 'button[data-ta="run-search"]');
  // WoS renders records in shadow DOM + a virtualized list, so we walk shadow roots
  // and scroll to load more rows until we have enough record links.
  const collect = `(()=>{const out=new Set();(function w(r){r.querySelectorAll('*').forEach(e=>{if(e.shadowRoot)w(e.shadowRoot);if(e.tagName==='A'&&/\\/full-record\\//.test(e.href||''))out.add(e.href);});})(document);return JSON.stringify([...out]);})()`;
  let urls = [];
  let lastInfo = null;
  for (let i = 0; i < 25; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    const inf = await proxyGet(proxy, "/info", { target }, 8000).catch(() => ({}));
    lastInfo = inf;
    if (!/\/summary\//.test(inf.url || "")) continue;
    const found = JSON.parse((await evalJs(proxy, target, collect)) || "[]");
    if (found.length > urls.length) urls = found;
    if (urls.length >= count * 2) break;
    await scroll(proxy, target, "bottom");
  }
  if (debug && urls.length === 0) {
    const html = await evalJs(
      proxy,
      target,
      `document.documentElement.outerHTML.slice(0,5000)`
    ).catch(() => "");
    process.stderr.write(`[debug][wos] no records found. url=${lastInfo?.url||'?'} title=${lastInfo?.title||'?'}\n`);
    process.stderr.write(`[debug][wos] html snippet: ${html.slice(0, 500)}\n`);
  }
  return { target, urls: urls.slice(0, count * 3) };
}

// --- From a WoS full-record page, get the article DOI ---
async function doiFromRecord(proxy, target, recordUrl) {
  await navigate(proxy, target, recordUrl);
  await waitForComplete(proxy, target);
  await new Promise((r) => setTimeout(r, 1200));
  const doi = await evalJs(
    proxy,
    target,
    `(()=>{let h='';(function w(r){r.querySelectorAll('*').forEach(e=>{if(e.shadowRoot)w(e.shadowRoot);if(!h&&e.tagName==='A'&&/doi\\.org\\/10\\./.test(e.href||''))h=e.href;});})(document);if(h)return (h.match(/10\\.\\d{4,9}\\/[^\\s"?]+/)||[])[0];const m=(document.body.innerText||'').match(/10\\.\\d{4,9}\\/[^\\s"]+/);return m?m[0]:'';})()`
  );
  return (doi || "").replace(/[.,;]+$/, "");
}

async function captureBrowserFullTextHtml(proxy, tab, outDir, doi, fallbackTitle = "") {
  const raw = await evalJs(
    proxy,
    tab,
    `(()=>{const root=document.querySelector('article,.article-body,.article__body,.c-article-body,#body,#fulltext');if(!root)return '';const text=(root.innerText||'').trim();if(text.length<500)return '';const title=document.querySelector('meta[name=citation_title]')?.content||document.querySelector('h1')?.innerText||${JSON.stringify(fallbackTitle)};return JSON.stringify({title,html:'<!doctype html><meta charset="utf-8"><title>'+String(title).replace(/[<&]/g,'')+'</title>'+root.outerHTML});})()`
  ).catch(() => "");
  if (!raw) return null;
  const value = JSON.parse(raw);
  const safe = safeArticleTitle(value.title || fallbackTitle || doi);
  const file = path.join(outDir, "FullText", `${safe}.html`);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, value.html, "utf8");
  return { file, bytes: Buffer.byteLength(value.html), format: "html", status: STATUS.FULL_TEXT_HTML_AVAILABLE };
}

// --- Download main PDF (and optionally SI) for a DOI via the authenticated browser ---
async function downloadDoi(proxy, doi, outDir, wantSi, debug, { cleanBundle = false, bundleTitle = "" } = {}) {
  const tab = (await newTab(proxy, "https://doi.org/" + doi)).targetId;
  try {
    const info = await waitForComplete(proxy, tab);
    const wall = classifyWall(info.url || "", info.title || "");
    if (wall) {
      // Attempt automatic verification before giving up.
      if (debug) process.stderr.write(`[debug][doi] wall detected: ${wall.status} "${wall.reason}" — attempting auto-verification...\n`);
      const verifyResult = await handleVerification(proxy, tab, wall, { debug, maxAttempts: 1 });
      if (verifyResult.passed) {
        if (debug) process.stderr.write(`[debug][doi] auto-verification passed (${verifyResult.method}), retrying...\n`);
        // Verification passed — re-read the page state and continue the download loop.
        const newInfo = await waitForComplete(proxy, tab);
        const reWall = classifyWall(newInfo.url || "", newInfo.title || "");
        if (!reWall) {
          // Wall is gone, fall through to PDF candidate extraction below.
          // We need to re-read meta candidates, so jump back to the metadata polling loop.
          info.url = newInfo.url;
          info.title = newInfo.title;
          // Clear the title so waitForComplete re-reads it; fall through
        } else {
          // Still blocked after auto-verification — hand off to user.
          return { doi, status: STATUS.VERIFICATION_AUTO_FAILED, url: info.url, reason: `auto-verify failed (${verifyResult.method || 'unknown'}), still: ${reWall.reason}` };
        }
      } else {
        return {
          doi,
          status: verifyResult.attempted ? STATUS.VERIFICATION_AUTO_FAILED : wall.status,
          url: info.url,
          reason: verifyResult.attempted ? `automatic verification did not resolve: ${wall.reason}` : wall.reason,
        };
      }
    }
    // poll: publisher landings often JS-redirect (e.g. linkinghub -> sciencedirect)
    // and inject citation_pdf_url late; re-read a few times before giving up.
    let meta = {};
    for (let i = 0; i < 4; i++) {
      await new Promise((r) => setTimeout(r, 1200));
      meta = JSON.parse(
        (await evalJs(
          proxy,
          tab,
          `(()=>{
        const m=document.querySelector('meta[name=citation_pdf_url]');
        const cand=[]; if(m&&m.content)cand.push(m.content);
        document.querySelectorAll('a').forEach(a=>{const h=a.href||'';if(/\\/pdf|pdfdirect|pdfft|\\.pdf(\\?|$)|\\/doi\\/epdf/i.test(h))cand.push(h);});
        const articleTitle=document.querySelector('meta[name=citation_title]')?.content||document.querySelector('meta[property="og:title"]')?.content||document.querySelector('h1')?.innerText||'';
        return JSON.stringify({cand:[...new Set(cand)].slice(0,6),title:document.title||'',articleTitle,url:location.href,body:(document.body.innerText||'').slice(0,160)});
      })()`
        )) || "{}"
      );
      const w = classifyWall(meta.url || "", meta.title || "", meta.body || "");
      if (w) {
        // Attempt auto-verification before giving up.
        if (debug) process.stderr.write(`[debug][doi] meta-stage wall: ${w.status} "${w.reason}" — attempting auto-verification...\n`);
        const vr = await handleVerification(proxy, tab, w, { debug, maxAttempts: 1 });
        if (vr.passed) {
          if (debug) process.stderr.write(`[debug][doi] auto-verification passed (${vr.method}), continuing...\n`);
          // Wall is gone after verification, re-poll meta
          await new Promise((r) => setTimeout(r, 1500));
          continue;
        }
        return {
          doi,
          status: vr.attempted ? STATUS.VERIFICATION_AUTO_FAILED : w.status,
          url: meta.url,
          reason: vr.attempted ? `automatic verification did not resolve: ${w.reason}` : w.reason,
        };
      }
      if (meta.cand && meta.cand.length) break;
    }
    // Publisher quirk: Wiley's citation_pdf_url/epdf opens a viewer, not raw bytes.
    // The pdfdirect?download=true endpoint returns the actual PDF in the same session.
    if (/wiley\.com/i.test(meta.url || "") || (meta.cand || []).some((c) => /wiley\.com/i.test(c))) {
      meta.cand = [
        `https://onlinelibrary.wiley.com/doi/pdfdirect/${doi}?download=true`,
        ...(meta.cand || []),
      ];
    }
    // Distinguish WoS-stage "no record" from publisher-stage "no PDF":
    // if we got here, WoS found the record (we have a doi.org redirect to a
    // publisher page), so "no PDF candidates" means no_authorized_pdf_found.
    if (!meta.cand || !meta.cand.length) {
      const html = await captureBrowserFullTextHtml(proxy, tab, outDir, doi, bundleTitle || meta.articleTitle || "");
      if (html) return { doi, ...html, via: meta.url, provider: "web_access", accessMode: "institution_browser" };
      if (debug) {
        process.stderr.write(
          `[debug][doi] ${doi} no PDF candidates. url=${meta.url||'?'} title=${meta.title||'?'}\n`
        );
      }
      return { doi, status: STATUS.NO_AUTHORIZED_PDF_FOUND, url: meta.url };
    }

    if (cleanBundle && bundleTitle && (!meta.articleTitle || !exactArticleTitleMatch(bundleTitle, meta.articleTitle))) {
      return {
        doi,
        title: meta.articleTitle || "",
        status: STATUS.DO_NOT_AUTO_RETRY,
        url: meta.url,
        reason: meta.articleTitle
          ? `WoS title mismatch: expected "${bundleTitle}"`
          : `WoS title could not be verified: expected "${bundleTitle}"`,
      };
    }

    const safe = doi.replace(/[\/:*?"<>|]/g, "_");
    const articleTitle = bundleTitle || meta.articleTitle || doi;
    const bundleDir = cleanBundle ? articleBundleDirectory(outDir, articleTitle) : "";
    const pdfPath = cleanBundle
      ? path.join(bundleDir, `${safeArticleTitle(articleTitle)}.pdf`)
      : path.join(outDir, "PDFs", safe + ".pdf");
    for (const pdfUrl of meta.cand) {
      const got = await fetchToFile(proxy, tab, pdfUrl, pdfPath);
      if (got.ok) {
        const res = {
          doi,
          ...(cleanBundle ? { title: articleTitle } : {}),
          status: STATUS.DOWNLOADED,
          file: got.file,
          bytes: got.bytes,
          via: meta.url,
        };
        if (wantSi) {
          const si = cleanBundle
            ? await downloadWosSupportingInformation({
                proxy,
                tab,
                landingUrl: meta.url,
                bundleDir,
                reservedFilenames: [path.basename(pdfPath)],
              })
            : await downloadSi(proxy, tab, meta.url, doi, outDir);
          res.si = si;
          if ((si?.downloaded || si?.count || 0) > 0) res.status = STATUS.DOWNLOADED_WITH_SI;
        }
        return res;
      }
    }
    return { doi, status: STATUS.PDF_FETCH_FAILED, url: meta.url };
  } finally {
    await closeTab(proxy, tab);
  }
}

async function downloadDirectUrl(pdfUrl, outDir, title = "") {
  const response = await fetch(pdfUrl, { headers: { Accept: "application/pdf, text/html, application/xml" }, signal: AbortSignal.timeout(60000) });
  const saved = await saveFullTextResponse(response, { outDir, title, source: pdfUrl });
  if (!saved.ok) return { title, status: STATUS.PDF_FETCH_FAILED, url: pdfUrl, err: saved.reason || `HTTP ${saved.httpStatus}` };
  return {
    title,
    status: saved.format === "pdf"
      ? STATUS.OPEN_ACCESS_DOWNLOADED
      : saved.format === "html"
        ? STATUS.FULL_TEXT_HTML_AVAILABLE
        : STATUS.NATIVE_FULLTEXT_DOWNLOADED,
    provider: "direct_url",
    accessMode: "open_access",
    ...saved,
  };
}

async function downloadSi(proxy, tab, landingUrl, doi, outDir) {
  // Best-effort: scan landing page for supplement links, download each.
  await navigate(proxy, tab, landingUrl);
  await waitForComplete(proxy, tab);
  await new Promise((r) => setTimeout(r, 800));
  const links = JSON.parse(
    (await evalJs(
      proxy,
      tab,
      `JSON.stringify([...new Set(Array.from(document.querySelectorAll('a')).map(a=>a.href).filter(h=>/downloadSupplement|\\/suppl|supplementary|mmc\\d|_si_/i.test(h)))].slice(0,30))`
    )) || "[]"
  );
  const safe = doi.replace(/[\/:*?"<>|]/g, "_");
  let n = 0;
  for (const u of links) {
    const name = (u.split("file=")[1] || u.split("/").pop() || "si" + ++n)
      .replace(/[\/:*?"<>|]/g, "_")
      .slice(0, 80);
    const got = await fetchAnyToFile(
      proxy,
      tab,
      u,
      path.join(outDir, "SupportingInformation", safe + "__" + name)
    );
    if (got.ok) n++;
  }
  return { count: n, found: links.length };
}

async function downloadSiForDoi(proxy, doi, outDir) {
  const tab = (await newTab(proxy, `https://doi.org/${doi}`)).targetId;
  try {
    const info = await waitForComplete(proxy, tab);
    const wall = classifyWall(info.url || "", info.title || "");
    if (wall) return { status: wall.status, count: 0, found: 0, reason: wall.reason };
    const result = await downloadSi(proxy, tab, info.url, doi, outDir);
    return { status: result.count > 0 ? "downloaded" : "not_found", ...result };
  } finally {
    await closeTab(proxy, tab);
  }
}

function decorateResult(result, article, route, wantSi) {
  const integrity = result.file && fs.existsSync(result.file)
    ? {
        sha256: result.sha256 || crypto.createHash("sha256").update(fs.readFileSync(result.file)).digest("hex"),
        format: result.format || path.extname(result.file).replace(/^\./, "").toLowerCase(),
      }
    : {};
  return {
    doi: article.doi || result.doi || "",
    title: article.title || result.title || "",
    language: article.language || "",
    publisher: article.publisher || "",
    route: route.provider,
    route_reason: route.reason,
    si_requested: wantSi,
    ...result,
    ...integrity,
  };
}

async function attachSupportingInformation(result, doi, args, context) {
  if (!args.si || !isSuccess(result.status)) return result;
  try {
    await context.ensureBrowser();
    result.si = await downloadSiForDoi(args.proxy, doi, args.out);
  } catch (error) {
    result.si = { status: "fetch_failed", count: 0, reason: String(error?.message || error).slice(0, 160) };
  }
  if ((result.si?.count || 0) > 0) result.status = STATUS.DOWNLOADED_WITH_SI;
  return result;
}

async function runWebAccess(doi, article, args, context) {
  await context.ensureBrowser();
  return downloadDoi(args.proxy, doi, args.out, args.si, args.debug, {
    cleanBundle: shouldUseCleanWosBundle(args),
    bundleTitle: args.title || article.title || "",
  });
}

async function downloadArxivTitle(title, args) {
  const hit = await findArxivByTitle(title).catch(() => null);
  if (!hit?.pdfUrl) return null;
  const downloaded = await downloadDirectUrl(hit.pdfUrl, args.out, hit.title).catch((error) => ({ status: STATUS.FAILED_AFTER_RETRY, err: String(error).slice(0, 120) }));
  return { ...downloaded, title: hit.title, arxiv: hit.id, route: "open_access", route_reason: "arxiv_exact_title", si_requested: args.si, ...(args.si ? { si: { status: "not_found" } } : {}) };
}

async function downloadCnkiByTitle(args, context) {
  if (!args.title) {
    return {
      title: "",
      status: STATUS.METADATA_AMBIGUOUS,
      reason: "CNKI title search requires --title when --pdf-url is not a CNKI URL",
      source: "cnki",
    };
  }
  await context.ensureBrowser();
  process.stderr.write(`[cnki] searching Chinese title: ${args.title}\n`);
  return downloadCnkiTitle(args.proxy, args.title, args.out, {
    cnkiUrl: context.cnkiUrl,
    format: args.cnkiFormat || "any",
    debug: args.debug,
    wantSi: args.si,
    transport: context.cnkiTransport,
  }).catch((error) => ({
    title: args.title,
    status: STATUS.FAILED_AFTER_RETRY,
    err: String(error).slice(0, 120),
    source: "cnki",
  }));
}

function attemptSummary(result, provider) {
  if (!result) return null;
  return {
    provider,
    status: result.status,
    ...(result.httpStatus ? { http_status: result.httpStatus } : {}),
  };
}

async function routeDoiDownload(doi, args, context) {
  let article;
  try {
    article = await fetchCrossrefByDoi(doi, { mailto: context.contactEmail });
  } catch (error) {
    article = { doi, title: args.title || doi, language: args.language || "", metadata_error: String(error?.message || error).slice(0, 160) };
  }
  if (args.title && context.singleDoi) article.title = args.title;
  if (args.language) article.language = args.language;
  if (args.sourceUrl) article.sourceUrl = args.sourceUrl;
  if (args.route) article.routeOverride = args.route;

  if (isChineseLiterature(article) || args.route === "cnki") {
    await context.ensureBrowser();
    const route = { provider: "cnki", reason: args.route ? "explicit_override" : "chinese_literature" };
    const result = await downloadCnkiTitle(args.proxy, article.title || doi, args.out, {
      cnkiUrl: context.cnkiUrl,
      format: args.cnkiFormat || "any",
      debug: args.debug,
      wantSi: args.si,
      transport: context.cnkiTransport,
    });
    return decorateResult(result, article, route, args.si);
  }

  const publisherProvider = classifyPublisher(article);
  const publisherCredentials = publisherProvider === "other" ? null : providerCredentials(publisherProvider);
  const initialRoute = chooseRoute({
    ...article,
    routeOverride: args.route,
    hasPublisherCredentials: hasUsablePublisherCredentials(publisherProvider, publisherCredentials),
  });
  const useApiFirst = !args.route && initialRoute.reason === "publisher_api_credentials_available";
  let apiResult = null;
  let oaResult = null;

  if (useApiFirst) {
    apiResult = await downloadPublisherArticle(article, {
      provider: publisherProvider,
      credentials: publisherCredentials,
      outDir: args.out,
    });
    if (isSuccess(apiResult.status)) {
      apiResult.oa_status = "not_checked_api_first";
      await attachSupportingInformation(apiResult, doi, args, context);
      return decorateResult(apiResult, article, {
        provider: initialRoute.provider,
        reason: initialRoute.reason,
      }, args.si);
    }
  }

  if (!args.route || args.route === "open_access") {
    const oa = await downloadOpenAccessArticle(article, { email: context.contactEmail, outDir: args.out });
    oaResult = oa;
    if (isSuccess(oa.status)) {
      if (apiResult) oa.api_attempt = attemptSummary(apiResult, publisherProvider);
      await attachSupportingInformation(oa, doi, args, context);
      return decorateResult(oa, article, {
        provider: "open_access",
        reason: apiResult ? "publisher_api_failed_oa_fallback" : "article_level_oa",
      }, args.si);
    }
    if (args.route === "open_access") return decorateResult(oa, article, { provider: "open_access", reason: "explicit_override" }, args.si);
  }

  const route = chooseRoute({
    ...article,
    isOa: false,
    routeOverride: args.route,
    hasPublisherCredentials: hasUsablePublisherCredentials(publisherProvider, publisherCredentials),
  });
  if (route.provider === "web_access") {
    const result = await runWebAccess(doi, article, args, context);
    return decorateResult({
      ...result,
      provider: "web_access",
      accessMode: "institution_browser",
      ...(oaResult ? { oa_attempt: { status: oaResult.status, assessment: oaResult.oaAssessment || "unknown" } } : {}),
    }, article, route, args.si);
  }

  const credentials = route.provider === publisherProvider ? publisherCredentials : providerCredentials(route.provider);
  if (!apiResult) {
    apiResult = await downloadPublisherArticle(article, {
      provider: route.provider,
      credentials,
      outDir: args.out,
    });
  }
  if (isSuccess(apiResult.status)) {
    await attachSupportingInformation(apiResult, doi, args, context);
    return decorateResult(apiResult, article, route, args.si);
  }
  const oaAttempt = oaResult
    ? { status: oaResult.status, assessment: oaResult.oaAssessment || "unknown" }
    : null;
  if (!apiResult.fallbackConfirmationRequired) {
    return decorateResult({ ...apiResult, ...(oaAttempt ? { oa_attempt: oaAttempt } : {}) }, article, route, args.si);
  }
  const providerFallback = args.apiFallbackWebFor?.includes(route.provider)
    ? true
    : args.noApiFallbackWebFor?.includes(route.provider)
      ? false
      : args.apiFallbackWeb;
  if (providerFallback === undefined) {
    return decorateResult({
      ...apiResult,
      api_status: apiResult.status,
      ...(oaAttempt ? { oa_attempt: oaAttempt } : {}),
      status: STATUS.API_FALLBACK_CONFIRMATION_REQUIRED,
      next_action: `Publisher API and OA fallback failed. Ask once for ${route.provider}, then re-run with --api-fallback-web-for ${route.provider} or --no-api-fallback-web-for ${route.provider}`,
    }, article, route, args.si);
  }
  if (!providerFallback) return decorateResult({ ...apiResult, ...(oaAttempt ? { oa_attempt: oaAttempt } : {}), web_fallback: "declined" }, article, route, args.si);
  const web = await runWebAccess(doi, article, args, context);
  return decorateResult({
    ...web,
    provider: "web_access",
    accessMode: "institution_browser",
    api_attempt: attemptSummary(apiResult, route.provider),
    ...(oaAttempt ? { oa_attempt: oaAttempt } : {}),
    web_fallback: "accepted",
  }, article, route, args.si);
}

function outputAndManifest(args, results, t0) {
  const secs = ((Date.now() - t0) / 1000).toFixed(1);
  const summary = { total: results.length, downloaded: results.filter((result) => isSuccess(result.status)).length, seconds: Number(secs) };
  const manifest = writeManifest(args.out, {
    request: {
      topic: args.topic || "",
      title: args.title || "",
      dois: args.dois || [],
      pdf_url: args.pdfUrl || "",
      si_requested: args.si,
      language_override: args.language || "",
      route_override: args.route || "",
      source_url: args.sourceUrl || "",
      api_fallback_web: args.apiFallbackWeb ?? null,
      api_fallback_web_for: args.apiFallbackWebFor || [],
      no_api_fallback_web_for: args.noApiFallbackWebFor || [],
    },
    summary,
    results,
  });
  const output = { summary, manifest, results };
  console.log(JSON.stringify(output, null, 2));
  return output;
}

async function main() {
  const args = parseArgs(process.argv);
  const siChoice = parseSiChoice(args);
  if (!siChoice.confirmed) {
    console.log(JSON.stringify({
      summary: { total: 0, downloaded: 0, seconds: 0 },
      results: [{ status: STATUS.SI_CONFIRMATION_REQUIRED, next_action: "Ask whether to download Supporting Information, then re-run with --si or --no-si" }],
    }, null, 2));
    process.exitCode = 2;
    return;
  }
  fs.mkdirSync(args.out, { recursive: true });
  const schoolConfig = loadSchoolConfig();
  const settings = loadSettings();
  const discoveryUrl = discoveryUrlFromConfig(schoolConfig);
  const cnkiUrl = cnkiUrlFromConfig(schoolConfig, args.cnkiUrl);
  const contactEmail = args.unpaywallEmail || settings?.open_access?.contact_email || process.env.UNPAYWALL_EMAIL || "";
  if (args.openAccess && !args.route) args.route = "open_access";
  process.stderr.write(`[config] ${schoolSummary(schoolConfig)}; discovery=${discoveryUrl}; cnki=${cnkiUrl}\n`);
  const results = [];
  const t0 = Date.now();
  let browserReady = false;
  const ensureBrowser = async () => {
    if (!browserReady) {
      await healthCheck(args.proxy);
      browserReady = true;
    }
  };
  const context = { ensureBrowser, cnkiUrl, contactEmail, singleDoi: (args.dois || []).length === 1 };

  context.cnkiTransport = createCnkiTransport({
    mode: schoolConfig?.discovery?.cnki_transport?.mode || "browser",
    entryUrl: cnkiUrl,
    webvpnUrlTemplate: schoolConfig?.discovery?.cnki_transport?.webvpn_url_template || "",
  });

  if (args.pdfUrl) {
    const directRoute = chooseDirectUrlRoute(args);
    if (directRoute.mode === "title_search") {
      const cnki = await downloadCnkiByTitle(args, context);
      results.push({ ...cnki, route: "cnki", route_reason: directRoute.reason, si_requested: args.si });
      outputAndManifest(args, results, t0);
      return;
    }
    if (directRoute.provider === "cnki") {
      await ensureBrowser();
      const cnki = await downloadCnkiDirectUrl(args.proxy, args.pdfUrl, args.title || "cnki-paper", args.out, { debug: args.debug, wantSi: args.si });
      results.push({ ...cnki, route: "cnki", route_reason: directRoute.reason, si_requested: args.si });
      outputAndManifest(args, results, t0);
      return;
    }
    const r = await downloadDirectUrl(args.pdfUrl, args.out, args.title || "").catch((e) => ({
      title: args.title || "",
      status: STATUS.FAILED_AFTER_RETRY,
      url: args.pdfUrl,
      err: String(e).slice(0, 120),
    }));
    results.push({ ...r, si_requested: args.si, ...(args.si ? { si: { status: "not_found", reason: "A direct PDF URL does not identify a supporting-information landing page" } } : {}) });
    outputAndManifest(args, results, t0);
    return;
  }

  if (args.title && (isChineseLiterature({ title: args.title, language: args.language, sourceUrl: args.sourceUrl }) || args.route === "cnki") && !args.topic) {
    const r = await downloadCnkiByTitle(args, context);
    results.push({ ...r, route: "cnki", route_reason: "chinese_literature", si_requested: args.si });
    outputAndManifest(args, results, t0);
    return;
  }

  let dois = args.dois || [];

  if (!dois.length && args.title && !args.topic) {
    if (args.openAccess) {
      const arxiv = await downloadArxivTitle(args.title, args);
      if (arxiv) {
        results.push(arxiv);
        outputAndManifest(args, results, t0);
        return;
      }
    }
    const metadata = await findCrossrefByTitle(args.title, { mailto: contactEmail }).catch(() => null);
    if (metadata?.doi) {
      dois = [metadata.doi];
      context.singleDoi = true;
    } else {
      process.stderr.write(`[oa] no exact Crossref record; trying arXiv exact title: ${args.title}\n`);
      const arxiv = await downloadArxivTitle(args.title, args);
      if (arxiv) {
        results.push(arxiv);
      } else {
        results.push({ title: args.title, status: args.openAccess ? STATUS.OA_NOT_FOUND : STATUS.METADATA_AMBIGUOUS, err: "no exact Crossref or arXiv title match", si_requested: args.si });
      }
      outputAndManifest(args, results, t0);
      return;
    }
  }

  if (!dois.length && args.topic) {
    await ensureBrowser();
    const searchQuery = wosSearchQuery(args.topic, args.title || "");
    process.stderr.write(`[wos] searching: ${searchQuery}\n`);
    const { target, urls } = await wosRecordUrls(args.proxy, searchQuery, args.count, args.debug, discoveryUrl);
    process.stderr.write(`[wos] ${urls.length} records\n`);
    for (const u of urls) {
      if (dois.length >= args.count) break;
      const doi = await doiFromRecord(args.proxy, target, u);
      if (doi && /^10\./.test(doi)) {
        dois.push(doi);
        process.stderr.write(`[doi] ${doi}\n`);
      }
    }
    if (!dois.length && args.title) {
      process.stderr.write(`[oa] WoS produced no DOI; trying arXiv exact title: ${args.title}\n`);
      const hit = await findArxivByTitle(args.title).catch((e) => ({ err: String(e).slice(0, 120) }));
      if (hit && hit.pdfUrl) {
        process.stderr.write(`[oa] arXiv ${hit.id} -> ${hit.pdfUrl}\n`);
        const r = await downloadDirectUrl(hit.pdfUrl, args.out, hit.title).catch((e) => ({
          title: args.title,
          status: STATUS.FAILED_AFTER_RETRY,
          err: String(e).slice(0, 120),
        }));
        results.push({ ...r, arxiv: hit.id });
      } else {
        results.push({ title: args.title, status: STATUS.NO_AUTHORIZED_PDF_FOUND, err: hit?.err || "no exact arXiv title match" });
      }
    }
  }
  dois = selectBatchDois(dois, args.count);

  for (const doi of dois) {
    const r = await routeDoiDownload(doi, args, context).catch((e) => {
      // Distinguish parameter/logic errors (do_not_auto_retry) from
      // network/CDP errors (failed_after_retry).
      const msg = String(e).slice(0, 120);
      const isLogic = /unknown arg|mutually exclusive|required|not reachable/i.test(msg);
      return {
        doi,
        status: isLogic ? STATUS.DO_NOT_AUTO_RETRY : STATUS.FAILED_AFTER_RETRY,
        err: msg,
      };
    });
    // Apply legacy status mapping for backward-compatible output if requested.
    if (args.legacyStatus) {
      r.status = reverseMapStatus(r.status);
    }
    results.push(r);
    process.stderr.write(
      `[dl] ${doi} -> ${r.status}${r.bytes ? " " + r.bytes + "B" : ""}\n`
    );
  }
  outputAndManifest(args, results, t0);
}

// Reverse mapping: canonical -> legacy (only for --legacy-status output).
// Best-effort; some canonical codes have no legacy equivalent and pass through.
function reverseMapStatus(s) {
  const m = {
    [STATUS.CARSI_WAITING_USER]: "needs_user_login",
    [STATUS.PUBLISHER_VERIFICATION_WAITING_USER]: "needs_user_verify",
    [STATUS.SCIENCEDIRECT_ROBOT_CHECK]: "needs_user_verify",
    [STATUS.PUBLISHER_BLOCKED_WAITING_USER]: "publisher_blocked",
    [STATUS.NO_FULL_TEXT_LINK]: "no_pdf_link",
    [STATUS.NO_AUTHORIZED_PDF_FOUND]: "no_pdf_link",
    [STATUS.FAILED_AFTER_RETRY]: "error",
    [STATUS.DO_NOT_AUTO_RETRY]: "error",
  };
  return m[s] || s;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  main().catch((e) => {
    console.error(e.stack || String(e));
    process.exit(1);
  });
}
