#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import {
  DEFAULT_PROXY,
  healthCheck,
  proxyGet,
  proxyEval,
  proxyPostUrl,
  waitForComplete,
  closeTab,
} from "./lib/cdp-utils.mjs";
import { isPdfHead } from "./lib/pdf-utils.mjs";

function usage() {
  console.log(`Usage:
  node browser_pdf_downloader.mjs --url <pdf-url> --out <file.pdf> [--proxy http://127.0.0.1:3456] [--close] [--allow-non-pdf]
  node browser_pdf_downloader.mjs --target <targetId> --out <file.pdf> [--proxy http://127.0.0.1:3456]

Downloads a PDF through an already-authenticated Chrome page controlled by the web-access CDP proxy.
It does not bypass logins, CAPTCHA, Cloudflare, paywalls, or publisher restrictions.`);
}

function parseArgs(argv) {
  const args = {
    proxy: DEFAULT_PROXY,
    close: false,
    allowNonPdf: false,
    chunkSize: 262144,
  };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--help" || a === "-h") {
      args.help = true;
    } else if (a === "--url") {
      args.url = argv[++i];
    } else if (a === "--target") {
      args.target = argv[++i];
    } else if (a === "--out") {
      args.out = argv[++i];
    } else if (a === "--proxy") {
      args.proxy = argv[++i].replace(/\/$/, "");
    } else if (a === "--close") {
      args.close = true;
    } else if (a === "--allow-non-pdf") {
      args.allowNonPdf = true;
    } else if (a === "--chunk-size") {
      args.chunkSize = Number(argv[++i]);
    } else {
      throw new Error(`Unknown argument: ${a}`);
    }
  }
  return args;
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    usage();
    return;
  }
  if (!args.out) throw new Error("--out is required");
  if (!args.url && !args.target) throw new Error("Provide --url or --target");

  // Fail fast with a friendly message if the CDP proxy isn't running.
  await healthCheck(args.proxy);

  let target = args.target;
  let openedByScript = false;

  if (!target) {
    const created = await proxyPostUrl(args.proxy, "/new", args.url, {}, 60000);
    target = created.targetId;
    openedByScript = true;
    await waitForComplete(args.proxy, target);
  } else if (args.url) {
    await proxyPostUrl(args.proxy, "/navigate", args.url, { target }, 60000);
    await waitForComplete(args.proxy, target);
  }

  // FIX: fetch the *requested* URL, not location.href — the page may have
  // JS-redirected after navigation, and fetching location.href would grab the
  // redirected HTML page instead of the PDF. Fall back to location.href only
  // when --target was given without --url (caller already navigated).
  const fetchTarget = args.url ? JSON.stringify(args.url) : "location.href";
  const initJs = `(
    async () => {
      const r = await fetch(${fetchTarget}, { credentials: "include" });
      const ct = r.headers.get("content-type") || "";
      const ab = await r.arrayBuffer();
      window.__natureDownloaderBytes = new Uint8Array(ab);
      return {
        ok: r.ok,
        status: r.status,
        contentType: ct,
        size: window.__natureDownloaderBytes.length,
        url: location.href,
        head: Array.from(window.__natureDownloaderBytes.slice(0, 8))
      };
    }
  )()`;

  const init = await proxyEval(args.proxy, target, initJs, 120000);
  const meta = init.value;
  if (!meta || !meta.ok) {
    throw new Error(`Browser fetch failed: ${JSON.stringify(meta)}`);
  }

  const headBytes = Buffer.from(meta.head || []);
  if (!args.allowNonPdf && !isPdfHead(headBytes)) {
    // Clean up the window var before erroring out.
    await proxyEval(args.proxy, target, `delete window.__natureDownloaderBytes`, 10000).catch(() => {});
    throw new Error(
      `Downloaded content is not a PDF. content-type=${meta.contentType}, head=${JSON.stringify(meta.head)}. ` +
        `If this is expected, rerun with --allow-non-pdf.`
    );
  }

  fs.mkdirSync(path.dirname(path.resolve(args.out)), { recursive: true });
  const stream = fs.createWriteStream(args.out);
  const size = Number(meta.size);
  try {
    for (let start = 0; start < size; start += args.chunkSize) {
      const end = Math.min(start + args.chunkSize, size);
      const chunkJs = `(
        () => {
          const bytes = window.__natureDownloaderBytes.slice(${start}, ${end});
          let bin = "";
          for (let i = 0; i < bytes.length; i += 0x8000) {
            bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
          }
          return btoa(bin);
        }
      )()`;
      const chunk = await proxyEval(args.proxy, target, chunkJs, 120000);
      stream.write(Buffer.from(chunk.value, "base64"));
    }
    await new Promise((resolve, reject) => {
      stream.end(resolve);
      stream.on("error", reject);
    });
  } finally {
    // Always clean up the window var.
    await proxyEval(args.proxy, target, `delete window.__natureDownloaderBytes`, 10000).catch(() => {});
  }

  const saved = fs.readFileSync(args.out);
  const savedHead = saved.subarray(0, 8).toString("ascii");
  const result = {
    out: path.resolve(args.out),
    bytes: saved.length,
    contentType: meta.contentType,
    sourceUrl: meta.url,
    signature: savedHead,
    pdf: savedHead.startsWith("%PDF"),
  };
  console.log(JSON.stringify(result, null, 2));

  if (args.close && openedByScript) {
    await closeTab(args.proxy, target);
  }
}

main().catch((error) => {
  console.error(error.stack || String(error));
  process.exit(1);
});
