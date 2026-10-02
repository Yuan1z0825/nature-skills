import path from "node:path";
import { evalJs, navigate, sleep, waitForComplete } from "./cdp-utils.mjs";
import { fetchAnyToFile } from "./pdf-utils.mjs";

const SUPPLEMENT_LABEL = /(?:supporting\s+information|supplement(?:ary|al)?(?:\s+(?:information|material|data|file|table|figure|video))?|source\s+data|\bmmc\d+\b)/i;
const ATTACHMENT_URL = /(?:downloadSupplement|\/suppl_file\/|_si_|\bmmc\d+\b|\/supplementary\/)/i;
const FILE_EXTENSION = /\.(?:pdf|zip|xlsx?|docx?|csv|tsv|txt|mp4|mov|avi|mpe?g|mp3|wav)(?:$|[?#])/i;
const EXTERNAL_REPOSITORY = /(?:github\.com|zenodo\.org|figshare\.com|dryad\.org|osf\.io)/i;
const CONTENT_TYPE_EXTENSION = new Map([
  ["application/pdf", ".pdf"],
  ["application/zip", ".zip"],
  ["application/x-zip-compressed", ".zip"],
  ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"],
  ["application/vnd.ms-excel", ".xls"],
  ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"],
  ["text/csv", ".csv"],
  ["video/mp4", ".mp4"],
]);

function cleanTitle(value = "") {
  return String(value)
    .normalize("NFKC")
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim()
    .toLowerCase();
}

export function exactArticleTitleMatch(expected, actual) {
  return Boolean(expected && actual && cleanTitle(expected) === cleanTitle(actual));
}

export function safeArticleTitle(title = "") {
  return String(title)
    .normalize("NFKC")
    .replace(/[\\/:*?"<>|]+/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 160) || "article";
}

export function articleBundleDirectory(outDir, title) {
  return path.join(outDir, safeArticleTitle(title));
}

export function shouldUseCleanWosBundle(args = {}) {
  return Boolean(args.topic && args.title && args.si);
}

export function wosSearchQuery(topic, exactTitle = "") {
  return exactTitle ? `"${String(exactTitle).replace(/"/g, "").trim()}"` : topic;
}

function filenameFromLink(link, url) {
  const explicit = String(link.download || "").trim();
  if (explicit) return path.basename(explicit);
  const parsed = new URL(url);
  const fromQuery = parsed.searchParams.get("file") || parsed.searchParams.get("filename");
  return path.basename(fromQuery || parsed.pathname) || "supplement";
}

export function selectSupportingInformationLinks(links, baseUrl, limit = 30) {
  const attachments = [];
  const pages = [];
  const seen = new Set();
  for (const link of links || []) {
    const rawUrl = link.href || link.dataHref || link.dataUrl || link.dataDownloadUrl || "";
    const label = [link.text, link.ariaLabel, link.title].filter(Boolean).join(" ").trim();
    if (!rawUrl || !SUPPLEMENT_LABEL.test(`${label} ${link.download || ""} ${rawUrl}`)) continue;
    if (/^#/i.test(link.rawHref || "") || /^(?:#|javascript:|mailto:|tel:|data:)/i.test(rawUrl)) continue;
    let url;
    try {
      url = new URL(rawUrl, baseUrl).href;
    } catch {
      continue;
    }
    if (!/^https?:/i.test(url) || EXTERNAL_REPOSITORY.test(url) || seen.has(url)) continue;
    seen.add(url);
    const isAttachment = Boolean(link.download || link.dataDownloadUrl) || FILE_EXTENSION.test(url) || /\/download(?:\/|\?|Supplement)/i.test(url) || ATTACHMENT_URL.test(url) && /(?:file|filename|mmc\d+)/i.test(url);
    if (isAttachment) {
      attachments.push({ url, label, filename: filenameFromLink(link, url) });
    } else {
      pages.push({ url, label });
    }
    if (attachments.length + pages.length >= limit) break;
  }
  return { attachments, pages };
}

const SCAN_LINKS_SCRIPT = `(()=>JSON.stringify(Array.from(document.querySelectorAll('a[href],button,[role=link],[data-href],[data-url],[data-download-url]')).map(e=>({text:(e.innerText||e.textContent||'').trim().slice(0,240),href:e.href||'',rawHref:e.getAttribute('href')||'',download:e.getAttribute('download')||'',ariaLabel:e.getAttribute('aria-label')||'',title:e.getAttribute('title')||'',dataHref:e.getAttribute('data-href')||'',dataUrl:e.getAttribute('data-url')||'',dataDownloadUrl:e.getAttribute('data-download-url')||''}))))()`;

async function scanPage(proxy, tab, url) {
  await navigate(proxy, tab, url);
  await waitForComplete(proxy, tab);
  let links = [];
  for (let attempt = 0; attempt < 5; attempt++) {
    await sleep(attempt === 0 ? 800 : 1000);
    const raw = await evalJs(proxy, tab, SCAN_LINKS_SCRIPT);
    try {
      links = JSON.parse(raw || "[]");
    } catch {
      links = [];
    }
    const found = selectSupportingInformationLinks(links, url);
    if (found.attachments.length || found.pages.length) break;
  }
  return links;
}

export async function fetchAttachmentWithNavigationFallback(
  proxy,
  tab,
  attachment,
  resolvePath,
  dependencies = {}
) {
  const fetchImpl = dependencies.fetchImpl || ((p, t, url, outPath) => (
    fetchAnyToFile(p, t, url, outPath, { rejectHtml: true })
  ));
  const navigateImpl = dependencies.navigateImpl || navigate;
  const waitForCompleteImpl = dependencies.waitForCompleteImpl || waitForComplete;
  let result = await fetchImpl(proxy, tab, attachment.url, resolvePath);
  if (result.ok || !/(?:failed to fetch|cors)/i.test(result.err || "")) return result;
  await navigateImpl(proxy, tab, attachment.url);
  await waitForCompleteImpl(proxy, tab);
  return fetchImpl(proxy, tab, attachment.url, resolvePath);
}

function filenameFromDisposition(value = "") {
  const utf8 = value.match(/filename\*\s*=\s*UTF-8''([^;]+)/i);
  if (utf8) {
    try {
      return decodeURIComponent(utf8[1].replace(/^"|"$/g, ""));
    } catch {}
  }
  return (value.match(/filename\s*=\s*"([^"]+)"/i) || value.match(/filename\s*=\s*([^;]+)/i) || [])[1] || "";
}

function safeAttachmentName(value = "") {
  return path.basename(String(value))
    .replace(/[\\/:*?"<>|]+/g, "_")
    .replace(/^\.+/, "")
    .trim()
    .slice(0, 140) || "supplement";
}

function uniqueAttachmentPath(bundleDir, attachment, meta, usedNames) {
  const headerName = filenameFromDisposition(meta.contentDisposition);
  let filename = safeAttachmentName(headerName || attachment.filename);
  if (!path.extname(filename)) {
    let finalName = "";
    try {
      finalName = path.basename(new URL(meta.finalUrl || meta.url || attachment.url).pathname);
    } catch {}
    if (path.extname(finalName)) filename = safeAttachmentName(finalName);
    else {
      const contentType = String(meta.contentType || "").split(";")[0].trim().toLowerCase();
      filename += CONTENT_TYPE_EXTENSION.get(contentType) || "";
    }
  }
  let candidate = filename;
  let suffix = 2;
  while (usedNames.has(candidate.toLowerCase())) {
    const ext = path.extname(filename);
    const stem = filename.slice(0, filename.length - ext.length);
    candidate = `${stem}-${suffix++}${ext}`;
  }
  usedNames.add(candidate.toLowerCase());
  return path.join(bundleDir, candidate);
}

export async function downloadWosSupportingInformation({
  proxy,
  tab,
  landingUrl,
  bundleDir,
  reservedFilenames = [],
  dependencies = {},
}) {
  const scanPageImpl = dependencies.scanPageImpl || scanPage;
  const fetchAttachmentImpl = dependencies.fetchAttachmentImpl || fetchAttachmentWithNavigationFallback;

  let landingLinks;
  try {
    landingLinks = await scanPageImpl(proxy, tab, landingUrl);
  } catch (error) {
    return { status: "fetch_failed", found: 0, downloaded: 0, files: [], failures: [{ url: landingUrl, error: String(error).slice(0, 200) }] };
  }
  const first = selectSupportingInformationLinks(landingLinks, landingUrl);
  const attachments = [...first.attachments];
  const seen = new Set(attachments.map((item) => item.url));
  const failures = [];

  for (const page of first.pages) {
    try {
      const nestedLinks = await scanPageImpl(proxy, tab, page.url);
      const nested = selectSupportingInformationLinks(nestedLinks, page.url);
      for (const attachment of nested.attachments) {
        if (seen.has(attachment.url)) continue;
        seen.add(attachment.url);
        attachments.push(attachment);
        if (attachments.length >= 30) break;
      }
    } catch (error) {
      failures.push({ url: page.url, error: String(error).slice(0, 200) });
    }
    if (attachments.length >= 30) break;
  }

  if (!attachments.length) {
    return {
      status: failures.length ? "fetch_failed" : "not_found",
      found: 0,
      downloaded: 0,
      files: [],
      failures,
    };
  }

  const files = [];
  const usedNames = new Set(reservedFilenames.map((name) => String(name).toLowerCase()));
  for (const attachment of attachments) {
    const result = await fetchAttachmentImpl(
      proxy,
      tab,
      attachment,
      (meta) => uniqueAttachmentPath(bundleDir, attachment, meta, usedNames)
    ).catch((error) => ({ ok: false, err: String(error).slice(0, 200) }));
    if (result.ok) files.push(result.file);
    else failures.push({ url: attachment.url, error: result.err || "download failed" });
  }
  const downloaded = files.length;
  const status = downloaded === attachments.length && failures.length === 0 ? "downloaded" : downloaded > 0 ? "partial" : "fetch_failed";
  return { status, found: attachments.length, downloaded, files, failures };
}
