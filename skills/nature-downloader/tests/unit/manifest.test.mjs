import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { writeManifest } from "../../scripts/lib/manifest.mjs";

test("manifest records route and SI choice without secrets", () => {
  const outDir = fs.mkdtempSync(path.join(os.tmpdir(), "manifest-"));
  const file = writeManifest(outDir, {
    request: { si_requested: false },
    results: [{
      doi: "10.1016/example",
      provider: "elsevier",
      api_key: "must-not-leak",
      source: "https://api.example.test/fulltext?api_key=query-secret&doi=10.1016/example",
      reason: "Authorization: Bearer bearer-secret",
      status: "downloaded",
    }],
  });
  const text = fs.readFileSync(file, "utf8");
  assert.doesNotMatch(text, /must-not-leak/);
  assert.doesNotMatch(text, /query-secret|bearer-secret/);
  assert.match(text, /api_key=\[REDACTED\]/);
  assert.match(text, /"si_requested": false/);
  assert.match(text, /"provider": "elsevier"/);
});
