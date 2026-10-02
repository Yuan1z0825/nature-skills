import { describe, test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {
  credentialsPathFromEnv,
  deleteProviderCredentials,
  loadCredentials,
  maskSecret,
  saveProviderCredentials,
} from "../../scripts/lib/credentials.mjs";

describe("publisher credential storage", () => {
  test("stores secrets separately with owner-only permissions and masks output", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "lit-dl-creds-"));
    const env = { LIT_DL_CONFIG_DIR: dir };
    const file = credentialsPathFromEnv(env);

    saveProviderCredentials("elsevier", { api_key: "secret-12345678", insttoken: "inst-87654321" }, env);

    assert.equal(file, path.join(dir, "credentials.json"));
    assert.equal(fs.statSync(file).mode & 0o777, 0o600);
    assert.deepEqual(loadCredentials(env).elsevier, {
      api_key: "secret-12345678",
      insttoken: "inst-87654321",
    });
    assert.equal(maskSecret("secret-12345678"), "***********5678");

    deleteProviderCredentials("elsevier", env);
    assert.equal(loadCredentials(env).elsevier, undefined);
  });
});
