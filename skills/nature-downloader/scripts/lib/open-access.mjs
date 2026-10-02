import path from "node:path";

export function normalizeTitle(title = "") {
  return String(title).replace(/\s+/g, " ").trim().toLowerCase();
}

export function exactTitleMatch(candidate, expected) {
  return normalizeTitle(candidate) === normalizeTitle(expected);
}

export function normalizeArxivId(value = "") {
  const text = String(value).trim();
  const match = text.match(/(?:arxiv\.org\/(?:abs|pdf)\/)?([a-z-]+\/\d{7}|\d{4}\.\d{4,5})(v\d+)?(?:\.pdf)?/i);
  if (!match) return "";
  return `${match[1]}${match[2] || ""}`;
}

export function arxivPdfUrl(id) {
  const normalized = normalizeArxivId(id);
  if (!normalized) return "";
  return `https://arxiv.org/pdf/${normalized}`;
}

function decodeXml(text = "") {
  return text
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

export function parseArxivAtom(xml, expectedTitle) {
  const entries = String(xml).match(/<entry>[\s\S]*?<\/entry>/g) || [];
  for (const entry of entries) {
    const title = decodeXml((entry.match(/<title>([\s\S]*?)<\/title>/) || [])[1] || "").replace(/\s+/g, " ").trim();
    if (!exactTitleMatch(title, expectedTitle)) continue;
    const rawId = decodeXml((entry.match(/<id>([\s\S]*?)<\/id>/) || [])[1] || "");
    const id = normalizeArxivId(rawId);
    if (!id) continue;
    return { id, title, pdfUrl: arxivPdfUrl(id) };
  }
  return null;
}

export async function findArxivByTitle(title, { fetchImpl = fetch } = {}) {
  const url = new URL("https://export.arxiv.org/api/query");
  url.searchParams.set("search_query", `ti:"${title}"`);
  url.searchParams.set("start", "0");
  url.searchParams.set("max_results", "5");
  const response = await fetchImpl(url, { signal: AbortSignal.timeout(30000) });
  if (!response.ok) {
    throw new Error(`arXiv lookup failed: HTTP ${response.status}`);
  }
  return parseArxivAtom(await response.text(), title);
}

export function parsePmcOaXml(xml = "") {
  const links = [];
  const linkRe = /<link\b([^>]+)>/gi;
  for (const match of String(xml).matchAll(linkRe)) {
    const attrs = match[1];
    const format = (attrs.match(/\bformat=["']([^"']+)/i) || [])[1] || "";
    const href = (attrs.match(/\bhref=["']([^"']+)/i) || [])[1] || "";
    if (!href || !/pdf/i.test(format)) continue;
    links.push({ source: "pmc", url: href, format: "pdf", version: "publishedVersion", license: "pmc-oa" });
  }
  return links;
}

export function parseUnpaywallRecord(record = {}) {
  if (!record?.is_oa) return [];
  const locations = [record.best_oa_location, ...(record.oa_locations || [])].filter(Boolean);
  const seen = new Set();
  const out = [];
  for (const location of locations) {
    const url = location.url_for_pdf || location.url || "";
    if (!url || seen.has(url)) continue;
    seen.add(url);
    out.push({
      source: location.host_type === "publisher" ? "publisher_oa" : "repository",
      resolver: "unpaywall",
      url,
      format: location.url_for_pdf ? "pdf" : "landing",
      hostType: location.host_type || "",
      version: location.version || "",
      license: location.license || record.license || "",
    });
  }
  return out;
}

export function rankOaCandidates(candidates = []) {
  const sourceRank = { pmc: 0, unpaywall: 1, publisher_oa: 2, repository: 3, arxiv: 4 };
  return [...candidates].sort((a, b) => {
    const source = (sourceRank[a.source] ?? 99) - (sourceRank[b.source] ?? 99);
    if (source) return source;
    return (a.format === "pdf" ? 0 : 1) - (b.format === "pdf" ? 0 : 1);
  });
}

export async function findPmcCandidates(pmcid, { fetchImpl = fetch } = {}) {
  if (!pmcid) return [];
  const response = await fetchImpl(`https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=${encodeURIComponent(pmcid)}`, { signal: AbortSignal.timeout(30000) });
  if (!response.ok) return [];
  return parsePmcOaXml(await response.text());
}

export async function findUnpaywallCandidates(doi, email, { fetchImpl = fetch } = {}) {
  if (!doi || !email) return [];
  const record = await fetchUnpaywallRecord(doi, email, { fetchImpl });
  return parseUnpaywallRecord(record);
}

export async function fetchUnpaywallRecord(doi, email, { fetchImpl = fetch } = {}) {
  if (!doi || !email) return null;
  const response = await fetchImpl(`https://api.unpaywall.org/v2/${encodeURIComponent(doi)}?email=${encodeURIComponent(email)}`, { signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`Unpaywall lookup failed: HTTP ${response.status}`);
  return response.json();
}

export function filenameForPdfUrl(url, title = "") {
  if (title) {
    const safeTitle = title
      .trim()
      .replace(/[\/:*?"<>|]+/g, "")
      .replace(/\s+/g, "_")
      .slice(0, 120);
    if (safeTitle) return `${safeTitle}.pdf`;
  }
  const base = path.basename(new URL(url).pathname) || "paper.pdf";
  return base.endsWith(".pdf") ? base : `${base}.pdf`;
}
