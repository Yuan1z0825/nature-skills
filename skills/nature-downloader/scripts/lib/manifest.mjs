import fs from "node:fs";
import path from "node:path";

const SECRET_KEY_RE = /(?:api[_-]?key|secret|password|cookie|session|authtoken|insttoken|access[_-]?token|authorization)/i;
const SECRET_QUERY_RE = /([?&](?:api[_-]?key|apikey|secret|password|authtoken|insttoken|access[_-]?token|authorization)=)[^&#\s"']*/gi;

function redactString(value) {
  return value
    .replace(SECRET_QUERY_RE, "$1[REDACTED]")
    .replace(/\b(Bearer\s+)[A-Za-z0-9._~+/=-]+/gi, "$1[REDACTED]");
}

function redact(value) {
  if (Array.isArray(value)) return value.map(redact);
  if (typeof value === "string") return redactString(value);
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(
    Object.entries(value)
      .filter(([key]) => !SECRET_KEY_RE.test(key))
      .map(([key, child]) => [key, redact(child)])
  );
}

export function writeManifest(outDir, manifest) {
  fs.mkdirSync(outDir, { recursive: true });
  const file = path.join(outDir, "manifest.json");
  const temp = `${file}.tmp-${process.pid}`;
  const payload = {
    version: 2,
    generated_at: new Date().toISOString(),
    ...redact(manifest),
  };
  fs.writeFileSync(temp, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  fs.renameSync(temp, file);
  return file;
}
