import { saveFullTextResponse } from "./direct-download.mjs";
import {
  findPmcCandidates,
  fetchUnpaywallRecord,
  parseUnpaywallRecord,
  rankOaCandidates,
} from "./open-access.mjs";
import { STATUS } from "./status-codes.mjs";

function httpsForFtp(url = "") {
  return String(url).replace(/^ftp:\/\/ftp\.ncbi\.nlm\.nih\.gov\//i, "https://ftp.ncbi.nlm.nih.gov/");
}

async function tryCandidates(article, candidates, { outDir, fetchImpl }) {
  const attempts = [];
  for (const candidate of rankOaCandidates(candidates)) {
    const url = httpsForFtp(candidate.url);
    let response;
    try {
      response = await fetchImpl(url, { headers: { Accept: "application/pdf, text/html, application/xml" }, signal: AbortSignal.timeout(60000) });
    } catch (error) {
      attempts.push({ source: candidate.source, url, status: "request_failed", reason: String(error?.message || error).slice(0, 120) });
      continue;
    }
    const saved = await saveFullTextResponse(response, { outDir, title: article.title, doi: article.doi, source: url });
    if (!saved.ok) {
      attempts.push({ source: candidate.source, url, status: "invalid_or_unavailable", http_status: saved.httpStatus, reason: saved.reason || "invalid content" });
      continue;
    }
    return { downloaded: {
      status: saved.format === "html"
        ? STATUS.FULL_TEXT_HTML_AVAILABLE
        : saved.format === "pdf"
          ? STATUS.OPEN_ACCESS_DOWNLOADED
          : STATUS.NATIVE_FULLTEXT_DOWNLOADED,
      provider: "open_access",
      accessMode: "open_access",
      oaEvidence: candidate,
      ...saved,
      oaAttempts: attempts,
    }, attempts };
  }
  return { downloaded: null, attempts };
}

async function findPmcidByDoi(doi, fetchImpl) {
  if (!doi) return { pmcid: "", checked: false };
  const url = new URL("https://www.ebi.ac.uk/europepmc/webservices/rest/search");
  url.searchParams.set("query", `DOI:${doi}`);
  url.searchParams.set("format", "json");
  const response = await fetchImpl(url, { headers: { Accept: "application/json" }, signal: AbortSignal.timeout(30000) });
  if (!response.ok) return { pmcid: "", checked: false, error: `Europe PMC HTTP ${response.status}` };
  const record = (await response.json())?.resultList?.result?.[0];
  return { pmcid: record?.pmcid || "", checked: true };
}

export async function downloadOpenAccessArticle(article, {
  email = "",
  outDir,
  fetchImpl = fetch,
} = {}) {
  const pmcLookup = article.pmcid
    ? { pmcid: article.pmcid, checked: true }
    : await findPmcidByDoi(article.doi, fetchImpl).catch((error) => ({ pmcid: "", checked: false, error: String(error?.message || error).slice(0, 120) }));
  const pmcid = pmcLookup.pmcid;
  const allAttempts = [];
  if (pmcid) {
    const pmc = await findPmcCandidates(pmcid, { fetchImpl }).catch(() => []);
    const attempt = await tryCandidates(article, pmc, { outDir, fetchImpl });
    allAttempts.push(...attempt.attempts);
    if (attempt.downloaded) return attempt.downloaded;
  }

  let unpaywallRecord = null;
  let unpaywallChecked = false;
  let unpaywallError = "";
  if (article.doi && email) {
    try {
      unpaywallRecord = await fetchUnpaywallRecord(article.doi, email, { fetchImpl });
      unpaywallChecked = true;
    } catch (error) {
      unpaywallError = String(error?.message || error).slice(0, 120);
    }
  }
  const unpaywall = parseUnpaywallRecord(unpaywallRecord);
  const publisher = article.publisherPdfUrl && article.license
    ? [{ source: "publisher_oa", url: article.publisherPdfUrl, format: "pdf", version: "publishedVersion", license: article.license }]
    : [];
  const attempt = await tryCandidates(article, [...unpaywall, ...publisher], { outDir, fetchImpl });
  allAttempts.push(...attempt.attempts);
  if (attempt.downloaded) return attempt.downloaded;
  const confirmedOa = Boolean(pmcid || unpaywallRecord?.is_oa || article.license);
  const confirmedClosed = Boolean(unpaywallChecked && unpaywallRecord?.is_oa === false);
  return {
    status: STATUS.OA_NOT_FOUND,
    provider: "open_access",
    doi: article.doi,
    title: article.title,
    oaAssessment: confirmedOa ? "confirmed_oa" : confirmedClosed ? "confirmed_closed" : "unknown",
    oaChecks: {
      pmc: { checked: pmcLookup.checked, pmcid: pmcid || "", error: pmcLookup.error || "" },
      unpaywall: { checked: unpaywallChecked, error: unpaywallError, is_oa: unpaywallRecord?.is_oa ?? null },
      crossref_license: article.license || "",
    },
    oaAttempts: allAttempts,
  };
}
