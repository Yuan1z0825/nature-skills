import { describe, test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { downloadPublisherArticle } from "../../scripts/lib/publisher-providers.mjs";

function response(body, { status = 200, contentType = "application/pdf" } = {}) {
  return new Response(body, { status, headers: { "content-type": contentType } });
}

describe("publisher API providers", () => {
  test("requires provider credentials without exposing a secret", async () => {
    const result = await downloadPublisherArticle({ doi: "10.1016/example", title: "Example" }, {
      provider: "elsevier",
      credentials: null,
      outDir: fs.mkdtempSync(path.join(os.tmpdir(), "provider-")),
      fetchImpl: async () => { throw new Error("must not fetch"); },
    });
    assert.equal(result.status, "credentials_missing");
    assert.match(result.configureUrl, /elsevier\.com/);
  });

  test("downloads and validates Elsevier PDF full text", async () => {
    const outDir = fs.mkdtempSync(path.join(os.tmpdir(), "provider-"));
    const result = await downloadPublisherArticle({ doi: "10.1016/example", title: "Example" }, {
      provider: "elsevier",
      credentials: { api_key: "key", insttoken: "token" },
      outDir,
      fetchImpl: async (_url, options) => {
        assert.equal(options.headers["X-ELS-APIKey"], "key");
        assert.equal(options.headers["X-ELS-Insttoken"], "token");
        return response(Buffer.from("%PDF-1.7\ncontent"));
      },
    });
    assert.equal(result.status, "downloaded");
    assert.equal(result.format, "pdf");
    assert.equal(fs.existsSync(result.file), true);
    assert.match(result.sha256, /^[a-f0-9]{64}$/);
  });

  test("accepts Springer JATS XML as native full text", async () => {
    const outDir = fs.mkdtempSync(path.join(os.tmpdir(), "provider-"));
    const secret = "springer-secret";
    const result = await downloadPublisherArticle({ doi: "10.1007/example", title: "Springer Example" }, {
      provider: "springer_nature",
      credentials: { api_key: secret },
      outDir,
      fetchImpl: async () => response(`<?xml version="1.0"?><article article-type="research-article"><body>Text</body></article>`, { contentType: "application/xml" }),
    });
    assert.equal(result.status, "native_fulltext_downloaded");
    assert.equal(result.format, "jats_xml");
    assert.match(result.file, /\.xml$/);
    assert.doesNotMatch(result.source, new RegExp(secret));
    assert.doesNotMatch(result.source, /api_key=/i);
  });

  test("reports readable publisher HTML with the HTML-specific success status", async () => {
    const outDir = fs.mkdtempSync(path.join(os.tmpdir(), "provider-"));
    const result = await downloadPublisherArticle({ doi: "10.1007/example", title: "HTML Example" }, {
      provider: "springer_nature",
      credentials: { api_key: "key" },
      outDir,
      fetchImpl: async () => response(`<!doctype html><article class="article-body">${"Full text ".repeat(100)}</article>`, { contentType: "text/html" }),
    });
    assert.equal(result.status, "full_text_html_available");
    assert.equal(result.format, "html");
  });

  test("reports entitlement failures before web fallback", async () => {
    const result = await downloadPublisherArticle({ doi: "10.1109/example", title: "IEEE Example" }, {
      provider: "ieee",
      credentials: { api_key: "key", fulltext_endpoint: "https://fulltext.ieee.test/articles/{doi}" },
      outDir: fs.mkdtempSync(path.join(os.tmpdir(), "provider-")),
      fetchImpl: async () => response("Forbidden", { status: 403, contentType: "text/plain" }),
    });
    assert.equal(result.status, "api_not_entitled");
    assert.equal(result.fallbackConfirmationRequired, true);
  });

  test("does not mistake an IEEE metadata key for paid full-text access", async () => {
    const result = await downloadPublisherArticle({ doi: "10.1109/example", title: "IEEE Example" }, {
      provider: "ieee",
      credentials: { api_key: "metadata-key" },
      outDir: fs.mkdtempSync(path.join(os.tmpdir(), "provider-")),
      fetchImpl: async () => { throw new Error("must not call metadata API as full text"); },
    });
    assert.equal(result.status, "api_fulltext_unavailable");
    assert.match(result.detail, /Full-Text Access API/i);
  });

  test("retries transient Elsevier failures in the canonical provider", async () => {
    let calls = 0;
    const result = await downloadPublisherArticle({ doi: "10.1016/example", title: "Retry Example" }, {
      provider: "elsevier",
      credentials: { api_key: "key" },
      outDir: fs.mkdtempSync(path.join(os.tmpdir(), "provider-")),
      fetchImpl: async () => ++calls === 1
        ? response("temporary", { status: 503, contentType: "text/plain" })
        : response(Buffer.from("%PDF-1.7\ncontent")),
      sleepImpl: async () => {},
    });
    assert.equal(calls, 2);
    assert.equal(result.status, "downloaded");
  });
});
