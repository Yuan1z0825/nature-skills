// PDF fetch + disk-streaming helpers for nature-downloader.
//
// All functions take proxy + target explicitly so they work regardless of
// which script calls them. Bytes are fetched inside the page's authenticated
// context via fetch(), then transferred to Node in base64 chunks and written
// to disk. This is the same approach as the original code but:
//  - deduplicated (fetchToFile / fetchAnyToFile share fetchToBuffer + streamToDisk)
//  - window variable is randomized + deleted after use (avoids multi-tab collisions)
//  - maxBytes guard prevents OOM on huge files
//  - requirePdf flag controls %PDF head validation

import fs from "node:fs";
import path from "node:path";
import { evalJs } from "./cdp-utils.mjs";
import { STATUS } from "./status-codes.mjs";
import { classifyFullTextContent } from "./provider-utils.mjs";

const DEFAULT_MAX_BYTES = 200 * 1024 * 1024; // 200 MB guard
const DEFAULT_CHUNK = 1048576; // 1 MB per base64 round-trip

/**
 * Check if a byte array starts with the %PDF signature.
 */
export function isPdfHead(bytes) {
  if (!bytes || bytes.length < 5) return false;
  const head = String.fromCharCode(...bytes.slice(0, 5));
  return head === "%PDF-";
}

export function isHtmlResponse({ contentType = "", head = [] } = {}) {
  if (/\b(?:text\/html|application\/xhtml\+xml)\b/i.test(contentType)) return true;
  const prefix = Buffer.from(head || []).toString("utf8").trimStart().toLowerCase();
  return prefix.startsWith("<!doctype html") || prefix.startsWith("<html") || prefix.startsWith("<head");
}

export function shouldRejectHtmlResponse(meta, rejectHtml = false) {
  return Boolean(rejectHtml && isHtmlResponse(meta));
}

/**
 * Fetch a URL inside the target tab's authenticated context.
 * Returns { ok, status, size, head, contentType, url } or { ok:false, err }.
 *
 * The bytes are stored in a randomized window variable to avoid collisions
 * when multiple tabs download concurrently.
 */
export async function fetchToBuffer(
  proxy,
  target,
  url,
  { requirePdf = true, maxBytes = DEFAULT_MAX_BYTES } = {}
) {
  // Random window var name so concurrent tabs don't clobber each other.
  const varName = `__litDlBytes_${Math.random().toString(36).slice(2, 10)}`;
  const js = `(async()=>{try{
    const r=await fetch(${JSON.stringify(url)},{credentials:'include'});
    const ab=await r.arrayBuffer();
    const b=new Uint8Array(ab);
    if(b.length>${maxBytes}){return JSON.stringify({ok:false,err:'pdf_too_large',size:b.length});}
    window['${varName}']=b;
    return JSON.stringify({ok:r.ok,status:r.status,size:b.length,head:Array.from(b.slice(0,64)),contentType:r.headers.get('content-type')||'',contentDisposition:r.headers.get('content-disposition')||'',url:r.url||location.href});
  }catch(e){return JSON.stringify({ok:false,err:String(e).slice(0,200)})}})()`;
  const raw = await evalJs(proxy, target, js, 120000);
  const meta = JSON.parse(raw || "{}");

  if (!meta.ok || !meta.size) {
    return { ok: false, err: meta.err || "empty response", varName };
  }
  if (meta.err === "pdf_too_large") {
    return { ok: false, err: STATUS.PDF_TOO_LARGE, size: meta.size, varName };
  }
  if (requirePdf) {
    const headBytes = meta.head || [];
    if (!isPdfHead(headBytes)) {
      // Clean up the window var before returning.
      await evalJs(proxy, target, `delete window['${varName}']`).catch(() => {});
      return { ok: false, err: "not a PDF (head mismatch)", head: meta.head, varName };
    }
  }
  return {
    ok: true,
    status: meta.status,
    size: meta.size,
    head: meta.head,
    contentType: meta.contentType,
    contentDisposition: meta.contentDisposition,
    url: meta.url,
    varName,
  };
}

/**
 * Stream bytes from a window variable to disk in base64 chunks.
 * Deletes the window variable when done (or on error).
 */
