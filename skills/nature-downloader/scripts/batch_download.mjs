#!/usr/bin/env node
// Batch literature downloader for the SJTU CARSI / Web of Science route.
//
// Runs the whole chain inside Node + the web-access CDP proxy, so large data
// (search DOMs, PDF bytes) never enters the agent's context. Only compact
// per-paper status is printed. This is the token-efficient fast path.
//
// Usage:
//   node batch_download.mjs --topic "<query>" --count 10 --out <dir> [--si]
//   node batch_download.mjs --dois 10.x/a,10.y/b --out <dir> [--si]
//   node batch_download.mjs --title "<exact title>" --out <dir> [--open-access]
//   node batch_download.mjs --pdf-url "https://..." --title "<title>" --out <dir>
//   node batch_download.mjs --title "<中文题名>" --out <dir> [--cnki-url <entry>] [--cnki-format pdf|any]
//   options: [--proxy http://127.0.0.1:3456] [--debug] [--legacy-status]
//
// Boundaries: uses only the user's already-authenticated browser session.
// Stops at jAccount / CARSI pages and never handles credentials. For visible
// verification widgets it makes a bounded attempt before reporting a handoff.
// Main PDF only by default; --si also fetches supplements.

import fs from "node:fs";
import path from "node:path";
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
import { classifyWall, STATUS, isSuccess, mapLegacyStatus } from "./lib/status-codes.mjs";
import { fetchToFile, fetchAnyToFile } from "./lib/pdf-utils.mjs";
import { handleVerification } from "./lib/anti-bot.mjs";
import {
  DEFAULT_DISCOVERY_URL,
  discoveryUrlFromConfig,
  loadSchoolConfig,
  schoolSummary,
} from "./lib/school-config.mjs";
import { filenameForPdfUrl, findArxivByTitle } from "./lib/open-access.mjs";
import {
  DEFAULT_CNKI_URL,
  downloadCnkiTitle,
  looksChinese,
} from "./lib/cnki.mjs";

// Core Collection only: journal articles that carry DOIs (avoids Derwent/patent records).
const WOS = DEFAULT_DISCOVERY_URL;

function parseArgs(argv) {
  const a = { count: 10, out: ".", si: false, proxy: DEFAULT_PROXY, debug: false, legacyStatus: false };
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
    else if (k === "--proxy") a.proxy = argv[++i].replace(/\/$/, "");
    else if (k === "--debug") a.debug = true;
    else if (k === "--legacy-status") a.legacyStatus = true;
    else throw new Error("unknown arg " + k);
  }
  const modes = [a.topic, a.title, a.pdfUrl, a.dois?.length].filter(Boolean).length;
  if (modes > 1 && !(a.topic && a.title && modes === 2)) {
    throw new Error("--topic, --title, --pdf-url, and --dois are mutually exclusive except --topic with --title");
  }
  if (a.cnkiFormat && !["pdf", "any"].includes(a.cnkiFormat)) {
    throw new Error("--cnki-format must be pdf or any");
  }
  return a;
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

// --- Download main PDF (and optionally SI) for a DOI via the authenticated browser ---
async function downloadDoi(proxy, doi, outDir, wantSi, debug) {
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
        return JSON.stringify({cand:[...new Set(cand)].slice(0,6),title:document.title||'',url:location.href,body:(document.body.innerText||'').slice(0,160)});
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
      if (debug) {
        process.stderr.write(
          `[debug][doi] ${doi} no PDF candidates. url=${meta.url||'?'} title=${meta.title||'?'}\n`
        );
      }
      return { doi, status: STATUS.NO_AUTHORIZED_PDF_FOUND, url: meta.url };
    }

    const safe = doi.replace(/[\/:*?"<>|]/g, "_");
    for (const pdfUrl of meta.cand) {
      const got = await fetchToFile(proxy, tab, pdfUrl, path.join(outDir, "PDFs", safe + ".pdf"));
      if (got.ok) {
        const res = {
          doi,
          status: STATUS.DOWNLOADED,
          file: got.file,
          bytes: got.bytes,
          via: meta.url,
        };
        if (wantSi) {
          const si = await downloadSi(proxy, tab, meta.url, doi, outDir);
          res.si = si;
          if (si && si.count > 0) res.status = STATUS.DOWNLOADED_WITH_SI;
        }
        return res;
      }
    }
    return { doi, status: STATUS.PDF_FETCH_FAILED, url: meta.url };
  } finally {
    await closeTab(proxy, tab);
  }
}

