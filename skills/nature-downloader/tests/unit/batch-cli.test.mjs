import { describe, test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parseArgs, selectBatchDois } from "../../scripts/batch_download.mjs";

describe("batch CLI contract", () => {
  test("does not create an output directory before SI is confirmed", () => {
    const parent = fs.mkdtempSync(path.join(os.tmpdir(), "si-gate-"));
    const out = path.join(parent, "must-not-exist");
    const script = fileURLToPath(new URL("../../scripts/batch_download.mjs", import.meta.url));
    const run = spawnSync(process.execPath, [script, "--title", "Example", "--out", out], { encoding: "utf8" });
    assert.equal(run.status, 2);
    assert.match(run.stdout, /si_confirmation_required/);
    assert.equal(fs.existsSync(out), false);
  });

  test("rejects conflicting SI choices", () => {
    assert.throws(
      () => parseArgs(["node", "batch_download.mjs", "--title", "Example", "--si", "--no-si"]),
      /mutually exclusive/i
    );
  });

  test("accepts publisher-scoped web fallback decisions", () => {
    const args = parseArgs([
      "node", "batch_download.mjs", "--dois", "10.1016/example", "--no-si",
      "--api-fallback-web-for", "elsevier,ieee",
      "--no-api-fallback-web-for", "springer_nature",
    ]);
    assert.deepEqual(args.apiFallbackWebFor, ["elsevier", "ieee"]);
    assert.deepEqual(args.noApiFallbackWebFor, ["springer_nature"]);
  });

  test("accepts a title alongside a known PDF URL", () => {
    const args = parseArgs([
      "node", "batch_download.mjs",
      "--pdf-url", "https://example.org/paper.pdf",
      "--title", "Example Paper",
      "--no-si",
    ]);
    assert.equal(args.pdfUrl, "https://example.org/paper.pdf");
    assert.equal(args.title, "Example Paper");
  });

  test("does not silently truncate an explicit DOI list", () => {
    const dois = Array.from({ length: 12 }, (_, index) => `10.1234/item-${index + 1}`);
    const args = parseArgs([
      "node", "batch_download.mjs", "--dois", dois.join(","), "--no-si",
    ]);
    assert.equal(args.count, undefined);
    assert.deepEqual(selectBatchDois(args.dois, args.count), dois);
  });

  test("keeps the topic default and honors an explicit DOI count", () => {
    const topic = parseArgs(["node", "batch_download.mjs", "--topic", "rice", "--no-si"]);
    assert.equal(topic.count, 10);
    assert.deepEqual(selectBatchDois(["a", "b", "c"], 2), ["a", "b"]);
  });

  test("requires a title for a zh non-CNKI PDF route without touching the network", () => {
    const parent = fs.mkdtempSync(path.join(os.tmpdir(), "cnki-title-required-"));
    const script = fileURLToPath(new URL("../../scripts/batch_download.mjs", import.meta.url));
    const run = spawnSync(process.execPath, [
      script,
      "--pdf-url", "https://example.org/paper.pdf",
      "--language", "zh",
      "--no-si",
      "--out", parent,
    ], { encoding: "utf8" });
    assert.equal(run.status, 0);
    assert.match(run.stdout, /metadata_ambiguous/);
    assert.match(run.stdout, /CNKI title search requires --title/);
  });
});
