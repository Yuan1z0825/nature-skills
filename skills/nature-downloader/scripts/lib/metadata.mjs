export function normalizeDoi(value = "") {
  return String(value).trim().replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, "").toLowerCase();
}

export function parseCrossrefWork(work = {}) {
  const links = Array.isArray(work.link) ? work.link : [];
  const pdfLink = links.find((link) => /application\/pdf/i.test(link?.["content-type"] || ""));
  return {
    doi: normalizeDoi(work.DOI || work.doi || ""),
    title: Array.isArray(work.title) ? work.title[0] || "" : work.title || "",
    publisher: work.publisher || "",
    language: work.language || "",
    license: Array.isArray(work.license) ? work.license[0]?.URL || "" : "",
    publisherPdfUrl: pdfLink?.URL || "",
    sourceUrl: work.URL || "",
    type: work.type || "",
  };
}

export async function fetchCrossrefByDoi(doi, { fetchImpl = fetch, mailto = "" } = {}) {
  const headers = { Accept: "application/json" };
  if (mailto) headers["User-Agent"] = `nature-downloader/1.0 (mailto:${mailto})`;
  const response = await fetchImpl(`https://api.crossref.org/works/${encodeURIComponent(normalizeDoi(doi))}`, {
    headers,
    signal: AbortSignal.timeout(30000),
  });
  if (!response.ok) throw new Error(`Crossref DOI lookup failed: HTTP ${response.status}`);
  const body = await response.json();
  return parseCrossrefWork(body?.message || {});
}

export async function findCrossrefByTitle(title, { fetchImpl = fetch, mailto = "" } = {}) {
  const url = new URL("https://api.crossref.org/works");
  url.searchParams.set("query.title", title);
  url.searchParams.set("rows", "5");
  if (mailto) url.searchParams.set("mailto", mailto);
  const response = await fetchImpl(url, { headers: { Accept: "application/json" }, signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`Crossref title lookup failed: HTTP ${response.status}`);
  const items = (await response.json())?.message?.items || [];
  const normalize = (value) => String(value || "").replace(/\s+/g, " ").trim().toLowerCase();
  const exact = items.find((item) => normalize(Array.isArray(item.title) ? item.title[0] : item.title) === normalize(title));
  return exact ? parseCrossrefWork(exact) : null;
}
