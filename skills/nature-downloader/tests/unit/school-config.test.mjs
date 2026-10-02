import { test, describe } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {
  configPathFromEnv,
  loadSchoolConfig,
  discoveryUrlFromConfig,
  DEFAULT_DISCOVERY_URL,
} from "../../scripts/lib/school-config.mjs";

describe("school config loader", () => {
  test("uses LIT_DL_CONFIG_DIR when present", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "lit-dl-"));
    assert.equal(configPathFromEnv({ LIT_DL_CONFIG_DIR: dir }), path.join(dir, "school.json"));
  });

  test("returns null for missing config", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "lit-dl-"));
    assert.equal(loadSchoolConfig({ LIT_DL_CONFIG_DIR: dir }), null);
  });

  test("returns configured discovery URL", () => {
    const config = {
      discovery: {
        web_of_science_url: "https://example.edu/wos",
      },
    };
    assert.equal(discoveryUrlFromConfig(config), "https://example.edu/wos");
  });

  test("falls back to default Web of Science URL", () => {
    assert.equal(discoveryUrlFromConfig(null), DEFAULT_DISCOVERY_URL);
    assert.equal(discoveryUrlFromConfig({}), DEFAULT_DISCOVERY_URL);
  });
});
