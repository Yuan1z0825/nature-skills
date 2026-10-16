import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { downloadPublisherArticle } from "../../scripts/lib/publisher-providers.mjs";
import { hasUsablePublisherCredentials } from "../../scripts/lib/routing.mjs";
import { saveProviderCredentials, loadCredentials, maskedCredentials } from "../../scripts/lib/credentials.mjs";

const article = { doi: "10.1007/example", title: "Springer services" };
const xml = '<article><body>Full text</body></article>';
function options(t, credentials, fetchImpl) {
  const outDir = fs.mkdtempSync(path.join(os.tmpdir(), "springer-services-"));
  t.after(() => fs.rmSync(outDir, { recursive: true, force: true }));
  return { provider: "springer_nature", credentials, outDir, fetchImpl };
}
function jats(body = xml) {
  return new Response(body, { headers: { "content-type": "application/xml" } });
}

test("Springer Meta credentials never enable full-text requests", async (t) => {
  const credentials = { metadata_api_key: "meta-secret" };
  assert.equal(hasUsablePublisherCredentials("springer_nature", credentials), false);
  const result = await downloadPublisherArticle(article, options(t, credentials, async () => {
    assert.fail("must not use Meta credentials for full text");
  }));
  assert.equal(result.status, "api_fulltext_unavailable");
  assert.equal(result.fallbackConfirmationRequired, true);
});

test("OA-only credentials use the OA JATS endpoint and redact their source", async (t) => {
  const credentials = { metadata_api_key: "meta-secret", openaccess_api_key: "oa-secret" };
  assert.equal(hasUsablePublisherCredentials("springer_nature", credentials), true);
  let calls = 0;
  const result = await downloadPublisherArticle(article, options(t, credentials, async (input, request) => {
    calls++;
    const url = new URL(input);
    assert.equal(url.origin, "https://api.springernature.com");
    assert.equal(url.pathname, "/openaccess/jats");
    assert.equal(url.searchParams.get("api_key"), "oa-secret");
    assert.equal(url.searchParams.get("q"), "doi:10.1007/example");
    assert.equal(request.headers.Accept, "application/xml");
    return jats();
  }));
  assert.equal(calls, 1);
  assert.equal(result.status, "native_fulltext_downloaded");
  assert.equal(result.service, "openaccess");
  assert.equal(fs.readFileSync(result.file, "utf8"), xml);
  assert.doesNotMatch(JSON.stringify(result), /oa-secret|meta-secret|api_key=/);
});

test("Full Text selects its own credential including the issued metric", async (t) => {
  const result = await downloadPublisherArticle(article, options(t, {
    api_key: "legacy-secret", fulltext_api_key: "tdm-secret/metric", openaccess_api_key: "oa-secret",
  }, async (input) => {
    const url = new URL(input);
    assert.equal(url.pathname, "/xmldata/jats");
    assert.equal(url.searchParams.get("api_key"), "tdm-secret/metric");
    return jats();
  }));
  assert.equal(result.service, "fulltext");
  assert.equal(result.serviceAttempts.length, 1);
  assert.doesNotMatch(JSON.stringify(result), /tdm-secret|oa-secret|legacy-secret/);
});

test("failed or unusable Full Text responses fall back to the configured OA service", async (t) => {
  for (const failure of [403, 404, 429, 500, "network", "metadata"]) {
    const calls = [];
    const result = await downloadPublisherArticle(article, options(t, {
      fulltext_api_key: "tdm-secret", openaccess_api_key: "oa-secret",
    }, async (input) => {
      const url = new URL(input);
      calls.push(url.pathname);
      if (url.pathname === "/xmldata/jats") {
        if (failure === "network") throw new Error("offline");
        if (failure === "metadata") return jats("<response><records/></response>");
        return new Response("unavailable", { status: failure });
      }
      assert.equal(url.searchParams.get("api_key"), "oa-secret");
      return jats();
    }));
    assert.deepEqual(calls, ["/xmldata/jats", "/openaccess/jats"]);
    assert.equal(result.status, "native_fulltext_downloaded");
    assert.equal(result.serviceAttempts.length, 2);
    assert.notEqual(result.serviceAttempts[0].status, "native_fulltext_downloaded");
  }
});

test("OA metadata and failed services remain failures eligible for existing fallbacks", async (t) => {
  const result = await downloadPublisherArticle(article, options(t, {
    fulltext_api_key: "tdm-secret", openaccess_api_key: "oa-secret",
  }, async (input) => new URL(input).pathname === "/xmldata/jats"
    ? new Response("Forbidden", { status: 403 })
    : jats("<response><records/></response>")));
  assert.equal(result.status, "api_fulltext_unavailable");
  assert.equal(result.fallbackConfirmationRequired, true);
  assert.equal(result.serviceAttempts.length, 2);
});

test("Springer service storage preserves other service grants and legacy credentials", (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "springer-storage-"));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const env = { LIT_DL_CONFIG_DIR: dir };
  saveProviderCredentials("springer_nature", { api_key: "legacy-secret" }, env);
  saveProviderCredentials("springer_nature", { metadata_api_key: "meta-secret" }, env);
  saveProviderCredentials("springer_nature", { openaccess_api_key: "oa-secret" }, env);
  saveProviderCredentials("springer_nature", { fulltext_api_key: "tdm-secret" }, env);
  assert.deepEqual(loadCredentials(env).springer_nature, {
    api_key: "legacy-secret", metadata_api_key: "meta-secret",
    openaccess_api_key: "oa-secret", fulltext_api_key: "tdm-secret",
  });
  assert.doesNotMatch(JSON.stringify(maskedCredentials(env)), /legacy-secret|meta-secret|oa-secret|tdm-secret/);
});

test("legacy Springer credentials remain Full Text credentials", async (t) => {
  assert.equal(hasUsablePublisherCredentials("springer_nature", { api_key: "legacy-secret" }), true);
  const result = await downloadPublisherArticle(article, options(t, { api_key: "legacy-secret" }, async (input) => {
    const url = new URL(input);
    assert.equal(url.pathname, "/xmldata/jats");
    assert.equal(url.searchParams.get("api_key"), "legacy-secret");
    return jats();
  }));
  assert.equal(result.service, "fulltext");
  assert.equal(result.status, "native_fulltext_downloaded");
});

test("Springer network failures do not expose service keys", async (t) => {
  const result = await downloadPublisherArticle(article, options(t, { openaccess_api_key: "oa-secret" }, async () => {
    throw new Error("https://api.springernature.com/openaccess/jats?api_key=oa-secret");
  }));
  assert.equal(result.status, "api_fulltext_unavailable");
  assert.doesNotMatch(JSON.stringify(result), /oa-secret/);
});