async function downloadPdfUrl(proxy, pdfUrl, outDir, title = "") {
  const tab = (await newTab(proxy, pdfUrl)).targetId;
  try {
    await waitForComplete(proxy, tab);
    const fileName = filenameForPdfUrl(pdfUrl, title);
    const got = await fetchToFile(proxy, tab, pdfUrl, path.join(outDir, "PDFs", fileName));
    if (got.ok) {
      return {
        title,
        status: STATUS.DOWNLOADED,
        file: got.file,
        bytes: got.bytes,
        via: pdfUrl,
      };
    }
    return { title, status: STATUS.PDF_FETCH_FAILED, url: pdfUrl, err: got.err };
  } finally {
    await closeTab(proxy, tab);
  }
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

async function main() {
  const args = parseArgs(process.argv);
  fs.mkdirSync(args.out, { recursive: true });
  const schoolConfig = loadSchoolConfig();
  const discoveryUrl = discoveryUrlFromConfig(schoolConfig);
  const cnkiUrl = cnkiUrlFromConfig(schoolConfig, args.cnkiUrl);
  process.stderr.write(`[config] ${schoolSummary(schoolConfig)}; discovery=${discoveryUrl}; cnki=${cnkiUrl}\n`);

  // Fail fast with a friendly message if the CDP proxy isn't running.
  await healthCheck(args.proxy);

  const results = [];
  const t0 = Date.now();

  if (args.pdfUrl) {
    const r = await downloadPdfUrl(args.proxy, args.pdfUrl, args.out, args.title || "").catch((e) => ({
      title: args.title || "",
      status: STATUS.FAILED_AFTER_RETRY,
      url: args.pdfUrl,
      err: String(e).slice(0, 120),
    }));
    results.push(r);
    const secs = ((Date.now() - t0) / 1000).toFixed(1);
    console.log(JSON.stringify({ summary: { total: 1, downloaded: isSuccess(r.status) ? 1 : 0, seconds: Number(secs) }, results }, null, 2));
    return;
  }

  if (args.title && args.openAccess && !args.topic) {
    process.stderr.write(`[oa] searching arXiv exact title: ${args.title}\n`);
    const hit = await findArxivByTitle(args.title).catch((e) => ({ err: String(e).slice(0, 120) }));
    if (hit && hit.pdfUrl) {
      process.stderr.write(`[oa] arXiv ${hit.id} -> ${hit.pdfUrl}\n`);
      const r = await downloadPdfUrl(args.proxy, hit.pdfUrl, args.out, hit.title).catch((e) => ({
        title: args.title,
        status: STATUS.FAILED_AFTER_RETRY,
        err: String(e).slice(0, 120),
      }));
      results.push({ ...r, arxiv: hit.id });
    } else {
      results.push({ title: args.title, status: STATUS.NO_AUTHORIZED_PDF_FOUND, err: hit?.err || "no exact arXiv title match" });
    }
    const secs = ((Date.now() - t0) / 1000).toFixed(1);
    console.log(JSON.stringify({ summary: { total: 1, downloaded: results.filter((r) => isSuccess(r.status)).length, seconds: Number(secs) }, results }, null, 2));
    return;
  }

  if (args.title && looksChinese(args.title) && !args.topic) {
    process.stderr.write(`[cnki] searching Chinese title: ${args.title}\n`);
    const r = await downloadCnkiTitle(args.proxy, args.title, args.out, {
      cnkiUrl,
      format: args.cnkiFormat || "any",
      debug: args.debug,
    }).catch((e) => ({
      title: args.title,
      status: STATUS.FAILED_AFTER_RETRY,
      err: String(e).slice(0, 120),
      source: "cnki",
    }));
    results.push(r);
    const secs = ((Date.now() - t0) / 1000).toFixed(1);
    console.log(JSON.stringify({ summary: { total: 1, downloaded: isSuccess(r.status) ? 1 : 0, seconds: Number(secs) }, results }, null, 2));
    return;
  }

  let dois = args.dois || [];

  if (!dois.length && args.topic) {
    process.stderr.write(`[wos] searching: ${args.topic}\n`);
    const { target, urls } = await wosRecordUrls(args.proxy, args.topic, args.count, args.debug, discoveryUrl);
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
        const r = await downloadPdfUrl(args.proxy, hit.pdfUrl, args.out, hit.title).catch((e) => ({
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
  dois = [...new Set(dois)].slice(0, args.count);

  for (const doi of dois) {
    const r = await downloadDoi(args.proxy, doi, args.out, args.si, args.debug).catch((e) => {
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
  const secs = ((Date.now() - t0) / 1000).toFixed(1);
  const ok = results.filter((r) => isSuccess(r.status)).length;
  console.log(
    JSON.stringify(
      { summary: { total: dois.length, downloaded: ok, seconds: Number(secs) }, results },
      null,
      2
    )
  );
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

main().catch((e) => {
  console.error(e.stack || String(e));
  process.exit(1);
});
