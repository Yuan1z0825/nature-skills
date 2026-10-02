import { describe, test } from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import {
  articleBundleDirectory,
  downloadWosSupportingInformation,
  exactArticleTitleMatch,
  fetchAttachmentWithNavigationFallback,
  selectSupportingInformationLinks,
  shouldUseCleanWosBundle,
  wosSearchQuery,
} from "../../scripts/lib/wos-supporting-information.mjs";
import { parseArgs } from "../../scripts/batch_download.mjs";

describe("WoS supporting information selection", () => {
  test("keeps the clean bundle behavior isolated to WoS plus --si", () => {
    assert.equal(shouldUseCleanWosBundle({ topic: "Exact title", title: "Exact title", si: true }), true);
    assert.equal(shouldUseCleanWosBundle({ topic: "rice", si: true }), false);
    assert.equal(shouldUseCleanWosBundle({ topic: "rice", si: false }), false);
    assert.equal(shouldUseCleanWosBundle({ dois: ["10.1/x"], si: true }), false);
    assert.equal(shouldUseCleanWosBundle({ pdfUrl: "https://example.org/a.pdf", si: true }), false);
    assert.equal(shouldUseCleanWosBundle({ title: "OA title", openAccess: true, si: true }), false);
  });

  test("applies one explicit SI choice to a WoS topic batch", () => {
    const args = parseArgs(["node", "batch_download.mjs", "--topic", "rice", "--si"]);
    assert.equal(args.topic, "rice");
    assert.equal(args.si, true);
  });

  test("uses a quoted exact-phrase query when a title is supplied", () => {
    assert.equal(wosSearchQuery("fallback topic", "Exact article title"), '"Exact article title"');
    assert.equal(wosSearchQuery("rice drought", ""), "rice drought");
  });

  test("selects explicit attachments and one-level supplementary pages", () => {
    const links = [
      { text: "Supplementary Information", href: "/articles/paper/supplementary-information" },
      { text: "Download supplementary table", href: "/files/table-s1.xlsx", download: "table-s1.xlsx" },
      { text: "Source Data", href: "/files/source-data.zip" },
      { text: "Supplementary Information", dataDownloadUrl: "/download/123" },
      { text: "GitHub", href: "https://github.com/example/project" },
      { text: "References", href: "/references" },
    ];

    assert.deepEqual(selectSupportingInformationLinks(links, "https://publisher.test/article"), {
      attachments: [
        { url: "https://publisher.test/files/table-s1.xlsx", label: "Download supplementary table", filename: "table-s1.xlsx" },
        { url: "https://publisher.test/files/source-data.zip", label: "Source Data", filename: "source-data.zip" },
        { url: "https://publisher.test/download/123", label: "Supplementary Information", filename: "123" },
      ],
      pages: [
        { url: "https://publisher.test/articles/paper/supplementary-information", label: "Supplementary Information" },
      ],
    });
  });

  test("recognizes Elsevier, MDPI, and Wiley attachment patterns", () => {
    const links = [
      { text: "mmc1", href: "https://publisher.test/article#mmc1", rawHref: "#mmc1" },
      { text: "mmc1", href: "/action/downloadSupplement?doi=10.1/x&file=mmc1.mp4" },
      { text: "Supplementary Materials", href: "/article_deploy/html/images/supplementary/sensors-22-02521-s001.pdf" },
      { text: "Data S1", href: "/action/downloadSupplement?doi=10.1111/x&file=pce14065-sup-0001.pdf" },
    ];
    assert.equal(selectSupportingInformationLinks(links, "https://publisher.test/article").attachments.length, 3);
  });

  test("retries a CORS-blocked attachment after navigating to its origin", async () => {
    const calls = [];
    const result = await fetchAttachmentWithNavigationFallback(
      "proxy",
      "tab",
      { url: "https://cdn.publisher.test/mmc1.pdf" },
      () => "/tmp/mmc1.pdf",
      {
        fetchImpl: async () => {
          calls.push("fetch");
          return calls.length === 1 ? { ok: false, err: "TypeError: Failed to fetch" } : { ok: true, file: "/tmp/mmc1.pdf" };
        },
        navigateImpl: async () => { calls.push("navigate"); },
        waitForCompleteImpl: async () => { calls.push("wait"); },
      }
    );
    assert.equal(result.ok, true);
    assert.deepEqual(calls, ["fetch", "navigate", "wait", "fetch"]);
  });
});

