import path from "node:path";
import { STATUS, classifyWall } from "./status-codes.mjs";
import {
  closeTab,
  evalJs,
  navigate,
  newTab,
  proxyGet,
  sleep,
  waitForComplete,
} from "./cdp-utils.mjs";
import { fetchAnyToFile, fetchToFile } from "./pdf-utils.mjs";
import { handleVerification } from "./anti-bot.mjs";

export const DEFAULT_CNKI_URL = "https://kns.cnki.net/kns8s/defaultresult/index";

const CNKI_HOST_RE = /(^|\.)cnki\.net$|(^|\.)cnki\.com\.cn$/i;
const CHINESE_RE = /[\u3400-\u9fff]/;

export function looksChinese(text = "") {
  return CHINESE_RE.test(String(text));
}

export function cnkiSearchUrl(query, baseUrl = DEFAULT_CNKI_URL) {
  const url = new URL(baseUrl);
  url.searchParams.set("kw", query);
  return url.toString();
}

export function safeCnkiFileName(title = "", ext = ".pdf") {
  const cleaned = String(title || "cnki-paper")
    .trim()
    .replace(/[\/:*?"<>|]+/g, "")
    .replace(/\s+/g, "_")
    .slice(0, 120);
  return `${cleaned || "cnki-paper"}${ext}`;
}

export function isCnkiUrl(url = "") {
  try {
    return CNKI_HOST_RE.test(new URL(url).hostname);
  } catch {
    return false;
  }
}

function classifyCnkiWall(url = "", title = "", body = "") {
  const wall = classifyWall(url, title, body);
  if (wall) return wall;
  const text = `${title} ${body}`;
  // Slider/drag/puzzle CAPTCHA — auto-attemptable
  if (/滑块|滑动验证|拖动滑块|拼图验证|请按住滑块|请拖动|slide to verify|drag the slider|slide verification|slider captcha/i.test(text)) {
    return { status: STATUS.PUBLISHER_VERIFICATION_WAITING_USER, reason: "CNKI slider captcha — auto-attemptable" };
  }
  // Login/auth wall
  if (/登录|统一身份认证|机构登录|校外访问|账号登录|扫码登录|验证码|安全验证|人机验证/i.test(text)) {
    return { status: STATUS.CARSI_WAITING_USER, reason: "CNKI or institutional login required" };
  }
  if (/没有权限|无权访问|未订购|未购买|余额不足|下载权限|未开通|403|forbidden/i.test(text)) {
    return { status: STATUS.LIBRARY_NO_PERMISSION, reason: "CNKI access denied" };
  }
  return null;
}

async function pageSnapshot(proxy, target) {
  const info = await proxyGet(proxy, "/info", { target }, 10000).catch(() => ({}));
  const body = await evalJs(
    proxy,
    target,
    `(document.body && document.body.innerText || "").slice(0,1000)`
  ).catch(() => "");
  return { url: info.url || "", title: info.title || "", body: body || "" };
}

async function submitSearchIfNeeded(proxy, target, query) {
  await evalJs(
    proxy,
    target,
    `(()=>{
      const value=${JSON.stringify(query)};
      const inputs=[...document.querySelectorAll('input[type="text"],input:not([type]),textarea')];
      const input=inputs.find(i=>/主题|篇名|关键词|检索|search|keyword|kw/i.test([i.placeholder,i.name,i.id,i.className].join(" ")))||inputs[0];
      if(!input)return false;
      const setter=Object.getOwnPropertyDescriptor(Object.getPrototypeOf(input),'value')?.set;
      if(setter)setter.call(input,value);else input.value=value;
      input.dispatchEvent(new Event('input',{bubbles:true}));
      input.dispatchEvent(new Event('change',{bubbles:true}));
      const buttons=[...document.querySelectorAll('button,input[type="button"],input[type="submit"],a')];
      const button=document.querySelector('input.search-btn,.search-btn')||
        buttons.find(e=>/检索|搜索|查询|Search/i.test(e.innerText||e.value||e.title||""));
      if(button){button.click();return true;}
      input.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',code:'Enter',bubbles:true}));
      return true;
    })()`,
    30000
  ).catch(() => false);
}

async function findResultUrl(proxy, target, title) {
  const raw = await evalJs(
    proxy,
    target,
    `(()=>{
      const expected=${JSON.stringify(title)}.replace(/\\s+/g,"").toLowerCase();
      const links=[...document.querySelectorAll('a[href]')].map(a=>({
        href:a.href,
        text:(a.innerText||a.title||"").replace(/\\s+/g," ").trim()
      })).filter(x=>x.href&&/cnki\\.net|cnki\\.com\\.cn/i.test(x.href));
      const detail=links.filter(x=>/detail|KCMS|kcms|kns8s\\/Detail|dbcode|filename|FileName/i.test(x.href));
      const exact=detail.find(x=>x.text.replace(/\\s+/g,"").toLowerCase()===expected);
      const contains=detail.find(x=>x.text&&expected&&(
        x.text.replace(/\\s+/g,"").toLowerCase().includes(expected)||
        expected.includes(x.text.replace(/\\s+/g,"").toLowerCase())
      ));
      const fallback=detail[0]||links.find(x=>/detail|KCMS|kcms/i.test(x.href));
      return JSON.stringify(exact||contains||fallback||null);
    })()`,
    30000
  );
  return JSON.parse(raw || "null");
}

async function findDownloadCandidates(proxy, target) {
  const raw = await evalJs(
    proxy,
    target,
    `(()=>{
      const out=[];
      const push=(url,text)=>{if(url&&/cnki\\.net|cnki\\.com\\.cn/i.test(url))out.push({url,text:text||""});};
      document.querySelectorAll('a[href],button,[onclick]').forEach(e=>{
        const text=(e.innerText||e.value||e.title||e.getAttribute('aria-label')||"").trim();
        const href=e.href||"";
        const onclick=e.getAttribute('onclick')||"";
        if(/PDF|整本下载|全文下载|下载|CAJ|HTML阅读|在线阅读/i.test(text+href+onclick)){
          push(href,text);
          const m=onclick.match(/https?:\\/\\/[^'"\\s)]+/i);
          if(m)push(m[0],text);
        }
      });
      return JSON.stringify([...new Map(out.map(x=>[x.url,x])).values()].slice(0,12));
    })()`,
    30000
  );
  const candidates = JSON.parse(raw || "[]");
  const score = (item) => {
    const s = `${item.text} ${item.url}`;
    if (/pdf/i.test(s)) return 0;
    if (/下载|download/i.test(s)) return 1;
    if (/caj/i.test(s)) return 2;
    return 3;
  };
  return candidates.sort((a, b) => score(a) - score(b));
}

export function filterCnkiDownloadCandidates(candidates = [], format = "any") {
  if (format !== "pdf") return candidates;
  return candidates.filter((candidate) => /pdf/i.test(`${candidate.text || ""} ${candidate.url || ""}`));
}

export async function downloadCnkiTitle(proxy, title, outDir, { cnkiUrl = DEFAULT_CNKI_URL, format = "any", debug = false } = {}) {
  const tab = (await newTab(proxy, cnkiSearchUrl(title, cnkiUrl))).targetId;
  try {
    await waitForComplete(proxy, tab);
    await sleep(1500);
    await submitSearchIfNeeded(proxy, tab, title);
    await sleep(2500);
    await waitForComplete(proxy, tab);

    let snap = await pageSnapshot(proxy, tab);
    let wall = classifyCnkiWall(snap.url, snap.title, snap.body);
    if (wall) {
      if (debug) process.stderr.write(`[debug][cnki] wall after search: ${wall.status} "${wall.reason}" — attempting auto-verification...\n`);
      const vr = await handleVerification(proxy, tab, wall, { debug, maxAttempts: 2 });
      if (vr.passed) {
        if (debug) process.stderr.write(`[debug][cnki] auto-verification passed (${vr.method}), re-reading page...\n`);
        await sleep(1500);
        await waitForComplete(proxy, tab);
        snap = await pageSnapshot(proxy, tab);
        wall = classifyCnkiWall(snap.url, snap.title, snap.body);
        if (wall) {
          return { title, status: STATUS.VERIFICATION_AUTO_FAILED, url: snap.url, reason: `auto-verify failed (${vr.method}), still: ${wall.reason}` };
        }
      } else {
        return {
          title,
          status: vr.attempted ? STATUS.VERIFICATION_AUTO_FAILED : wall.status,
          url: snap.url,
          reason: vr.attempted ? `automatic verification did not resolve: ${wall.reason}` : wall.reason,
        };
      }
    }

    const hit = await findResultUrl(proxy, tab, title);
    if (!hit || !hit.href) {
      if (debug) process.stderr.write(`[debug][cnki] no result. url=${snap.url} title=${snap.title}\n`);
      return { title, status: STATUS.NO_FULL_TEXT_LINK, url: snap.url };
    }

    await navigate(proxy, tab, hit.href);
    await waitForComplete(proxy, tab);
    await sleep(1500);
    snap = await pageSnapshot(proxy, tab);
    wall = classifyCnkiWall(snap.url, snap.title, snap.body);
    if (wall) {
      if (debug) process.stderr.write(`[debug][cnki] wall after detail nav: ${wall.status} "${wall.reason}" — attempting auto-verification...\n`);
      const vr = await handleVerification(proxy, tab, wall, { debug, maxAttempts: 2 });
      if (vr.passed) {
        if (debug) process.stderr.write(`[debug][cnki] auto-verification passed (${vr.method}), re-reading page...\n`);
        await sleep(1500);
        await waitForComplete(proxy, tab);
        snap = await pageSnapshot(proxy, tab);
        wall = classifyCnkiWall(snap.url, snap.title, snap.body);
        if (wall) {
          return { title, status: STATUS.VERIFICATION_AUTO_FAILED, url: snap.url, reason: `auto-verify failed (${vr.method}), still: ${wall.reason}` };
        }
      } else {
        return {
          title,
          status: vr.attempted ? STATUS.VERIFICATION_AUTO_FAILED : wall.status,
          url: snap.url,
          reason: vr.attempted ? `automatic verification did not resolve: ${wall.reason}` : wall.reason,
        };
      }
    }

    const candidates = filterCnkiDownloadCandidates(await findDownloadCandidates(proxy, tab), format);
    if (!candidates.length) {
      if (debug) process.stderr.write(`[debug][cnki] no download candidates. url=${snap.url} title=${snap.title}\n`);
      return { title, status: STATUS.NO_AUTHORIZED_PDF_FOUND, url: snap.url, via: hit.href };
    }

    for (const candidate of candidates) {
      const lower = `${candidate.text} ${candidate.url}`.toLowerCase();
      const ext = lower.includes("caj") ? ".caj" : ".pdf";
      const outPath = path.join(outDir, ext === ".caj" ? "CNKI" : "PDFs", safeCnkiFileName(title, ext));
      const got = ext === ".pdf"
        ? await fetchToFile(proxy, tab, candidate.url, outPath).catch((e) => ({ ok: false, err: String(e).slice(0, 120) }))
        : await fetchAnyToFile(proxy, tab, candidate.url, outPath).catch((e) => ({ ok: false, err: String(e).slice(0, 120) }));
      if (got.ok) {
        return {
          title,
          status: STATUS.DOWNLOADED,
          file: got.file,
          bytes: got.bytes,
          via: snap.url,
          source: "cnki",
          format: ext.slice(1),
        };
      }
    }

    return { title, status: STATUS.PDF_FETCH_FAILED, url: snap.url, via: hit.href, source: "cnki" };
  } finally {
    await closeTab(proxy, tab);
  }
}
