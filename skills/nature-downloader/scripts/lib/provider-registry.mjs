import fs from "node:fs";

const file = new URL("../../data/publishers.json", import.meta.url);
export const PROVIDER_REGISTRY = Object.freeze(JSON.parse(fs.readFileSync(file, "utf8")));
export const PUBLISHER_PROVIDERS = Object.freeze(Object.keys(PROVIDER_REGISTRY));

export function providerDescriptor(provider) {
  return PROVIDER_REGISTRY[provider] || null;
}
