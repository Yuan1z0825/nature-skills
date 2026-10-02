import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { classifyFullTextContent } from "./provider-utils.mjs";

export function safeArticleBasename(title = "", doi = "") {
  const base = String(title || doi || "article")
    .trim()
    .replace(/[\/:*?"<>|]+/g, "")
    .replace(/\s+/g, "_")
    .slice(0, 140);
  return base || "article";
}

export async function saveFullTextResponse(response, { outDir, title = "", doi = "", source = "" } = {}) {
  if (!response.ok) return { ok: false, httpStatus: response.status };
  const body = Buffer.from(await response.arrayBuffer());
  const contentType = response.headers.get("content-type") || "";
  const classification = classifyFullTextContent({ contentType, head: body.subarray(0, 65536) });
  if (!classification.valid) return { ok: false, httpStatus: response.status, contentType, ...classification };
  const folder = classification.format === "pdf" ? "PDFs" : "FullText";
  const file = path.join(outDir, folder, `${safeArticleBasename(title, doi)}${classification.extension}`);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temp = `${file}.part-${process.pid}`;
  fs.writeFileSync(temp, body);
  fs.renameSync(temp, file);
  return {
    ok: true,
    file,
    bytes: body.length,
    sha256: crypto.createHash("sha256").update(body).digest("hex"),
    contentType,
    format: classification.format,
    source: source || response.url || "",
  };
}
