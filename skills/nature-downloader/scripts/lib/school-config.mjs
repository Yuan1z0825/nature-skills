import fs from "node:fs";
import os from "node:os";
import path from "node:path";

export const DEFAULT_DISCOVERY_URL = "https://www.webofscience.com/wos/woscc/basic-search";

export function configPathFromEnv(env = process.env) {
  const dir = env.LIT_DL_CONFIG_DIR || path.join(os.homedir(), ".config", "lit-dl");
  return path.join(dir, "school.json");
}

export function loadSchoolConfig(env = process.env) {
  const file = configPathFromEnv(env);
  if (!fs.existsSync(file)) return null;
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return null;
  }
}

export function discoveryUrlFromConfig(config) {
  return (
    config?.discovery?.web_of_science_url ||
    config?.discovery?.wos_url ||
    config?.discovery?.url ||
    DEFAULT_DISCOVERY_URL
  );
}

export function schoolSummary(config) {
  if (!config) return "unconfigured";
  const school = config.school?.name || "unknown school";
  const auth = config.auth?.type || "unknown auth";
  return `${school} (${auth})`;
}
