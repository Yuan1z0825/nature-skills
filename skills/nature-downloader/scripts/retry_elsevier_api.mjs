#!/usr/bin/env node
// Deprecated compatibility wrapper. The canonical Elsevier implementation is
// scripts/lib/publisher-providers.mjs, orchestrated by batch_download.mjs.

import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
if (!args.length) {
  console.error("retry_elsevier_api.mjs is deprecated. Pass normal batch_download arguments, including --dois, --out, and exactly one of --si/--no-si.");
  process.exit(2);
}
if (!args.includes("--route")) args.push("--route", "elsevier");
const result = spawnSync(process.execPath, [path.join(here, "batch_download.mjs"), ...args], { stdio: "inherit" });
process.exit(result.status ?? 1);
