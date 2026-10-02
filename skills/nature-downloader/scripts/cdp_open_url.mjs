#!/usr/bin/env node
import { DEFAULT_PROXY, healthCheck, proxyGet, proxyPostUrl, waitForComplete } from "./lib/cdp-utils.mjs";

function usage() {
  console.log(`Usage:
  node cdp_open_url.mjs --url <url> [--proxy http://127.0.0.1:3456] [--wait]

Opens a URL in the already-authorized Chrome CDP proxy.
This helper URL-encodes nested URLs correctly, which matters for URLs containing # or #! fragments.
It does not read cookies, passwords, local storage, or browser profiles.`);
}

function parseArgs(argv) {
  const args = {
    proxy: DEFAULT_PROXY,
    wait: false,
  };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--help" || a === "-h") args.help = true;
    else if (a === "--url") args.url = argv[++i];
    else if (a === "--proxy") args.proxy = argv[++i].replace(/\/$/, "");
    else if (a === "--wait") args.wait = true;
    else throw new Error(`Unknown argument: ${a}`);
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    usage();
    return;
  }
  if (!args.url) throw new Error("--url is required");

  // Fail fast with a friendly message if the CDP proxy isn't running.
  await healthCheck(args.proxy);

  const created = await proxyPostUrl(args.proxy, "/new", args.url, {}, 60000);
  const target = created.targetId;
  const info = args.wait
    ? await waitForComplete(args.proxy, target)
    : await proxyGet(args.proxy, "/info", { target }, 10000);
  console.log(
    JSON.stringify(
      {
        targetId: target,
        title: info?.title || null,
        url: info?.url || null,
        ready: info?.ready || null,
      },
      null,
      2
    )
  );
}

main().catch((error) => {
  console.error(error.stack || String(error));
  process.exit(1);
});
