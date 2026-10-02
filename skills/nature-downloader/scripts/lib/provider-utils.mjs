import { STATUS } from "./status-codes.mjs";

const LOGIN_RE = /\b(?:log[ -]?in|sign[ -]?in|password|authentication required|access denied|forbidden)\b|登录|统一身份认证|无权访问/i;

function bytesToText(head) {
  return Buffer.from(head || []).toString("utf8");
}

export function classifyFullTextContent({ contentType = "", head = Buffer.alloc(0) } = {}) {
  const bytes = Buffer.from(head || []);
  const text = bytesToText(bytes).trimStart();
  const lowerType = String(contentType).toLowerCase();
  if (bytes.subarray(0, 5).toString("ascii") === "%PDF-") return { valid: true, format: "pdf", extension: ".pdf" };
  if (/^(?:CAJ|HN|KDH)/.test(bytes.subarray(0, 12).toString("ascii"))) return { valid: true, format: "caj", extension: ".caj" };
  if (/html|xhtml/.test(lowerType) || /^<!doctype html|^<html|^<head/i.test(text)) {
    if (LOGIN_RE.test(text)) return { valid: false, format: "html", reason: "login_or_error_page" };
    if (/<article[\s>]|\bfull[- ]text\b|class=["'][^"']*(?:article-body|fulltext)/i.test(text)) {
      return { valid: true, format: "html", extension: ".html" };
    }
    return { valid: false, format: "html", reason: "not_fulltext_html" };
  }
  if (/xml|jats/.test(lowerType) || /^<\?xml|^<article[\s>]/i.test(text)) {
    if (/<article[\s>]|<book-part-wrapper[\s>]/i.test(text)) return { valid: true, format: "jats_xml", extension: ".xml" };
    return { valid: false, format: "xml", reason: "not_jats_fulltext" };
  }
  return { valid: false, format: "unknown", reason: "unsupported_or_invalid_content" };
}

export function classifyProviderFailure({ status = 0 } = {}) {
  if (status === 401) return STATUS.CREDENTIALS_INVALID;
  if (status === 403) return STATUS.API_NOT_ENTITLED;
  if (status === 404 || status === 204) return STATUS.API_FULLTEXT_UNAVAILABLE;
  if (status === 429) return STATUS.RATE_LIMITED;
  return STATUS.API_FULLTEXT_UNAVAILABLE;
}
