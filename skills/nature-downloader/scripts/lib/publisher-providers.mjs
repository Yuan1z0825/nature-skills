import { saveFullTextResponse } from "./direct-download.mjs";
import { classifyProviderFailure } from "./provider-utils.mjs";
import { STATUS } from "./status-codes.mjs";
import { PROVIDER_REGISTRY } from "./provider-registry.mjs";

export const PROVIDER_CONFIG_URLS = Object.freeze(Object.fromEntries(
  Object.entries(PROVIDER_REGISTRY).map(([provider, descriptor]) => [provider, descriptor.config_url])
));

const SECRET_QUERY_PARAM_RE = /^(?:api[_-]?key|apikey|secret|password|authtoken|insttoken|access[_-]?token|authorization)$/i;

function safeSourceUrl(value) {
  const url = new URL(value);
  for (const key of [...url.searchParams.keys()]) {
    if (SECRET_QUERY_PARAM_RE.test(key)) url.searchParams.delete(key);
  }
  return String(url);
}

function providerRequest(article, provider, credentials) {
  const doi = encodeURIComponent(article.doi || "");
  if (provider === "elsevier") {
    const headers = { Accept: "application/pdf", "X-ELS-APIKey": credentials.api_key };
    if (credentials.insttoken) headers["X-ELS-Insttoken"] = credentials.insttoken;
    if (credentials.authtoken) headers["X-ELS-Authtoken"] = credentials.authtoken;
    return { url: `https://api.elsevier.com/content/article/doi/${doi}?httpAccept=application/pdf`, options: { headers } };
  }
  if (provider === "springer_nature") {
    const url = new URL("https://spdi.public.springernature.app/xmldata/jats");
    url.searchParams.set("q", `doi:${article.doi}`);
    url.searchParams.set("api_key", credentials.api_key);
    return { url, options: { headers: { Accept: "application/xml" } } };
  }
  if (provider === "ieee") {
    if (!credentials.fulltext_endpoint) {
      return { unavailable: "IEEE metadata API key is configured, but paid Full-Text Access API product/endpoint is missing" };
    }
    const endpoint = credentials.fulltext_endpoint.replace("{doi}", encodeURIComponent(article.doi || ""));
    const url = new URL(endpoint);
    if (!url.searchParams.has("apikey")) url.searchParams.set("apikey", credentials.api_key);
    return { url, options: { headers: { Accept: "application/pdf, text/html, application/xml" } } };
  }
  throw new Error(`unsupported publisher provider: ${provider}`);
}

function failureResult(provider, status, extra = {}) {
  return {
    provider,
    status,
    fallbackConfirmationRequired: status === STATUS.API_NOT_ENTITLED || status === STATUS.API_FULLTEXT_UNAVAILABLE,
    ...extra,
  };
}

export async function downloadPublisherArticle(article, {
  provider,
  credentials,
  outDir,
  fetchImpl = fetch,
  sleepImpl = (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
} = {}) {
  if (!credentials?.api_key) {
    return failureResult(provider, STATUS.CREDENTIALS_MISSING, { configureUrl: PROVIDER_CONFIG_URLS[provider] });
  }
  const request = providerRequest(article, provider, credentials);
  if (request.unavailable) return failureResult(provider, STATUS.API_FULLTEXT_UNAVAILABLE, { detail: request.unavailable });
  let response;
  const maxAttempts = provider === "elsevier" ? 3 : 1;
  let lastError = "";
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      response = await fetchImpl(request.url, { ...request.options, signal: AbortSignal.timeout(60000) });
      if (!(provider === "elsevier" && (response.status === 429 || response.status >= 500) && attempt < maxAttempts)) break;
      lastError = `HTTP ${response.status}`;
    } catch (error) {
      lastError = String(error?.message || error).slice(0, 200);
      if (attempt === maxAttempts) break;
    }
    await sleepImpl(250 * attempt);
  }
  if (!response) return failureResult(provider, STATUS.API_FULLTEXT_UNAVAILABLE, { reason: lastError || "request failed", attempts: maxAttempts });
  if (!response.ok) {
    return failureResult(provider, classifyProviderFailure({ status: response.status }), { httpStatus: response.status, attempts: maxAttempts });
  }

  const saved = await saveFullTextResponse(response, {
    outDir,
    title: article.title,
    doi: article.doi,
    source: safeSourceUrl(request.url),
  });
  if (!saved.ok) {
    return failureResult(provider, STATUS.API_FULLTEXT_UNAVAILABLE, {
      httpStatus: saved.httpStatus,
      contentType: saved.contentType,
      reason: saved.reason,
    });
  }
  return {
    provider,
    status: saved.format === "pdf"
      ? STATUS.DOWNLOADED
      : saved.format === "html"
        ? STATUS.FULL_TEXT_HTML_AVAILABLE
        : STATUS.NATIVE_FULLTEXT_DOWNLOADED,
    accessMode: "publisher_api",
    ...saved,
  };
}
