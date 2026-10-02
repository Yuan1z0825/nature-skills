import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const runtimeRoots = ["SKILL.md", "README.md", "agents", "data", "examples", "scripts", "src"];
const textExtensions = new Set([".md", ".yaml", ".yml", ".json", ".py", ".mjs", ".tsv", ".txt"]);

function filesUnder(relative) {
  const target = path.join(root, relative);
  if (!fs.existsSync(target)) return [];
  if (fs.statSync(target).isFile()) return [target];
  return fs.readdirSync(target, { withFileTypes: true }).flatMap((entry) =>
    entry.name === "__pycache__" ? [] : filesUnder(path.join(relative, entry.name))
  );
}

test("distributed skill contains no local identity, institution preset, or secret file", () => {
  const files = runtimeRoots.flatMap(filesUnder).filter((file) => textExtensions.has(path.extname(file)));
  const joined = files.map((file) => `${path.relative(root, file)}\n${fs.readFileSync(file, "utf8")}`).join("\n");

  assert.doesNotMatch(joined, /\/Users\/[a-z0-9._-]+\/|C:\\Users\\[a-z0-9._-]+\\/i);
  const legacyInstitutionMarkers = new RegExp(
    ["s" + "jtu", "j" + "account", "w" + "hu\\."].join("|"),
    "i"
  );
  assert.doesNotMatch(joined, legacyInstitutionMarkers);
  assert.doesNotMatch(joined, /(?:id|cas|sso|passport|authserver)\.[a-z0-9-]+\.edu\.cn/i);

  const schools = fs.readFileSync(path.join(root, "data/schools.yaml"), "utf8");
  assert.match(schools, /^schools:\s*\[\]\s*$/m);

  for (const forbidden of ["credentials.json", "school.json", ".env"]) {
    assert.equal(files.some((file) => path.basename(file) === forbidden), false, `${forbidden} must not be distributed`);
  }
});
