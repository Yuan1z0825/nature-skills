import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { PUBLISHER_PROVIDERS } from "./provider-registry.mjs";

const PROVIDERS = new Set(PUBLISHER_PROVIDERS);

export function credentialsPathFromEnv(env = process.env) {
  const dir = env.LIT_DL_CONFIG_DIR || path.join(os.homedir(), ".config", "lit-dl");
  return path.join(dir, "credentials.json");
}

export function loadCredentials(env = process.env) {
  const file = credentialsPathFromEnv(env);
  if (!fs.existsSync(file)) return {};
  try {
    const value = JSON.parse(fs.readFileSync(file, "utf8"));
    return value && typeof value === "object" ? value : {};
  } catch {
    return {};
  }
}

function assertProvider(provider) {
  if (!PROVIDERS.has(provider)) throw new Error(`unsupported provider: ${provider}`);
}

function writeCredentials(value, env) {
  const file = credentialsPathFromEnv(env);
  fs.mkdirSync(path.dirname(file), { recursive: true, mode: 0o700 });
  const temp = `${file}.tmp-${process.pid}`;
  fs.writeFileSync(temp, `${JSON.stringify(value, null, 2)}\n`, { mode: 0o600 });
  fs.chmodSync(temp, 0o600);
  fs.renameSync(temp, file);
  fs.chmodSync(file, 0o600);
  return file;
}

export function saveProviderCredentials(provider, secrets, env = process.env) {
  assertProvider(provider);
  const clean = Object.fromEntries(
    Object.entries(secrets || {}).filter(([, value]) => typeof value === "string" && value.trim()).map(([key, value]) => [key, value.trim()])
  );
  if (!clean.api_key) throw new Error("api_key is required");
  const all = loadCredentials(env);
  all[provider] = clean;
  writeCredentials(all, env);
  return clean;
}

export function deleteProviderCredentials(provider, env = process.env) {
  assertProvider(provider);
  const all = loadCredentials(env);
  delete all[provider];
  writeCredentials(all, env);
}

export function providerCredentials(provider, env = process.env) {
  assertProvider(provider);
  return loadCredentials(env)[provider] || null;
}

export function maskSecret(value = "") {
  const text = String(value);
  if (!text) return "";
  if (text.length <= 4) return "*".repeat(text.length);
  return `${"*".repeat(text.length - 4)}${text.slice(-4)}`;
}

export function maskedCredentials(env = process.env) {
  const all = loadCredentials(env);
  return Object.fromEntries(Object.entries(all).map(([provider, values]) => [
    provider,
    Object.fromEntries(Object.entries(values || {}).map(([key, value]) => [key, maskSecret(value)])),
  ]));
}
