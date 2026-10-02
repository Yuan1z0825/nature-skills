import { describe, test } from "node:test";
import assert from "node:assert/strict";
import { parseCrossrefWork } from "../../scripts/lib/metadata.mjs";

describe("metadata normalization", () => {
  test("normalizes a Crossref work into one literature entity", () => {
    const article = parseCrossrefWork({
      DOI: "10.1016/J.CELL.2026.01.001",
      title: ["A useful article"],
      publisher: "Elsevier BV",
      language: "en",
      license: [{ URL: "https://creativecommons.org/licenses/by/4.0/" }],
      link: [{ URL: "https://example.org/article.pdf", "content-type": "application/pdf", "intended-application": "text-mining" }],
    });
    assert.equal(article.doi, "10.1016/j.cell.2026.01.001");
    assert.equal(article.title, "A useful article");
    assert.equal(article.publisher, "Elsevier BV");
    assert.equal(article.language, "en");
    assert.equal(article.license, "https://creativecommons.org/licenses/by/4.0/");
    assert.equal(article.publisherPdfUrl, "https://example.org/article.pdf");
  });
});