describe("clean article bundle", () => {
  test("uses the exact readable title as the article folder", () => {
    assert.equal(
      articleBundleDirectory("/tmp/out", "Leaf direction: Lamina joint development and environmental responses"),
      path.join("/tmp/out", "Leaf direction Lamina joint development and environmental responses")
    );
  });

  test("matches requested and discovered titles exactly with punctuation tolerance", () => {
    assert.equal(
      exactArticleTitleMatch(
        "Sounds emitted by plants under stress are airborne and informative",
        "Sounds emitted by plants under stress are airborne and informative."
      ),
      true
    );
    assert.equal(exactArticleTitleMatch("Leaf direction", "Leaf direction: Lamina joint development and environmental responses"), false);
  });

  test("downloads direct attachments plus attachments found one page deep", async () => {
    const bundleDir = "/tmp/out/Article";
    const scanned = [];
    const result = await downloadWosSupportingInformation({
      proxy: "proxy",
      tab: "tab",
      landingUrl: "https://publisher.test/article",
      bundleDir,
      dependencies: {
        scanPageImpl: async (_proxy, _tab, url) => {
          scanned.push(url);
          if (url.endsWith("/article")) {
            return [
              { text: "Supplementary Information", href: "/supplement-page" },
              { text: "Source Data", href: "/files/source-data.zip" },
            ];
          }
          return [{ text: "Supplementary Table", href: "/files/table-s1.xlsx" }];
        },
        fetchAttachmentImpl: async (_proxy, _tab, attachment, resolvePath) => {
          const file = resolvePath({
            finalUrl: attachment.url,
            contentType: attachment.url.endsWith("zip") ? "application/zip" : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            contentDisposition: `attachment; filename=${attachment.filename}`,
          });
          return { ok: true, file, bytes: 100 };
        },
      },
    });

    assert.deepEqual(scanned, [
      "https://publisher.test/article",
      "https://publisher.test/supplement-page",
    ]);
    assert.equal(result.status, "downloaded");
    assert.equal(result.downloaded, 2);
    assert.deepEqual(result.files.sort(), [
      path.join(bundleDir, "source-data.zip"),
      path.join(bundleDir, "table-s1.xlsx"),
    ]);
  });

  test("reports not_found without creating diagnostic files", async () => {
    const result = await downloadWosSupportingInformation({
      proxy: "proxy",
      tab: "tab",
      landingUrl: "https://publisher.test/article",
      bundleDir: "/tmp/out/Article",
      dependencies: { scanPageImpl: async () => [] },
    });
    assert.deepEqual(result, {
      status: "not_found",
      found: 0,
      downloaded: 0,
      files: [],
      failures: [],
    });
  });

  test("adds a MIME extension and never overwrites the main PDF", async () => {
    const bundleDir = "/tmp/out/Article";
    const result = await downloadWosSupportingInformation({
      proxy: "proxy",
      tab: "tab",
      landingUrl: "https://publisher.test/article",
      bundleDir,
      reservedFilenames: ["Article.pdf"],
      dependencies: {
        scanPageImpl: async () => [{ text: "Supplementary", href: "/downloadSupplement?file=Article.pdf" }],
        fetchAttachmentImpl: async (_proxy, _tab, attachment, resolvePath) => ({
          ok: true,
          file: resolvePath({
            url: "https://publisher.test/downloadSupplement",
            contentType: "application/pdf",
            contentDisposition: "attachment; filename=Article.pdf",
          }),
          bytes: 100,
        }),
      },
    });
    assert.deepEqual(result.files, [path.join(bundleDir, "Article-2.pdf")]);

    const extensionless = await downloadWosSupportingInformation({
      proxy: "proxy",
      tab: "tab",
      landingUrl: "https://publisher.test/article",
      bundleDir,
      dependencies: {
        scanPageImpl: async () => [{ text: "Supplementary", href: "/downloadSupplement?file=supplement" }],
        fetchAttachmentImpl: async (_proxy, _tab, attachment, resolvePath) => ({
          ok: true,
          file: resolvePath({ url: attachment.url, contentType: "application/pdf", contentDisposition: "" }),
          bytes: 100,
        }),
      },
    });
    assert.deepEqual(extensionless.files, [path.join(bundleDir, "supplement.pdf")]);
  });

  test("reports an inaccessible supplementary page as fetch_failed", async () => {
    const result = await downloadWosSupportingInformation({
      proxy: "proxy",
      tab: "tab",
      landingUrl: "https://publisher.test/article",
      bundleDir: "/tmp/out/Article",
      dependencies: {
        scanPageImpl: async (_proxy, _tab, url) => {
          if (url.endsWith("/article")) return [{ text: "Supplementary Information", href: "/supplement-page" }];
          throw new Error("publisher verification required");
        },
      },
    });
    assert.equal(result.status, "fetch_failed");
    assert.match(result.failures[0].error, /verification required/);
  });
});