export async function streamToDisk(
  proxy,
  target,
  varName,
  size,
  outPath,
  chunkSize = DEFAULT_CHUNK,
  onProgress,
  evalImpl = evalJs
) {
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  const tempPath = `${outPath}.part-${process.pid}-${Math.random().toString(36).slice(2, 10)}`;
  let handle;
  try {
    handle = await fs.promises.open(tempPath, "w");
    for (let s = 0; s < size; s += chunkSize) {
      const e = Math.min(s + chunkSize, size);
      const b64 = await evalImpl(
        proxy,
        target,
        `(()=>{const b=window['${varName}'].slice(${s},${e});let x='';for(let i=0;i<b.length;i+=0x8000){x+=String.fromCharCode.apply(null,b.subarray(i,i+0x8000));}return btoa(x);})()`,
        60000
      );
      const chunk = Buffer.from(b64, "base64");
      if (chunk.length !== e - s) {
        throw new Error(`browser download chunk size mismatch: expected ${e - s}, received ${chunk.length}`);
      }
      let offset = 0;
      while (offset < chunk.length) {
        const { bytesWritten } = await handle.write(
          chunk,
          offset,
          chunk.length - offset,
        );
        offset += bytesWritten;
      }
      if (onProgress) onProgress(e, size);
    }
    await handle.close();
    handle = undefined;
    fs.renameSync(tempPath, outPath);
  } finally {
    if (handle) await handle.close().catch(() => {});
    if (fs.existsSync(tempPath)) fs.unlinkSync(tempPath);
    // Always clean up the window var, even on error.
    await evalImpl(proxy, target, `delete window['${varName}']`).catch(() => {});
  }
  return { file: outPath, bytes: size };
}

/**
 * Fetch a URL (requiring %PDF) and stream to disk.
 * Returns { ok:true, file, bytes } or { ok:false, err }.
 */
export async function fetchToFile(proxy, target, url, outPath, { onProgress, maxBytes } = {}) {
  const meta = await fetchToBuffer(proxy, target, url, { requirePdf: true, maxBytes });
  if (!meta.ok) return { ok: false, err: meta.err };
  const res = await streamToDisk(
    proxy,
    target,
    meta.varName,
    meta.size,
    outPath,
    DEFAULT_CHUNK,
    onProgress
  );
  return { ok: true, ...res };
}

/**
 * Like fetchToFile but accepts any binary (SI can be jpg/xlsx/docx — not PDF).
 * Returns { ok:true, bytes } or { ok:false, err }.
 */
export async function fetchAnyToFile(proxy, target, url, outPath, { onProgress, maxBytes, rejectHtml = false } = {}) {
  const meta = await fetchToBuffer(proxy, target, url, { requirePdf: false, maxBytes });
  if (!meta.ok) return { ok: false, err: meta.err };
  if (shouldRejectHtmlResponse(meta, rejectHtml)) {
    await evalJs(proxy, target, `delete window['${meta.varName}']`).catch(() => {});
    return { ok: false, err: "HTML response rejected" };
  }
  const resolvedOutPath = typeof outPath === "function" ? outPath(meta) : outPath;
  const res = await streamToDisk(
    proxy,
    target,
    meta.varName,
    meta.size,
    resolvedOutPath,
    DEFAULT_CHUNK,
    onProgress
  );
  return {
    ok: true,
    file: res.file,
    bytes: res.bytes,
    contentType: meta.contentType,
    contentDisposition: meta.contentDisposition,
    finalUrl: meta.url,
  };
}

export async function fetchNativeToFile(proxy, target, url, outPath, { allowedFormats = ["caj", "html", "jats_xml"], onProgress, maxBytes } = {}) {
  const meta = await fetchToBuffer(proxy, target, url, { requirePdf: false, maxBytes });
  if (!meta.ok) return { ok: false, err: meta.err };
  const classification = classifyFullTextContent({ contentType: meta.contentType, head: meta.head });
  if (!classification.valid || !allowedFormats.includes(classification.format)) {
    await evalJs(proxy, target, `delete window['${meta.varName}']`).catch(() => {});
    return { ok: false, err: classification.reason || `unexpected format ${classification.format}` };
  }
  const result = await streamToDisk(proxy, target, meta.varName, meta.size, outPath, DEFAULT_CHUNK, onProgress);
  return { ok: true, ...result, format: classification.format, contentType: meta.contentType, finalUrl: meta.url };
}
