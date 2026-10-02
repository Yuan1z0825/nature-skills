import { describe, test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { downloadOpenAccessArticle } from "../../scripts/lib/open-access-provider.mjs";

describe("OA provider waterfall", () => {
  test("uses PMC before Unpaywall and records OA evidence", async () => {
    const calls = [];
    const result = await downloadOpenAccessArticle({ doi: "10.1234/example", title: "OA Example", pmcid: "PMC123" }, {
      email: "researcher@example.org",
      outDir: fs.mkdtempSync(path.join(os.tmpdir(), "oa-")),
      fetchImpl: async (url) => {
        calls.push(String(url));
        if (String(url).includes("oa.fcgi")) return new Response(`<OA><records><record><link format="pdf" href="https://ftp.ncbi.nlm.nih.gov/a.pdf" /></record></records></OA>`);
        if (String(url).includes("unpaywall")) return Response.json({ is_oa: true, best_oa_location: { url_for_pdf: "https://repo.example/a.pdf" }, oa_locations: [] });
        if (String(url).includes("ftp.ncbi")) return new Response(Buffer.from("%PDF-1.7\nPMC"), { headers: { "content-type": "application/pdf" } });
        throw new Error(`unexpected URL ${url}`);
      },
    });
    assert.equal(result.status, "open_access_downloaded");
    assert.equal(result.oaEvidence.source, "pmc");
    assert.equal(calls.some((url) => url.includes("repo.example")), false);
  });

  test("reports oa_not_found when no lawful candidate exists", async () => {
    const result = await downloadOpenAccessArticle({ doi: "10.1234/closed", title: "Closed" }, {
      email: "researcher@example.org",
      outDir: fs.mkdtempSync(path.join(os.tmpdir(), "oa-")),
      fetchImpl: async (url) => String(url).includes("unpaywall")
        ? Response.json({ is_oa: false, oa_locations: [] })
        : new Response("not found", { status: 404 }),
    });
    assert.equal(result.status, "oa_not_found");
    assert.equal(result.oaAssessment, "confirmed_closed");
  });

  test("keeps OA state unknown when required resolvers could not decide", async () => {
    const result = await downloadOpenAccessArticle({ doi: "10.1234/unknown", title: "Unknown" }, {
      email: "",
      outDir: fs.mkdtempSync(path.join(os.tmpdir(), "oa-")),
      fetchImpl: async () => new Response("unavailable", { status: 503 }),
    });
    assert.equal(result.status, "oa_not_found");
    assert.equal(result.oaAssessment, "unknown");
  });

  test("does not reclassify a confirmed OA article as closed when its file is temporarily unavailable", async () => {
    const result = await downloadOpenAccessArticle({ doi: "10.1234/oa", title: "OA", license: "cc-by", publisherPdfUrl: "https://publisher.example/a.pdf" }, {
      email: "researcher@example.org",
      outDir: fs.mkdtempSync(path.join(os.tmpdir(), "oa-")),
      fetchImpl: async (url) => String(url).includes("unpaywall")
        ? Response.json({ is_oa: true, best_oa_location: { url_for_pdf: "https://repo.example/a.pdf", host_type: "repository" }, oa_locations: [] })
        : String(url).includes("europepmc")
          ? Response.json({ resultList: { result: [] } })
          : new Response("temporary", { status: 503 }),
    });
    assert.equal(result.oaAssessment, "confirmed_oa");
    assert.equal(result.oaAttempts.length >= 1, true);
  });
});
