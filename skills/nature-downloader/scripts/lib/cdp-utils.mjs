// Shared CDP proxy client for nature-downloader scripts.
//
// All functions take the proxy URL as an explicit parameter (fixes the
// --proxy bug in batch_download.mjs where PROXY was a hard-coded const and
// args.proxy was parsed but never used).
//
// Endpoint reference (web-access CDP proxy v2.5.3+):
//   GET  /targets              -> [{targetId, url, title, ...}]
//   GET  /info?target=<id>     -> {targetId, url, title, ready, ...}
//   POST /new       (body=url) -> {targetId, ...}
//   POST /navigate  (body=url, ?target=id) -> {...}
//   POST /eval      (body=js,  ?target=id) -> {value, ...}
//   POST /click     (body=sel, ?target=id) -> {...}
//   GET  /close?target=<id>    -> {...}
//   GET  /scroll?target=<id>&direction=bottom -> {...}

import { STATUS } from "./status-codes.mjs";

export const DEFAULT_PROXY = "http://127.0.0.1:3456";

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * Check that the CDP proxy is reachable. Throws a friendly error with
 * remediation hints if not.
 */
export async function healthCheck(proxy = DEFAULT_PROXY, timeoutMs = 5000) {
  const u = new URL("/targets", proxy);
  let err;
  try {
    const r = await fetch(u, { signal: AbortSignal.timeout(timeoutMs) });
    if (!r.ok) {
      err = `HTTP ${r.status}`;
    } else {
      await r.json(); // parse to confirm it's the proxy, not a random page
      return true;
    }
  } catch (e) {
    err = e.code || e.name || String(e).split("\n")[0].slice(0, 80);
  }
  throw new Error(
    `CDP proxy not reachable at ${proxy} (${err}).\n` +
      `  Start: node <web-access>/scripts/check-deps.mjs\n` +
      `  Verify: chrome://inspect/#remote-debugging -> enable "Allow remote debugging"\n` +
      `  Probe: curl ${proxy}/targets`
  );
}

/**
 * Fetch JSON from a URL with timeout. Throws on HTTP error with status + body slice.
 */
export async function httpJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    signal: AbortSignal.timeout(options.timeoutMs || 60000),
  });
  const text = await response.text();
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} from ${url}: ${text.slice(0, 500)}`);
  }
  return JSON.parse(text);
}

/**
 * GET to a proxy endpoint with query params.
 */
export async function proxyGet(proxy, endpoint, params = {}, timeoutMs = 60000) {
  const u = new URL(endpoint, proxy);
  for (const [k, v] of Object.entries(params)) u.searchParams.set(k, v);
  return httpJson(u.toString(), { timeoutMs });
}

/**
 * POST to a proxy endpoint where the URL/payload goes in the body
 * (web-access CDP proxy v2.5.3+: /new and /navigate take URL in POST body
 * so query params with their own ? fragments don't get mis-split).
 */
export async function proxyPostUrl(proxy, endpoint, url, params = {}, timeoutMs = 60000) {
  const u = new URL(endpoint, proxy);
  for (const [k, v] of Object.entries(params)) u.searchParams.set(k, v);
  return httpJson(u.toString(), { method: "POST", body: url, timeoutMs });
}

/**
 * POST JS to /eval and return the full response object {value, ...}.
 */
export async function proxyEval(proxy, target, js, timeoutMs = 60000) {
  return proxyPostUrl(proxy, "/eval", js, { target }, timeoutMs);
}

/**
 * POST JS to /eval and return just the .value (the common case).
 */
export async function evalJs(proxy, target, js, timeoutMs = 60000) {
  const r = await proxyEval(proxy, target, js, timeoutMs);
  return r && r.value;
}

/**
 * Poll /info until ready === "complete" or maxMs elapsed.
 * Returns the last info object (may be null on persistent failure).
 */
export async function waitForComplete(proxy, target, maxMs = 45000) {
  const started = Date.now();
  let last = null;
  while (Date.now() - started < maxMs) {
    try {
      last = await proxyGet(proxy, "/info", { target }, 10000);
      if (last.ready === "complete") return last;
    } catch (_) {}
    await sleep(1000);
  }
  return last;
}

/**
 * Open a new tab at the given URL. Returns {targetId, ...}.
 */
export async function newTab(proxy, url, timeoutMs = 60000) {
  return proxyPostUrl(proxy, "/new", url, {}, timeoutMs);
}

/**
 * Navigate an existing tab to a URL.
 */
export async function navigate(proxy, target, url, timeoutMs = 60000) {
  return proxyPostUrl(proxy, "/navigate", url, { target }, timeoutMs);
}

/**
 * Close a tab. Swallows errors (best-effort cleanup).
 */
export async function closeTab(proxy, target) {
  try {
    await proxyGet(proxy, "/close", { target }, 10000);
  } catch (_) {}
}

/**
 * List all open targets/tabs.
 */
export async function listTargets(proxy) {
  return proxyGet(proxy, "/targets");
}

/**
 * Click an element matching a CSS selector in the target tab.
 * Swallows errors (used for cookie consent, search button — non-critical).
 */
export async function click(proxy, target, selector, timeoutMs = 30000) {
  try {
    return await proxyPostUrl(proxy, "/click", selector, { target }, timeoutMs);
  } catch (_) {
    return null;
  }
}

/**
 * Scroll the target tab in a direction (default "bottom").
 * Swallows errors.
 */
export async function scroll(proxy, target, direction = "bottom") {
  try {
    return await proxyGet(proxy, "/scroll", { target, direction }, 30000);
  } catch (_) {
    return null;
  }
}
