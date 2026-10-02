import { describe, test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { streamToDisk } from "../../scripts/lib/pdf-utils.mjs";


describe("browser download file writes", () => {
  test("publishes the final file only after every chunk is written", async () => {
    const directory = fs.mkdtempSync(path.join(os.tmpdir(), "browser-download-"));
    const outPath = path.join(directory, "paper.pdf");
    const chunks = [Buffer.from("AB").toString("base64"), Buffer.from("CD").toString("base64")];
    const evalImpl = async (_proxy, _target, script) => (
      script.startsWith("delete ") ? "" : chunks.shift()
    );

    const result = await streamToDisk(
      "proxy", "target", "bytes", 4, outPath, 2, undefined, evalImpl,
    );

    assert.deepEqual(result, { file: outPath, bytes: 4 });
    assert.equal(fs.readFileSync(outPath, "utf8"), "ABCD");
    assert.deepEqual(fs.readdirSync(directory), ["paper.pdf"]);
  });

  test("a failed chunk leaves an existing final file unchanged", async () => {
    const directory = fs.mkdtempSync(path.join(os.tmpdir(), "browser-download-"));
    const outPath = path.join(directory, "paper.pdf");
    fs.writeFileSync(outPath, "original", "utf8");
    let chunkCalls = 0;
    const evalImpl = async (_proxy, _target, script) => {
      if (script.startsWith("delete ")) return "";
      chunkCalls += 1;
      if (chunkCalls === 1) return Buffer.from("AB").toString("base64");
      throw new Error("browser connection lost");
    };

    await assert.rejects(
      streamToDisk(
        "proxy", "target", "bytes", 4, outPath, 2, undefined, evalImpl,
      ),
      /browser connection lost/,
    );

    assert.equal(fs.readFileSync(outPath, "utf8"), "original");
    assert.deepEqual(fs.readdirSync(directory), ["paper.pdf"]);
  });

  test("a truncated browser chunk is rejected", async () => {
    const directory = fs.mkdtempSync(path.join(os.tmpdir(), "browser-download-"));
    const outPath = path.join(directory, "paper.pdf");
    const evalImpl = async (_proxy, _target, script) => (
      script.startsWith("delete ") ? "" : Buffer.from("A").toString("base64")
    );

    await assert.rejects(
      streamToDisk(
        "proxy", "target", "bytes", 2, outPath, 2, undefined, evalImpl,
      ),
      /chunk size mismatch/,
    );

    assert.equal(fs.existsSync(outPath), false);
    assert.deepEqual(fs.readdirSync(directory), []);
  });
});
