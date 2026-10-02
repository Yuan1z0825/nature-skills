import { describe, test } from "node:test";
import assert from "node:assert/strict";
import {
  classifyPublisher,
  chooseDirectUrlRoute,
  chooseRoute,
  hasUsablePublisherCredentials,
  parseSiChoice,
} from "../../scripts/lib/routing.mjs";

describe("SI confirmation gate", () => {
  test("requires one explicit SI choice before downloading", () => {
    assert.deepEqual(parseSiChoice({ si: false, noSi: false }), {
      confirmed: false,
      status: "si_confirmation_required",
    });
    assert.deepEqual(parseSiChoice({ si: true, noSi: false }), {
      confirmed: true,
      wantSi: true,
    });
    assert.deepEqual(parseSiChoice({ si: false, noSi: true }), {
      confirmed: true,
      wantSi: false,
    });
    assert.throws(() => parseSiChoice({ si: true, noSi: true }), /mutually exclusive/i);
  });
});

describe("literature routing", () => {
  test("routes every Chinese article only to CNKI", () => {
    assert.equal(chooseRoute({ title: "乡村振兴研究", isOa: true, publisher: "Elsevier" }).provider, "cnki");
    assert.equal(chooseRoute({ language: "zh", doi: "10.1016/example", isOa: false }).provider, "cnki");
    assert.equal(chooseRoute({ sourceUrl: "https://kns.cnki.net/kcms/detail/detail.aspx?filename=x" }).provider, "cnki");
  });

  test("does not let a non-CNKI PDF URL bypass Chinese routing", () => {
    assert.deepEqual(chooseDirectUrlRoute({
      pdfUrl: "https://example.org/paper.pdf",
      title: "乡村振兴研究",
    }), { provider: "cnki", mode: "title_search", reason: "chinese_literature" });
    assert.deepEqual(chooseDirectUrlRoute({
      pdfUrl: "https://example.org/paper.pdf",
      language: "zh-CN",
    }), { provider: "cnki", mode: "title_search", reason: "chinese_literature" });
  });

  test("keeps CNKI direct URLs on the direct CNKI path", () => {
    assert.deepEqual(chooseDirectUrlRoute({
      pdfUrl: "https://kns.cnki.net/kcms/detail/detail.aspx?filename=x",
      title: "乡村振兴研究",
    }), { provider: "cnki", mode: "direct", reason: "explicit_cnki_url" });
  });

  test("routes supported publishers with credentials to their API before OA", () => {
    const route = chooseRoute({ language: "en", isOa: true, publisher: "Elsevier", hasPublisherCredentials: true });
    assert.equal(route.provider, "elsevier");
    assert.equal(route.reason, "publisher_api_credentials_available");
  });

  test("requires an IEEE full-text endpoint before treating its credentials as usable", () => {
    assert.equal(hasUsablePublisherCredentials("elsevier", { api_key: "key" }), true);
    assert.equal(hasUsablePublisherCredentials("ieee", { api_key: "metadata-key" }), false);
    assert.equal(hasUsablePublisherCredentials("ieee", {
      api_key: "fulltext-key",
      fulltext_endpoint: "https://ieee.example/articles/{doi}",
    }), true);
  });

  test("routes an English OA article without publisher credentials to OA", () => {
    assert.equal(chooseRoute({ language: "en", isOa: true, publisher: "Elsevier", hasPublisherCredentials: false }).provider, "open_access");
  });

  test("routes English non-OA articles by publisher", () => {
    assert.equal(chooseRoute({ language: "en", isOa: false, publisher: "Elsevier" }).provider, "elsevier");
    assert.equal(chooseRoute({ language: "en", isOa: false, publisher: "Springer Nature" }).provider, "springer_nature");
    assert.equal(chooseRoute({ language: "en", isOa: false, publisher: "IEEE" }).provider, "ieee");
    assert.equal(chooseRoute({ language: "en", isOa: false, publisher: "Wiley" }).provider, "web_access");
  });

  test("recognizes publisher from DOI prefixes and names", () => {
    assert.equal(classifyPublisher({ doi: "10.1016/j.cell.2026.01.001" }), "elsevier");
    assert.equal(classifyPublisher({ doi: "10.1007/s00122-021-03957-1" }), "springer_nature");
    assert.equal(classifyPublisher({ doi: "10.1109/5.771073" }), "ieee");
    assert.equal(classifyPublisher({ publisher: "Elsevier B.V." }), "elsevier");
  });
});
