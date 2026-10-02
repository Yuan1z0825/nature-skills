import { isCnkiUrl, looksChinese } from "./cnki.mjs";
import { PROVIDER_REGISTRY } from "./provider-registry.mjs";
import { STATUS } from "./status-codes.mjs";

export function parseSiChoice({ si = false, noSi = false } = {}) {
  if (si && noSi) throw new Error("--si and --no-si are mutually exclusive");
  if (!si && !noSi) return { confirmed: false, status: STATUS.SI_CONFIRMATION_REQUIRED };
  return { confirmed: true, wantSi: Boolean(si) };
}

export function classifyPublisher({ doi = "", publisher = "", sourceUrl = "" } = {}) {
  const marker = `${publisher} ${sourceUrl}`.toLowerCase();
  for (const [provider, descriptor] of Object.entries(PROVIDER_REGISTRY)) {
    if (new RegExp(descriptor.doi_pattern, "i").test(doi) || new RegExp(descriptor.marker_pattern, "i").test(marker)) return provider;
  }
  return "other";
}

export function hasUsablePublisherCredentials(provider, credentials) {
  if (!credentials?.api_key) return false;
  return provider !== "ieee" || Boolean(credentials.fulltext_endpoint);
}

export function isChineseLiterature({ title = "", language = "", sourceUrl = "", cnki = null } = {}) {
  if (cnki) return true;
  if (sourceUrl && isCnkiUrl(sourceUrl)) return true;
  if (/^(?:zh|zho|chi)(?:[-_]|$)/i.test(language)) return true;
  return looksChinese(title);
}

export function chooseDirectUrlRoute({ pdfUrl = "", title = "", language = "", sourceUrl = "", route = "" } = {}) {
  if (isCnkiUrl(pdfUrl)) return { provider: "cnki", mode: "direct", reason: "explicit_cnki_url" };
  if (route === "cnki" || isChineseLiterature({ title, language, sourceUrl })) {
    return { provider: "cnki", mode: "title_search", reason: route === "cnki" ? "explicit_override" : "chinese_literature" };
  }
  return { provider: "direct_url", mode: "direct", reason: "explicit_pdf_url" };
}

export function chooseRoute(article = {}) {
  if (article.routeOverride) return { provider: article.routeOverride, reason: "explicit_override" };
  if (isChineseLiterature(article)) return { provider: "cnki", reason: "chinese_literature" };
  const publisher = classifyPublisher(article);
  if (publisher !== "other" && article.hasPublisherCredentials) {
    return { provider: publisher, reason: "publisher_api_credentials_available" };
  }
  if (article.isOa === true) return { provider: "open_access", reason: "article_level_oa" };
  if (publisher !== "other") return { provider: publisher, reason: "supported_publisher" };
  return { provider: "web_access", reason: "other_publisher" };
}
