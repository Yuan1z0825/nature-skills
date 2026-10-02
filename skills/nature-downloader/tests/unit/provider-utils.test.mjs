import { describe, test } from "node:test";
import assert from "node:assert/strict";
import {
  classifyFullTextContent,
  classifyProviderFailure,
} from "../../scripts/lib/provider-utils.mjs";

describe("native full-text validation", () => {
  test("distinguishes PDF, CAJ, HTML, JATS/XML, and login/error pages", () => {
    assert.equal(classifyFullTextContent({ contentType: "application/pdf", head: Buffer.from("%PDF-1.7") }).format, "pdf");
    assert.equal(classifyFullTextContent({ contentType: "application/octet-stream", head: Buffer.from("CAJViewer") }).format, "caj");
    assert.equal(classifyFullTextContent({ contentType: "text/html", head: Buffer.from("<!doctype html><article>Full text</article>") }).format, "html");
    assert.equal(classifyFullTextContent({ contentType: "application/xml", head: Buffer.from("<?xml version=\"1.0\"?><article article-type=\"research-article\">") }).format, "jats_xml");
    assert.equal(classifyFullTextContent({ contentType: "text/html", head: Buffer.from("<!doctype html><title>Log in</title><form>Password</form>") }).valid, false);
  });

  test("maps API authorization and empty-fulltext failures", () => {
    assert.equal(classifyProviderFailure({ status: 401 }), "credentials_invalid");
    assert.equal(classifyProviderFailure({ status: 403 }), "api_not_entitled");
    assert.equal(classifyProviderFailure({ status: 404 }), "api_fulltext_unavailable");
  });
});
